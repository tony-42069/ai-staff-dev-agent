from typing import Dict, Optional, Any, List, Tuple
import asyncio
from datetime import datetime
import re
from fastapi import Depends
from functools import lru_cache

_core_intelligence: Optional['CoreIntelligence'] = None

@lru_cache()
def get_core_intelligence() -> 'CoreIntelligence':
    """Get or create the CoreIntelligence singleton instance"""
    global _core_intelligence
    if _core_intelligence is None:
        _core_intelligence = CoreIntelligence()
    return _core_intelligence

class CoreIntelligence:
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.command_history = []
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize regex patterns for intent extraction"""
        self.patterns = {
            'help': r'\b(help|assist|guide|how to|what can you do)\b',
            'create_agent': r'\b(create|new|add)\s+(an?\s+)?agent\b',
            'create_project': r'\b(create|new|add|start)\s+(an?\s+)?project\b',
            'assign_agent': r'\b(assign|connect|link)\s+(an?\s+)?agent\b',
            'run_analysis': r'\b(analyze|review|check|examine)\s+(the\s+)?code\b',
            'view_status': r'\b(status|progress|state|health)\b'
        }

    def _extract_intent(self, content: str) -> str:
        """Extract primary intent from message content"""
        content = content.lower()
        for intent, pattern in self.patterns.items():
            if re.search(pattern, content):
                return intent
        return 'unknown'

    def _extract_entities(self, content: str) -> Dict[str, Any]:
        """Extract relevant entities from message content"""
        entities = {}
        
        # Extract agent name
        agent_match = re.search(r'agent\s+name[d\s:]?\s*["\']?([a-zA-Z0-9_-]+)["\']?', content, re.I)
        if agent_match:
            entities['agent_name'] = agent_match.group(1)

        # Extract project name
        project_match = re.search(r'project\s+name[d\s:]?\s*["\']?([a-zA-Z0-9_-]+)["\']?', content, re.I)
        if project_match:
            entities['project_name'] = project_match.group(1)

        # Extract capabilities
        capability_matches = re.findall(r'capabilities?[:\s]\s*\[([^\]]+)\]', content, re.I)
        if capability_matches:
            capabilities = [cap.strip() for cap in capability_matches[0].split(',')]
            entities['capabilities'] = capabilities

        return entities

    def _handle_help_request(self, entities: Dict[str, Any]) -> str:
        """Handle help request with context-aware responses"""
        if 'agent' in str(entities).lower():
            return """I can help you with agent management:
- Create a new agent with: "Create agent name: AgentName capabilities: [cap1, cap2]"
- View agent status: "Show agent AgentName status"
- Assign agent to project: "Assign agent AgentName to project ProjectName"
"""
        elif 'project' in str(entities).lower():
            return """I can help you with project management:
- Create a new project: "Create project name: ProjectName"
- View project status: "Show project ProjectName status"
- List project agents: "List agents in project ProjectName"
"""
        else:
            return """I can help you with:
1. Agent Management
   - Create and configure agents
   - Monitor agent status
   - Assign agents to projects

2. Project Management
   - Create new projects
   - Track project progress
   - Manage project resources

3. Development Tasks
   - Code analysis and review
   - Testing and validation
   - Documentation generation

