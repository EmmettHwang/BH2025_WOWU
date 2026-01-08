-- 마이그레이션: 신규가입 설정 컬럼 추가
-- 날짜: 2026-01-08
-- 설명: system_settings 테이블에 신규가입 관련 설정 컬럼 추가

USE bh2025;

-- open_courses: 모집중인 과정 코드 (쉼표로 구분)
ALTER TABLE system_settings 
ADD COLUMN IF NOT EXISTS open_courses TEXT 
COMMENT '모집중인 과정 코드 목록 (쉼표 구분, 예: C-001,C-002)';

-- interest_keywords: 관심분야 키워드 (쉼표로 구분)
ALTER TABLE system_settings 
ADD COLUMN IF NOT EXISTS interest_keywords TEXT 
COMMENT '관심분야 키워드 목록 (쉼표 구분)';

-- 기본값 설정 (첫 번째 레코드에만)
UPDATE system_settings 
SET interest_keywords = 'AI, 로봇, 빅데이터, 프로그래밍, 헬스케어, 데이터엔지니어, 데이터과학자, 의과학자, ML엔지니어, AI보안엔지니어, AI APP개발, 임베디드&온디바이스AI, 전문도메인융합, 첨단산업AX, AI HW엔지니어'
WHERE interest_keywords IS NULL OR interest_keywords = ''
LIMIT 1;

SELECT '✅ 신규가입 설정 컬럼 추가 완료' AS status;
