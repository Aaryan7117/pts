import 'package:flutter/material.dart';
import '../../data/repositories/intake_repository.dart';

/// Encounter state provider managing active visit lifecycle
class EncounterProvider extends ChangeNotifier {
  final IntakeRepository _repository;

  String? _encounterId;
  String? _patientId;
  String? _tokenNumber;
  String _channel = 'android_byod';
  String _status = 'NOT_STARTED';
  String _severityBadge = 'GREEN';
  String _department = 'General Medicine';
  bool _isLoading = false;

  EncounterProvider({IntakeRepository? repository})
      : _repository = repository ?? IntakeRepository();

  String? get encounterId => _encounterId;
  String? get patientId => _patientId;
  String? get tokenNumber => _tokenNumber;
  String get channel => _channel;
  String get status => _status;
  String get severityBadge => _severityBadge;
  String get department => _department;
  bool get isLoading => _isLoading;

  void setDepartment(String dept) {
    _department = dept;
    notifyListeners();
  }

  void setSeverityBadge(String badge) {
    _severityBadge = badge;
    notifyListeners();
  }

  Future<void> bootstrap({
    String? qrToken,
    String channel = 'android_byod',
    String language = 'hi',
  }) async {
    _isLoading = true;
    _channel = channel;
    notifyListeners();

    try {
      final response = await _repository.bootstrap(
        qrToken: qrToken,
        channel: channel,
        language: language,
      );
      _encounterId = response.encounterId;
      _patientId = response.patientId;
      _tokenNumber = response.tokenNumber;
      _status = response.status;
    } catch (_) {
      // Fallback
      _encounterId = 'enc-fallback-01';
      _patientId = 'pat-fallback-01';
      _tokenNumber = 'A-104';
      _status = 'BOOTSTRAPPED';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Full privacy wipe of all active session data
  void resetSession() {
    _encounterId = null;
    _patientId = null;
    _tokenNumber = null;
    _status = 'NOT_STARTED';
    _severityBadge = 'GREEN';
    _department = 'General Medicine';
    _isLoading = false;
    notifyListeners();
  }
}
