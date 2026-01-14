import pymysql

DB_CONFIG = {
    'host': 'www.kdt2025.com',
    'port': 3306,
    'user': 'iyrc',
    'password': 'dodan1004~!@',
    'database': 'bh2025'
}

print("=== instructors 테이블 확인 ===\n")

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 테이블 구조 확인
    print("📋 테이블 구조:")
    cursor.execute("DESCRIBE instructors")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col['Field']}: {col['Type']}")
    print()
    
    # Root 또는 관리자 계정 찾기
    print("🔑 Root/관리자 계정 찾기:")
    cursor.execute("SELECT * FROM instructors WHERE name LIKE '%root%' OR name LIKE '%관리자%' OR name='admin' LIMIT 5")
    admins = cursor.fetchall()
    if admins:
        for admin in admins:
            print(f"  {admin}")
    else:
        print("  ⚠️ Root/관리자 계정이 없습니다!")
        print("\n  첫 5명의 강사:")
        cursor.execute("SELECT * FROM instructors LIMIT 5")
        instructors = cursor.fetchall()
        for inst in instructors:
            print(f"    이름: {inst.get('name')}, 코드: {inst.get('instructor_code')}, 비밀번호: {inst.get('password', 'N/A')}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()
