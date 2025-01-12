from typing import Dict, Optional, Any
import asyncio
from datetime import datetime

class CoreIntelligence:
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.command_history = []

    async def process_message(self, content: str) -> str:
        """Process a chat message and return a response"""
        try:
            # Store message in context
            self.context['last_message'] = {
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Basic response logic - will be enhanced later
            if 'help' in content.lower():
                return "I can help you with:\n- Creating and managing agents\n- Setting up projects\n- Running development tasks\n\nTry asking me something specific!"
            
            if 'create' in content.lower() and 'agent' in content.lower():
                return "To create a new agent, please provide:\n- Name\n- Description\n- Capabilities\n\nOr use the Agents page in the dashboard."

            if 'project' in content.lower():
                return "I can help you manage projects. Would you like to:\n- Create a new project\n- View existing projects\n- Assign agents to a project"

            # Default response
            return "I understand you're saying: '{}'. How can I assist you with that?".format(content)

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

            # Basic command processing - will be enhanced later
            if command.startswith('/help'):
                return "Available commands:\n/help - Show this help\n/status - Check agent status\n/clear - Clear chat history"
            
            if command.startswith('/status'):
                return "All systems operational. Ready to assist."
            
            if command.startswith('/clear'):
                self.context = {}
                return "Chat context cleared."

            return f"Unknown command: {command}. Type /help for available commands."

        except Exception as e:
            return f"Error executing command: {str(e)}"

    async def _handle_project_generation(self, task: Dict) -> Dict:
        """Handle project generation requests"""
        try:
            project_type = task.get('type')
            name = task.get('name')
            
            # Basic project generation logic - will be enhanced later
            return {
                'status': 'success',
                'message': f'Project {name} of type {project_type} is being generated.',
                'path': f'projects/{name}'
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