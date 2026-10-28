import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/constants/api_constants.dart';
import '../../models/asset_dto.dart';

/// Uzak Sunucu HTTP Veri Kaynağı (Remote REST DataSource)
class AssetRemoteDataSource {
  final http.Client client;

  const AssetRemoteDataSource({required this.client});

  /// Sunucudan varlıkları çeker
  Future<List<AssetDto>> fetchAssets({String? token}) async {
    try {
      final response = await client.get(
        Uri.parse('${ApiConstants.baseUrl}${ApiConstants.assets}'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
      ).timeout(ApiConstants.timeoutDuration);

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((json) => AssetDto.fromDb(json as Map<String, dynamic>)).toList();
      }
      return [];
    } catch (_) {
      // Çevrimdışı veya hata durumunda yerel önbellek kullanılır
      return [];
    }
  }
}
