#!/usr/bin/env python3
"""
실제 사용 중인 Python 패키지 확인 스크립트
"""

import os
import re
from pathlib import Path

# 체크할 파일 확장자
EXTENSIONS = ['.py']

# 제외할 디렉토리
EXCLUDE_DIRS = {'__pycache__', '.git', 'venv', 'env', 'node_modules', '.pytest_cache'}

def find_python_files(directory):
    """Python 파일 찾기"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 제외할 디렉토리 스킵
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_imports(file_path):
    """파일에서 import 문 추출"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # import xxx 패턴
        for match in re.finditer(r'^import\s+(\w+)', content, re.MULTILINE):
            imports.add(match.group(1))
        
        # from xxx import 패턴
        for match in re.finditer(r'^from\s+(\w+)', content, re.MULTILINE):
            imports.add(match.group(1))
            
    except Exception as e:
        print(f"⚠️  에러 ({file_path}): {e}")
    
    return imports

def main():
    # backend 디렉토리의 모든 Python 파일 찾기
    backend_dir = Path(__file__).parent / 'backend'
    python_files = find_python_files(backend_dir)
    
    print(f"📂 검색 디렉토리: {backend_dir}")
    print(f"📄 Python 파일 개수: {len(python_files)}\n")
    
    # 모든 import 수집
    all_imports = set()
    for file_path in python_files:
        imports = extract_imports(file_path)
        all_imports.update(imports)
    
    # 표준 라이브러리 제외
    stdlib = {
        'os', 'sys', 'io', 're', 'json', 'time', 'datetime', 'pathlib',
        'typing', 'asyncio', 'shutil', 'base64', 'uuid', 'urllib', 
        'ftplib', 'pickle', 'tempfile', 'warnings', 'traceback',
    }
    
    # 로컬 모듈 제외
    local_modules = {'backend', 'rag'}
    
    third_party = sorted(all_imports - stdlib - local_modules)
    
    print("=" * 60)
    print("🔍 사용 중인 서드파티 패키지")
    print("=" * 60)
    
    # requirements.txt 매핑
    package_mapping = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn[standard]',
        'pymysql': 'pymysql',
        'dotenv': 'python-dotenv',
        'httpx': 'httpx',
        'requests': 'requests',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'reportlab': 'reportlab',
        'PIL': 'pillow',
        'openai': 'openai',
        'google': 'google-generativeai',
        'langchain_core': 'langchain-core',
        'langchain_text_splitters': 'langchain-text-splitters',
        'langchain': 'langchain-core',
        'faiss': 'faiss-cpu',
        'sentence_transformers': 'sentence-transformers',
        'PyPDF2': 'pypdf2',
        'docx': 'python-docx',
        'tiktoken': 'tiktoken',
        'pydantic': 'pydantic',
    }
    
    used_packages = set()
    for module in third_party:
        if module in package_mapping:
            package = package_mapping[module]
            used_packages.add(package)
            print(f"✅ {module:25} → {package}")
        else:
            print(f"❓ {module:25} → (매핑 필요)")
    
    print("\n" + "=" * 60)
    print("📦 requirements.txt 필수 패키지")
    print("=" * 60)
    
    for package in sorted(used_packages):
        print(f"  {package}")
    
    print(f"\n총 {len(used_packages)}개 패키지 사용 중")

if __name__ == '__main__':
    main()
