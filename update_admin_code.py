#!/usr/bin/env python3
"""관리자 코드를 0에서 IC-999로 변경하는 스크립트"""

import pymysql
from pymysql.cursors import DictCursor
import sys

# 데이터베이스 연결 설정
DB_CONFIG = {
    'host': 'autorack.proxy.rlwy.net',
    'port': 58642,
    'user': 'root',
    'password': 'FwjSYglTSLjNHxqLZFQNPrTZQLRAMExe',
    'database': 'railway',
    'cursorclass': DictCursor
}

def update_admin_code():
    """관리자 코드를 0에서 IC-999로 변경"""
    conn = None
    try:
        print("📡 데이터베이스 연결 중...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. 현재 code='0'인 항목 확인
        print("\n🔍 현재 관리자 코드 확인...")
        cursor.execute("SELECT * FROM instructor_codes WHERE code = '0'")
        old_admin = cursor.fetchone()
        if old_admin:
            print(f"   현재: Code={old_admin['code']}, Name={old_admin['name']}, Type={old_admin['type']}")
        else:
            print("   ⚠️  code='0'인 관리자 코드가 없습니다.")
            return
        
        # 2. IC-999 코드가 이미 있는지 확인
        cursor.execute("SELECT * FROM instructor_codes WHERE code = 'IC-999'")
        existing = cursor.fetchone()
        if existing:
            print(f"   ⚠️  IC-999 코드가 이미 존재합니다: {existing}")
            confirm = input("   기존 IC-999를 삭제하고 계속하시겠습니까? (y/N): ")
            if confirm.lower() != 'y':
                print("   작업을 취소했습니다.")
                return
            cursor.execute("DELETE FROM instructor_codes WHERE code = 'IC-999'")
            conn.commit()
            print("   ✅ 기존 IC-999 코드를 삭제했습니다.")
        
        # 3. code='0'을 'IC-999'로 변경
        print("\n��� 관리자 코드 변경 중...")
        update_query = """
            UPDATE instructor_codes
            SET code = 'IC-999', type = '0. 관리자'
            WHERE code = '0'
        """
        cursor.execute(update_query)
        conn.commit()
        print("   ✅ instructor_codes 테이블 업데이트 완료")
        
        # 4. instructors 테이블에서 instructor_type도 업데이트
        print("\n🔄 강사 정보 업데이트 중...")
        cursor.execute("SELECT COUNT(*) as cnt FROM instructors WHERE instructor_type = '0'")
        result = cursor.fetchone()
        count = result['cnt'] if result else 0
        
        if count > 0:
            update_instructors_query = """
                UPDATE instructors
                SET instructor_type = 'IC-999'
                WHERE instructor_type = '0'
            """
            cursor.execute(update_instructors_query)
            conn.commit()
            print(f"   ✅ {count}명의 강사 instructor_type을 IC-999로 업데이트했습니다.")
        else:
            print("   ℹ️  instructor_type='0'인 강사가 없습니다.")
        
        # 5. 변경 결과 확인
        print("\n✅ 최종 결과 확인...")
        cursor.execute("SELECT * FROM instructor_codes WHERE code = 'IC-999'")
        new_admin = cursor.fetchone()
        if new_admin:
            print(f"   Code: {new_admin['code']}")
            print(f"   Name: {new_admin['name']}")
            print(f"   Type: {new_admin['type']}")
            print(f"   Permissions: {new_admin['permissions']}")
            print(f"   Default Screen: {new_admin['default_screen']}")
        
        cursor.execute("SELECT code, name, instructor_type FROM instructors WHERE instructor_type = 'IC-999'")
        admins = cursor.fetchall()
        if admins:
            print(f"\n   관리자 계정 ({len(admins)}명):")
            for admin in admins:
                print(f"     - {admin['code']}: {admin['name']} (타입: {admin['instructor_type']})")
        
        print("\n🎉 관리자 코드 변경이 완료되었습니다!")
        
    except pymysql.Error as e:
        print(f"\n❌ 데이터베이스 오류: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("\n📡 데이터베이스 연결 종료")

if __name__ == '__main__':
    print("=" * 60)
    print("관리자 코드 변경: 0 → IC-999")
    print("=" * 60)
    update_admin_code()
