import pymysql

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
    
    # 모든 테이블 목록
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("=== 데이터베이스 모든 테이블 ===\n")
    
    for (table_name,) in tables:
        print(f"\n### {table_name} ###")
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]}, Default: {col[4]})")
        
        # 샘플 데이터 개수
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  → 데이터 개수: {count}개")
    
finally:
    conn.close()
