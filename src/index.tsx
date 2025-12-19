import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { serveStatic } from 'hono/cloudflare-workers'

type Bindings = {
  DB: D1Database
}

const app = new Hono<{ Bindings: Bindings }>()

// CORS 활성화
app.use('/api/*', cors())

// 정적 파일 서빙
app.use('/static/*', serveStatic({ root: './public' }))

// ==================== 학급(반) API ====================
// 모든 학급 조회
app.get('/api/classes', async (c) => {
  const { results } = await c.env.DB.prepare(
    'SELECT * FROM classes ORDER BY grade, name'
  ).all()
  return c.json(results)
})

// 특정 학급 조회
app.get('/api/classes/:id', async (c) => {
  const id = c.req.param('id')
  const { results } = await c.env.DB.prepare(
    'SELECT * FROM classes WHERE id = ?'
  ).bind(id).all()
  
  if (results.length === 0) {
    return c.json({ error: 'Class not found' }, 404)
  }
  return c.json(results[0])
})

// 학급 생성
app.post('/api/classes', async (c) => {
  const { name, grade, teacher_name, description } = await c.req.json()
  
  const result = await c.env.DB.prepare(
    'INSERT INTO classes (name, grade, teacher_name, description) VALUES (?, ?, ?, ?)'
  ).bind(name, grade, teacher_name, description).run()
  
  return c.json({ id: result.meta.last_row_id, name, grade, teacher_name, description }, 201)
})

// 학급 수정
app.put('/api/classes/:id', async (c) => {
  const id = c.req.param('id')
  const { name, grade, teacher_name, description } = await c.req.json()
  
  await c.env.DB.prepare(
    'UPDATE classes SET name = ?, grade = ?, teacher_name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
  ).bind(name, grade, teacher_name, description, id).run()
  
  return c.json({ id, name, grade, teacher_name, description })
})

// 학급 삭제
app.delete('/api/classes/:id', async (c) => {
  const id = c.req.param('id')
  await c.env.DB.prepare('DELETE FROM classes WHERE id = ?').bind(id).run()
  return c.json({ message: 'Class deleted successfully' })
})

// ==================== 학생 API ====================
// 모든 학생 조회 (학급별 필터 가능)
app.get('/api/students', async (c) => {
  const classId = c.req.query('class_id')
  
  let query = `
    SELECT s.*, c.name as class_name, c.grade 
    FROM students s 
    LEFT JOIN classes c ON s.class_id = c.id
  `
  
  if (classId) {
    query += ' WHERE s.class_id = ?'
    const { results } = await c.env.DB.prepare(query + ' ORDER BY s.student_number').bind(classId).all()
    return c.json(results)
  }
  
  const { results } = await c.env.DB.prepare(query + ' ORDER BY c.grade, c.name, s.student_number').all()
  return c.json(results)
})

// 특정 학생 조회
app.get('/api/students/:id', async (c) => {
  const id = c.req.param('id')
  const { results } = await c.env.DB.prepare(
    `SELECT s.*, c.name as class_name, c.grade 
     FROM students s 
     LEFT JOIN classes c ON s.class_id = c.id 
     WHERE s.id = ?`
  ).bind(id).all()
  
  if (results.length === 0) {
    return c.json({ error: 'Student not found' }, 404)
  }
  return c.json(results[0])
})

// 학생 생성
app.post('/api/students', async (c) => {
  const { class_id, student_number, name, phone, email, parent_name, parent_phone, address, notes } = await c.req.json()
  
  const result = await c.env.DB.prepare(
    'INSERT INTO students (class_id, student_number, name, phone, email, parent_name, parent_phone, address, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
  ).bind(class_id, student_number, name, phone, email, parent_name, parent_phone, address, notes).run()
  
  return c.json({ id: result.meta.last_row_id }, 201)
})

