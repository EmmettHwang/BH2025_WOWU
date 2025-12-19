// 전역 상태
let currentTab = 'classes';
let classes = [];
let students = [];
let lessons = [];
let counselings = [];

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    loadClasses();
    showTab('classes');
});

// 탭 전환
function showTab(tab) {
    currentTab = tab;
    
    // 탭 버튼 활성화 상태 변경
    document.querySelectorAll('.tab-btn').forEach(btn => {
        const isActive = btn.getAttribute('data-tab') === tab;
        btn.className = isActive 
            ? 'tab-btn px-6 py-4 font-semibold text-blue-600 border-b-2 border-blue-600'
            : 'tab-btn px-6 py-4 font-semibold text-gray-600 hover:text-blue-600';
    });
    
    // 해당 탭 콘텐츠 로드
    switch(tab) {
        case 'classes':
            loadClasses();
            break;
        case 'students':
            loadStudents();
            break;
        case 'lessons':
            loadLessons();
            break;
        case 'counselings':
            loadCounselings();
            break;
    }
}

// ==================== 학급 관리 ====================
async function loadClasses() {
    try {
        const response = await axios.get('/api/classes');
        classes = response.data;
        renderClasses();
    } catch (error) {
        console.error('학급 목록 로드 실패:', error);
        alert('학급 목록을 불러오는데 실패했습니다.');
    }
}

