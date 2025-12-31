# 데이터 로딩 성능 개선 방안

## 📊 현재 상황 분석

### 응답 시간 측정 결과:
```
1. 학생 목록:     1.45초
2. 강사 목록:     1.43초
3. 과정 목록:     1.14초
4. 상담 목록:     1.57초
5. 시간표 목록:   1.37초
6. 프로젝트 목록: 1.76초
7. 훈련일지 목록: 1.68초

총 예상 시간: 약 1.8초 (병렬 처리 중 가장 느린 API 기준)
```

### 문제점:
1. **외부 DB 연결 지연** (bitnmeta2.synology.me:3307)
2. **매번 전체 데이터 로드**
3. **JOIN 쿼리 많음** (instructor_codes, courses 등)
4. **캐싱 없음**

---

## 🚀 개선 방안 (우선순위별)

### ✅ **방안 1: 대시보드 전용 요약 API 생성** (★★★★★ 가장 효과적)

**개념:**
- 대시보드에 필요한 최소한의 데이터만 한 번에 반환하는 API
- 7개 API → 1개 API로 통합
- 서버에서 통계 계산 완료 후 전송

**구현:**
```python
# backend/main.py
@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """대시보드용 요약 데이터 (빠른 로딩)"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 기본 통계만 가져오기
    cursor.execute("SELECT COUNT(*) as count FROM students")
    students_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM instructors")
    instructors_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM courses")
    courses_count = cursor.fetchone()['count']
    
    # ... (필요한 통계만 SELECT)
    
    return {
        "students_count": students_count,
        "instructors_count": instructors_count,
        "courses_count": courses_count,
        "today_timetables": today_count,
        "today_counselings": today_counseling_count,
        # ...
    }
```

**예상 효과:** 1.8초 → **0.3초** (6배 빠름)

---

### ✅ **방안 2: Redis 캐싱 도입** (★★★★☆)

**개념:**
- 자주 변경되지 않는 데이터를 메모리에 캐시
- 5분~1시간 TTL 설정

**구현:**
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_result(ttl=300):  # 5분 캐시
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/api/students")
@cache_result(ttl=60)  # 1분 캐시
async def get_students():
    # ...
```

**예상 효과:** 1.8초 → **0.1초** (18배 빠름, 캐시 히트 시)

---

### ✅ **방안 3: 프론트엔드 로컬 캐싱** (★★★★☆)

**개념:**
- localStorage/IndexedDB에 데이터 저장
- 일정 시간(예: 5분) 동안 캐시 사용
- 백그라운드에서 업데이트

**구현:**
```javascript
// frontend/app.js
const CACHE_DURATION = 5 * 60 * 1000; // 5분

async function getCachedData(key, fetchFunction) {
    const cacheKey = `cache_${key}`;
    const timestampKey = `cache_${key}_timestamp`;
    
    const cached = localStorage.getItem(cacheKey);
    const timestamp = localStorage.getItem(timestampKey);
    
    // 캐시가 유효한 경우
    if (cached && timestamp && (Date.now() - parseInt(timestamp)) < CACHE_DURATION) {
        // 백그라운드 업데이트
        fetchFunction().then(data => {
            localStorage.setItem(cacheKey, JSON.stringify(data));
            localStorage.setItem(timestampKey, Date.now().toString());
        });
        
        return JSON.parse(cached);
    }
    
    // 캐시 없음 또는 만료됨
    const data = await fetchFunction();
    localStorage.setItem(cacheKey, JSON.stringify(data));
    localStorage.setItem(timestampKey, Date.now().toString());
    return data;
}

// 사용
const students = await getCachedData('students', 
    () => axios.get(`${API_BASE_URL}/api/students`).then(r => r.data)
);
```

**예상 효과:** 1.8초 → **0.05초** (36배 빠름, 캐시 히트 시)

---

### ✅ **방안 4: 페이지네이션 & 지연 로딩** (★★★☆☆)

**개념:**
- 대시보드 초기 렌더링 시 필수 데이터만 로드
- 나머지는 스크롤/탭 클릭 시 로드

**구현:**
```javascript
async function loadDashboard() {
    // 1단계: 필수 통계만 로드
    window.showLoading('대시보드 로딩 중...');
    const summary = await axios.get(`${API_BASE_URL}/api/dashboard/summary`);
    renderDashboardBasic(summary.data);
    window.hideLoading();
    
    // 2단계: 백그라운드에서 상세 데이터 로드
    loadDashboardDetails();
}

