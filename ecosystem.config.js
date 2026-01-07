module.exports = {
  apps: [
    {
      name: 'bh2025-backend',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000 --workers 4',
      interpreter: 'python3',
      cwd: './backend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: 8000,
        PYTHONPATH: './backend',
        // DB 환경변수는 .env 파일에서 로드
        // 또는 여기에 직접 설정 가능
        // DB_HOST: 'your_mysql_host',
        // DB_PORT: '3306',
        // DB_USER: 'your_db_user',
        // DB_PASSWORD: 'your_db_password',
        // DB_NAME: 'BH2025',
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      time: true
    }
  ]
};
