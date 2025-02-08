# 🎯 AI Staff Development Agent

## System Overview

```mermaid
graph TD
    A[Frontend Dashboard] --> B[Backend API]
    B --> C[Agent Service]
    C --> D[Core Intelligence]
    D --> E[Template System]
    B --> F[Database]
    C --> G[Operation Queue]
    D --> H[Config Manager]
    G --> I[Retry Handler]
    B --> J[WebSocket Server]
    J --> K[Real-time Updates]
    B --> L[Metrics Collector]
    L --> M[Performance Dashboard]
    J --> N[Connection Manager]
    N --> O[Heartbeat System]
```

## 🔑 Key Components & Entry Points

### ✅ Recently Completed
- Frontend connectivity with proper error handling
- Enhanced WebSocket stability features:
  * Robust reconnection with exponential backoff
  * Heartbeat mechanism for connection health
  * Message queueing for disconnected state
  * Comprehensive subscription management
- Comprehensive monitoring system:
  * System metrics collection (CPU, Memory, Disk)
  * WebSocket health monitoring
  * Real-time metrics visualization
  * Metrics history management
- Type-safe implementation across components
- API proxy configuration for development
- Basic agent management interface

### 🚧 Current Focus (MVP Launch Priorities)
- Resolving container stability issues
- Optimizing build process
- Resource management improvements
- Final MVP testing and deployment

### Core Files
1. `backend/app/core/intelligence.py`
   - Core agent intelligence and capability management
   - Start here for understanding agent behavior

2. `backend/app/services/agent_service.py`
   - Agent lifecycle and operation handling
   - Key for agent-project interactions
   - Real-time agent status monitoring
   - Operation scheduling and retry logic

3. `dashboard/frontend/src/components/Agents/AgentList.tsx`
   - Main agent management interface
   - Start here for UI modifications
   - Real-time agent status updates
   - Metrics visualization

4. `private/config/templates/agent_class.py.template`
   - Base template for agent generation
   - Reference for agent capabilities

5. `docker-compose.yml`
   - System deployment configuration
   - Service dependencies and networking
   - Resource allocation settings

6. `backend/app/models/operations.py`
   - Operation tracking and management
   - Queue system models
   - Retry strategies

7. `backend/app/websockets/operations.py`
   - Real-time operation updates
   - WebSocket communication
   - Connection stability management

## 🚀 Essential Commands

```bash
# Start Development Environment
docker compose up -d
cd dashboard/frontend && npm run dev

# Run Tests
python -m pytest tests/

# Deploy Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor System
docker compose logs -f
```

## 📚 Documentation Map

### For New Users
1. [Quickstart Guide](quickstart.md)
   - Installation & basic setup
   - First-time configuration
   - Resource requirements

### For Developers
1. [Technical Guide](technical_guide.md)
   - System architecture
   - Development workflows
   - Testing procedures
   - Build optimization guidelines

### For Project Managers
1. [Roadmap & Strategy](roadmap.md)
   - Project vision
   - Milestone tracking
   - MVP launch plan

## 💬 Chat Session Management

### Overview
```mermaid
graph TD
    S[New Chat] --> T{Type}
    T -->|Task| U[Create SessionID]
    T -->|Query| V[Use Existing Session]
    U --> W[Track Context]
    V --> W
    W --> X[Update Manifest]
```

### Key Components
1. `src/core/intelligence.py`
   - ChatSessionManager class
   - Session state tracking
   - Context preservation

2. `backend/app/services/agent_service.py`
   - Session lifecycle management
   - Real-time status updates
   - Operation context binding

3. `dashboard/frontend/src/components/Agents/AgentList.tsx`
   - Active sessions display
   - Session status indicators
   - Real-time updates via WebSocket

### Common Tasks
1. Starting New Chat
   - Generate unique session ID
   - Initialize context store
   - Bind to active agent

2. Managing Sessions
   - Track active conversations
   - Handle session timeouts
   - Preserve context between messages

3. Monitoring Status
   - View active sessions
   - Track session metrics
   - Debug session issues

## 🔄 Development Workflow

```mermaid
graph LR
    A[New Task] --> B{Type?}
    B -->|Feature| C[Technical Guide]
    B -->|Bug| D[Error Analysis]
    B -->|Enhancement| E[Roadmap]
    C --> F[Implementation]
    D --> F
    E --> F
```

## 🎯 Quick Reference

### Common Tasks
1. Adding a New Agent
   - Update `private/config/agents.yaml`
   - Use template from `private/config/templates/agent_class.py.template`
   - Register in `backend/app/services/agent_service.py`

2. Modifying Capabilities
   - Edit `private/config/templates/capability.py`
   - Update tests in `tests/test_code_analyzer.py`
   - Rebuild agent service

3. Frontend Changes
   - Components in `dashboard/frontend/src/components/`
   - State management in `dashboard/frontend/src/services/`
   - Run `npm test` to verify changes

### Common Issues
1. Agent Initialization Failures
   - Check logs: `docker compose logs -f agent-service`
   - Verify config in `private/config/agents.yaml`
   - Check capability requirements
   - Review operation queue status
   - Check retry handler logs

2. Frontend Connection Issues
   - Verify API endpoints in `.env`
   - Check WebSocket connection
   - Review browser console logs
   - Monitor real-time updates
   - Check metrics collector status

3. Operation Failures
   - Check operation status in queue
   - Review retry attempts and strategies
   - Monitor resource allocation
   - Check agent availability

4. Build and Container Issues
   - Clean Docker system: `docker system prune`
   - Monitor resource usage during builds
   - Check for network connectivity issues
   - Review container resource limits
   - Clear build cache if needed

## 📈 Performance Guidelines

- Monitor system metrics via Grafana
- Review operation queue for bottlenecks
- Check WebSocket latency in browser dev tools
- Monitor container resource usage
- Track build performance metrics

## 🔗 External Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
