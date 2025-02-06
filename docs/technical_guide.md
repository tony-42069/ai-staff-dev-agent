# 🛠️ Technical Guide

## System Architecture

### Core Components

```mermaid
graph TD
    subgraph Frontend
        A[React Dashboard] --> B[WebSocket Client]
        A --> C[REST Client]
    end
    
    subgraph Backend
        D[FastAPI Server] --> E[Agent Service]
        E --> F[Core Intelligence]
        F --> G[Template System]
        D --> H[Database]
        E --> I[Operation Queue]
    end
    
    B --> D
    C --> D
```

### Component Details

#### 1. Core Intelligence (`intelligence.py`)
```python
class CoreIntelligence:
    def _initialize_core_capabilities(self):
        self.capabilities = {
            'project_generation': Capability(...),
            'code_generation': Capability(...),
            'code_analysis': Capability(...)
        }
```

#### 2. Agent Service (`agent_service.py`)
```python
class AgentService:
    VALID_CAPABILITIES = {
        "code_review",
        "testing",
        "development",
        "documentation",
        "deployment"
    }
```

#### 3. Template System
- Base templates for agent generation
- Dynamic capability loading
- Configuration management
- Lifecycle management

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd ai-staff-dev-agent

# Install dependencies
python -m pip install -r requirements.txt
cd dashboard/frontend && npm install

# Start services
docker compose up -d
npm run dev
```

### 2. Code Organization

```
ai-staff-dev-agent/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── core/         # Core logic
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── websockets/   # WebSocket handlers
│   └── alembic/          # Database migrations
├── dashboard/
│   └── frontend/
│       ├── src/
│       │   ├── components/  # React components
│       │   ├── services/    # API clients
│       │   └── types/       # TypeScript types
│       └── tests/
└── private/
    └── config/
        └── templates/     # Agent templates
```

### 3. Development Standards

#### Code Style
- Python: PEP 8
- TypeScript: ESLint + Prettier
- Git commit messages: Conventional Commits

#### Testing
```bash
# Backend tests
pytest tests/

# Frontend tests
cd dashboard/frontend
npm test

# E2E tests
npm run test:e2e
```

#### Performance Monitoring
```typescript
// Frontend performance tracking
const { startMeasure, endMeasure } = usePerformanceMonitor('ComponentName');
startMeasure();
render(<Component />);
endMeasure();
```

## Database Schema

### Core Tables

#### 1. Agents
```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    capabilities JSONB,
    status VARCHAR(50),
    metadata JSONB
);
```

#### 2. Projects
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    status VARCHAR(50),
    metadata JSONB
);
```

#### 3. Operations
```sql
CREATE TABLE operations (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    project_id UUID REFERENCES projects(id),
    type VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## API Reference

### REST Endpoints

#### Agents
```typescript
interface Agent {
  id: string;
  name: string;
  capabilities: string[];
  status: 'active' | 'inactive';
  metadata: Record<string, any>;
}

// GET /api/v1/agents
// POST /api/v1/agents
// GET /api/v1/agents/{agent_id}
// PUT /api/v1/agents/{agent_id}
// DELETE /api/v1/agents/{agent_id}
```

#### Projects
```typescript
interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  metadata: Record<string, any>;
}

// GET /api/v1/projects
// POST /api/v1/projects
// GET /api/v1/projects/{project_id}
// PUT /api/v1/projects/{project_id}
// DELETE /api/v1/projects/{project_id}
```

### WebSocket Events

```typescript
interface WebSocketMessage {
  type: 'agent_operation' | 'project_update' | 'capability_execution';
  payload: {
    operation: string;
    status: string;
    result?: any;
    error?: string;
  };
}
```

## Deployment

### Development
```bash
docker compose up -d
```

### Production
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Configuration
```bash
# Update agent settings
python private/config/templates/manage_config.py update-agent ExampleAgent

# Validate configuration
python private/config/templates/manage_config.py validate
```

## Monitoring & Debugging

### 1. Logs
```bash
# View service logs
docker compose logs -f

# View specific service
docker compose logs -f agent-service
```

### 2. Metrics
- Grafana dashboard: http://localhost:3000/grafana
- Prometheus metrics: http://localhost:9090

### 3. Performance Monitoring
- Frontend DevTools Performance tab
- WebSocket latency metrics
- Database query performance

## Security Considerations

### 1. Authentication
- JWT-based authentication
- Role-based access control
- API key management

### 2. Data Protection
- Environment variable management
- Secure WebSocket connections
- Database encryption

### 3. Code Security
- Dependency scanning
- Static code analysis
- Regular security updates

## Troubleshooting

### Common Issues

1. Agent Initialization Failures
   - Check configuration in `private/config/agents.yaml`
   - Verify capability requirements
   - Review service logs

2. Database Connection Issues
   - Check connection string
   - Verify migrations
   - Check database logs

3. WebSocket Connection Problems
   - Check network connectivity
   - Verify WebSocket URL
   - Review browser console logs

## Best Practices

### 1. Code Quality
- Write comprehensive tests
- Use TypeScript for type safety
- Follow project coding standards
- Document complex logic

### 2. Performance
- Optimize database queries
- Implement caching where appropriate
- Monitor memory usage
- Profile slow operations

### 3. Development Process
- Create feature branches
- Write clear commit messages
- Update documentation
- Review code changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit pull request

## Resources

- [Project Documentation](docs/)
- [API Documentation](api-docs/)
- [Contributing Guide](CONTRIBUTING.md)
