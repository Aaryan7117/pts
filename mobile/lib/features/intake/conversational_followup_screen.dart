import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/choice_card.dart';
import '../../core/widgets/primary_button.dart';

/// Question category for SOCRATES & AYUSH adaptive questioning
enum FollowupQuestionType {
  severity,
  duration,
  medications,
  allergies,
  agni,
  koshtha,
  prakriti,
  generalYesNo,
}

/// Screen 08 — Conversational Follow-up (SOCRATES Adaptive Questioning)
/// Adaptive clinical follow-up questions with massive tactile choices in 5 native Indian scripts
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 08)
class ConversationalFollowupScreen extends StatefulWidget {
  const ConversationalFollowupScreen({super.key});

  @override
  State<ConversationalFollowupScreen> createState() => _ConversationalFollowupScreenState();
}

class _ConversationalFollowupScreenState extends State<ConversationalFollowupScreen> {
  String _selectedAnswer = '';

  static FollowupQuestionType _detectQuestionType(String question) {
    final q = question.toLowerCase();

    // 1. Severity Scale
    if (q.contains('1-10') ||
        q.contains('1 to 10') ||
        q.contains('1 से 10') ||
        q.contains('1 முதல் 10') ||
        q.contains('1 నుండి 10') ||
        q.contains('1 ते 10') ||
        q.contains('scale') ||
        q.contains('severity') ||
        q.contains('पैमाने') ||
        q.contains('तकलीफ कितनी') ||
        q.contains('दर्द कितना') ||
        q.contains('கடுமையானது') ||
        q.contains('வலி எவ்வளவு') ||
        q.contains('తీవ్రంగా') ||
        q.contains('నొప్పి ఎంత') ||
        q.contains('प्रमाणात') ||
        q.contains('किती तीव्र')) {
      return FollowupQuestionType.severity;
    }

    // 2. Duration
    if (q.contains('duration') ||
        q.contains('how long') ||
        q.contains('कब से') ||
        q.contains('दिन') ||
        q.contains('हफ्ते') ||
        q.contains('महीने') ||
        q.contains('காலமாக') ||
        q.contains('நாட்கள்') ||
        q.contains('வாரங்கள்') ||
        q.contains('எంతకాలంగా') ||
        q.contains('రోజులు') ||
        q.contains('వారాలు') ||
        q.contains('నెలలు') ||
        q.contains('किती दिवसांपासून') ||
        q.contains('कधीपासून') ||
        q.contains('आठवडे') ||
        q.contains('महिने')) {
      return FollowupQuestionType.duration;
    }

    // 3. Medications
    if (q.contains('medicat') ||
        q.contains('medicine') ||
        q.contains('prescript') ||
        q.contains('दवाई') ||
        q.contains('दवाइयाँ') ||
        q.contains('दवा') ||
        q.contains('மருந்து') ||
        q.contains('మందు') ||
        q.contains('औषध')) {
      return FollowupQuestionType.medications;
    }

    // 4. Allergies
    if (q.contains('allerg') ||
        q.contains('reaction') ||
        q.contains('एलर्जी') ||
        q.contains('ஒவ்வாமை') ||
        q.contains('అలర్జీ') ||
        q.contains('अॅलर्जी') ||
        q.contains('अलर्जी')) {
      return FollowupQuestionType.allergies;
    }

    // 5. AYUSH Agni (Digestion / Appetite)
    if (q.contains('appetite') ||
        q.contains('heaviness') ||
        q.contains('agni') ||
        q.contains('भूख') ||
        q.contains('अग्नि') ||
        q.contains('पेट भारी') ||
        q.contains('पाचन') ||
        q.contains('பசி') ||
        q.contains('அக்னி') ||
        q.contains('செரிமான') ||
        q.contains('ఆకలి') ||
        q.contains('అగ్ని') ||
        q.contains('జీర్ణం') ||
        q.contains('भूक') ||
        q.contains('अग्नी') ||
        q.contains('पोट जड')) {
      return FollowupQuestionType.agni;
    }

    // 6. AYUSH Koshtha (Bowel pattern)
    if (q.contains('bowel') ||
        q.contains('stool') ||
        q.contains('koshtha') ||
        q.contains('constipat') ||
        q.contains('कोष्ठ') ||
        q.contains('पेट साफ') ||
        q.contains('शौच') ||
        q.contains('कब्ज') ||
        q.contains('கோஷ்ட') ||
        q.contains('மலம்') ||
        q.contains('மலச்சிக்கல்') ||
        q.contains('కోష్ఠ') ||
        q.contains('మలవిసర్జన') ||
        q.contains('మలబద్ధకం') ||
        q.contains('बद्धकोष्ठता')) {
      return FollowupQuestionType.koshtha;
    }

    // 7. AYUSH Prakriti (Constitution / Sensitivity)
    if (q.contains('cold, heat') ||
        q.contains('prakriti') ||
        q.contains('skin dry') ||
        q.contains('humidity') ||
        q.contains('ठंड ज़्यादा') ||
        q.contains('गर्मी ज़्यादा') ||
        q.contains('प्रकृति') ||
        q.contains('त्वचा') ||
        q.contains('குளிர்') ||
        q.contains('வெப்பம்') ||
        q.contains('ஈரப்பதம்') ||
        q.contains('தோல்') ||
        q.contains('చలి') ||
        q.contains('వేడి') ||
        q.contains('తేమ') ||
        q.contains('చర్మం') ||
        q.contains('थंडी') ||
        q.contains('उष्णता') ||
        q.contains('ओलसरपणा')) {
      return FollowupQuestionType.prakriti;
    }

    return FollowupQuestionType.generalYesNo;
  }

