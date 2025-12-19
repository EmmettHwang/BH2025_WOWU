import pymysql

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
    
    print("=== subjects 테이블 구조 확인 ===")
    cursor.execute("DESCRIBE subjects")
    columns = cursor.fetchall()
    column_names = [col[0] for col in columns]
    
    for col in columns:
        print(f"{col[0]}: {col[1]}")
    
    # 필요한 컬럼 추가
    required_columns = {
        'lecture_days': "VARCHAR(50) DEFAULT ''",  # 강의요일 (예: "월,수,금")
        'frequency': "VARCHAR(20) DEFAULT '매주'",  # 매주/격주
        'lecture_hours': "INT DEFAULT 0",  # 강의시수
        'description': "TEXT"  # 설명
    }
    
    print("\n=== 컬럼 추가 중 ===")
    for col_name, col_type in required_columns.items():
        if col_name not in column_names:
            try:
                alter_query = f"ALTER TABLE subjects ADD COLUMN {col_name} {col_type}"
                cursor.execute(alter_query)
                conn.commit()
                print(f"✓ {col_name} 컬럼 추가됨")
            except Exception as e:
                print(f"✗ {col_name} 추가 실패: {e}")
        else:
            print(f"- {col_name} 이미 존재함")
    
    print("\n=== consultations 테이블 구조 확인 ===")
    cursor.execute("DESCRIBE consultations")
    columns = cursor.fetchall()
    column_names = [col[0] for col in columns]
    
    for col in columns:
        print(f"{col[0]}: {col[1]}")
    
    # consultations 테이블에 필요한 컬럼 추가
    consultation_columns = {
        'counseling_type': "VARCHAR(50) DEFAULT ''",
        'topic': "VARCHAR(200) DEFAULT ''",
        'follow_up': "TEXT",
        'is_completed': "TINYINT DEFAULT 0"
    }
    
    print("\n=== consultations 테이블 컬럼 추가 중 ===")
    for col_name, col_type in consultation_columns.items():
        if col_name not in column_names:
            try:
                alter_query = f"ALTER TABLE consultations ADD COLUMN {col_name} {col_type}"
                cursor.execute(alter_query)
                conn.commit()
                print(f"✓ {col_name} 컬럼 추가됨")
            except Exception as e:
                print(f"✗ {col_name} 추가 실패: {e}")
        else:
            print(f"- {col_name} 이미 존재함")
    
    print("\n=== 스키마 업데이트 완료 ===")
    
finally:
    conn.close()
