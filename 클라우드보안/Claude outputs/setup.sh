#!/bin/bash
# EC2 Amazon Linux 2 / AL2023 - Node.js 웹서버 자동 설치 스크립트
# 사용법: chmod +x setup.sh && sudo bash setup.sh

set -e

echo "====================================="
echo "  Node.js 웹서버 설치 시작"
echo "====================================="

# 1. 시스템 업데이트
echo "[1/6] 시스템 업데이트 중..."
dnf update -y 2>/dev/null || yum update -y

# 2. Node.js 22 LTS 설치 (nvm 사용)
echo "[2/6] Node.js 설치 중..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm install 22
nvm use 22
nvm alias default 22

# node/npm을 전역에서 쓸 수 있도록 심볼릭 링크
NODE_PATH=$(nvm which current)
ln -sf "$NODE_PATH" /usr/local/bin/node
ln -sf "$(dirname $NODE_PATH)/npm" /usr/local/bin/npm
ln -sf "$(dirname $NODE_PATH)/npx" /usr/local/bin/npx

echo "Node.js 버전: $(node -v)"
echo "npm 버전: $(npm -v)"

# 3. 앱 디렉토리 생성
echo "[3/6] 앱 디렉토리 생성 중..."
APP_DIR="/home/ec2-user/myapp"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# 4. package.json 생성
echo "[4/6] Node.js 프로젝트 초기화 중..."
cat > package.json << 'EOF'
{
  "name": "myapp",
  "version": "1.0.0",
  "description": "EC2 Node.js 웹서비스",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF

# app.js 생성
cat > app.js << 'EOF'
const express = require('express');
const os = require('os');
const app = express();
const PORT = process.env.PORT || 8080;

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>EC2 Node.js 웹서버</title>
      <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f1923; color: #e0e0e0; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .card { background: #1a2634; border-radius: 16px; padding: 40px 50px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); max-width: 500px; width: 90%; }
        h1 { color: #4fc3f7; margin-bottom: 8px; font-size: 1.8rem; }
        .badge { display: inline-block; background: #27ae60; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; margin-bottom: 24px; }
        .info { background: #0f1923; border-radius: 10px; padding: 16px 20px; margin-top: 16px; }
        .info p { margin: 6px 0; font-size: 0.95rem; }
        .label { color: #4fc3f7; font-weight: 600; margin-right: 8px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🚀 EC2 웹서버 가동 중!</h1>
        <div class="badge">✅ 정상 작동</div>
        <div class="info">
          <p><span class="label">호스트명:</span>${os.hostname()}</p>
          <p><span class="label">Node.js:</span>${process.version}</p>
          <p><span class="label">포트:</span>${PORT}</p>
          <p><span class="label">업타임:</span>${Math.floor(process.uptime())}초</p>
          <p><span class="label">시간:</span>${new Date().toLocaleString('ko-KR')}</p>
        </div>
      </div>
    </body>
    </html>
  `);
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`서버 실행 중: http://0.0.0.0:${PORT}`);
});
EOF

# 5. 의존성 설치
echo "[5/6] 패키지 설치 중..."
npm install

# 6. systemd 서비스 등록 (자동 시작)
echo "[6/6] systemd 서비스 등록 중..."
cat > /etc/systemd/system/myapp.service << EOF
[Unit]
Description=Node.js 웹서비스
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/myapp
ExecStart=/usr/local/bin/node app.js
Restart=always
RestartSec=5
Environment=PORT=8080
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable myapp
systemctl start myapp

echo ""
echo "====================================="
echo "  ✅ 설치 완료!"
echo "====================================="
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "EC2 퍼블릭 IP")
echo ""
echo "  접속 URL: http://${INSTANCE_IP}:8080"
echo ""
echo "  서비스 상태 확인: sudo systemctl status myapp"
echo "  로그 확인:        sudo journalctl -u myapp -f"
echo "  서비스 재시작:    sudo systemctl restart myapp"
echo "====================================="
