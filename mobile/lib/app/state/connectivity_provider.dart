import 'package:flutter/material.dart';
import '../../core/widgets/offline_banner.dart';

/// Connectivity state provider managing Online, Edge Mode, and Offline
class ConnectivityProvider extends ChangeNotifier {
  NetworkStatus _status = NetworkStatus.online;

  NetworkStatus get status => _status;

  void setStatus(NetworkStatus status) {
    if (_status != status) {
      _status = status;
      notifyListeners();
    }
  }

  void toggleStatus() {
    if (_status == NetworkStatus.online) {
      _status = NetworkStatus.edgeMode;
    } else if (_status == NetworkStatus.edgeMode) {
      _status = NetworkStatus.offline;
    } else {
      _status = NetworkStatus.online;
    }
    notifyListeners();
  }
}
