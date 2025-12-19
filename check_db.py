import pymysql
import json

# 데이터베이스 연결
conn = pymysql.connect(
    host='bitnmeta2.synology.me',
    user='iyrc',
    passwd='Dodan1004!',
    db='bh2025',
    charset='utf8',
    port=3307
)

try:
    cursor = conn.cursor()
    
    # students 테이블 구조 확인
    print("=== students 테이블 구조 ===")
    cursor.execute("DESCRIBE students")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]}, Default: {col[4]})")
    
    # 샘플 데이터 조회
    print("\n=== students 테이블 샘플 데이터 (최대 3개) ===")
    cursor.execute("SELECT * FROM students LIMIT 3")
    rows = cursor.fetchall()
    
    # 컬럼명 가져오기
    cursor.execute("SHOW COLUMNS FROM students")
    column_names = [col[0] for col in cursor.fetchall()]
    
    for row in rows:
        data = dict(zip(column_names, row))
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    
    # 테이블 목록 확인
    print("\n=== 데이터베이스의 모든 테이블 ===")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
finally:
    conn.close()
