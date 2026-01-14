# -*- coding: utf-8 -*-
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import pymysql
import pandas as pd
import io
import os
import json
import logging
from datetime import datetime, timedelta, date
from openai import OpenAI
from dotenv import load_dotenv
import requests
from ftplib import FTP
import uuid
import base64
from PIL import Image
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# .env 파일을 상위 디렉토리에서 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# 로깅 필터 설정 (불필요한 200 OK 로그 제거)
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # 특정 엔드포인트의 200 OK 로그는 제외
        message = record.getMessage()
        if '200 OK' in message:
            # 진행률 조회 API는 로그 제외
            if '/api/rag/indexing-progress/' in message:
                return False
            
            # 대시보드 새로고침 시 호출되는 일반적인 GET 요청들 제외
            dashboard_apis = [
                '/api/courses',
                '/api/students',
                '/api/instructors',
                '/api/counselings',
                '/api/timetables',
                '/api/projects',
                '/api/training-logs',
                '/api/team-activity-logs'
            ]
            
            for api in dashboard_apis:
                if f'GET {api} ' in message and '200 OK' in message:
                    return False
            
            # 로그인 401은 포함 (보안상 중요)
        return True

# uvicorn 로거에 필터 적용
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

app = FastAPI(
    title="학급 관리 시스템 API",
    # 요청 크기 제한 설정 (기본 10MB)
    # Cafe24 배포 시 nginx client_max_body_size도 조정 필요
)

# 정적 파일 서빙 (프론트엔드)
import os
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# public 폴더의 GLB 파일을 frontend에서 직접 접근 가능하도록 심볼릭 링크 또는 복사
# 또는 별도 라우트로 서빙

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3D 모델 파일 (GLB) 서빙
from fastapi.responses import FileResponse
from fastapi import HTTPException

# 방법 1: 루트 경로에서 서빙 (프록시 서버와 충돌 가능)
@app.get("/{filename}.glb")
async def serve_glb_file_root(filename: str):
    """루트 경로에서 GLB 파일 서빙 (3D 모델용)"""
    print(f"[DEBUG] GLB 파일 요청 (루트): {filename}.glb")
    glb_path = os.path.join(frontend_dir, f"{filename}.glb")
    print(f"[DEBUG] GLB 파일 경로: {glb_path}")
    print(f"[DEBUG] 파일 존재 여부: {os.path.exists(glb_path)}")
    
    if os.path.exists(glb_path):
        print(f"[OK] GLB 파일 전송: {filename}.glb")
        return FileResponse(glb_path, media_type="model/gltf-binary")
    else:
        print(f"[ERROR] GLB 파일 없음: {filename}.glb")
        raise HTTPException(status_code=404, detail=f"GLB file not found: {filename}.glb")

# 방법 2: /api/models/ 경로에서 서빙 (권장)
@app.get("/api/models/{filename}.glb")
async def serve_glb_file_api(filename: str):
    """API 경로에서 GLB 파일 서빙 (3D 모델용)"""
    print(f"[DEBUG] GLB 파일 요청 (API): {filename}.glb")
    glb_path = os.path.join(frontend_dir, f"{filename}.glb")
    print(f"[DEBUG] GLB 파일 경로: {glb_path}")
    print(f"[DEBUG] 파일 존재 여부: {os.path.exists(glb_path)}")
    
    if os.path.exists(glb_path):
        print(f"[OK] GLB 파일 전송 (API): {filename}.glb")
        return FileResponse(glb_path, media_type="model/gltf-binary")
    else:
        print(f"[ERROR] GLB 파일 없음 (API): {filename}.glb")
        raise HTTPException(status_code=404, detail=f"GLB file not found: {filename}.glb")


# ==================== 버전 API ====================
@app.get("/api/version")
async def get_version():
    """README.md에서 버전 정보 추출"""
    import re
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # **현재 버전**: v3.8.202601081106 형식에서 버전 추출
            match = re.search(r'\*\*현재 버전\*\*:\s*v?([\d.]+)', content)
            if match:
                return {"version": match.group(1)}
            return {"version": "unknown"}
    except Exception as e:
        return {"version": "unknown", "error": str(e)}


# 데이터베이스 연결 설정 (환경 변수에서 로드)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'www.kdt2025.com'),
    'user': os.getenv('DB_USER', 'iyrc'),
    'passwd': os.getenv('DB_PASSWORD', 'dodan1004~!@'),
    'db': os.getenv('DB_NAME', 'bh2025'),
    'charset': 'utf8',
    'port': int(os.getenv('DB_PORT', '3306'))
}

def get_db_connection():
    """데이터베이스 연결 (재시도 및 예외 처리)"""
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.err.OperationalError as e:
        error_code = e.args[0] if e.args else 0
        error_msg = str(e)
        
        print(f"[ERROR] DB 연결 실패: {error_msg}")
        
        # 사용자 친화적인 에러 메시지
        if error_code == 2003:  # Can't connect to MySQL server
            raise HTTPException(
                status_code=503,
                detail="데이터베이스 서버 점검 중|현재 데이터베이스 서버에 연결할 수 없습니다.\n\n잠시 후 다시 시도해주시거나\n관리자에게 문의해주세요.\n\n💡 관리자(root) 계정은 정상 이용 가능합니다."
            )
        elif error_code == 1045:  # Access denied
            raise HTTPException(
                status_code=503,
                detail="데이터베이스 인증 오류|데이터베이스 접근 권한 문제가 발생했습니다.\n\n시스템 관리자에게 문의해주세요."
            )
        elif error_code == 2002:  # Can't connect through socket
            raise HTTPException(
                status_code=503,
                detail="데이터베이스 연결 실패|데이터베이스 서버와의 연결이 끊어졌습니다.\n\n네트워크 상태를 확인해주세요."
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="데이터베이스 오류|데이터베이스 서버에 일시적인 문제가 발생했습니다.\n\n잠시 후 다시 시도해주세요.\n\n오류 코드: " + str(error_code)
            )
    except Exception as e:
        print(f"[ERROR] DB 연결 중 예상치 못한 오류: {e}")
        raise HTTPException(
            status_code=503,
            detail="시스템 오류|데이터베이스 연결 중 오류가 발생했습니다.\n\n잠시 후 다시 시도해주세요."
        )

def ensure_photo_urls_column(cursor, table_name: str):
    """photo_urls 컬럼이 없으면 추가"""
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'photo_urls'")
        if not cursor.fetchone():
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN photo_urls TEXT")
    except:
        pass  # 이미 존재하거나 권한 문제

def ensure_career_path_column(cursor):
    """students 테이블에 career_path 컬럼이 없으면 추가하고 기본값 설정"""
    try:
        cursor.execute("SHOW COLUMNS FROM students LIKE 'career_path'")
        if not cursor.fetchone():
            # 컬럼 추가
            cursor.execute("ALTER TABLE students ADD COLUMN career_path VARCHAR(50) DEFAULT '4. 미정'")
            # 기존 데이터의 NULL 값을 '4. 미정'으로 업데이트
            cursor.execute("UPDATE students SET career_path = '4. 미정' WHERE career_path IS NULL")
            print("[OK] students 테이블에 career_path 컬럼 추가 완료")
    except Exception as e:
        print(f"[WARN] career_path 컬럼 추가 실패: {e}")
        pass  # 이미 존재하거나 권한 문제

def ensure_career_decision_column(cursor):
    """consultations 테이블에 career_decision 컬럼이 없으면 추가"""
    try:
        cursor.execute("SHOW COLUMNS FROM consultations LIKE 'career_decision'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE consultations ADD COLUMN career_decision VARCHAR(50) DEFAULT NULL")
            print("[OK] consultations 테이블에 career_decision 컬럼 추가 완료")
    except Exception as e:
        print(f"[WARN] career_decision 컬럼 추가 실패: {e}")
        pass

def ensure_profile_photo_columns(cursor, table_name: str):
    """profile_photo와 attachments 컬럼이 없으면 추가"""
    try:
        # profile_photo 컬럼 확인 및 추가 (단일 프로필 사진)
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'profile_photo'")
        if not cursor.fetchone():
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN profile_photo VARCHAR(500) DEFAULT NULL")
            print(f"[OK] {table_name} 테이블에 profile_photo 컬럼 추가 완료")
        
        # attachments 컬럼 확인 및 추가 (첨부 파일 배열, 최대 20개)
        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE 'attachments'")
        if not cursor.fetchone():
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN attachments TEXT DEFAULT NULL")
            print(f"[OK] {table_name} 테이블에 attachments 컬럼 추가 완료")
    except Exception as e:
        print(f"[WARN] {table_name} 컬럼 추가 실패: {e}")
        pass  # 이미 존재하거나 권한 문제

def ensure_menu_permissions_column(cursor):
    """instructor_codes 테이블에 menu_permissions 컬럼이 없으면 추가"""
    try:
        cursor.execute("SHOW COLUMNS FROM instructor_codes LIKE 'menu_permissions'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE instructor_codes ADD COLUMN menu_permissions TEXT DEFAULT NULL")
            print("[OK] instructor_codes 테이블에 menu_permissions 컬럼 추가 완료")
    except Exception as e:
        print(f"[WARN] menu_permissions 컬럼 추가 실패: {e}")
        pass

# FTP 설정 (환경 변수에서 로드)
FTP_CONFIG = {
    'host': os.getenv('FTP_HOST', 'bitnmeta2.synology.me'),
    'port': int(os.getenv('FTP_PORT', '2121')),
    'user': os.getenv('FTP_USER', 'ha'),
    'passwd': os.getenv('FTP_PASSWORD', 'dodan1004~')
}

# FTP 경로 설정
FTP_PATHS = {
    'guidance': '/homes/ha/camFTP/BH2025/guidance',  # 상담일지
    'train': '/homes/ha/camFTP/BH2025/train',        # 훈련일지
    'student': '/homes/ha/camFTP/BH2025/student',    # 학생
    'teacher': '/homes/ha/camFTP/BH2025/teacher',    # 강사
    'team': '/homes/ha/camFTP/BH2025/team'           # 팀(프로젝트)
}

def create_thumbnail(file_data: bytes, filename: str) -> str:
    """
    이미지 썸네일 생성 및 로컬 저장
    
    Args:
        file_data: 원본 이미지 바이트 데이터
        filename: 파일명
    
    Returns:
        썸네일 파일명
    """
    try:
        # 이미지 열기
        image = Image.open(io.BytesIO(file_data))
        
        # EXIF 방향 정보 처리
        try:
            from PIL import ImageOps
            image = ImageOps.exif_transpose(image)
        except:
            pass
        
        # RGB로 변환 (PNG 투명도 처리)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 썸네일 크기 (최대 200x200)
        image.thumbnail((200, 200), Image.Resampling.LANCZOS)
        
        # 썸네일 저장 경로 (크로스 플랫폼 지원)
        thumb_filename = f"thumb_{filename}"
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        thumbnails_dir = os.path.join(backend_dir, 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        thumb_path = os.path.join(thumbnails_dir, thumb_filename)
        
        # 썸네일 저장
        image.save(thumb_path, 'JPEG', quality=85, optimize=True)
        
        return thumb_filename
        
    except Exception as e:
        print(f"썸네일 생성 실패: {str(e)}")
        return None

def upload_to_ftp(file_data: bytes, filename: str, category: str) -> str:
    """
    FTP 서버에 파일 업로드 및 썸네일 생성 (기존 함수 - base64 업로드용)
    
    Args:
        file_data: 파일 바이트 데이터
        filename: 저장할 파일명 (확장자 포함)
        category: 카테고리 (guidance, train, student, teacher)
    
    Returns:
        업로드된 파일의 FTP URL
    """
    try:
        # 썸네일 생성 (백그라운드에서 실행, 실패해도 업로드는 계속)
        try:
            create_thumbnail(file_data, filename)
        except Exception as e:
            print(f"썸네일 생성 중 오류 (무시): {str(e)}")
        
        # FTP 연결
        ftp = FTP()
        ftp.encoding = 'utf-8'  # 한글 파일명 지원
        ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
        ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
        
        # 경로 이동
        target_path = FTP_PATHS.get(category)
        if not target_path:
            raise ValueError(f"Invalid category: {category}")
        
        try:
            ftp.cwd(target_path)
        except:
            # 경로가 없으면 생성
            path_parts = target_path.split('/')
            current_path = ''
            for part in path_parts:
                if not part:
                    continue
                current_path += '/' + part
                try:
                    ftp.cwd(current_path)
                except:
                    ftp.mkd(current_path)
                    ftp.cwd(current_path)
        
        # 파일 업로드
        ftp.storbinary(f'STOR {filename}', io.BytesIO(file_data))
        
        # URL 생성 (FTP URL)
        file_url = f"ftp://{FTP_CONFIG['host']}:{FTP_CONFIG['port']}{target_path}/{filename}"
        
        ftp.quit()
        return file_url
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP 업로드 실패: {str(e)}")


async def upload_stream_to_ftp(file: UploadFile, filename: str, category: str) -> str:
    """
    FTP 서버에 파일 스트리밍 업로드 (메모리 절약형 - 대용량 파일용)
    
    Args:
        file: FastAPI UploadFile 객체
        filename: 저장할 파일명 (확장자 포함)
        category: 카테고리 (guidance, train, student, teacher)
    
    Returns:
        업로드된 파일의 FTP URL
    """
    try:
        # FTP 연결
        ftp = FTP()
        ftp.encoding = 'utf-8'  # 한글 파일명 지원
        ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
        ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
        
        # 경로 이동
        target_path = FTP_PATHS.get(category)
        if not target_path:
            raise ValueError(f"Invalid category: {category}")
        
        try:
            ftp.cwd(target_path)
        except:
            # 경로가 없으면 생성
            path_parts = target_path.split('/')
            current_path = ''
            for part in path_parts:
                if not part:
                    continue
                current_path += '/' + part
                try:
                    ftp.cwd(current_path)
                except:
                    ftp.mkd(current_path)
                    ftp.cwd(current_path)
        
        # 파일 스트리밍 업로드 (1MB 청크 단위로 읽어서 전송)
        # 메모리에 전체 파일을 올리지 않음
        await file.seek(0)  # 파일 포인터를 처음으로
        ftp.storbinary(f'STOR {filename}', file.file, blocksize=1024*1024)
        
        # URL 생성 (FTP URL)
        file_url = f"ftp://{FTP_CONFIG['host']}:{FTP_CONFIG['port']}{target_path}/{filename}"
        
        ftp.quit()
        
        # 썸네일 생성 (백그라운드에서, 실패해도 무시)
        # 이미지 파일인 경우에만 썸네일 생성 시도
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            try:
                # 썸네일용으로 파일 일부만 읽기 (처음 10MB만)
                await file.seek(0)
                thumbnail_data = await file.read(10 * 1024 * 1024)
                if thumbnail_data:
                    create_thumbnail(thumbnail_data, filename)
            except Exception as e:
                print(f"썸네일 생성 실패: {str(e)}")
        
        return file_url
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FTP 스트리밍 업로드 실패: {str(e)}")

# ==================== 신규가입 (학생 등록 신청) API ====================

def ensure_student_registrations_table(cursor):
    """student_registrations 테이블이 없으면 생성"""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_registrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                birth_date VARCHAR(20),
                gender VARCHAR(10),
                phone VARCHAR(50),
                email VARCHAR(100),
                address TEXT,
                interests TEXT,
                education TEXT,
                introduction TEXT,
                course_code VARCHAR(50),
                profile_photo VARCHAR(500),
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                processed_at DATETIME,
                processed_by VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("[OK] student_registrations 테이블 확인/생성 완료")
        
        # 기존 profile_photo 컬럼이 TEXT인 경우 VARCHAR(500)으로 변경
        cursor.execute("SHOW COLUMNS FROM student_registrations LIKE 'profile_photo'")
        col = cursor.fetchone()
        if col and 'text' in col['Type'].lower():
            try:
                cursor.execute("ALTER TABLE student_registrations MODIFY COLUMN profile_photo VARCHAR(500)")
                print("[OK] student_registrations.profile_photo 컬럼 타입 변경: TEXT → VARCHAR(500)")
            except Exception as modify_err:
                print(f"[WARN] profile_photo 컬럼 타입 변경 실패: {modify_err}")
                
    except Exception as e:
        print(f"[WARN] student_registrations 테이블 생성 실패: {e}")

@app.get("/api/student-registrations")
async def get_student_registrations(status: Optional[str] = None):
    """신규가입 신청 목록 조회"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        ensure_student_registrations_table(cursor)
        conn.commit()

        query = "SELECT * FROM student_registrations WHERE 1=1"
        params = []

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        registrations = cursor.fetchall()

        # datetime 변환
        for reg in registrations:
            for key, value in reg.items():
                if isinstance(value, (datetime, date)):
                    reg[key] = value.isoformat()

        return registrations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/student-registrations")
async def create_student_registration(data: dict):
    """신규가입 신청 등록"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        ensure_student_registrations_table(cursor)
        conn.commit()

        name = data.get('name')
        if not name:
            raise HTTPException(status_code=400, detail="이름은 필수입니다")

        # profile_photo 처리: base64인 경우 특수 플래그로 저장
        profile_photo = data.get('profile_photo', '')
        if profile_photo and profile_photo.startswith('data:image'):
            # base64 데이터는 너무 커서 DB에 저장 불가 - 플래그만 저장
            profile_photo = '[BASE64_PENDING]'
            print(f"[INFO] Base64 이미지 감지 - 승인 시 처리 예정")

        cursor.execute("""
            INSERT INTO student_registrations
            (name, birth_date, gender, phone, email, address, interests, education, introduction, course_code, profile_photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name,
            data.get('birth_date'),
            data.get('gender'),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('address', ''),
            data.get('interests', ''),
            data.get('education', ''),
            data.get('introduction', ''),
            data.get('course_code', ''),
            profile_photo
        ))

        conn.commit()
        registration_id = cursor.lastrowid

        print(f"[OK] 신규가입 신청 등록 완료: ID={registration_id}, 이름={name}")

        return {"message": "신규가입 신청이 완료되었습니다", "id": registration_id}
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 신규가입 신청 실패: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.put("/api/student-registrations/{registration_id}/approve")
async def approve_student_registration(registration_id: int, data: dict):
    """신규가입 승인 - 학생 DB로 이동"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        ensure_student_registrations_table(cursor)
        conn.commit()

        # students 테이블에 필요한 컬럼 확인 및 추가
        cursor.execute("SHOW COLUMNS FROM students")
        existing_columns = {col['Field'] for col in cursor.fetchall()}
        
        required_columns = {
            'code': "VARCHAR(50) UNIQUE",
            'name': "VARCHAR(100)",
            'birth_date': "VARCHAR(20)",
            'gender': "VARCHAR(10)",
            'phone': "VARCHAR(50)",
            'email': "VARCHAR(100)",
            'address': "TEXT",
            'interests': "TEXT",
            'education': "VARCHAR(255)",
            'introduction': "TEXT",
            'course_code': "VARCHAR(50)",
            'profile_photo': "VARCHAR(500)",
            'password': "VARCHAR(100) DEFAULT 'kdt2025'"
        }
        
        columns_added = []
        for col_name, col_def in required_columns.items():
            if col_name not in existing_columns:
                try:
                    # UNIQUE 제약이 있으면 제거
                    col_def_no_unique = col_def.replace(' UNIQUE', '')
                    cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_def_no_unique}")
                    columns_added.append(col_name)
                    print(f"[OK] students 테이블에 {col_name} 컬럼 추가")
                except Exception as col_err:
                    print(f"[WARN] {col_name} 컬럼 추가 실패: {col_err}")
        
        if columns_added:
            conn.commit()
            print(f"[OK] students 테이블 컬럼 {len(columns_added)}개 추가 완료: {', '.join(columns_added)}")
        
        conn.commit()

        # 신청 정보 조회
        cursor.execute("SELECT * FROM student_registrations WHERE id = %s", (registration_id,))
        registration = cursor.fetchone()

        if not registration:
            raise HTTPException(status_code=404, detail="신청 정보를 찾을 수 없습니다")

        if registration['status'] != 'pending':
            raise HTTPException(status_code=400, detail="이미 처리된 신청입니다")

        # 학생 코드 생성
        cursor.execute("SELECT MAX(CAST(SUBSTRING(code, 2) AS UNSIGNED)) as max_code FROM students WHERE code LIKE 'S%'")
        result = cursor.fetchone()
        next_num = (result['max_code'] or 0) + 1
        student_code = f"S{next_num:03d}"

        # 학생 테이블에 추가 (비밀번호는 생년월일 6자리)
        birth_date = registration['birth_date'] or ''
        # 숫자만 추출하여 6자리로
        password = ''.join(filter(str.isdigit, birth_date))[:6] if birth_date else 'kdt2025'

        # profile_photo 처리
        profile_photo = registration['profile_photo'] or ''
        
        # [BASE64_PENDING] 플래그인 경우 사진 없음으로 처리
        if profile_photo == '[BASE64_PENDING]':
            profile_photo = ''
            print(f"[INFO] Base64 플래그 감지 - 사진 없이 진행")
        # base64 이미지면 FTP에 업로드하고 URL로 변환
        elif profile_photo and profile_photo.startswith('data:image'):
            try:
                # base64 이미지를 FTP에 업로드
                import base64
                import io
                from PIL import Image
                
                # data:image/jpeg;base64,... 형식에서 base64 부분만 추출
                header, encoded = profile_photo.split(',', 1)
                image_data = base64.b64decode(encoded)
                
                # 이미지 파일로 변환
                image = Image.open(io.BytesIO(image_data))
                
                # JPEG로 저장
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=85)
                output.seek(0)
                
                # FTP 업로드 (파일명: profile_학생코드_타임스탬프.jpg)
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"profile_{student_code}_{timestamp}.jpg"
                
                # FTP 연결 및 업로드 (FTP_CONFIG 사용)
                import ftplib
                
                if FTP_CONFIG['host'] and FTP_CONFIG['user']:
                    ftp = ftplib.FTP()
                    ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
                    ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
                    
                    # /homes/ha/camFTP/BH2025/student 디렉토리로 이동
                    ftp.cwd('/homes/ha/camFTP/BH2025/student')
                    
                    # 파일 업로드
                    ftp.storbinary(f'STOR {filename}', output)
                    ftp.quit()
                    
                    # FTP URL 생성
                    profile_photo = f"ftp://{FTP_CONFIG['host']}/homes/ha/camFTP/BH2025/student/{filename}"
                    print(f"[OK] Base64 이미지를 FTP로 변환: {profile_photo}")
                else:
                    # FTP 설정이 없으면 빈 문자열
                    profile_photo = ''
                    print(f"[WARN] FTP 설정 없음 - profile_photo를 빈 값으로 저장")
                    
            except Exception as img_err:
                print(f"[ERROR] Base64 → FTP 변환 실패: {img_err}")
                profile_photo = ''  # 에러 시 빈 값

        cursor.execute("""
            INSERT INTO students
            (code, name, birth_date, gender, phone, email, address, interests, education, introduction, course_code, profile_photo, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            student_code,
            registration['name'],
            registration['birth_date'],
            registration['gender'],
            registration['phone'],
            registration['email'],
            registration['address'],
            registration['interests'],
            registration['education'],
            registration['introduction'],
            registration['course_code'],
            profile_photo,  # 변환된 URL 또는 원본 URL
            password
        ))

        student_id = cursor.lastrowid

        # 신청 상태 업데이트
        processed_by = data.get('processed_by', '')
        cursor.execute("""
            UPDATE student_registrations
            SET status = 'approved', processed_at = NOW(), processed_by = %s
            WHERE id = %s
        """, (processed_by, registration_id))

        conn.commit()

        print(f"[OK] 신규가입 승인 완료: 신청ID={registration_id}, 학생ID={student_id}, 학생코드={student_code}")

        return {
            "message": "학생으로 등록되었습니다",
            "student_id": student_id,
            "student_code": student_code
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"[ERROR] 신규가입 승인 실패: {e}")
        print(f"[ERROR] 상세 오류:\n{error_detail}")
        raise HTTPException(status_code=500, detail=f"승인 처리 실패: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.put("/api/student-registrations/{registration_id}/reject")
async def reject_student_registration(registration_id: int, data: dict):
    """신규가입 거절"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        ensure_student_registrations_table(cursor)
        conn.commit()

        # 신청 상태 확인
        cursor.execute("SELECT status FROM student_registrations WHERE id = %s", (registration_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="신청 정보를 찾을 수 없습니다")

        if result[0] != 'pending':
            raise HTTPException(status_code=400, detail="이미 처리된 신청입니다")

        processed_by = data.get('processed_by', '')
        cursor.execute("""
            UPDATE student_registrations
            SET status = 'rejected', processed_at = NOW(), processed_by = %s
            WHERE id = %s
        """, (processed_by, registration_id))

        conn.commit()

        print(f"[OK] 신규가입 거절 완료: 신청ID={registration_id}")

        return {"message": "신청이 거절되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 신규가입 거절 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.delete("/api/student-registrations/{registration_id}")
async def delete_student_registration(registration_id: int):
    """신규가입 신청 삭제"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM student_registrations WHERE id = %s", (registration_id,))
        conn.commit()
        return {"message": "신청이 삭제되었습니다"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ==================== 학생 관리 API ====================

@app.get("/api/students")
async def get_students(
    course_code: Optional[str] = None,
    search: Optional[str] = None
):
    """학생 목록 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # career_path 컬럼 확인 및 추가
        ensure_career_path_column(cursor)
        
        # profile_photo, attachments 컬럼 확인 및 추가
        ensure_profile_photo_columns(cursor, 'students')
        
        query = "SELECT * FROM students WHERE 1=1"
        params = []
        
        if course_code:
            query += " AND course_code = %s"
            params.append(course_code)
        
        if search:
            query += " AND (name LIKE %s OR code LIKE %s OR phone LIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY code"
        
        cursor.execute(query, params)
        students = cursor.fetchall()
        
        # datetime 객체를 문자열로 변환
        for student in students:
            for key, value in student.items():
                if isinstance(value, (datetime, date)):
                    student[key] = value.isoformat()
                elif isinstance(value, bytes):
                    student[key] = None  # thumbnail은 제외
        
        return students
    finally:
        conn.close()

@app.get("/api/students/{student_id}")
async def get_student(student_id: int):
    """특정 학생 조회 (과정 정보 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # profile_photo, attachments 컬럼 확인 및 추가
        ensure_profile_photo_columns(cursor, 'students')
        
        # 학생 정보와 과정 정보를 JOIN하여 가져오기
        query = """
            SELECT s.*, c.name as course_name
            FROM students s
            LEFT JOIN courses c ON s.course_code = c.code
            WHERE s.id = %s
        """
        cursor.execute(query, (student_id,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
        
        # datetime 변환
        for key, value in student.items():
            if isinstance(value, (datetime, date)):
                student[key] = value.isoformat()
            elif isinstance(value, bytes):
                student[key] = None
        
        return student
    finally:
        conn.close()

@app.post("/api/students")
async def create_student(data: dict):
    """학생 생성 (프로필/첨부 파일 분리)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # profile_photo와 attachments 컬럼이 없으면 자동 생성
        ensure_profile_photo_columns(cursor, 'students')
        
        # 자동으로 학생 코드 생성
        cursor.execute("SELECT MAX(CAST(SUBSTRING(code, 2) AS UNSIGNED)) as max_code FROM students WHERE code LIKE 'S%'")
        result = cursor.fetchone()
        next_num = (result[0] or 0) + 1
        code = data.get('code', f"S{next_num:03d}")
        
        # 필수 필드 검증
        name = data.get('name')
        if not name:
            raise HTTPException(status_code=400, detail="이름은 필수입니다")
        
        # phone 필드 기본값 처리 (NULL 방지)
        phone = data.get('phone', '')
        if not phone:
            phone = ''
        
        # course_code 유효성 검증
        course_code = data.get('course_code')
        if course_code and course_code.strip():
            cursor.execute("SELECT COUNT(*) FROM courses WHERE code = %s", (course_code.strip(),))
            if cursor.fetchone()[0] == 0:
                course_code = None  # 유효하지 않은 과정 코드는 NULL로
        else:
            course_code = None  # 빈 문자열도 NULL로 처리
        
        query = """
            INSERT INTO students 
            (code, name, birth_date, gender, phone, email, address, interests, education, 
             introduction, campus, course_code, notes, profile_photo, attachments, career_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            code,
            name,
            data.get('birth_date'),
            data.get('gender'),
            phone,
            data.get('email'),
            data.get('address'),
            data.get('interests'),
            data.get('education'),
            data.get('introduction'),
            data.get('campus'),
            course_code,
            data.get('notes'),
            data.get('profile_photo'),
            data.get('attachments'),
            data.get('career_path', '4. 미정')
        ))
        
        conn.commit()
        return {"id": cursor.lastrowid, "code": code}
    finally:
        conn.close()

@app.put("/api/students/{student_id}")
async def update_student(student_id: int, data: dict):
    """학생 수정 (JSON 데이터 지원 - 프로필/첨부 파일 분리)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 새로운 컬럼 자동 생성 (profile_photo, attachments)
        ensure_profile_photo_columns(cursor, 'students')
        
        # 데이터 추출
        name = data.get('name')
        if not name:
            raise HTTPException(status_code=400, detail="이름은 필수입니다")
        
        birth_date = data.get('birth_date')
        gender = data.get('gender')
        phone = data.get('phone')
        email = data.get('email')
        address = data.get('address')
        interests = data.get('interests')
        education = data.get('education')
        introduction = data.get('introduction')
        campus = data.get('campus')
        course_code = data.get('course_code')
        notes = data.get('notes')
        career_path = data.get('career_path', '4. 미정')
        
        # 프로필 사진 (단일 URL)
        profile_photo = data.get('profile_photo')
        
        # 첨부 파일 (JSON 배열, 최대 20개)
        attachments = data.get('attachments')
        if attachments:
            import json
            try:
                attachment_list = json.loads(attachments) if isinstance(attachments, str) else attachments
                if len(attachment_list) > 20:
                    raise HTTPException(status_code=400, detail="첨부 파일은 최대 20개까지 가능합니다")
                attachments = json.dumps(attachment_list)
            except json.JSONDecodeError:
                attachments = None
        
        # type 컬럼 확인 및 기본값 처리
        cursor.execute("SHOW COLUMNS FROM students LIKE 'type'")
        has_type_column = cursor.fetchone() is not None
        
        if has_type_column:
            # type 컬럼이 있으면 포함
            query = """
                UPDATE students 
                SET name = %s, birth_date = %s, gender = %s, phone = %s, email = %s,
                    address = %s, interests = %s, education = %s, introduction = %s,
                    campus = %s, course_code = %s, notes = %s, career_path = %s, 
                    profile_photo = %s, attachments = %s,
                    type = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (
                name, birth_date, gender, phone, email,
                address, interests, education, introduction,
                campus, course_code, notes, career_path,
                profile_photo, attachments,
                '1',  # 기본값: 일반 학생
                student_id
            ))
        else:
            # type 컬럼이 없으면 제외
            query = """
                UPDATE students 
                SET name = %s, birth_date = %s, gender = %s, phone = %s, email = %s,
                    address = %s, interests = %s, education = %s, introduction = %s,
                    campus = %s, course_code = %s, notes = %s, career_path = %s,
                    profile_photo = %s, attachments = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (
                name, birth_date, gender, phone, email,
                address, interests, education, introduction,
                campus, course_code, notes, career_path,
                profile_photo, attachments,
                student_id
            ))
        
        conn.commit()
        return {"id": student_id}
    finally:
        conn.close()

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: int):
    """학생 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        return {"message": "학생이 삭제되었습니다"}
    finally:
        conn.close()

@app.post("/api/students/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """Excel 파일로 학생 일괄 등록"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Excel 파일만 업로드 가능합니다")
    
    try:
        # Excel 파일 읽기
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 현재 최대 학생 코드 조회
        cursor.execute("SELECT MAX(CAST(SUBSTRING(code, 2) AS UNSIGNED)) as max_code FROM students WHERE code LIKE 'S%'")
        result = cursor.fetchone()
        next_num = (result[0] or 0) + 1
        
        success_count = 0
        error_list = []
        
        for idx, row in df.iterrows():
            try:
                code = f"S{next_num:03d}"
                
                # 컬럼명 매핑
                name = row.get('이름', '')
                birth_date = str(row.get('생년월일(78.01.12)', ''))
                gender = row.get('성별\n(선택)', '')
                phone = str(row.get('휴대폰번호', ''))
                email = row.get('이메일', '')
                address = row.get('주소', '')
                interests = row.get('관심 있는 분야(2개)', '')
                education = row.get('최종 학교/학년(졸업)', '')
                introduction = row.get('자기소개 (200자 내외)', '')
                campus = row.get('지원하고자 하는 캠퍼스를 선택하세요', '')
                
                query = """
                    INSERT INTO students 
                    (code, name, birth_date, gender, phone, email, address, interests, education, introduction, campus)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    code, name, birth_date, gender, phone, email, 
                    address, interests, education, introduction, campus
                ))
                
                next_num += 1
                success_count += 1
                
            except Exception as e:
                error_list.append(f"행 {idx+2}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"{success_count}명의 학생이 등록되었습니다",
            "success_count": success_count,
            "errors": error_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류: {str(e)}")

@app.get("/api/template/students")
async def download_template():
    """학생 등록 템플릿 다운로드"""
    template_path = "/home/user/webapp/student_template.xlsx"
    if os.path.exists(template_path):
        return FileResponse(
            template_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="학생등록양식.xlsx"
        )
    raise HTTPException(status_code=404, detail="템플릿 파일을 찾을 수 없습니다")

# ==================== 과목 관리 API ====================

@app.get("/api/subjects")
async def get_subjects():
    """과목 목록 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT s.*, i.name as instructor_name
            FROM subjects s
            LEFT JOIN instructors i ON s.main_instructor = i.code
            ORDER BY s.code
        """)
        subjects = cursor.fetchall()
        
        for subject in subjects:
            for key, value in subject.items():
                if isinstance(value, (datetime, date)):
                    subject[key] = value.isoformat()
        
        return subjects
    finally:
        conn.close()

@app.get("/api/subjects/{subject_code}")
async def get_subject(subject_code: str):
    """특정 과목 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT s.*, i.name as instructor_name
            FROM subjects s
            LEFT JOIN instructors i ON s.main_instructor = i.code
            WHERE s.code = %s
        """, (subject_code,))
        subject = cursor.fetchone()
        
        if not subject:
            raise HTTPException(status_code=404, detail="과목을 찾을 수 없습니다")
        
        for key, value in subject.items():
            if isinstance(value, (datetime, date)):
                subject[key] = value.isoformat()
        
        return subject
    finally:
        conn.close()

@app.post("/api/subjects")
async def create_subject(data: dict):
    """과목 생성"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO subjects 
            (code, name, main_instructor, day_of_week, is_biweekly, week_offset, hours, description,
             sub_subject_1, sub_hours_1, sub_subject_2, sub_hours_2, sub_subject_3, sub_hours_3,
             sub_subject_4, sub_hours_4, sub_subject_5, sub_hours_5)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            data.get('code'),
            data.get('name'),
            data.get('main_instructor'),
            data.get('day_of_week', 0),
            data.get('is_biweekly', 0),
            data.get('week_offset', 0),
            data.get('hours', 0),
            data.get('description', ''),
            data.get('sub_subject_1', ''),
            data.get('sub_hours_1', 0),
            data.get('sub_subject_2', ''),
            data.get('sub_hours_2', 0),
            data.get('sub_subject_3', ''),
            data.get('sub_hours_3', 0),
            data.get('sub_subject_4', ''),
            data.get('sub_hours_4', 0),
            data.get('sub_subject_5', ''),
            data.get('sub_hours_5', 0)
        ))
        
        conn.commit()
        return {"code": data.get('code')}
    except pymysql.err.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    finally:
        conn.close()

@app.put("/api/subjects/{subject_code}")
async def update_subject(subject_code: str, data: dict):
    """과목 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 업데이트할 필드 동적 구성
        update_fields = []
        update_values = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            update_values.append(data['name'])
        
        if 'main_instructor' in data:
            update_fields.append("main_instructor = %s")
            update_values.append(data['main_instructor'])
        
        if 'assistant_instructor' in data:
            update_fields.append("assistant_instructor = %s")
            update_values.append(data['assistant_instructor'])
        
        if 'reserve_instructor' in data:
            update_fields.append("reserve_instructor = %s")
            update_values.append(data['reserve_instructor'])
        
        if 'instructor_code' in data:
            update_fields.append("instructor_code = %s")
            update_values.append(data['instructor_code'])
        
        if 'day_of_week' in data:
            update_fields.append("day_of_week = %s")
            update_values.append(data['day_of_week'])
        
        if 'is_biweekly' in data:
            update_fields.append("is_biweekly = %s")
            update_values.append(data['is_biweekly'])
        
        if 'week_offset' in data:
            update_fields.append("week_offset = %s")
            update_values.append(data['week_offset'])
        
        if 'hours' in data:
            update_fields.append("hours = %s")
            update_values.append(data['hours'])
        
        if 'description' in data:
            update_fields.append("description = %s")
            update_values.append(data['description'])
        
        # 세부 과목들
        for i in range(1, 6):
            if f'sub_subject_{i}' in data:
                update_fields.append(f"sub_subject_{i} = %s")
                update_values.append(data[f'sub_subject_{i}'])
            if f'sub_hours_{i}' in data:
                update_fields.append(f"sub_hours_{i} = %s")
                update_values.append(data[f'sub_hours_{i}'])
        
        if not update_fields:
            return {"code": subject_code, "message": "No fields to update"}
        
        query = f"UPDATE subjects SET {', '.join(update_fields)} WHERE code = %s"
        update_values.append(subject_code)
        
        cursor.execute(query, tuple(update_values))
        conn.commit()
        return {"code": subject_code}
    except Exception as e:
        import traceback
        print(f"교과목 수정 오류: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"교과목 수정 실패: {str(e)}")
    finally:
        conn.close()

@app.delete("/api/subjects/{subject_code}")
async def delete_subject(subject_code: str):
    """과목 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE code = %s", (subject_code,))
        conn.commit()
        return {"message": "과목이 삭제되었습니다"}
    finally:
        conn.close()

