import pymysql

DB_CONFIG = {
    'host': 'www.kdt2025.com',
    'port': 3306,
    'user': 'iyrc',
    'password': 'dodan1004~!@',
    'database': 'bh2025'
}

print("=== instructor_codes 테이블 구조 확인 ===\n")

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 테이블 구조 확인
    print("📋 테이블 구조:")
    cursor.execute("DESCRIBE instructor_codes")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col['Field']}: {col['Type']}")
    print()
    
    # 데이터 확인 (모든 컬럼)
    print("👥 강사 정보:")
    cursor.execute("SELECT * FROM instructor_codes LIMIT 5")
    instructors = cursor.fetchall()
    for inst in instructors:
        print(f"  {inst}")
    print()
    
    # Root 계정 확인
    print("🔑 Root 계정 찾기:")
    cursor.execute("SELECT * FROM instructor_codes WHERE name='root' OR code='root'")
    root = cursor.fetchone()
    if root:
        print(f"  ✅ Root 계정 발견: {root}")
    else:
        print("  ⚠️ Root 계정이 없습니다!")
        print("\n  모든 강사 목록:")
        cursor.execute("SELECT * FROM instructor_codes")
        all_instructors = cursor.fetchall()
        for inst in all_instructors:
            print(f"    {inst}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 오류: {e}")