Try asking something specific like:
- "Create a new agent for code review"
- "Start a project for web development"
- "Analyze code in project X"
"""

    async def _handle_agent_creation(self, entities: Dict[str, Any]) -> str:
        """Handle agent creation request"""
        if not entities.get('agent_name'):
            return "Please provide an agent name. Example: 'Create agent name: ReviewAgent capabilities: [code_review, testing]'"
        
        try:
            result = await self.execute_capability(
                'agent_creation',
                {
                    'name': entities['agent_name'],
                    'capabilities': entities.get('capabilities', ['code_review']),
                    'metadata': entities
                }
            )
            if result['status'] == 'success':
                return f"Agent {entities['agent_name']} created successfully with capabilities: {', '.join(entities.get('capabilities', ['code_review']))}"
            else:
                return f"Failed to create agent: {result['message']}"
        except Exception as e:
            return f"Error creating agent: {str(e)}"

    async def _handle_project_creation(self, entities: Dict[str, Any]) -> str:
        """Handle project creation request"""
        if not entities.get('project_name'):
            return "Please provide a project name. Example: 'Create project name: WebApp'"
        
        try:
            result = await self._handle_project_generation({
                'name': entities['project_name'],
                'type': entities.get('project_type', 'generic')
            })
            if result['status'] == 'success':
                return f"Project {entities['project_name']} created successfully at {result['path']}"
            else:
                return f"Failed to create project: {result['message']}"
        except Exception as e:
            return f"Error creating project: {str(e)}"

    async def _handle_agent_assignment(self, entities: Dict[str, Any]) -> str:
        """Handle agent assignment to project"""
        if not (entities.get('agent_name') and entities.get('project_name')):
            return "Please provide both agent and project names. Example: 'Assign agent ReviewBot to project WebApp'"
        
        try:
            result = await self.execute_capability(
                'agent_assignment',
                {
                    'agent_name': entities['agent_name'],
                    'project_name': entities['project_name']
                }
            )
            if result['status'] == 'success':
                return f"Agent {entities['agent_name']} assigned to project {entities['project_name']}"
            else:
                return f"Failed to assign agent: {result['message']}"
        except Exception as e:
            return f"Error assigning agent: {str(e)}"

    async def _handle_code_analysis(self, entities: Dict[str, Any]) -> str:
        """Handle code analysis request"""
        try:
            result = await self.execute_capability(
                'code_review',
                {
                    'project_name': entities.get('project_name'),
                    'scope': entities.get('scope', 'full'),
                    'metrics': ['quality', 'complexity', 'coverage']
                }
            )
            if result['status'] == 'success':
                return f"Code analysis completed:\n- Quality Score: {result.get('quality_score', 'N/A')}\n- Issues Found: {len(result.get('findings', []))}\n- Suggestions: {len(result.get('suggestions', []))}"
            else:
                return f"Failed to analyze code: {result['message']}"
        except Exception as e:
            return f"Error analyzing code: {str(e)}"

    async def _handle_status_request(self, entities: Dict[str, Any]) -> str:
        """Handle status check request"""
        try:
            if entities.get('agent_name'):
                result = await self.execute_capability(
                    'status_check',
                    {'agent_name': entities['agent_name']}
                )
                return f"Agent {entities['agent_name']} status: {result.get('status', 'unknown')}"
            elif entities.get('project_name'):
                result = await self.execute_capability(
                    'status_check',
                    {'project_name': entities['project_name']}
                )
                return f"Project {entities['project_name']} status: {result.get('status', 'unknown')}"
            else:
                return "All systems operational. Ready to assist."
        except Exception as e:
            return f"Error checking status: {str(e)}"

    def _generate_clarifying_response(self, content: str, intent: str, entities: Dict[str, Any]) -> str:
        """Generate a response asking for clarification"""
        if not entities:
            return f"I understand you want to {intent.replace('_', ' ')}, but I need more details. Can you provide:\n" + \
                   "- Specific agent or project name\n" + \
                   "- Required capabilities or settings\n" + \
                   "- Any additional preferences"
        else:
            missing = []
            if intent in ['create_agent', 'assign_agent'] and not entities.get('agent_name'):
                missing.append('agent name')
            if intent in ['create_project', 'assign_agent'] and not entities.get('project_name'):
                missing.append('project name')
            if intent == 'create_agent' and not entities.get('capabilities'):
                missing.append('agent capabilities')
            
            if missing:
                return f"I need the following information to proceed:\n- {'\n- '.join(missing)}"
            else:
                return "I'm not sure what you'd like me to do. Try asking for 'help' to see available commands."

    async def process_message(self, content: str) -> str:
        """Process a chat message and return a response"""
        try:
            # Store message in context
            self.context['last_message'] = {
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Extract intent and entities
            intent = self._extract_intent(content)
            entities = self._extract_entities(content)

            # Update context with extracted information
            self.context.update({
                'current_intent': intent,
                'entities': entities
            })

            # Handle different intents
            if intent == 'help':
                return self._handle_help_request(entities)
            elif intent == 'create_agent':
                return await self._handle_agent_creation(entities)
            elif intent == 'create_project':
                return await self._handle_project_creation(entities)
            elif intent == 'assign_agent':
                return await self._handle_agent_assignment(entities)
            elif intent == 'run_analysis':
                return await self._handle_code_analysis(entities)
            elif intent == 'view_status':
                return await self._handle_status_request(entities)
            else:
                return self._generate_clarifying_response(content, intent, entities)

        except Exception as e:
            return f"I encountered an error processing your message: {str(e)}"

    async def process_command(self, command: str) -> str:
        """Process a command and return the result"""
        try:
            # Store command in history
            self.command_history.append({
                'command': command,
                'timestamp': datetime.utcnow().isoformat()
            })

            # Extract command and args
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []

            if cmd == '/help':
                return """Available commands:
