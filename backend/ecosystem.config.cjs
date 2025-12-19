module.exports = {
  apps: [
    {
      name: 'bhhs-backend',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8000 --reload --limit-max-requests 10000 --timeout-keep-alive 300',
      cwd: '/home/user/webapp/backend',
      env: {
        NODE_ENV: 'development',
        PYTHONUNBUFFERED: '1'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      interpreter: 'python3'
    }
  ]
}
