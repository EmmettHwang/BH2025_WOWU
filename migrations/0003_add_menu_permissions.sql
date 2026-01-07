-- 0003_add_menu_permissions.sql
-- 새로 추가된 메뉴(문서 관리, 문제은행)를 강사 권한에 추가

-- 먼저 현재 instructor_codes 테이블 구조 확인
-- menu_permissions 컬럼이 JSON 타입인지 확인 필요

-- 모든 instructor_type의 menu_permissions에 새 메뉴 추가
-- (관리자는 제외 - 이미 모든 권한 보유)

UPDATE instructor_codes
SET menu_permissions = JSON_ARRAY_APPEND(
    COALESCE(menu_permissions, JSON_ARRAY()),
    '$',
    'rag-documents'
)
WHERE code != 'IC-999' AND code != '0'
  AND (menu_permissions IS NULL OR NOT JSON_CONTAINS(menu_permissions, '"rag-documents"'));

UPDATE instructor_codes
SET menu_permissions = JSON_ARRAY_APPEND(
    COALESCE(menu_permissions, JSON_ARRAY()),
    '$',
    'exam-bank'
)
WHERE code != 'IC-999' AND code != '0'
  AND (menu_permissions IS NULL OR NOT JSON_CONTAINS(menu_permissions, '"exam-bank"'));

-- 마이그레이션 완료 후 확인 쿼리
-- SELECT code, name, menu_permissions FROM instructor_codes;