@app.post("/api/courses/{course_code}/subjects")
async def save_course_subjects(course_code: str, data: dict):
    """과정-교과목 관계 저장"""
    subject_codes = data.get('subject_codes', [])
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 기존 과정-교과목 관계 삭제
        cursor.execute("DELETE FROM course_subjects WHERE course_code = %s", (course_code,))
        
        # 새로운 관계 추가
        for idx, subject_code in enumerate(subject_codes, start=1):
            cursor.execute("""
                INSERT INTO course_subjects (course_code, subject_code, display_order)
                VALUES (%s, %s, %s)
            """, (course_code, subject_code, idx))
        
        conn.commit()
        return {
            "message": f"{len(subject_codes)}개의 교과목이 저장되었습니다",
            "course_code": course_code,
            "subject_count": len(subject_codes)
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"교과목 저장 실패: {str(e)}")
    finally:
        conn.close()

# ==================== 유틸리티 함수 ====================

def convert_datetime(obj):
    """datetime 객체를 문자열로 변환 + internship → workship 컬럼명 매핑"""
    from datetime import timedelta
    
    # DB 컬럼명 → 프론트엔드 필드명 매핑
    if 'internship_hours' in obj:
        obj['workship_hours'] = obj.pop('internship_hours')
    if 'internship_end_date' in obj:
        obj['workship_end_date'] = obj.pop('internship_end_date')
    
    for key, value in obj.items():
        if isinstance(value, (datetime, date)):
            obj[key] = value.isoformat()
        elif isinstance(value, timedelta):
            # timedelta를 HH:MM:SS 형식으로 변환
            total_seconds = int(value.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            obj[key] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        elif isinstance(value, bytes):
            obj[key] = None
    return obj

# ==================== 강사코드 관리 API ====================

@app.get("/api/instructor-codes")
async def get_instructor_codes():
    """강사코드 목록 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # menu_permissions 컬럼 확인 및 추가
        ensure_menu_permissions_column(cursor)
        conn.commit()
        
        # permissions 컬럼 존재 여부 확인 및 추가
        cursor.execute("SHOW COLUMNS FROM instructor_codes LIKE 'permissions'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE instructor_codes ADD COLUMN permissions TEXT DEFAULT NULL")
            conn.commit()
            print("[OK] instructor_codes 테이블에 permissions 컬럼 추가")
        
        # "0. 관리자" 타입이 없으면 추가
        cursor.execute("SELECT * FROM instructor_codes WHERE code = '0'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO instructor_codes (code, name, type, permissions)
                VALUES ('0', '관리자', '0', NULL)
            """)
            conn.commit()
            print("[OK] '0. 관리자' 타입 추가 완료")
        
        cursor.execute("SELECT * FROM instructor_codes ORDER BY code")
        codes = cursor.fetchall()
        
        # permissions와 menu_permissions를 JSON으로 파싱
        import json
        for code in codes:
            if code.get('permissions'):
                try:
                    code['permissions'] = json.loads(code['permissions'])
                except:
                    code['permissions'] = None
            if code.get('menu_permissions'):
                try:
                    code['menu_permissions'] = json.loads(code['menu_permissions'])
                except:
                    code['menu_permissions'] = None
        
        return [convert_datetime(code) for code in codes]
    finally:
        conn.close()

@app.post("/api/instructor-codes")
async def create_instructor_code(data: dict):
    """강사코드 생성"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # menu_permissions 컬럼 확인 및 추가
        ensure_menu_permissions_column(cursor)
        conn.commit()
        
        # default_screen 컬럼이 없으면 추가
        cursor.execute("SHOW COLUMNS FROM instructor_codes LIKE 'default_screen'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE instructor_codes ADD COLUMN default_screen VARCHAR(50) DEFAULT NULL")
            conn.commit()
            print("[OK] instructor_codes 테이블에 default_screen 컬럼 추가")
        
        import json
        permissions_json = json.dumps(data.get('permissions', {})) if data.get('permissions') else None
        menu_permissions_json = json.dumps(data.get('menu_permissions', [])) if data.get('menu_permissions') else None
        default_screen = data.get('default_screen')
        
        query = """
            INSERT INTO instructor_codes (code, name, type, permissions, menu_permissions, default_screen)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (data['code'], data['name'], data['type'], permissions_json, menu_permissions_json, default_screen))
        conn.commit()
        return {"code": data['code']}
    finally:
        conn.close()

@app.put("/api/instructor-codes/{code}")
async def update_instructor_code(code: str, data: dict):
    """강사코드 수정 (권한 설정 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # menu_permissions 컬럼 확인 및 추가
        ensure_menu_permissions_column(cursor)
        conn.commit()
        
        # default_screen 컬럼이 없으면 추가
        cursor.execute("SHOW COLUMNS FROM instructor_codes LIKE 'default_screen'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE instructor_codes ADD COLUMN default_screen VARCHAR(50) DEFAULT NULL")
            conn.commit()
            print("[OK] instructor_codes 테이블에 default_screen 컬럼 추가")
        
        import json
        permissions_json = json.dumps(data.get('permissions', {})) if data.get('permissions') else None
        menu_permissions_json = json.dumps(data.get('menu_permissions', [])) if data.get('menu_permissions') else None
        default_screen = data.get('default_screen')
        
        query = """
            UPDATE instructor_codes
            SET name = %s, type = %s, permissions = %s, menu_permissions = %s, default_screen = %s
            WHERE code = %s
        """
        cursor.execute(query, (data['name'], data['type'], permissions_json, menu_permissions_json, default_screen, code))
        conn.commit()
        return {"code": code}
    finally:
        conn.close()

@app.delete("/api/instructor-codes/{code}")
async def delete_instructor_code(code: str):
    """강사코드 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 사용 중인지 확인
        cursor.execute("SELECT COUNT(*) as cnt FROM instructors WHERE instructor_type = %s", (code,))
        result = cursor.fetchone()
        if result and result['cnt'] > 0:
            raise HTTPException(status_code=400, detail=f"이 강사코드는 {result['cnt']}명의 강사가 사용 중입니다. 먼저 강사의 타입을 변경하세요.")
        
        cursor.execute("DELETE FROM instructor_codes WHERE code = %s", (code,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="강사코드를 찾을 수 없습니다")
        
        conn.commit()
        return {"message": "강사코드가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")
    finally:
        conn.close()

@app.post("/api/admin/migrate-admin-code")
async def migrate_admin_code():
    """관리자 코드를 0에서 IC-999로 마이그레이션"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 0. type 컬럼 길이 확인 및 확장
        cursor.execute("SHOW COLUMNS FROM instructor_codes LIKE 'type'")
        type_column = cursor.fetchone()
        if type_column:
            # VARCHAR(10) 또는 더 작은 경우 VARCHAR(50)으로 확장
            cursor.execute("ALTER TABLE instructor_codes MODIFY COLUMN type VARCHAR(50)")
            conn.commit()
        
        # 1. code='0' 확인
        cursor.execute("SELECT * FROM instructor_codes WHERE code = '0'")
        old_admin = cursor.fetchone()
        
        if not old_admin:
            # code='0'이 없으면 IC-999가 이미 존재하는지 확인
            cursor.execute("SELECT * FROM instructor_codes WHERE code = 'IC-999'")
            existing_ic999 = cursor.fetchone()
            if existing_ic999:
                return {
                    "success": True,
                    "message": "이미 마이그레이션되었습니다",
                    "admin_code": existing_ic999,
                    "instructor_count": 0
                }
            else:
                raise HTTPException(status_code=404, detail="관리자 코드 '0'을 찾을 수 없습니다")
        
        # 2. IC-999가 이미 있는지 확인하고 삭제
        cursor.execute("SELECT * FROM instructor_codes WHERE code = 'IC-999'")
        existing = cursor.fetchone()
        if existing:
            cursor.execute("DELETE FROM instructor_codes WHERE code = 'IC-999'")
            conn.commit()
        
        # 3. code='0'의 모든 데이터 가져오기
        old_data = {
            'name': old_admin['name'],
            'type': '0. 관리자',
            'permissions': old_admin.get('permissions'),
            'default_screen': old_admin.get('default_screen'),
            'created_at': old_admin.get('created_at'),
            'updated_at': old_admin.get('updated_at')
        }
        
        # 4. code='0' 삭제
        cursor.execute("DELETE FROM instructor_codes WHERE code = '0'")
        conn.commit()
        
        # 5. IC-999로 새로 삽입
        import json as json_module
        permissions_json = json_module.dumps(old_data['permissions']) if old_data['permissions'] else None
        
        cursor.execute("""
            INSERT INTO instructor_codes (code, name, type, permissions, default_screen, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, ('IC-999', old_data['name'], old_data['type'], permissions_json, old_data['default_screen'], old_data['created_at']))
        
        # 6. instructors 테이블의 instructor_type도 업데이트
        cursor.execute("""
            UPDATE instructors
            SET instructor_type = 'IC-999'
            WHERE instructor_type = '0'
        """)
        
        conn.commit()
        
        # 7. 결과 확인
        cursor.execute("SELECT * FROM instructor_codes WHERE code = 'IC-999'")
        new_admin = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as cnt FROM instructors WHERE instructor_type = 'IC-999'")
        instructor_count = cursor.fetchone()
        
        return {
            "success": True,
            "message": "관리자 코드가 성공적으로 마이그레이션되었습니다",
            "admin_code": new_admin,
            "instructor_count": instructor_count['cnt']
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"마이그레이션 실패: {str(e)}")
    finally:
        conn.close()

# ==================== 강사 관리 API ====================

@app.get("/api/instructors")
async def get_instructors(search: Optional[str] = None):
    """강사 목록 조회 (검색 기능 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # password 컬럼 존재 여부 확인
        cursor.execute("SHOW COLUMNS FROM instructors LIKE 'password'")
        has_password = cursor.fetchone() is not None
        
        # profile_photo와 attachments 컬럼 자동 생성
        ensure_profile_photo_columns(cursor, 'instructors')
        
        if has_password:
            query = """
                SELECT i.code, TRIM(i.name) as name, i.phone, i.major, i.instructor_type, 
                       i.email, i.created_at, i.updated_at, i.profile_photo, i.attachments, i.password,
                       ic.name as instructor_type_name, ic.type as instructor_type_type
                FROM instructors i
                LEFT JOIN instructor_codes ic ON i.instructor_type = ic.code
                WHERE 1=1
            """
        else:
            query = """
                SELECT i.code, TRIM(i.name) as name, i.phone, i.major, i.instructor_type, 
                       i.email, i.created_at, i.updated_at, i.profile_photo, i.attachments,
                       ic.name as instructor_type_name, ic.type as instructor_type_type
                FROM instructors i
                LEFT JOIN instructor_codes ic ON i.instructor_type = ic.code
                WHERE 1=1
            """
        params = []
        
        if search:
            query += " AND (i.name LIKE %s OR i.code LIKE %s OR i.phone LIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY i.code"
        
        cursor.execute(query, params)
        instructors = cursor.fetchall()
        return [convert_datetime(inst) for inst in instructors]
    finally:
        conn.close()

@app.get("/api/instructors/{code}")
async def get_instructor(code: str):
    """특정 강사 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT i.*, ic.name as type_name
            FROM instructors i
            LEFT JOIN instructor_codes ic ON i.instructor_type = ic.code
            WHERE i.code = %s
        """, (code,))
        instructor = cursor.fetchone()
        if not instructor:
            raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다")
        return convert_datetime(instructor)
    finally:
        conn.close()

@app.post("/api/instructors")
async def create_instructor(data: dict):
    """강사 생성 (프로필/첨부 파일 분리)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # profile_photo와 attachments 컬럼이 없으면 자동 생성
        ensure_profile_photo_columns(cursor, 'instructors')
        
        query = """
            INSERT INTO instructors (code, name, phone, major, instructor_type, email, profile_photo, attachments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['code'], data['name'], data.get('phone'),
            data.get('major'), data.get('instructor_type'), data.get('email'),
            data.get('profile_photo'), data.get('attachments')
        ))
        conn.commit()
        return {"code": data['code']}
    finally:
        conn.close()

@app.put("/api/instructors/{code}")
async def update_instructor(code: str, data: dict):
    """강사 수정 (JSON 데이터 지원 - 프로필/첨부 파일 분리)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 새로운 컬럼 자동 생성 (profile_photo, attachments)
        ensure_profile_photo_columns(cursor, 'instructors')
        
        # 데이터 추출
        name = data.get('name')
        if not name:
            raise HTTPException(status_code=400, detail="이름은 필수입니다")
        
        phone = data.get('phone')
        major = data.get('major')
        email = data.get('email')
        
        # 프로필 사진 (단일 URL)
        profile_photo = data.get('profile_photo')
        
        # 첨부 파일 (JSON 배열, 최대 20개)
        attachments = data.get('attachments')
        if attachments:
            import json
            try:
                attachment_list = json.loads(attachments) if isinstance(attachments, str) else attachments
                if len(attachment_list) > 20:
                    raise HTTPException(status_code=400, detail="첨부 파일은 최대 20개까지 가능합니다")
                attachments = json.dumps(attachment_list)
            except json.JSONDecodeError:
                attachments = None
        
        # instructor_type은 MyPage에서 변경하지 않음 (외래 키 제약 조건)
        query = """
            UPDATE instructors
            SET name = %s, phone = %s, major = %s, email = %s, 
                profile_photo = %s, attachments = %s
            WHERE code = %s
        """
        cursor.execute(query, (
            name, phone, major, email, profile_photo, attachments, code
        ))
        conn.commit()
        return {"code": code}
    finally:
        conn.close()

@app.delete("/api/instructors/{code}")
async def delete_instructor(code: str):
    """강사 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM instructors WHERE code = %s", (code,))
        conn.commit()
        return {"message": "강사가 삭제되었습니다"}
    finally:
        conn.close()

# ==================== 공휴일 관리 API ====================

@app.get("/api/holidays")
async def get_holidays(year: Optional[int] = None):
    """공휴일 목록 조회 (연도별 필터)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if year:
            cursor.execute("""
                SELECT * FROM holidays
                WHERE YEAR(holiday_date) = %s
                ORDER BY holiday_date
            """, (year,))
        else:
            cursor.execute("SELECT * FROM holidays ORDER BY holiday_date")
        
        holidays = cursor.fetchall()
        return [convert_datetime(h) for h in holidays]
    finally:
        conn.close()

@app.post("/api/holidays")
async def create_holiday(data: dict):
    """공휴일 생성 (중복 시 조용히 무시)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 중복 체크: 같은 날짜에 같은 이름의 공휴일이 있는지 확인
        cursor.execute("""
            SELECT id FROM holidays 
            WHERE holiday_date = %s AND name = %s
        """, (data['holiday_date'], data['name']))
        existing = cursor.fetchone()
        
        if existing:
            # 이미 존재하는 경우 조용히 기존 ID 반환 (에러 없이)
            print(f"ℹ️  이미 등록된 공휴일: {data['holiday_date']} - {data['name']}")
            return {"id": existing['id'], "message": "이미 등록된 공휴일입니다"}
        
        # 새로 등록
        query = """
            INSERT INTO holidays (holiday_date, name, is_legal)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (data['holiday_date'], data['name'], data.get('is_legal', 0)))
        conn.commit()
        return {"id": cursor.lastrowid, "message": "공휴일이 추가되었습니다"}
    finally:
        conn.close()

@app.put("/api/holidays/{holiday_id}")
async def update_holiday(holiday_id: int, data: dict):
    """공휴일 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE holidays
            SET holiday_date = %s, name = %s, is_legal = %s
            WHERE id = %s
        """
        cursor.execute(query, (data['holiday_date'], data['name'], data.get('is_legal', 0), holiday_id))
        conn.commit()
        return {"id": holiday_id}
    finally:
        conn.close()

@app.delete("/api/holidays/{holiday_id}")
async def delete_holiday(holiday_id: int):
    """공휴일 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM holidays WHERE id = %s", (holiday_id,))
        conn.commit()
        return {"message": "공휴일이 삭제되었습니다"}
    finally:
        conn.close()

@app.post("/api/holidays/auto-add/{year}")
async def auto_add_holidays(year: int):
    """법정공휴일 자동 추가"""
    from datetime import datetime, timedelta
    import korean_lunar_calendar
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 법정공휴일 정의 (양력)
        solar_holidays = [
            (1, 1, "신정"),
            (3, 1, "삼일절"),
            (5, 5, "어린이날"),
            (6, 6, "현충일"),
            (8, 15, "광복절"),
            (10, 3, "개천절"),
            (10, 9, "한글날"),
            (12, 25, "성탄절"),
        ]
        
        # 음력 공휴일 (설날, 추석, 부처님오신날)
        lunar_holidays = [
            # 설날: 음력 12/30, 1/1, 1/2
            ((12, 30), "설날 연휴"),
            ((1, 1), "설날"),
            ((1, 2), "설날 연휴"),
            # 부처님오신날: 음력 4/8
            ((4, 8), "부처님오신날"),
            # 추석: 음력 8/14, 8/15, 8/16
            ((8, 14), "추석 연휴"),
            ((8, 15), "추석"),
            ((8, 16), "추석 연휴"),
        ]
        
        added = 0
        skipped = 0
        
        # 양력 공휴일 추가
        for month, day, name in solar_holidays:
            holiday_date = f"{year}-{month:02d}-{day:02d}"
            
            # 중복 체크
            cursor.execute("""
                SELECT id FROM holidays 
                WHERE holiday_date = %s AND name = %s
            """, (holiday_date, name))
            
            if cursor.fetchone():
                skipped += 1
                print(f"ℹ️  이미 등록됨: {holiday_date} - {name}")
            else:
                cursor.execute("""
                    INSERT INTO holidays (holiday_date, name, is_legal)
                    VALUES (%s, %s, 1)
                """, (holiday_date, name))
                added += 1
                print(f"[OK] 추가됨: {holiday_date} - {name}")
        
        # 음력 공휴일 추가
        try:
            for (lunar_month, lunar_day), name in lunar_holidays:
                # 음력을 양력으로 변환
                calendar = korean_lunar_calendar.KoreanLunarCalendar()
                
                # 설날 전날(음력 12/30)의 경우 전년도 기준
                if lunar_month == 12 and lunar_day == 30:
                    calendar.setLunarDate(year - 1, lunar_month, lunar_day, False)
                else:
                    calendar.setLunarDate(year, lunar_month, lunar_day, False)
                
                solar_date = calendar.SolarIsoFormat()
                
                # 중복 체크
                cursor.execute("""
                    SELECT id FROM holidays 
                    WHERE holiday_date = %s AND name = %s
                """, (solar_date, name))
                
                if cursor.fetchone():
                    skipped += 1
                    print(f"ℹ️  이미 등록됨: {solar_date} - {name} (음력)")
                else:
                    cursor.execute("""
                        INSERT INTO holidays (holiday_date, name, is_legal)
                        VALUES (%s, %s, 1)
                    """, (solar_date, name))
                    added += 1
                    print(f"[OK] 추가됨: {solar_date} - {name} (음력)")
        except Exception as e:
            print(f"[WARN]  음력 변환 실패 (korean_lunar_calendar 라이브러리 필요): {e}")
            print("ℹ️  음력 공휴일은 추가되지 않았습니다. 수동으로 추가해주세요.")
        
        conn.commit()
        
        total = added + skipped
        return {
            "year": year,
            "added": added,
            "skipped": skipped,
            "total": total,
            "message": f"{year}년 법정공휴일 자동 추가 완료"
        }
    finally:
        conn.close()

# ==================== 과정(학급) 관리 API ====================

@app.get("/api/courses")
async def get_courses():
    """과정 목록 조회 (학생수, 과목수, 교과목 목록 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT s.id) as student_count,
                   COUNT(DISTINCT cs.subject_code) as subject_count
            FROM courses c
            LEFT JOIN students s ON c.code = s.course_code
            LEFT JOIN course_subjects cs ON c.code = cs.course_code
            GROUP BY c.code
            ORDER BY c.code
        """)
        courses = cursor.fetchall()
        
        # 각 과정의 교과목 목록 조회
        for course in courses:
            cursor.execute("""
                SELECT subject_code
                FROM course_subjects
                WHERE course_code = %s
                ORDER BY subject_code
            """, (course['code'],))
            subjects = cursor.fetchall()
            course['subjects'] = [s['subject_code'] for s in subjects]
        
        return [convert_datetime(course) for course in courses]
    finally:
        conn.close()

@app.get("/api/courses/{code}")
async def get_course(code: str):
    """특정 과정 조회 (교과목 포함)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT c.*,
                   COUNT(DISTINCT s.id) as student_count
            FROM courses c
            LEFT JOIN students s ON c.code = s.course_code
            WHERE c.code = %s
            GROUP BY c.code
        """, (code,))
        course = cursor.fetchone()
        if not course:
            raise HTTPException(status_code=404, detail="과정을 찾을 수 없습니다")
        
        # 과정의 교과목 조회
        cursor.execute("""
            SELECT subject_code
            FROM course_subjects
            WHERE course_code = %s
            ORDER BY subject_code
        """, (code,))
        subjects = cursor.fetchall()
        course['subjects'] = [s['subject_code'] for s in subjects]
        
        return convert_datetime(course)
    finally:
        conn.close()

@app.post("/api/courses")
async def create_course(data: dict):
    """과정 생성"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 이모지 제거 (utf8mb4 미지원 DB 컬럼 대응)
        def remove_emoji(text):
            if not text:
                return text
            try:
                # 4바이트 UTF-8 문자 모두 제거 (이모지 포함)
                return ''.join(c for c in text if len(c.encode('utf-8')) < 4)
            except:
                return text
        
        # morning_hours, afternoon_hours 컬럼이 없으면 추가
        try:
            cursor.execute("""
                ALTER TABLE courses 
                ADD COLUMN morning_hours INT DEFAULT 4
            """)
        except:
            pass  # 이미 존재하면 무시
        
        try:
            cursor.execute("""
                ALTER TABLE courses 
                ADD COLUMN afternoon_hours INT DEFAULT 4
            """)
        except:
            pass  # 이미 존재하면 무시
        
        # notes 필드 이모지 제거
        notes_cleaned = remove_emoji(data.get('notes'))
        
        query = """
            INSERT INTO courses (code, name, lecture_hours, project_hours, internship_hours,
                                capacity, location, notes, start_date, lecture_end_date,
                                project_end_date, internship_end_date, final_end_date, total_days,
                                morning_hours, afternoon_hours)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['code'], data['name'], data['lecture_hours'], data['project_hours'],
            data.get('workship_hours', 0), data['capacity'], data.get('location'),  # workship_hours → DB에는 internship_hours
            notes_cleaned, data.get('start_date'), data.get('lecture_end_date'),
            data.get('project_end_date'), data.get('workship_end_date'),  # workship_end_date → DB에는 internship_end_date
            data.get('final_end_date'), data.get('total_days'),
            data.get('morning_hours', 4), data.get('afternoon_hours', 4)
        ))
        conn.commit()
        return {"code": data['code']}
    except Exception as e:
        conn.rollback()
        import traceback
        print(f"[ERROR] 과정 생성 에러: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"과정 생성 실패: {str(e)}")
    finally:
        conn.close()

@app.put("/api/courses/{code}")
async def update_course(code: str, data: dict):
    """과정 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 이모지 제거 (utf8mb4 미지원 DB 컬럼 대응)
        def remove_emoji(text):
            if not text:
                return text
            try:
                # 4바이트 UTF-8 문자 모두 제거 (이모지 포함)
                return ''.join(c for c in text if len(c.encode('utf-8')) < 4)
            except:
                return text
        
        # 동적 UPDATE 쿼리 생성
        update_fields = []
        values = []
        
        field_mapping = {
            'name': 'name',
            'lecture_hours': 'lecture_hours',
            'project_hours': 'project_hours',
            'workship_hours': 'internship_hours',  # DB 컬럼명은 아직 internship_hours
            'capacity': 'capacity',
            'location': 'location',
            'notes': 'notes',
            'start_date': 'start_date',
            'lecture_end_date': 'lecture_end_date',
            'project_end_date': 'project_end_date',
            'workship_end_date': 'internship_end_date',  # DB 컬럼명은 아직 internship_end_date
            'final_end_date': 'final_end_date',
            'total_days': 'total_days',
            'morning_hours': 'morning_hours',
            'afternoon_hours': 'afternoon_hours'
        }
        
        for field_name, db_column in field_mapping.items():
            if field_name in data:
                value = data[field_name]
                # notes 필드만 이모지 제거
                if field_name == 'notes':
                    value = remove_emoji(value)
                update_fields.append(f"{db_column} = %s")
                values.append(value)
        
        if not update_fields:
            return {"code": code, "message": "업데이트할 필드가 없습니다"}
        
        query = f"UPDATE courses SET {', '.join(update_fields)} WHERE code = %s"
        values.append(code)
        
        cursor.execute(query, tuple(values))
        conn.commit()
        return {"code": code}
    except Exception as e:
        import traceback
        print(f"과정 업데이트 에러: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"과정 업데이트 실패: {str(e)}")
    finally:
        conn.close()

@app.delete("/api/courses/{code}")
async def delete_course(code: str):
    """과정 삭제 (관련 데이터 cascade) - [WARN] 위험: 시간표, 훈련일지 모두 삭제됨!"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 삭제될 데이터 개수 확인 (경고용)
        cursor.execute("SELECT COUNT(*) as count FROM timetables WHERE course_code = %s", (code,))
        timetable_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM training_logs WHERE course_code = %s", (code,))
        training_log_count = cursor.fetchone()['count']
        
        # students 테이블에 course_id 컬럼이 있는지 확인
        student_count = 0
        try:
            cursor.execute("SELECT COUNT(*) as count FROM students WHERE course_id = %s", (code,))
            student_count = cursor.fetchone()['count']
        except Exception as e:
            print(f"[INFO] students 테이블에 course_id 컬럼이 없음 (정상): {e}")
        
        # 데이터가 많을 경우 경고 로그
        if timetable_count > 0 or training_log_count > 0 or student_count > 0:
            print(f"[WARN] 과정 삭제: {code} - 시간표 {timetable_count}건, 훈련일지 {training_log_count}건, 학생 {student_count}명 함께 삭제됨!")
        
        # 1. 학생 가입 신청 삭제
        cursor.execute("DELETE FROM student_registrations WHERE course_code = %s", (code,))
        
        # 2. 시간표 삭제
        cursor.execute("DELETE FROM timetables WHERE course_code = %s", (code,))
        
        # 3. 훈련일지 삭제
        cursor.execute("DELETE FROM training_logs WHERE course_code = %s", (code,))
        
        # 4. 수업노트 삭제 (과정별 수업노트가 있을 경우)
        try:
            cursor.execute("DELETE FROM class_notes WHERE course_code = %s", (code,))
            print(f"[INFO] class_notes에서 과정 {code} 관련 데이터 삭제")
        except Exception as e:
            print(f"[INFO] class_notes 테이블에 course_code 컬럼이 없음 (정상, 스킵): {e}")
        
        # 5. 과정-교과목 연결 삭제
        cursor.execute("DELETE FROM course_subjects WHERE course_code = %s", (code,))
        
        # 6. 학생 데이터 처리 (course_id를 NULL로 설정 - 컬럼이 있는 경우만)
        try:
            cursor.execute("UPDATE students SET course_id = NULL WHERE course_id = %s", (code,))
            print(f"[INFO] 학생 {student_count}명의 course_id를 NULL로 설정")
        except Exception as e:
            print(f"[INFO] students 테이블에 course_id 컬럼이 없음 (정상, 스킵): {e}")
        
        # 7. 과정 삭제
        cursor.execute("DELETE FROM courses WHERE code = %s", (code,))
        
        conn.commit()
        return {
            "message": "과정 및 관련 데이터가 삭제되었습니다",
            "deleted": {
                "timetables": timetable_count,
                "training_logs": training_log_count,
                "students_affected": student_count
            }
        }
    except Exception as e:
        conn.rollback()
        import traceback
        print(f"과정 삭제 오류: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"과정 삭제 실패: {str(e)}")
    finally:
        conn.close()

# ==================== 프로젝트 관리 API ====================

@app.get("/api/projects")
async def get_projects(course_code: Optional[str] = None):
    """팀 목록 조회 (과정별 필터)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Check if new columns exist, if not, add them
        try:
            cursor.execute("SHOW COLUMNS FROM projects LIKE 'group_type'")
            if not cursor.fetchone():
                # Add new columns
                cursor.execute("ALTER TABLE projects ADD COLUMN group_type VARCHAR(50)")
                cursor.execute("ALTER TABLE projects ADD COLUMN instructor_code VARCHAR(50)")
                cursor.execute("ALTER TABLE projects ADD COLUMN mentor_code VARCHAR(50)")
                conn.commit()
        except:
            pass  # Columns might already exist
        
        # Check if account columns exist, if not, add them
        try:
            cursor.execute("SHOW COLUMNS FROM projects LIKE 'account1_name'")
            if not cursor.fetchone():
                # Add shared account columns (5 sets of 3 fields = 15 columns)
                for i in range(1, 6):
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN account{i}_name VARCHAR(100)")
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN account{i}_id VARCHAR(100)")
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN account{i}_pw VARCHAR(100)")
                conn.commit()
        except:
            pass  # Columns might already exist
        
        # Check if photo_urls column exists, if not, add it
        ensure_photo_urls_column(cursor, 'projects')
        
        query = """
            SELECT p.*, 
                   c.name as course_name,
                   i1.name as instructor_name,
                   i2.name as mentor_name
            FROM projects p
            LEFT JOIN courses c ON p.course_code = c.code
            LEFT JOIN instructors i1 ON p.instructor_code = i1.code
            LEFT JOIN instructors i2 ON p.mentor_code = i2.code
            WHERE 1=1
        """
        params = []
        
        if course_code:
            query += " AND p.course_code = %s"
            params.append(course_code)
        
        query += " ORDER BY p.code"
        
        cursor.execute(query, params)
        projects = cursor.fetchall()
        return [convert_datetime(proj) for proj in projects]
    finally:
        conn.close()

@app.get("/api/projects/{code}")
async def get_project(code: str):
    """특정 팀 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT p.*, 
                   c.name as course_name,
                   i1.name as instructor_name,
                   i2.name as mentor_name
            FROM projects p
            LEFT JOIN courses c ON p.course_code = c.code
            LEFT JOIN instructors i1 ON p.instructor_code = i1.code
            LEFT JOIN instructors i2 ON p.mentor_code = i2.code
            WHERE p.code = %s
        """, (code,))
        project = cursor.fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다")
        return convert_datetime(project)
    finally:
        conn.close()

@app.post("/api/projects")
async def create_project(data: dict):
    """팀 생성 (5명의 팀원 정보)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if new columns exist, if not, add them
        try:
            cursor.execute("SHOW COLUMNS FROM projects LIKE 'member1_code'")
            if not cursor.fetchone():
                # Add new columns
                for i in range(1, 6):
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN member{i}_code VARCHAR(50)")
                cursor.execute("ALTER TABLE projects ADD COLUMN group_type VARCHAR(50)")
                cursor.execute("ALTER TABLE projects ADD COLUMN instructor_code VARCHAR(50)")
                cursor.execute("ALTER TABLE projects ADD COLUMN mentor_code VARCHAR(50)")
                conn.commit()
        except:
            pass  # Columns might already exist
        
        # Check if account columns exist, if not, add them
        try:
            cursor.execute("SHOW COLUMNS FROM projects LIKE 'account1_name'")
            if not cursor.fetchone():
                # Add shared account columns (5 sets of 3 fields = 15 columns)
                for i in range(1, 6):
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN account{i}_name VARCHAR(100)")
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN account{i}_id VARCHAR(100)")
                    cursor.execute(f"ALTER TABLE projects ADD COLUMN account{i}_pw VARCHAR(100)")
                conn.commit()
        except:
            pass  # Columns might already exist
        
        # Ensure photo_urls column exists
        ensure_photo_urls_column(cursor, 'projects')
        
        # Ensure description column exists (TEXT type for markdown support)
        try:
            cursor.execute("SHOW COLUMNS FROM projects LIKE 'description'")
            result = cursor.fetchone()
            if not result:
                print("[INFO] Adding description column to projects table...")
                cursor.execute("ALTER TABLE projects ADD COLUMN description TEXT")
                conn.commit()
                print("[OK] Description column added successfully")
        except Exception as e:
            print(f"[WARN] Description column check failed: {e}")
            # Column might already exist, continue anyway
            pass
        
        query = """
            INSERT INTO projects (code, name, description, group_type, course_code, instructor_code, mentor_code,
                                 member1_name, member1_phone, member1_code,
                                 member2_name, member2_phone, member2_code,
                                 member3_name, member3_phone, member3_code,
                                 member4_name, member4_phone, member4_code,
                                 member5_name, member5_phone, member5_code,
                                 member6_name, member6_phone, member6_code,
                                 account1_name, account1_id, account1_pw,
                                 account2_name, account2_id, account2_pw,
                                 account3_name, account3_id, account3_pw,
                                 account4_name, account4_id, account4_pw,
                                 account5_name, account5_id, account5_pw,
                                 photo_urls)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['code'], data['name'], data.get('description'), data.get('group_type'), data.get('course_code'),
            data.get('instructor_code'), data.get('mentor_code'),
            data.get('member1_name'), data.get('member1_phone'), data.get('member1_code'),
            data.get('member2_name'), data.get('member2_phone'), data.get('member2_code'),
            data.get('member3_name'), data.get('member3_phone'), data.get('member3_code'),
            data.get('member4_name'), data.get('member4_phone'), data.get('member4_code'),
            data.get('member5_name'), data.get('member5_phone'), data.get('member5_code'),
            data.get('member6_name'), data.get('member6_phone'), data.get('member6_code'),
            data.get('account1_name'), data.get('account1_id'), data.get('account1_pw'),
            data.get('account2_name'), data.get('account2_id'), data.get('account2_pw'),
            data.get('account3_name'), data.get('account3_id'), data.get('account3_pw'),
            data.get('account4_name'), data.get('account4_id'), data.get('account4_pw'),
            data.get('account5_name'), data.get('account5_id'), data.get('account5_pw'),
            data.get('photo_urls', '[]')
        ))
        conn.commit()
        return {"code": data['code']}
    finally:
        conn.close()

@app.put("/api/projects/{code}")
async def update_project(code: str, data: dict):
    """팀 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Ensure photo_urls column exists
        ensure_photo_urls_column(cursor, 'projects')
        
        # Ensure description column exists (TEXT type for markdown support)
        try:
            cursor.execute("SHOW COLUMNS FROM projects LIKE 'description'")
            result = cursor.fetchone()
            if not result:
                print("[INFO] Adding description column to projects table...")
                cursor.execute("ALTER TABLE projects ADD COLUMN description TEXT")
                conn.commit()
                print("[OK] Description column added successfully")
        except Exception as e:
            print(f"[WARN] Description column check failed: {e}")
            # Column might already exist, continue anyway
            pass
        
        query = """
            UPDATE projects
            SET name = %s, description = %s, group_type = %s, course_code = %s, 
                instructor_code = %s, mentor_code = %s,
                member1_name = %s, member1_phone = %s, member1_code = %s,
                member2_name = %s, member2_phone = %s, member2_code = %s,
                member3_name = %s, member3_phone = %s, member3_code = %s,
                member4_name = %s, member4_phone = %s, member4_code = %s,
                member5_name = %s, member5_phone = %s, member5_code = %s,
                member6_name = %s, member6_phone = %s, member6_code = %s,
                account1_name = %s, account1_id = %s, account1_pw = %s,
                account2_name = %s, account2_id = %s, account2_pw = %s,
                account3_name = %s, account3_id = %s, account3_pw = %s,
                account4_name = %s, account4_id = %s, account4_pw = %s,
                account5_name = %s, account5_id = %s, account5_pw = %s,
                photo_urls = %s
            WHERE code = %s
        """
        cursor.execute(query, (
            data['name'], data.get('description'), data.get('group_type'), data.get('course_code'),
            data.get('instructor_code'), data.get('mentor_code'),
            data.get('member1_name'), data.get('member1_phone'), data.get('member1_code'),
            data.get('member2_name'), data.get('member2_phone'), data.get('member2_code'),
            data.get('member3_name'), data.get('member3_phone'), data.get('member3_code'),
            data.get('member4_name'), data.get('member4_phone'), data.get('member4_code'),
            data.get('member5_name'), data.get('member5_phone'), data.get('member5_code'),
            data.get('member6_name'), data.get('member6_phone'), data.get('member6_code'),
            data.get('account1_name'), data.get('account1_id'), data.get('account1_pw'),
            data.get('account2_name'), data.get('account2_id'), data.get('account2_pw'),
            data.get('account3_name'), data.get('account3_id'), data.get('account3_pw'),
            data.get('account4_name'), data.get('account4_id'), data.get('account4_pw'),
            data.get('account5_name'), data.get('account5_id'), data.get('account5_pw'),
            data.get('photo_urls', '[]'),
            code
        ))
        conn.commit()
        return {"code": code}
    finally:
        conn.close()

@app.delete("/api/projects/{code}")
async def delete_project(code: str):
    """팀 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE code = %s", (code,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="팀을 찾을 수 없습니다")
        conn.commit()
        return {"message": "팀이 삭제되었습니다"}
    finally:
        conn.close()