/help - Show this help
/status [agent|project] [name] - Check status
/clear - Clear chat history
/analyze [project] [path] - Run code analysis
/assign [agent] [project] - Assign agent to project
/list [agents|projects] - List available resources"""
            
            elif cmd == '/status':
                if len(args) >= 2:
                    return await self._handle_status_request({
                        f"{args[0]}_name": args[1]
                    })
                return "All systems operational. Ready to assist."
            
            elif cmd == '/clear':
                self.context = {}
                return "Chat context cleared."
            
            elif cmd == '/analyze':
                if len(args) >= 2:
                    return await self._handle_code_analysis({
                        'project_name': args[0],
                        'path': args[1]
                    })
                return "Usage: /analyze [project] [path]"
            
            elif cmd == '/assign':
                if len(args) >= 2:
                    return await self._handle_agent_assignment({
                        'agent_name': args[0],
                        'project_name': args[1]
                    })
                return "Usage: /assign [agent] [project]"
            
            elif cmd == '/list':
                if args and args[0] in ['agents', 'projects']:
                    result = await self.execute_capability(
                        'list_resources',
                        {'resource_type': args[0]}
                    )
                    if result['status'] == 'success':
                        items = result.get('items', [])
                        return f"Available {args[0]}:\n" + "\n".join(f"- {item}" for item in items)
                    return f"Error listing {args[0]}: {result['message']}"
                return "Usage: /list [agents|projects]"

            return f"Unknown command: {command}. Type /help for available commands."

        except Exception as e:
            return f"Error executing command: {str(e)}"

    async def _handle_project_generation(self, task: Dict) -> Dict:
        """Handle project generation requests"""
        try:
            project_type = task.get('type', 'generic')
            name = task.get('name')
            
            # Enhanced project generation logic
            result = await self.execute_capability(
                'project_generation',
                {
                    'name': name,
                    'type': project_type,
                    'template': task.get('template', 'default'),
                    'settings': task.get('settings', {})
                }
            )
            
            if result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': f'Project {name} of type {project_type} generated successfully.',
                    'path': result.get('path', f'projects/{name}'),
                    'details': result.get('details', {})
                }
            else:
                return {
                    'status': 'error',
                    'message': result.get('message', 'Project generation failed')
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_context(self) -> Dict:
        """Get the current context"""
        return self.context

    def clear_context(self) -> None:
        """Clear the current context"""
        self.context = {}

    async def execute_capability(
        self,
        capability: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an agent capability"""
        try:
            # Store operation in context
            self.context['last_operation'] = {
                'capability': capability,
                'params': params,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Handle different capabilities
            if capability == 'code_review':
                return await self._handle_code_review(params)
            elif capability == 'testing':
                return await self._handle_testing(params)
            elif capability == 'development':
                return await self._handle_development(params)
            elif capability == 'documentation':
                return await self._handle_documentation(params)
            elif capability == 'deployment':
                return await self._handle_deployment(params)
            elif capability == 'project_generation':
                return await self._handle_project_generation(params)
            elif capability == 'agent_creation':
                return await self._handle_agent_creation(params)
            elif capability == 'agent_assignment':
                return await self._handle_agent_assignment(params)
            elif capability == 'list_resources':
                return await self._handle_list_resources(params)
            elif capability == 'status_check':
                return await self._handle_status_check(params)
            else:
                raise ValueError(f"Unknown capability: {capability}")

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def _handle_code_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code review capability"""
        try:
            from private.config.code_analyzer import CodeAnalyzerCapability
            analyzer = CodeAnalyzerCapability()
            
            # Get code from project if project_name is provided
            if project_name := params.get('project_name'):
                # TODO: Implement project code retrieval
                code = "# Project code here"
            else:
                code = params.get('code', '')

            analysis = analyzer.analyze_code(code)
            return {
                'status': 'success',
                'quality_score': analysis.quality_score,
                'issues': analysis.issues,
                'metrics': analysis.metrics,
                'suggestions': analysis.suggestions
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Code review failed: {str(e)}'
            }

    async def _handle_testing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle testing capability"""
        try:
            # TODO: Implement actual test execution
            return {
                'status': 'success',
                'message': 'Tests executed',
                'results': {
                    'passed': 10,
                    'failed': 2,
                    'skipped': 1,
                    'coverage': 85.5
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Testing failed: {str(e)}'
            }

    async def _handle_development(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle development capability"""
        try:
            task_type = params.get('type', 'unknown')
            # TODO: Implement actual development tasks
            return {
                'status': 'success',
                'message': f'Development task ({task_type}) completed',
                'changes': [
                    {'file': 'example.py', 'type': 'modify', 'lines': '+10/-5'}
                ]
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Development task failed: {str(e)}'
            }

    async def _handle_documentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle documentation capability"""
        try:
            # TODO: Implement actual documentation generation
            return {
                'status': 'success',
                'message': 'Documentation updated',
                'files': [
                    {'path': 'docs/README.md', 'status': 'updated'},
                    {'path': 'docs/API.md', 'status': 'created'}
                ]
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Documentation failed: {str(e)}'
            }

    async def _handle_deployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deployment capability"""
        try:
            # TODO: Implement actual deployment
            return {
                'status': 'success',
                'message': 'Deployment completed',
                'details': {
                    'environment': params.get('environment', 'production'),
                    'version': '1.0.0',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Deployment failed: {str(e)}'
            }

    async def _handle_list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource listing capability"""
        try:
            resource_type = params.get('resource_type', 'unknown')
            # TODO: Implement actual resource listing
            if resource_type == 'agents':
                return {
                    'status': 'success',
                    'items': ['DevAgent', 'TestAgent']
                }
            elif resource_type == 'projects':
                return {
                    'status': 'success',
                    'items': ['WebApp', 'MobileApp']
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown resource type: {resource_type}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to list resources: {str(e)}'
            }

    async def _handle_status_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status check capability"""
        try:
            if agent_name := params.get('agent_name'):
                # TODO: Implement actual agent status check
                return {
                    'status': 'active',
                    'last_operation': datetime.utcnow().isoformat(),
                    'capabilities': ['code_review', 'testing']
                }
            elif project_name := params.get('project_name'):
                # TODO: Implement actual project status check
                return {
                    'status': 'in_progress',
                    'completion': 75,
                    'active_agents': ['DevAgent']
                }
            else:
                return {
                    'status': 'error',
                    'message': 'No agent or project specified'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Status check failed: {str(e)}'
            }
