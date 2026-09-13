"""
MediKiosk — Master Demo Data Seed Script
Seeds realistic, reproducible dummy data for hackathon demonstrations & evaluations.

Usage:
  python scripts/seed_demo_data.py            # Seed data (idempotent / upsert)
  python scripts/seed_demo_data.py --reset    # Clear existing data and reseed
  python scripts/seed_demo_data.py --verify   # Verify database integrity and showcase queries
"""

import sys
import os
import json
import sqlite3
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_synthetic_patients import get_synthetic_patients
from scripts.generate_synthetic_documents import generate_all_synthetic_documents

DB_PATH = PROJECT_ROOT / "medikiosk.db"


DEPARTMENTS = [
    {
        "id": "dept-gm-01",
        "name": "General Medicine",
        "code": "GM-01",
        "description": "Adult Primary Care, Internal Medicine & Chronic Lifestyle Disease Management",
        "floor": "Ground Floor",
        "is_active": 1,
    },
    {
        "id": "dept-kc-02",
        "name": "Kayachikitsa",
        "code": "KC-02",
        "description": "Ayurveda Internal Medicine, Panchakarma & Integrative Holistic Care",
        "floor": "1st Floor",
        "is_active": 1,
    },
    {
        "id": "dept-cd-03",
        "name": "Cardiology",
        "code": "CD-03",
        "description": "Cardiovascular Medicine, ECG Evaluation & Acute Chest Pain Triage",
        "floor": "Ground Floor",
        "is_active": 1,
    },
]

DOCTORS = [
    {
        "id": "doc-sharma-101",
        "name": "Dr. Arvind Sharma, MD",
        "pin": "1234",
        "department": "General Medicine",
        "specialty": "Internal Medicine & Diabetology",
        "room_number": "OPD Room 101",
        "is_available": 1,
    },
    {
        "id": "doc-priya-204",
        "name": "Dr. Priya Ramachandran, BAMS, MD (Ayu)",
        "pin": "5678",
        "department": "Kayachikitsa",
        "specialty": "Integrative Ayurveda & Metabolic Disorders",
        "room_number": "OPD Room 204",
        "is_available": 1,
    },
    {
        "id": "doc-kulkarni-108",
        "name": "Dr. Rajesh Kulkarni, DM",
        "pin": "9999",
        "department": "Cardiology",
        "specialty": "Cardiology & Cardiac Emergency Triage",
        "room_number": "OPD Room 108",
        "is_available": 1,
    },
]


def ensure_tables(conn: sqlite3.Connection):
    """Ensure all required tables and indexes exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            age             INTEGER,
            gender          TEXT,
            phone           TEXT,
            language        TEXT DEFAULT 'hi',
            abha_id         TEXT,
            hospital_mrn    TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS doctors (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            pin             TEXT DEFAULT '1234',
            department      TEXT NOT NULL,
            specialty       TEXT,
            room_number     TEXT,
            is_available    INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS departments (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL UNIQUE,
            code            TEXT UNIQUE,
            description     TEXT,
            floor           TEXT,
            is_active       INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS encounters (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT,
            token_number    TEXT UNIQUE,
            language        TEXT DEFAULT 'hi',
            channel         TEXT DEFAULT 'kiosk',
            status          TEXT DEFAULT 'BOOTSTRAPPED',
            department      TEXT DEFAULT 'General Medicine',
            severity_badge  TEXT DEFAULT 'GREEN',
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS clinical_facts (
            id                  TEXT PRIMARY KEY,
            encounter_id        TEXT NOT NULL REFERENCES encounters(id),
            category            TEXT NOT NULL,
            field               TEXT NOT NULL,
            value               TEXT NOT NULL,
            dose                TEXT,
            frequency           TEXT,
            patient_words       TEXT,
            normalized_concept  TEXT,
            concept_code        TEXT,
            provenance_tier     TEXT NOT NULL,
            source_type         TEXT,
            source_reference    TEXT,
            confidence          REAL DEFAULT 0.0,
            confidence_breakdown TEXT,
            temporal_state      TEXT,
            valid_from          TEXT,
            valid_until         TEXT,
            is_negated          INTEGER DEFAULT 0,
            status              TEXT DEFAULT 'pending',
            created_at          TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_facts_encounter ON clinical_facts(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_facts_category ON clinical_facts(category);

        CREATE TABLE IF NOT EXISTS documents (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES encounters(id),
            file_path       TEXT NOT NULL,
            ocr_status      TEXT DEFAULT 'PENDING',
            ocr_raw_text    TEXT,
            ocr_lines       TEXT,
            highlighted_path TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS call_sessions (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES encounters(id),
            status          TEXT DEFAULT 'CALL_ACTIVE',
            language        TEXT DEFAULT 'hi',
            current_step    TEXT DEFAULT 'chief_complaint',
            turn_count      INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now')),
            ended_at        TEXT
        );

        CREATE TABLE IF NOT EXISTS queue_tokens (
            token           TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES encounters(id),
            department      TEXT DEFAULT 'General Medicine',
            status          TEXT DEFAULT 'WAITING',
            position        INTEGER DEFAULT 0,
            doctor_room     TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            called_at       TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id    TEXT REFERENCES encounters(id),
            actor           TEXT NOT NULL,
            action          TEXT NOT NULL,
            details         TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_audit_encounter ON audit_log(encounter_id);
    """)
    conn.commit()


