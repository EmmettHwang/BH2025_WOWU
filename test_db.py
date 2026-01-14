import pymysql
import os

print("=== DB 연결 테스트 ===\n")

# DB 설정
DB_CONFIG = {
    'host': 'www.kdt2025.com',
    'port': 3306,
    'user': 'iyrc',
    'password': 'dodan1004~!@',
    'database': 'bh2025'
}

print(f"접속 정보:")
print(f"  - Host: {DB_CONFIG['host']}")
print(f"  - Port: {DB_CONFIG['port']}")
print(f"  - User: {DB_CONFIG['user']}")
print(f"  - Database: {DB_CONFIG['database']}")
print()

try:
    print("🔄 DB 연결 시도 중...")
    conn = pymysql.connect(**DB_CONFIG)
    print("✅ DB 연결 성공!\n")
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 테이블 목록 확인
    print("📋 테이블 목록:")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        table_name = list(table.values())[0]
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        print(f"  - {table_name}: {count}개 레코드")
    print()
    
    # instructor_codes 테이블 확인
    print("👥 강사 정보 (instructor_codes):")
    cursor.execute("SELECT code, name, password FROM instructor_codes LIMIT 5")
    instructors = cursor.fetchall()
    if instructors:
        for inst in instructors:
            print(f"  - 코드: {inst['code']}, 이름: {inst['name']}, 비밀번호: {inst['password']}")
    else:
        print("  ⚠️ 강사 정보가 없습니다!")
    print()
    
    # Root 계정 확인
    print("🔑 Root 계정 확인:")
    cursor.execute("SELECT * FROM instructor_codes WHERE name='root'")
    root = cursor.fetchone()
    if root:
        print(f"  ✅ Root 계정 존재")
        print(f"  - 코드: {root['code']}")
        print(f"  - 이름: {root['name']}")
        print(f"  - 비밀번호: {root['password']}")
    else:
        print("  ⚠️ Root 계정이 없습니다!")
    
    cursor.close()
    conn.close()
    print("\n✅ 모든 테스트 완료!")
    
except pymysql.err.OperationalError as e:
    print(f"❌ DB 연결 실패: {e}")
    print("\n가능한 원인:")
    print("  1. DB 서버 주소가 틀렸습니다")
    print("  2. 방화벽에서 접근이 차단되었습니다")
    print("  3. 사용자 권한이 없습니다")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
