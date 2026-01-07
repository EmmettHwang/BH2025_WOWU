module.exports = {
  apps: [
    {
      name: 'fastapi-backend',
      script: 'uvicorn',
      args: 'backend.main:app --host 0.0.0.0 --port 8000 --reload',
      interpreter: 'python3',
      env: {
        PYTHONUNBUFFERED: '1',
        PORT: 8000
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      cwd: '/home/user/webapp'
    },
    {
      name: 'frontend-server',
      script: 'python3',
      args: '-m http.server 3000 --directory frontend',
      env: {
        PORT: 3000
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      cwd: '/home/user/webapp'
    }
  ]
}
