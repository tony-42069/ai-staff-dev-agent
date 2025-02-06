# Quickstart Guide

## 🚀 Prerequisites

### System Requirements
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 16299 or later)
- WSL 2 feature enabled
- BIOS-level hardware virtualization support enabled
- 4GB system RAM minimum
- Node.js 16 or later
- Python 3.9 or later

### Required Software
1. Docker Desktop for Windows
2. Git
3. Visual Studio Code (recommended)
4. React Developer Tools browser extension (recommended)

## 🔧 Installation Steps

### 1. Docker Desktop Setup

1. Download and Install:
   - Visit https://www.docker.com/products/docker-desktop
   - Download for Windows
   - Run installer (enable WSL 2 and Hyper-V if prompted)
   - Restart computer

2. Verify Installation:
```powershell
# Check Docker
docker --version

# Check Docker Compose
docker compose version
```

3. Configure Docker Desktop:
   - Open Docker Desktop
   - Settings → Resources
   - Recommended allocations:
     * CPUs: 4+
     * Memory: 8GB+
     * Swap: 2GB+
     * Disk image size: 60GB+

### 2. Project Setup

1. Clone Repository:
```powershell
git clone https://github.com/yourusername/ai-staff-dev-agent.git
cd ai-staff-dev-agent
```

2. Install Dependencies:
```powershell
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../dashboard/frontend
npm install
```

## 🏃‍♂️ Running the System

### 1. Development Mode

```powershell
# Start backend services
docker compose up -d

# Start frontend development server
cd dashboard/frontend
npm run dev
```

### 2. Production Mode

```powershell
# Build and start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker compose logs -f
```

### 3. Verify Services

1. Check Container Status:
```powershell
docker compose ps
```

2. Access Components:
- Frontend Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- Monitoring Dashboard: http://localhost:3001

## 📊 Monitoring Setup

### 1. Performance Monitoring

1. Enable Frontend Monitoring:
```typescript
// In your component:
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor';

const { startMeasure, endMeasure } = usePerformanceMonitor('ComponentName');
```

2. View Metrics:
- Open browser DevTools
- Go to Performance tab
- Check console for performance logs

### 2. System Monitoring

1. Access Grafana:
- URL: http://localhost:3000/grafana
- Default credentials:
  * Username: admin
  * Password: admin

2. View Dashboards:
- System Metrics
- Application Metrics
- WebSocket Performance
- Database Metrics

## 🔧 Configuration

### 1. Environment Setup

1. Create configuration files:
```powershell
cp .env.example .env
cp backend/.env.example backend/.env
cp dashboard/frontend/.env.example dashboard/frontend/.env
```

2. Update configurations:
- Database settings
- API endpoints
- Authentication keys
- Monitoring endpoints

### 2. Agent Configuration

1. Update agent settings:
```powershell
python private/config/templates/manage_config.py update-agent ExampleAgent \
  '{"version": "1.0.0", "capabilities": ["code_review", "testing"]}'
```

2. Verify configuration:
```powershell
python private/config/templates/manage_config.py validate
```

## 🚨 Troubleshooting

### Common Issues

1. Docker Desktop Issues:
   - Check WSL 2 installation
   - Verify virtualization in BIOS
   - Restart Docker Desktop

2. Permission Issues:
   - Run terminal as Administrator
   - Check Windows user permissions

3. Resource Issues:
   - Increase Docker Desktop resources
   - Close unnecessary applications

4. Network Issues:
   - Check port availability
   - Verify firewall settings
   - Check Docker network configuration

### Getting Help

- Docker Documentation: https://docs.docker.com/
- Project Issues: https://github.com/yourusername/ai-staff-dev-agent/issues
- WSL Documentation: https://docs.microsoft.com/en-us/windows/wsl/

## 📝 Next Steps

1. Follow the development guide in docs/development_guide.md
2. Review system architecture in docs/system_architecture.md
3. Configure initial agent capabilities
4. Run system verification tests
5. Begin monitoring system performance

## 🔄 Updating the System

1. Pull latest changes:
```powershell
git pull origin main
```

2. Update dependencies:
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../dashboard/frontend
npm install
```

3. Run migrations:
```powershell
cd ../backend
alembic upgrade head
```

4. Rebuild containers:
```powershell
docker compose up -d --build
