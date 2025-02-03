# Installation Guide

## Prerequisites

Before deploying the AI Staff Development Agent, you need to install Docker and Docker Compose.

### Installing Docker Desktop (Windows)

1. Download Docker Desktop for Windows:
   - Visit https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"
   - Run the installer

2. During installation:
   - Enable WSL 2 if prompted
   - Enable Hyper-V if prompted
   - Follow the installation wizard

3. After installation:
   - Restart your computer
   - Start Docker Desktop
   - Wait for Docker to finish starting up (icon will be steady in taskbar)

### Verify Installation

1. Open PowerShell or Command Prompt and run:
```powershell
# Check Docker installation
docker --version

# Check Docker Compose installation (included with Docker Desktop)
docker compose version
```

### System Requirements

- Windows 10 64-bit: Pro, Enterprise, or Education (Build 16299 or later)
- WSL 2 feature enabled
- BIOS-level hardware virtualization support must be enabled
- 4GB system RAM minimum

## Post-Installation Steps

1. Configure Docker Desktop settings:
   - Open Docker Desktop
   - Go to Settings
   - Adjust resources (Memory, CPU, Disk) as needed
   - Apply & Restart

2. Test Docker:
```powershell
# Run hello-world container
docker run hello-world
```

## Deploying the Agent

After installing Docker Desktop and verifying it's running:

1. Build and start services:
```powershell
docker compose up -d
```

2. Verify services are running:
```powershell
docker compose ps
```

3. View logs:
```powershell
docker compose logs -f
```

4. Stop services:
```powershell
docker compose down
```

## Troubleshooting

### Common Issues

1. Docker Desktop not starting:
   - Check WSL 2 installation
   - Verify virtualization is enabled in BIOS
   - Restart Docker Desktop

2. Permission issues:
   - Run terminal as Administrator
   - Check Windows user permissions

3. Resource issues:
   - Increase Docker Desktop resource limits
   - Close unnecessary applications

### Getting Help

- Docker Documentation: https://docs.docker.com/
- Docker Desktop Manual: https://docs.docker.com/desktop/windows/
- WSL 2 Installation: https://docs.microsoft.com/en-us/windows/wsl/install

## Next Steps

After installation:
1. Follow the deployment steps in master_plan.md
2. Configure initial agent capabilities
3. Run system verification tests
4. Begin monitoring system performance

## Performance Monitoring Setup

### Prerequisites
- Node.js 16 or later
- React Developer Tools browser extension (recommended)

### Setting Up Performance Monitoring

1. Install required dependencies:
```bash
npm install @tanstack/react-virtual
```

2. Configure Performance Monitoring:
```typescript
// In your component:
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor';

// Initialize monitoring
const { startMeasure, endMeasure, measureMessageLatency, getMetrics } = usePerformanceMonitor('ComponentName');
```

3. Enable Performance Tracking:
- Open browser DevTools
- Go to Performance tab
- Enable performance monitoring
- Check console for performance metrics logs

### Verifying Performance Monitoring

1. Check component performance:
```typescript
// Performance metrics will be logged on component unmount
console.debug('Performance Metrics:', getMetrics());
```

2. Monitor WebSocket latency:
```typescript
// In message handler:
const startTime = performance.now();
measureMessageLatency(startTime);
```

3. View real-time metrics in browser console