# ==================== 수업관리(시간표) API ====================

@app.get("/api/timetables")
async def get_timetables(
    course_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """시간표 목록 조회 (과정/기간별 필터)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
            SELECT t.*, 
                   c.name as course_name, c.start_date as course_start_date,
                   s.name as subject_name,
                   i.name as instructor_name,
                   tl.id as training_log_id,
                   tl.content as training_content,
                   tl.photo_urls as training_log_photo_urls
            FROM timetables t
            LEFT JOIN courses c ON t.course_code = c.code
            LEFT JOIN subjects s ON t.subject_code = s.code
            LEFT JOIN instructors i ON t.instructor_code = i.code
            LEFT JOIN training_logs tl ON t.id = tl.timetable_id
            WHERE 1=1
        """
        params = []
        
        if course_code:
            query += " AND t.course_code = %s"
            params.append(course_code)
        
        if start_date:
            query += " AND t.class_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND t.class_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY t.class_date, t.start_time"
        
        cursor.execute(query, params)
        timetables = cursor.fetchall()
        
        # 주차/일차 계산
        for tt in timetables:
            if tt.get('course_start_date') and tt.get('class_date'):
                delta = (tt['class_date'] - tt['course_start_date']).days
                tt['week_number'] = (delta // 7) + 1
                tt['day_number'] = delta + 1
            else:
                tt['week_number'] = None
                tt['day_number'] = None
        return [convert_datetime(tt) for tt in timetables]
    finally:
        conn.close()

@app.get("/api/timetables/{timetable_id}")
async def get_timetable(timetable_id: int):
    """특정 시간표 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT t.*,
                   c.name as course_name,
                   s.name as subject_name,
                   i.name as instructor_name
            FROM timetables t
            LEFT JOIN courses c ON t.course_code = c.code
            LEFT JOIN subjects s ON t.subject_code = s.code
            LEFT JOIN instructors i ON t.instructor_code = i.code
            WHERE t.id = %s
        """, (timetable_id,))
        timetable = cursor.fetchone()
        if not timetable:
            raise HTTPException(status_code=404, detail="시간표를 찾을 수 없습니다")
        return convert_datetime(timetable)
    finally:
        conn.close()

@app.post("/api/timetables")
async def create_timetable(data: dict):
    """시간표 생성"""
    # 디버깅: 받은 데이터 로깅
    print(f"[DEBUG] 시간표 추가 데이터: {data}")
    print(f"[DEBUG] type 값: '{data.get('type')}' (타입: {type(data.get('type'))})")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO timetables (course_code, subject_code, class_date, start_time,
                                   end_time, instructor_code, type, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['course_code'], data.get('subject_code'), data['class_date'],
            data['start_time'], data['end_time'], data.get('instructor_code'),
            data['type'], data.get('notes')
        ))
        conn.commit()
        return {"id": cursor.lastrowid}
    except Exception as e:
        print(f"[ERROR] 시간표 추가 실패: {e}")
        raise
    finally:
        conn.close()

@app.put("/api/timetables/{timetable_id}")
async def update_timetable(timetable_id: int, data: dict):
    """시간표 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE timetables
            SET course_code = %s, subject_code = %s, class_date = %s,
                start_time = %s, end_time = %s, instructor_code = %s,
                type = %s, notes = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            data['course_code'], data.get('subject_code'), data['class_date'],
            data['start_time'], data['end_time'], data.get('instructor_code'),
            data['type'], data.get('notes'), timetable_id
        ))
        conn.commit()
        return {"id": timetable_id}
    except Exception as e:
        conn.rollback()
        print(f"시간표 수정 에러: {str(e)}")
        print(f"데이터: {data}")
        raise HTTPException(status_code=500, detail=f"시간표 수정 실패: {str(e)}")
    finally:
        conn.close()

@app.delete("/api/timetables/{timetable_id}")
async def delete_timetable(timetable_id: int):
    """시간표 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM timetables WHERE id = %s", (timetable_id,))
        conn.commit()
        return {"message": "시간표가 삭제되었습니다"}
    finally:
        conn.close()

# ==================== 상담 관리 API ====================

@app.get("/api/counselings")
async def get_counselings(
    student_id: Optional[int] = None,
    month: Optional[str] = None,
    course_code: Optional[str] = None
):
    """상담 목록 조회 (학생별/월별/학급별 필터)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # photo_urls, career_decision 컬럼 확인 및 추가
        ensure_photo_urls_column(cursor, 'consultations')
        ensure_career_decision_column(cursor)
        
        query = """
            SELECT c.*, s.name as student_name, s.code as student_code, s.course_code,
                   i.name as instructor_name
            FROM consultations c
            LEFT JOIN students s ON c.student_id = s.id
            LEFT JOIN instructors i ON c.instructor_code = i.code
            WHERE 1=1
        """
        params = []
        
        if student_id:
            query += " AND c.student_id = %s"
            params.append(student_id)
        
        if month:  # 형식: "2025-01"
            query += " AND DATE_FORMAT(c.consultation_date, '%%Y-%%m') = %s"
            params.append(month)
        
        if course_code:
            query += " AND s.course_code = %s"
            params.append(course_code)
        
        query += " ORDER BY c.consultation_date DESC"
        
        cursor.execute(query, params)
        counselings = cursor.fetchall()
        
        for counseling in counselings:
            for key, value in counseling.items():
                if isinstance(value, (datetime, date)):
                    counseling[key] = value.isoformat()
        
        return counselings
    finally:
        conn.close()

@app.get("/api/counselings/{counseling_id}")
async def get_counseling(counseling_id: int):
    """특정 상담 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT c.*, s.name as student_name, s.code as student_code,
                   i.name as instructor_name
            FROM consultations c
            LEFT JOIN students s ON c.student_id = s.id
            LEFT JOIN instructors i ON c.instructor_code = i.code
            WHERE c.id = %s
        """, (counseling_id,))
        counseling = cursor.fetchone()
        
        if not counseling:
            raise HTTPException(status_code=404, detail="상담 기록을 찾을 수 없습니다")
        
        for key, value in counseling.items():
            if isinstance(value, (datetime, date)):
                counseling[key] = value.isoformat()
        
        return counseling
    finally:
        conn.close()

@app.post("/api/counselings")
async def create_counseling(data: dict):
    """상담 생성"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # photo_urls, career_decision 컬럼 확인 및 추가
        ensure_photo_urls_column(cursor, 'consultations')
        ensure_career_decision_column(cursor)
        
        # consultations 테이블 구조에 맞게 조정
        query = """
            INSERT INTO consultations 
            (student_id, instructor_code, consultation_date, consultation_type, main_topic, content, status, photo_urls, career_decision)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # instructor_code가 빈 문자열이면 None으로 처리
        instructor_code = data.get('instructor_code')
        if instructor_code == '':
            instructor_code = None
        
        cursor.execute(query, (
            data.get('student_id'),
            instructor_code,
            data.get('consultation_date') or data.get('counseling_date'),
            data.get('consultation_type', '정기'),
            data.get('main_topic') or data.get('topic', ''),
            data.get('content'),
            data.get('status', '완료'),
            data.get('photo_urls'),
            data.get('career_decision')
        ))
        
        conn.commit()
        return {"id": cursor.lastrowid}
    except pymysql.err.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    except pymysql.err.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"데이터 무결성 오류: {str(e)}")
    finally:
        conn.close()

@app.put("/api/counselings/{counseling_id}")
async def update_counseling(counseling_id: int, data: dict):
    """상담 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # photo_urls, career_decision 컬럼 확인 및 추가
        ensure_photo_urls_column(cursor, 'consultations')
        ensure_career_decision_column(cursor)
        
        query = """
            UPDATE consultations 
            SET student_id = %s, instructor_code = %s, consultation_date = %s, consultation_type = %s,
                main_topic = %s, content = %s, status = %s, photo_urls = %s, career_decision = %s
            WHERE id = %s
        """
        
        # instructor_code가 빈 문자열이면 None으로 처리
        instructor_code = data.get('instructor_code')
        if instructor_code == '':
            instructor_code = None
        
        cursor.execute(query, (
            data.get('student_id'),
            instructor_code,
            data.get('consultation_date') or data.get('counseling_date'),
            data.get('consultation_type', '정기'),
            data.get('main_topic') or data.get('topic', ''),
            data.get('content'),
            data.get('status', '완료'),
            data.get('photo_urls'),
            data.get('career_decision'),
            counseling_id
        ))
        
        conn.commit()
        return {"id": counseling_id}
    finally:
        conn.close()

@app.delete("/api/counselings/{counseling_id}")
async def delete_counseling(counseling_id: int):
    """상담 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consultations WHERE id = %s", (counseling_id,))
        conn.commit()
        return {"message": "상담 기록이 삭제되었습니다"}
    finally:
        conn.close()

# ==================== 훈련일지 관리 API ====================

@app.get("/api/training-logs")
async def get_training_logs(
    course_code: Optional[str] = None,
    instructor_code: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    timetable_id: Optional[int] = None
):
    """훈련일지 목록 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # training_logs 테이블이 없으면 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timetable_id INT NOT NULL,
                course_code VARCHAR(50),
                instructor_code VARCHAR(50),
                class_date DATE,
                content TEXT,
                homework TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (timetable_id) REFERENCES timetables(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        
        query = """
            SELECT tl.*, 
                   t.class_date, t.start_time, t.end_time, t.type,
                   s.name as subject_name,
                   i.name as instructor_name,
                   c.name as course_name
            FROM training_logs tl
            LEFT JOIN timetables t ON tl.timetable_id = t.id
            LEFT JOIN subjects s ON t.subject_code = s.code
            LEFT JOIN instructors i ON t.instructor_code = i.code
            LEFT JOIN courses c ON t.course_code = c.code
            WHERE 1=1
        """
        
        params = []
        
        if timetable_id:
            query += " AND tl.timetable_id = %s"
            params.append(timetable_id)
        
        if course_code:
            query += " AND t.course_code = %s"
            params.append(course_code)
        
        if instructor_code:
            query += " AND t.instructor_code = %s"
            params.append(instructor_code)
        
        if year and month:
            query += " AND YEAR(t.class_date) = %s AND MONTH(t.class_date) = %s"
            params.extend([year, month])
        elif year:
            query += " AND YEAR(t.class_date) = %s"
            params.append(year)
        
        query += " ORDER BY t.class_date, t.start_time"
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        for log in logs:
            for key, value in log.items():
                if isinstance(value, (datetime, date)):
                    log[key] = value.isoformat()
        
        return logs
    finally:
        conn.close()

@app.get("/api/training-logs/{log_id}")
async def get_training_log(log_id: int):
    """특정 훈련일지 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT tl.*, 
                   t.class_date, t.start_time, t.end_time, t.type,
                   s.name as subject_name,
                   i.name as instructor_name,
                   c.name as course_name
            FROM training_logs tl
            LEFT JOIN timetables t ON tl.timetable_id = t.id
            LEFT JOIN subjects s ON t.subject_code = s.code
            LEFT JOIN instructors i ON t.instructor_code = i.code
            LEFT JOIN courses c ON t.course_code = c.code
            WHERE tl.id = %s
        """, (log_id,))
        log = cursor.fetchone()
        
        if not log:
            raise HTTPException(status_code=404, detail="훈련일지를 찾을 수 없습니다")
        
        for key, value in log.items():
            if isinstance(value, (datetime, date)):
                log[key] = value.isoformat()
        
        return log
    finally:
        conn.close()

@app.post("/api/training-logs")
async def create_training_log(data: dict):
    """훈련일지 생성"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # photo_urls 컬럼이 없으면 자동 생성
        ensure_photo_urls_column(cursor, 'training_logs')
        
        query = """
            INSERT INTO training_logs 
            (timetable_id, course_code, instructor_code, class_date, content, homework, notes, photo_urls)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            data.get('timetable_id'),
            data.get('course_code'),
            data.get('instructor_code'),
            data.get('class_date'),
            data.get('content', ''),
            data.get('homework', ''),
            data.get('notes', ''),
            data.get('photo_urls')
        ))
        
        conn.commit()
        return {"id": cursor.lastrowid}
    except pymysql.err.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(e)}")
    finally:
        conn.close()

@app.put("/api/training-logs/{log_id}")
async def update_training_log(log_id: int, data: dict):
    """훈련일지 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # photo_urls 컬럼이 없으면 자동 생성
        ensure_photo_urls_column(cursor, 'training_logs')
        
        query = """
            UPDATE training_logs 
            SET content = %s, homework = %s, notes = %s, photo_urls = %s
            WHERE id = %s
        """
        
        cursor.execute(query, (
            data.get('content', ''),
            data.get('homework', ''),
            data.get('notes', ''),
            data.get('photo_urls'),
            log_id
        ))
        
        conn.commit()
        return {"id": log_id}
    finally:
        conn.close()

@app.delete("/api/training-logs/{log_id}")
async def delete_training_log(log_id: int):
    """훈련일지 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM training_logs WHERE id = %s", (log_id,))
        conn.commit()
        return {"message": "훈련일지가 삭제되었습니다"}
    finally:
        conn.close()

@app.post("/api/training-logs/generate-content")
async def generate_training_content(data: dict):
    """AI를 이용한 훈련일지 수업 내용 자동 생성 (사용자 입력 기반 확장)"""
    subject_name = data.get('subject_name', '')
    sub_subjects = data.get('sub_subjects', [])  # 세부 교과목 리스트
    class_date = data.get('class_date', '')
    instructor_name = data.get('instructor_name', '')
    user_input = data.get('user_input', '').strip()  # 사용자가 입력한 내용
    detail_level = data.get('detail_level', 'normal')  # 'summary', 'normal', 'detailed'
    timetable_type = data.get('timetable_type', 'lecture')  # 'lecture', 'project', 'practice'
    
    if not user_input:
        raise HTTPException(status_code=400, detail="수업 내용을 먼저 입력해주세요 (최소 몇 단어라도)")
    
    # Groq API 키 확인
    groq_api_key = os.getenv('GROQ_API_KEY', '')
    
    # 세부 교과목 텍스트 포맷팅
    sub_subjects_text = ""
    if sub_subjects:
        for sub in sub_subjects:
            sub_subjects_text += f"- {sub.get('name', '')} ({sub.get('hours', 0)}시간)\n"
    
    # 상세도에 따른 지시사항
    detail_instructions = {
        'summary': '간결하고 핵심적인 내용으로 200-300자 정도로 작성해주세요.',
        'normal': '적절한 상세도로 400-600자 정도로 작성해주세요.',
        'detailed': '매우 상세하고 구체적으로 800-1200자 정도로 작성해주세요. 예제, 실습 내용, 학생 반응 등을 포함하세요.'
    }
    
    # 타입별 시스템 프롬프트
    if timetable_type == 'project':
        system_prompt = """당신은 IT 프로젝트 과정의 전문 지도 강사입니다.
강사가 입력한 간단한 메모나 키워드를 바탕으로, 실제 프로젝트 진행 내용을 전문적인 훈련일지 형식으로 확장하여 작성해주세요.

**중요 규칙**:
1. 강사가 입력한 원본 내용은 반드시 그대로 포함
2. 원본 텍스트를 절대 삭제하거나 변경하지 말 것
3. **개조식(bullet point) 형식으로 작성** - 완전한 문장이 아닌 간결한 구문 사용
4. "~했습니다", "~입니다" 등의 서술형 대신 "~함", "~진행", "~학습" 등의 체언 종결 사용
5. 프로젝트 진행 상황, 문제 해결, 팀 협업에 초점"""

        user_prompt_template = """
다음은 강사가 입력한 오늘 프로젝트 활동 메모입니다:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【강사가 입력한 원본 내용】
{user_input}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【프로젝트 정보】
- 날짜: {class_date}
- 활동: 프로젝트
- 지도강사: {instructor_name}

위의 원본 내용을 **반드시 그대로 유지하면서** 프로젝트 훈련일지 형식으로 확장해주세요:

[OK] 필수 요구사항:
1. 강사가 입력한 원본 내용("{user_input}")을 반드시 포함
2. 원본 내용을 중심으로 프로젝트 목표, 진행 상황, 팀 활동 추가
3. 원본 키워드나 문장을 삭제하거나 변경 금지
4. **개조식(bullet point) 형식으로 작성**

📝 작성 형식 (개조식):
- 프로젝트 주제: [원본 내용 포함]
- 금일 목표:
  • 목표1
  • 목표2
- 주요 진행 내용:
  • 내용1 (원본 키워드 활용)
  • 내용2
  • 내용3
- 팀별 활동:
  • 활동1
  • 활동2
- 문제 해결 및 개선사항:
  • 이슈1 및 해결방법
  • 이슈2 및 해결방법
- 진행률 및 성과:
  • 달성사항1
  • 달성사항2

{detail_instructions}

**다시 한번 강조**: 
1. "{user_input}" 이 내용은 반드시 결과물에 포함
2. 개조식으로 작성 (서술형 금지)
"""
    
    elif timetable_type == 'practice':
        system_prompt = """당신은 IT 현장실습 과정의 전문 지도 강사입니다.
강사가 입력한 간단한 메모나 키워드를 바탕으로, 실제 현장실습 진행 내용을 전문적인 훈련일지 형식으로 확장하여 작성해주세요.

**중요 규칙**:
1. 강사가 입력한 원본 내용은 반드시 그대로 포함
2. 원본 텍스트를 절대 삭제하거나 변경하지 말 것
3. **개조식(bullet point) 형식으로 작성** - 완전한 문장이 아닌 간결한 구문 사용
4. "~했습니다", "~입니다" 등의 서술형 대신 "~함", "~진행", "~학습" 등의 체언 종결 사용
5. 현장 업무, 실무 경험, 기업 멘토링에 초점"""

        user_prompt_template = """
다음은 강사가 입력한 오늘 현장실습 활동 메모입니다:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【강사가 입력한 원본 내용】
{user_input}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【현장실습 정보】
- 날짜: {class_date}
- 활동: 현장실습
- 지도강사: {instructor_name}

위의 원본 내용을 **반드시 그대로 유지하면서** 현장실습 훈련일지 형식으로 확장해주세요:

[OK] 필수 요구사항:
1. 강사가 입력한 원본 내용("{user_input}")을 반드시 포함
2. 원본 내용을 중심으로 실습 목표, 현장 업무, 멘토링 내용 추가
3. 원본 키워드나 문장을 삭제하거나 변경 금지
4. **개조식(bullet point) 형식으로 작성**

📝 작성 형식 (개조식):
- 실습 업무: [원본 내용 포함]
- 금일 목표:
  • 목표1
  • 목표2
- 주요 실습 내용:
  • 내용1 (원본 키워드 활용)
  • 내용2
  • 내용3
- 현장 업무 수행:
  • 업무1
  • 업무2
- 멘토링 및 피드백:
  • 피드백1
  • 피드백2
- 학습 성과 및 역량:
  • 성과1
  • 성과2

{detail_instructions}

**다시 한번 강조**: 
1. "{user_input}" 이 내용은 반드시 결과물에 포함
2. 개조식으로 작성 (서술형 금지)
"""
    
    else:  # lecture (기존 교과목)
        system_prompt = """당신은 IT 훈련 과정의 전문 강사입니다.
강사가 입력한 간단한 메모나 키워드를 바탕으로, 실제 수업에서 진행한 내용을 전문적인 훈련일지 형식으로 확장하여 작성해주세요.

**중요 규칙**:
1. 강사가 입력한 원본 내용은 반드시 그대로 포함
2. 원본 텍스트를 절대 삭제하거나 변경하지 말 것
3. **개조식(bullet point) 형식으로 작성** - 완전한 문장이 아닌 간결한 구문 사용
4. "~했습니다", "~입니다" 등의 서술형 대신 "~함", "~진행", "~학습" 등의 체언 종결 사용"""

        user_prompt_template = """
다음은 강사가 입력한 오늘 수업의 메모입니다:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【강사가 입력한 원본 내용】
{user_input}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【수업 정보】
- 날짜: {class_date}
- 과목: {subject_name}
- 강사: {instructor_name}
- 세부 교과목: 
{sub_subjects_text}

위의 원본 내용을 **반드시 그대로 유지하면서** 훈련일지 형식으로 확장해주세요:

[OK] 필수 요구사항:
1. 강사가 입력한 원본 내용("{user_input}")을 반드시 포함
2. 원본 내용을 중심으로 학습 목표, 진행 내용, 실습 활동 추가
3. 원본 키워드나 문장을 삭제하거나 변경 금지
4. **개조식(bullet point) 형식으로 작성** - 서술형 문장 대신 간결한 구문 사용

📝 작성 형식 (개조식):
- 수업 주제: [원본 내용 포함]
- 학습 목표:
  • 목표1
  • 목표2
- 주요 학습 내용:
  • 내용1 (원본 키워드 활용)
  • 내용2
  • 내용3
- 실습/프로젝트:
  • 실습1
  • 실습2
- 학습 성과:
  • 성과1
  • 성과2

📏 작성 스타일:
- [ERROR] 나쁜 예: "오늘 수업에서는 HTML을 학습했습니다." (서술형)
- [OK] 좋은 예: "HTML 기본 문법 학습 및 실습 진행" (개조식)
- [ERROR] 나쁜 예: "학생들은 CSS를 이해하고 활용할 수 있게 되었습니다."
- [OK] 좋은 예: "CSS 선택자, 속성 이해 및 레이아웃 실습 완료"

{detail_instructions}

**다시 한번 강조**: 
1. "{user_input}" 이 내용은 반드시 결과물에 포함
2. 개조식으로 작성 (서술형 금지)
"""
    
    # 프롬프트 변수 대입
    user_prompt = user_prompt_template.format(
        user_input=user_input,
        class_date=class_date,
        subject_name=subject_name,
        instructor_name=instructor_name,
        sub_subjects_text=sub_subjects_text if sub_subjects_text else '세부 교과목 정보 없음',
        detail_instructions=detail_instructions.get(detail_level, detail_instructions['normal'])
    )
    
    try:
        if groq_api_key:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",  # 업데이트된 모델로 변경
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Groq API 오류: {response.text}")
            
            content = response.json()['choices'][0]['message']['content']
        else:
            # API 키가 없으면 템플릿 기반 생성 (타입별 템플릿)
            if timetable_type == 'project':
                # 프로젝트 템플릿
                detail_templates = {
                    'summary': f"""• 프로젝트 주제: {user_input}
• 금일 핵심 진행사항 및 완료된 작업
• 팀 협업 및 문제 해결 진행""",
                    
                    'normal': f"""【프로젝트 주제】
• {user_input}

【금일 목표】
• {user_input} 관련 주요 기능 구현
• 팀원 간 역할 분담 및 협업 진행
• 프로젝트 일정 대비 진행 상황 점검

【주요 진행 내용】
• {user_input} 핵심 기능 개발
• 데이터 구조 설계 및 구현
• UI/UX 개선 작업
• 코드 리뷰 및 품질 개선

【팀별 활동】
• 역할별 작업 진행 상황 공유
• 통합 작업 및 충돌 해결
• 상호 코드 리뷰 및 피드백

【문제 해결 및 개선사항】
• 발생한 기술적 이슈 해결
• 일정 지연 요인 파악 및 대응
• 효율적 개발 방법론 적용

【프로젝트 목표 달성도】
• 계획 대비 진행률: 약 65% (중반 단계)
• 주요 기능 구현 완료율: 70%
• 팀 협업 효율성: 우수""",
                    
                    'detailed': f"""【프로젝트 개요】
• 프로젝트 주제: {user_input}
• 진행 방식: 애자일 방법론, 스프린트 단위 개발
• 금일 목표: 핵심 기능 구현 및 통합 테스트

【금일 목표】
1. {user_input} 관련 주요 모듈 완성
2. 팀원 간 작업 통합 및 충돌 해결
3. 프로젝트 중간 점검 및 일정 조정
4. 품질 개선 및 리팩토링 진행

【주요 진행 내용】
• 개발 작업
  - {user_input} 핵심 로직 구현
  - 데이터베이스 스키마 설계 및 적용
  - API 엔드포인트 개발
  - 프론트엔드 컴포넌트 제작

• 통합 작업
  - Git 브랜치 병합 및 충돌 해결
  - 통합 테스트 수행
  - 버그 수정 및 코드 최적화
  - 문서화 작업 진행

【팀별 활동 상세】
• 프론트엔드 팀
  - UI 컴포넌트 구현 완료
  - 반응형 디자인 적용
  - 사용자 경험 개선

• 백엔드 팀
  - API 서버 기능 구현
  - 데이터베이스 연동 완료
  - 보안 및 인증 처리

• 기획/디자인 팀
  - 와이어프레임 최종 확정
  - 디자인 가이드 작성
  - 사용자 시나리오 테스트

【문제 해결 및 개선사항】
• 기술적 이슈
  - {user_input} 관련 버그 3건 해결
  - 성능 최적화 2건 적용
  - 보안 취약점 1건 수정

• 협업 개선
  - 코드 리뷰 프로세스 개선
  - 커뮤니케이션 도구 활용 강화
  - 일정 관리 방법 최적화

【프로젝트 목표 달성도】
• 전체 진행률: 약 65% (전체 기간 대비 중반 단계)
• 금일 목표 달성률: 85%
• 핵심 기능 완성도: 70%
• 팀 협업 효율: 매우 우수
• 일정 준수율: 양호

【향후 계획】
• 다음 스프린트: {user_input} 고도화 및 테스트
• 남은 기간: 프로젝트 완성 및 발표 준비
• 최종 배포 및 유지보수 계획 수립"""
                }
            
            elif timetable_type == 'practice':
                # 현장실습 템플릿
                detail_templates = {
                    'summary': f"""• 실습 업무: {user_input}
• 현장 실무 경험 및 멘토링 수행
• 실무 역량 강화 및 피드백 적용""",
                    
                    'normal': f"""【실습 업무】
• {user_input}

【금일 목표】
• {user_input} 관련 실무 업무 수행
• 기업 멘토 지도 하에 현장 실습 진행
• 실무 프로세스 이해 및 적용

【주요 실습 내용】
• {user_input} 현장 업무 직접 수행
• 실무 도구 및 시스템 활용 학습
• 업무 프로세스 및 워크플로우 습득
• 팀 협업 및 커뮤니케이션 실습

【현장 업무 수행】
• 실제 프로젝트 참여 및 기여
• 업무 요구사항 분석 및 구현
• 품질 관리 및 테스트 수행
• 문서 작성 및 보고서 제출

【멘토링 및 피드백】
• 기업 멘토의 실무 지도 및 조언
• 작업 결과물에 대한 구체적 피드백
• 개선 방향 및 학습 가이드 제공
• 진로 상담 및 커리어 조언

【학습 성과 및 역량】
• {user_input}에 대한 실무 경험 축적
• 현장 업무 수행 능력 향상
• 협업 및 문제 해결 역량 강화
• 직무 역량 및 전문성 성장""",
                    
                    'detailed': f"""【실습 개요】
• 실습 업무: {user_input}
• 실습 기업: 현장 파트너 기업
• 실습 방식: 멘토 1:1 지도 + 팀 협업
• 금일 목표: 실무 프로젝트 참여 및 핵심 업무 수행

【금일 목표】
1. {user_input} 관련 실무 작업 완수
2. 기업 멘토 피드백 반영 및 개선
3. 현장 프로세스 및 도구 활용 숙달
4. 팀 협업 및 커뮤니케이션 강화

【주요 실습 내용】
• 실무 작업
  - {user_input} 관련 과제 수행
  - 실제 비즈니스 요구사항 분석
  - 현장 도구 및 시스템 활용
  - 품질 기준에 맞는 결과물 산출

• 프로세스 학습
  - 업무 워크플로우 이해 및 적용
  - 협업 도구 활용 (Jira, Slack 등)
  - 코드 리뷰 및 배포 프로세스 경험
  - 애자일/스크럼 방법론 실습

【현장 업무 수행 상세】
• 개발 작업
  - {user_input} 기능 개발 및 테스트
  - 레거시 코드 유지보수
  - 버그 수정 및 성능 개선
  - 기술 문서 작성

• 협업 활동
  - 팀 미팅 참석 및 의견 제시
  - 타 부서와의 커뮤니케이션
  - 일정 관리 및 진행 상황 보고
  - 동료 실습생과의 지식 공유

【멘토링 및 피드백】
• 멘토 지도 내용
  - {user_input} 실무 노하우 전수
  - 코드 리뷰 및 개선 방향 제시
  - 산업 트렌드 및 기술 동향 안내
  - 커리어 발전 방향 상담

• 받은 피드백
  - 작업 속도 및 품질: 우수
  - 기술 이해도: 빠른 학습 능력
  - 협업 태도: 적극적 참여
  - 개선 필요사항: 시간 관리 기술

【학습 성과 및 역량】
• 기술 역량
  - {user_input} 실무 활용 능력 향상
  - 현장 도구 숙련도 증가
  - 문제 해결 능력 강화
  - 코드 품질 의식 함양

• 소프트 스킬
  - 팀 협업 및 커뮤니케이션 능력
  - 업무 책임감 및 자기 관리
  - 비즈니스 이해도 향상
  - 전문가 마인드셋 형성

【진로 및 취업 준비】
• 현장 경험을 통한 직무 적합성 확인
• 포트폴리오 강화 소재 확보
• 기업 인사 담당자와의 네트워킹
• 취업 역량 및 경쟁력 제고"""
                }
            
            else:  # lecture
                # 교과목 템플릿 (기존 유지)
                detail_templates = {
                    'summary': f"""• 수업 주제: {user_input}
• 핵심 개념 학습 및 기본 실습 완료
• 주요 기술 이해도 향상""",
                    
                    'normal': f"""【수업 주제】
• {user_input}

【학습 목표】
• {user_input}의 핵심 개념 이해
• 실무 활용 방법 습득
• 관련 기술 실습 능력 향상

【주요 학습 내용】
• {user_input} 이론 강의 진행
• 기본 원리 및 핵심 개념 설명
• 실제 활용 사례 분석
• 단계별 실습 프로젝트 수행

【실습 활동】
• {user_input} 기반 프로젝트 실습
• 개별/팀별 과제 수행
• 문제 해결 및 피드백

【학습 성과】
• {user_input}에 대한 이해도 향상
• 실무 적용 능력 강화
• 과제 완료율 우수""",
                    
                    'detailed': f"""【수업 개요】
• 수업 주제: {user_input}
• 진행 방식: 이론 강의 + 실습 병행
• 학습 목표: 핵심 개념 이해 및 실무 활용 능력 배양

【학습 목표】
1. {user_input}의 기본 개념 및 원리 완전 이해
2. 실무 환경에서의 효과적 활용 방법 습득
3. 관련 도구 및 기술 숙련도 향상
4. 문제 해결 및 응용 능력 강화

【주요 학습 내용】
• 이론 학습
  - {user_input}의 배경 및 필요성
  - 핵심 개념 및 용어 정리
  - 기본 원리 및 작동 방식 설명
  - 실제 산업 현장 활용 사례 분석

• 실습 진행
  - 기초 실습: {user_input} 기본 활용법
  - 중급 실습: 실무 시나리오 적용
  - 고급 실습: 복합 프로젝트 구현
  - 오류 디버깅 및 최적화 기법

【실습 활동 상세】
• 개별 실습
  - {user_input} 기본 기능 구현
  - 단계별 과제 수행 및 검토
  - 개인별 맞춤 피드백 제공

• 팀 프로젝트
  - 협업 도구 활용한 팀 작업
  - 역할 분담 및 일정 관리
  - 최종 결과물 발표 및 상호 평가

【학습 성과 및 피드백】
• 성취 수준
  - {user_input} 개념 이해도: 상
  - 실습 과제 완료율: 90% 이상
  - 팀 프로젝트 수행 능력: 우수

• 학생 반응
  - 적극적 수업 참여도
  - 질의응답 활발히 진행
  - 추가 학습 자료 요청 다수

【향후 학습 계획】
• 다음 차시: {user_input} 심화 과정
• 고급 기능 및 응용 기술 학습 예정
• 실무 프로젝트 완성도 향상 중점"""
                }
            
            content = detail_templates.get(detail_level, detail_templates['normal'])
        
        return {
            "content": content.strip(),
            "subject_name": subject_name,
            "class_date": class_date
        }
    except Exception as e:
        print(f"[ERROR] AI 생성 실패 상세: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 생성 실패: {str(e)}")

# ==================== AI 생기부 작성 API ====================

def generate_report_template(student, counselings, counseling_text, style='formal'):
    """스타일별 생기부 템플릿 생성"""
    name = student['name']
    code = student.get('code', '')
    birth = student.get('birth_date', '')
    interests = student.get('interests', '정보 없음')
    education = student.get('education', '')
    count = len(counselings)
    
    if style == 'formal':
        # 공식적 스타일
        report = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 학생 생활기록부 】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 기본 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 성명: {name} ({code})
• 생년월일: {birth}
• 학력: {education}
• 관심분야: {interests}
• 상담 이력: 총 {count}회

2. 학생 특성 종합 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
본 학생은 {count}회에 걸친 지속적인 상담을 통해 다음과 같은 특성을 보였습니다.

【 학업 태도 및 역량 】
자기주도적 학습 태도를 갖추고 있으며, {interests} 분야에 대한 높은 관심과 열정을 보이고 있습니다.
학습 과정에서 어려움에 직면했을 때에도 포기하지 않고 해결 방안을 모색하는 모습을 보였습니다.

【 성장 과정 및 발전 사항 】
상담 기간 동안 학생은 꾸준한 성장을 보여주었습니다. 초기에 비해 자기 인식 능력이 향상되었으며,
구체적인 목표 설정과 실행 계획 수립 능력이 발전하였습니다.

【 대인관계 및 의사소통 】
상담자와의 소통 과정에서 자신의 생각을 논리적으로 표현하는 능력이 우수하였으며,
타인의 조언을 경청하고 수용하는 긍정적인 태도를 보였습니다.

3. 상담 내역 및 주요 논의 사항
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{counseling_text}

4. 종합 의견 및 향후 지도 방향
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 강점 및 잠재력 】
• 자기주도적 학습 능력 보유
• {interests} 분야에 대한 높은 관심과 동기
• 목표 지향적 사고방식
• 긍정적이고 적극적인 태도

【 개선 및 발전 방향 】
• 체계적인 학습 계획 수립 및 실행
• 시간 관리 능력 강화
• 자신감 향상을 위한 성공 경험 축적
• 지속적인 자기 성찰 및 피드백 수용

【 향후 지도 계획 】
1단계 (1-2개월): 기초 역량 강화 및 학습 습관 확립
2단계 (3-4개월): 심화 학습 및 실전 경험 축적
3단계 (5-6개월): 자기주도 학습 완성 및 목표 달성

