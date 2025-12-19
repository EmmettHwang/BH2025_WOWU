# 교육관리시스템 API 엔드포인트 정리

## ✅ 완료된 API 모듈 (9개)

### 1. 강사코드 관리 (Instructor Codes)
- `GET /api/instructor-codes` - 강사코드 목록 조회
- `POST /api/instructor-codes` - 강사코드 생성
- `PUT /api/instructor-codes/{code}` - 강사코드 수정
- `DELETE /api/instructor-codes/{code}` - 강사코드 삭제

### 2. 강사 관리 (Instructors)
- `GET /api/instructors?search={query}` - 강사 목록 조회 (검색 기능)
- `GET /api/instructors/{code}` - 특정 강사 조회
- `POST /api/instructors` - 강사 생성
- `PUT /api/instructors/{code}` - 강사 수정
- `DELETE /api/instructors/{code}` - 강사 삭제

### 3. 교과목 관리 (Subjects)
- `GET /api/subjects` - 과목 목록 조회
- `GET /api/subjects/{subject_id}` - 특정 과목 조회
- `POST /api/subjects` - 과목 생성 (lecture_days, frequency, lecture_hours)
- `PUT /api/subjects/{subject_id}` - 과목 수정
- `DELETE /api/subjects/{subject_id}` - 과목 삭제

### 4. 공휴일 관리 (Holidays)
- `GET /api/holidays?year={year}` - 공휴일 목록 조회 (연도별 필터)
- `POST /api/holidays` - 공휴일 생성
- `PUT /api/holidays/{holiday_id}` - 공휴일 수정
- `DELETE /api/holidays/{holiday_id}` - 공휴일 삭제

### 5. 과정(학급) 관리 (Courses)
- `GET /api/courses` - 과정 목록 조회 (학생수, 과목수 포함)
- `GET /api/courses/{code}` - 특정 과정 조회
- `POST /api/courses` - 과정 생성 (start_date, lecture_end_date, project_end_date, internship_end_date, final_end_date, total_days)
- `PUT /api/courses/{code}` - 과정 수정
- `DELETE /api/courses/{code}` - 과정 삭제

### 6. 학생 관리 (Students) ✅ 기존 완료
- `GET /api/students?course_code={code}&search={query}` - 학생 목록 조회
- `GET /api/students/{student_id}` - 특정 학생 조회
- `POST /api/students` - 학생 생성
- `PUT /api/students/{student_id}` - 학생 수정
- `DELETE /api/students/{student_id}` - 학생 삭제
- `POST /api/students/upload-excel` - Excel 일괄 등록
- `GET /api/students/download-template` - Excel 템플릿 다운로드

### 7. 학생상담 관리 (Counselings) ✅ 기존 완료
- `GET /api/counselings?student_id={id}&month={YYYY-MM}&course_code={code}` - 상담 목록 조회
- `GET /api/counselings/{counseling_id}` - 특정 상담 조회
- `POST /api/counselings` - 상담 생성
- `PUT /api/counselings/{counseling_id}` - 상담 수정
- `DELETE /api/counselings/{counseling_id}` - 상담 삭제

### 8. 프로젝트 관리 (Projects)
- `GET /api/projects?course_code={code}` - 프로젝트 목록 조회
- `GET /api/projects/{code}` - 특정 프로젝트 조회
- `POST /api/projects` - 프로젝트 생성 (5명의 팀원 정보)
- `PUT /api/projects/{code}` - 프로젝트 수정
- `DELETE /api/projects/{code}` - 프로젝트 삭제

### 9. 수업관리(시간표) (Timetables)
- `GET /api/timetables?course_code={code}&start_date={date}&end_date={date}` - 시간표 목록 조회
- `GET /api/timetables/{timetable_id}` - 특정 시간표 조회
- `POST /api/timetables` - 시간표 생성
- `PUT /api/timetables/{timetable_id}` - 시간표 수정
- `DELETE /api/timetables/{timetable_id}` - 시간표 삭제

### 10. AI 생기부 작성 ✅ 기존 완료
- `POST /api/ai/generate-report` - AI 생활기록부 생성 (OpenAI GPT-4o-mini)

## 테스트 결과

### ✅ 정상 작동 확인
```bash
# 강사코드 조회 - 5개 데이터 반환
curl http://localhost:8000/api/instructor-codes

# 강사 조회 - 33명 데이터 반환, type_name JOIN 정상
curl http://localhost:8000/api/instructors

# 공휴일 조회 - 2025년 공휴일 데이터 반환
curl "http://localhost:8000/api/holidays?year=2025"

# 과정 조회 - student_count, subject_count 집계 정상
curl http://localhost:8000/api/courses

# 시간표 조회 - course_name, subject_name, instructor_name JOIN 정상
curl "http://localhost:8000/api/timetables?course_code=C-001"
```

## 다음 단계
- [ ] 프론트엔드 UI에 9개 관리 모듈 탭 추가
- [ ] 각 모듈별 CRUD 기능 구현
- [ ] 검색/필터 기능 추가
