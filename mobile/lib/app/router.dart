import 'package:flutter/material.dart';
import '../features/welcome/welcome_screen.dart';
import '../features/language/language_screen.dart';
import '../features/consent/consent_screen.dart';
import '../features/identity/identity_screen.dart';
import '../features/care_stream/care_stream_screen.dart';
import '../features/intake/voice_intake_screen.dart';
import '../features/intake/text_intake_screen.dart';
import '../features/call_intake/call_intake_screen.dart';
import '../features/intake/active_voice_capture_screen.dart';
import '../features/intake/conversational_followup_screen.dart';
import '../features/intake/ai_processing_screen.dart';
import '../features/intake/summary_confirmation_screen.dart';
import '../features/triage/triage_screen.dart';
import '../features/documents/document_intro_screen.dart';
import '../features/documents/document_camera_screen.dart';
import '../features/documents/ocr_processing_screen.dart';
import '../features/documents/ocr_result_screen.dart';
import '../features/documents/source_document_screen.dart';
import '../features/vitals/vitals_screen.dart';
import '../features/ayush/ayush_screen.dart';
import '../features/queue/queue_screen.dart';
import '../features/services/services_screen.dart';
import '../features/map/map_screen.dart';
import '../features/emergency/emergency_screen.dart';
import '../features/emergency/ambulance_screen.dart';
import '../features/completion/completion_screen.dart';

/// Centralized Route Definitions for MediKiosk (Screens 01 to 24 + A-06B + Text Intake)
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 & 10.1
class MediRouter {
  static const String initialRoute = '/welcome';

  static Map<String, WidgetBuilder> get routes => {
        '/welcome': (context) => const WelcomeScreen(),
        '/language': (context) => const LanguageScreen(),
        '/consent': (context) => const ConsentScreen(),
        '/identity': (context) => const IdentityScreen(),
        '/care_stream': (context) => const CareStreamScreen(),
        '/intake': (context) => const VoiceIntakeScreen(),
        '/text_intake': (context) => const TextIntakeScreen(),
        '/active_call': (context) => const CallIntakeScreen(),
        '/active_capture': (context) => const ActiveVoiceCaptureScreen(),
        '/followup': (context) => const ConversationalFollowupScreen(),
        '/processing': (context) => const AiProcessingScreen(),
        '/summary': (context) => const SummaryConfirmationScreen(),
        '/triage': (context) => const TriageScreen(),
        '/doc_intro': (context) => const DocumentIntroScreen(),
        '/doc_camera': (context) => const DocumentCameraScreen(),
        '/ocr_processing': (context) => const OcrProcessingScreen(),
        '/ocr_result': (context) => const OcrResultScreen(),
        '/doc_view': (context) => const SourceDocumentScreen(),
        '/vitals': (context) => const VitalsScreen(),
        '/ayush': (context) => const AyushScreen(),
        '/queue': (context) => const QueueScreen(),
        '/services': (context) => const ServicesScreen(),
        '/map': (context) => const MapScreen(),
        '/emergency': (context) => const EmergencyScreen(),
        '/ambulance': (context) => const AmbulanceScreen(),
        '/completion': (context) => const CompletionScreen(),
      };
}
