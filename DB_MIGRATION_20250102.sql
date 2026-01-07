-- ================================================
-- DB Migration: timetables.type 컬럼 수정
-- Date: 2025-01-02
-- Issue: 500 Error when adding/updating timetables
-- Reason: DB ENUM had 'workship', but frontend sends 'practice'
-- ================================================

-- Step 1: Add 'practice' to ENUM (keep 'workship' temporarily)
ALTER TABLE timetables 
MODIFY COLUMN type ENUM('lecture', 'project', 'workship', 'practice') NOT NULL;

-- Step 2: Update existing 'workship' data to 'practice'
UPDATE timetables SET type = 'practice' WHERE type = 'workship';

-- Step 3: Remove 'workship' from ENUM
ALTER TABLE timetables 
MODIFY COLUMN type ENUM('lecture', 'project', 'practice') NOT NULL;

-- ================================================
-- Result:
-- - 60 rows updated from 'workship' to 'practice'
-- - Final ENUM: ('lecture', 'project', 'practice')
-- - Resolved: 시간표 추가/수정 시 500 에러 해결
-- ================================================
