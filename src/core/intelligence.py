"""
Core Intelligence Engine for AI Agent Development Framework
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass
import logging
from pathlib import Path
import yaml
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base class for all AI agents"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the agent"""
        pass
        
    @abstractmethod
    def cleanup(self) -> bool:
        """Clean up agent resources"""
        pass
        
    @abstractmethod
    def execute_task(self, task: Dict) -> Dict:
        """Execute a task"""
        pass

@dataclass
class AgentCapability:
    """Defines a specific capability that an agent can have"""
    name: str
    description: str
    requirements: List[str]
    parameters: Dict[str, Union[str, int, float, bool]]
    implementation: str  # Python code as string

@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    name: str
    version: str
    capabilities: List[str]
    parameters: Dict[str, Union[str, int, float, bool]]
    security_level: str
    environment: Dict[str, str]

@dataclass
class Capability:
    """Simplified capability implementation"""
    name: str
    description: str
    handler: Callable[[Dict], Dict]

    def execute(self, task: Dict) -> Dict:
        try:
            return self.handler(task)
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

class CoreIntelligence:
    """Core Intelligence Engine for managing AI agents"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.capabilities: Dict[str, AgentCapability] = {}
        self.agents: Dict[str, AgentConfig] = {}
        self._load_configurations()
        self._initialize_core_capabilities()

    def _load_configurations(self):
        """Load core configurations from protected directory"""
        try:
            with open(self.config_path / 'capabilities.yaml', 'r') as f:
                capabilities_data = yaml.safe_load(f)
                for cap_data in capabilities_data:
                    capability = AgentCapability(**cap_data)
                    self.capabilities[capability.name] = capability

            with open(self.config_path / 'agents.yaml', 'r') as f:
                agents_data = yaml.safe_load(f)
                for agent_data in agents_data:
                    agent = AgentConfig(**agent_data)
                    self.agents[agent.name] = agent
                    
        except Exception as e:
            logger.error(f"Error loading configurations: {str(e)}")
            raise

    def _initialize_core_capabilities(self):
        """Initialize core development capabilities"""
        self.capabilities['project_generation'] = Capability(
            name='project_generation',
            description='Creates new project structures',
            handler=self._handle_project_generation
        )
    
        self.capabilities['code_generation'] = Capability(
            name='code_generation', 
            description='Generates code and tests',
            handler=self._handle_code_generation
        )

        self.capabilities['agent_creation'] = Capability(
            name='agent_creation',
            description='Creates new AI agents',
            handler=self._handle_agent_creation
        )

        self.capabilities['development_tasks'] = Capability(
            name='development_tasks',
            description='Handles development tasks',
            handler=self._handle_development_tasks
        )

    def _handle_project_generation(self, task: Dict) -> Dict:
        """Handle project generation requests"""
        project_type = task.get('type')
        name = task.get('name')
        return {'status': 'success', 'path': f'projects/{name}'}

    def _handle_code_generation(self, task: Dict) -> Dict:
        """Handle code generation requests"""
        try:
            language = task.get('language', 'python')
            code_spec = task.get('specification')

            # Basic code generation logic
            return {
                'status': 'success',
                'code': f'# Generated {language} code\n# Based on specification',
                'language': language
            }
        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _handle_agent_creation(self, task: Dict) -> Dict:
        """Handle agent creation requests"""
        try:
            agent_type = task.get('agent_type')
            capabilities = task.get('capabilities', [])

            # Basic agent creation logic
            return {
                'status': 'success',
                'agent_type': agent_type,
                'capabilities': capabilities
            }
        except Exception as e:
            logger.error(f"Error in agent creation: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _handle_development_tasks(self, task: Dict) -> Dict:
        """Handle development tasks"""
        try:
            task_type = task.get('task_type')
            parameters = task.get('parameters', {})

            # Basic development task handling
            return {
                'status': 'success',
                'task_type': task_type,
                'result': 'Task completed'
            }
        except Exception as e:
            logger.error(f"Error in development task: {str(e)}")
            return {'status': 'error', 'message': str(e)}

class AgentFactory:
    """Factory for creating new AI agents"""
    
    def __init__(self, core_intelligence: CoreIntelligence):
        self.core = core_intelligence

    def create_agent(self, config: AgentConfig) -> Agent:
        """Simplified agent creation"""
        class DynamicAgent(Agent):
            def __init__(self, core):
                self.name = config.name
                self.version = config.version
                self.core = core
                self.capabilities = {
                    cap: self.core.capabilities[cap] 
                    for cap in config.capabilities
                }

            def initialize(self) -> bool:
                logger.info(f"Initializing {self.name}")
                return True

            def cleanup(self) -> bool:
                logger.info(f"Cleaning up {self.name}")
                return True

            def execute_task(self, task: Dict) -> Dict:
                capability = task.get('capability')
                if capability not in self.capabilities:
                    raise ValueError(f"Unknown capability: {capability}")
                return self.capabilities[capability].execute(task)

        return DynamicAgent(self.core)

    def _generate_agent_files(self, agent_dir: Path, config: AgentConfig):
        """Generate necessary files for the agent"""
        # Generate main agent class
        self._generate_main_class(agent_dir, config)
        
        # Generate capability implementations
        self._generate_capabilities(agent_dir, config)
        
        # Generate tests
        self._generate_tests(agent_dir, config)
        
        # Generate configuration
        self._generate_config(agent_dir, config)

    def _generate_main_class(self, agent_dir: Path, config: AgentConfig):
        """Generate the main agent class file"""
        try:
            template = self._load_template('agent_class.py.template')
            logger.info(f"Formatting template for agent: {config.name}")
            
            # Use a dictionary for string formatting
            format_dict = {
                'name': config.name,
                'version': config.version
            }
            
            content = template.safe_substitute(format_dict) if hasattr(template, 'safe_substitute') else template.format(**format_dict)
            
            with open(agent_dir / 'agent.py', 'w') as f:
                f.write(content)
                    
        except Exception as e:
            logger.error(f"Error generating main class: {str(e)}")
            raise

    def _generate_capabilities(self, agent_dir: Path, config: AgentConfig):
        """Generate capability implementations"""
        try:
            cap_dir = agent_dir / 'capabilities'
            cap_dir.mkdir(exist_ok=True)
            
            template = self._load_template('capability.py.template')
            
            for cap_name in config.capabilities:
                capability = self.core.capabilities[cap_name]
                content = template.format(
                    name=cap_name,
                    description=capability.description,
                    implementation=capability.implementation
                )
                
                with open(cap_dir / f'{cap_name}.py', 'w') as f:
                    f.write(content)
                    
        except Exception as e:
            logger.error(f"Error generating capabilities: {str(e)}")
            raise

    def _generate_tests(self, agent_dir: Path, config: AgentConfig):
        """Generate test files for the agent"""
        try:
            test_dir = agent_dir / 'tests'
            test_dir.mkdir(exist_ok=True)
            
            template = self._load_template('test_agent.py.template')
            content = template.format(
                name=config.name,
                capabilities=", ".join(config.capabilities)
            )
            
            with open(test_dir / 'test_agent.py', 'w') as f:
                f.write(content)
                
        except Exception as e:
            logger.error(f"Error generating tests: {str(e)}")
            raise

    def _generate_config(self, agent_dir: Path, config: AgentConfig):
        """Generate agent configuration file"""
        try:
            with open(agent_dir / 'config.yaml', 'w') as f:
                yaml.dump(config.__dict__, f)
        except Exception as e:
            logger.error(f"Error generating config: {str(e)}")
            raise

    def _load_template(self, template_name: str) -> str:
        """Load a template file from the protected templates directory"""
        try:
            template_path = self.core.config_path / 'templates' / template_name
            logger.info(f"Loading template: {template_path}")
            
            with open(template_path, 'r') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            raise

class AgentManager:
    """Manages running AI agents"""
    
    def __init__(self, core_intelligence: CoreIntelligence):
        self.core = core_intelligence
        self.factory = AgentFactory(core_intelligence)
        self.running_agents: Dict[str, 'Agent'] = {}

    def start_agent(self, agent_name: str) -> bool:
        """Start an AI agent"""
        try:
            if (agent_name not in self.core.agents):
                raise ValueError(f"Unknown agent: {agent_name}")
                
            config = self.core.agents[agent_name]
            agent = self._load_agent(config)
            
            if agent and agent.initialize():
                self.running_agents[agent_name] = agent
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error starting agent: {str(e)}")
            return False

    def stop_agent(self, agent_name: str) -> bool:
        """Stop a running AI agent"""
        try:
            if agent_name not in self.running_agents:
                raise ValueError(f"Agent not running: {agent_name}")
                
            agent = self.running_agents[agent_name]
            if agent.cleanup():
                del self.running_agents[agent_name]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error stopping agent: {str(e)}")
            return False

    def _load_agent(self, config: AgentConfig) -> Optional['Agent']:
        """Dynamic agent loading"""
        try:
            agent_path = Path(f"agents/{config.name}/agent.py")
            if not agent_path.exists():
                agent = self.factory.create_agent(config)
                return agent
            
            # Load existing agent
            spec = importlib.util.spec_from_file_location(
                config.name, agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            agent_class = getattr(module, f"{config.name}Agent")
            return agent_class()
            
        except Exception as e:
            logger.error(f"Error loading agent: {str(e)}")
            return None
