# Implementation Plan for Agent-Project Integration

## Phase 1: Database and Schema Updates

### 1.1 Create New Migration
```python
"""add_agent_metadata_to_projects

Revision ID: add_agent_metadata
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

def upgrade():
    # Add agent_metadata column with default structure
    op.add_column('projects', sa.Column('agent_metadata', JSONB, nullable=False, server_default=sa.text("""
    '{
        "assigned_agents": [],
        "capability_requirements": [],
        "operation_history": []
    }'::jsonb
    """)))
    
    # Add validation trigger
    op.execute("""
    CREATE OR REPLACE FUNCTION validate_agent_metadata()
    RETURNS trigger AS $$
    BEGIN
        IF NOT (
            NEW.agent_metadata ? 'assigned_agents' AND
            NEW.agent_metadata ? 'capability_requirements' AND
            NEW.agent_metadata ? 'operation_history'
        ) THEN
            RAISE EXCEPTION 'Invalid agent_metadata structure';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER ensure_valid_agent_metadata
    BEFORE INSERT OR UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION validate_agent_metadata();
    """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS ensure_valid_agent_metadata ON projects")
    op.execute("DROP FUNCTION IF EXISTS validate_agent_metadata")
    op.drop_column('projects', 'agent_metadata')
```

## Phase 2: Backend Service Updates

### 2.1 Update Agent Service
```python
# backend/app/services/agent_service.py

from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID
from app.models.agent import Agent
from app.models.project import Project
from app.core.intelligence import CoreIntelligence

class AgentProjectOperation:
    def __init__(self, agent_id: str, project_id: str, capability: str):
        self.agent_id = agent_id
        self.project_id = project_id
        self.capability = capability
        self.status = "pending"
        self.timestamp = datetime.utcnow()
        self.result = None

class AgentService:
    def __init__(self, db: AsyncSession, core: CoreIntelligence):
        self.db = db
        self.core = core
    
    async def assign_to_project(
        self, 
        agent_id: str, 
        project_id: str,
        capabilities: List[str]
    ) -> Dict:
        """Assign an agent to a project with specific capabilities"""
        agent = await self.get_by_id(agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
            
        # Validate capabilities
        invalid_caps = set(capabilities) - self.VALID_CAPABILITIES
        if invalid_caps:
            raise ValueError(f"Invalid capabilities: {invalid_caps}")
            
        # Update project metadata
        async with self.db.begin():
            project = await self.db.execute(
                select(Project).filter(Project.id == project_id)
            )
            project = project.scalar_one_or_none()
            if not project:
                raise ValueError(f"Project {project_id} not found")
                
            metadata = project.agent_metadata
            if agent_id not in metadata["assigned_agents"]:
                metadata["assigned_agents"].append(agent_id)
                metadata["capability_requirements"].extend(capabilities)
                
            await self.db.commit()
            
        return {"status": "success", "message": "Agent assigned to project"}
    
    async def execute_capability(
        self,
        agent_id: str,
        project_id: str, 
        capability: str,
        params: Dict = None
    ) -> Dict:
        """Execute an agent capability on a project"""
        # Validate agent assignment
        project = await self.db.execute(
            select(Project).filter(Project.id == project_id)
        )
        project = project.scalar_one_or_none()
        if not project or agent_id not in project.agent_metadata["assigned_agents"]:
            raise ValueError("Agent not assigned to project")
            
        # Create operation record
        operation = AgentProjectOperation(agent_id, project_id, capability)
        
        try:
            # Execute via core intelligence
            result = await self.core.execute_capability(
                capability,
                {
                    "agent_id": agent_id,
                    "project_id": project_id,
                    "parameters": params or {}
                }
            )
            
            # Update operation history
            async with self.db.begin():
                metadata = project.agent_metadata
                metadata["operation_history"].append({
                    "agent_id": agent_id,
                    "capability": capability,
                    "timestamp": operation.timestamp.isoformat(),
                    "status": "completed",
                    "result": result
                })
                await self.db.commit()
                
            return result
            
        except Exception as e:
            # Log failed operation
            async with self.db.begin():
                metadata = project.agent_metadata
                metadata["operation_history"].append({
                    "agent_id": agent_id,
                    "capability": capability,
                    "timestamp": operation.timestamp.isoformat(),
                    "status": "failed",
                    "error": str(e)
                })
                await self.db.commit()
            raise
```