async function loadDashboardDetails() {
    // 비동기로 나머지 데이터 로드
    const [counselings, projects, trainingLogs] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/counselings?limit=5`),
        axios.get(`${API_BASE_URL}/api/projects?limit=5`),
        axios.get(`${API_BASE_URL}/api/training-logs?limit=5`)
    ]);
    
    // 점진적으로 화면 업데이트
    updateDashboardDetails(counselings.data, projects.data, trainingLogs.data);
}
```

**예상 효과:** 1.8초 → **0.5초** (첫 화면 표시), 전체 로딩은 백그라운드

---

### ✅ **방안 5: DB 쿼리 최적화** (★★★☆☆)

**개념:**
- 인덱스 추가
- 불필요한 JOIN 제거
- SELECT * 대신 필요한 컬럼만 선택

**구현:**
```sql
-- 인덱스 추가
CREATE INDEX idx_students_course ON students(course_code);
CREATE INDEX idx_counselings_date ON counselings(consultation_date);
CREATE INDEX idx_timetables_date ON timetables(class_date);

-- 쿼리 최적화
-- 기존:
SELECT * FROM students s 
LEFT JOIN courses c ON s.course_code = c.code;

-- 개선:
SELECT s.code, s.name, s.phone, c.name as course_name 
FROM students s 
LEFT JOIN courses c ON s.course_code = c.code 
WHERE s.course_code = 'CS-001'
LIMIT 10;
```

**예상 효과:** 1.8초 → **1.2초** (30% 개선)

---

### ✅ **방안 6: 데이터 압축** (★★☆☆☆)

**개념:**
- gzip 압축으로 네트워크 전송량 감소

**구현:**
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**예상 효과:** 1.8초 → **1.5초** (네트워크 속도에 따라 다름)

---

### ✅ **방안 7: 연결 풀링 최적화** (★★☆☆☆)

**개념:**
- DB 연결을 재사용하여 연결 시간 절약

**구현:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'mysql+pymysql://user:pass@host:port/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**예상 효과:** 1.8초 → **1.4초** (20% 개선)

---

## 🎯 추천 구현 순서

### 1단계 (즉시 구현 가능, 가장 효과적):
```
✅ 프론트엔드 로컬 캐싱 (방안 3)
   - 코드만 수정하면 됨
   - 즉시 36배 성능 향상
   - 서버 부하도 감소
```

### 2단계 (빠른 성능 향상):
```
✅ 대시보드 전용 요약 API (방안 1)
   - 백엔드 API 1개 추가
   - 프론트엔드 약간 수정
   - 6배 성능 향상
```

### 3단계 (장기적 개선):
```
✅ Redis 캐싱 (방안 2) - Redis 설치 필요
✅ DB 쿼리 최적화 (방안 5) - 인덱스 추가
✅ 페이지네이션 (방안 4) - UX 개선
```

---

## 💡 실제 적용 시 예상 결과

### 현재:
```
대시보드 로딩: 1.8초
학생 목록: 1.5초
상담 관리: 1.6초
```

### 방안 3 적용 후 (프론트엔드 캐싱):
```
대시보드 로딩 (첫 방문): 1.8초
대시보드 로딩 (재방문): 0.05초 ⚡
학생 목록 (첫 방문): 1.5초
학생 목록 (재방문): 0.05초 ⚡
```

### 방안 1+3 적용 후 (요약 API + 캐싱):
```
대시보드 로딩 (첫 방문): 0.3초 ⚡⚡⚡
대시보드 로딩 (재방문): 0.05초 ⚡⚡⚡
학생 목록 (첫 방문): 1.5초
학생 목록 (재방문): 0.05초 ⚡
```

### 방안 1+2+3 적용 후 (요약 API + Redis + 프론트 캐싱):
```
모든 페이지 (첫 방문): 0.1~0.3초 ⚡⚡⚡
모든 페이지 (재방문): 0.05초 ⚡⚡⚡
```

---

## 🔧 구현 난이도

| 방안 | 난이도 | 소요 시간 | 효과 |
|------|--------|----------|------|
| 방안 3 (프론트 캐싱) | ⭐ 쉬움 | 30분 | ★★★★★ |
| 방안 1 (요약 API) | ⭐⭐ 보통 | 1시간 | ★★★★★ |
| 방안 4 (페이지네이션) | ⭐⭐ 보통 | 1시간 | ★★★☆☆ |
| 방안 5 (쿼리 최적화) | ⭐⭐⭐ 어려움 | 2시간 | ★★★☆☆ |
| 방안 6 (압축) | ⭐ 쉬움 | 10분 | ★★☆☆☆ |
| 방안 2 (Redis) | ⭐⭐⭐⭐ 어려움 | 3시간 | ★★★★★ |
| 방안 7 (연결 풀) | ⭐⭐⭐ 어려움 | 2시간 | ★★☆☆☆ |

---

## 📝 결론

**즉시 구현 추천:**
1. ✅ **프론트엔드 로컬 캐싱** (30분 작업으로 36배 개선)
2. ✅ **대시보드 요약 API** (1시간 작업으로 6배 개선)

이 두 가지만 구현해도 **체감 속도가 극적으로 개선**됩니다!

어떤 방안을 먼저 구현해드릴까요? 😊
