import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;

/// Speech recognition service for capturing voice input on Android
class SpeechService {
  static final SpeechService _instance = SpeechService._internal();
  factory SpeechService() => _instance;
  SpeechService._internal();

  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _isAvailable = false;

  bool get isListening => _speech.isListening;
  bool get isAvailable => _isAvailable;

  Future<bool> initialize() async {
    if (_isAvailable) return true;
    try {
      _isAvailable = await _speech.initialize(
        onError: (val) => debugPrint('SpeechToText Error: ${val.errorMsg}'),
        onStatus: (val) => debugPrint('SpeechToText Status: $val'),
      );
      return _isAvailable;
    } catch (e) {
      debugPrint('SpeechToText init exception: $e');
      _isAvailable = false;
      return false;
    }
  }

  Future<bool> startListening({
    required ValueChanged<String> onResult,
    String? languageCode,
  }) async {
    final available = await initialize();
    if (!available) return false;

    // Map language code to locale if possible (e.g. hi -> hi_IN, en -> en_IN)
    String? localeId;
    if (languageCode == 'hi') {
      localeId = 'hi_IN';
    } else if (languageCode == 'ta') {
      localeId = 'ta_IN';
    } else if (languageCode == 'te') {
      localeId = 'te_IN';
    } else if (languageCode == 'mr') {
      localeId = 'mr_IN';
    } else {
      localeId = 'en_IN';
    }

    try {
      await _speech.listen(
        onResult: (result) {
          onResult(result.recognizedWords);
        },
        listenOptions: stt.SpeechListenOptions(
          partialResults: true,
          cancelOnError: false,
          listenMode: stt.ListenMode.dictation,
          localeId: localeId,
        ),
      );
      return true;
    } catch (e) {
      debugPrint('SpeechToText listen exception: $e');
      return false;
    }
  }

  Future<void> stopListening() async {
    try {
      if (_speech.isListening) {
        await _speech.stop();
      }
    } catch (e) {
      debugPrint('SpeechToText stop error: $e');
    }
  }
}