  static String _getFallbackQuestion(String langCode) {
    switch (langCode) {
      case 'ta':
        return 'இந்த அறிகுறிகளுடன் தலைச்சுற்றல் அல்லது வாந்தி போன்ற உணர்வு உள்ளதா?';
      case 'te':
        return 'ఈ లక్షణాలతో పాటు మీకు తలతిరగడం లేదా వాంతులు వచ్చినట్లు అనిపిస్తుందా?';
      case 'mr':
        return 'या लक्षणांसोबत तुम्हाला चक्कर किंवा उलट्या आल्यासारखे वाटत आहे का?';
      case 'hi':
        return 'क्या आपको इन लक्षणों के साथ चक्कर या उल्टी जैसा लग रहा है?';
      case 'en':
      default:
        return 'Are you experiencing any dizziness or nausea alongside your symptoms?';
    }
  }

  List<Map<String, String>> _getOptionsForQuestion(String question, String langCode) {
    final qType = _detectQuestionType(question);

    switch (qType) {
      case FollowupQuestionType.severity:
        switch (langCode) {
          case 'ta':
            return [
              {'title': '1 - 3 : லேசான வலி', 'subtitle': 'வழக்கமான வேலைகளில் பெரிய பாதிப்பு இல்லை', 'val': '1-3 Mild'},
              {'title': '4 - 6 : மிதமான வலி', 'subtitle': 'தினசரி பணிகளில் குறிப்பிடத்தக்க அசௌகரியம்', 'val': '4-6 Moderate'},
              {'title': '7 - 10 : கடுமையான வலி', 'subtitle': 'தாங்க முடியாத வலி, வேலை செய்ய இயலாது', 'val': '7-10 Severe'},
            ];
          case 'te':
            return [
              {'title': '1 - 3 : తేలికపాటి నొప్పి', 'subtitle': 'సాధారణ పనులకు అంతరాయం కలగదు', 'val': '1-3 Mild'},
              {'title': '4 - 6 : మోస్తరు నొప్పి', 'subtitle': 'రోజువారీ పనులకు ఇబ్బందిగా ఉంది', 'val': '4-6 Moderate'},
              {'title': '7 - 10 : తీవ్రమైన నొప్పి', 'subtitle': 'భరించలేని నొప్పి, పనులు చేయడం కష్టం', 'val': '7-10 Severe'},
            ];
          case 'mr':
            return [
              {'title': '1 - 3 : सौम्य वेदना', 'subtitle': 'दैनंदिन कामात फारसा अडथळा नाही', 'val': '1-3 Mild'},
              {'title': '4 - 6 : मध्यम वेदना', 'subtitle': 'रोजच्या कामांमध्ये लक्षणीय त्रास होतो', 'val': '4-6 Moderate'},
              {'title': '7 - 10 : तीव्र वेदना', 'subtitle': 'असह्य वेदना, हालचाल करणे कठीण', 'val': '7-10 Severe'},
            ];
          case 'hi':
            return [
              {'title': '1 - 3 : हल्का दर्द', 'subtitle': 'सामान्य दिनचर्या में कोई रुकावट नहीं', 'val': '1-3 Mild'},
              {'title': '4 - 6 : मध्यम दर्द', 'subtitle': 'दैनिक कार्यों में परेशानी हो रही है', 'val': '4-6 Moderate'},
              {'title': '7 - 10 : तेज / असहनीय दर्द', 'subtitle': 'असहनीय दर्द, काम करना मुश्किल', 'val': '7-10 Severe'},
            ];
          case 'en':
          default:
            return [
              {'title': '1 - 3 : Mild Pain', 'subtitle': 'Noticeable discomfort but routine activities unimpaired', 'val': '1-3 Mild'},
              {'title': '4 - 6 : Moderate Pain', 'subtitle': 'Significant pain interfering with daily routine', 'val': '4-6 Moderate'},
              {'title': '7 - 10 : Severe Pain', 'subtitle': 'Unbearable pain, unable to perform basic functions', 'val': '7-10 Severe'},
            ];
        }

      case FollowupQuestionType.duration:
        switch (langCode) {
          case 'ta':
            return [
              {'title': '1 - 2 நாட்கள்', 'subtitle': 'இன்று அல்லது நேற்றிலிருந்து தொடங்கியது', 'val': '1-2 Days'},
              {'title': '3 - 7 நாட்கள்', 'subtitle': 'சுமார் ஒரு வாரமாக நீடிக்கிறது', 'val': '3-7 Days'},
              {'title': '2 - 4 வாரங்கள்', 'subtitle': 'பல வாரங்களாகத் தொடர்கிறது', 'val': '2-4 Weeks'},
              {'title': '1 மாதத்திற்கும் மேல்', 'subtitle': 'நீண்டகால தொடர் பிரச்சனை', 'val': 'Over 1 Month'},
            ];
          case 'te':
            return [
              {'title': '1 - 2 రోజులు', 'subtitle': 'ఈరోజు లేదా నిన్నటి నుండి ప్రారంభమైంది', 'val': '1-2 Days'},
              {'title': '3 - 7 రోజులు', 'subtitle': 'సుమారు ఒక వారం నుండి ఉంది', 'val': '3-7 Days'},
              {'title': '2 - 4 వారాలు', 'subtitle': 'కొన్ని వారాలుగా కొనసాగుతోంది', 'val': '2-4 Weeks'},
              {'title': '1 నెలకు పైగా', 'subtitle': 'చాలా కాలంగా ఉన్న దీర్ఘకాలిక సమస్య', 'val': 'Over 1 Month'},
            ];
          case 'mr':
            return [
              {'title': '1 - 2 दिवस', 'subtitle': 'आज किंवा कालपासून सुरू झाले', 'val': '1-2 Days'},
              {'title': '3 - 7 दिवस', 'subtitle': 'सुमारे एका आठवड्यापासून त्रास आहे', 'val': '3-7 Days'},
              {'title': '2 - 4 आठवडे', 'subtitle': 'काही आठवड्यांपासून सुरू आहे', 'val': '2-4 Weeks'},
              {'title': '1 महिन्यापेक्षा जास्त', 'subtitle': 'दीर्घकालीन जुनाट समस्या', 'val': 'Over 1 Month'},
            ];
          case 'hi':
            return [
              {'title': '1 - 2 दिन', 'subtitle': 'आज या कल से शुरू हुआ', 'val': '1-2 Days'},
              {'title': '3 - 7 दिन', 'subtitle': 'लगभग एक हफ्ते से चल रहा है', 'val': '3-7 Days'},
              {'title': '2 - 4 हफ्ते', 'subtitle': 'कई हफ्तों से यह परेशानी बनी हुई है', 'val': '2-4 Weeks'},
              {'title': '1 महीने से अधिक', 'subtitle': 'काफी समय से पुरानी समस्या है', 'val': 'Over 1 Month'},
            ];
          case 'en':
          default:
            return [
              {'title': '1 - 2 Days', 'subtitle': 'Acute onset within the past 48 hours', 'val': '1-2 Days'},
              {'title': '3 - 7 Days', 'subtitle': 'Ongoing for several days this week', 'val': '3-7 Days'},
              {'title': '2 - 4 Weeks', 'subtitle': 'Sub-acute symptoms lasting weeks', 'val': '2-4 Weeks'},
              {'title': 'Over 1 Month', 'subtitle': 'Chronic persistent problem', 'val': 'Over 1 Month'},
            ];
        }

      case FollowupQuestionType.medications:
        switch (langCode) {
          case 'ta':
            return [
              {'title': 'மருந்துகள் எதுவும் எடுக்கவில்லை', 'subtitle': 'வழக்கமான மருந்துகள் எதுவும் இல்லை', 'val': 'No current medications'},
              {'title': 'வழக்கமான மருந்துகள் எடுக்கிறேன்', 'subtitle': 'ரத்த அழுத்தம், சர்க்கரை அல்லது தைராய்டு மாத்திரை', 'val': 'Taking regular chronic medications'},
              {'title': 'வலி நிவாரணி / பாராசிட்டமால் எடுத்தேன்', 'subtitle': 'சமீபத்தில் தற்காலிக நிவாரண மாத்திரை உட்கொண்டேன்', 'val': 'Took OTC Paracetamol'},
            ];
          case 'te':
            return [
              {'title': 'మందులు ఏవీ వాడటం లేదు', 'subtitle': 'ఎలాంటి సాధారణ మందులు తీసుకోవడం లేదు', 'val': 'No current medications'},
              {'title': 'రెగ్యులర్ మందులు వాడుతున్నాను', 'subtitle': 'బీపీ, షుగర్ లేదా థైరాయిడ్ రోజువారీ మందులు', 'val': 'Taking regular chronic medications'},
              {'title': 'పెయిన్ కిల్లర్ / పారాసిటమాల్ తీసుకున్నాను', 'subtitle': 'ఇటీవల తాత్కాలిక ఉపశమనం కోసం తీసుకున్నాను', 'val': 'Took OTC Paracetamol'},
            ];
          case 'mr':
            return [
              {'title': 'कोणतीही औषधे घेत नाही', 'subtitle': 'कोणतीही नियमित औषधे चालू नाहीत', 'val': 'No current medications'},
              {'title': 'नियमित औषधे सुरू आहेत', 'subtitle': 'बीपी, शुगर किंवा थायरॉईडची रोजची औषधे', 'val': 'Taking regular chronic medications'},
              {'title': 'पेनकिलर / पॅरासिटामॉल घेतली', 'subtitle': 'नुकतीच दुखण्यावर तात्पुरती गोळी घेतली', 'val': 'Took OTC Paracetamol'},
            ];
          case 'hi':
            return [
              {'title': 'कोई दवा नहीं ले रहे', 'subtitle': 'कोई नियमित या डॉक्टर की दवा नहीं चल रही', 'val': 'No current medications'},
              {'title': 'नियमित दवाएं चल रही हैं', 'subtitle': 'बीपी, शुगर या थायरॉइड की नियमित दवा', 'val': 'Taking regular chronic medications'},
              {'title': 'दर्द निवारक / पैरासिटामोल ली', 'subtitle': 'हाल ही में राहत के लिए अस्थायी गोली ली', 'val': 'Took OTC Paracetamol'},
            ];
          case 'en':
          default:
            return [
              {'title': 'No Current Medications', 'subtitle': 'Not on any regular or prescription drugs', 'val': 'No current medications'},
              {'title': 'Taking Regular Chronic Medicines', 'subtitle': 'Taking daily BP, sugar, or thyroid medication', 'val': 'Taking regular chronic medications'},
              {'title': 'Took Painkiller / Paracetamol', 'subtitle': 'Over-the-counter temporary relief taken recently', 'val': 'Took OTC Paracetamol'},
            ];
        }

      case FollowupQuestionType.allergies:
        switch (langCode) {
          case 'ta':
            return [
              {'title': 'எந்த ஒவ்வாமையும் இல்லை', 'subtitle': 'மருந்துகளால் எந்த ஒவ்வாமை எதிர்வினையும் ஏற்பட்டதில்லை', 'val': 'No drug allergies'},
              {'title': 'ஆம், மருந்து ஒவ்வாமை உண்டு', 'subtitle': 'ஆண்டிபயாடிக் அல்லது மாத்திரைகளால் ஒவ்வாமை', 'val': 'Yes, has drug allergy'},
              {'title': 'உறுதியாகத் தெரியவில்லை', 'subtitle': 'இதுவரை ஒவ்வாமை சோதனை செய்யவில்லை', 'val': 'Unsure about allergies'},
            ];
          case 'te':
            return [
              {'title': 'ఎలాంటి అలర్జీ లేదు', 'subtitle': 'మందుల వల్ల ఎప్పుడూ ఇబ్బంది కలగలేదు', 'val': 'No drug allergies'},
              {'title': 'అవును, మందుల అలర్జీ ఉంది', 'subtitle': 'యాంటీబయాటిక్స్ లేదా పెయిన్ కిల్లర్లతో అలర్జీ', 'val': 'Yes, has drug allergy'},
              {'title': 'ఖచ్చితంగా తెలియదు', 'subtitle': 'మందుల అలర్జీ గురించి స్పష్టత లేదు', 'val': 'Unsure about allergies'},
            ];
          case 'mr':
            return [
              {'title': 'कोणतीही अॅलर्जी नाही', 'subtitle': 'औषधांमुळे कधीही त्रास झालेला नाही', 'val': 'No drug allergies'},
              {'title': 'होय, औषधांची अॅलर्जी आहे', 'subtitle': 'अँटिबायोटिक किंवा इतर गोळ्यांची अॅलर्जी', 'val': 'Yes, has drug allergy'},
              {'title': 'नक्की माहिती नाही', 'subtitle': 'अॅलर्जीबद्दल स्पष्ट माहिती नाही', 'val': 'Unsure about allergies'},
            ];
          case 'hi':
            return [
              {'title': 'कोई एलर्जी नहीं है', 'subtitle': 'दवाइयों से कभी कोई दुष्प्रभाव नहीं हुआ', 'val': 'No drug allergies'},
              {'title': 'हाँ, दवा से एलर्जी है', 'subtitle': 'एंटीबायोटिक या दर्द की दवा से एलर्जी का इतिहास', 'val': 'Yes, has drug allergy'},
              {'title': 'पक्का नहीं पता', 'subtitle': 'कभी दवा एलर्जी की जांच या अनुभव नहीं हुआ', 'val': 'Unsure about allergies'},
            ];
          case 'en':
          default:
            return [
              {'title': 'No Known Drug Allergy', 'subtitle': 'Never had an adverse drug reaction', 'val': 'No drug allergies'},
              {'title': 'Yes, Allergic to Medicines', 'subtitle': 'History of reaction (e.g. Penicillin, Sulfa)', 'val': 'Yes, has drug allergy'},
              {'title': 'Unsure / Never Checked', 'subtitle': 'Not aware of any specific drug allergies', 'val': 'Unsure about allergies'},
            ];
        }

      case FollowupQuestionType.agni:
        switch (langCode) {
          case 'ta':
            return [
              {'title': 'சம அக்னி : சீரான செரிமானம்', 'subtitle': 'சரியான நேரத்தில் பசி, இயல்பான செரிமானம்', 'val': 'Sama Agni'},
              {'title': 'விஷம அக்னி : மாறுபடும் பசி / வாயு', 'subtitle': 'சில நேரம் அதிக பசி, சில நேரம் பசியின்மை, வாயு', 'val': 'Vishama Agni'},
              {'title': 'தீக்ஷ்ண அக்னி : தீவிர பசி / நெஞ்செரிச்சல்', 'subtitle': 'அளவுக்கு அதிகமான பசி, நெஞ்செரிச்சல், அசிடிட்டி', 'val': 'Tikshna Agni'},
              {'title': 'மந்த அக்னி : மந்த செரிமானம் / பாரம்', 'subtitle': 'பசியின்மை, சாப்பிட்ட பிறகு வயிறு கனமாக இருத்தல்', 'val': 'Manda Agni'},
            ];
          case 'te':
            return [
              {'title': 'సమ అగ్ని : సమతుల్య జీర్ణక్రియ', 'subtitle': 'సమయానికి ఆకలి, సులభంగా జీర్ణం కావడం', 'val': 'Sama Agni'},
              {'title': 'విషమ అగ్ని : అస్థిర ఆకలి / గ్యాస్', 'subtitle': 'ఒక్కోసారి ఎక్కువ ఆకలి, ఒక్కోసారి లేకపోవడం, గ్యాస్', 'val': 'Vishama Agni'},
              {'title': 'తీక్షణ అగ్ని : అధిక ఆకలి / మంట', 'subtitle': 'తీవ్రమైన ఆకలి, ఎసిడిటీ, ఛాతీలో మంట', 'val': 'Tikshna Agni'},
              {'title': 'మంద అగ్ని : మందగించిన ఆకలి / భారం', 'subtitle': 'ఆకలి లేకపోవడం, భోజనం తర్వాత కడుపు భారం', 'val': 'Manda Agni'},
            ];
          case 'mr':
            return [
              {'title': 'सम अग्नी : संतुलित पचन', 'subtitle': 'वेळेवर भूक, सहज आणि योग्य पचन', 'val': 'Sama Agni'},
              {'title': 'विषम अग्नी : अनियमित भूक व गॅस', 'subtitle': 'कधी जास्त भूक, कधी अजिबात नाही, गॅसेस', 'val': 'Vishama Agni'},
              {'title': 'तीक्ष्ण अग्नी : अति भूक व जळजळ', 'subtitle': 'खूप भूक लागणे, ॲसिडिटी, छातीत जळजळ', 'val': 'Tikshna Agni'},
              {'title': 'मंद अग्नी : मंद भूक व जडपणा', 'subtitle': 'भूक मंदावणे, जेवणानंतर पोट जड वाटणे', 'val': 'Manda Agni'},
            ];
          case 'hi':
            return [
              {'title': 'सम अग्नि : सामान्य भूख व पाचन', 'subtitle': 'समय पर भूख लगना, बिना परेशानी के भोजन पचना', 'val': 'Sama Agni'},
              {'title': 'विषम अग्नि : अनिश्चित भूख व गैस', 'subtitle': 'कभी बहुत भूख, कभी भूख न लगना, पेट में गैस', 'val': 'विषम अग्नि'},
              {'title': 'तीक्ष्ण अग्नि : तेज भूख व एसिडिटी', 'subtitle': 'बहुत अधिक भूख, सीने में जलन, खट्टी डकारें', 'val': 'तीक्ष्ण अग्नि'},
              {'title': 'मंद अग्नि : कम भूख व भारीपन', 'subtitle': 'भूख न लगना, खाना खाने के बाद पेट भारी रहना', 'val': 'मंद अग्नि'},
            ];
          case 'en':
          default:
            return [
              {'title': 'Sama Agni : Balanced Digestion', 'subtitle': 'Regular appetite, timely digestion without discomfort', 'val': 'Sama Agni'},
              {'title': 'Vishama Agni : Irregular / Gas', 'subtitle': 'Variable hunger, bloating, gas, irregular digestion', 'val': 'Vishama Agni'},
              {'title': 'Tikshna Agni : Sharp / Burning', 'subtitle': 'Intense hunger, acid reflux, burning in stomach/chest', 'val': 'Tikshna Agni'},
              {'title': 'Manda Agni : Sluggish / Heavy', 'subtitle': 'Poor appetite, heavy sensation in stomach after food', 'val': 'Manda Agni'},
            ];
        }

      case FollowupQuestionType.koshtha:
        switch (langCode) {
          case 'ta':
            return [
              {'title': 'மத்யம கோஷ்டம் : சீரான மலம்', 'subtitle': 'தினசரி ஒரு முறை இயல்பான மலம் கழித்தல்', 'val': 'Madhyama Koshtha'},
              {'title': 'க்ரூர கோஷ்டம் : மலச்சிக்கல்', 'subtitle': 'கடினமான உலர் மலம், மலம் கழிக்க சிரமம்', 'val': 'Krura Koshtha'},
              {'title': 'மிருது கோஷ்டம் : தளர்வான மலம்', 'subtitle': 'தினமும் இருமுறை அல்லது அதற்கு மேல், தளர்வான மலம்', 'val': 'Mridu Koshtha'},
            ];
          case 'te':
            return [
              {'title': 'మధ్యమ కోష్ఠం : సాధారణ విసర్జన', 'subtitle': 'రోజుకు ఒకసారి సులభంగా మలవిసర్జన', 'val': 'Madhyama Koshtha'},
              {'title': 'క్రూర కోష్ఠం : మలబద్ధకం', 'subtitle': 'గట్టిగా పొడిగా రావడం, ఇబ్బందిగా ఉండటం', 'val': 'Krura Koshtha'},
              {'title': 'మృదు కోష్ఠం : తరచుగా / వదులుగా', 'subtitle': 'రోజుకు రెండు లేదా అంతకంటే ఎక్కువ సార్లు', 'val': 'Mridu Koshtha'},
            ];
          case 'mr':
            return [
              {'title': 'मध्यम कोष्ठ : नियमित शौच', 'subtitle': 'दिवसातून एकदा सामान्यपणे पोट साफ होणे', 'val': 'Madhyama Koshtha'},
              {'title': 'क्रूर कोष्ठ : बद्धकोष्ठता', 'subtitle': 'कठीण व कोरडे शौच, त्रास होतो', 'val': 'Krura Koshtha'},
              {'title': 'मृदू कोष्ठ : पातळ किंवा वारंवार', 'subtitle': 'दिवसातून दोन किंवा जास्त वेळा, पातळ शौच', 'val': 'Mridu Koshtha'},
            ];
          case 'hi':
            return [
              {'title': 'मध्यम कोष्ठ : नियमित शौच', 'subtitle': 'रोजाना एक बार सामान्य रूप से पेट साफ होना', 'val': 'Madhyama Koshtha'},
              {'title': 'क्रूर कोष्ठ : कब्ज व कड़ा मल', 'subtitle': 'मल कड़ा व सूखा, शौच में जोर लगाना पड़ना', 'val': 'क्रूर कोष्ठ'},
              {'title': 'मृदु कोष्ठ : बार-बार या ढीला मल', 'subtitle': 'दिन में 2 या अधिक बार, पतला या ढीला मल', 'val': 'मृदु कोष्ठ'},
            ];
          case 'en':
          default:
            return [
              {'title': 'Madhyama Koshtha : Regular', 'subtitle': 'Once daily bowel movement, normal consistency', 'val': 'Madhyama Koshtha'},
              {'title': 'Krura Koshtha : Hard / Constipated', 'subtitle': 'Hard dry stool, straining, once in 2-3 days', 'val': 'Krura Koshtha'},
              {'title': 'Mridu Koshtha : Soft / Loose', 'subtitle': 'Twice or more daily, loose or soft motion', 'val': 'Mridu Koshtha'},
            ];
        }

      case FollowupQuestionType.prakriti:
        switch (langCode) {
          case 'ta':
            return [
              {'title': 'குளிர் தாங்க இயலாமை / வறண்ட தோல்', 'subtitle': 'குளிர் காற்று ஆகாது, மூட்டு வலி, வறண்ட தோல் (வாதம்)', 'val': 'Vata Cold Sensitivity'},
              {'title': 'வெப்பம் தாங்க இயலாமை / சூடான தோல்', 'subtitle': 'வெயில் ஆகாது, அதிக வியர்வை, சூடான தோல் (பித்தம்)', 'val': 'Pitta Heat Sensitivity'},
              {'title': 'ஈரப்பதம் தாங்க இயலாமை / எண்ணெய் பசை', 'subtitle': 'குளிர்/ஈரப்பதத்தால் சளி, பாரம், எண்ணெய் தோல் (கபம்)', 'val': 'Kapha Damp Sensitivity'},
            ];
          case 'te':
            return [
              {'title': 'చలి పడకపోవడం / పొడి చర్మం', 'subtitle': 'చల్లని వాతావరణం పడదు, పొడి చర్మం, కీళ్ల నొప్పులు (వాతం)', 'val': 'Vata Cold Sensitivity'},
              {'title': 'వేడి పడకపోవడం / వెచ్చని చర్మం', 'subtitle': 'ఎండ వేడి తట్టుకోలేకపోవడం, అధిక చెమట (పిత్తం)', 'val': 'Pitta Heat Sensitivity'},
              {'title': 'తేమ పడకపోవడం / జిడ్డు చర్మం', 'subtitle': 'తేమ వాతావరణంలో బరువుగా అనిపించడం, జిడ్డు చర్మం (కఫం)', 'val': 'Kapha Damp Sensitivity'},
            ];
          case 'mr':
            return [
              {'title': 'थंडीचा त्रास / कोरडी त्वचा', 'subtitle': 'थंड हवा सहन न होणे, कोरडी त्वचा, सांधेदुखी (वात)', 'val': 'Vata Cold Sensitivity'},
              {'title': 'उष्णतेचा त्रास / गरम त्वचा', 'subtitle': 'ऊन सहन न होणे, जास्त घाम, अंगाची आग (पित्त)', 'val': 'Pitta Heat Sensitivity'},
              {'title': 'दमटपणाचा त्रास / तेलकट त्वचा', 'subtitle': 'ओलसर हवेने जड वाटणे, तेलकट त्वचा, आळस (कफ)', 'val': 'Kapha Damp Sensitivity'},
            ];
          case 'hi':
            return [
              {'title': 'ठंड से परेशानी / रूखी त्वचा', 'subtitle': 'ठंडी हवा असहनीय, सूखी त्वचा व जोड़ों में खिंचाव (वात)', 'val': 'वात ठंड से परेशानी'},
              {'title': 'गर्मी से परेशानी / गर्म त्वचा', 'subtitle': 'धूप व गर्मी असहनीय, अधिक पसीना व जलन (पित्त)', 'val': 'पित्त गर्मी से परेशानी'},
              {'title': 'नमी व ठंड से परेशानी / चिकनी त्वचा', 'subtitle': 'गीले मौसम में भारीपन, चिकनी त्वचा व सुस्ती (कफ)', 'val': 'कफ नमी से परेशानी'},
            ];
          case 'en':
          default:
            return [
              {'title': 'Cold Sensitive / Dry Skin', 'subtitle': 'Intolerant to cold weather, dry skin or cracking joints (Vata)', 'val': 'Vata Cold Sensitivity'},
              {'title': 'Heat Sensitive / Warm Skin', 'subtitle': 'Intolerant to hot climate, excessive sweating, reddish skin (Pitta)', 'val': 'Pitta Heat Sensitivity'},
              {'title': 'Damp-Cold Sensitive / Cool Skin', 'subtitle': 'Intolerant to damp cold, heavy build, oily smooth skin (Kapha)', 'val': 'Kapha Damp Sensitivity'},
            ];
        }

      case FollowupQuestionType.generalYesNo:
        switch (langCode) {
          case 'ta':
            return [
              {'title': 'ஆம்', 'subtitle': 'இந்த அறிகுறி உள்ளது', 'val': 'Yes'},
              {'title': 'இல்லை', 'subtitle': 'இந்த பிரச்சனை இல்லை', 'val': 'No'},
              {'title': 'எப்போதாவது / லேசாக', 'subtitle': 'லேசான அல்லது எப்போதாவது ஏற்படும் உணர்வு', 'val': 'Mild occasional'},
            ];
          case 'te':
            return [
              {'title': 'అవును', 'subtitle': 'ఈ లక్షణం ఉంది', 'val': 'Yes'},
              {'title': 'లేదు', 'subtitle': 'ఈ సమస్య లేదు', 'val': 'No'},
              {'title': 'అప్పుడప్పుడు / కొద్దిగా', 'subtitle': 'తేలికపాటి లేదా అప్పుడప్పుడు వస్తుంది', 'val': 'Mild occasional'},
            ];
          case 'mr':
            return [
              {'title': 'होय', 'subtitle': 'हे लक्षण जाणवत आहे', 'val': 'Yes'},
              {'title': 'नाही', 'subtitle': 'हा त्रास नाही', 'val': 'No'},
              {'title': 'अधूनमधून / थोडेफार', 'subtitle': 'कधीकधी किंवा थोडा त्रास जाणवतो', 'val': 'Mild occasional'},
            ];
          case 'hi':
            return [
              {'title': 'हाँ', 'subtitle': 'यह लक्षण महसूस हो रहा है', 'val': 'Yes'},
              {'title': 'नहीं', 'subtitle': 'यह परेशानी नहीं है', 'val': 'No'},
              {'title': 'कभी-कभी / थोड़ा बहुत', 'subtitle': 'हल्का या कभी-कभार महसूस होता है', 'val': 'कभी-कभी'},
            ];
          case 'en':
          default:
            return [
              {'title': 'Yes', 'subtitle': 'Experiencing this symptom', 'val': 'Yes'},
              {'title': 'No', 'subtitle': 'Do not have this symptom', 'val': 'No'},
              {'title': 'Mild / Occasionally', 'subtitle': 'Occasional or mild sensation', 'val': 'Mild occasional'},
            ];
        }
    }
  }

