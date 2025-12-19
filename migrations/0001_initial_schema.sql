-- 학급(반) 테이블
CREATE TABLE IF NOT EXISTS classes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  grade INTEGER NOT NULL,
  teacher_name TEXT,
  description TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 학생 테이블
CREATE TABLE IF NOT EXISTS students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  class_id INTEGER NOT NULL,
  student_number TEXT NOT NULL,
  name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  parent_name TEXT,
  parent_phone TEXT,
  address TEXT,
  notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
  UNIQUE(class_id, student_number)
);

-- 수업 내용 테이블
CREATE TABLE IF NOT EXISTS lessons (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  class_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  subject TEXT NOT NULL,
  lesson_date DATE NOT NULL,
  content TEXT,
  homework TEXT,
  attachments TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- 상담 내용 테이블
CREATE TABLE IF NOT EXISTS counselings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  counseling_date DATE NOT NULL,
  counseling_type TEXT NOT NULL,
  topic TEXT NOT NULL,
  content TEXT NOT NULL,
  follow_up TEXT,
  is_completed INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_students_class_id ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_lessons_class_id ON lessons(class_id);
CREATE INDEX IF NOT EXISTS idx_lessons_date ON lessons(lesson_date);
CREATE INDEX IF NOT EXISTS idx_counselings_student_id ON counselings(student_id);
CREATE INDEX IF NOT EXISTS idx_counselings_date ON counselings(counseling_date);
