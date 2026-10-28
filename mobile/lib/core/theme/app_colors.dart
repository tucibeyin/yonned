import 'package:flutter/material.dart';

/// Yonned Tasarım Sistemi Renk Paleti (Obsidian Dark Theme)
class AppColors {
  AppColors._();

  // Temel Arka Plan ve Yüzeyler (Deep Obsidian)
  static const Color background = Color(0xFF090A0F);
  static const Color surface = Color(0xFF12141D);
  static const Color surfaceElevated = Color(0xFF1A1D2A);
  static const Color surfaceBorder = Color(0xFF262B3D);

  // Vurgu ve Durum Renkleri
  // Canlı Zümrüt (Aktif süreçler, boş peronlar, başarı)
  static const Color emerald = Color(0xFF10B981);
  static const Color emeraldMuted = Color(0xFF064E3B);

  // Kehribar (Devam eden ameliyat/bakım, beklemede)
  static const Color amber = Color(0xFFF59E0B);
  static const Color amberMuted = Color(0xFF78350F);

  // Ametist Moru (Kişisel Varlık Cüzdanı, evcil hayvanlar)
  static const Color amethyst = Color(0xFF8B5CF6);
  static const Color amethystMuted = Color(0xFF4C1D95);

  // Kobalt Mavisi (İşletme / Kurumsal bağlam)
  static const Color cobalt = Color(0xFF3B82F6);
  static const Color cobaltMuted = Color(0xFF1E3A8A);

  // Hata & Tehlike
  static const Color crimson = Color(0xFFEF4444);

  // Tipografi ve Metin Renkleri
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);
}