  // Returns localized 'Analysing your response...' in all 5 languages
  static String _analysingLabel(String langCode) {
    switch (langCode) {
      case 'ta':
        return 'உங்கள் பதிலை பகுப்பாய்கிறோம்...';
      case 'te':
        return 'మీ సమాధానాన్ని విశ్లేషిస్తున్నాము...';
      case 'mr':
        return 'तुमच्या उत्तराचे विश्लेषण होत आहे...';
      case 'hi':
        return 'आपका उत्तर विश्लेषण हो रहा है...';
      case 'en':
      default:
        return 'Analysing your response...';
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();
    final isProcessing = intake.isProcessingTurn;

    final question = intake.activeQuestion.isNotEmpty
        ? intake.activeQuestion
        : _getFallbackQuestion(lang.currentLanguage);

    final List<Map<String, String>> options = intake.suggestedOptions.isNotEmpty
        ? intake.suggestedOptions
            .map((o) => {
                  'title': o.title,
                  'subtitle': o.subtitle,
                  'val': o.val,
                })
            .toList()
        : _getOptionsForQuestion(question, lang.currentLanguage);

    // Edge case: unknown question type returns empty options — skip to summary
    if (options.isEmpty && !isProcessing) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (context.mounted) {
          Navigator.of(context).pushReplacementNamed('/summary');
        }
      });
    }

    return MediScaffold(
      title: lang.translate('followup_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Stack(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: MediDimensions.space12),
              Text(
                question,
                style: MediTypography.headlineLarge.copyWith(fontSize: 24),
              ),
              const SizedBox(height: MediDimensions.space12),
              Text(
                lang.translate('followup_sub'),
                style: MediTypography.bodyMedium,
              ),
              const SizedBox(height: MediDimensions.space20),
              Expanded(
                child: options.isEmpty
                    ? const Center(child: CircularProgressIndicator())
                    : ListView.separated(
                        itemCount: options.length,
                        separatorBuilder: (_, _) => const SizedBox(height: MediDimensions.space16),
                        itemBuilder: (context, index) {
                          final opt = options[index];
                          final isSelected = _selectedAnswer == opt['val'];
                          return LargeChoiceCard(
                            title: opt['title']!,
                            subtitle: opt['subtitle']!,
                            icon: isSelected ? Icons.check_circle : Icons.radio_button_unchecked,
                            isSelected: isSelected,
                            onTap: isProcessing
                                ? () {}
                                : () {
                                    setState(() {
                                      _selectedAnswer = opt['val']!;
                                    });
                                  },
                          );
                        },
                      ),
              ),
            ],
          ),

          // Loading overlay: covers choices while backend call is in flight
          if (isProcessing)
            Positioned.fill(
              child: Container(
                color: MediColors.canvas.withValues(alpha: 0.80),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SizedBox(
                      width: 52,
                      height: 52,
                      child: CircularProgressIndicator(
                        strokeWidth: 4.0,
                        valueColor: AlwaysStoppedAnimation<Color>(MediColors.brandPrimary),
                      ),
                    ),
                    const SizedBox(height: MediDimensions.space16),
                    Text(
                      _analysingLabel(lang.currentLanguage),
                      style: MediTypography.bodyLarge.copyWith(
                        color: MediColors.textPrimary,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: isProcessing
                ? _analysingLabel(lang.currentLanguage)
                : lang.translate('confirm_answer'),
            icon: isProcessing ? Icons.hourglass_top_rounded : Icons.arrow_forward_rounded,
            onPressed: isProcessing
                ? null
                : () async {
                    final answerToSubmit = _selectedAnswer.isNotEmpty
                        ? _selectedAnswer
                        : (options.isNotEmpty ? options.first['val']! : 'Yes');

                    await intake.submitTurn(patientSpeech: answerToSubmit);
                    if (context.mounted) {
                      if (intake.isInterviewCompleted) {
                        Navigator.of(context).pushReplacementNamed('/summary');
                      } else {
                        setState(() {
                          _selectedAnswer = '';
                        });
                      }
                    }
                  },
          ),
          const SizedBox(height: MediDimensions.space8),
          TextButton(
            onPressed: isProcessing ? null : () => Navigator.of(context).pushNamed('/summary'),
            child: Text(
              lang.translate('skip_to_summary'),
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: isProcessing ? MediColors.textDisabled : MediColors.brandPrimary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