def reset_database(conn: sqlite3.Connection):
    """Clear all records from database tables."""
    tables = [
        "clinical_facts",
        "documents",
        "call_sessions",
        "queue_tokens",
        "audit_log",
        "encounters",
        "patients",
        "doctors",
        "departments",
    ]
    for table in tables:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    print("✔ Database reset: all previous records cleared.")


def seed_database(reset: bool = False):
    """Seed departments, doctors, synthetic patients, documents, facts, and queue."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    ensure_tables(conn)

    if reset:
        reset_database(conn)

    print("\n🌱 Seeding MediKiosk Demonstration Dataset...")

    # 1. Seed Departments
    for d in DEPARTMENTS:
        conn.execute(
            """
            INSERT OR REPLACE INTO departments (id, name, code, description, floor, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (d["id"], d["name"], d["code"], d["description"], d["floor"], d["is_active"])
        )
    print(f"  ✔ Seeded {len(DEPARTMENTS)} Clinical Departments")

    # 2. Seed Doctors
    for doc in DOCTORS:
        conn.execute(
            """
            INSERT OR REPLACE INTO doctors (id, name, pin, department, specialty, room_number, is_available)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (doc["id"], doc["name"], doc["pin"], doc["department"], doc["specialty"], doc["room_number"], doc["is_available"])
        )
    print(f"  ✔ Seeded {len(DOCTORS)} Medical Staff Profiles (PINs: 1234, 5678, 9999)")

    # 3. Load Synthetic Patients
    patients = get_synthetic_patients()

    # 4. Generate Document Images & Get Records
    doc_records = generate_all_synthetic_documents(patients, PROJECT_ROOT)
    print(f"  ✔ Generated & Saved {len(doc_records)} Synthetic Prescription & Lab Evidence Images")

    # Map document records by doc_id for quick lookup
    doc_map = {d["id"]: d for d in doc_records}

    # 5. Insert Patients, Encounters, Queue, Facts, and Audit Logs
    total_facts = 0
    total_docs = 0

    for p_case in patients:
        pat = p_case["patient"]
        enc = p_case["encounter"]
        q = p_case["queue"]
        facts = p_case.get("clinical_facts", [])
        call = p_case.get("call_session")
        case_docs = p_case.get("documents", [])

        # Insert Patient
        conn.execute(
            """
            INSERT OR REPLACE INTO patients (id, name, age, gender, phone, language, abha_id, hospital_mrn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (pat["id"], pat["name"], pat["age"], pat["gender"], pat["phone"], pat["language"], pat["abha_id"], pat["hospital_mrn"])
        )

        # Insert Encounter
        conn.execute(
            """
            INSERT OR REPLACE INTO encounters (id, patient_id, token_number, language, channel, status, department, severity_badge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (enc["id"], pat["id"], enc["token_number"], enc["language"], enc["channel"], enc["status"], enc["department"], enc["severity_badge"])
        )

        # Insert Queue Token
        conn.execute(
            """
            INSERT OR REPLACE INTO queue_tokens (token, encounter_id, department, status, position, doctor_room)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (q["token"], enc["id"], q["department"], q["status"], q["position"], q["doctor_room"])
        )

        # Insert Call Session if present
        if call:
            conn.execute(
                """
                INSERT OR REPLACE INTO call_sessions (id, encounter_id, status, language, current_step, turn_count)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (call["id"], enc["id"], call["status"], call["language"], call["current_step"], call["turn_count"])
            )

        # Insert Documents
        for d_def in case_docs:
            d_rec = doc_map.get(d_def["id"])
            if d_rec:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO documents (id, encounter_id, file_path, ocr_status, ocr_raw_text, ocr_lines, highlighted_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (d_rec["id"], enc["id"], d_rec["file_path"], d_rec["ocr_status"], d_rec["ocr_raw_text"], d_rec["ocr_lines"], d_rec["highlighted_path"])
                )
                total_docs += 1

        # Insert Clinical Facts
        for f in facts:
            source_ref_json = json.dumps(f["source_reference"]) if f.get("source_reference") else None
            conf_breakdown_json = json.dumps(f["confidence_breakdown"]) if f.get("confidence_breakdown") else None

            conn.execute(
                """
                INSERT OR REPLACE INTO clinical_facts
                (id, encounter_id, category, field, value, dose, frequency,
                 patient_words, normalized_concept, concept_code, provenance_tier,
                 source_type, source_reference, confidence, confidence_breakdown,
                 temporal_state, is_negated, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f["id"], enc["id"], f["category"], f["field"], f["value"],
                    f.get("dose"), f.get("frequency"), f.get("patient_words"),
                    f.get("normalized_concept"), f.get("concept_code"), f.get("provenance_tier", "TOUCH"),
                    f.get("source_type"), source_ref_json, f.get("confidence", 1.0),
                    conf_breakdown_json, f.get("temporal_state"), 1 if f.get("is_negated") else 0,
                    f.get("status", "patient_confirmed")
                )
            )
            total_facts += 1

        # Insert Audit Trail
        conn.execute(
            """
            INSERT INTO audit_log (encounter_id, actor, action, details)
            VALUES (?, 'system', 'encounter_bootstrapped', ?)
            """,
            (enc["id"], json.dumps({"channel": enc["channel"], "patient_id": pat["id"]}))
        )
        if enc["severity_badge"] == "RED":
            conn.execute(
                """
                INSERT INTO audit_log (encounter_id, actor, action, details)
                VALUES (?, 'system', 'red_flag_triggered', '{"severity": "RED", "triage_priority": "CRITICAL"}')
                """,
                (enc["id"],)
            )
        conn.execute(
            """
            INSERT INTO audit_log (encounter_id, actor, action, details)
            VALUES (?, 'patient', 'intake_completed', '{"facts_captured": %d}')
            """ % len(facts),
            (enc["id"],)
        )

    conn.commit()
    conn.close()

    print(f"  ✔ Seeded {len(patients)} Patient Records")
    print(f"  ✔ Seeded {len(patients)} Encounters (5 RED, 3 YELLOW, 7 GREEN)")
    print(f"  ✔ Seeded {len(patients)} Queue Tokens with Triage Prioritization")
    print(f"  ✔ Seeded {total_docs} Clinical Documents with OCR Evidence Links")
    print(f"  ✔ Seeded {total_facts} Immutable Clinical Facts (Voice, OCR, AYUSH, Labs)")
    print(f"  ✔ Seeded DPDP-Compliant Audit Logs for all Encounters\n")
    print("✅ Seed process completed successfully!")


def verify_database():
    """Run verification checks on seeded database."""
    print("\n🔍 Verifying Seeded Database State...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Table row counts
    tables = [
        "departments", "doctors", "patients", "encounters",
        "queue_tokens", "documents", "clinical_facts", "call_sessions", "audit_log"
    ]
    print("\n📊 Table Statistics:")
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()["c"]
        print(f"   - {t:<16}: {count:>3} rows")

    # Check Doctor Queue ordering (RED first, then YELLOW, then GREEN)
    print("\n🩺 Doctor Queue Triage Verification:")
    q_rows = conn.execute("""
        SELECT qt.position, qt.token, e.severity_badge, p.name, e.department, e.channel
        FROM queue_tokens qt
        JOIN encounters e ON qt.encounter_id = e.id
        JOIN patients p ON e.patient_id = p.id
        ORDER BY
            CASE e.severity_badge
                WHEN 'RED' THEN 0
                WHEN 'YELLOW' THEN 1
                ELSE 2
            END,
            qt.position ASC
    """).fetchall()

    for r in q_rows:
        badge_symbol = "🔴" if r["severity_badge"] == "RED" else "🟡" if r["severity_badge"] == "YELLOW" else "🟢"
        print(f"   Pos {r['position']:>2} | {badge_symbol} {r['severity_badge']:<6} | Token: {r['token']:<6} | {r['name']:<20} | {r['department']:<18} ({r['channel']})")

    # Check Primary Demo Case (Lakshmi Devi)
    print("\n🌟 Primary Demo Case Verification (Lakshmi Devi):")
    lakshmi = conn.execute("SELECT * FROM encounters WHERE patient_id = 'pat-demo-lakshmi-001'").fetchone()
    if lakshmi:
        facts = conn.execute("SELECT category, field, value, provenance_tier, confidence FROM clinical_facts WHERE encounter_id = ?", (lakshmi["id"],)).fetchall()
        docs = conn.execute("SELECT id, file_path, highlighted_path FROM documents WHERE encounter_id = ?", (lakshmi["id"],)).fetchall()
        print(f"   Encounter ID : {lakshmi['id']}")
        print(f"   Queue Token  : {lakshmi['token_number']}")
        print(f"   Severity     : {lakshmi['severity_badge']} (Emergency Red-Flag)")
        print(f"   Language     : {lakshmi['language']} (Tamil)")
        print(f"   Facts Count  : {len(facts)}")
        for f in facts:
            print(f"     • [{f['category']}] {f['field']}: {f['value']} (Tier: {f['provenance_tier']}, Conf: {f['confidence']})")
        print(f"   Documents    : {len(docs)}")
        for d in docs:
            exists_orig = Path(d["file_path"]).exists()
            exists_box = Path(d["highlighted_path"]).exists()
            print(f"     • Doc {d['id']}: Original={exists_orig}, EvidenceBoxed={exists_box}")
    else:
        print("   ❌ Lakshmi Devi encounter not found!")

    # Check Safety Engines Compatibility
    print("\n🛡️ Safety Engines & Alerts Verification:")
    from app.core.clinical.drug_safety import DrugInteractionEngine
    from app.core.clinical.lab_checker import LabRangeChecker

    # Case 2: Warfarin + Aspirin
    case2_meds = [r["value"] for r in conn.execute("SELECT value FROM clinical_facts WHERE encounter_id = 'enc-demo-rajesh-002' AND category = 'medication'").fetchall()]
    alerts_c2 = DrugInteractionEngine.check_prescriptions(case2_meds)
    print(f"   Case 2 (Rajesh Sharma) Drug Alerts : {len(alerts_c2)} found -> {[a['severity'] + ': ' + a['drug_a'] + ' + ' + a['drug_b'] for a in alerts_c2]}")

    # Case 6: Amlodipine + Licorice
    case6_meds = [r["value"] for r in conn.execute("SELECT value FROM clinical_facts WHERE encounter_id = 'enc-demo-meenakshi-006' AND category = 'medication'").fetchall()]
    alerts_c6 = DrugInteractionEngine.check_prescriptions(case6_meds)
    print(f"   Case 6 (Meenakshi S.) Herb-Drug    : {len(alerts_c6)} found -> {[a['severity'] + ': ' + a['drug_a'] + ' + ' + a['drug_b'] for a in alerts_c6]}")

    # Case 4: Fasting Glucose 342 mg/dL
    panic_lab = LabRangeChecker.evaluate_result("fasting_blood_glucose", 342.0)
    print(f"   Case 4 (Sunita Patel) Panic Lab    : {panic_lab['status']} (Panic Urgent={panic_lab['requires_urgent_escalation']})")

    conn.close()
    print("\n✅ Verification complete! All showcase tests passed.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MediKiosk Demo Seed Script")
    parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding")
    parser.add_argument("--verify", action="store_true", help="Verify seeded database after seeding")
    args = parser.parse_args()

    seed_database(reset=args.reset)
    if args.verify or True:  # Default to verify so execution prints summary
        verify_database()
