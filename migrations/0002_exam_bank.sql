-- 문제은행 시험 테이블
CREATE TABLE IF NOT EXISTS exam_bank (
  exam_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '시험 일련번호',
  exam_name VARCHAR(255) NOT NULL COMMENT '시험명칭',
  subject VARCHAR(100) NOT NULL COMMENT '교과목',
  exam_date DATE NOT NULL COMMENT '시험일자',
  total_questions INT NOT NULL DEFAULT 0 COMMENT '문항수',
  question_type VARCHAR(50) NOT NULL DEFAULT 'multiple_choice' COMMENT '문제 유형 (multiple_choice, short_answer, essay)',
  difficulty VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '난이도 (easy, medium, hard)',
  instructor_code VARCHAR(50) COMMENT '출제 강사 코드',
  description TEXT COMMENT '시험 설명',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  INDEX idx_exam_date (exam_date),
  INDEX idx_subject (subject),
  INDEX idx_instructor (instructor_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='문제은행 시험 테이블';

-- 문제은행 문제 테이블
CREATE TABLE IF NOT EXISTS exam_questions (
  question_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '문제 일련번호',
  exam_id INT NOT NULL COMMENT '시험 일련번호',
  question_number INT NOT NULL COMMENT '문제 번호',
  question_text TEXT NOT NULL COMMENT '문제 내용',
  question_type VARCHAR(50) NOT NULL DEFAULT 'multiple_choice' COMMENT '문제 유형',
  options JSON COMMENT '선택지 (JSON 배열)',
  correct_answer TEXT NOT NULL COMMENT '정답',
  explanation TEXT COMMENT '해설',
  reference_page VARCHAR(100) COMMENT '출제 페이지',
  reference_document VARCHAR(255) COMMENT '참고 문헌',
  difficulty VARCHAR(20) NOT NULL DEFAULT 'medium' COMMENT '난이도',
  points INT DEFAULT 1 COMMENT '배점',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일시',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일시',
  FOREIGN KEY (exam_id) REFERENCES exam_bank(exam_id) ON DELETE CASCADE,
  INDEX idx_exam_id (exam_id),
  INDEX idx_question_number (question_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='문제은행 문제 테이블';
