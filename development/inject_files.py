import os
from pathlib import Path

# 사용자님이 보고 계신 바로 그 경로를 타겟팅합니다.
TARGET_ROOT = Path(r"D:\python_projects\world_coder\development\tg_pos_app\lib")

# 생성할 파일 내용 (login_screen.dart)
LOGIN_SCREEN_CODE = r"""
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'pos_screen_v3.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _u = TextEditingController(text: "owner");
  final _p = TextEditingController(text: "1234");
  final _api = ApiService();
  bool _l = false;

  Future<void> _f() async {
    setState(() => _l = true);
    final ok = await _api.login(_u.text, _p.text);
    setState(() => _l = false);
    if (ok && mounted) Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const PosScreenV3(storeId: 1)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: ElevatedButton(onPressed: _f, child: const Text("LOGIN")))
    );
  }
}
"""

def inject():
    # 1. screens 폴더 확인 및 생성
    screens_dir = TARGET_ROOT / "screens"
    if not screens_dir.exists():
        print(f"[!] Creating directory: {screens_dir}")
        screens_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 파일 쓰기
    target_file = screens_dir / "login_screen.dart"
    print(f"[*] Injecting file to: {target_file}")
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(LOGIN_SCREEN_CODE)
        
    # 3. 확인 사살
    if target_file.exists():
        print(f"[SUCCESS] File Created! Size: {target_file.stat().st_size} bytes")
    else:
        print("[CRITICAL ERROR] File still missing even after write.")

if __name__ == "__main__":
    inject()