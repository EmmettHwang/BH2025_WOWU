from ftplib import FTP
import io

FTP_CONFIG = {
    'host': 'bitnmeta2.synology.me',
    'port': 2121,
    'user': 'ha',
    'passwd': 'dodan1004~'
}

file_path = 'homes/ha/camFTP/BH2025/teacher/20251120_135717_68039764_file.png'

try:
    print(f"🔄 FTP 연결 시도...")
    ftp = FTP()
    ftp.encoding = 'utf-8'
    ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'], timeout=10)
    ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
    print("✅ FTP 연결 및 로그인 성공!")
    
    print(f"\n🔄 파일 다운로드 시도: /{file_path}")
    file_data = io.BytesIO()
    ftp.retrbinary(f'RETR /{file_path}', file_data.write)
    ftp.quit()
    
    file_size = len(file_data.getvalue())
    print(f"✅ 파일 다운로드 성공! 크기: {file_size} bytes")
    
except Exception as e:
    print(f"❌ 에러 발생: {str(e)}")
    print(f"   에러 타입: {type(e).__name__}")
    import traceback
    traceback.print_exc()