// 학생 수정
app.put('/api/students/:id', async (c) => {
  const id = c.req.param('id')
  const { class_id, student_number, name, phone, email, parent_name, parent_phone, address, notes } = await c.req.json()
  
  await c.env.DB.prepare(
    'UPDATE students SET class_id = ?, student_number = ?, name = ?, phone = ?, email = ?, parent_name = ?, parent_phone = ?, address = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
  ).bind(class_id, student_number, name, phone, email, parent_name, parent_phone, address, notes, id).run()
  
  return c.json({ id })
})

// 학생 삭제
app.delete('/api/students/:id', async (c) => {
  const id = c.req.param('id')
  await c.env.DB.prepare('DELETE FROM students WHERE id = ?').bind(id).run()
  return c.json({ message: 'Student deleted successfully' })
})

// ==================== 수업 API ====================
// 수업 목록 조회 (학급별 필터 가능)
app.get('/api/lessons', async (c) => {
  const classId = c.req.query('class_id')
  
  let query = `
    SELECT l.*, c.name as class_name, c.grade 
    FROM lessons l 
    LEFT JOIN classes c ON l.class_id = c.id
  `
  
  if (classId) {
    query += ' WHERE l.class_id = ?'
    const { results } = await c.env.DB.prepare(query + ' ORDER BY l.lesson_date DESC').bind(classId).all()
    return c.json(results)
  }
  
  const { results } = await c.env.DB.prepare(query + ' ORDER BY l.lesson_date DESC').all()
  return c.json(results)
})

// 특정 수업 조회
app.get('/api/lessons/:id', async (c) => {
  const id = c.req.param('id')
  const { results } = await c.env.DB.prepare(
    `SELECT l.*, c.name as class_name, c.grade 
     FROM lessons l 
     LEFT JOIN classes c ON l.class_id = c.id 
     WHERE l.id = ?`
  ).bind(id).all()
  
  if (results.length === 0) {
    return c.json({ error: 'Lesson not found' }, 404)
  }
  return c.json(results[0])
})

// 수업 생성
app.post('/api/lessons', async (c) => {
  const { class_id, title, subject, lesson_date, content, homework, attachments } = await c.req.json()
  
  const result = await c.env.DB.prepare(
    'INSERT INTO lessons (class_id, title, subject, lesson_date, content, homework, attachments) VALUES (?, ?, ?, ?, ?, ?, ?)'
  ).bind(class_id, title, subject, lesson_date, content, homework, attachments).run()
  
  return c.json({ id: result.meta.last_row_id }, 201)
})

// 수업 수정
app.put('/api/lessons/:id', async (c) => {
  const id = c.req.param('id')
  const { class_id, title, subject, lesson_date, content, homework, attachments } = await c.req.json()
  
  await c.env.DB.prepare(
    'UPDATE lessons SET class_id = ?, title = ?, subject = ?, lesson_date = ?, content = ?, homework = ?, attachments = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
  ).bind(class_id, title, subject, lesson_date, content, homework, attachments, id).run()
  
  return c.json({ id })
})

// 수업 삭제
app.delete('/api/lessons/:id', async (c) => {
  const id = c.req.param('id')
  await c.env.DB.prepare('DELETE FROM lessons WHERE id = ?').bind(id).run()
  return c.json({ message: 'Lesson deleted successfully' })
})

// ==================== 상담 API ====================
// 상담 목록 조회 (학생별 필터 가능)
app.get('/api/counselings', async (c) => {
  const studentId = c.req.query('student_id')
  
  let query = `
    SELECT co.*, s.name as student_name, s.student_number, c.name as class_name 
    FROM counselings co 
    LEFT JOIN students s ON co.student_id = s.id
    LEFT JOIN classes c ON s.class_id = c.id
  `
  
  if (studentId) {
    query += ' WHERE co.student_id = ?'
    const { results } = await c.env.DB.prepare(query + ' ORDER BY co.counseling_date DESC').bind(studentId).all()
    return c.json(results)
  }
  
  const { results } = await c.env.DB.prepare(query + ' ORDER BY co.counseling_date DESC').all()
  return c.json(results)
})