5. 교사 종합 소견
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{name} 학생은 충분한 잠재력과 강한 학습 의지를 갖춘 우수한 학생입니다.
상담 과정에서 보여준 진지한 태도와 자기 개선 노력은 매우 인상적이었습니다.
체계적인 지원과 지속적인 격려를 통해 {interests} 분야에서 탁월한 성과를 달성할 수 있을 것으로 
기대되며, 앞으로의 성장과 발전이 매우 기대됩니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
작성일: {datetime.now().strftime('%Y년 %m월 %d일')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    elif style == 'friendly':
        # 친근한 스타일
        report = f"""💙 {name} 학생 생활기록부 💙

안녕하세요! {name} 학생의 한 학기 동안의 성장 이야기를 정리해봤어요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 학생 소개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 이름: {name} ({code})
• 생년월일: {birth}
• 학력: {education}
• 좋아하는 것: {interests}
• 함께한 상담: {count}회

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 {name} 학생은 어떤 학생일까요?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{name} 학생은 {interests}에 대한 열정이 가득한 학생이에요!
{count}번의 상담을 통해 정말 많이 성장하는 모습을 볼 수 있었답니다.

【 멋진 점들 】
✓ 자기주도적으로 학습하는 습관이 있어요
✓ {interests} 분야에 대한 관심이 정말 높아요
✓ 어려운 일이 있어도 포기하지 않고 도전해요
✓ 선생님의 조언을 잘 듣고 실천하려고 노력해요

【 성장하는 모습 】
처음 만났을 때보다 자신감이 많이 생겼어요! 
자신에 대해 더 잘 이해하게 되었고, 구체적인 목표를 세우는 법도 배웠답니다.
무엇보다 꾸준히 노력하는 모습이 정말 멋있었어요. 👍

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[DOC] 함께 나눈 이야기들
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{counseling_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 앞으로의 계획
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 계속 키워나갈 점 】
• 자신감을 더 키워봐요!
• {interests} 실력을 꾸준히 향상시켜요
• 시간 관리를 잘해서 효율적으로 공부해요
• 작은 목표들을 하나씩 달성해나가요

【 함께 노력할 방법 】
1. 우선 기초를 탄탄히 다져요 (1-2개월)
2. 실력을 쌓으면서 자신감을 키워요 (3-4개월)
3. 스스로 잘할 수 있게 되도록 도와드릴게요 (5-6개월)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💝 선생님의 한마디
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{name} 학생, 정말 열심히 노력하는 모습이 멋있어요!
{interests}에 대한 열정과 배우고자 하는 의지가 느껴져서 선생님도 기쁩니다.
앞으로도 지금처럼 꾸준히 노력하다 보면 분명 원하는 목표를 이룰 수 있을 거예요.
언제든지 도움이 필요하면 찾아오세요. 항상 응원하고 있어요! 화이팅! 💪✨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
작성일: {datetime.now().strftime('%Y년 %m월 %d일')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    else:  # detailed
        # 상세 분석 스타일
        report = f"""╔════════════════════════════════════════════════════╗
║          학생 생활기록부 (상세 분석)              ║
╚════════════════════════════════════════════════════╝

1. 기본 정보 및 배경
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 학생 프로필 】
• 성명: {name}
• 학번: {code}
• 생년월일: {birth}
• 최종학력: {education}
• 관심분야: {interests}
• 상담 횟수: {count}회
• 기록 기간: {counselings[0]['consultation_date'] if counselings else '정보없음'} ~ {counselings[-1]['consultation_date'] if counselings else '정보없음'}

2. 학생 특성 심층 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 인지적 특성 】
▪ 자기 인식 수준: 우수
  - 자신의 강점과 약점을 정확하게 파악하고 있음
  - 현실적인 목표 설정 능력 보유
  - 자기 성찰 능력이 발달되어 있음

▪ 학습 접근 방식: 자기주도적
  - 능동적인 학습 태도
  - 문제 해결을 위한 적극적 탐색
  - {interests} 분야에 대한 깊이 있는 관심

▪ 사고 패턴: 논리적이고 체계적
  - 상황을 분석하고 판단하는 능력 우수
  - 구조화된 사고방식
  - 단계적 접근 능력

【 정서적 특성 】
▪ 정서 안정성: 양호
  - 전반적으로 안정적인 정서 상태
  - 스트레스 상황에 대한 적응력 보유
  - 긍정적 마인드셋 유지

▪ 동기 수준: 높음
  - {interests}에 대한 내적 동기 강함
  - 성취 지향적 태도
  - 지속적인 자기 개발 의지

▪ 자신감: 발전 중
  - 기초적 자신감은 보유
  - 성공 경험 축적을 통한 향상 필요
  - 긍정적 자기 이미지 형성 과정

【 사회적 특성 】
▪ 의사소통 능력: 우수
  - 자신의 생각을 명확히 표현
  - 타인의 의견을 경청하는 태도
  - 건설적인 대화 참여

▪ 협력 태도: 긍정적
  - 상담자의 조언을 개방적으로 수용
  - 피드백에 대한 긍정적 반응
  - 지도에 협조적인 자세

3. 상담 내역 상세 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 전체 상담 현황 】
{counseling_text}

【 상담 효과 분석 】
▪ 자기 인식 향상
  - 상담 초기 대비 자기 이해도 증가
  - 강점과 개선점에 대한 명확한 인식

▪ 목표 설정 능력 발전
  - 구체적이고 현실적인 목표 수립
  - 단계별 실행 계획 능력 향상

▪ 문제 해결 능력 개선
  - 어려움에 대한 적극적 대처
  - 다양한 해결 방안 모색 능력

4. 역량 평가 (5단계 척도)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 학업 관련 역량 】
• 자기주도 학습: ★★★★☆ (4/5)
• 문제 해결 능력: ★★★★☆ (4/5)
• 창의적 사고: ★★★☆☆ (3/5)
• 분석적 사고: ★★★★☆ (4/5)

【 개인 역량 】
• 자기 관리: ★★★☆☆ (3/5)
• 시간 관리: ★★★☆☆ (3/5)
• 목표 지향성: ★★★★☆ (4/5)
• 회복탄력성: ★★★★☆ (4/5)

【 사회적 역량 】
• 의사소통: ★★★★★ (5/5)
• 협업 능력: ★★★★☆ (4/5)
• 리더십: ★★★☆☆ (3/5)
• 공감 능력: ★★★★☆ (4/5)

5. SWOT 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 Strengths (강점) 】
✓ 자기주도적 학습 태도
✓ {interests}에 대한 깊은 관심과 열정
✓ 논리적이고 체계적인 사고방식
✓ 우수한 의사소통 능력
✓ 긍정적이고 적극적인 자세

【 Weaknesses (약점) 】
△ 시간 관리 능력 개선 필요
△ 자신감 향상 필요
△ 체계적 학습 전략 수립 필요
△ 실행력 강화 필요

【 Opportunities (기회) 】
◆ {interests} 분야의 성장 가능성
◆ 체계적 지원 시스템 활용
◆ 멘토링 및 코칭 기회
◆ 프로젝트 참여를 통한 실전 경험

【 Threats (위협) 】
⚠ 과도한 목표로 인한 스트레스
⚠ 초기 어려움으로 인한 동기 저하 가능성
⚠ 시간 관리 실패 시 학습 효율 저하

6. 단계별 발전 계획 (상세)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 Phase 1: 기초 확립 단계 (1-2개월) 】
▸ 목표
  - {interests} 기본 개념 및 원리 완전 이해
  - 체계적 학습 습관 형성
  - 기초 실력 다지기

▸ 실행 방법
  - 주간 학습 계획표 작성 및 실행
  - 매일 30분 이상 집중 학습
  - 주 1회 진도 점검 및 피드백
  - 기초 개념 테스트 및 보완

▸ 평가 지표
  - 학습 계획 실행률 80% 이상
  - 기초 개념 이해도 테스트 80점 이상
  - 주간 학습 시간 15시간 이상

【 Phase 2: 실력 향상 단계 (3-4개월) 】
▸ 목표
  - 실전 적용 능력 배양
  - 문제 해결 능력 향상
  - 프로젝트 수행 경험 축적

▸ 실행 방법
  - 미니 프로젝트 수행 (주 1회)
  - 실전 문제 풀이 및 분석
  - 멘토링 세션 참여 (월 2회)
  - 학습 그룹 활동 참여

▸ 평가 지표
  - 프로젝트 완성도 평가
  - 문제 해결 속도 및 정확도
  - 자신감 수준 자체 평가

【 Phase 3: 전문성 심화 단계 (5-6개월) 】
▸ 목표
  - 독립적 학습 능력 완성
  - 심화 지식 및 기술 습득
  - 장기 목표 달성 준비

▸ 실행 방법
  - 자기주도 프로젝트 수행
  - 심화 학습 자료 탐구
  - 포트폴리오 구축
  - 분야별 전문가 네트워킹

▸ 평가 지표
  - 프로젝트 포트폴리오 3개 이상
  - 자기주도 학습률 90% 이상
  - 종합 평가 90점 이상

7. 지원 체계 및 모니터링
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 정기 지원 프로그램 】
▸ 주간 체크인 (매주)
  - 학습 진행 상황 확인
  - 어려움 및 질문 해결
  - 다음 주 계획 수립

▸ 월간 면담 (매월)
  - 월간 성과 리뷰
  - 심층 상담 및 코칭
  - 차월 목표 설정

▸ 분기 평가 (3개월마다)
  - 종합 성과 평가
  - SWOT 재분석
  - 장기 계획 조정

【 맞춤형 지원 서비스 】
▸ 학습 자료 제공
  - 수준별 학습 자료
  - 추천 도서 및 온라인 강의
  - 실습 프로젝트 자료

▸ 멘토링 연결
  - 분야별 전문가 멘토
  - 선배 학습자와의 교류
  - 스터디 그룹 운영

▸ 심리·정서 지원
  - 필요시 심리 상담
  - 동기 부여 세션
  - 스트레스 관리 지도

8. 종합 평가 및 권장사항
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 종합 평가 】
{name} 학생은 {interests} 분야에서 탁월한 잠재력을 보유하고 있습니다.
{count}회의 상담을 통해 확인된 학생의 자기주도적 학습 태도, 논리적 사고력, 
우수한 의사소통 능력은 향후 발전의 강력한 기반이 될 것입니다.

현재 시간 관리와 체계적 학습 전략 수립에서 개선이 필요하나, 
이는 체계적인 지도와 꾸준한 연습을 통해 충분히 향상될 수 있는 영역입니다.

학생이 보여준 높은 학습 동기와 개선 의지를 고려할 때, 
적절한 지원과 체계적인 지도가 제공된다면 목표한 성과를 달성할 수 있을 것으로 
확신합니다.

【 권장사항 】
1. 단계별 목표 달성에 집중
   - 한 번에 모든 것을 이루려 하지 말고 단계별 접근
   - 작은 성공 경험을 축적하여 자신감 향상

2. 체계적인 시간 관리
   - 학습 계획표 작성 및 준수
   - 우선순위에 따른 시간 배분
   - 규칙적인 생활 패턴 유지

3. 지속적인 자기 성찰
   - 일일 학습 일지 작성
   - 주간 회고 및 개선점 도출
   - 정기적인 자기 평가

4. 적극적인 도움 요청
   - 어려움 발생 시 즉시 상담
   - 멘토 및 동료와의 활발한 교류
   - 학습 커뮤니티 적극 활용

5. 균형 잡힌 생활
   - 학습과 휴식의 균형
   - 취미 및 여가 활동 병행
   - 신체적·정신적 건강 관리

【 기대 효과 】
위 계획대로 6개월간 체계적인 학습과 지도가 이루어진다면:
• {interests} 분야 기본 역량 완전 확립
• 자기주도적 학습 능력 완성
• 실전 프로젝트 수행 경험 축적
• 자신감 및 자기효능감 대폭 향상
• 장기적 성장을 위한 탄탄한 기반 마련

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【 교사 최종 의견 】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{name} 학생과의 {count}회 상담을 통해 학생의 우수한 잠재력과 
강한 성장 의지를 확인할 수 있었습니다.

학생이 보여준 진지한 태도, 자기 성찰 능력, 그리고 지속적인 개선 노력은
교사로서 매우 인상 깊었으며, 앞으로의 발전이 매우 기대됩니다.

{interests} 분야에서의 깊은 관심과 열정을 바탕으로,
체계적인 학습과 꾸준한 노력을 통해 반드시 목표를 달성할 수 있을 것으로
확신합니다.

학생의 성공적인 성장을 위해 지속적으로 지원하고 격려하겠습니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

작성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}
작성자: 담당 교사
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return report

@app.post("/api/ai/generate-report")
async def generate_ai_report(data: dict):
    """AI를 이용한 생기부 작성"""
    student_id = data.get('student_id')
    style = data.get('style', 'formal')  # formal, friendly, detailed
    custom_instructions = data.get('custom_instructions', '')
    
    if not student_id:
        raise HTTPException(status_code=400, detail="학생 ID가 필요합니다")
    
    # Groq API 키 확인 (없으면 무료 API 사용)
    groq_api_key = os.getenv('GROQ_API_KEY', '')
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 학생 정보 조회
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
        
        # 상담 내역 조회
        cursor.execute("""
            SELECT consultation_date, consultation_type, main_topic, content
            FROM consultations
            WHERE student_id = %s
            ORDER BY consultation_date
        """, (student_id,))
        counselings = cursor.fetchall()
        
        if not counselings:
            raise HTTPException(status_code=400, detail="상담 기록이 없습니다")
        
        # 상담 내용 포맷팅
        counseling_text = ""
        for c in counselings:
            counseling_text += f"\n[{c['consultation_date']}] {c['consultation_type']} - {c['main_topic']}\n"
            counseling_text += f"내용: {c['content']}\n"
        
        system_prompt = """당신은 학생 생활기록부를 작성하는 전문 교사입니다.
학생의 상담 기록을 바탕으로 학생의 성장과 발달, 특성을 잘 드러내는 생활기록부를 작성해주세요.
생활기록부는 교육적이고 긍정적인 표현을 사용하며, 학생의 강점과 발전 가능성을 강조해야 합니다."""

        user_prompt = f"""
학생 정보:
- 이름: {student['name']}
- 생년월일: {student['birth_date']}
- 관심분야: {student['interests']}
- 학력: {student['education']}

상담 기록:
{counseling_text}

맞춤형 지시사항:
{custom_instructions if custom_instructions else '표준 생활기록부 형식으로 작성'}

위 정보를 바탕으로 학생의 생활기록부를 작성해주세요.
1. 학생의 전반적인 특성과 성장 과정을 요약해주세요 (200-300자)
2. 각 상담 내용을 통합하여 학생의 학업, 생활, 진로 측면의 발달사항을 기술해주세요 (500-800자)
"""
        
        # Groq API 사용 (무료, 빠른 추론)
        if groq_api_key:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"Groq API 오류: {response.text}")
            
            ai_report = response.json()['choices'][0]['message']['content']
        else:
            # API 키가 없으면 스타일별 생기부 템플릿 생성
            ai_report = generate_report_template(student, counselings, counseling_text, style)
        
        ai_report = ai_report
        
        return {
            "student_id": student_id,
            "student_name": student['name'],
            "report": ai_report,
            "counseling_count": len(counselings),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 보고서 생성 실패: {str(e)}")
    finally:
        conn.close()

# ==================== 헬스 체크 ====================

@app.get("/api/status")
async def api_status():
    """API 상태 확인"""
    return {
        "message": "학급 관리 시스템 API",
        "version": "2.0",
        "status": "running"
    }

def generate_calculation_pdf(calculation_result: dict, course_code: str):
    """과정 계산 결과 PDF 생성"""
    try:
        # 한글 폰트 등록
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic.ttf')
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
            font_name = 'NanumGothic'
        else:
            font_name = 'Helvetica'
        
        # PDF 파일 경로 (크로스 플랫폼 지원)
        import tempfile
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"course_calculation_{course_code}_{timestamp}.pdf"
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, filename)
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        story = []
        
        # 스타일 정의
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=12
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=16
        )
        
        # 제목
        story.append(Paragraph(f'과정 자동 계산 보고서', title_style))
        story.append(Paragraph(f'과정 코드: {course_code}', normal_style))
        story.append(Spacer(1, 20))
        
        # 1. 기본 정보
        story.append(Paragraph('1. 과정 기본 정보', heading_style))
        basic_data = [
            ['항목', '내용'],
            ['과정 시작일', calculation_result['start_date']],
            ['과정 종료일', calculation_result['final_end_date']],
            ['총 교육시간', f"{calculation_result['total_hours']}시간"],
            ['일일 수업시간', f"{calculation_result['daily_hours']}시간 (오전 {calculation_result['morning_hours']}h + 오후 {calculation_result['afternoon_hours']}h)"],
            ['주간 수업시간', f"{calculation_result['daily_hours'] * 5}시간 (월~금)"]
        ]
        basic_table = Table(basic_data, colWidths=[100, 300])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # 2. 단계별 상세
        story.append(Paragraph('2. 교육 단계별 상세', heading_style))
        phase_data = [
            ['단계', '시간', '일수', '시작일', '종료일'],
            ['이론', f"{calculation_result['lecture_hours']}h", f"{calculation_result['lecture_days']}일", 
             calculation_result['start_date'], calculation_result['lecture_end_date']],
            ['프로젝트', f"{calculation_result['project_hours']}h", f"{calculation_result['project_days']}일",
             calculation_result['lecture_end_date'], calculation_result['project_end_date']],
            ['현장실습', f"{calculation_result['workship_hours']}h", f"{calculation_result['workship_days']}일",
             calculation_result['project_end_date'], calculation_result['workship_end_date']]
        ]
        phase_table = Table(phase_data, colWidths=[80, 70, 70, 90, 90])
        phase_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(phase_table)
        story.append(Spacer(1, 20))
        
        # 3. 일수 계산
        story.append(Paragraph('3. 교육일수 분석', heading_style))
        days_data = [
            ['구분', '일수'],
            ['총 기간', f"{calculation_result['total_days']}일"],
            ['근무일', f"{calculation_result['work_days']}일"],
            ['주말', f"{calculation_result['weekend_days']}일"],
            ['공휴일', f"{calculation_result['holiday_count']}일"],
            ['제외일 합계', f"{calculation_result['excluded_days']}일"]
        ]
        days_table = Table(days_data, colWidths=[200, 200])
        days_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(days_table)
        story.append(Spacer(1, 20))
        
        # 4. 공휴일 목록
        story.append(Paragraph('4. 과정 기간 내 공휴일', heading_style))
        story.append(Paragraph(f"공휴일: {calculation_result['holidays_formatted']}", normal_style))
        story.append(Spacer(1, 20))
        
        # 5. 계산 공식
        story.append(Paragraph('5. 계산 방식', heading_style))
        story.append(Paragraph('• 근무일 계산: 주말(토,일) 및 공휴일 제외', normal_style))
        story.append(Paragraph(f"• 일일 수업: {calculation_result['morning_hours']}시간(오전) + {calculation_result['afternoon_hours']}시간(오후) = {calculation_result['daily_hours']}시간", normal_style))
        story.append(Paragraph(f"• 필요 근무일 = 총 교육시간({calculation_result['total_hours']}h) ÷ 일일시간({calculation_result['daily_hours']}h) = {calculation_result['work_days']}일", normal_style))
        story.append(Spacer(1, 20))
        
        # 생성 정보
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}", normal_style))
        story.append(Paragraph("시스템: 바이오헬스교육관리시스템", normal_style))
        
        # PDF 빌드
        doc.build(story)
        
        # FTP 업로드
        try:
            upload_to_ftp(pdf_path, f"course_reports/{filename}")
            print(f"[OK] PDF FTP 업로드 완료: {filename}")
        except Exception as e:
            print(f"[WARN] PDF FTP 업로드 실패: {str(e)}")
        
        return pdf_path
        
    except Exception as e:
        import traceback
        print(f"PDF 생성 오류: {str(e)}")
        print(traceback.format_exc())
        raise

def generate_detailed_calculation(start_date, lecture_hours, project_hours, workship_hours,
                                  morning_hours, afternoon_hours, holidays_detail,
                                  lecture_end_date, project_end_date, workship_end_date,
                                  lecture_days, project_days, intern_days,
                                  weekend_days, holiday_count):
    """상세 계산 과정 생성 - 오전/오후 분할 고려"""
    from datetime import timedelta
    from collections import defaultdict
    
    # 날짜 형식 헬퍼
    def format_date(d):
        weekdays = ['월', '화', '수', '목', '금', '토', '일']
        return f"{d.year}-{d.month:02d}-{d.day:02d} ({weekdays[d.weekday()]})"
    
    # 공휴일 set 생성
    holidays_set = set([h['date'] for h in holidays_detail]) if holidays_detail else set()
    
    def is_workday(date):
        return date.weekday() < 5 and date not in holidays_set
    
    # 상세 계산 로직 (오전/오후 분할 정확 처리, 날짜별 상세 표시)
    def calculate_stage_detail(stage_name, start, hours, morning_h, afternoon_h, start_at_afternoon=False):
        current = start
        remaining = hours
        monthly_hours = defaultdict(lambda: {'days': 0, 'hours': 0, 'detail': []})
        all_dates = []  # 모든 날짜 기록
        
        # 첫날 오후부터 시작하는 경우
        first_day = True
        
        while remaining > 0:
            if not is_workday(current):
                current += timedelta(days=1)
                continue
            
            month_key = f"{current.year}년 {current.month}월"
            day_hours = 0
            time_str = ""
            
            # 첫날이고 오후부터 시작하는 경우
            if first_day and start_at_afternoon:
                # 오후만
                if remaining >= afternoon_h:
                    day_hours = afternoon_h
                    remaining -= afternoon_h
                    time_str = f"오후 {afternoon_h}시간"
                else:
                    day_hours = remaining
                    remaining = 0
                    time_str = f"오후 {day_hours}시간"
                first_day = False
            else:
                # 일반적인 경우: 오전 + 오후
                morning_done = 0
                afternoon_done = 0
                
                # 오전
                if remaining >= morning_h:
                    morning_done = morning_h
                    remaining -= morning_h
                elif remaining > 0:
                    morning_done = remaining
                    remaining = 0
                
                # 오후
                if remaining >= afternoon_h:
                    afternoon_done = afternoon_h
                    remaining -= afternoon_h
                elif remaining > 0:
                    afternoon_done = remaining
                    remaining = 0
                
                day_hours = morning_done + afternoon_done
                
                if morning_done > 0 and afternoon_done > 0:
                    time_str = f"오전 {morning_done}시간 + 오후 {afternoon_done}시간"
                elif morning_done > 0:
                    time_str = f"오전 {morning_done}시간"
                elif afternoon_done > 0:
                    time_str = f"오후 {afternoon_done}시간"
                
                first_day = False
            
            if day_hours > 0:
                monthly_hours[month_key]['hours'] += day_hours
                monthly_hours[month_key]['days'] += 1
                all_dates.append(f"    {format_date(current)}: {time_str} (누적: {hours - remaining}시간)")
            
            current += timedelta(days=1)
        
        # 종료일 찾기
        end_date = current - timedelta(days=1)
        while not is_workday(end_date):
            end_date -= timedelta(days=1)
        
        # 종료 시간 판단
        # 오후부터 시작한 경우: (hours - afternoon_h) % 8을 기준으로 계산
        # 그 외: hours % 8을 기준으로 계산
        if start_at_afternoon:
            # 첫날 오후(4시간) + N일 + 마지막날
            # 예: 220 = 4(첫날) + 208(26일) + 8(마지막날)
            remaining_after_first = hours - afternoon_h
            last_day_hours = remaining_after_first % (morning_h + afternoon_h)
        else:
            last_day_hours = hours % (morning_h + afternoon_h)
        
        if last_day_hours == 0:
            end_time = "18:00"
        elif last_day_hours <= morning_h:
            end_time = "13:00"
        else:
            end_time = "18:00"
        
        # 월별 요약 생성 (날짜별 상세 포함)
        summary = f"\n【{stage_name}: {hours}시간】\n"
        summary += f"  • 시작: {format_date(start)} {'14:00' if start_at_afternoon else '09:00'}\n"
        summary += f"  • 종료: {format_date(end_date)} {end_time}\n\n"
        
        summary += "  📅 일자별 상세:\n"
        for date_line in all_dates:
            summary += date_line + "\n"
        
        summary += "\n  [STAT] 월별 집계:\n"
        for month, data in sorted(monthly_hours.items()):
            summary += f"    {month}: 근무일 {data['days']}일, 수업시간 {data['hours']}시간\n"
        
        summary += f"\n  [OK] 총: {hours}시간 완료\n"
        
        # 다음 단계가 오후부터 시작하는지 판단
        # last_day_hours == 0이면 오전+오후 모두 사용 → 다음은 다음날 오전부터
        # last_day_hours <= morning_h이면 오전만 사용 → 다음은 같은 날 오후부터
        # last_day_hours > morning_h이면 오전+오후 모두 사용 → 다음은 다음날 오전부터
        ends_with_afternoon = (last_day_hours == 0 or last_day_hours > morning_h)
        
        return summary, end_date, ends_with_afternoon
    
    # 공휴일 정보 포맷팅
    holidays_str = ""
    if holidays_detail:
        for h in holidays_detail:
            holidays_str += f"\n  - {h['date'].year}-{h['date'].month:02d}-{h['date'].day:02d} ({h['weekday']}): {h['name']}"
    else:
        holidays_str += "\n  없음"
    
    # 각 단계별 상세 계산
    lecture_detail, lecture_actual_end, lecture_ends_afternoon = calculate_stage_detail(
        "1단계: 이론", start_date, lecture_hours, morning_hours, afternoon_hours, False
    )
    
    # 프로젝트 시작일 결정
    if lecture_ends_afternoon:
        # 이론이 하루 전체를 사용했다면 다음날부터
        project_start = lecture_actual_end + timedelta(days=1)
        while not is_workday(project_start):
            project_start += timedelta(days=1)
        project_starts_afternoon = False
    else:
        # 이론이 오전만 사용했다면 같은 날 오후부터
        project_start = lecture_actual_end
        project_starts_afternoon = True
    
    project_detail, project_actual_end, project_ends_afternoon = calculate_stage_detail(
        "2단계: 프로젝트", project_start, project_hours, morning_hours, afternoon_hours, project_starts_afternoon
    )
    
    # 현장실습 시작일 결정
    if project_ends_afternoon:
        intern_start = project_actual_end + timedelta(days=1)
        while not is_workday(intern_start):
            intern_start += timedelta(days=1)
        intern_starts_afternoon = False
    else:
        intern_start = project_actual_end
        intern_starts_afternoon = True
    
    intern_detail, intern_actual_end, _ = calculate_stage_detail(
        "3단계: 현장실습", intern_start, workship_hours, morning_hours, afternoon_hours, intern_starts_afternoon
    )
    
    details = f"""
[STAT] 과정 자동 계산 상세 내역

📋 기본 정보
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 시작일: {format_date(start_date)}
• 일일 수업: 오전 {morning_hours}시간 + 오후 {afternoon_hours}시간 = {morning_hours + afternoon_hours}시간
• 주간 수업: {(morning_hours + afternoon_hours) * 5}시간 (월~금)

🎯 교육 단계별 시간
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 이론: {lecture_hours}시간
• 프로젝트: {project_hours}시간
• 현장실습: {workship_hours}시간
• 총: {lecture_hours + project_hours + workship_hours}시간

📅 공휴일 (과정 기간 내)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{holidays_str}
• 총 공휴일: {holiday_count}일

🧮 단계별 계산 과정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{lecture_detail}
{project_detail}
{intern_detail}

[STAT] 최종 요약
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 교육 기간: {format_date(start_date)} ~ {format_date(intern_actual_end)}
• 총 교육시간: {lecture_hours + project_hours + workship_hours}시간
• 총 근무일: {lecture_days + project_days + intern_days}일
• 주말 제외: {weekend_days}일
• 공휴일 제외: {holiday_count}일
• 실제 경과일: {(intern_actual_end - start_date).days + 1}일
"""
    
    # 정확한 종료일 반환
    actual_dates = {
        'lecture_end': lecture_actual_end,
        'project_end': project_actual_end,
        'workship_end': intern_actual_end
    }
    
    return details, actual_dates
    return details

@app.post("/api/courses/calculate-dates")
async def calculate_course_dates(data: dict):
    """
    과정 날짜 자동 계산 (공휴일 제외)
    - start_date: 시작일
    - lecture_hours: 강의시간
    - project_hours: 프로젝트시간
    - workship_hours: 현장실습시간
    """
    from datetime import timedelta
    
    try:
        start_date_str = data.get('start_date')
        lecture_hours = int(data.get('lecture_hours', 0))
        project_hours = int(data.get('project_hours', 0))
        workship_hours = int(data.get('workship_hours', 0))
        daily_hours = int(data.get('daily_hours', 8))  # 일일 수업시간 (기본값 8시간)
        morning_hours = int(data.get('morning_hours', 4))
        afternoon_hours = int(data.get('afternoon_hours', 4))
        
        if not start_date_str:
            raise HTTPException(status_code=400, detail="시작일은 필수입니다.")
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        # 시간을 일수로 변환 (입력된 일일 시간 기준)
        lecture_days = (lecture_hours + daily_hours - 1) // daily_hours  # 올림 처리
        project_days = (project_hours + daily_hours - 1) // daily_hours
        intern_days = (workship_hours + daily_hours - 1) // daily_hours
        
        # 공휴일 가져오기
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 시작일로부터 1년간의 공휴일 조회
        end_year = start_date.year + 1
        cursor.execute("""
            SELECT holiday_date 
            FROM holidays 
            WHERE holiday_date >= %s 
            AND YEAR(holiday_date) BETWEEN %s AND %s
        """, (start_date_str, start_date.year, end_year))
        
        holidays_result = cursor.fetchall()
        holidays = set(row[0] for row in holidays_result)
        
        cursor.close()
        conn.close()
        
        # 근무일 계산 함수 (주말 및 공휴일 제외)
        def add_business_days(start, days_to_add):
            current = start
            added_days = 0
            
            while added_days < days_to_add:
                current += timedelta(days=1)
                # 주말(토요일=5, 일요일=6)과 공휴일 제외
                if current.weekday() < 5 and current not in holidays:
                    added_days += 1
            
            return current
        
        # 각 단계별 종료일 계산
        lecture_end_date = add_business_days(start_date, lecture_days)
        project_end_date = add_business_days(lecture_end_date, project_days)
        workship_end_date = add_business_days(project_end_date, intern_days)
        
        # 총 일수 계산 (실제 캘린더 일수)
        total_days = (workship_end_date - start_date).days
        
        # 과정 기간 내 공휴일 목록 생성 (상세)
        holidays_in_period = []
        holidays_detail = []  # 상세 정보 저장
        current = start_date
        
        # 공휴일 이름 조회를 위한 DB 연결
        conn_holiday = get_db_connection()
        cursor_holiday = conn_holiday.cursor(pymysql.cursors.DictCursor)
        
        while current <= workship_end_date:
            if current in holidays:
                # 공휴일 이름 조회
                cursor_holiday.execute(
                    "SELECT name FROM holidays WHERE holiday_date = %s",
                    (current,)
                )
                holiday_info = cursor_holiday.fetchone()
                holiday_name = holiday_info['name'] if holiday_info else '공휴일'
                
                holidays_in_period.append(current)
                holidays_detail.append({
                    'date': current,
                    'name': holiday_name,
                    'weekday': ['월', '화', '수', '목', '금', '토', '일'][current.weekday()]
                })
            current += timedelta(days=1)
        
        cursor_holiday.close()
        conn_holiday.close()
        
        # 공휴일을 그룹화 (연속된 날짜는 범위로 표시)
        holiday_strings = []
        if holidays_in_period:
            holidays_in_period.sort()
            i = 0
            while i < len(holidays_in_period):
                start_holiday = holidays_in_period[i]
                end_holiday = start_holiday
                
                # 연속된 날짜 찾기
                j = i + 1
                while j < len(holidays_in_period) and (holidays_in_period[j] - holidays_in_period[j-1]).days == 1:
                    end_holiday = holidays_in_period[j]
                    j += 1
                
                # 포맷팅 (연속이면 범위로, 아니면 단일 날짜로)
                if start_holiday == end_holiday:
                    holiday_strings.append(start_holiday.strftime('%-m/%-d'))
                else:
                    holiday_strings.append(f"{start_holiday.strftime('%-m/%-d')}~{end_holiday.strftime('%-m/%-d')}")
                
                i = j
        
        # 주말 일수 계산
        weekend_days = 0
        current = start_date
        while current <= workship_end_date:
            if current.weekday() >= 5:  # 토요일(5), 일요일(6)
                weekend_days += 1
            current += timedelta(days=1)
        
        # 제외 일수 (주말 + 공휴일)
        excluded_days = weekend_days + len(holidays_in_period)
        
        # 상세 계산 과정 생성 (정확한 종료일 포함)
        calculation_details, actual_dates = generate_detailed_calculation(
            start_date, lecture_hours, project_hours, workship_hours,
            morning_hours, afternoon_hours, holidays_detail,
            lecture_end_date, project_end_date, workship_end_date,
            lecture_days, project_days, intern_days,
            weekend_days, len(holidays_in_period)
        )
        
        # 정확한 종료일 사용
        lecture_end_date = actual_dates['lecture_end']
        project_end_date = actual_dates['project_end']
        workship_end_date = actual_dates['workship_end']
        
        result = {
            "start_date": start_date_str,
            "lecture_end_date": lecture_end_date.strftime('%Y-%m-%d'),
            "project_end_date": project_end_date.strftime('%Y-%m-%d'),
            "workship_end_date": workship_end_date.strftime('%Y-%m-%d'),
            "final_end_date": workship_end_date.strftime('%Y-%m-%d'),
            "total_days": (workship_end_date - start_date).days,
            "lecture_days": lecture_days,
            "project_days": project_days,
            "workship_days": intern_days,
            "work_days": lecture_days + project_days + intern_days,
            "weekend_days": weekend_days,
            "holiday_count": len(holidays_in_period),
            "excluded_days": excluded_days,
            "holidays_formatted": ", ".join(holiday_strings) if holiday_strings else "없음",
            "holidays_detail": holidays_detail,
            "lecture_hours": lecture_hours,
            "project_hours": project_hours,
            "workship_hours": workship_hours,
            "total_hours": lecture_hours + project_hours + workship_hours,
            "morning_hours": morning_hours,
            "afternoon_hours": afternoon_hours,
            "daily_hours": daily_hours,
            "course_code": data.get('course_code', ''),
            "calculation_details": calculation_details
        }
        
        # course_code가 있으면 비고란에 상세 계산 과정 저장
        course_code = data.get('course_code')
        if course_code:
            try:
                import re
                conn_update = get_db_connection()
                cursor_update = conn_update.cursor()
                
                # 이모지 및 4바이트 UTF-8 문자 제거 (utf8mb4 미지원 DB 컬럼 대응)
                def remove_emoji(text):
                    # 4바이트 UTF-8 문자 모두 제거 (이모지 포함)
                    # UTF-8에서 4바이트는 \xF0-\xF7로 시작
                    try:
                        # 각 문자를 검사하여 4바이트 문자 제거
                        return ''.join(c for c in text if len(c.encode('utf-8')) < 4)
                    except:
                        return text
                
                notes_text = remove_emoji(calculation_details)
                
                # 과정의 비고란(notes)에 상세 계산 과정 저장
                cursor_update.execute("""
                    UPDATE courses 
                    SET notes = %s
                    WHERE code = %s
                """, (notes_text, course_code))
                conn_update.commit()
                cursor_update.close()
                conn_update.close()
                
                result['notes_updated'] = True
            except Exception as e:
                print(f"비고란 업데이트 실패: {str(e)}")
                import traceback
                print(traceback.format_exc())
                result['notes_updated'] = False
                result['notes_error'] = str(e)
        
        # 자동 저장 옵션이 있으면 시간표도 생성
        if data.get('auto_save_timetable', False):
            if course_code:
                # 시간표 자동 생성 호출
                try:
                    # 과정에 배정된 교과목 자동 조회
                    conn_temp = get_db_connection()
                    cursor_temp = conn_temp.cursor(pymysql.cursors.DictCursor)
                    cursor_temp.execute("""
                        SELECT subject_code FROM course_subjects 
                        WHERE course_code = %s
                    """, (course_code,))
                    subject_codes = [row['subject_code'] for row in cursor_temp.fetchall()]
                    conn_temp.close()
                    
                    timetable_data = {
                        'course_code': course_code,
                        'start_date': start_date_str,
                        'lecture_hours': lecture_hours,
                        'project_hours': project_hours,
                        'workship_hours': workship_hours,
                        'morning_hours': morning_hours,
                        'afternoon_hours': afternoon_hours,
                        'subject_codes': subject_codes
                    }
                    # 시간표 생성 로직 호출 (동일 함수 재사용)
                    from fastapi.responses import Response
                    timetable_result = await auto_generate_timetables(timetable_data)
                    result['timetable_generated'] = True
                    result['timetable_count'] = timetable_result.get('generated_count', 0)
                except Exception as e:
                    print(f"시간표 자동 생성 실패: {str(e)}")
                    result['timetable_generated'] = False
                    result['timetable_error'] = str(e)
        
        # PDF 생성 옵션이 있으면 PDF도 생성
        if data.get('generate_pdf', False):
            try:
                pdf_path = generate_calculation_pdf(result, data.get('course_code', 'COURSE'))
                result['pdf_generated'] = True
                result['pdf_path'] = pdf_path
            except Exception as e:
                print(f"PDF 생성 실패: {str(e)}")
                result['pdf_generated'] = False
                result['pdf_error'] = str(e)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"날짜 계산 실패: {str(e)}")

