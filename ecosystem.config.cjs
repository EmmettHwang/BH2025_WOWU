module.exports = {
  apps: [
    {
      name: 'frontend-server',
      script: 'node',
      args: 'frontend/proxy-server.cjs',
      cwd: '/home/user/webapp',
      env: {
        NODE_ENV: 'development',
        PORT: 3000
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'bhhs-backend',
      script: 'python3',
      args: 'backend/main.py',
      cwd: '/home/user/webapp',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork'
    }
  ]
}