// 특정 상담 조회
app.get('/api/counselings/:id', async (c) => {
  const id = c.req.param('id')
  const { results } = await c.env.DB.prepare(
    `SELECT co.*, s.name as student_name, s.student_number, c.name as class_name 
     FROM counselings co 
     LEFT JOIN students s ON co.student_id = s.id
     LEFT JOIN classes c ON s.class_id = c.id
     WHERE co.id = ?`
  ).bind(id).all()
  
  if (results.length === 0) {
    return c.json({ error: 'Counseling not found' }, 404)
  }
  return c.json(results[0])
})

// 상담 생성
app.post('/api/counselings', async (c) => {
  const { student_id, counseling_date, counseling_type, topic, content, follow_up, is_completed } = await c.req.json()
  
  const result = await c.env.DB.prepare(
    'INSERT INTO counselings (student_id, counseling_date, counseling_type, topic, content, follow_up, is_completed) VALUES (?, ?, ?, ?, ?, ?, ?)'
  ).bind(student_id, counseling_date, counseling_type, topic, content, follow_up, is_completed || 0).run()
  
  return c.json({ id: result.meta.last_row_id }, 201)
})

// 상담 수정
app.put('/api/counselings/:id', async (c) => {
  const id = c.req.param('id')
  const { student_id, counseling_date, counseling_type, topic, content, follow_up, is_completed } = await c.req.json()
  
  await c.env.DB.prepare(
    'UPDATE counselings SET student_id = ?, counseling_date = ?, counseling_type = ?, topic = ?, content = ?, follow_up = ?, is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
  ).bind(student_id, counseling_date, counseling_type, topic, content, follow_up, is_completed, id).run()
  
  return c.json({ id })
})

// 상담 삭제
app.delete('/api/counselings/:id', async (c) => {
  const id = c.req.param('id')
  await c.env.DB.prepare('DELETE FROM counselings WHERE id = ?').bind(id).run()
  return c.json({ message: 'Counseling deleted successfully' })
})

// ==================== 메인 페이지 ====================
app.get('/', (c) => {
  return c.html(`
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>학급 관리 시스템</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/css/all.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen">
            <!-- 헤더 -->
            <header class="bg-blue-600 text-white shadow-lg">
                <div class="container mx-auto px-4 py-6">
                    <h1 class="text-3xl font-bold">
                        <i class="fas fa-school mr-3"></i>
                        학급 관리 시스템
                    </h1>
                </div>
            </header>

            <!-- 네비게이션 탭 -->
            <nav class="bg-white shadow-md">
                <div class="container mx-auto px-4">
                    <div class="flex space-x-4">
                        <button onclick="showTab('classes')" class="tab-btn px-6 py-4 font-semibold text-blue-600 border-b-2 border-blue-600" data-tab="classes">
                            <i class="fas fa-users mr-2"></i>학급 관리
                        </button>
                        <button onclick="showTab('students')" class="tab-btn px-6 py-4 font-semibold text-gray-600 hover:text-blue-600" data-tab="students">
                            <i class="fas fa-user-graduate mr-2"></i>학생 관리
                        </button>
                        <button onclick="showTab('lessons')" class="tab-btn px-6 py-4 font-semibold text-gray-600 hover:text-blue-600" data-tab="lessons">
                            <i class="fas fa-book mr-2"></i>수업 관리
                        </button>
                        <button onclick="showTab('counselings')" class="tab-btn px-6 py-4 font-semibold text-gray-600 hover:text-blue-600" data-tab="counselings">
                            <i class="fas fa-comments mr-2"></i>상담 관리
                        </button>
                    </div>
                </div>
            </nav>

            <!-- 메인 콘텐츠 -->
            <main class="container mx-auto px-4 py-8">
                <div id="app"></div>
            </main>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
        <script src="/static/app.js"></script>
    </body>
    </html>
  `)
})

export default app
