/// Yonned API Sabitleri ve Uç Noktaları
class ApiConstants {
  ApiConstants._();

  // Canlı ve Staging Sunucu Uç Noktaları (Cloudflare TLS 1.3 Korumalı)
  static const String baseUrl = 'https://api.yonned.com/api/v1';
  static const String stagingBaseUrl = 'https://staging-api.yonned.com/api/v1';

  // Zaman Aşımı Süresi
  static const Duration timeoutDuration = Duration(seconds: 15);

  // Endpoint Yolları
  static const String authPhoneLogin = '/auth/login/phone';
  static const String authVerifyOtp = '/auth/verify/otp';
  static const String assets = '/assets';
  static const String assetShares = '/assets/shares';
  static const String sessions = '/sessions';
}
