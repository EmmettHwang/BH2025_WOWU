# Cafe24 배포 문제 해결 가이드

## 🔴 문제 1: 파일 크기 제한 (413 에러)

### 원인
Cafe24의 nginx 기본 설정: `client_max_body_size 1M` (1MB 제한)

### 해결 방법

#### 방법 1: nginx 설정 수정 (가장 확실 - 관리자 권한 필요)

SSH로 Cafe24 서버 접속 후:

```bash
# nginx 설정 파일 찾기
sudo find /etc -name "nginx.conf" 2>/dev/null
# 또는
sudo find /usr/local -name "nginx.conf" 2>/dev/null

# nginx 설정 편집
sudo nano /etc/nginx/nginx.conf
# 또는
sudo nano /usr/local/nginx/conf/nginx.conf
```

다음 내용 추가:
```nginx
http {
    # 전역 설정
    client_max_body_size 10M;
    client_body_buffer_size 10M;
    
    server {
        # 특정 location만 설정
        location /api/upload-image {
            client_max_body_size 10M;
        }
    }
}
```

설정 후:
```bash
# 설정 검증
sudo nginx -t

# nginx 재시작
sudo systemctl reload nginx
# 또는
sudo service nginx reload
```

#### 방법 2: .htaccess 수정 (Apache 사용 시)

`/www/.htaccess` 또는 `/public_html/.htaccess`:

```apache
# PHP 설정
php_value upload_max_filesize 10M
php_value post_max_size 10M
php_value memory_limit 128M
php_value max_execution_time 300
php_value max_input_time 300

# Apache 설정
LimitRequestBody 10485760
```

#### 방법 3: php.ini 수정 (PHP 사용 시)

```bash
# php.ini 찾기
php -i | grep "php.ini"

# 편집
sudo nano /etc/php.ini
# 또는
nano ~/www/php.ini
```

수정:
```ini
upload_max_filesize = 10M
post_max_size = 10M
memory_limit = 128M
max_execution_time = 300
max_input_time = 300
```

#### 방법 4: Cafe24 관리자 페이지에서 설정

1. Cafe24 호스팅 관리 페이지 로그인
2. 웹사이트 설정 → PHP 설정
3. `upload_max_filesize` 찾아서 10M으로 변경
4. `post_max_size` 찾아서 10M으로 변경
5. 저장

#### 방법 5: 이미지 압축 추가 (프론트엔드 해결책)

파일을 업로드하기 전에 JavaScript로 압축:

```javascript
// app.js에 추가할 함수
async function compressImage(file, maxSizeMB = 1) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                // 최대 크기 계산 (1920px)
                const maxDimension = 1920;
                if (width > maxDimension || height > maxDimension) {
                    if (width > height) {
                        height = (height / width) * maxDimension;
                        width = maxDimension;
                    } else {
                        width = (width / height) * maxDimension;
                        height = maxDimension;
                    }
                }
                
                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // 품질 조정하며 압축
                let quality = 0.9;
                canvas.toBlob((blob) => {
                    // 목표 크기보다 크면 품질 낮춰서 재시도
                    if (blob.size > maxSizeMB * 1024 * 1024 && quality > 0.1) {
                        quality -= 0.1;
                        canvas.toBlob((newBlob) => {
                            resolve(new File([newBlob], file.name, {
                                type: 'image/jpeg',
                                lastModified: Date.now()
                            }));
                        }, 'image/jpeg', quality);
                    } else {
                        resolve(new File([blob], file.name, {
                            type: 'image/jpeg',
                            lastModified: Date.now()
                        }));
                    }
                }, 'image/jpeg', quality);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}
```

---

## 🔴 문제 2: 사진 업로드 후 안 바뀜

### 원인
1. Cafe24의 강력한 CDN 캐싱
2. nginx의 정적 파일 캐싱
3. 브라우저 캐시

### 해결 방법

#### 방법 1: nginx 캐싱 헤더 설정

SSH로 접속 후 nginx 설정:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|webp)$ {
    expires -1;
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    add_header Pragma "no-cache";
}

# 또는 썸네일 API만 캐싱 방지
location /api/thumbnail {
    expires -1;
    add_header Cache-Control "no-store, no-cache, must-revalidate";
}
```

#### 방법 2: .htaccess로 캐싱 방지

`/www/.htaccess`:

```apache
# 이미지 캐싱 방지
<FilesMatch "\.(jpg|jpeg|png|gif|webp)$">
    Header set Cache-Control "no-cache, no-store, must-revalidate"
    Header set Pragma "no-cache"
    Header set Expires 0
</FilesMatch>

# 또는 특정 디렉토리만
<Directory "/www/backend/thumbnails">
    Header set Cache-Control "no-cache, no-store, must-revalidate"
</Directory>
```

#### 방법 3: 백엔드에서 캐싱 헤더 추가

`backend/main.py` 수정:

```python
from fastapi.responses import FileResponse