function renderClasses() {
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">
                    <i class="fas fa-users mr-2"></i>학급 목록
                </h2>
                <button onclick="showClassForm()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-plus mr-2"></i>학급 추가
                </button>
            </div>
            
            <div id="class-form" class="hidden mb-6 p-4 bg-gray-50 rounded-lg"></div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                ${classes.map(cls => `
                    <div class="border rounded-lg p-4 hover:shadow-lg transition-shadow">
                        <div class="flex justify-between items-start mb-3">
                            <h3 class="text-xl font-bold text-blue-600">${cls.grade}학년 ${cls.name}</h3>
                            <div class="space-x-2">
                                <button onclick="editClass(${cls.id})" class="text-blue-600 hover:text-blue-800">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteClass(${cls.id})" class="text-red-600 hover:text-red-800">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <p class="text-gray-600"><i class="fas fa-user-tie mr-2"></i>담임: ${cls.teacher_name || '미정'}</p>
                        ${cls.description ? `<p class="text-gray-500 text-sm mt-2">${cls.description}</p>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function showClassForm(classId = null) {
    const cls = classId ? classes.find(c => c.id === classId) : null;
    const formDiv = document.getElementById('class-form');
    
    formDiv.innerHTML = `
        <h3 class="text-lg font-bold mb-4">${cls ? '학급 수정' : '새 학급 추가'}</h3>
        <form onsubmit="saveClass(event, ${classId})">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-700 mb-2">학년</label>
                    <input type="number" name="grade" value="${cls?.grade || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">반 이름</label>
                    <input type="text" name="name" value="${cls?.name || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">담임 교사</label>
                    <input type="text" name="teacher_name" value="${cls?.teacher_name || ''}" 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">설명</label>
                    <input type="text" name="description" value="${cls?.description || ''}" 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
            </div>
            <div class="mt-4 space-x-2">
                <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-save mr-2"></i>저장
                </button>
                <button type="button" onclick="hideClassForm()" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg">
                    취소
                </button>
            </div>
        </form>
    `;
    
    formDiv.classList.remove('hidden');
}

function hideClassForm() {
    document.getElementById('class-form').classList.add('hidden');
}

async function saveClass(event, classId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        name: formData.get('name'),
        grade: parseInt(formData.get('grade')),
        teacher_name: formData.get('teacher_name'),
        description: formData.get('description')
    };
    
    try {
        if (classId) {
            await axios.put(`/api/classes/${classId}`, data);
        } else {
            await axios.post('/api/classes', data);
        }
        hideClassForm();
        loadClasses();
    } catch (error) {
        console.error('학급 저장 실패:', error);
        alert('학급 저장에 실패했습니다.');
    }
}

function editClass(id) {
    showClassForm(id);
}

async function deleteClass(id) {
    if (!confirm('정말 이 학급을 삭제하시겠습니까?')) return;
    
    try {
        await axios.delete(`/api/classes/${id}`);
        loadClasses();
    } catch (error) {
        console.error('학급 삭제 실패:', error);
        alert('학급 삭제에 실패했습니다.');
    }
}

// ==================== 학생 관리 ====================
async function loadStudents() {
    try {
        const [studentsRes, classesRes] = await Promise.all([
            axios.get('/api/students'),
            axios.get('/api/classes')
        ]);
        students = studentsRes.data;
        classes = classesRes.data;
        renderStudents();
    } catch (error) {
        console.error('학생 목록 로드 실패:', error);
        alert('학생 목록을 불러오는데 실패했습니다.');
    }
}

function renderStudents() {
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">
                    <i class="fas fa-user-graduate mr-2"></i>학생 목록
                </h2>
                <button onclick="showStudentForm()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-plus mr-2"></i>학생 추가
                </button>
            </div>
            
            <div id="student-form" class="hidden mb-6 p-4 bg-gray-50 rounded-lg"></div>
            
            <div class="overflow-x-auto">
                <table class="min-w-full bg-white">
                    <thead class="bg-gray-100">
                        <tr>
                            <th class="px-4 py-2 text-left">학번</th>
                            <th class="px-4 py-2 text-left">이름</th>
                            <th class="px-4 py-2 text-left">학급</th>
                            <th class="px-4 py-2 text-left">연락처</th>
                            <th class="px-4 py-2 text-left">학부모</th>
                            <th class="px-4 py-2 text-left">작업</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${students.map(student => `
                            <tr class="border-b hover:bg-gray-50">
                                <td class="px-4 py-2">${student.student_number}</td>
                                <td class="px-4 py-2 font-semibold">${student.name}</td>
                                <td class="px-4 py-2">${student.grade}학년 ${student.class_name}</td>
                                <td class="px-4 py-2">${student.phone || '-'}</td>
                                <td class="px-4 py-2">${student.parent_name || '-'} (${student.parent_phone || '-'})</td>
                                <td class="px-4 py-2">
                                    <button onclick="editStudent(${student.id})" class="text-blue-600 hover:text-blue-800 mr-2">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button onclick="deleteStudent(${student.id})" class="text-red-600 hover:text-red-800">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function showStudentForm(studentId = null) {
    const student = studentId ? students.find(s => s.id === studentId) : null;
    const formDiv = document.getElementById('student-form');
    
    formDiv.innerHTML = `
        <h3 class="text-lg font-bold mb-4">${student ? '학생 정보 수정' : '새 학생 추가'}</h3>
        <form onsubmit="saveStudent(event, ${studentId})">
            <div class="grid grid-cols-3 gap-4">
                <div>
                    <label class="block text-gray-700 mb-2">학급</label>
                    <select name="class_id" required class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">선택하세요</option>
                        ${classes.map(cls => `
                            <option value="${cls.id}" ${student?.class_id === cls.id ? 'selected' : ''}>
                                ${cls.grade}학년 ${cls.name}
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">학번</label>
                    <input type="text" name="student_number" value="${student?.student_number || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">이름</label>
                    <input type="text" name="name" value="${student?.name || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">연락처</label>
                    <input type="tel" name="phone" value="${student?.phone || ''}" 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">학부모 이름</label>
                    <input type="text" name="parent_name" value="${student?.parent_name || ''}" 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">학부모 연락처</label>
                    <input type="tel" name="parent_phone" value="${student?.parent_phone || ''}" 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div class="col-span-3">
                    <label class="block text-gray-700 mb-2">주소</label>
                    <input type="text" name="address" value="${student?.address || ''}" 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div class="col-span-3">
                    <label class="block text-gray-700 mb-2">비고</label>
                    <textarea name="notes" rows="2" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">${student?.notes || ''}</textarea>
                </div>
            </div>
            <div class="mt-4 space-x-2">
                <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-save mr-2"></i>저장
                </button>
                <button type="button" onclick="hideStudentForm()" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg">
                    취소
                </button>
            </div>
        </form>
    `;
    
    formDiv.classList.remove('hidden');
}

function hideStudentForm() {
    document.getElementById('student-form').classList.add('hidden');
}

async function saveStudent(event, studentId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        class_id: parseInt(formData.get('class_id')),
        student_number: formData.get('student_number'),
        name: formData.get('name'),
        phone: formData.get('phone'),
        email: formData.get('email'),
        parent_name: formData.get('parent_name'),
        parent_phone: formData.get('parent_phone'),
        address: formData.get('address'),
        notes: formData.get('notes')
    };
    
    try {
        if (studentId) {
            await axios.put(`/api/students/${studentId}`, data);
        } else {
            await axios.post('/api/students', data);
        }
        hideStudentForm();
        loadStudents();
    } catch (error) {
        console.error('학생 저장 실패:', error);
        alert('학생 저장에 실패했습니다.');
    }
}

function editStudent(id) {
    showStudentForm(id);
}

async function deleteStudent(id) {
    if (!confirm('정말 이 학생을 삭제하시겠습니까?')) return;
    
    try {
        await axios.delete(`/api/students/${id}`);
        loadStudents();
    } catch (error) {
        console.error('학생 삭제 실패:', error);
        alert('학생 삭제에 실패했습니다.');
    }
}

// ==================== 수업 관리 ====================
async function loadLessons() {
    try {
        const [lessonsRes, classesRes] = await Promise.all([
            axios.get('/api/lessons'),
            axios.get('/api/classes')
        ]);
        lessons = lessonsRes.data;
        classes = classesRes.data;
        renderLessons();
    } catch (error) {
        console.error('수업 목록 로드 실패:', error);
        alert('수업 목록을 불러오는데 실패했습니다.');
    }
}

function renderLessons() {
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">
                    <i class="fas fa-book mr-2"></i>수업 목록
                </h2>
                <button onclick="showLessonForm()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-plus mr-2"></i>수업 추가
                </button>
            </div>
            
            <div id="lesson-form" class="hidden mb-6 p-4 bg-gray-50 rounded-lg"></div>
            
            <div class="space-y-4">
                ${lessons.map(lesson => `
                    <div class="border rounded-lg p-4 hover:shadow-lg transition-shadow">
                        <div class="flex justify-between items-start mb-3">
                            <div>
                                <h3 class="text-xl font-bold text-blue-600">${lesson.title}</h3>
                                <p class="text-gray-600">
                                    <i class="fas fa-chalkboard-teacher mr-2"></i>${lesson.subject} | 
                                    ${lesson.grade}학년 ${lesson.class_name} | 
                                    ${lesson.lesson_date}
                                </p>
                            </div>
                            <div class="space-x-2">
                                <button onclick="editLesson(${lesson.id})" class="text-blue-600 hover:text-blue-800">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteLesson(${lesson.id})" class="text-red-600 hover:text-red-800">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="text-gray-700">
                            <p class="mb-2"><strong>수업 내용:</strong> ${lesson.content || '-'}</p>
                            ${lesson.homework ? `<p class="text-blue-600"><strong>숙제:</strong> ${lesson.homework}</p>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function showLessonForm(lessonId = null) {
    const lesson = lessonId ? lessons.find(l => l.id === lessonId) : null;
    const formDiv = document.getElementById('lesson-form');
    
    formDiv.innerHTML = `
        <h3 class="text-lg font-bold mb-4">${lesson ? '수업 내용 수정' : '새 수업 추가'}</h3>
        <form onsubmit="saveLesson(event, ${lessonId})">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-700 mb-2">학급</label>
                    <select name="class_id" required class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">선택하세요</option>
                        ${classes.map(cls => `
                            <option value="${cls.id}" ${lesson?.class_id === cls.id ? 'selected' : ''}>
                                ${cls.grade}학년 ${cls.name}
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">과목</label>
                    <input type="text" name="subject" value="${lesson?.subject || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">제목</label>
                    <input type="text" name="title" value="${lesson?.title || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">수업 날짜</label>
                    <input type="date" name="lesson_date" value="${lesson?.lesson_date || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div class="col-span-2">
                    <label class="block text-gray-700 mb-2">수업 내용</label>
                    <textarea name="content" rows="3" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">${lesson?.content || ''}</textarea>
                </div>
                <div class="col-span-2">
                    <label class="block text-gray-700 mb-2">숙제</label>
                    <textarea name="homework" rows="2" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">${lesson?.homework || ''}</textarea>
                </div>
            </div>
            <div class="mt-4 space-x-2">
                <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-save mr-2"></i>저장
                </button>
                <button type="button" onclick="hideLessonForm()" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg">
                    취소
                </button>
            </div>
        </form>
    `;
    
    formDiv.classList.remove('hidden');
}

function hideLessonForm() {
    document.getElementById('lesson-form').classList.add('hidden');
}

async function saveLesson(event, lessonId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        class_id: parseInt(formData.get('class_id')),
        title: formData.get('title'),
        subject: formData.get('subject'),
        lesson_date: formData.get('lesson_date'),
        content: formData.get('content'),
        homework: formData.get('homework'),
        attachments: ''
    };
    
    try {
        if (lessonId) {
            await axios.put(`/api/lessons/${lessonId}`, data);
        } else {
            await axios.post('/api/lessons', data);
        }
        hideLessonForm();
        loadLessons();
    } catch (error) {
        console.error('수업 저장 실패:', error);
        alert('수업 저장에 실패했습니다.');
    }
}

function editLesson(id) {
    showLessonForm(id);
}

async function deleteLesson(id) {
    if (!confirm('정말 이 수업 내용을 삭제하시겠습니까?')) return;
    
    try {
        await axios.delete(`/api/lessons/${id}`);
        loadLessons();
    } catch (error) {
        console.error('수업 삭제 실패:', error);
        alert('수업 삭제에 실패했습니다.');
    }
}

// ==================== 상담 관리 ====================
async function loadCounselings() {
    try {
        const [counselingsRes, studentsRes] = await Promise.all([
            axios.get('/api/counselings'),
            axios.get('/api/students')
        ]);
        counselings = counselingsRes.data;
        students = studentsRes.data;
        renderCounselings();
    } catch (error) {
        console.error('상담 목록 로드 실패:', error);
        alert('상담 목록을 불러오는데 실패했습니다.');
    }
}

function renderCounselings() {
    const app = document.getElementById('app');
    app.innerHTML = `
        <div class="bg-white rounded-lg shadow-md p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">
                    <i class="fas fa-comments mr-2"></i>상담 목록
                </h2>
                <button onclick="showCounselingForm()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-plus mr-2"></i>상담 추가
                </button>
            </div>
            
            <div id="counseling-form" class="hidden mb-6 p-4 bg-gray-50 rounded-lg"></div>
            
            <div class="space-y-4">
                ${counselings.map(counseling => `
                    <div class="border rounded-lg p-4 hover:shadow-lg transition-shadow ${counseling.is_completed ? 'bg-green-50' : ''}">
                        <div class="flex justify-between items-start mb-3">
                            <div>
                                <h3 class="text-xl font-bold text-blue-600">${counseling.topic}</h3>
                                <p class="text-gray-600">
                                    <i class="fas fa-user mr-2"></i>${counseling.student_name} (${counseling.student_number}) | 
                                    ${counseling.class_name} | 
                                    ${counseling.counseling_date}
                                </p>
                                <span class="inline-block px-2 py-1 text-xs rounded mt-2 ${
                                    counseling.counseling_type === '학업' ? 'bg-blue-100 text-blue-800' :
                                    counseling.counseling_type === '생활' ? 'bg-green-100 text-green-800' :
                                    'bg-purple-100 text-purple-800'
                                }">
                                    ${counseling.counseling_type}
                                </span>
                                ${counseling.is_completed ? '<span class="inline-block px-2 py-1 text-xs rounded mt-2 ml-2 bg-green-200 text-green-800">완료</span>' : ''}
                            </div>
                            <div class="space-x-2">
                                <button onclick="editCounseling(${counseling.id})" class="text-blue-600 hover:text-blue-800">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteCounseling(${counseling.id})" class="text-red-600 hover:text-red-800">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        <div class="text-gray-700">
                            <p class="mb-2"><strong>상담 내용:</strong> ${counseling.content}</p>
                            ${counseling.follow_up ? `<p class="text-blue-600"><strong>후속 조치:</strong> ${counseling.follow_up}</p>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function showCounselingForm(counselingId = null) {
    const counseling = counselingId ? counselings.find(c => c.id === counselingId) : null;
    const formDiv = document.getElementById('counseling-form');
    
    formDiv.innerHTML = `
        <h3 class="text-lg font-bold mb-4">${counseling ? '상담 내용 수정' : '새 상담 추가'}</h3>
        <form onsubmit="saveCounseling(event, ${counselingId})">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-gray-700 mb-2">학생</label>
                    <select name="student_id" required class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">선택하세요</option>
                        ${students.map(student => `
                            <option value="${student.id}" ${counseling?.student_id === student.id ? 'selected' : ''}>
                                ${student.name} (${student.student_number})
                            </option>
                        `).join('')}
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">상담 날짜</label>
                    <input type="date" name="counseling_date" value="${counseling?.counseling_date || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">상담 유형</label>
                    <select name="counseling_type" required class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="학업" ${counseling?.counseling_type === '학업' ? 'selected' : ''}>학업</option>
                        <option value="생활" ${counseling?.counseling_type === '생활' ? 'selected' : ''}>생활</option>
                        <option value="진로" ${counseling?.counseling_type === '진로' ? 'selected' : ''}>진로</option>
                        <option value="기타" ${counseling?.counseling_type === '기타' ? 'selected' : ''}>기타</option>
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">주제</label>
                    <input type="text" name="topic" value="${counseling?.topic || ''}" required 
                           class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div class="col-span-2">
                    <label class="block text-gray-700 mb-2">상담 내용</label>
                    <textarea name="content" rows="4" required class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">${counseling?.content || ''}</textarea>
                </div>
                <div class="col-span-2">
                    <label class="block text-gray-700 mb-2">후속 조치</label>
                    <textarea name="follow_up" rows="2" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">${counseling?.follow_up || ''}</textarea>
                </div>
                <div>
                    <label class="flex items-center">
                        <input type="checkbox" name="is_completed" ${counseling?.is_completed ? 'checked' : ''} class="mr-2">
                        <span class="text-gray-700">완료됨</span>
                    </label>
                </div>
            </div>
            <div class="mt-4 space-x-2">
                <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                    <i class="fas fa-save mr-2"></i>저장
                </button>
                <button type="button" onclick="hideCounselingForm()" class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded-lg">
                    취소
                </button>
            </div>
        </form>
    `;
    
    formDiv.classList.remove('hidden');
}

function hideCounselingForm() {
    document.getElementById('counseling-form').classList.add('hidden');
}

async function saveCounseling(event, counselingId) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        student_id: parseInt(formData.get('student_id')),
        counseling_date: formData.get('counseling_date'),
        counseling_type: formData.get('counseling_type'),
        topic: formData.get('topic'),
        content: formData.get('content'),
        follow_up: formData.get('follow_up'),
        is_completed: formData.get('is_completed') ? 1 : 0
    };
    
    try {
        if (counselingId) {
            await axios.put(`/api/counselings/${counselingId}`, data);
        } else {
            await axios.post('/api/counselings', data);
        }
        hideCounselingForm();
        loadCounselings();
    } catch (error) {
        console.error('상담 저장 실패:', error);
        alert('상담 저장에 실패했습니다.');
    }
}

function editCounseling(id) {
    showCounselingForm(id);
}

async function deleteCounseling(id) {
    if (!confirm('정말 이 상담 내용을 삭제하시겠습니까?')) return;
    
    try {
        await axios.delete(`/api/counselings/${id}`);
        loadCounselings();
    } catch (error) {
        console.error('상담 삭제 실패:', error);
        alert('상담 삭제에 실패했습니다.');
    }
}
