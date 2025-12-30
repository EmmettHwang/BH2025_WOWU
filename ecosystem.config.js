module.exports = {
  apps: [
    {
      name: 'bh2025-backend',
      script: 'uvicorn',
      args: 'backend.main:app --host 0.0.0.0 --port 8000 --workers 4',
      interpreter: 'python3',
      cwd: './',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 8000,
        // DB 환경변수 (필요시 수정)
        DB_HOST: 'bitnmeta2.synology.me',
        DB_PORT: '23306',
        DB_USER: 'BH2025',
        DB_PASSWORD: 'DBwjdqh!2025',
        DB_NAME: 'BH2025',
        // API 키는 system_settings 테이블에서 로드
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      time: true
    }
  ]
};
