import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/di/service_locator.dart';
import 'core/theme/app_theme.dart';
import 'presentation/views/dashboard_view.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Clean Architecture Servislerini ve Veritabanını Başlat
  ServiceLocator.init();

  runApp(const YonnedApp());
}

class YonnedApp extends StatelessWidget {
  const YonnedApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => ServiceLocator.createWorkspaceViewModel(),
        ),
        ChangeNotifierProvider(
          create: (_) => ServiceLocator.createAssetViewModel(),
        ),
      ],
      child: MaterialApp(
        title: 'Yonned',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        home: const DashboardView(),
      ),
    );
  }
}
