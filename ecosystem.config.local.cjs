module.exports = {
  apps: [
    {
      name: 'bh2025-backend-local',
      script: 'python',
      args: '-m uvicorn main:app --host 0.0.0.0 --port 8000 --reload',
      cwd: './backend',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },
    {
      name: 'bh2025-frontend-local',
      script: 'python',
      args: '-m http.server 8080',
      cwd: './frontend',
      interpreter: 'none',
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log'
    }
  ]
};
