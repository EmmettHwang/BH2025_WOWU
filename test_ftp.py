from ftplib import FTP
import sys

FTP_CONFIG = {
    'host': 'bitnmeta2.synology.me',
    'port': 2121,
    'user': 'ha',
    'passwd': 'dodan1004~'
}

try:
    print(f"🔄 FTP 서버 연결 시도: {FTP_CONFIG['host']}:{FTP_CONFIG['port']}")
    ftp = FTP()
    ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'], timeout=10)
    print("✅ FTP 서버 연결 성공!")
    
    print(f"🔄 로그인 시도: {FTP_CONFIG['user']}")
    ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
    print("✅ FTP 로그인 성공!")
    
    print(f"🔄 디렉토리 확인...")
    ftp.cwd('/homes/ha/camFTP/BH2025/teacher')
    files = []
    ftp.retrlines('LIST', files.append)
    print(f"✅ 디렉토리 접근 성공! 파일 수: {len(files)}")
    if len(files) > 0:
        print(f"   첫 번째 파일: {files[0]}")
    
    ftp.quit()
    print("\n🎉 FTP 서버 연결 테스트 성공!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ FTP 연결 실패: {str(e)}")
    print(f"   에러 타입: {type(e).__name__}")
    sys.exit(1)