### 2.2 Update Project Service
```python
# backend/app/services/project_service.py

class ProjectService:
    async def get_agent_operations(
        self,
        project_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get agent operations history for a project"""
        project = await self.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
            
        history = project.agent_metadata["operation_history"]
        if status:
            history = [op for op in history if op["status"] == status]
            
        return history
        
    async def get_project_agents(
        self,
        project_id: str
    ) -> List[Dict]:
        """Get agents assigned to a project with their capabilities"""
        project = await self.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
            
        agent_ids = project.agent_metadata["assigned_agents"]
        agents = []
        
        for agent_id in agent_ids:
            agent = await self.agent_service.get_by_id(agent_id)
            if agent:
                agents.append({
                    "id": agent.id,
                    "name": agent.name,
                    "capabilities": agent.capabilities
                })
                
        return agents
```

## Phase 3: Frontend Updates

### 3.1 Update Project Types
```typescript
// dashboard/frontend/src/types/project.ts

export interface AgentOperation {
  agent_id: string;
  capability: string;
  timestamp: string;
  status: 'pending' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

export interface ProjectAgentMetadata {
  assigned_agents: string[];
  capability_requirements: string[];
  operation_history: AgentOperation[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  agent_metadata: ProjectAgentMetadata;
}
```

### 3.2 Add WebSocket Handlers
```typescript
// dashboard/frontend/src/services/websocket.ts

export interface AgentOperationMessage {
  type: 'agent_operation';
  payload: {
    project_id: string;
    agent_id: string;
    operation: AgentOperation;
  };
}

export interface ProjectUpdateMessage {
  type: 'project_update';
  payload: {
    project_id: string;
    metadata: ProjectAgentMetadata;
  };
}

export type WebSocketMessage = 
  | AgentOperationMessage
  | ProjectUpdateMessage;

export class WebSocketService {
  private socket: WebSocket;
  private reconnectAttempts = 0;
  private readonly MAX_RECONNECT_ATTEMPTS = 5;

  constructor() {
    this.socket = this.connect();
    this.setupEventHandlers();
  }

  private connect(): WebSocket {
    const socket = new WebSocket(WS_URL);
    
    socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    socket.onclose = () => {
      if (this.reconnectAttempts < this.MAX_RECONNECT_ATTEMPTS) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.socket = this.connect();
        }, 1000 * Math.pow(2, this.reconnectAttempts));
      }
    };
    
    return socket;
  }

  private setupEventHandlers() {
    this.socket.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'agent_operation':
          this.handleAgentOperation(message.payload);
          break;
        case 'project_update':
          this.handleProjectUpdate(message.payload);
          break;
      }
    };
  }

  private handleAgentOperation(payload: AgentOperationMessage['payload']) {
    // Update project state
    queryClient.setQueryData<Project[]>(['projects'], (projects) => {
      if (!projects) return projects;
      
      return projects.map(project => {
        if (project.id === payload.project_id) {
          return {
            ...project,
            agent_metadata: {
              ...project.agent_metadata,
              operation_history: [
                ...project.agent_metadata.operation_history,
                payload.operation
              ]
            }
          };
        }
        return project;
      });
    });
  }

  private handleProjectUpdate(payload: ProjectUpdateMessage['payload']) {
    queryClient.setQueryData<Project[]>(['projects'], (projects) => {
      if (!projects) return projects;
      
      return projects.map(project => {
        if (project.id === payload.project_id) {
          return {
            ...project,
            agent_metadata: payload.metadata
          };
        }
        return project;
      });
    });
  }
}
```

### 3.3 Update Projects Component
```typescript
// dashboard/frontend/src/components/Projects/Projects.tsx

export const Projects: FC = () => {
  // ... existing code ...

  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedCapability, setSelectedCapability] = useState<string | null>(null);

  // Get available agents
  const { data: agents } = useQuery(['agents'], agentApi.getAll);

  // Execute agent capability
  const executeMutation = useMutation({
    mutationFn: ({ projectId, agentId, capability }: {
      projectId: string;
      agentId: string;
      capability: string;
    }) => agentApi.executeCapability(agentId, projectId, capability),
    
    onSuccess: () => {
      queryClient.invalidateQueries(['projects']);
      toast({
        title: 'Operation started',
        status: 'success',
        duration: 3000
      });
    }
  });

  // Render agent operations history
  const renderOperationHistory = (project: Project) => {
    const history = project.agent_metadata.operation_history;
    if (!history.length) return null;

    return (
      <Box mt={4}>
        <Text fontWeight="medium" mb={2}>Operation History</Text>
        <Stack spacing={2}>
          {history.map((op, i) => (
            <Box
              key={i}
              p={2}
              borderRadius="md"
              bg={op.status === 'completed' ? 'green.50' : 'red.50'}
            >
              <Text fontSize="sm">
                {op.capability} by {op.agent_id}
              </Text>
              <Text fontSize="xs" color="gray.600">
                {new Date(op.timestamp).toLocaleString()}
              </Text>
              {op.error && (
                <Text fontSize="xs" color="red.500">
                  Error: {op.error}
                </Text>
              )}
            </Box>
          ))}
        </Stack>
      </Box>
    );
  };

  // ... rest of the component code ...
};
```

