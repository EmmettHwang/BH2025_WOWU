#!/usr/bin/env python3
"""
관리자 코드 정리 스크립트
- code='0'을 instructor_codes에서 삭제
- instructors 테이블의 instructor_type='0'을 'IC-999'로 변경
"""

import requests
import json

API_BASE = "http://localhost:3000"

def cleanup_admin_code():
    """관리자 코드 정리"""
    
    print("=" * 60)
    print("관리자 코드 정리 작업")
    print("=" * 60)
    
    # 1. 현재 강사코드 확인
    print("\n1️⃣  현재 강사코드 확인 중...")
    response = requests.get(f"{API_BASE}/api/instructor-codes")
    codes = response.json()
    
    has_zero = any(c['code'] == '0' for c in codes)
    has_ic999 = any(c['code'] == 'IC-999' for c in codes)
    
    print(f"   code='0' 존재: {has_zero}")
    print(f"   code='IC-999' 존재: {has_ic999}")
    
    if not has_ic999:
        print("\n❌ IC-999 코드가 없습니다. 먼저 마이그레이션을 실행하세요.")
        print("   curl -X POST http://localhost:3000/api/admin/migrate-admin-code")
        return
    
    # 2. instructors 테이블의 instructor_type='0'을 'IC-999'로 변경
    print("\n2️⃣  강사 계정의 타입 변경 중...")
    response = requests.get(f"{API_BASE}/api/instructors")
    instructors = response.json()
    
    type_zero_instructors = [i for i in instructors if i.get('instructor_type') == '0']
    print(f"   instructor_type='0'인 강사: {len(type_zero_instructors)}명")
    
    if type_zero_instructors:
        for instructor in type_zero_instructors:
            print(f"     - {instructor['code']}: {instructor['name']} (type: {instructor.get('instructor_type')})")
            
            # instructor_type 변경
            update_data = {
                'name': instructor['name'],
                'instructor_type': 'IC-999',
                'password': instructor.get('password', '')  # 비밀번호는 그대로 유지
            }
            
            try:
                response = requests.put(f"{API_BASE}/api/instructors/{instructor['code']}", json=update_data)
                if response.status_code == 200:
                    print(f"       ✅ {instructor['code']} 타입 변경 완료: '0' → 'IC-999'")
                else:
                    print(f"       ❌ {instructor['code']} 타입 변경 실패: {response.text}")
            except Exception as e:
                print(f"       ❌ {instructor['code']} 타입 변경 오류: {e}")
    else:
        print("   ℹ️  변경할 강사가 없습니다.")
    
    # 3. code='0' 삭제 (이제 사용하는 강사가 없으므로 안전하게 삭제 가능)
    if has_zero:
        print("\n3️⃣  code='0' 삭제 중...")
        try:
            response = requests.delete(f"{API_BASE}/api/instructor-codes/0")
            if response.status_code == 200:
                print("   ✅ code='0'이 성공적으로 삭제되었습니다.")
            else:
                result = response.json()
                print(f"   ❌ 삭제 실패: {result.get('detail', response.text)}")
        except Exception as e:
            print(f"   ❌ 삭제 오류: {e}")
    else:
        print("\n3️⃣  code='0'이 이미 삭제되었습니다.")
    
    # 4. 최종 확인
    print("\n4️⃣  최종 확인...")
    response = requests.get(f"{API_BASE}/api/instructor-codes")
    codes = response.json()
    
    has_zero_final = any(c['code'] == '0' for c in codes)
    has_ic999_final = any(c['code'] == 'IC-999' for c in codes)
    
    print(f"   code='0' 존재: {has_zero_final}")
    print(f"   code='IC-999' 존재: {has_ic999_final}")
    
    if has_ic999_final and not has_zero_final:
        print("\n🎉 관리자 코드 정리 완료!")
    elif has_ic999_final and has_zero_final:
        print("\n⚠️  IC-999는 생성되었지만 code='0'이 아직 남아있습니다.")
        print("   이것은 DB 레벨의 제약조건 때문일 수 있습니다.")
        print("   하지만 프론트엔드 코드에서 두 가지 모두 지원하므로 정상 작동할 것입니다.")
    else:
        print("\n❌ 문제가 발생했습니다. 수동으로 확인이 필요합니다.")

if __name__ == '__main__':
    try:
        cleanup_admin_code()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