@app.post("/api/ai/generate-training-logs")
async def generate_ai_training_logs(data: dict):
    """AI 훈련일지 자동 생성"""
    timetable_ids = data.get('timetable_ids', [])
    prompt_guide = data.get('prompt', '')
    delete_before_create = data.get('delete_before_create', False)
    
    if not timetable_ids:
        raise HTTPException(status_code=400, detail="시간표 ID가 필요합니다")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        success_count = 0
        failed_count = 0
        
        for timetable_id in timetable_ids:
            try:
                # 시간표 정보 가져오기
                cursor.execute("""
                    SELECT t.*, 
                           c.name as course_name,
                           s.name as subject_name,
                           i.name as instructor_name
                    FROM timetables t
                    LEFT JOIN courses c ON t.course_code = c.code
                    LEFT JOIN subjects s ON t.subject_code = s.code
                    LEFT JOIN instructors i ON t.instructor_code = i.code
                    WHERE t.id = %s
                """, (timetable_id,))
                
                timetable = cursor.fetchone()
                if not timetable:
                    failed_count += 1
                    continue
                
                # 삭제 후 작성 옵션이 활성화된 경우, 기존 훈련일지 삭제
                if delete_before_create:
                    cursor.execute("""
                        DELETE FROM training_logs WHERE timetable_id = %s
                    """, (timetable_id,))
                
                # AI로 훈련일지 내용 생성 - 타입별 템플릿
                timetable_type = timetable.get('type', 'lecture')
                
                if timetable_type == 'project':
                    # 프로젝트 타입 템플릿
                    content = f"""[{timetable['class_date']}] 프로젝트 활동

▶ 프로젝트 정보
- 활동: 프로젝트
- 지도강사: {timetable['instructor_name'] or timetable['instructor_code']}
- 날짜: {timetable['class_date']}

▶ 금일 목표
• 프로젝트 핵심 기능 구현 및 개발 진행
• 팀원 간 역할 분담 및 협업 강화
• 프로젝트 일정 대비 진행 상황 점검

▶ 주요 진행 내용
• 프로젝트 핵심 기능 개발 및 구현
• 데이터 구조 설계 및 적용
• UI/UX 개선 작업 진행
• 코드 리뷰 및 품질 개선

▶ 팀별 활동
• 역할별 작업 진행 상황 공유
• 통합 작업 및 충돌 해결
• 상호 코드 리뷰 및 피드백

▶ 문제 해결 및 개선사항
• 발생한 기술적 이슈 해결
• 일정 지연 요인 파악 및 대응
• 효율적 개발 방법론 적용

▶ 프로젝트 목표 달성도
• 계획 대비 진행률: 약 65% (중반 단계)
• 주요 기능 구현 완료율: 70%
• 팀 협업 효율성: 우수

▶ 특이사항
{prompt_guide if prompt_guide else '특별한 사항 없음'}

▶ 향후 계획
• 다음 단계: 프로젝트 고도화 및 테스트
• 남은 기간: 프로젝트 완성 및 발표 준비
"""
                
                elif timetable_type == 'practice':
                    # 현장실습 타입 템플릿
                    content = f"""[{timetable['class_date']}] 현장실습 활동

▶ 실습 정보
- 활동: 현장실습
- 지도강사: {timetable['instructor_name'] or timetable['instructor_code']}
- 날짜: {timetable['class_date']}

▶ 금일 목표
• 현장 실무 업무 수행 및 학습
• 기업 멘토 지도 하에 실습 진행
• 실무 프로세스 이해 및 적용

▶ 주요 실습 내용
• 현장 업무 직접 수행 및 경험
• 실무 도구 및 시스템 활용 학습
• 업무 프로세스 및 워크플로우 습득
• 팀 협업 및 커뮤니케이션 실습

▶ 현장 업무 수행
• 실제 프로젝트 참여 및 기여
• 업무 요구사항 분석 및 구현
• 품질 관리 및 테스트 수행
• 문서 작성 및 보고서 제출

▶ 멘토링 및 피드백
• 기업 멘토의 실무 지도 및 조언
• 작업 결과물에 대한 구체적 피드백
• 개선 방향 및 학습 가이드 제공
• 진로 상담 및 커리어 조언

▶ 학습 성과 및 역량
• 실무 경험 축적 및 역량 강화
• 현장 업무 수행 능력 향상
• 협업 및 문제 해결 역량 강화
• 직무 역량 및 전문성 성장

▶ 특이사항
{prompt_guide if prompt_guide else '특별한 사항 없음'}

▶ 향후 계획
• 현장 실습 지속 및 심화
• 실무 프로젝트 완성도 제고
"""
                
                else:  # lecture (교과목)
                    # 교과목 타입 템플릿 (기존 유지)
                    content = f"""[{timetable['class_date']}] {timetable['subject_name'] or '과목'} 수업

▶ 교육 내용
- 과목: {timetable['subject_name'] or timetable['subject_code']}
- 강사: {timetable['instructor_name'] or timetable['instructor_code']}
- 수업 유형: 교과

▶ 학습 목표
• {timetable['subject_name'] or '과목'}의 핵심 개념 이해
• 실무 활용 방법 습득
• 관련 기술 실습 능력 향상

▶ 주요 학습 내용
• {timetable['subject_name'] or '과목'} 이론 강의 진행
• 기본 원리 및 핵심 개념 설명
• 실제 활용 사례 분석
• 단계별 실습 프로젝트 수행

▶ 실습 활동
• {timetable['subject_name'] or '과목'} 기반 프로젝트 실습
• 개별/팀별 과제 수행
• 문제 해결 및 피드백

▶ 학습 성과
• {timetable['subject_name'] or '과목'}에 대한 이해도 향상
• 실무 적용 능력 강화
• 과제 완료율 우수

▶ 특이사항
{prompt_guide if prompt_guide else '특별한 사항 없음'}

▶ 다음 시간 계획
• {timetable['subject_name'] or '과목'} 심화 학습 진행 예정
"""
                
                # 훈련일지 생성
                cursor.execute("""
                    INSERT INTO training_logs (timetable_id, content, created_at)
                    VALUES (%s, %s, NOW())
                """, (timetable_id, content))
                
                success_count += 1
                
            except Exception as e:
                print(f"훈련일지 생성 실패 (timetable_id: {timetable_id}): {str(e)}")
                failed_count += 1
                continue
        
        conn.commit()
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "total_count": len(timetable_ids)
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"AI 훈련일지 생성 실패: {str(e)}")
    finally:
        conn.close()

@app.post("/api/counselings/ai-generate")
async def generate_ai_counseling(data: dict):
    """AI 상담일지 자동 생성"""
    student_code = data.get('student_code')
    course_code = data.get('course_code')
    custom_prompt = data.get('custom_prompt', '')
    
    if not student_code:
        raise HTTPException(status_code=400, detail="학생 코드가 필요합니다")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 학생 정보 가져오기 (student_id 필요)
        cursor.execute("""
            SELECT s.*, c.name as course_name
            FROM students s
            LEFT JOIN courses c ON s.course_code = c.code
            WHERE s.code = %s
        """, (student_code,))
        
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="학생을 찾을 수 없습니다")
        
        student_id = student['id']
        
        # 기존 상담 횟수 확인 (consultations 테이블 사용)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM consultations
            WHERE student_id = %s
        """, (student_id,))
        
        result = cursor.fetchone()
        counseling_count = result['count'] if result else 0
        
        # AI로 상담일지 내용 생성
        content = f"""[상담 {counseling_count + 1}회차] {student['name']} 학생 상담

▶ 학생 정보
- 이름: {student['name']}
- 학생 코드: {student['code']}
- 과정: {student.get('course_name', '')}
- 연락처: {student.get('phone', '')}

▶ 상담 내용
{student['name']} 학생과 학업 진행 상황 및 향후 계획에 대해 상담을 진행하였습니다.

▶ 학습 태도 및 참여도
학생의 수업 참여도와 학습 태도가 양호한 편이며, 과제 수행 능력도 우수합니다.

▶ 진로 및 목표
현재 진행 중인 과정에 대한 이해도가 높으며, 명확한 진로 목표를 가지고 있습니다.

▶ 특이사항 및 요청사항
{custom_prompt if custom_prompt else '특별한 사항 없음'}

▶ 향후 지도 방향
- 현재의 학습 태도를 유지하도록 격려
- 추가적인 학습 자료 제공 및 심화 학습 기회 제공
- 정기적인 진도 체크 및 피드백 제공

▶ 다음 상담 계획
약 2-3주 후 학습 진도를 확인하고 추가 상담을 진행할 예정입니다.
"""
        
        # 상담일지 생성 (consultations 테이블에 student_id 사용)
        cursor.execute("""
            INSERT INTO consultations 
            (student_id, consultation_date, consultation_type, main_topic, content, status, created_at)
            VALUES (%s, CURDATE(), '정기', 'AI 자동 생성', %s, '완료', NOW())
        """, (student_id, content))
        
        conn.commit()
        
        return {
            "message": "상담일지가 생성되었습니다",
            "student_code": student_code,
            "student_name": student['name']
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"AI 상담일지 생성 실패: {str(e)}")
    finally:
        conn.close()

@app.post("/api/ai/replace-timetable")
async def replace_timetable(data: dict):
    """AI 시간표 대체: 시간표 날짜 변경 및 원래 날짜를 공휴일로 등록"""
    course_code = data.get('course_code')
    original_date = data.get('original_date')
    replacement_date = data.get('replacement_date')
    
    if not course_code or not original_date or not replacement_date:
        raise HTTPException(status_code=400, detail="모든 필드가 필요합니다")
    
    if original_date == replacement_date:
        raise HTTPException(status_code=400, detail="원래 날짜와 대체 날짜가 같습니다")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. 해당 날짜의 시간표 개수 확인
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM timetables
            WHERE course_code = %s AND class_date = %s
        """, (course_code, original_date))
        count_result = cursor.fetchone()
        timetables_count = count_result['count']
        
        if timetables_count == 0:
            raise HTTPException(status_code=404, detail="해당 날짜에 시간표가 없습니다")
        
        # 2. 시간표 날짜 업데이트
        cursor.execute("""
            UPDATE timetables
            SET class_date = %s
            WHERE course_code = %s AND class_date = %s
        """, (replacement_date, course_code, original_date))
        
        updated_count = cursor.rowcount
        
        # 3. 원래 날짜를 공휴일로 등록
        # 공휴일명: "공강/대체(대체날짜)"
        holiday_name = f"공강/대체({replacement_date})"
        
        # 기존 공휴일이 있는지 확인
        cursor.execute("""
            SELECT id FROM holidays
            WHERE holiday_date = %s
        """, (original_date,))
        existing_holiday = cursor.fetchone()
        
        if existing_holiday:
            # 기존 공휴일 업데이트
            cursor.execute("""
                UPDATE holidays
                SET name = %s
                WHERE holiday_date = %s
            """, (holiday_name, original_date))
        else:
            # 새 공휴일 등록
            cursor.execute("""
                INSERT INTO holidays (holiday_date, name, is_legal)
                VALUES (%s, %s, 0)
            """, (original_date, holiday_name))
        
        conn.commit()
        
        return {
            "success": True,
            "timetables_updated": updated_count,
            "original_date": original_date,
            "replacement_date": replacement_date,
            "holiday_created": {
                "date": original_date,
                "name": holiday_name,
                "category": "일반"
            }
        }
        
    except HTTPException as he:
        conn.rollback()
        raise he
    except Exception as e:
        conn.rollback()
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"[ERROR] 시간표 대체 실패: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"시간표 대체 실패: {error_detail}")
    finally:
        if conn:
            conn.close()

@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    category: str = Query(..., description="guidance, train, student, teacher, team")
):
    """
    이미지 파일을 FTP 서버에 업로드
    
    Args:
        file: 업로드할 이미지 파일
        category: 저장 카테고리 (guidance=상담일지, train=훈련일지, student=학생, teacher=강사, team=팀)
    
    Returns:
        업로드된 파일의 URL
    """
    try:
        # 파일 확장자 검증 (이미지 + PDF)
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico', '.svg',  # 이미지 + 파비콘
            '.pdf',  # PDF
            '.ppt', '.pptx',  # PowerPoint
            '.xls', '.xlsx',  # Excel
            '.doc', '.docx',  # Word
            '.txt',  # 텍스트
            '.hwp'  # 한글
        ]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"허용되지 않는 파일 형식입니다. 허용 형식: {', '.join(allowed_extensions)}"
            )
        
        # 파일 크기 체크 (100MB 제한 - 메모리에 올리지 않고 크기만 확인)
        await file.seek(0, 2)  # 파일 끝으로 이동
        file_size = await file.tell()  # 현재 위치 = 파일 크기
        await file.seek(0)  # 파일 처음으로 되돌림
        
        if file_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"파일 크기는 100MB를 초과할 수 없습니다 (현재: {file_size / 1024 / 1024:.2f}MB)")
        
        # 원본 파일명 보존 (타임스탬프 접두어로 중복 방지)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        # 원본 파일명에서 확장자 제거
        original_name = os.path.splitext(file.filename)[0]
        
        # 안전한 파일명으로 변환 (ASCII 문자만 허용)
        # 한글/특수문자는 언더스코어로, 영문/숫자/-/_/.만 유지
        safe_name = ""
        for c in original_name:
            if c.isascii() and (c.isalnum() or c in ('-', '_', '.')):
                safe_name += c
            else:
                safe_name += '_'
        
        # 연속된 언더스코어 제거
        import re
        safe_name = re.sub(r'_+', '_', safe_name)
        safe_name = safe_name.strip('_')
        
        # 너무 긴 파일명은 자르기
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        
        # 파일명이 비어있으면 file로 대체
        if not safe_name:
            safe_name = "file"
        
        new_filename = f"{timestamp}_{unique_id}_{safe_name}{file_ext}"
        
        # 스트리밍 FTP 업로드 (메모리 절약)
        file_url = await upload_stream_to_ftp(file, new_filename, category)
        
        return {
            "success": True,
            "url": file_url,
            "filename": new_filename,
            "original_filename": file.filename,  # 원본 파일명 추가
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] 이미지 업로드 실패 (category={category}): {str(e)}")
        print(f"[ERROR] Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"이미지 업로드 실패: {str(e)}")

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    directory: str = Form("uploads")
):
    """
    범용 파일 업로드 API (신규가입 프로필 사진 등)
    
    Args:
        file: 업로드할 파일
        directory: FTP 저장 디렉토리 (기본값: uploads)
    
    Returns:
        업로드된 파일의 URL
    """
    try:
        # 파일 확장자 검증
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # 이미지
            '.pdf', '.doc', '.docx', '.txt', '.hwp'  # 문서
        ]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"허용되지 않는 파일 형식입니다. 허용 형식: {', '.join(allowed_extensions)}"
            )
        
        # 파일 크기 체크 (10MB 제한)
        await file.seek(0, 2)
        file_size = await file.tell()
        await file.seek(0)
        
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"파일 크기는 10MB를 초과할 수 없습니다")
        
        # 파일명 생성 (타임스탬프 + UUID)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        original_name = os.path.splitext(file.filename)[0]
        safe_filename = f"{timestamp}_{unique_id}{file_ext}"
        
        # 파일 데이터 읽기
        file_data = await file.read()
        
        # FTP 업로드
        ftp = ftplib.FTP()
        ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
        ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
        
        # /homes/ha/camFTP/BH2025/student 디렉토리로 이동
        ftp.cwd('/homes/ha/camFTP/BH2025/student')
        
        # 파일 업로드
        ftp.storbinary(f'STOR {safe_filename}', io.BytesIO(file_data))
        ftp.quit()
        
        # URL 생성
        file_url = f"ftp://{FTP_CONFIG['host']}/homes/ha/camFTP/BH2025/student/{safe_filename}"
        
        print(f"[OK] 파일 업로드 성공: {file_url}")
        
        return {
            "success": True,
            "file_url": file_url,
            "filename": safe_filename,
            "original_filename": file.filename,
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] 파일 업로드 실패: {e}")
        print(f"[ERROR] Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")