## Phase 4: Testing Updates

### 4.1 Backend Tests
```python
# backend/tests/test_agent_service.py

async def test_assign_agent_to_project():
    agent_id = "test-agent"
    project_id = "test-project"
    capabilities = ["code_review", "testing"]
    
    result = await agent_service.assign_to_project(
        agent_id,
        project_id,
        capabilities
    )
    
    assert result["status"] == "success"
    
    project = await project_service.get_by_id(project_id)
    assert agent_id in project.agent_metadata["assigned_agents"]
    assert all(cap in project.agent_metadata["capability_requirements"] 
              for cap in capabilities)

async def test_execute_capability():
    agent_id = "test-agent"
    project_id = "test-project"
    capability = "code_review"
    
    result = await agent_service.execute_capability(
        agent_id,
        project_id,
        capability
    )
    
    assert result["status"] in ["completed", "failed"]
    
    project = await project_service.get_by_id(project_id)
    history = project.agent_metadata["operation_history"]
    assert len(history) > 0
    assert history[-1]["agent_id"] == agent_id
    assert history[-1]["capability"] == capability
```

### 4.2 Frontend Tests
```typescript
// dashboard/frontend/src/components/Projects/__tests__/Projects.test.tsx

describe('Projects with Agent Integration', () => {
  beforeEach(() => {
    // Mock WebSocket
    const mockSocket = {
      send: jest.fn(),
      close: jest.fn()
    };
    (window as any).WebSocket = jest.fn(() => mockSocket);
  });

  it('should display agent operations history', async () => {
    const mockProject = {
      id: '1',
      name: 'Test Project',
      agent_metadata: {
        operation_history: [
          {
            agent_id: 'agent1',
            capability: 'code_review',
            timestamp: '2025-01-24T20:00:00Z',
            status: 'completed'
          }
        ]
      }
    };

    render(<Projects />);
    
    // Wait for project to load
    await screen.findByText('Test Project');
    
    // Verify operation history
    expect(screen.getByText('code_review by agent1')).toBeInTheDocument();
  });

  it('should handle agent capability execution', async () => {
    const mockAgent = {
      id: 'agent1',
      name: 'Test Agent',
      capabilities: ['code_review']
    };

    const mockProject = {
      id: '1',
      name: 'Test Project',
      agent_metadata: {
        assigned_agents: ['agent1'],
        operation_history: []
      }
    };

    render(<Projects />);
    
    // Select agent and capability
    await userEvent.selectOptions(
      screen.getByLabelText('Select Agent'),
      mockAgent.id
    );
    
    await userEvent.selectOptions(
      screen.getByLabelText('Select Capability'),
      'code_review'
    );
    
    // Execute capability
    await userEvent.click(screen.getByText('Execute'));
    
    // Verify success message
    expect(screen.getByText('Operation started')).toBeInTheDocument();
  });
});
```

## Implementation Schedule

1. Week 1: Database Updates
   - Create and test new migration
   - Update database models and validation

2. Week 2: Backend Services
   - Implement AgentService updates
   - Add ProjectService methods
   - Write backend tests

3. Week 3: Frontend Integration
   - Update TypeScript interfaces
   - Implement WebSocket service
   - Update Projects component
   - Add frontend tests

4. Week 4: Testing & Deployment
   - Integration testing
   - Performance testing
   - Documentation updates
   - Deployment preparation

## Success Metrics

1. Technical Metrics:
   - 95% test coverage for new code
   - < 100ms average response time for agent operations
   - Zero regression bugs in existing functionality

2. User Experience Metrics:
   - Real-time updates working reliably
   - Clear error messages and recovery paths
   - Intuitive UI for agent-project interactions

3. Integration Metrics:
   - Successful agent-project assignments
   - Reliable capability execution
   - Accurate operation history tracking
