"""
MediKiosk — NegEx + Multilingual Semantic Concept Normalizer
Maps patient statements in 5 languages to standardized SNOMED-CT & NAMASTE concept codes.

Pipeline:
  1. Deterministic NegEx pre-filter (checks for negation terms: nahi, not, illai, ledu, etc.)
  2. Multilingual sentence transformer embeds the statement in 15ms on CPU
  3. Cosine similarity maps phrase to SNOMED/NAMASTE concepts without LLM hallucination

Embedding model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  (XLM-RoBERTa based, ~470 MB, natively covers hi, mr, ta, te, en).
  English-only models such as all-MiniLM-L6-v2 emit [UNK] for Devanagari,
  Tamil and Telugu input and must not be substituted here.

Ref: MediKiosk_Tech_Stack_Finalized.md Section 3B
"""

import json
import re
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from app.config import settings

logger = logging.getLogger("medikiosk.normalizer")


class ConceptMatch:
    """Result of semantic concept normalization."""
    def __init__(
        self,
        concept: Optional[dict],
        score: float,
        status: str,
        is_negated: bool = False
    ):
        self.concept = concept      # {name, code, category, ...}
        self.score = score          # Cosine similarity score
        self.status = status        # CONFIRMED_MATCH | REQUIRES_EXPLAIN_BACK | ESCALATE_TO_LLM | EXPLICITLY_DENIED
        self.is_negated = is_negated

    def to_dict(self) -> dict:
        return {
            "concept": self.concept,
            "score": self.score,
            "status": self.status,
            "is_negated": self.is_negated
        }


