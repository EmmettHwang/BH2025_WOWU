module.exports = {
  apps: [
    {
      name: 'frontend-server',
      script: 'node',
      args: 'frontend/proxy-server.cjs',
      cwd: process.cwd(), // 현재 디렉토리 자동 감지
      env: {
        NODE_ENV: 'development',
        PORT: 3000
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10
    },
    {
      name: 'backend-server',
      script: process.platform === 'win32' ? 'python' : 'python3',
      args: '-m uvicorn main:app --reload --host 0.0.0.0 --port 8000',
      cwd: process.platform === 'win32' 
        ? `${process.cwd()}\\backend` 
        : `${process.cwd()}/backend`,
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: process.env.PATH // 가상환경 PATH 상속
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10
    }
  ]
}