@app.post("/api/upload-image-base64")
async def upload_image_base64(data: dict):
    """
    Base64 인코딩된 이미지를 FTP 서버에 업로드 (모바일 카메라 촬영용)
    
    Args:
        data: {
            "image": "data:image/jpeg;base64,...",
            "category": "guidance|train|student|teacher"
        }
    
    Returns:
        업로드된 파일의 URL
    """
    try:
        image_data = data.get('image')
        category = data.get('category')
        
        if not image_data or not category:
            raise HTTPException(status_code=400, detail="image와 category는 필수입니다")
        
        # Base64 데이터 파싱
        if ',' in image_data:
            header, base64_data = image_data.split(',', 1)
            # 이미지 타입 추출 (data:image/jpeg;base64 -> jpeg)
            if 'image/' in header:
                image_type = header.split('image/')[1].split(';')[0]
                file_ext = f'.{image_type}'
            else:
                file_ext = '.jpg'
        else:
            base64_data = image_data
            file_ext = '.jpg'
        
        # Base64 디코딩
        file_data = base64.b64decode(base64_data)
        
        # 파일 크기 체크 (100MB 제한 - 413 에러 방지)
        if len(file_data) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"파일 크기는 100MB를 초과할 수 없습니다 (현재: {len(file_data) / 1024 / 1024:.2f}MB)")
        
        # 고유한 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{timestamp}_{unique_id}{file_ext}"
        
        # FTP 업로드
        file_url = upload_to_ftp(file_data, new_filename, category)
        
        return {
            "success": True,
            "url": file_url,
            "filename": new_filename,
            "size": len(file_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Base64 이미지 업로드 실패: {str(e)}")
        print(f"[ERROR] Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"이미지 업로드 실패: {str(e)}")

@app.get("/api/download-image")
async def download_image(url: str = Query(..., description="FTP URL to download")):
    """
    FTP 서버의 이미지를 다운로드하는 프록시 API
    
    Args:
        url: FTP URL (예: ftp://bitnmeta2.synology.me:2121/homes/ha/camFTP/BH2025/guidance/file.jpg)
    
    Returns:
        이미지 파일
    """
    try:
        # FTP URL 파싱
        if not url.startswith('ftp://'):
            raise HTTPException(status_code=400, detail="FTP URL이 아닙니다")
        
        # URL에서 정보 추출
        # ftp://bitnmeta2.synology.me:2121/homes/ha/camFTP/BH2025/guidance/file.jpg
        url_parts = url.replace('ftp://', '').split('/', 1)
        host_port = url_parts[0]
        file_path = url_parts[1] if len(url_parts) > 1 else ''
        
        # 호스트와 포트 분리
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 21
        
        # 파일명 추출
        filename = file_path.split('/')[-1]
        
        # FTP 연결 및 다운로드
        ftp = FTP()
        ftp.encoding = 'utf-8'  # 한글 파일명 지원
        ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
        ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
        
        # 파일 다운로드
        file_data = io.BytesIO()
        ftp.retrbinary(f'RETR /{file_path}', file_data.write)
        ftp.quit()
        
        # 파일 데이터 가져오기
        file_data.seek(0)
        file_bytes = file_data.read()
        
        # 임시 파일로 저장 (크로스 플랫폼 지원)
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_filename = os.path.join(temp_dir, filename)
        with open(temp_filename, 'wb') as f:
            f.write(file_bytes)
        
        # 파일 확장자로 MIME 타입 결정
        ext = os.path.splitext(filename)[1].lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.hwp': 'application/x-hwp'
        }
        media_type = media_type_map.get(ext, 'application/octet-stream')
        
        # PDF와 이미지는 inline으로 보여주고, 나머지는 다운로드
        inline_types = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.txt']
        disposition_type = 'inline' if ext in inline_types else 'attachment'
        
        return FileResponse(
            temp_filename,
            media_type=media_type,
            filename=filename,
            headers={
                'Content-Disposition': f'{disposition_type}; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 다운로드 실패: {str(e)}")

@app.get("/api/thumbnail")
@app.head("/api/thumbnail")
async def get_thumbnail(url: str = Query(..., description="FTP URL")):
    """
    이미지 썸네일 제공 API
    
    Args:
        url: FTP URL
    
    Returns:
        썸네일 이미지 (있으면 제공, 없으면 FTP에서 다운로드하여 생성)
    """
    try:
        # URL에서 파일명 추출
        filename = url.split('/')[-1]
        thumb_filename = f"thumb_{filename}"
        # 크로스 플랫폼 지원 경로
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        thumbnails_dir = os.path.join(backend_dir, 'thumbnails')
        thumb_path = os.path.join(thumbnails_dir, thumb_filename)
        
        # 썸네일 디렉토리 생성 (없으면)
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # 썸네일이 있으면 반환
        if os.path.exists(thumb_path):
            return FileResponse(
                thumb_path,
                media_type='image/jpeg',
                headers={
                    'Cache-Control': 'public, max-age=86400'  # 1일 캐싱
                }
            )
        
        # 썸네일이 없으면 FTP에서 원본 다운로드하여 생성
        try:
            # FTP URL 파싱
            url_parts = url.replace('ftp://', '').split('/', 1)
            file_path = url_parts[1] if len(url_parts) > 1 else ''
            
            # FTP 연결 및 다운로드
            ftp = FTP()
            ftp.encoding = 'utf-8'  # 한글 파일명 지원
            ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
            ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
            
            # 파일 다운로드
            file_data = io.BytesIO()
            ftp.retrbinary(f'RETR /{file_path}', file_data.write)
            ftp.quit()
            
            # 파일 데이터 가져오기
            file_data.seek(0)
            file_bytes = file_data.read()
            
            # 썸네일 생성
            thumb_result = create_thumbnail(file_bytes, filename)
            
            if thumb_result and os.path.exists(thumb_path):
                return FileResponse(
                    thumb_path,
                    media_type='image/jpeg',
                    headers={
                        'Cache-Control': 'public, max-age=86400'
                    }
                )
            else:
                # 썸네일 생성 실패
                raise HTTPException(status_code=404, detail="썸네일 생성 실패")
                
        except Exception as e:
            print(f"FTP 다운로드 및 썸네일 생성 실패: {str(e)}")
            raise HTTPException(status_code=404, detail="썸네일을 생성할 수 없습니다")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"썸네일 조회 실패: {str(e)}")

@app.get("/health")
async def health_check():
    """헬스 체크"""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# ==================== 인증 API ====================

@app.post("/api/auth/login")
async def login(credentials: dict):
    """
    통합 로그인 API
    - 이름으로 강사 또는 학생 자동 구분 로그인
    - 기본 비밀번호: kdt2025
    - 관리자 계정: root / xhRl1004!@# (DB 없이 접속 가능)
    """
    user_name = credentials.get('name')
    password = credentials.get('password')
    
    if not user_name or not password:
        raise HTTPException(status_code=400, detail="이름과 비밀번호를 입력하세요")
    
    # 🔐 관리자 계정 (.env에서 로드, DB 없이 무조건 접속 가능)
    ROOT_USERNAME = os.getenv('ROOT_USERNAME', 'root')
    ROOT_PASSWORD = os.getenv('ROOT_PASSWORD', 'xhRl1004!@#')
    
    if user_name.strip() == ROOT_USERNAME and password == ROOT_PASSWORD:
        print(f"[OK] 관리자({ROOT_USERNAME}) 로그인 성공")
        # 모든 메뉴에 대한 권한 부여
        all_permissions = {
            "dashboard": True,
            "instructor-codes": True,
            "instructors": True,
            "system-settings": True,
            "subjects": True,
            "holidays": True,
            "courses": True,
            "students": True,
            "counselings": True,
            "timetables": True,
            "training-logs": True,
            "ai-report": True,
            "ai-training-log": True,
            "ai-counseling": True,
            "projects": True,
            "team-activity-logs": True
        }
        return {
            "success": True,
            "message": "관리자님, 환영합니다!",
            "instructor": {
                "code": "ROOT",
                "name": ROOT_USERNAME,
                "phone": None,
                "major": "시스템 관리자",
                "instructor_type": "0",
                "email": "root@system.com",
                "photo_urls": None,
                "password": ROOT_PASSWORD,
                "instructor_type_name": "관리자",
                "instructor_type_type": "0",
                "permissions": all_permissions,
                "default_screen": "dashboard"
            }
        }
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1️⃣ 먼저 강사 테이블에서 검색
        cursor.execute("SHOW COLUMNS FROM instructors LIKE 'password'")
        has_instructor_password = cursor.fetchone() is not None
        
        ensure_profile_photo_columns(cursor, 'instructors')
        
        if has_instructor_password:
            cursor.execute("""
                SELECT i.code, TRIM(i.name) as name, i.phone, i.major, i.instructor_type, 
                       i.email, i.created_at, i.updated_at, i.profile_photo, i.attachments, i.password,
                       ic.name as instructor_type_name, ic.type as instructor_type_type, 
                       ic.permissions, ic.default_screen
                FROM instructors i
                LEFT JOIN instructor_codes ic ON i.instructor_type = ic.code
                WHERE TRIM(i.name) = %s
            """, (user_name.strip(),))
        else:
            cursor.execute("""
                SELECT i.code, TRIM(i.name) as name, i.phone, i.major, i.instructor_type, 
                       i.email, i.created_at, i.updated_at, i.profile_photo, i.attachments,
                       ic.name as instructor_type_name, ic.type as instructor_type_type, 
                       ic.permissions, ic.default_screen
                FROM instructors i
                LEFT JOIN instructor_codes ic ON i.instructor_type = ic.code
                WHERE TRIM(i.name) = %s
            """, (user_name.strip(),))
        
        instructor = cursor.fetchone()
        
        # 2️⃣ 강사로 검색되면 강사 로그인 처리
        if instructor:
        
            # 비밀번호 확인 (기본값: kdt2025)
            default_password = "kdt2025"
            stored_password = instructor.get('password', default_password)
            
            if stored_password is None:
                stored_password = default_password
            
            if password != stored_password:
                raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")
            
            # datetime 변환
            for key, value in instructor.items():
                if isinstance(value, (datetime, date)):
                    instructor[key] = value.isoformat()
                elif isinstance(value, bytes):
                    instructor[key] = None
            
            # permissions 처리 (JSON 또는 menu_permissions 배열)
            import json
            permissions_dict = {}
            
            # 1. permissions 컬럼 확인 (JSON 문자열)
            if instructor.get('permissions'):
                try:
                    permissions_dict = json.loads(instructor['permissions'])
                except:
                    pass
            
            # 2. menu_permissions 배열 확인
            if not permissions_dict:
                cursor.execute("""
                    SELECT menu_permissions FROM instructor_codes WHERE code = %s
                """, (instructor.get('instructor_type'),))
                result = cursor.fetchone()
                if result and result.get('menu_permissions'):
                    try:
                        menu_list = json.loads(result['menu_permissions'])
                        permissions_dict = {menu: True for menu in menu_list}
                    except:
                        pass
            
            # 3. 권한이 없으면 빈 객체
            if not permissions_dict:
                permissions_dict = {}
            
            instructor['permissions'] = permissions_dict
            
            print(f"[OK] 강사 로그인 성공: {instructor['name']}")
            return {
                "success": True,
                "message": f"{instructor['name']}님, 환영합니다!",
                "user_type": "instructor",
                "instructor": instructor
            }
        
        # 3️⃣ 강사가 아니면 학생 테이블에서 검색
        ensure_profile_photo_columns(cursor, 'students')
        
        cursor.execute("SHOW COLUMNS FROM students LIKE 'password'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE students ADD COLUMN password VARCHAR(100) DEFAULT 'kdt2025'")
            conn.commit()
        
        cursor.execute("""
            SELECT s.*, 
                   c.name as course_name,
                   c.start_date,
                   c.final_end_date as end_date
            FROM students s
            LEFT JOIN courses c ON s.course_code = c.code
            WHERE s.name = %s
            LIMIT 1
        """, (user_name.strip(),))
        
        student = cursor.fetchone()
        
        if not student:
            raise HTTPException(status_code=401, detail="등록되지 않은 사용자입니다")
        
        # 비밀번호 확인
        default_password = "kdt2025"
        stored_password = student.get('password', default_password)
        
        if stored_password is None:
            stored_password = default_password
        
        if password != stored_password:
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")
        
        # datetime 변환
        for key, value in student.items():
            if isinstance(value, (datetime, date)):
                student[key] = value.isoformat()
            elif isinstance(value, bytes):
                student[key] = None
        
        print(f"[OK] 학생 로그인 성공: {student['name']}")
        return {
            "success": True,
            "message": f"{student['name']}님, 환영합니다!",
            "user_type": "student",
            "student": student
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")
    finally:
        conn.close()

@app.post("/api/auth/student-login")
async def student_login(credentials: dict):
    """
    학생 로그인 API
    - 학생 이름과 비밀번호로 로그인
    - 기본 비밀번호: kdt2025
    """
    student_name = credentials.get('name')
    password = credentials.get('password')
    
    print(f"[DEBUG] 학생 로그인 시도: 이름='{student_name}', 비밀번호='{password}'")
    
    if not student_name:
        raise HTTPException(status_code=400, detail="이름을 입력하세요")
    
    if not password:
        raise HTTPException(status_code=400, detail="비밀번호를 입력하세요")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # profile_photo와 attachments 컬럼이 없으면 자동 생성
        ensure_profile_photo_columns(cursor, 'students')
        
        # password 컬럼이 없으면 추가
        cursor.execute("SHOW COLUMNS FROM students LIKE 'password'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE students ADD COLUMN password VARCHAR(100) DEFAULT 'kdt2025'")
            conn.commit()
            print("[OK] students 테이블에 password 컬럼 추가")
        
        # 학생 조회 (이름으로)
        cursor.execute("""
            SELECT s.*, 
                   c.name as course_name,
                   c.start_date,
                   c.final_end_date as end_date
            FROM students s
            LEFT JOIN courses c ON s.course_code = c.code
            WHERE s.name = %s
            LIMIT 1
        """, (student_name.strip(),))
        
        student = cursor.fetchone()
        
        print(f"[DEBUG] 조회 결과: {student}")
        
        if not student:
            print(f"[ERROR] 학생을 찾을 수 없음: '{student_name}' (길이: {len(student_name)}, bytes: {student_name.encode('utf-8')})")
            
            # 신규 가입 신청 내역 확인
            cursor.execute("""
                SELECT status, created_at 
                FROM student_registrations 
                WHERE name = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (student_name.strip(),))
            registration = cursor.fetchone()
            
            if registration:
                if registration['status'] == 'pending':
                    raise HTTPException(
                        status_code=403, 
                        detail="신청 대기 중|회원가입 신청이 접수되었습니다.\n관리자 승인 후 로그인이 가능합니다.\n\n신청일시: " + 
                               (registration['created_at'].strftime('%Y년 %m월 %d일 %H시 %M분') if registration['created_at'] else '알 수 없음')
                    )
                elif registration['status'] == 'rejected':
                    raise HTTPException(
                        status_code=403,
                        detail="신청 거절됨|회원가입 신청이 거절되었습니다.\n자세한 사항은 관리자에게 문의하세요."
                    )
            
            # 모든 학생 이름 목록 출력
            cursor.execute("SELECT id, name FROM students ORDER BY id")
            all_students = cursor.fetchall()
            print(f"📋 등록된 학생 목록: {[s['name'] for s in all_students]}")
            raise HTTPException(
                status_code=401, 
                detail="등록되지 않은 사용자|입력하신 정보로 등록된 학생을 찾을 수 없습니다.\n\n신규 가입을 원하시면 회원가입 페이지를 이용해 주세요."
            )
        
        # 비밀번호 확인 (기본값: kdt2025)
        default_password = "kdt2025"
        stored_password = student.get('password', default_password)
        
        if stored_password is None:
            stored_password = default_password
        
        if password != stored_password:
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")
        
        # datetime 변환
        for key, value in student.items():
            if isinstance(value, (datetime, date)):
                student[key] = value.isoformat()
            elif isinstance(value, bytes):
                student[key] = None
        
        return {
            "success": True,
            "message": f"{student['name']}님, 환영합니다!",
            "student": student
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")
    finally:
        conn.close()

@app.post("/api/auth/change-password")
async def change_password(data: dict):
    """
    비밀번호 변경 API
    - old_password가 있으면: 본인이 비밀번호 변경 (기존 비밀번호 확인 필요)
    - old_password가 없으면: 주강사가 다른 강사 비밀번호 관리 (기존 비밀번호 확인 불필요)
    """
    instructor_code = data.get('instructor_code')
    old_password = data.get('old_password')  # 선택적 파라미터
    new_password = data.get('new_password')
    
    if not instructor_code or not new_password:
        raise HTTPException(status_code=400, detail="강사코드와 새 비밀번호를 입력하세요")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # password 컬럼이 없으면 추가
        cursor.execute("SHOW COLUMNS FROM instructors LIKE 'password'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE instructors ADD COLUMN password VARCHAR(100) DEFAULT 'kdt2025'")
            conn.commit()
        
        # 기존 비밀번호 확인 (old_password가 제공된 경우에만)
        if old_password:
            cursor.execute("SELECT password FROM instructors WHERE code = %s", (instructor_code,))
            result = cursor.fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다")
            
            stored_password = result.get('password', 'kdt2025')
            if stored_password is None:
                stored_password = 'kdt2025'
            
            if old_password != stored_password:
                raise HTTPException(status_code=401, detail="현재 비밀번호가 일치하지 않습니다")
        else:
            # old_password가 없으면 주강사 권한으로 직접 변경
            cursor.execute("SELECT code FROM instructors WHERE code = %s", (instructor_code,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="강사를 찾을 수 없습니다")
        
        # 비밀번호 업데이트
        cursor.execute("""
            UPDATE instructors 
            SET password = %s 
            WHERE code = %s
        """, (new_password, instructor_code))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "비밀번호가 변경되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"비밀번호 변경 실패: {str(e)}")
    finally:
        conn.close()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """프론트엔드 index.html 서빙"""
    try:
        index_path = os.path.join(frontend_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")

# ==================== 팀 활동일지 API ====================

@app.get("/api/team-activity-logs")
async def get_team_activity_logs(project_id: Optional[int] = None):
    """팀 활동일지 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if project_id:
            cursor.execute("""
                SELECT * FROM team_activity_logs
                WHERE project_id = %s
                ORDER BY activity_date DESC, created_at DESC
            """, (project_id,))
        else:
            cursor.execute("""
                SELECT * FROM team_activity_logs
                ORDER BY activity_date DESC, created_at DESC
            """)
        
        logs = cursor.fetchall()
        return logs
    except pymysql.err.ProgrammingError as e:
        # 테이블이 없는 경우 빈 배열 반환
        if "doesn't exist" in str(e):
            return []
        raise
    finally:
        conn.close()

@app.post("/api/team-activity-logs")
async def create_team_activity_log(log: dict):
    """팀 활동일지 생성"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO team_activity_logs 
            (project_id, instructor_code, activity_date, activity_type, content, achievements, next_plan, notes, photo_urls)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            log.get('project_id'),
            log.get('instructor_code'),
            log.get('activity_date'),
            log.get('activity_type', '팀 활동'),
            log.get('content'),
            log.get('achievements'),
            log.get('next_plan'),
            log.get('notes'),
            log.get('photo_urls', '[]')
        ))
        
        conn.commit()
        log_id = cursor.lastrowid
        
        return {"success": True, "id": log_id, "message": "팀 활동일지가 생성되었습니다"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/team-activity-logs/{log_id}")
async def update_team_activity_log(log_id: int, log: dict):
    """팀 활동일지 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE team_activity_logs
            SET instructor_code = %s, activity_date = %s, activity_type = %s, content = %s,
                achievements = %s, next_plan = %s, notes = %s, photo_urls = %s
            WHERE id = %s
        """, (
            log.get('instructor_code'),
            log.get('activity_date'),
            log.get('activity_type'),
            log.get('content'),
            log.get('achievements'),
            log.get('next_plan'),
            log.get('notes'),
            log.get('photo_urls', '[]'),
            log_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="팀 활동일지를 찾을 수 없습니다")
        
        return {"success": True, "message": "팀 활동일지가 수정되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/team-activity-logs/{log_id}")
async def delete_team_activity_log(log_id: int):
    """팀 활동일지 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM team_activity_logs WHERE id = %s", (log_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="팀 활동일지를 찾을 수 없습니다")
        
        return {"success": True, "message": "팀 활동일지가 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    """로그인 페이지 서빙"""
    try:
        login_path = os.path.join(frontend_dir, "login.html")
        with open(login_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Login page not found")

@app.get("/manifest.json")
async def serve_manifest():
    """manifest.json 서빙"""
    from fastapi.responses import FileResponse
    manifest_path = os.path.join(frontend_dir, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="manifest.json not found")

@app.get("/{filename}.html", response_class=HTMLResponse)
async def serve_html(filename: str):
    """프론트엔드 HTML 파일 서빙"""
    try:
        html_path = os.path.join(frontend_dir, f"{filename}.html")
        if not os.path.exists(html_path):
            raise HTTPException(status_code=404, detail=f"{filename}.html not found")
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"{filename}.html not found")

@app.get("/{filename:path}.js")
async def serve_js(filename: str):
    """프론트엔드 JS 파일 서빙"""
    from fastapi.responses import FileResponse
    js_path = os.path.join(frontend_dir, f"{filename}.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail=f"{filename}.js not found")

@app.get("/{filename:path}.css")
async def serve_css(filename: str):
    """프론트엔드 CSS 파일 서빙"""
    from fastapi.responses import FileResponse
    css_path = os.path.join(frontend_dir, f"{filename}.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    raise HTTPException(status_code=404, detail=f"{filename}.css not found")

@app.get("/favicon.ico")
async def serve_favicon():
    """favicon.ico 서빙"""
    from fastapi.responses import FileResponse
    favicon_path = os.path.join(frontend_dir, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    raise HTTPException(status_code=404, detail="favicon.ico not found")

@app.get("/{filename}.png")
async def serve_png(filename: str):
    """PNG 이미지 파일 서빙"""
    from fastapi.responses import FileResponse
    png_path = os.path.join(frontend_dir, f"{filename}.png")
    if os.path.exists(png_path):
        return FileResponse(png_path, media_type="image/png")
    raise HTTPException(status_code=404, detail=f"{filename}.png not found")

# ==================== FTP 이미지 프록시 ====================
from fastapi.responses import StreamingResponse
from urllib.parse import urlparse, unquote

@app.get("/api/proxy-image")
async def proxy_ftp_image(url: str):
    """FTP 이미지를 HTTP로 프록시"""
    try:
        # URL 파싱
        parsed = urlparse(url)
        
        if parsed.scheme != 'ftp':
            raise HTTPException(status_code=400, detail="FTP URL만 지원됩니다")
        
        # FTP 연결
        ftp = FTP()
        ftp.encoding = 'utf-8'  # 한글 파일명 지원
        ftp.connect(parsed.hostname or FTP_CONFIG['host'], parsed.port or FTP_CONFIG['port'])
        ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
        
        # 파일 경로 추출 (URL 디코딩)
        file_path = unquote(parsed.path)
        
        # 파일을 메모리로 읽기
        file_data = io.BytesIO()
        ftp.retrbinary(f'RETR {file_path}', file_data.write)
        ftp.quit()
        
        # 파일 포인터를 처음으로 이동
        file_data.seek(0)
        
        # 파일 확장자로 MIME 타입 결정
        ext = file_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp'
        }
        media_type = mime_types.get(ext, 'image/jpeg')
        
        return StreamingResponse(file_data, media_type=media_type)
        
    except Exception as e:
        print(f"FTP 이미지 프록시 에러: {e}")
        raise HTTPException(status_code=500, detail=f"이미지를 불러올 수 없습니다: {str(e)}")

# ==================== 시스템 설정 API ====================

def ensure_system_settings_table(cursor):
    """system_settings 테이블이 없으면 생성"""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                setting_key VARCHAR(50) UNIQUE NOT NULL,
                setting_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("[OK] system_settings 테이블 확인/생성 완료")
    except Exception as e:
        print(f"[WARN] system_settings 테이블 생성 실패: {e}")

@app.get("/api/system-settings")
async def get_system_settings():
    """시스템 설정 조회"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        ensure_system_settings_table(cursor)
        conn.commit()
        
        cursor.execute("SELECT * FROM system_settings")
        settings = cursor.fetchall()
        
        # 설정을 키-값 형태로 변환
        settings_dict = {}
        for setting in settings:
            settings_dict[setting['setting_key']] = setting['setting_value']
        
        # 기본값 설정
        if 'system_title' not in settings_dict:
            settings_dict['system_title'] = 'KDT교육관리시스템 v3.2'
        if 'system_subtitle1' not in settings_dict:
            settings_dict['system_subtitle1'] = '보건복지부(한국보건산업진흥원), KDT, 우송대학교산학협력단'
        if 'system_subtitle2' not in settings_dict:
            settings_dict['system_subtitle2'] = '바이오헬스아카데미 올인원테크 이노베이터'
        if 'logo_url' not in settings_dict:
            settings_dict['logo_url'] = '/woosong-logo.png'
        if 'favicon_url' not in settings_dict:
            settings_dict['favicon_url'] = '/favicon.ico'
        
        return settings_dict
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.post("/api/system-settings")
async def update_system_settings(
    system_title: Optional[str] = Form(None),
    system_subtitle1: Optional[str] = Form(None),
    system_subtitle2: Optional[str] = Form(None),
    logo_url: Optional[str] = Form(None),
    favicon_url: Optional[str] = Form(None),
    youtube_api_key: Optional[str] = Form(None),
    groq_api_key: Optional[str] = Form(None),
    gemini_api_key: Optional[str] = Form(None),
    bgm_genre: Optional[str] = Form(None),
    bgm_volume: Optional[str] = Form(None),
    dashboard_refresh_interval: Optional[str] = Form(None)
):
    """시스템 설정 업데이트"""
    print(f"📝 시스템 설정 업데이트 요청:")
    print(f"  - system_title: {system_title}")
    print(f"  - system_subtitle1: {system_subtitle1}")
    print(f"  - system_subtitle2: {system_subtitle2}")
    print(f"  - logo_url: {logo_url}")
    print(f"  - favicon_url: {favicon_url}")
    print(f"  - youtube_api_key: {youtube_api_key}")
    print(f"  - groq_api_key: {'설정됨' if groq_api_key else '미설정'}")
    print(f"  - gemini_api_key: {'설정됨' if gemini_api_key else '미설정'}")
    print(f"  - bgm_genre: {bgm_genre}")
    print(f"  - bgm_volume: {bgm_volume}")
    print(f"  - dashboard_refresh_interval: {dashboard_refresh_interval}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        ensure_system_settings_table(cursor)
        conn.commit()
        
        updates = {
            'system_title': system_title,
            'system_subtitle1': system_subtitle1,
            'system_subtitle2': system_subtitle2,
            'logo_url': logo_url,
            'favicon_url': favicon_url,
            'youtube_api_key': youtube_api_key,
            'groq_api_key': groq_api_key,
            'gemini_api_key': gemini_api_key,
            'bgm_genre': bgm_genre,
            'bgm_volume': bgm_volume,
            'dashboard_refresh_interval': dashboard_refresh_interval
        }
        
        update_count = 0
        for key, value in updates.items():
            if value is not None:
                print(f"💾 DB 업데이트: {key} = {value}")
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = %s
                """, (key, value, value))
                update_count += 1
        
        conn.commit()
        print(f"[OK] {update_count}개 설정 업데이트 완료")
        
        # 저장된 데이터 확인
        cursor.execute("SELECT setting_key, setting_value FROM system_settings")
        saved_data = cursor.fetchall()
        print(f"[STAT] 현재 DB 상태:")
        for row in saved_data:
            print(f"  - {row[0]}: {row[1]}")
        
        return {"message": "시스템 설정이 업데이트되었습니다", "updated_count": update_count}
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 시스템 설정 업데이트 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# ==================== 학생 수업일지 API ====================

def ensure_class_notes_table(cursor):
    """class_notes 테이블이 없으면 생성하고 필요한 컬럼 추가"""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS class_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                instructor_code VARCHAR(50),
                note_date DATE NOT NULL,
                content TEXT,
                photo_urls TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_student_date (student_id, note_date),
                INDEX idx_instructor_code (instructor_code, note_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 기존 테이블에 instructor_code 컬럼이 없으면 추가
        try:
            cursor.execute("""
                ALTER TABLE class_notes 
                ADD COLUMN instructor_code VARCHAR(50) AFTER student_id
            """)
            print("[OK] instructor_code 컬럼 추가됨")
        except Exception:
            pass  # 이미 존재하면 무시
        
        # 기존 테이블에 photo_urls 컬럼이 없으면 추가
        try:
            cursor.execute("""
                ALTER TABLE class_notes 
                ADD COLUMN photo_urls TEXT AFTER content
            """)
            print("[OK] photo_urls 컬럼 추가됨")
        except Exception:
            pass  # 이미 존재하면 무시
        
        # student_id를 NULL 허용으로 변경
        try:
            cursor.execute("""
                ALTER TABLE class_notes 
                MODIFY COLUMN student_id INT NULL
            """)
            print("[OK] student_id NULL 허용으로 변경됨")
        except Exception:
            pass
        
        # note_date를 DATE에서 DATETIME으로 변경 (시간 정보 저장)
        try:
            cursor.execute("""
                ALTER TABLE class_notes 
                MODIFY COLUMN note_date DATETIME NOT NULL
            """)
            print("[OK] note_date를 DATETIME으로 변경됨")
        except Exception as e:
            # 이미 DATETIME이거나 변경 불가능하면 무시
            pass
        
        print("[OK] class_notes 테이블 확인/생성 완료")
    except Exception as e:
        print(f"[WARN] class_notes 테이블 생성 실패: {e}")

@app.get("/api/class-notes")
async def get_all_class_notes(student_id: Optional[int] = None, instructor_code: Optional[str] = None):
    """모든 수업일지 조회 (필터링 옵션)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_class_notes_table(cursor)
        conn.commit()
        
        query = "SELECT * FROM class_notes WHERE 1=1"
        params = []
        
        if student_id is not None:
            # 학생 메모만 조회 (student_id가 일치하고 NULL이 아닌 것)
            query += " AND student_id = %s AND student_id IS NOT NULL"
            params.append(student_id)
        
        if instructor_code is not None:
            # 강사 메모만 조회 (instructor_code가 일치하고 student_id가 NULL인 것)
            query += " AND instructor_code = %s AND student_id IS NULL"
            params.append(instructor_code)
        
        query += " ORDER BY note_date DESC"
        
        cursor.execute(query, params)
        notes = cursor.fetchall()
        
        # datetime 변환
        for note in notes:
            for key, value in note.items():
                if isinstance(value, (datetime, date)):
                    note[key] = value.isoformat()
        
        return notes
    finally:
        conn.close()

@app.get("/api/class-notes/{note_id}")
async def get_class_note_by_id(note_id: int):
    """ID로 특정 수업일지 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_class_notes_table(cursor)
        conn.commit()
        
        cursor.execute("SELECT * FROM class_notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        
        if not note:
            raise HTTPException(status_code=404, detail="수업일지를 찾을 수 없습니다")
        
        # datetime 변환
        for key, value in note.items():
            if isinstance(value, (datetime, date)):
                note[key] = value.isoformat()
        
        return note
    finally:
        conn.close()

@app.post("/api/class-notes")
async def create_class_note(data: dict):
    """수업일지 생성 또는 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_class_notes_table(cursor)
        
        note_id = data.get('id')  # ID가 있으면 수정
        student_id = data.get('student_id')
        instructor_code = data.get('instructor_code')
        note_date = data.get('note_date')
        content = data.get('content', '')
        photo_urls = data.get('photo_urls', '[]')
        
        print(f"[DEBUG] class-notes 데이터 수신: id={note_id}, student_id={student_id}, note_date={note_date}, content_len={len(content)}")
        
        if not note_date:
            raise HTTPException(status_code=400, detail="note_date는 필수입니다")
        
        # student_id와 instructor_code 중 하나는 반드시 있어야 함
        if not student_id and not instructor_code:
            raise HTTPException(status_code=400, detail="student_id 또는 instructor_code가 필요합니다")
        
        # ID가 있으면 UPDATE, 없으면 INSERT
        if note_id:
            cursor.execute(
                """UPDATE class_notes 
                   SET student_id = %s, instructor_code = %s, note_date = %s, content = %s, photo_urls = %s
                   WHERE id = %s""",
                (student_id, instructor_code, note_date, content, photo_urls, note_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="수업일지를 찾을 수 없습니다")
        else:
            # INSERT 쿼리
            cursor.execute(
                """INSERT INTO class_notes (student_id, instructor_code, note_date, content, photo_urls) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (student_id, instructor_code, note_date, content, photo_urls)
            )
            note_id = cursor.lastrowid
        
        conn.commit()
        
        # 저장된 일지 반환
        cursor.execute("SELECT * FROM class_notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        
        # datetime 변환
        for key, value in note.items():
            if isinstance(value, (datetime, date)):
                note[key] = value.isoformat()
        
        return {"success": True, "message": "수업일지가 저장되었습니다", "note": note, "id": note_id}
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] class-notes 저장 에러: {str(e)}")
        print(f"   데이터: id={note_id}, student_id={student_id}, note_date={note_date}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.put("/api/class-notes/{note_id}")
async def update_class_note(note_id: int, data: dict):
    """수업일지 수정"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_class_notes_table(cursor)
        
        note_date = data.get('note_date')
        content = data.get('content', '')
        photo_urls = data.get('photo_urls', '[]')
        
        if not note_date:
            raise HTTPException(status_code=400, detail="note_date는 필수입니다")
        
        # UPDATE 쿼리
        cursor.execute(
            """UPDATE class_notes 
               SET note_date = %s, content = %s, photo_urls = %s 
               WHERE id = %s""",
            (note_date, content, photo_urls, note_id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="수업일지를 찾을 수 없습니다")
        
        conn.commit()
        
        # 수정된 일지 반환
        cursor.execute("SELECT * FROM class_notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        
        # datetime 변환
        for key, value in note.items():
            if isinstance(value, (datetime, date)):
                note[key] = value.isoformat()
        
        return {"success": True, "message": "수업일지가 수정되었습니다", "note": note}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/class-notes/{note_id}")
async def delete_class_note(note_id: int):
    """수업일지 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM class_notes WHERE id = %s", (note_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="수업일지를 찾을 수 없습니다")
        
        return {"success": True, "message": "수업일지가 삭제되었습니다"}
    finally:
        conn.close()

@app.post("/api/upload-note-file")
async def upload_note_file(
    file: UploadFile = File(...),
    note_id: int = Form(...)
):
    """
    수업메모 파일 업로드 (사진, 문서 등)
    
    Args:
        file: 업로드할 파일
        note_id: 수업메모 ID
    
    Returns:
        업로드된 파일 정보
    """
    conn = get_db_connection()
    try:
        print(f"[DEBUG] upload-note-file 시작: note_id={note_id}, filename={file.filename}")
        
        # 파일 업로드 (기존 upload-image 로직 재사용)
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',  # 이미지
            '.pdf',  # PDF
            '.doc', '.docx',  # Word
            '.xls', '.xlsx'  # Excel
        ]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"허용되지 않는 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
            )
        
        # 파일 크기 체크 (100MB)
        # UploadFile은 seek()가 동기 함수입니다
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"파일 크기는 100MB 이하여야 합니다 (현재: {file_size / 1024 / 1024:.2f}MB)"
            )
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        original_name = os.path.splitext(file.filename)[0]
        
        # 안전한 파일명
        safe_name = ""
        for c in original_name:
            if c.isascii() and (c.isalnum() or c in ('-', '_', '.')):
                safe_name += c
            else:
                safe_name += '_'
        
        import re
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')[:50]
        if not safe_name:
            safe_name = "file"
        
        new_filename = f"{timestamp}_{unique_id}_{safe_name}{file_ext}"
        
        # FTP 업로드 (student 카테고리)
        file_url = await upload_stream_to_ftp(file, new_filename, "student")
        
        # DB에 파일 URL 추가
        cursor = conn.cursor()
        cursor.execute("SELECT photo_urls FROM class_notes WHERE id = %s", (note_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
        
        existing_urls = result[0] if result[0] else ""
        
        # URL 목록 업데이트 (콤마로 구분)
        if existing_urls:
            new_urls = f"{existing_urls},{file_url}"
        else:
            new_urls = file_url
        
        cursor.execute(
            "UPDATE class_notes SET photo_urls = %s WHERE id = %s",
            (new_urls, note_id)
        )
        conn.commit()
        
        print(f"[OK] upload-note-file 성공: note_id={note_id}, url={file_url}")
        
        return {
            "success": True,
            "url": file_url,
            "filename": new_filename,
            "note_id": note_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] upload-note-file 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
    finally:
        conn.close()

# ==================== 강사 SSIRN 메모 관리 ====================
def ensure_instructor_notes_table(cursor):
    """instructor_notes 테이블이 없으면 생성"""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS instructor_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                instructor_id INT NOT NULL,
                note_date DATE NOT NULL,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE CASCADE,
                INDEX idx_instructor_date (instructor_id, note_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("[OK] instructor_notes 테이블 확인/생성 완료")
    except Exception as e:
        print(f"[WARN] instructor_notes 테이블 생성 실패: {e}")

@app.get("/api/instructors/{instructor_id}/notes")
async def get_instructor_notes(instructor_id: int, note_date: Optional[str] = None):
    """강사의 SSIRN 메모 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_instructor_notes_table(cursor)
        conn.commit()
        
        if note_date:
            # 특정 날짜의 메모 조회
            cursor.execute(
                "SELECT * FROM instructor_notes WHERE instructor_id = %s AND note_date = %s",
                (instructor_id, note_date)
            )
            notes = cursor.fetchall()
            
            # datetime 변환
            for note in notes:
                for key, value in note.items():
                    if isinstance(value, (datetime, date)):
                        note[key] = value.isoformat()
            
            return notes
        else:
            # 모든 메모 조회 (최근 순)
            cursor.execute(
                "SELECT * FROM instructor_notes WHERE instructor_id = %s ORDER BY note_date DESC, created_at DESC",
                (instructor_id,)
            )
            notes = cursor.fetchall()
            
            # datetime 변환
            for note in notes:
                for key, value in note.items():
                    if isinstance(value, (datetime, date)):
                        note[key] = value.isoformat()
            
            return notes
    finally:
        conn.close()

@app.post("/api/instructors/{instructor_id}/notes")
async def create_or_update_instructor_note(instructor_id: int, data: dict):
    """강사 SSIRN 메모 생성 또는 업데이트"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_instructor_notes_table(cursor)
        
        note_date = data.get('note_date')
        content = data.get('content', '')
        note_id = data.get('id')  # ID가 있으면 수정, 없으면 생성
        
        if not note_date:
            raise HTTPException(status_code=400, detail="note_date는 필수입니다")
        
        if note_id:
            # ID가 제공된 경우: 기존 메모 업데이트
            cursor.execute(
                "UPDATE instructor_notes SET content = %s, note_date = %s WHERE id = %s AND instructor_id = %s",
                (content, note_date, note_id, instructor_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
            message = "메모가 수정되었습니다"
        else:
            # ID가 없는 경우: 항상 새로 생성 (같은 날짜에도 여러 개 가능)
            cursor.execute(
                "INSERT INTO instructor_notes (instructor_id, note_date, content) VALUES (%s, %s, %s)",
                (instructor_id, note_date, content)
            )
            note_id = cursor.lastrowid
            message = "메모가 저장되었습니다"
        
        conn.commit()
        
        # 저장된 메모 반환
        cursor.execute("SELECT * FROM instructor_notes WHERE id = %s", (note_id,))
        note = cursor.fetchone()
        
        # datetime 변환
        for key, value in note.items():
            if isinstance(value, (datetime, date)):
                note[key] = value.isoformat()
        
        return {"success": True, "message": message, "note": note}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/api/instructors/{instructor_id}/notes/{note_id}")
async def delete_instructor_note(instructor_id: int, note_id: int):
    """강사 SSIRN 메모 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM instructor_notes WHERE id = %s AND instructor_id = %s", (note_id, instructor_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다")
        
        return {"success": True, "message": "메모가 삭제되었습니다"}
    finally:
        conn.close()

# ==================== 공지사항 관리 ====================
def ensure_notices_table(cursor):
    """notices 테이블이 없으면 생성"""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                target_type VARCHAR(20) DEFAULT 'all' COMMENT '대상: all(전체), courses(특정반)',
                target_courses TEXT COMMENT '대상 반 목록 (JSON)',
                created_by VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_dates (start_date, end_date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # 기존 테이블에 컬럼 추가 (없는 경우만)
        try:
            cursor.execute("SHOW COLUMNS FROM notices LIKE 'target_type'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE notices ADD COLUMN target_type VARCHAR(20) DEFAULT 'all' COMMENT '대상: all(전체), courses(특정반)'")
                print("[OK] notices 테이블에 target_type 컬럼 추가")
        except:
            pass
        
        try:
            cursor.execute("SHOW COLUMNS FROM notices LIKE 'target_courses'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE notices ADD COLUMN target_courses TEXT COMMENT '대상 반 목록 (JSON)'")
                print("[OK] notices 테이블에 target_courses 컬럼 추가")
        except:
            pass
        
        print("[OK] notices 테이블 확인/생성 완료")
    except Exception as e:
        print(f"[WARN] notices 테이블 생성 실패: {e}")

@app.get("/api/notices")
async def get_notices(active_only: bool = False, course_id: str = None):
    """공지사항 목록 조회 (반별 필터링 지원)"""
    import json
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        ensure_notices_table(cursor)
        conn.commit()
        
        if active_only:
            # 현재 활성화된 공지만 조회 (오늘 날짜가 start_date와 end_date 사이)
            cursor.execute("""
                SELECT * FROM notices 
                WHERE CURDATE() BETWEEN start_date AND end_date
                ORDER BY created_at DESC
            """)
        else:
            # 모든 공지 조회
            cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        
        notices = cursor.fetchall()
        
        # 반별 필터링
        if course_id:
            filtered_notices = []
            for notice in notices:
                # target_type이 'all'이면 모두에게 표시
                if notice.get('target_type') == 'all' or not notice.get('target_type'):
                    filtered_notices.append(notice)
                # target_type이 'courses'이면 target_courses 체크
                elif notice.get('target_type') == 'courses' and notice.get('target_courses'):
                    try:
                        target_list = json.loads(notice['target_courses'])
                        if course_id in target_list:
                            filtered_notices.append(notice)
                    except:
                        pass
            notices = filtered_notices
        
        # datetime 변환
        for notice in notices:
            for key, value in notice.items():
                if isinstance(value, (datetime, date)):
                    notice[key] = value.isoformat()
        
        return notices
    finally:
        conn.close()

@app.get("/api/notices/{notice_id}")
async def get_notice(notice_id: int):
    """특정 공지사항 조회"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM notices WHERE id = %s", (notice_id,))
        notice = cursor.fetchone()
        
        if not notice:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        # datetime 변환
        for key, value in notice.items():
            if isinstance(value, (datetime, date)):
                notice[key] = value.isoformat()
        
        return notice
    finally:
        conn.close()

@app.post("/api/notices")
async def create_notice(data: dict):
    """공지사항 생성"""
    import json
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        ensure_notices_table(cursor)
        conn.commit()
        
        # target_courses를 JSON 문자열로 변환
        target_courses = data.get('target_courses', [])
        target_courses_json = json.dumps(target_courses) if target_courses else None
        
        query = """
            INSERT INTO notices (title, content, start_date, end_date, target_type, target_courses, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['title'],
            data['content'],
            data['start_date'],
            data['end_date'],
            data.get('target_type', 'all'),
            target_courses_json,
            data.get('created_by')
        ))
        conn.commit()
        
        return {"id": cursor.lastrowid, "success": True, "message": "공지사항이 등록되었습니다"}
    finally:
        conn.close()

@app.put("/api/notices/{notice_id}")
async def update_notice(notice_id: int, data: dict):
    """공지사항 수정"""
    import json
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # target_courses를 JSON 문자열로 변환
        target_courses = data.get('target_courses', [])
        target_courses_json = json.dumps(target_courses) if target_courses else None
        
        query = """
            UPDATE notices
            SET title = %s, content = %s, start_date = %s, end_date = %s,
                target_type = %s, target_courses = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            data['title'],
            data['content'],
            data['start_date'],
            data['end_date'],
            data.get('target_type', 'all'),
            target_courses_json,
            notice_id
        ))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        return {"success": True, "message": "공지사항이 수정되었습니다"}
    finally:
        conn.close()

@app.delete("/api/notices/{notice_id}")
async def delete_notice(notice_id: int):
    """공지사항 삭제"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        return {"success": True, "message": "공지사항이 삭제되었습니다"}
    finally:
        conn.close()

# ==================== 예진이 챗봇 API ====================
@app.post("/api/aesong-chat")
async def aesong_chat(data: dict, request: Request):
    """예진이 AI 챗봇 - GROQ, Gemini, 또는 Gemma 모델 사용"""
    message = data.get('message', '')
    character = data.get('character', '예진이')  # 캐릭터 이름 받기
    model = data.get('model', 'groq')  # 사용할 모델 (groq, gemini, gemma)
    
    # 헤더에서 API 키 가져오기 (프론트엔드에서 전달)
    groq_api_key_header = request.headers.get('X-GROQ-API-Key', '')
    gemini_api_key_header = request.headers.get('X-Gemini-API-Key', '')
    
    # DB에서 API 키 가져오기 (헤더가 없을 경우)
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT setting_key, setting_value FROM system_settings WHERE setting_key IN ('groq_api_key', 'gemini_api_key')")
        db_settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
    except:
        db_settings = {}
    finally:
        cursor.close()
        conn.close()
    
    # API 키 우선순위: 헤더 > DB > 환경변수
    groq_api_key = groq_api_key_header or db_settings.get('groq_api_key', '') or os.getenv('GROQ_API_KEY', '')
    gemini_api_key = gemini_api_key_header or db_settings.get('gemini_api_key', '') or os.getenv('GOOGLE_CLOUD_TTS_API_KEY', '')
    
    if not message:
        raise HTTPException(status_code=400, detail="메시지가 필요합니다")
    
    try:
        # 캐릭터별 페르소나 설정
        if character == '데이빗':
            system_prompt = """당신은 '데이빗'입니다. 우송대학교 바이오헬스 교육과정의 생산직 프로그램 전문가입니다.

특징:
- AI 기반 바이오헬스 디지털 케어 프로그램 개발 전문가입니다
- 학생들이 AI를 활용한 헬스케어 솔루션을 개발할 수 있도록 쉽게 실습 중심으로 설명합니다
- 친절하고 열정적인 톤으로 대화합니다
- 쉽고 이해하기 편한 말투를 사용합니다 (예: ~하면 돼요, ~해보세요)
- 이모티콘을 사용하지 마세요 (절대 금지)
- 복잡한 AI와 헬스케어 개념도 실습 예제로 쉽게 설명해줍니다
- 실무 경험을 바탕으로 실용적인 조언을 제공합니다
- 짧고 명확하면서도 친절하게 답변합니다 (2-3문장)

중요: 당신의 이름은 '데이빗'입니다. 절대 다른 이름을 사용하지 마세요.

역할:
- 우송대학교 바이오헬스 교육 관리 시스템의 생산직 프로그램 전문가
- AI 기반 바이오헬스 디지털 케어 프로그램 개발 교육
- 헬스케어 데이터 분석, AI 모델 구축, 디지털 헬스 앱 개발 등 실습 중심 교육
- 학생들에게 실무에서 바로 활용 가능한 AI 헬스케어 기술 전수
- 매우 친절하고 열정적인 강사"""
        elif character == 'PM 정운표' or character == '아솔님':
            system_prompt = """당신은 'PM 정운표'입니다. 우송대학교 바이오헬스 교육과정의 프로젝트 매니저입니다.

특징:
- 프로젝트 관리 전문가로서 실무적이고 체계적인 조언을 제공합니다
- 중후하고 신뢰감 있는 톤으로 대화합니다
- 존댓말을 사용하며 프로페셔널한 말투를 사용합니다 (예: ~하시면 됩니다, ~권장드립니다)
- 이모티콘을 사용하지 마세요 (절대 금지)
- 프로젝트 진행, 팀워크, 일정 관리 등 실무적인 조언을 제공합니다
- 짧고 명확하면서도 실용적으로 답변합니다 (2-3문장)

중요: 당신의 이름은 'PM 정운표'입니다. 절대 다른 이름을 사용하지 마세요.

역할:
- 우송대학교 바이오헬스 교육 관리 시스템의 프로젝트 매니저
- 학생들의 프로젝트 진행 및 팀 협업 지원
- 실무 중심의 조언자"""
        else:
            system_prompt = """당신은 '예진이'라는 이름의 친근하고 귀여운 AI 비서입니다.
우송대학교의 마스코트로, 학생들을 돕는 역할을 합니다.

특징:
- 항상 밝고 긍정적인 톤으로 대화합니다
- 친근하고 귀여운 말투를 사용합니다 (예: ~해요, ~이에요)
- 이모티콘을 사용하지 마세요 (절대 금지)
- 학생들의 고민과 질문에 공감하며 답변합니다
- 짧고 명확하게 답변합니다 (2-3문장)

중요: 당신의 이름은 '예진이'입니다. 절대 다른 이름을 사용하지 마세요.

역할:
- 우송대학교 바이오헬스 교육 관리 시스템의 도우미
- 학생 관리, 상담, 훈련일지 등에 대해 안내
- 친근한 대화 상대"""

        # Gemini 모델 사용
        if model == 'gemini':
            if not gemini_api_key:
                raise Exception("Gemini API 키가 설정되지 않았습니다. 시스템 등록에서 API 키를 입력해주세요.")
            
            # Gemini API 호출
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": f"{system_prompt}\n\n사용자: {message}\n\n당신:"}
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 200,
                    "topP": 0.9
                }
            }
            
            response = requests.post(gemini_url, json=payload, timeout=15)
            
            if response.status_code != 200:
                raise Exception(f"Gemini API 오류: {response.text}")
            
            result = response.json()
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
            
            return {
                "response": ai_response,
                "model": "gemini-2.0-flash-exp"
            }
        
        # Gemma-3-4B 모델 사용 (GROQ 무료 모델)
        elif model == 'gemma':
            if not groq_api_key:
                raise Exception("GROQ API 키가 설정되지 않았습니다. 시스템 등록에서 API 키를 입력해주세요.")
            
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gemma2-9b-it",  # GROQ의 Gemma 2 9B 모델 (무료)
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.8,
                "max_tokens": 200,
                "top_p": 0.9
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                raise Exception(f"GROQ API 오류: {response.text}")
            
            ai_response = response.json()['choices'][0]['message']['content']
            
            return {
                "response": ai_response,
                "model": "gemma2-9b-it"
            }
        
        # GROQ 모델 사용 (기본값 - Llama 3.3 70B)
        else:
            if not groq_api_key:
                # API 키가 없으면 안내 메시지
                raise Exception("GROQ API 키가 설정되지 않았습니다. 시스템 등록에서 API 키를 입력해주세요.")
            
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.8,
                "max_tokens": 200,
                "top_p": 0.9
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                raise Exception(f"GROQ API 오류: {response.text}")
            
            ai_response = response.json()['choices'][0]['message']['content']
            
            return {
                "response": ai_response,
                "model": "llama-3.3-70b-versatile"
            }
        
    except Exception as e:
        print(f"예진이 챗봇 오류: {str(e)}")
        # 오류 시 기본 응답
        return {
            "response": "죄송합니다. 지금은 답변하기 어려워요. 잠시 후 다시 말씀해주세요.",
            "model": "error",
            "error": str(e)
        }

# ==================== Google Cloud TTS API ====================
@app.post("/api/tts")
async def text_to_speech(data: dict, request: Request):
    """Google Cloud TTS - 텍스트를 음성으로 변환 (개선된 파라미터)"""
    text = data.get('text', '')
    character = data.get('character', '예진이')
    
    if not text:
        raise HTTPException(status_code=400, detail="텍스트가 필요합니다")
    
    # Google Cloud TTS API 키 확인
    # 1. 헤더에서 가져오기
    api_key_header = request.headers.get('X-Gemini-API-Key', '')
    
    # 2. DB에서 가져오기 (헤더가 없을 경우)
    api_key_db = ''
    if not api_key_header:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'gemini_api_key'")
            result = cursor.fetchone()
            if result:
                api_key_db = result['setting_value']
        except:
            pass
        finally:
            cursor.close()
            conn.close()
    
    # 3. 환경변수에서 가져오기 (최후 수단)
    api_key = api_key_header or api_key_db or os.getenv('GOOGLE_CLOUD_TTS_API_KEY', '')
    
    if not api_key:
        raise HTTPException(status_code=500, detail="Google Cloud TTS API 키가 설정되지 않았습니다. 시스템 등록에서 Gemini API 키를 입력해주세요.")
    
    try:
        # 캐릭터별 음성 설정 (자연스러운 파라미터로 개선)
        if character == '데이빗':
            voice_name = "ko-KR-Neural2-C"  # Neural2 남성 음성 (더 자연스러움)
            pitch = -3.0  # 적당히 낮은 톤
            speaking_rate = 0.95  # 조금 느린 속도
        elif character == 'PM 정운표' or character == '아솔님':
            voice_name = "ko-KR-Neural2-C"  # Neural2 남성 음성 (PM 중후한 목소리)
            pitch = -5.0  # 매우 낮은 톤 (중후함)
            speaking_rate = 0.85  # 느린 속도 (안정감)
        else:
            voice_name = "ko-KR-Neural2-A"  # Neural2 여성 음성 (더 자연스러움)
            pitch = 2.0  # 적당히 높은 톤
            speaking_rate = 1.0  # 보통 속도
        
        # Google Cloud TTS API 요청
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
        
        payload = {
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": "ko-KR",
                "name": voice_name
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "pitch": pitch,
                "speakingRate": speaking_rate,
                "volumeGainDb": 0.0,
                "effectsProfileId": ["headphone-class-device"]  # 헤드폰 최적화
            }
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"Google TTS API 오류: {response.text}")
        
        # Base64 인코딩된 오디오 데이터 반환
        audio_content = response.json().get('audioContent', '')
        
        return {
            "audioContent": audio_content,
            "character": character,
            "voice": voice_name
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"TTS 오류 상세: {str(e)}")
        print(f"TTS 오류 스택: {error_trace}")
        raise HTTPException(status_code=500, detail=f"TTS 생성 실패: {str(e)}")

@app.post("/api/timetables/auto-generate")
async def auto_generate_timetables(data: dict):
    """스마트 시간표 자동 생성 (과정별 요일 배정 기반)
    
    Args:
        course_code: 과정 코드
        start_date: 시작일
        lecture_hours: 이론 시간
        project_hours: 프로젝트 시간
        workship_hours: 현장실습 시간
        morning_hours: 오전 시간 (기본 4)
        afternoon_hours: 오후 시간 (기본 4)
    
    Note:
        - course_subjects 테이블의 day_of_week, week_type을 기반으로 시간표 생성
        - 예: 월요일=G-002, 금요일(홀수주)=G-001, 금요일(짝수주)=G-003
    """
    conn = get_db_connection()
    try:
        course_code = data['course_code']
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        lecture_hours = data['lecture_hours']
        project_hours = data['project_hours']
        workship_hours = data['workship_hours']
        morning_hours = data.get('morning_hours', 4)
        afternoon_hours = data.get('afternoon_hours', 4)
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 기존 시간표 삭제
        cursor.execute("DELETE FROM timetables WHERE course_code = %s", (course_code,))
        
        # 공휴일 목록 가져오기
        cursor.execute("SELECT holiday_date FROM holidays ORDER BY holiday_date")
        holidays = [row['holiday_date'] for row in cursor.fetchall()]
        
        # 과정별 요일 배정 정보 가져오기 (subjects 테이블의 day_of_week 사용)
        cursor.execute("""
            SELECT cs.subject_code, s.day_of_week, s.is_biweekly, s.week_offset,
                   s.name, s.hours, s.main_instructor
            FROM course_subjects cs
            JOIN subjects s ON cs.subject_code = s.code
            WHERE cs.course_code = %s
            ORDER BY s.day_of_week, s.week_offset
        """, (course_code,))
        course_subject_assignments = cursor.fetchall()
        
        # 요일별 교과목 매핑 생성 (day_of_week -> [(subject_code, week_type), ...])
        day_subject_map = {}
        for assignment in course_subject_assignments:
            day = assignment['day_of_week']
            if day is None:
                continue
            
            if day not in day_subject_map:
                day_subject_map[day] = []
            
            day_subject_map[day].append({
                'subject_code': assignment['subject_code'],
                'is_biweekly': assignment['is_biweekly'],
                'week_offset': assignment['week_offset'],
                'name': assignment['name'],
                'hours': assignment['hours'],
                'instructor': assignment['main_instructor']
            })
        
        # 주강사 추출
        course_instructors = []
        seen_instructors = set()
        for assignment in course_subject_assignments:
            instructor = assignment['main_instructor']
            if instructor and instructor not in seen_instructors:
                course_instructors.append(instructor)
                seen_instructors.add(instructor)
        
        if not course_instructors:
            cursor.execute("""
                SELECT code FROM instructors 
                WHERE instructor_type = '주강사' 
                ORDER BY code 
                LIMIT 3
            """)
            course_instructors = [row['code'] for row in cursor.fetchall()]
        
        print(f"📋 과정 {course_code}의 요일별 배정:")
        for day, subjects in sorted(day_subject_map.items()):
            # day_of_week는 1(월) ~ 5(금)이므로 -1 해야 함
            day_name = ['월', '화', '수', '목', '금'][day - 1] if 1 <= day <= 5 else f"[{day}]"
            for subj in subjects:
                week_info = f" ({'짝수' if subj['week_offset'] == 0 else '홀수'}주)" if subj['is_biweekly'] else ""
                print(f"  {day_name}{week_info}: {subj['subject_code']} - {subj['name']}")
        
        # 헬퍼 함수
        def is_weekend(date_obj):
            return date_obj.weekday() >= 5
        
        def is_holiday(date_obj):
            return date_obj in holidays
        
        def get_week_number(date_obj, start_date):
            """과정 시작일로부터 몇 주차인지 계산 (0부터 시작)"""
            days_diff = (date_obj - start_date).days
            return days_diff // 7
        
        timetables = []
        current_date = start_date
        
        # 각 교과목별 남은 시간 추적
        subject_remaining = {}
        for assignment in course_subject_assignments:
            subject_remaining[assignment['subject_code']] = assignment['hours']
        
        # 1단계: 이론 (lecture) - 과정별 요일 배정 기반
        total_remaining = lecture_hours
        MAX_ITERATIONS = 500
        iteration_count = 0
        afternoon_slot_available = False  # 오후 슬롯 사용 가능 여부
        
        while total_remaining > 0 and iteration_count < MAX_ITERATIONS:
            iteration_count += 1
            
            if is_weekend(current_date) or is_holiday(current_date):
                current_date += timedelta(days=1)
                afternoon_slot_available = False
                continue
            
            # 오늘 요일에 배정된 교과목 찾기
            # subjects 테이블의 day_of_week는 1(월)~7(일)이므로 weekday()+1로 변환
            today_weekday = current_date.weekday() + 1  # 0(월)~6(일) → 1(월)~7(일)
            if today_weekday not in day_subject_map:
                current_date += timedelta(days=1)
                afternoon_slot_available = False
                continue
            
            week_number = get_week_number(current_date, start_date)
            
            # 오늘 수업 가능한 교과목 필터링
            available_subjects = []
            for subj in day_subject_map[today_weekday]:
                # 격주 체크 (is_biweekly=1이면 격주, week_offset으로 짝수주/홀수주 구분)
                if subj['is_biweekly']:
                    if (week_number % 2) != subj['week_offset']:
                        continue
                # ★★★ 핵심: 남은 시간이 0보다 큰 교과목만 선택 ★★★
                if subject_remaining.get(subj['subject_code'], 0) > 0:
                    available_subjects.append(subj)
            
            # ★★★ 핵심: 해당 요일 배정 과목이 모두 소진되면 다른 과목으로 채우기 ★★★
            if not available_subjects:
                # 모든 교과목이 소진되었는지 확인
                all_subjects_exhausted = all(hours <= 0 for hours in subject_remaining.values())
                if all_subjects_exhausted and total_remaining <= 0:
                    # 이론 완전 종료
                    break
                
                # 해당 요일 과목은 소진되었지만, 다른 과목이 남아있으면 채우기
                if total_remaining > 0:
                    # 전체 교과목 중 남은 시수가 있는 과목 찾기
                    for assignment in course_subject_assignments:
                        if subject_remaining.get(assignment['subject_code'], 0) > 0:
                            available_subjects.append({
                                'subject_code': assignment['subject_code'],
                                'is_biweekly': 0,  # 요일 배정 무시
                                'week_offset': 0,
                                'name': assignment['name'],
                                'hours': assignment['hours'],
                                'instructor': assignment['main_instructor']
                            })
                    
                    # 여전히 과목이 없으면 다음날로
                    if not available_subjects:
                        current_date += timedelta(days=1)
                        afternoon_slot_available = False
                        continue
                else:
                    current_date += timedelta(days=1)
                    afternoon_slot_available = False
                    continue
            
            # 남은 시수가 많은 순으로 정렬
            available_subjects.sort(key=lambda s: subject_remaining.get(s['subject_code'], 0), reverse=True)
            
            # 오전 슬롯
            if total_remaining > 0 and available_subjects:
                subj = available_subjects[0]  # 남은 시수가 가장 많은 교과목
                hours_to_use = min(morning_hours, subject_remaining[subj['subject_code']], total_remaining)
                
                timetables.append({
                    'course_code': course_code,
                    'subject_code': subj['subject_code'],
                    'class_date': current_date,
                    'start_time': '09:00:00',
                    'end_time': f'{9 + int(hours_to_use):02d}:00:00',
                    'instructor_code': subj['instructor'],
                    'type': 'lecture'
                })
                
                subject_remaining[subj['subject_code']] -= hours_to_use
                total_remaining -= hours_to_use
                
                # ★★★ 핵심: 이론이 오전에 완전히 끝났는지 체크 ★★★
                if total_remaining <= 0:
                    # 이론이 오전에 끝남 → 오후부터 프로젝트 시작
                    afternoon_slot_available = True
                    break
            
            # 오후 슬롯 - 이론이 아직 남아있는 경우에만
            if total_remaining > 0:
                # ★★★ 1일 1과목 원칙: 오전 과목이 남아있으면 계속, 소진되었으면 다른 과목 ★★★
                afternoon_subject = None
                
                # 1. 오전에 사용한 과목이 아직 남아있는지 확인
                morning_subject_code = subj['subject_code'] if 'subj' in locals() else None
                if morning_subject_code and subject_remaining.get(morning_subject_code, 0) > 0:
                    # 오전 과목이 남아있으면 계속 사용
                    afternoon_subject = subj
                else:
                    # 2. 오전 과목이 소진되었으면 다른 과목 선택 (요일 배정 무시)
                    afternoon_available = []
                    for assignment in course_subject_assignments:
                        if subject_remaining.get(assignment['subject_code'], 0) > 0:
                            afternoon_available.append({
                                'subject_code': assignment['subject_code'],
                                'is_biweekly': 0,
                                'week_offset': 0,
                                'name': assignment['name'],
                                'hours': assignment['hours'],
                                'instructor': assignment['main_instructor']
                            })
                    
                    if afternoon_available:
                        # 남은 시수가 가장 많은 과목 선택
                        afternoon_available.sort(key=lambda s: subject_remaining.get(s['subject_code'], 0), reverse=True)
                        afternoon_subject = afternoon_available[0]
                
                # 오후 슬롯 생성
                if afternoon_subject:
                    hours_to_use = min(afternoon_hours, subject_remaining[afternoon_subject['subject_code']], total_remaining)
                    
                    timetables.append({
                        'course_code': course_code,
                        'subject_code': afternoon_subject['subject_code'],
                        'class_date': current_date,
                        'start_time': '14:00:00',
                        'end_time': f'{14 + int(hours_to_use):02d}:00:00',
                        'instructor_code': afternoon_subject['instructor'],
                        'type': 'lecture'
                    })
                    
                    subject_remaining[afternoon_subject['subject_code']] -= hours_to_use
                    total_remaining -= hours_to_use
            
            # 다음날로 이동
            current_date += timedelta(days=1)
            afternoon_slot_available = False
        
        # 프로젝트/현장실습에서는 course_instructors를 그대로 사용
        instructor_idx = 0
        
        # 2단계: 프로젝트 (project)
        if project_hours > 0:
            remaining_hours = project_hours
            
            # 이론이 오전에 끝나고 오후가 비어있으면 같은 날 오후부터 시작
            if afternoon_slot_available and remaining_hours > 0:
                daily_instructor = course_instructors[instructor_idx % len(course_instructors)]
                hours_to_use = min(afternoon_hours, remaining_hours)
                timetables.append({
                    'course_code': course_code,
                    'subject_code': None,
                    'class_date': current_date,
                    'start_time': '14:00:00',
                    'end_time': f'{14 + int(hours_to_use):02d}:00:00',
                    'instructor_code': daily_instructor,
                    'type': 'project'
                })
                remaining_hours -= hours_to_use
                instructor_idx += 1
                current_date += timedelta(days=1)
                afternoon_slot_available = False
            
            while remaining_hours > 0:
                if is_weekend(current_date) or is_holiday(current_date):
                    current_date += timedelta(days=1)
                    continue
                
                daily_instructor = course_instructors[instructor_idx % len(course_instructors)]
                
                # 오전
                if remaining_hours > 0:
                    hours_to_use = min(morning_hours, remaining_hours)
                    timetables.append({
                        'course_code': course_code,
                        'subject_code': None,
                        'class_date': current_date,
                        'start_time': '09:00:00',
                        'end_time': f'{9 + int(hours_to_use):02d}:00:00',
                        'instructor_code': daily_instructor,
                        'type': 'project'
                    })
                    remaining_hours -= hours_to_use
                    
                    # ★★★ 핵심: 프로젝트가 오전에 완전히 끝났는지 체크 ★★★
                    if remaining_hours <= 0:
                        # 프로젝트가 오전에 끝남 → 오후부터 현장실습 시작
                        afternoon_slot_available = True
                        break
                
                # 오후 - 프로젝트가 아직 남아있는 경우에만
                if remaining_hours > 0:
                    hours_to_use = min(afternoon_hours, remaining_hours)
                    timetables.append({
                        'course_code': course_code,
                        'subject_code': None,
                        'class_date': current_date,
                        'start_time': '14:00:00',
                        'end_time': f'{14 + int(hours_to_use):02d}:00:00',
                        'instructor_code': daily_instructor,
                        'type': 'project'
                    })
                    remaining_hours -= hours_to_use
                
                instructor_idx += 1
                current_date += timedelta(days=1)
                afternoon_slot_available = False
        
        # 3단계: 현장실습 (workship)
        if workship_hours > 0:
            remaining_hours = workship_hours
            
            # 프로젝트가 오전에 끝나고 오후가 비어있으면 같은 날 오후부터 시작
            if afternoon_slot_available and remaining_hours > 0:
                daily_instructor = course_instructors[instructor_idx % len(course_instructors)]
                hours_to_use = min(afternoon_hours, remaining_hours)
                timetables.append({
                    'course_code': course_code,
                    'subject_code': None,
                    'class_date': current_date,
                    'start_time': '14:00:00',
                    'end_time': f'{14 + int(hours_to_use):02d}:00:00',
                    'instructor_code': daily_instructor,
                    'type': 'workship'
                })
                remaining_hours -= hours_to_use
                instructor_idx += 1
                current_date += timedelta(days=1)
            
            while remaining_hours > 0:
                if is_weekend(current_date) or is_holiday(current_date):
                    current_date += timedelta(days=1)
                    continue
                
                daily_instructor = course_instructors[instructor_idx % len(course_instructors)]
                
                # 오전
                if remaining_hours > 0:
                    hours_to_use = min(morning_hours, remaining_hours)
                    timetables.append({
                        'course_code': course_code,
                        'subject_code': None,
                        'class_date': current_date,
                        'start_time': '09:00:00',
                        'end_time': f'{9 + int(hours_to_use):02d}:00:00',
                        'instructor_code': daily_instructor,
                        'type': 'workship'
                    })
                    remaining_hours -= hours_to_use
                
                # 오후
                if remaining_hours > 0:
                    hours_to_use = min(afternoon_hours, remaining_hours)
                    timetables.append({
                        'course_code': course_code,
                        'subject_code': None,
                        'class_date': current_date,
                        'start_time': '14:00:00',
                        'end_time': f'{14 + int(hours_to_use):02d}:00:00',
                        'instructor_code': daily_instructor,
                        'type': 'workship'
                    })
                    remaining_hours -= hours_to_use
                
                instructor_idx += 1
                current_date += timedelta(days=1)
        
        # DB에 삽입
        insert_query = """
            INSERT INTO timetables 
            (course_code, subject_code, class_date, start_time, end_time, 
             instructor_code, type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for tt in timetables:
            cursor.execute(insert_query, (
                tt['course_code'],
                tt['subject_code'],
                tt['class_date'],
                tt['start_time'],
                tt['end_time'],
                tt['instructor_code'],
                tt['type']
            ))
        
        conn.commit()
        
        return {
            "success": True,
            "generated_count": len(timetables),
            "message": f"{len(timetables)}개의 시간표가 생성되었습니다."
        }
        
    except Exception as e:
        conn.rollback()
        import traceback
        print(f"시간표 자동 생성 오류: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"시간표 자동 생성 실패: {str(e)}")
    finally:
        conn.close()


# ==================== DB 백업 API ====================

@app.post("/api/backup/create")
async def create_backup():
    """수동 DB 백업 생성"""
    import json
    from datetime import datetime, date, timedelta
    
    def convert_to_json_serializable(obj):
        """모든 객체를 JSON 직렬화 가능하게 변환"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif obj is None:
            return None
        return obj
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        backup_data = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 백업할 테이블 목록
        tables = [
            'timetables', 'training_logs', 'courses', 'subjects', 
            'instructors', 'students', 'course_subjects', 'holidays',
            'projects', 'class_notes', 'consultations', 'notices',
            'system_settings', 'team_activity_logs'
        ]
        
        total_records = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                serializable_rows = []
                for row in rows:
                    serializable_row = {k: convert_to_json_serializable(v) for k, v in row.items()}
                    serializable_rows.append(serializable_row)
                
                backup_data[table] = serializable_rows
                total_records += len(rows)
            except Exception as e:
                print(f"[WARN] {table} 백업 실패: {e}")
                backup_data[table] = []
        
        # 백업 디렉토리 생성
        backup_dir = '/home/user/webapp/backend/backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # JSON 파일로 저장
        backup_file = f'{backup_dir}/db_backup_{timestamp}.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        # 파일 크기 확인
        file_size = os.path.getsize(backup_file)
        
        return {
            "success": True,
            "backup_file": backup_file,
            "total_records": total_records,
            "file_size": file_size,
            "timestamp": timestamp,
            "tables": {table: len(backup_data[table]) for table in tables}
        }
        
    except Exception as e:
        import traceback
        print(f"[ERROR] 백업 생성 실패: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"백업 생성 실패: {str(e)}")
    finally:
        conn.close()


@app.get("/api/backup/list")
async def list_backups():
    """백업 파일 목록 조회"""
    import os
    import json
    
    backup_dir = '/home/user/webapp/backend/backups'
    
    try:
        if not os.path.exists(backup_dir):
            return {"backups": []}
        
        backups = []
        for filename in sorted(os.listdir(backup_dir), reverse=True):
            if filename.startswith('db_backup_') and filename.endswith('.json'):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                
                backups.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size": file_stat.st_size,
                    "created_at": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        return {"backups": backups}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백업 목록 조회 실패: {str(e)}")


@app.delete("/api/backup/delete/{filename}")
async def delete_backup(filename: str):
    """백업 파일 삭제"""
    import os
    
    backup_dir = '/home/user/webapp/backend/backups'
    filepath = os.path.join(backup_dir, filename)
    
    try:
        # 보안 체크
        if not filename.startswith('db_backup_') or not filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="잘못된 백업 파일명")
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="백업 파일이 없습니다")
        
        os.remove(filepath)
        return {"success": True, "message": f"{filename} 삭제 완료"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백업 삭제 실패: {str(e)}")


@app.post("/api/backup/auto-cleanup")
async def auto_cleanup_backups(keep_days: int = 7):
    """오래된 백업 자동 삭제 (keep_days일 이전 백업)"""
    import os
    from datetime import datetime, timedelta
    
    backup_dir = '/home/user/webapp/backend/backups'
    
    try:
        if not os.path.exists(backup_dir):
            return {"deleted_count": 0, "message": "백업 디렉토리 없음"}
        
        cutoff_time = datetime.now() - timedelta(days=keep_days)
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('db_backup_') and filename.endswith('.json'):
                filepath = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1
                    print(f"🗑️ 삭제: {filename}")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "keep_days": keep_days,
            "message": f"{keep_days}일 이전 백업 {deleted_count}개 삭제 완료"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자동 정리 실패: {str(e)}")

@app.get("/api/backup/download/{filename}")
async def download_backup(filename: str):
    """백업 파일 다운로드"""
    import os
    from fastapi.responses import FileResponse
    
    backup_dir = '/home/user/webapp/backend/backups'
    filepath = os.path.join(backup_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="백업 파일을 찾을 수 없습니다")
    
    if not filename.startswith('db_backup_'):
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다")
    
    return FileResponse(
        filepath,
        media_type='application/json',
        filename=filename
    )

@app.post("/api/backup/restore/{filename}")
async def restore_backup(filename: str):
    """백업 파일로 데이터베이스 복원"""
    import os
    import json
    from datetime import datetime
    
    backup_dir = '/home/user/webapp/backend/backups'
    filepath = os.path.join(backup_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="백업 파일을 찾을 수 없습니다")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
    
    cursor = conn.cursor()
    
    try:
        # 백업 파일 읽기
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        restored_records = 0
        
        # 각 테이블별로 복원
        for table_name, records in backup_data.items():
            if not records:
                continue
            
            try:
                # 기존 데이터 삭제
                cursor.execute(f"DELETE FROM {table_name}")
                
                # 데이터 삽입
                for record in records:
                    columns = ', '.join(record.keys())
                    placeholders = ', '.join(['%s'] * len(record))
                    values = tuple(record.values())
                    
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
                    restored_records += 1
                
                print(f"✅ {table_name}: {len(records)}개 복원")
            
            except Exception as table_error:
                print(f"⚠️ {table_name} 복원 오류: {str(table_error)}")
                continue
        
        conn.commit()
        
        return {
            "success": True,
            "restored_records": restored_records,
            "backup_file": filename,
            "message": f"백업 복원 완료: {restored_records}개 레코드"
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"복원 실패: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

@app.get("/api/backup/export")
async def export_database():
    """전체 데이터베이스 JSON으로 내보내기"""
    import json
    from datetime import datetime
    from fastapi.responses import StreamingResponse
    import io
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 전체 테이블 목록 조회
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        
        export_data = {}
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                records = cursor.fetchall()
                
                # datetime 객체를 문자열로 변환
                for record in records:
                    for key, value in record.items():
                        if isinstance(value, datetime):
                            record[key] = value.isoformat()
                
                export_data[table] = records
                print(f"✅ {table}: {len(records)}개 레코드")
            
            except Exception as table_error:
                print(f"⚠️ {table} 읽기 오류: {str(table_error)}")
                continue
        
        # JSON 문자열 생성
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        json_bytes = json_str.encode('utf-8')
        
        # StreamingResponse로 반환
        return StreamingResponse(
            io.BytesIO(json_bytes),
            media_type='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=db_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"내보내기 실패: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

@app.post("/api/backup/import")
async def import_database(file: UploadFile = File(...)):
    """JSON 파일로 데이터베이스 불러오기"""
    import json
    from datetime import datetime
    
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="JSON 파일만 업로드 가능합니다")
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
    
    cursor = conn.cursor()
    
    try:
        # 업로드된 파일 읽기
        content = await file.read()
        import_data = json.loads(content.decode('utf-8'))
        
        imported_records = 0
        
        # 각 테이블별로 불러오기
        for table_name, records in import_data.items():
            if not records:
                continue
            
            try:
                # 기존 데이터 삭제
                cursor.execute(f"DELETE FROM {table_name}")
                
                # 데이터 삽입
                for record in records:
                    columns = ', '.join(record.keys())
                    placeholders = ', '.join(['%s'] * len(record))
                    values = tuple(record.values())
                    
                    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, values)
                    imported_records += 1
                
                print(f"✅ {table_name}: {len(records)}개 불러오기")
            
            except Exception as table_error:
                print(f"⚠️ {table_name} 불러오기 오류: {str(table_error)}")
                continue
        
        conn.commit()
        
        return {
            "success": True,
            "imported_records": imported_records,
            "filename": file.filename,
            "message": f"데이터베이스 불러오기 완료: {imported_records}개 레코드"
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="잘못된 JSON 형식입니다")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"불러오기 실패: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

@app.post("/api/backup/reset")
async def reset_database(request: Request, data: dict):
    """DB 초기화 (자동 백업 후 진행, 비밀번호 확인 + 로그 기록)"""
    import os
    from datetime import datetime
    
    # 작업자 정보 확인
    operator_name = data.get('operator_name', '').strip()
    password = data.get('password', '').strip()
    
    # 체크박스 옵션
    delete_instructors = data.get('delete_instructors', False)
    delete_backups = data.get('delete_backups', False)
    delete_courses = data.get('delete_courses', False)
    
    if not operator_name or not password:
        raise HTTPException(status_code=400, detail="작업자 이름과 비밀번호가 필요합니다")
    
    client_ip = request.client.host if request.client else 'unknown'
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # db_management_logs 테이블 확인/생성
        ensure_db_management_logs_table(cursor)
        conn.commit()
        
        # 0단계: 강사 인증 확인
        cursor.execute("SELECT code, name, password FROM instructor_codes WHERE name = %s", (operator_name,))
        instructor = cursor.fetchone()
        
        if not instructor:
            raise HTTPException(status_code=401, detail="등록되지 않은 강사입니다")
        
        if instructor['password'] != password:
            # 실패 로그 기록
            cursor.execute("""
                INSERT INTO db_management_logs
                (action_type, operator_name, action_result, backup_file, details, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('reset', f"{operator_name} ({instructor['code']})", 'fail', '', '비밀번호 불일치', client_ip))
            conn.commit()
            raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")
        
        print(f"✅ 강사 인증 완료: {operator_name} ({instructor['code']})")
        
        # 1단계: 자동 백업 생성
        print("📦 DB 초기화 전 자동 백업 생성 중...")
        backup_response = await create_backup()
        
        if not backup_response.get('success'):
            raise HTTPException(status_code=500, detail="백업 생성 실패로 초기화를 중단합니다")
        
        backup_file = backup_response.get('filename', '')
        print(f"✅ 백업 완료: {backup_file}")
        
        # 2단계: 초기화할 테이블 목록
        tables_to_clear = [
            'students',              # 학생
            'timetables',           # 시간표
            'training_logs',        # 훈련일지
            'class_notes',          # 수업노트
            'consultations',        # 상담 (counselings 아님!)
            'notices',              # 공지사항
            'projects',             # 프로젝트
            'team_activity_logs',   # 팀활동일지
            'course_subjects',      # 과목
            'student_registrations' # 신규가입신청
        ]
        
        reset_details = []
        
        # 강사 정보 삭제 옵션
        if delete_instructors:
            tables_to_clear.extend(['instructors'])
            reset_details.append('강사 정보 삭제 (Root 제외)')
        
        # 과정 정보 삭제 옵션
        if delete_courses:
            tables_to_clear.append('courses')
            reset_details.append('과정 정보 삭제')
        
        # 백업 삭제 옵션 (DB가 아닌 파일 시스템)
        if delete_backups:
            reset_details.append('백업 파일 삭제')
        
        reset_type = '일반 초기화' if not reset_details else f"맞춤 초기화 ({', '.join(reset_details)})"
        print(f"⚠️ 초기화 모드: {reset_type}")
        
        deleted_records = {}
        total_deleted = 0
        
        # 강사 정보 삭제 (Root 제외)
        if delete_instructors:
            print("🗑️ instructor_codes: Root 계정 제외하고 삭제 중...")
            cursor.execute("SELECT COUNT(*) as count FROM instructor_codes WHERE name != 'root'")
            ic_count = cursor.fetchone()['count']
            cursor.execute("DELETE FROM instructor_codes WHERE name != 'root'")
            deleted_records['instructor_codes'] = ic_count
            total_deleted += ic_count
            print(f"🗑️ instructor_codes: {ic_count}개 삭제 (Root 계정 유지)")
        
        # 3단계: 각 테이블 초기화
        for table in tables_to_clear:
            try:
                # 테이블 존재 여부 확인
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if not cursor.fetchone():
                    print(f"⚠️ {table}: 테이블이 존재하지 않음 (스킵)")
                    deleted_records[table] = 0
                    continue
                
                # 현재 레코드 수 확인
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                
                # 테이블 데이터 삭제
                cursor.execute(f"DELETE FROM {table}")
                
                deleted_records[table] = count
                total_deleted += count
                print(f"🗑️ {table}: {count}개 삭제")
                
            except Exception as table_error:
                print(f"⚠️ {table} 초기화 오류: {str(table_error)}")
                deleted_records[table] = 0
                continue
        
        # 백업 파일 삭제
        if delete_backups:
            try:
                backup_dir = 'backups'
                if os.path.exists(backup_dir):
                    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
                    for f in backup_files:
                        os.remove(os.path.join(backup_dir, f))
                    deleted_records['backup_files'] = len(backup_files)
                    print(f"🗑️ 백업 파일: {len(backup_files)}개 삭제")
                else:
                    deleted_records['backup_files'] = 0
            except Exception as backup_error:
                print(f"⚠️ 백업 파일 삭제 오류: {str(backup_error)}")
                deleted_records['backup_files'] = 0
        
        conn.commit()
        
        # 4단계: 성공 로그 기록
        cursor.execute("""
            INSERT INTO db_management_logs
            (action_type, operator_name, action_result, backup_file, details, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'reset',
            f"{operator_name} ({instructor['code']})",
            'success',
            backup_file,
            f"{reset_type}: 총 {total_deleted}개 레코드 삭제. 테이블: {', '.join(tables_to_clear)}",
            client_ip
        ))
        conn.commit()
        
        print(f"✅ DB 초기화 완료: 총 {total_deleted}개 레코드 삭제 ({reset_type})")
        
        return {
            "success": True,
            "backup_file": backup_file,
            "deleted_records": deleted_records,
            "total_deleted": total_deleted,
            "reset_type": reset_type,
            "operator": f"{operator_name} ({instructor['code']})",
            "message": f"DB {reset_type} 완료: {total_deleted}개 레코드 삭제"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        
        # 실패 로그 기록
        try:
            cursor.execute("""
                INSERT INTO db_management_logs
                (action_type, operator_name, action_result, backup_file, details, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('reset', operator_name, 'fail', backup_file if 'backup_file' in locals() else '', str(e), client_ip))
            conn.commit()
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"DB 초기화 실패: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

@app.get("/api/backup/tables-info")
async def get_tables_info():
    """현재 DB 테이블 정보 조회"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
    
    cursor = conn.cursor()
    
    try:
        tables_info = []
        
        # 초기화 가능한 테이블 목록
        tables = [
            ('students', '학생'),
            ('timetables', '시간표'),
            ('training_logs', '훈련일지'),
            ('class_notes', '수업노트'),
            ('counselings', '상담'),
            ('notices', '공지사항'),
            ('projects', '프로젝트'),
            ('team_activity_logs', '팀활동일지'),
            ('course_subjects', '과목'),
            ('student_registrations', '신규가입신청')
        ]
        
        for table_name, korean_name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()[0]
                
                tables_info.append({
                    "table": table_name,
                    "name": korean_name,
                    "count": count
                })
            except:
                continue
        
        return {
            "success": True,
            "tables": tables_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"테이블 정보 조회 실패: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

@app.get("/api/backup/logs")
async def get_management_logs(limit: int = 50):
    """DB 관리 로그 조회"""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=503, detail="데이터베이스 연결 실패")
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT * FROM db_management_logs 
            ORDER BY created_at DESC 
            LIMIT %s
        """, (limit,))
        
        logs = cursor.fetchall()
        
        return {
            "success": True,
            "logs": logs,
            "total": len(logs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그 조회 실패: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

# ==================== DB 관리 로그 테이블 ====================
def ensure_db_management_logs_table():
    """DB 관리 로그 테이블 생성 (없으면)"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS db_management_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                action_type VARCHAR(50) NOT NULL COMMENT '작업 유형 (reset/restore/backup)',
                operator_name VARCHAR(100) NOT NULL COMMENT '작업자 이름',
                action_result VARCHAR(20) NOT NULL COMMENT '결과 (success/fail)',
                backup_file VARCHAR(255) COMMENT '백업 파일명',
                details TEXT COMMENT '상세 내용',
                ip_address VARCHAR(45) COMMENT 'IP 주소',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '작업 시간',
                INDEX idx_action_type (action_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='DB 관리 로그'
        """)
        conn.commit()
        print("[OK] db_management_logs 테이블 확인/생성 완료")
    except Exception as e:
        print(f"[WARN] db_management_logs 테이블 생성 오류: {e}")
    finally:
        conn.close()

# 서버 시작 시 테이블 확인
ensure_db_management_logs_table()

if __name__ == "__main__":
    import uvicorn
    # 파일 업로드 크기 제한 100MB로 증가
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        limit_max_requests=10000,
        timeout_keep_alive=300
    )


# ============================================
# RAG (Retrieval-Augmented Generation) API
# ============================================

from rag.document_loader import DocumentLoader
from rag.vector_store import VectorStoreManager
from rag.rag_chain import RAGChain
import shutil
from typing import Optional

# RAG 전역 인스턴스 (지연 로딩)
vector_store_manager = None
document_loader = None
rag_initialized = False  # RAG 초기화 상태

# RAG 인덱싱 진행률 추적 (디스크에 영구 저장)
PROGRESS_FILE = Path("./backend/indexing_progress.json")

def load_indexing_progress():
    """디스크에서 진행률 복원"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[INFO] 복원된 진행률 정보: {len(data)}개 항목")
                # 오래된 완료 항목은 자동 정리 (1시간 이상)
                cleaned = {}
                for k, v in data.items():
                    if v.get('status') == 'completed':
                        started = v.get('started_at', '')
                        if started:
                            from datetime import datetime, timedelta
                            started_time = datetime.fromisoformat(started)
                            if datetime.now() - started_time < timedelta(hours=1):
                                cleaned[k] = v
                    else:
                        cleaned[k] = v
                return cleaned
        except Exception as e:
            print(f"[WARN] 진행률 로드 실패: {e}")
            return {}
    return {}

def save_indexing_progress(progress_dict):
    """디스크에 진행률 저장"""
    try:
        PROGRESS_FILE.parent.mkdir(exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] 진행률 저장 실패: {e}")

# 서버 시작 시 진행률 복원
indexing_progress = load_indexing_progress()

def init_rag():
    """RAG 시스템 초기화 (지연 로딩)"""
    global vector_store_manager, document_loader, rag_initialized
    
    if rag_initialized:
        print("[INFO] RAG 시스템 이미 초기화됨")
        return True
    
    print("[INFO] 🔄 RAG 시스템 초기화 중... (한국어 임베딩 모델 로딩)")
    
    try:
        # 문서 로더 초기화
        document_loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
        
        # 벡터 DB 경로 (절대 경로로 통일)
        from pathlib import Path
        project_root = Path(__file__).parent.parent  # /home/user/webapp
        vector_db_path = project_root / "backend" / "vector_db"
        vector_db_path.mkdir(exist_ok=True, parents=True)
        
        # 벡터 스토어 초기화
        print("[INFO] 📥 임베딩 모델 다운로드 중 (최초 1회만, 약 10-20초 소요)")
        vector_store_manager = VectorStoreManager(
            persist_directory=str(vector_db_path),
            collection_name="biohealth_docs"
        )
        
        rag_initialized = True
        print("[OK] ✅ RAG 시스템 초기화 완료")
        print(f"[DOC] 저장된 문서 수: {vector_store_manager.count_documents()}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] ❌ RAG 시스템 초기화 실패: {e}")
        print("[WARN] RAG 기능을 사용하려면 필요한 패키지를 설치하세요:")
        print("   pip install -r requirements_rag.txt")
        return False


def load_default_documents():
    """documents 폴더의 기본 문서들을 RAG에 자동 로드 (중복 체크)"""
    global vector_store_manager, document_loader
    
    if not vector_store_manager or not document_loader:
        print("[WARN] RAG 시스템이 초기화되지 않아 기본 문서를 로드할 수 없습니다")
        return
    
    # 이미 문서가 있으면 건너뛰기
    current_doc_count = vector_store_manager.count_documents()
    if current_doc_count > 0:
        print(f"[INFO] 이미 {current_doc_count}개 문서가 저장되어 있습니다. 자동 로드 건너뜀")
        return
    
    documents_dir = Path("./documents")
    
    # documents 폴더가 없으면 생성
    if not documents_dir.exists():
        documents_dir.mkdir(parents=True)
        print("[INFO] documents 폴더가 생성되었습니다")
        return
    
    # 지원하는 파일 형식
    supported_extensions = ['.pdf', '.docx', '.doc', '.txt']
    
    # documents 폴더의 모든 파일 검색
    doc_files = []
    for ext in supported_extensions:
        doc_files.extend(documents_dir.glob(f'*{ext}'))
    
    if not doc_files:
        print("[INFO] documents 폴더에 문서가 없습니다")
        print("[TIP] 교재 및 교육자료를 documents 폴더에 넣어주세요")
        return
    
    print(f"\n[DOC] 기본 문서 자동 로드 시작 ({len(doc_files)}개 파일)")
    print("=" * 60)
    
    loaded_count = 0
    skipped_count = 0
    
    for doc_path in doc_files:
        try:
            # 파일명에서 메타데이터 추출
            filename = doc_path.stem
            parts = filename.split('_')
            
            metadata = {
                'original_filename': doc_path.name,
                'upload_date': datetime.now().strftime('%Y-%m-%d'),
                'file_size': doc_path.stat().st_size,
                'auto_loaded': True
            }
            
            # 파일명에서 과목, 강사명 등 추출 시도
            if len(parts) >= 2:
                metadata['subject'] = parts[1] if len(parts) > 1 else ''
                metadata['instructor'] = parts[2] if len(parts) > 2 else ''
            
            # 문서 로드
            documents = document_loader.load_document(str(doc_path), metadata)
            
            if not documents:
                print(f"[WARN] {doc_path.name}: 텍스트를 추출할 수 없습니다")
                skipped_count += 1
                continue
            
            # 텍스트와 메타데이터 분리
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # 벡터 스토어에 추가
            doc_ids = vector_store_manager.add_documents(texts, metadatas)
            
            print(f"[OK] {doc_path.name}: {len(documents)}개 청크 로드 완료")
            loaded_count += 1
            
        except Exception as e:
            print(f"[ERROR] {doc_path.name}: 로드 실패 - {str(e)}")
            skipped_count += 1
    
    print("=" * 60)
    print(f"[STAT] 기본 문서 로드 완료: {loaded_count}개 성공, {skipped_count}개 실패")
    print(f"[DOC] 현재 총 문서 수: {vector_store_manager.count_documents()}")
    print()


# 앱 시작 시 RAG 초기화
try:
    init_rag()
except:
    print("[WARN] RAG 초기화 실패 - RAG 기능 비활성화됨")


# ==================== Startup 이벤트 ====================
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    print("\n" + "="*60)
    print("🚀 BH2025 WOWU 백엔드 서버 시작")
    print("="*60)
    
    # 등록된 라우트 확인
    print("\n📋 등록된 API 엔드포인트:")
    doc_routes = []
    rag_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            if '/api/documents' in route.path:
                doc_routes.append(f"  {', '.join(route.methods)} {route.path}")
            elif '/api/rag' in route.path:
                rag_routes.append(f"  {', '.join(route.methods)} {route.path}")
    
    if doc_routes:
        print("\n📁 Documents API:")
        for r in sorted(doc_routes):
            print(r)
    else:
        print("\n⚠️  Documents API: 등록된 엔드포인트 없음!")
    
    if rag_routes:
        print("\n🤖 RAG API:")
        for r in sorted(rag_routes):
            print(r)
    else:
        print("\n⚠️  RAG API: 등록된 엔드포인트 없음!")
    
    print("\n" + "="*60)
    print("✅ 서버 URL: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("="*60 + "\n")


@app.post("/api/rag/upload")
async def upload_rag_document(
    file: UploadFile = File(...),
    subject: Optional[str] = Form(None),
    instructor: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """
    RAG 문서 업로드
    
    - PDF, DOCX, TXT 파일 지원
    - 자동으로 벡터 DB에 저장
    """
    if not vector_store_manager or not document_loader:
        raise HTTPException(status_code=503, detail="RAG 시스템이 초기화되지 않았습니다")
    
    # 파일 확장자 확인
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
        raise HTTPException(
            status_code=400, 
            detail="지원하지 않는 파일 형식입니다. PDF, DOCX, TXT 파일만 업로드 가능합니다."
        )
    
    # 파일 크기 확인 (50MB 제한)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=400, detail="파일 크기는 50MB 이하여야 합니다")
    
    try:
        # 파일 저장
        upload_dir = Path("./backend/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # 고유 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        print(f"📁 파일 저장 완료: {file_path}")
        
        # 메타데이터 구성
        metadata = {
            "original_filename": file.filename,
            "upload_date": datetime.now().isoformat(),
            "file_size": file_size,
            "subject": subject or "미지정",
            "instructor": instructor or "미지정",
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "description": description or ""
        }
        
        # 문서 로드 및 청킹
        print(f"📝 문서 처리 중: {file.filename}")
        documents = document_loader.load_document(str(file_path), metadata)
        
        if not documents:
            raise HTTPException(status_code=400, detail="문서에서 텍스트를 추출할 수 없습니다")
        
        # 벡터 DB에 저장
        print(f"💾 벡터 DB에 저장 중...")
        
        # Document 객체를 텍스트와 메타데이터로 분리
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        doc_ids = vector_store_manager.add_documents(texts, metadatas)
        
        return {
            "success": True,
            "message": "문서가 성공적으로 업로드되었습니다",
            "filename": file.filename,
            "file_path": str(file_path),
            "chunks_count": len(documents),
            "document_ids": doc_ids,
            "metadata": metadata
        }
        
    except Exception as e:
        print(f"[ERROR] 문서 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"문서 업로드 실패: {str(e)}")


@app.get("/api/rag/documents")
async def list_rag_documents(limit: int = 100):
    """RAG 문서 목록 조회"""
    if not vector_store_manager:
        raise HTTPException(status_code=503, detail="RAG 시스템이 초기화되지 않았습니다")
    
    try:
        documents = vector_store_manager.get_all_documents()
        count = vector_store_manager.count_documents()
        
        # 중복 제거 (원본 파일명 기준)
        unique_docs = {}
        for doc in documents:
            metadata = doc.get('metadata', {})
            filename = metadata.get('filename', metadata.get('source', '알 수 없음'))
            if filename not in unique_docs:
                unique_docs[filename] = {
                    'filename': filename,
                    'document_id': metadata.get('document_id', ''),
                    'uploaded_at': metadata.get('uploaded_at', ''),
                    'chunks_count': 1
                }
            else:
                unique_docs[filename]['chunks_count'] += 1
        
        return {
            "success": True,
            "total_chunks": count,
            "unique_documents": len(unique_docs),
            "documents": list(unique_docs.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 실패: {str(e)}")


@app.post("/api/rag/chat")
async def rag_chat(request: Request):
    """
    RAG 기반 채팅 (개선된 버전)
    
    Body:
        - message: 사용자 질문
        - k: 검색할 문서 수 (기본 5)
        - model: AI 모델 (groq, gemini, gemma)
        - document_context: 특정 문서로 제한 (선택, 파일명)
    
    특수 기능:
        - 통계/숫자 질문 감지 시 DB 직접 조회
        - 유사도 임계값 체크
        - 문서 특정 컨텍스트 지원
    """
    if not vector_store_manager:
        # RAG 시스템 지연 초기화
        print("[INFO] 첫 RAG 요청 - 시스템 초기화 중...")
        if not init_rag():
            raise HTTPException(status_code=503, detail="RAG 시스템 초기화에 실패했습니다. 서버 로그를 확인하세요.")
    
    try:
        data = await request.json()
        message = data.get('message', '').strip()
        k = data.get('k', 5)  # 기본값 3에서 5로 증가
        model = data.get('model', 'groq').lower()
        document_context = data.get('document_context', None)  # 특정 문서로 제한 (문자열 또는 배열)
        
        if not message:
            raise HTTPException(status_code=400, detail="메시지를 입력해주세요")
        
        # 문서 컨텍스트 정규화 (문자열 -> 배열)
        if document_context:
            if isinstance(document_context, str):
                document_context = [document_context]
            elif not isinstance(document_context, list):
                document_context = None
        
        # 문서 컨텍스트가 지정된 경우 메시지에 추가
        if document_context and len(document_context) > 0:
            doc_names = ', '.join(document_context)
            print(f"📄 문서 컨텍스트 ({len(document_context)}개): {doc_names}")
            message_with_context = f"[문서: {doc_names}에 대한 질문] {message}"
        else:
            message_with_context = message
            document_context = None
        
        # ==================== 통계/숫자 질문 감지 ====================
        message_lower = message.lower()
        
        # 강사 수 질문 감지
        if any(keyword in message_lower for keyword in ['강사', '강사수', '강사 수', '강사는', '강사 수는', '몇 명', '몇명', '인원']):
            if any(keyword in message_lower for keyword in ['수', '명', '얼마', '몇', '많', '인원']):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                    
                    # 강사 수 조회
                    cursor.execute("SELECT COUNT(*) as count FROM instructors")
                    result = cursor.fetchone()
                    instructor_count = result['count'] if result else 0
                    
                    # 강사 이름 목록 (상위 10명)
                    cursor.execute("""
                        SELECT name, email 
                        FROM instructors 
                        ORDER BY id 
                        LIMIT 10
                    """)
                    instructor_list = cursor.fetchall()
                    
                    conn.close()
                    
                    # 답변 생성
                    answer = f"현재 시스템에 등록된 강사 수는 **총 {instructor_count}명**입니다.\n\n"
                    
                    if instructor_list and len(instructor_list) > 0:
                        answer += "📋 **등록된 강사 (상위 10명):**\n"
                        for idx, instructor in enumerate(instructor_list, 1):
                            name = instructor.get('name', '이름없음')
                            email = instructor.get('email', '')
                            if email:
                                answer += f"{idx}. {name} ({email})\n"
                            else:
                                answer += f"{idx}. {name}\n"
                    
                    answer += "\n💡 *이 정보는 데이터베이스에서 실시간으로 조회되었습니다.*"
                    
                    return {
                        "success": True,
                        "model": "database",
                        "answer": answer,
                        "sources": [{
                            'source': 'instructors 테이블 (DB 직접 조회)',
                            'similarity': 1.0,
                            'content': f"총 강사 수: {instructor_count}명"
                        }],
                        "message": message,
                        "query_type": "statistics"
                    }
                except Exception as e:
                    print(f"[ERROR] 강사 수 조회 실패: {e}")
                    # 실패 시 RAG로 폴백
        
        # 학생 수 질문 감지
        if any(keyword in message_lower for keyword in ['학생', '학생수', '학생 수', '수강생', '훈련생']):
            if any(keyword in message_lower for keyword in ['수', '명', '얼마', '몇', '많', '인원']):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor(pymysql.cursors.DictCursor)
                    
                    cursor.execute("SELECT COUNT(*) as count FROM students")
                    result = cursor.fetchone()
                    student_count = result['count'] if result else 0
                    
                    # 과정별 통계
                    cursor.execute("""
                        SELECT course_code, COUNT(*) as count 
                        FROM students 
                        GROUP BY course_code 
                        ORDER BY count DESC 
                        LIMIT 5
                    """)
                    course_stats = cursor.fetchall()
                    
                    conn.close()
                    
                    answer = f"현재 시스템에 등록된 학생 수는 **총 {student_count}명**입니다.\n\n"
                    
                    if course_stats:
                        answer += "📊 **과정별 학생 수 (상위 5개):**\n"
                        for stat in course_stats:
                            answer += f"- {stat['course_code']}: {stat['count']}명\n"
                    
                    answer += "\n💡 *이 정보는 데이터베이스에서 실시간으로 조회되었습니다.*"
                    
                    return {
                        "success": True,
                        "model": "database",
                        "answer": answer,
                        "sources": [{
                            'source': 'students 테이블 (DB 직접 조회)',
                            'similarity': 1.0,
                            'content': f"총 학생 수: {student_count}명"
                        }],
                        "message": message,
                        "query_type": "statistics"
                    }
                except Exception as e:
                    print(f"[ERROR] 학생 수 조회 실패: {e}")
        
        # ==================== RAG 처리 ====================
        # API 키 가져오기 (DB → 헤더 → 환경변수 순서)
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT setting_key, setting_value FROM system_settings WHERE setting_key IN ('groq_api_key', 'gemini_api_key')")
        db_settings_list = cursor.fetchall()
        conn.close()
        
        db_settings = {item['setting_key']: item['setting_value'] for item in db_settings_list}
        
        groq_api_key = request.headers.get('X-GROQ-API-Key') or db_settings.get('groq_api_key', '') or os.getenv('GROQ_API_KEY', '')
        gemini_api_key = request.headers.get('X-Gemini-API-Key') or db_settings.get('gemini_api_key', '') or os.getenv('GOOGLE_CLOUD_TTS_API_KEY', '')
        
        # 모델에 따라 API 키 선택
        if model in ['groq', 'gemma']:
            api_key = groq_api_key
            api_type = 'groq'
        elif model == 'gemini':
            api_key = gemini_api_key
            api_type = 'gemini'
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 모델입니다")
        
        if not api_key:
            error_msg = f"{api_type.upper()} API 키가 설정되지 않았습니다. 시스템 설정에서 API 키를 입력해주세요."
            print(f"[ERROR] {error_msg}")
            raise HTTPException(
                status_code=400, 
                detail=error_msg
            )
        
        # RAG 체인 생성
        rag_chain = RAGChain(vector_store_manager, api_key, api_type)
        
        # RAG 질문 처리 (유사도 임계값 0.008 = 0.8%)
        print(f"💬 RAG 질문: {message_with_context if document_context else message}")
        result = await rag_chain.query(message_with_context if document_context else message, k=k, min_similarity=0.008)
        
        # 문서 컨텍스트가 지정된 경우 결과 필터링 (복수 문서 지원)
        if document_context and len(document_context) > 0:
            filtered_sources = []
            for source in result.get('sources', []):
                metadata = source.get('metadata', {})
                source_filename = metadata.get('filename', '') or metadata.get('original_filename', '')
                
                # 지정된 문서 목록에 포함되는 경우만 포함
                for doc_name in document_context:
                    if doc_name in source_filename or source_filename in doc_name:
                        filtered_sources.append(source)
                        break
            
            # 필터링된 소스가 있으면 사용, 없으면 모든 소스 사용
            if filtered_sources:
                result['sources'] = filtered_sources
                doc_names = ', '.join(document_context)
                print(f"📄 문서 필터링 ({len(document_context)}개): {len(filtered_sources)}/{len(result.get('sources', []))} 소스 사용")
            else:
                doc_names = ', '.join(document_context)
                print(f"⚠️ 문서 '{doc_names}'에서 관련 내용을 찾을 수 없어 전체 검색 결과를 사용합니다")
        
        return {
            "success": True,
            "model": model,
            "answer": result['answer'],
            "sources": result['sources'],
            "message": message,
            "document_context": document_context,
            "query_type": "rag"
        }
        
    except HTTPException as he:
        print(f"[ERROR] RAG 채팅 요청 실패: {he.detail}")
        raise he
    except Exception as e:
        print(f"[ERROR] RAG 채팅 실패: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"RAG 채팅 실패: {str(e)}")


@app.post("/api/rag/search")
async def rag_search(
    query: str = Form(...),
    k: int = Form(5),
    subject: Optional[str] = Form(None)
):
    """
    RAG 문서 검색
    
    - 질문과 유사한 문서 검색
    - 메타데이터 필터링 지원
    """
    if not vector_store_manager:
        # RAG 시스템 지연 초기화
        print("[INFO] 첫 RAG 요청 - 시스템 초기화 중...")
        if not init_rag():
            raise HTTPException(status_code=503, detail="RAG 시스템 초기화에 실패했습니다. 서버 로그를 확인하세요.")
    
    try:
        # 검색 (필터 없이)
        results = vector_store_manager.search_with_score(query, k=k)
        
        # 결과 포맷팅
        search_results = []
        for result in results:
            search_results.append({
                'content': result.get('content', ''),
                'similarity': float(result.get('score', 0)),
                'metadata': result.get('metadata', {})
            })
        
        return {
            "success": True,
            "query": query,
            "results_count": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 검색 실패: {str(e)}")


@app.delete("/api/rag/clear")
async def clear_rag_database():
    """RAG 데이터베이스 초기화 (모든 문서 삭제)"""
    if not vector_store_manager:
        raise HTTPException(status_code=503, detail="RAG 시스템이 초기화되지 않았습니다")
    
    try:
        old_count = vector_store_manager.count_documents()
        vector_store_manager.delete_collection()
        
        return {
            "success": True,
            "message": "RAG 데이터베이스가 초기화되었습니다",
            "deleted_chunks": old_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 초기화 실패: {str(e)}")


@app.get("/api/rag/status")
async def rag_status():
    """RAG 시스템 상태 확인"""
    global rag_initialized
    
    if not rag_initialized:
        return {
            "initialized": False,
            "loading": False,
            "message": "RAG 시스템이 아직 초기화되지 않았습니다. 첫 RAG 기능 사용 시 자동으로 초기화됩니다."
        }
    
    if not vector_store_manager:
        return {
            "initialized": False,
            "loading": True,
            "message": "한국어 임베딩 모델 로딩 중... (최초 1회만, 약 10-20초 소요)"
        }
    
    try:
        count = vector_store_manager.count_documents()
        
        return {
            "initialized": True,
            "loading": False,
            "document_count": count,
            "embedding_model": "jhgan/ko-sroberta-multitask",
            "collection_name": vector_store_manager.collection_name,
            "vector_db": "FAISS",
            "status": "정상"
        }
        
    except Exception as e:
        return {
            "initialized": False,
            "loading": False,
            "error": str(e)
        }


# ====================문제은행 API====================

@app.post("/api/exam-bank/generate")
async def generate_exam_questions(request: Request):
    """RAG 기반 문제 생성"""
    try:
        data = await request.json()
        print(f"[INFO] 문제 생성 요청: {data.get('exam_name')}, 문서: {data.get('document_context')}")
        
        exam_name = data.get('exam_name')
        subject = data.get('subject')
        exam_date = data.get('exam_date')
        num_questions = int(data.get('num_questions', 10))
        question_type = data.get('question_type', 'multiple_choice')
        difficulty = data.get('difficulty', 'medium')
        instructor_code = data.get('instructor_code', '')
        description = data.get('description', '')
        document_context = data.get('document_context', [])  # 선택된 RAG 문서 리스트
        
        print(f"[DEBUG] vector_store_manager: {vector_store_manager is not None}")
        
        # RAG 시스템 확인 (vector_store_manager만 체크)
        if not vector_store_manager:
            print("[ERROR] vector_store_manager가 None입니다")
            raise HTTPException(status_code=503, detail="RAG 시스템(Vector Store)이 초기화되지 않았습니다. 먼저 문서를 업로드하고 RAG 인덱싱을 완료해주세요.")
        
        # GROQ API 키 가져오기
        print("[INFO] GROQ API 키 조회 중...")
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'groq_api_key'")
        result = cursor.fetchone()
        groq_api_key = result['setting_value'] if result else os.getenv('GROQ_API_KEY', '')
        conn.close()
        
        print(f"[DEBUG] GROQ API 키 존재: {bool(groq_api_key)}")
        
        if not groq_api_key:
            print("[ERROR] GROQ API 키가 없습니다")
            raise HTTPException(status_code=400, detail="GROQ API 키가 설정되지 않았습니다. 시스템 설정에서 GROQ API 키를 등록해주세요.")
        
        # 난이도에 따른 프롬프트 조정
        difficulty_prompts = {
            'easy': '기본적이고 쉬운 수준의',
            'medium': '중간 수준의',
            'hard': '심화되고 어려운 수준의'
        }
        difficulty_text = difficulty_prompts.get(difficulty, '중간 수준의')
        
        # 문제 유형에 따른 프롬프트
        type_prompts = {
            'multiple_choice': f'''
{num_questions}개의 {difficulty_text} 객관식 문제를 생성해주세요.
각 문제는 다음 형식을 따라야 합니다:

문제 1:
[문제 내용]

A) [선택지 1]
B) [선택지 2]
C) [선택지 3]
D) [선택지 4]

정답: [A/B/C/D]
해설: [정답에 대한 설명]
참고: [출처 문서명]

각 문제는 반드시 위 형식을 정확히 따라주세요.
''',
            'short_answer': f'{num_questions}개의 {difficulty_text} 단답형 문제를 생성해주세요. 각 문제는 "문제:", "정답:", "해설:", "참고:" 형식으로 작성해주세요.',
            'essay': f'{num_questions}개의 {difficulty_text} 서술형 문제를 생성해주세요. 각 문제는 "문제:", "모범답안:", "채점기준:", "참고:" 형식으로 작성해주세요.'
        }
        
        # 선택된 문서 정보를 프롬프트에 명시
        doc_context_text = ""
        if document_context:
            doc_context_text = f"\n선택된 문서: {', '.join(document_context)}\n"
        
        prompt = f"""
시험명: {exam_name}
교과목: {subject}{doc_context_text}

{type_prompts.get(question_type, type_prompts['multiple_choice'])}

제공된 문서 내용을 기반으로 문제를 출제해주세요.
"""
        
        # RAG를 사용하여 문제 생성
        print(f"[INFO] RAGChain 초기화 중... (k={10 if document_context else 5})")
        from rag.rag_chain import RAGChain
        
        try:
            exam_rag_chain = RAGChain(vector_store_manager, groq_api_key, api_type='groq')
            print("[OK] RAGChain 초기화 완료")
        except Exception as chain_error:
            print(f"[ERROR] RAGChain 초기화 실패: {chain_error}")
            raise HTTPException(status_code=500, detail=f"RAGChain 초기화 실패: {str(chain_error)}")
        
        # 문서 컨텍스트가 있으면 더 많은 청크 검색
        k_value = 10 if document_context else 5
        
        print(f"[INFO] RAG 쿼리 실행 중... (프롬프트 길이: {len(prompt)})")
        try:
            # 문제 출제는 낮은 유사도도 허용 (0.0 = 모든 문서 사용)
            result = await exam_rag_chain.query(
                prompt,
                k=k_value,
                min_similarity=0.0,  # 유사도 임계값 제거
                document_context=document_context if document_context else None
            )
            print(f"[OK] RAG 쿼리 완료 (응답 길이: {len(result.get('answer', ''))})")
            print(f"[INFO] 사용된 문서 수: {len(result.get('sources', []))}")
        except Exception as query_error:
            print(f"[ERROR] RAG 쿼리 실패: {query_error}")
            import traceback
            print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"RAG 쿼리 실패: {str(query_error)}")
        
        return {
            "success": True,
            "questions_text": result['answer'],
            "sources": result.get('sources', []),
            "exam_info": {
                "exam_name": exam_name,
                "subject": subject,
                "exam_date": exam_date,
                "num_questions": num_questions,
                "question_type": question_type,
                "difficulty": difficulty
            }
        }
        
    except HTTPException as he:
        # HTTPException은 그대로 전달
        raise he
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] 문제 생성 실패: {str(e)}")
        print(f"[ERROR] Traceback:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"문제 생성 실패: {str(e)}")


@app.post("/api/exam-bank/save")
async def save_exam(request: Request):
    """생성된 문제를 데이터베이스에 저장"""
    try:
        data = await request.json()
        exam_name = data.get('exam_name')
        subject = data.get('subject')
        exam_date = data.get('exam_date')
        question_type = data.get('question_type', 'multiple_choice')
        difficulty = data.get('difficulty', 'medium')
        instructor_code = data.get('instructor_code', '')
        description = data.get('description', '')
        questions = data.get('questions', [])
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # exam_bank 테이블 생성 (없으면)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exam_bank (
                    exam_id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_name VARCHAR(255) NOT NULL,
                    subject VARCHAR(255),
                    exam_date DATE,
                    total_questions INT DEFAULT 0,
                    question_type VARCHAR(50) DEFAULT 'multiple_choice',
                    difficulty VARCHAR(50) DEFAULT 'medium',
                    instructor_code VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_exam_date (exam_date),
                    INDEX idx_instructor (instructor_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # exam_questions 테이블 생성 (없으면)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exam_questions (
                    question_id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_id INT NOT NULL,
                    question_number INT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type VARCHAR(50) DEFAULT 'multiple_choice',
                    options JSON,
                    correct_answer TEXT,
                    explanation TEXT,
                    reference_page VARCHAR(100),
                    reference_document VARCHAR(255),
                    difficulty VARCHAR(50) DEFAULT 'medium',
                    points INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exam_id) REFERENCES exam_bank(exam_id) ON DELETE CASCADE,
                    INDEX idx_exam (exam_id),
                    INDEX idx_question_number (question_number)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            print("[INFO] exam_bank 테이블 생성/확인 완료")
        except Exception as table_error:
            print(f"[WARN] 테이블 생성 중 오류 (무시): {table_error}")
        
        # 시험 정보 저장
        cursor.execute("""
            INSERT INTO exam_bank (exam_name, subject, exam_date, total_questions, 
                                   question_type, difficulty, instructor_code, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (exam_name, subject, exam_date, len(questions), question_type, 
              difficulty, instructor_code, description))
        
        exam_id = cursor.lastrowid
        
        # 문제 저장
        for idx, question in enumerate(questions, 1):
            # options를 JSON 문자열로 변환
            import json
            options_json = json.dumps(question.get('options', []), ensure_ascii=False) if question.get('options') else None
            
            cursor.execute("""
                INSERT INTO exam_questions (exam_id, question_number, question_text, 
                                           question_type, options, correct_answer, 
                                           explanation, reference_page, reference_document, 
                                           difficulty, points)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (exam_id, idx, question.get('question_text', ''),
                  question_type, options_json, question.get('correct_answer', ''),
                  question.get('explanation', ''), question.get('reference_page', ''),
                  question.get('reference_document', ''), difficulty, 
                  question.get('points', 1)))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "exam_id": exam_id,
            "message": f"시험 '{exam_name}'이(가) 저장되었습니다"
        }
        
    except Exception as e:
        print(f"[ERROR] 시험 저장 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"시험 저장 실패: {str(e)}")


@app.get("/api/exam-bank/list")
async def get_exam_list():
    """저장된 시험 목록 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # exam_bank 테이블 생성 (없으면)
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exam_bank (
                    exam_id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_name VARCHAR(255) NOT NULL,
                    subject VARCHAR(255),
                    exam_date DATE,
                    total_questions INT DEFAULT 0,
                    question_type VARCHAR(50) DEFAULT 'multiple_choice',
                    difficulty VARCHAR(50) DEFAULT 'medium',
                    instructor_code VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_exam_date (exam_date),
                    INDEX idx_instructor (instructor_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # exam_questions 테이블 생성 (없으면)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exam_questions (
                    question_id INT AUTO_INCREMENT PRIMARY KEY,
                    exam_id INT NOT NULL,
                    question_number INT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type VARCHAR(50) DEFAULT 'multiple_choice',
                    options JSON,
                    correct_answer TEXT,
                    explanation TEXT,
                    reference_page VARCHAR(100),
                    reference_document VARCHAR(255),
                    difficulty VARCHAR(50) DEFAULT 'medium',
                    points INT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exam_id) REFERENCES exam_bank(exam_id) ON DELETE CASCADE,
                    INDEX idx_exam (exam_id),
                    INDEX idx_question_number (question_number)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            conn.commit()
            print("[INFO] exam_bank 테이블 생성/확인 완료")
        except Exception as table_error:
            print(f"[WARN] 테이블 생성 중 오류 (무시): {table_error}")
        
        cursor.execute("""
            SELECT exam_id, exam_name, subject, exam_date, total_questions, 
                   question_type, difficulty, instructor_code, description,
                   created_at, updated_at
            FROM exam_bank
            ORDER BY exam_date DESC, created_at DESC
        """)
        
        exams = cursor.fetchall()
        conn.close()
        
        return {
            "success": True,
            "exams": exams
        }
        
    except Exception as e:
        print(f"[ERROR] 시험 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"시험 목록 조회 실패: {str(e)}")


@app.get("/api/exam-bank/{exam_id}")
async def get_exam_detail(exam_id: int):
    """시험 상세 정보 및 문제 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 시험 정보 조회
        cursor.execute("""
            SELECT exam_id, exam_name, subject, exam_date, total_questions, 
                   question_type, difficulty, instructor_code, description,
                   created_at, updated_at
            FROM exam_bank
            WHERE exam_id = %s
        """, (exam_id,))
        
        exam = cursor.fetchone()
        
        if not exam:
            raise HTTPException(status_code=404, detail="시험을 찾을 수 없습니다")
        
        # 문제 조회
        cursor.execute("""
            SELECT question_id, question_number, question_text, question_type,
                   options, correct_answer, explanation, reference_page,
                   reference_document, difficulty, points
            FROM exam_questions
            WHERE exam_id = %s
            ORDER BY question_number
        """, (exam_id,))
        
        questions = cursor.fetchall()
        
        # options JSON 파싱
        import json
        for q in questions:
            if q['options']:
                try:
                    q['options'] = json.loads(q['options'])
                except:
                    q['options'] = []
        
        conn.close()
        
        exam['questions'] = questions
        
        return {
            "success": True,
            "exam": exam
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 시험 상세 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"시험 상세 조회 실패: {str(e)}")


@app.delete("/api/exam-bank/{exam_id}")
async def delete_exam(exam_id: int):
    """시험 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 시험 존재 확인
        cursor.execute("SELECT exam_name FROM exam_bank WHERE exam_id = %s", (exam_id,))
        exam = cursor.fetchone()
        
        if not exam:
            raise HTTPException(status_code=404, detail="시험을 찾을 수 없습니다")
        
        # 시험 삭제 (CASCADE로 문제도 자동 삭제)
        cursor.execute("DELETE FROM exam_bank WHERE exam_id = %s", (exam_id,))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"시험 '{exam['exam_name']}'이(가) 삭제되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 시험 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"시험 삭제 실패: {str(e)}")


@app.delete("/api/exam-bank/{exam_id}/question/{question_id}")
async def delete_question(exam_id: int, question_id: int):
    """개별 문제 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 문제 존재 확인
        cursor.execute("""
            SELECT question_id FROM exam_questions 
            WHERE question_id = %s AND exam_id = %s
        """, (question_id, exam_id))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다")
        
        # 문제 삭제
        cursor.execute("DELETE FROM exam_questions WHERE question_id = %s", (question_id,))
        
        # 시험의 총 문항수 업데이트
        cursor.execute("""
            UPDATE exam_bank 
            SET total_questions = (
                SELECT COUNT(*) FROM exam_questions WHERE exam_id = %s
            )
            WHERE exam_id = %s
        """, (exam_id, exam_id))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "문제가 삭제되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 문제 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문제 삭제 실패: {str(e)}")


@app.put("/api/exam-bank/{exam_id}")
async def update_exam(exam_id: int, request: Request):
    """시험 정보 수정"""
    try:
        data = await request.json()
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 시험 존재 확인
        cursor.execute("SELECT exam_id FROM exam_bank WHERE exam_id = %s", (exam_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="시험을 찾을 수 없습니다")
        
        # 업데이트할 필드 구성
        update_fields = []
        params = []
        
        if 'exam_name' in data:
            update_fields.append("exam_name = %s")
            params.append(data['exam_name'])
        if 'subject' in data:
            update_fields.append("subject = %s")
            params.append(data['subject'])
        if 'exam_date' in data:
            update_fields.append("exam_date = %s")
            params.append(data['exam_date'])
        if 'difficulty' in data:
            update_fields.append("difficulty = %s")
            params.append(data['difficulty'])
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
        
        if update_fields:
            params.append(exam_id)
            query = f"UPDATE exam_bank SET {', '.join(update_fields)} WHERE exam_id = %s"
            cursor.execute(query, params)
        
        # 문제 업데이트
        if 'questions' in data:
            import json
            for question in data['questions']:
                question_id = question.get('question_id')
                if question_id:
                    # options를 JSON 문자열로 변환
                    options_json = json.dumps(question.get('options', []), ensure_ascii=False) if question.get('options') else None
                    
                    cursor.execute("""
                        UPDATE exam_questions 
                        SET question_text = %s, 
                            options = %s, 
                            correct_answer = %s, 
                            explanation = %s, 
                            reference_document = %s
                        WHERE question_id = %s AND exam_id = %s
                    """, (
                        question.get('question_text', ''),
                        options_json,
                        question.get('correct_answer', ''),
                        question.get('explanation', ''),
                        question.get('reference_document', ''),
                        question_id,
                        exam_id
                    ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "시험 정보가 수정되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 시험 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"시험 수정 실패: {str(e)}")


# ====================문서 관리 API====================

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form("general")
):
    """
    문서 업로드 (documents 폴더에 저장)
    - PDF, DOCX, DOC, TXT, PPTX, XLSX 파일 지원
    """
    try:
        # 파일 확장자 확인
        file_ext = Path(file.filename).suffix.lower()
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.pptx', '.ppt', '.xlsx', '.xls']
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="지원하지 않는 파일 형식입니다. PDF, DOCX, DOC, TXT, PPTX, XLSX 파일만 업로드 가능합니다."
            )
        
        # 파일 읽기
        content = await file.read()
        file_size = len(content)
        
        # 파일 크기 확인 (100MB 제한)
        if file_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="파일 크기는 100MB 이하여야 합니다")
        
        # 카테고리에 따라 저장 폴더 결정
        if category == "rag-indexed" or category == "rag":
            # RAG 문서는 rag_documents 폴더에 저장
            documents_dir = Path("./rag_documents")
        else:
            # 일반 문서는 documents 폴더에 저장
            documents_dir = Path("./documents")
        
        documents_dir.mkdir(exist_ok=True)
        
        # 고유 파일명 생성 (타임스탬프 + 원본 파일명)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = documents_dir / safe_filename
        
        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(content)
        
        print(f"[OK] 문서 저장 완료: {file_path}")
        
        return {
            "success": True,
            "message": "문서가 성공적으로 업로드되었습니다",
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_size": file_size,
            "file_path": str(file_path),
            "category": category,
            "upload_date": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 문서 업로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문서 업로드 실패: {str(e)}")


@app.get("/api/documents/list")
async def list_documents():
    """documents 및 rag_documents 폴더의 파일 목록 조회"""
    try:
        documents = []
        
        # documents 폴더와 rag_documents 폴더 모두에서 파일 조회
        for folder_name in ["documents", "rag_documents"]:
            folder_path = Path(f"./{folder_name}")
            
            if folder_path.exists():
                for file_path in folder_path.iterdir():
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        stat = file_path.stat()
                        documents.append({
                            "filename": file_path.name,
                            "file_size": stat.st_size,
                            "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
                            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "extension": file_path.suffix.lower(),
                            "folder": folder_name  # 어느 폴더에서 온 파일인지 표시
                        })
        
        # 수정일시 기준 내림차순 정렬
        documents.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return {
            "success": True,
            "documents": documents,
            "count": len(documents)
        }
        
    except Exception as e:
        print(f"[ERROR] 문서 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 실패: {str(e)}")


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """문서 삭제 (documents 및 rag_documents 폴더에서 검색)"""
    try:
        # 파일명 검증 (경로 탐색 공격 방지)
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="잘못된 파일명입니다")
        
        # documents와 rag_documents 폴더 모두에서 파일 찾기
        file_path = None
        for folder in ["documents", "rag_documents"]:
            test_path = Path(f"./{folder}") / filename
            if test_path.exists():
                file_path = test_path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="파일이 아닙니다")
        
        # 파일 삭제
        file_path.unlink()
        
        print(f"[OK] 문서 삭제 완료: {filename}")
        
        return {
            "success": True,
            "message": f"문서 '{filename}'이(가) 삭제되었습니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 문서 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문서 삭제 실패: {str(e)}")


@app.get("/api/documents/download/{filename}")
async def download_document(filename: str):
    """문서 다운로드 (documents 및 rag_documents 폴더에서 검색)"""
    try:
        # 파일명 검증
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="잘못된 파일명입니다")
        
        # documents와 rag_documents 폴더 모두에서 파일 찾기
        file_path = None
        for folder in ["documents", "rag_documents"]:
            test_path = Path(f"./{folder}") / filename
            if test_path.exists():
                file_path = test_path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        from fastapi.responses import FileResponse
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 문서 다운로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문서 다운로드 실패: {str(e)}")


@app.post("/api/rag/index-document")
async def index_document_to_rag(request: Request, background_tasks: BackgroundTasks):
    """
    문서를 RAG 시스템에 인덱싱 (백그라운드 처리)
    - filename: rag_documents 또는 documents 폴더에 있는 파일명
    - original_filename: 원본 파일명 (선택)
    """
    if not vector_store_manager or not document_loader:
        raise HTTPException(status_code=503, detail="RAG 시스템이 초기화되지 않았습니다")
    
    try:
        body = await request.json()
        filename = body.get('filename')
        original_filename = body.get('original_filename', filename)
        
        if not filename:
            raise HTTPException(status_code=400, detail="filename이 필요합니다")
        
        # 진행률 초기화
        indexing_progress[filename] = {
            "status": "started",
            "progress": 0,
            "message": "인덱싱 시작 중...",
            "started_at": datetime.now().isoformat()
        }
        save_indexing_progress(indexing_progress)
        
        # 백그라운드에서 실행할 함수 정의
        def do_indexing():
            try:
                _index_document_sync(filename, original_filename)
            except Exception as e:
                print(f"[ERROR] 백그라운드 인덱싱 실패: {str(e)}")
                indexing_progress[filename] = {
                    "status": "error",
                    "progress": 0,
                    "message": f"오류: {str(e)}"
                }
                save_indexing_progress(indexing_progress)
        
        # 백그라운드 태스크로 추가
        background_tasks.add_task(do_indexing)
        
        # 즉시 응답 반환 (백그라운드에서 계속 실행)
        return {
            "success": True,
            "message": "인덱싱이 백그라운드에서 시작되었습니다. 진행률을 조회하세요.",
            "filename": filename,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 인덱싱 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"인덱싱 요청 실패: {str(e)}")


def _index_document_sync(filename: str, original_filename: str):
    """
    실제 인덱싱 로직 (동기 함수, 백그라운드에서 실행됨)
    """
    try:
        
        # rag_documents 폴더와 documents 폴더에서 파일 찾기
        file_path = None
        for folder in ["rag_documents", "documents"]:
            test_path = Path(f"./{folder}") / filename
            if test_path.exists():
                file_path = test_path
                break
        
        if not file_path:
            indexing_progress[filename] = {"status": "error", "progress": 0, "message": "파일을 찾을 수 없습니다"}
            save_indexing_progress(indexing_progress)
            raise Exception(f"파일을 찾을 수 없습니다: {filename}")
        
        # 파일 확장자 확인
        file_ext = file_path.suffix.lower()
        if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
            indexing_progress[filename] = {"status": "error", "progress": 0, "message": "지원하지 않는 파일 형식"}
            save_indexing_progress(indexing_progress)
            raise Exception("RAG 인덱싱은 PDF, DOCX, TXT 파일만 지원합니다")
        
        print(f"📚 RAG 인덱싱 시작: {filename}")
        indexing_progress[filename] = {"status": "parsing", "progress": 10, "message": "문서 파싱 중..."}
        save_indexing_progress(indexing_progress)
        
        # 메타데이터 구성
        metadata = {
            "filename": filename,
            "original_filename": original_filename,
            "indexed_at": datetime.now().isoformat(),
            "file_size": file_path.stat().st_size,
            "source": "documents_folder"
        }
        
        # 문서 로드 및 청킹
        print(f"📝 문서 파싱 중...")
        documents = document_loader.load_document(str(file_path), metadata)
        
        if not documents:
            indexing_progress[filename] = {"status": "error", "progress": 0, "message": "텍스트 추출 실패"}
            save_indexing_progress(indexing_progress)
            raise Exception("문서에서 텍스트를 추출할 수 없습니다")
        
        print(f"🧩 청킹 완료: {len(documents)}개 조각")
        indexing_progress[filename] = {"status": "chunking", "progress": 30, "message": f"청킹 완료: {len(documents)}개 조각"}
        save_indexing_progress(indexing_progress)
        
        # 벡터 DB에 저장
        print(f"🔢 임베딩 및 인덱싱 중...")
        total_docs = len(documents)
        indexing_progress[filename] = {"status": "embedding", "progress": 50, "message": f"📝 {total_docs}개 문서 임베딩 생성 중..."}
        save_indexing_progress(indexing_progress)
        
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # 배치 단위로 진행률 업데이트
        batch_size = 8  # sentence-transformers 기본 배치 크기
        total_batches = (total_docs + batch_size - 1) // batch_size
        
        # 임베딩 시작 전 상태 업데이트
        indexing_progress[filename] = {
            "status": "embedding", 
            "progress": 50, 
            "message": f"🔢 임베딩 생성 중... (배치 0/{total_batches})"
        }
        save_indexing_progress(indexing_progress)
        
        # 진행률 콜백 함수
        last_logged_progress = [0]  # 마지막 로그 출력 진행률
        
        def update_progress(batch_num, total_batches, progress):
            old_progress = indexing_progress.get(filename, {}).get('progress', 0)
            
            indexing_progress[filename] = {
                "status": "embedding",
                "progress": progress,
                "message": f"🧠 임베딩 생성 중... (배치 {batch_num}/{total_batches})"
            }
            save_indexing_progress(indexing_progress)
            
            # 진행률이 변경되었을 때만 로그 출력
            if progress != old_progress and progress - last_logged_progress[0] >= 5:
                print(f"[INFO] 진행률: {progress}% (배치 {batch_num}/{total_batches})")
                last_logged_progress[0] = progress
        
        # 실제 임베딩 생성 (콜백 전달)
        doc_ids = vector_store_manager.add_documents(texts, metadatas, progress_callback=update_progress)
        
        # 완료 직전 상태
        indexing_progress[filename] = {
            "status": "saving", 
            "progress": 90, 
            "message": f"💾 벡터 데이터베이스 저장 중... ({len(doc_ids)}개)"
        }
        save_indexing_progress(indexing_progress)
        
        print(f"✅ RAG 인덱싱 완료: {len(doc_ids)}개 벡터 저장됨")
        indexing_progress[filename] = {"status": "completed", "progress": 100, "message": f"✅ 인덱싱 완료! ({len(doc_ids)}개 벡터)"}
        save_indexing_progress(indexing_progress)
        
        # 완료된 항목은 30초 후 자동 정리 (메모리 관리)
        import threading
        def cleanup():
            time.sleep(30)
            if filename in indexing_progress and indexing_progress[filename].get('status') == 'completed':
                del indexing_progress[filename]
                save_indexing_progress(indexing_progress)
                print(f"[INFO] 완료된 진행률 정보 정리: {filename}")
        threading.Thread(target=cleanup, daemon=True).start()
        
        print(f"[OK] 인덱싱 완료: {filename}, {len(documents)}개 청크, {len(doc_ids)}개 벡터")
        
    except Exception as e:
        print(f"[ERROR] RAG 인덱싱 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        indexing_progress[filename] = {"status": "error", "progress": 0, "message": f"오류: {str(e)}"}
        save_indexing_progress(indexing_progress)


@app.get("/api/rag/indexing-progress/{filename}")
async def get_indexing_progress(filename: str):
    """RAG 인덱싱 진행률 조회"""
    if filename not in indexing_progress:
        return {"status": "not_found", "progress": 0, "message": "진행 정보 없음"}
    return indexing_progress[filename]


@app.get("/api/rag/document-status/{filename}")
async def get_document_rag_status(filename: str):
    """
    문서의 RAG 인덱싱 상태 확인
    - indexed: 인덱싱 완료 여부
    - indexing: 현재 인덱싱 진행 중인지 여부
    - progress: 진행률 정보
    """
    if not vector_store_manager:
        # RAG 시스템 지연 초기화
        print("[INFO] 첫 RAG 요청 - 시스템 초기화 중...")
        if not init_rag():
            raise HTTPException(status_code=503, detail="RAG 시스템 초기화에 실패했습니다. 서버 로그를 확인하세요.")
    
    try:
        # 1. 진행 중인 인덱싱 확인
        is_indexing = filename in indexing_progress
        progress_info = indexing_progress.get(filename, {})
        
        # 2. 파일명으로 벡터 DB 검색
        documents = vector_store_manager.get_all_documents()
        
        # 해당 파일명을 가진 문서가 있는지 확인
        indexed_docs = [
            doc for doc in documents 
            if doc.get('metadata', {}).get('filename') == filename or
               doc.get('metadata', {}).get('original_filename') == filename
        ]
        
        is_indexed = len(indexed_docs) > 0
        
        return {
            "success": True,
            "filename": filename,
            "indexed": is_indexed,
            "indexing": is_indexing and progress_info.get('status') not in ['completed', 'error'],
            "progress": progress_info if is_indexing else None,
            "chunk_count": len(indexed_docs),
            "total_docs_in_rag": len(documents)
        }
        
    except Exception as e:
        print(f"[ERROR] RAG 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG 상태 조회 실패: {str(e)}")


# ==================== 시스템 연결 테스트 API ====================

@app.get("/api/test/database")
async def test_database_connection():
    """데이터베이스 연결 테스트"""
    import time
    start_time = time.time()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 간단한 쿼리 실행
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        response_time = int((time.time() - start_time) * 1000)
        
        print(f"[OK] DB 연결 테스트 성공 ({response_time}ms)")
        
        return {
            "success": True,
            "message": "데이터베이스 연결 정상",
            "host": DB_CONFIG['host'],
            "database": DB_CONFIG['db'],
            "response_time": response_time
        }
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        print(f"[ERROR] DB 연결 테스트 실패: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"데이터베이스 연결 실패: {str(e)}"
        )

@app.get("/api/test/ftp")
async def test_ftp_connection():
    """FTP 서버 연결 테스트"""
    import time
    from ftplib import FTP
    
    start_time = time.time()
    
    try:
        ftp = FTP()
        ftp.encoding = 'utf-8'
        
        # FTP 연결
        ftp.connect(FTP_CONFIG['host'], FTP_CONFIG['port'])
        ftp.login(FTP_CONFIG['user'], FTP_CONFIG['passwd'])
        
        # 현재 디렉토리 확인
        current_dir = ftp.pwd()
        
        ftp.quit()
        
        response_time = int((time.time() - start_time) * 1000)
        
        print(f"[OK] FTP 연결 테스트 성공 ({response_time}ms)")
        
        return {
            "success": True,
            "message": "FTP 서버 연결 정상",
            "host": FTP_CONFIG['host'],
            "port": FTP_CONFIG['port'],
            "user": FTP_CONFIG['user'],
            "current_dir": current_dir,
            "response_time": response_time
        }
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        print(f"[ERROR] FTP 연결 테스트 실패: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"FTP 서버 연결 실패: {str(e)}"
        )


# ==================== 서버 시작 ====================
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 BH2025 WOWU 백엔드 서버 시작")
    print("="*60)
    
    # 등록된 라우트 확인
    print("\n📋 등록된 API 엔드포인트:")
    doc_routes = []
    rag_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            if '/api/documents' in route.path:
                doc_routes.append(f"  {', '.join(route.methods)} {route.path}")
            elif '/api/rag' in route.path:
                rag_routes.append(f"  {', '.join(route.methods)} {route.path}")
    
    if doc_routes:
        print("\n📁 Documents API:")
        for r in sorted(doc_routes):
            print(r)
    
    if rag_routes:
        print("\n🤖 RAG API:")
        for r in sorted(rag_routes):
            print(r)
    
    print("\n" + "="*60)
    print("✅ 서버 URL: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
