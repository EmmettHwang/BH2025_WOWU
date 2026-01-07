#!/usr/bin/env python3
"""
기존 상담 DB에 진로 결정 데이터 무작위 삽입
- 학업: 1명
- 창업: 3명
- 미정: 10명
- 기타: 0명
- 취업: 나머지
"""
import pymysql
import random

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': 'bitnmeta2.synology.me',
    'user': 'iyrc',
    'passwd': 'Dodan1004!',
    'db': 'bh2025',
    'charset': 'utf8',
    'port': 3307
}

def main():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        cursor = conn.cursor()
        
        # 모든 상담 ID 가져오기
        cursor.execute("SELECT id FROM consultations")
        all_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"총 상담 건수: {len(all_ids)}건")
        
        # ID를 랜덤하게 섞기
        random.shuffle(all_ids)
        
        # 진로 결정 할당
        # 학업: 1건
        study_ids = all_ids[:1]
        # 창업: 3건
        startup_ids = all_ids[1:4]
        # 미정: 10건
        undecided_ids = all_ids[4:14]
        # 취업: 나머지
        employment_ids = all_ids[14:]
        
        print(f"학업: {len(study_ids)}건")
        print(f"창업: {len(startup_ids)}건")
        print(f"미정: {len(undecided_ids)}건")
        print(f"취업: {len(employment_ids)}건")
        
        # 업데이트 실행
        for id in study_ids:
            cursor.execute("UPDATE consultations SET career_decision = '1. 학업' WHERE id = %s", (id,))
        
        for id in startup_ids:
            cursor.execute("UPDATE consultations SET career_decision = '3. 창업' WHERE id = %s", (id,))
        
        for id in undecided_ids:
            cursor.execute("UPDATE consultations SET career_decision = '4. 미정' WHERE id = %s", (id,))
        
        for id in employment_ids:
            cursor.execute("UPDATE consultations SET career_decision = '2. 취업' WHERE id = %s", (id,))
        
        conn.commit()
        print("✅ 진로 결정 데이터 업데이트 완료!")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