@app.get("/api/thumbnail")
async def get_thumbnail(url: str):
    """썸네일 반환 (캐싱 방지)"""
    # ... 기존 코드 ...
    
    return FileResponse(
        thumbnail_path,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )
```

#### 방법 4: 파일명에 타임스탬프 포함 (가장 확실)

업로드할 때 파일명 자체를 바꾸기:

```python
# backend/main.py 수정
def upload_to_ftp(file_data: bytes, filename: str, category: str) -> str:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')  # 밀리초까지
    unique_id = str(uuid.uuid4())[:8]
    
    # 파일명에 타임스탬프 포함
    name, ext = os.path.splitext(filename)
    new_filename = f"{timestamp}_{unique_id}_{name}{ext}"
    
    # ... FTP 업로드 ...
```

#### 방법 5: CDN Purge (Cafe24 CDN 사용 시)

Cafe24 관리 페이지에서:
1. CDN 설정 메뉴
2. 캐시 삭제(Purge)
3. URL 또는 전체 삭제

---

## 🛠️ 즉시 적용 가능한 임시 해결책

### 1. 이미지 압축 추가 (프론트엔드)

```bash
cd /home/user/webapp/frontend
```

`app.js`의 `uploadMyPagePhoto` 함수 수정:

```javascript
window.uploadMyPagePhoto = async function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 파일 크기 체크 전에 압축
    let uploadFile = file;
    if (file.size > 1 * 1024 * 1024) {  // 1MB 이상이면 압축
        window.showAlert('📦 이미지를 압축하는 중...', 'info');
        uploadFile = await compressImage(file, 1);  // 1MB 이하로 압축
        console.log(`압축: ${(file.size / 1024 / 1024).toFixed(2)}MB → ${(uploadFile.size / 1024 / 1024).toFixed(2)}MB`);
    }
    
    // 파일 크기 체크 (1MB)
    if (uploadFile.size > 1 * 1024 * 1024) {
        window.showAlert('⚠️ 파일 크기는 1MB를 초과할 수 없습니다.\\n\\n현재 크기: ' + (uploadFile.size / 1024 / 1024).toFixed(2) + 'MB', 'warning');
        event.target.value = '';
        return;
    }
    
    const instructor = JSON.parse(localStorage.getItem('instructor'));
    const formData = new FormData();
    formData.append('file', uploadFile);
    
    // ... 나머지 코드 동일 ...
};
```

### 2. 강제 새로고침 URL 개선

`app.js` 수정:

```javascript
// 업로드 후
const photoUrl = response.data.url;

// URL에 타임스탬프를 2개 추가 (더 강력한 캐시 버스팅)
const timestamp = new Date().getTime();
const random = Math.random().toString(36).substring(7);
const imageUrl = API_BASE_URL + '/api/thumbnail?url=' + encodeURIComponent(photoUrl) + '&t=' + timestamp + '&r=' + random;

document.getElementById('mypage-photo').src = imageUrl;
```

---

## 📋 Cafe24 서버 접속 후 체크리스트

```bash
# 1. nginx 설정 확인
sudo nginx -T | grep client_max_body_size

# 2. PHP 설정 확인 (있는 경우)
php -i | grep upload_max_filesize
php -i | grep post_max_size

# 3. 디스크 용량 확인
df -h

# 4. 업로드 디렉토리 권한 확인
ls -la /www/backend/uploads/
ls -la /www/backend/thumbnails/

# 5. 백엔드 프로세스 확인
pm2 list
pm2 logs bhhs-backend --nostream --lines 50

# 6. 최근 업로드된 파일 확인
ls -lt /www/backend/uploads/ | head -10
ls -lt /www/backend/thumbnails/ | head -10
```

---

## 🚀 권장 조치 순서

1. **즉시 적용** (코드 수정):
   - ✅ 이미지 압축 기능 추가
   - ✅ 파일 크기 제한 1MB로 변경
   - ✅ 강력한 캐시 버스팅 (timestamp + random)

2. **Cafe24 관리 페이지** (권한 있음):
   - PHP 설정에서 upload_max_filesize 10M으로 변경
   - CDN 캐시 삭제

3. **SSH 접속** (권한 있음):
   - nginx client_max_body_size 설정
   - 캐싱 헤더 설정

4. **고객센터 문의** (권한 없음):
   - "nginx client_max_body_size를 10M으로 변경 요청"
   - "이미지 캐싱 비활성화 요청"

---

## 📞 Cafe24 고객센터 문의 내용

```
제목: nginx 파일 업로드 크기 제한 및 캐싱 설정 변경 요청

안녕하세요.

현재 호스팅 중인 웹사이트에서 이미지 업로드 시 413 에러가 발생하고,
업로드 후에도 캐시로 인해 즉시 반영되지 않는 문제가 있습니다.

다음 설정을 변경해 주시기 바랍니다:

1. nginx client_max_body_size를 1M → 10M로 변경
2. /api/thumbnail 경로의 캐싱 비활성화
   (Cache-Control: no-store, no-cache)

감사합니다.
```