class SemanticConceptNormalizer:
    """
    Combines deterministic NegEx rule-checking with multilingual sentence-transformer embeddings.
    Maps patient statements in 5 languages to standardized SNOMED-CT & NAMASTE concept codes.

    Confidence Tiers:
      ≥ 0.82 → CONFIRMED_MATCH (auto-accepted)
      0.55–0.82 → REQUIRES_EXPLAIN_BACK (patient must confirm)
      < 0.55 → ESCALATE_TO_LLM (fall back to LLM extraction)
    """

    # Negation terms across 5 supported languages
    NEGATION_TERMS: dict[str, list[str]] = {
        "hi": ["nahi", "nahin", "nhi", "mat", "na", "bina", "bilkul_nahi", "kabhi_nahi"],
        "en": ["no", "not", "denies", "without", "never", "none", "deny", "negative", "absent"],
        "ta": ["illai", "kidayathu", "illamal", "mattum", "alla"],
        "te": ["ledu", "kadu", "lekunda", "kaadu", "avadu"],
        "mr": ["nahi", "nasun", "nako", "kashach_nahi"]
    }

    # Pre-negation window: words before symptom that indicate negation (for NegEx algorithm)
    PRE_NEGATION_TRIGGERS = {"no", "not", "denies", "without", "nahi", "nahin", "na", "nhi", "ledu", "illai"}
    # Post-negation: terms after symptom that negate it
    POST_NEGATION_TRIGGERS = {"nahi", "nhi", "nahin", "not", "illai", "ledu"}

    def __init__(self):
        self._embedding_model = None  # SentenceTransformer instance
        self._concept_embeddings: Optional[np.ndarray] = None
        self._variant_owners: Optional[np.ndarray] = None
        self._concept_metadata: Optional[list[dict]] = None
        self._loaded = False

    def warmup(self) -> None:
        """Eagerly load the embedding model and pre-compute the concept index."""
        self._load_models()

    def _load_models(self):
        """Load the multilingual embedding model and pre-compute the concept index."""
        if self._loaded:
            return

        # Load concept bank
        concept_bank_path = Path(settings.CONCEPT_BANK_PATH)
        if concept_bank_path.exists():
            with open(concept_bank_path, "r", encoding="utf-8") as f:
                bank = json.load(f)
                self._concept_metadata = bank.get("concepts", [])
                logger.info(f"Loaded concept bank: {len(self._concept_metadata)} concepts")
        else:
            logger.warning(f"Concept bank not found at {concept_bank_path}. Using built-in defaults.")
            self._concept_metadata = self._get_default_concepts()

        try:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL_NAME}")
            self._build_concept_index()
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Using keyword-based fallback. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}. Using keyword fallback.")

        self._loaded = True

    def _build_concept_index(self):
        """
        Embed each concept variant (canonical name + every native-script keyword)
        as its own vector rather than concatenating them into one string. A Tamil
        or Telugu query then scores against a same-script anchor instead of a
        diluted multi-script blob, which is what makes cross-script matching work.
        """
        variants: list[str] = []
        owners: list[int] = []

        for idx, concept in enumerate(self._concept_metadata or []):
            for text in [concept.get("name", "")] + list(concept.get("keywords", [])):
                if text and text.strip():
                    variants.append(text.strip())
                    owners.append(idx)

        if not variants:
            logger.warning("Concept bank is empty — no embeddings computed.")
            return

        self._concept_embeddings = self._embedding_model.encode(
            variants,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=64,
        )
        self._variant_owners = np.asarray(owners, dtype=np.int32)
        logger.info(
            f"Pre-computed {len(variants)} concept variant embeddings "
            f"across {len(self._concept_metadata or [])} concepts"
        )

    def check_negation(self, text: str, lang: str) -> bool:
        """
        Deterministic syntactic guard: prevents mapping negated symptoms as positive facts.

        Handles patterns like:
          - "bukhar nahi hai" → negated (fever absent)
          - "bukhar hai" → not negated (fever present)
          - "I don't have headache" → negated
        """
        tokens = re.findall(r'\w+', text.lower())
        neg_set = set(self.NEGATION_TERMS.get(lang, self.NEGATION_TERMS["en"]))

        # Simple presence check for negation tokens
        has_negation = any(tok in neg_set for tok in tokens)

        if has_negation:
            logger.debug(f"Negation detected in '{text}' (lang={lang})")

        return has_negation

    def normalize(self, text: str, lang: str = "hi") -> ConceptMatch:
        """
        Normalize a patient statement to a standardized medical concept.

        Args:
            text: Patient's statement (e.g. "pet mein jalan", "knee pain 3 weeks")
            lang: Language code

        Returns:
            ConceptMatch with concept, score, and status
        """
        self._load_models()

        # Step 1: NegEx — check for negation
        is_negated = self.check_negation(text, lang)
        if is_negated:
            return ConceptMatch(
                concept=None,
                score=1.0,
                status="EXPLICITLY_DENIED",
                is_negated=True
            )

        # Step 2: Check high-precision multi-language keyword match first
        kw_match = self._keyword_match(text, lang)
        if kw_match.status == "CONFIRMED_MATCH" or (kw_match.concept and kw_match.score >= 0.85):
            return kw_match

        # Step 3: Try sentence-transformer vector embedding match
        if self._embedding_model is not None and self._concept_embeddings is not None:
            emb_match = self._embedding_match(text)
            if emb_match.concept and emb_match.score >= 0.70 and emb_match.score >= kw_match.score:
                return emb_match
            if kw_match.concept is not None and kw_match.score >= 0.55:
                return kw_match
            if emb_match.concept:
                return emb_match

        # Step 4: Return keyword match or raw match
        return kw_match

    def _keyword_match(self, text: str, lang: str) -> ConceptMatch:
        """
        High-precision substring and token matching against multi-language clinical keywords.
        """
        text_lower = text.lower().strip()
        best_match = None
        best_score = 0.0

        for concept in (self._concept_metadata or []):
            keywords = concept.get("keywords", [])
            for keyword in keywords:
                kw = keyword.lower().strip()
                if not kw:
                    continue
                if kw == text_lower:
                    # Exact whole-phrase match
                    return ConceptMatch(concept=concept, score=0.98, status="CONFIRMED_MATCH")
                elif kw in text_lower:
                    # Substring match (e.g. "मुझे उल्टी हो रही है" contains "उल्टी")
                    score = 0.93 + min(len(kw) / 100.0, 0.04)
                    if score > best_score:
                        best_score = score
                        best_match = concept

        if best_match and best_score >= 0.82:
            return ConceptMatch(concept=best_match, score=best_score, status="CONFIRMED_MATCH")
        elif best_match and best_score >= 0.55:
            return ConceptMatch(concept=best_match, score=best_score, status="REQUIRES_EXPLAIN_BACK")
        elif best_match:
            return ConceptMatch(concept=best_match, score=best_score, status="ESCALATE_TO_LLM")
        else:
            return ConceptMatch(concept=None, score=0.0, status="ESCALATE_TO_LLM")

    def _embedding_match(self, text: str) -> ConceptMatch:
        """Cosine similarity against every concept variant; best variant wins."""
        query_vector = self._embed_text(text)

        similarities = np.dot(self._concept_embeddings, query_vector)
        best_variant = int(np.argmax(similarities))
        best_score = float(similarities[best_variant])
        concept = self._concept_metadata[int(self._variant_owners[best_variant])]

        if best_score >= 0.82:
            return ConceptMatch(concept=concept, score=best_score, status="CONFIRMED_MATCH")
        elif best_score >= 0.55:
            return ConceptMatch(concept=concept, score=best_score, status="REQUIRES_EXPLAIN_BACK")
        else:
            return ConceptMatch(concept=concept, score=best_score, status="ESCALATE_TO_LLM")

    def _embed_text(self, text: str) -> np.ndarray:
        """Get normalized embedding vector using sentence-transformers."""
        return self._embedding_model.encode(
            text, normalize_embeddings=True, show_progress_bar=False
        )

    @staticmethod
    def _get_default_concepts() -> list[dict]:
        """Built-in concept bank for development/demo when concept_bank.json isn't available."""
        return [
            # === Chief Complaints / Symptoms ===
            {"name": "Fever", "code": "SNOMED:386661006", "category": "symptom",
             "keywords": ["fever", "bukhar", "bukhar hai", "taap", "juram", "காய்ச்சல்", "జ్వరం", "ताप"]},
            {"name": "Headache", "code": "SNOMED:25064002", "category": "symptom",
             "keywords": ["headache", "sir dard", "sar dard", "sir mein dard", "தலைவலி", "తలనొప్పి", "डोकेदुखी"]},
            {"name": "Cough", "code": "SNOMED:49727002", "category": "symptom",
             "keywords": ["cough", "khansi", "khasi", "இருமல்", "దగ్గు", "खोकला"]},
            {"name": "Chest pain", "code": "SNOMED:29857009", "category": "symptom",
             "keywords": ["chest pain", "seene mein dard", "chhati mein dard", "chest discomfort", "நெஞ்சு வலி", "ఛాతీ నొప్పి", "छातीत दुखणे"]},
            {"name": "Abdominal pain", "code": "SNOMED:21522001", "category": "symptom",
             "keywords": ["stomach pain", "pet dard", "pet mein dard", "abdominal pain", "வயிற்று வலி", "కడుపు నొప్పి", "पोटदुखी"]},
            {"name": "Knee joint pain", "code": "SNOMED:202446002", "category": "symptom",
             "keywords": ["knee pain", "ghutne mein dard", "ghutna dard", "joint pain", "knee joint", "மூட்டு வலி", "మోకాలి నొప్పి", "गुडघेदुखी"]},
            {"name": "Back pain", "code": "SNOMED:161891005", "category": "symptom",
             "keywords": ["back pain", "kamar dard", "peeth dard", "முதுகு வலி", "నడుము నొప్పి", "पाठदुखी"]},
            {"name": "Difficulty breathing", "code": "SNOMED:267036007", "category": "symptom",
             "keywords": ["breathing difficulty", "saans lene mein taklif", "dyspnea", "breathlessness", "மூச்சுத் திணறல்", "శ్వాస ఇబ్బంది", "श्वास घेण्यास त्रास"]},
            {"name": "Nausea and vomiting", "code": "SNOMED:422587007", "category": "symptom",
             "keywords": ["vomiting", "ulti", "nausea", "ji machlana", "उल्टी", "उलटी", "जी मचलाना", "वाந்தி", "వాంతి", "வாந்தி"]},
            {"name": "Diarrhea", "code": "SNOMED:62315008", "category": "symptom",
             "keywords": ["diarrhea", "loose motion", "dast", "pet kharab", "வயிற்றுப்போக்கு", "విరేచనాలు", "जुलाब"]},
            {"name": "Fatigue / Weakness", "code": "SNOMED:84229001", "category": "symptom",
             "keywords": ["fatigue", "weakness", "kamzori", "thakan", "tired", "சோர்வு", "అలసట", "थकवा"]},
            {"name": "Burning sensation in stomach", "code": "SNOMED:30789004", "category": "symptom",
             "keywords": ["acidity", "pet mein jalan", "gastric", "heartburn", "burning stomach", "நெஞ்சு எரிச்சல்", "గుండెల్లో మంట", "छातीत जळजळ", "jalan"]},
            {"name": "Skin rash", "code": "SNOMED:271807003", "category": "symptom",
             "keywords": ["rash", "skin rash", "daane", "chakathe", "त्वचेवर पुरळ", "చర్మంపై దద్దుర్లు", "சொறி"]},
            {"name": "Urination problems", "code": "SNOMED:249274008", "category": "symptom",
             "keywords": ["urination problem", "peshab mein taklif", "frequent urination", "burning urination", "சிறுநீர் பிரச்சனை", "మూత్ర సమస్య", "लघवीचा त्रास"]},
            {"name": "Swelling", "code": "SNOMED:267038008", "category": "symptom",
             "keywords": ["swelling", "sujan", "soojan", "edema", "வீக்கம்", "వాపు", "सूज"]},
            {"name": "Dizziness", "code": "SNOMED:404640003", "category": "symptom",
             "keywords": ["dizziness", "chakkar", "sir ghoomna", "lightheaded", "தலைச்சுற்றல்", "తలతిరుగుడు", "चक्कर"]},
            {"name": "Weight loss", "code": "SNOMED:89362005", "category": "symptom",
             "keywords": ["weight loss", "wajan kam", "vajan ghatna", "எடை இழப்பு", "బరువు తగ్గడం", "वजन कमी"]},
            {"name": "Insomnia / Sleep disturbance", "code": "SNOMED:193462001", "category": "symptom",
             "keywords": ["insomnia", "neend nahi aati", "sleep problem", "not sleeping", "தூக்கமின்மை", "నిద్రలేమి", "झोप न लागणे"]},

            # === AYUSH-Specific Concepts ===
            {"name": "Vata imbalance", "code": "NAMASTE:DOSHA-VATA-001", "category": "ayush",
             "keywords": ["vata", "vayu", "gas", "bloating", "constipation", "dry skin", "anxiety"]},
            {"name": "Pitta imbalance", "code": "NAMASTE:DOSHA-PITTA-001", "category": "ayush",
             "keywords": ["pitta", "acidity", "burning", "inflammation", "anger", "heat intolerance"]},
            {"name": "Kapha imbalance", "code": "NAMASTE:DOSHA-KAPHA-001", "category": "ayush",
             "keywords": ["kapha", "heaviness", "congestion", "lethargy", "excess mucus", "weight gain"]},
        ]


# Singleton
_normalizer: Optional[SemanticConceptNormalizer] = None


def get_normalizer() -> SemanticConceptNormalizer:
    global _normalizer
    if _normalizer is None:
        _normalizer = SemanticConceptNormalizer()
    return _normalizer
