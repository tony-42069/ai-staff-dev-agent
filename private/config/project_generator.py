from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import shutil
import json
import yaml
from jinja2 import Environment, FileSystemLoader
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProjectTemplate:
    """Data class for project template configuration"""
    name: str
    description: str
    files: List[Dict[str, str]]  # List of {path: template_name}
    dependencies: Dict[str, List[str]]  # Language: list of dependencies
    configuration: Dict[str, Any]  # Project-specific config

class ProjectGeneratorCapability:
    """Capability for generating new projects from templates"""
    
    def __init__(self):
        self.name = "project_generator"
        self.description = "Generates new projects from templates with proper structure and configuration"
        self.requirements = [
            {
                "name": "jinja2",
                "type": "package",
                "version": ">=3.0.0"
            }
        ]
        self.parameters = {
            "template_path": "private/config/templates/projects",
            "default_template": "python_package"
        }
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize Jinja2 environment and load templates"""
        self.template_path = Path(self.parameters["template_path"])
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, ProjectTemplate]:
        """Load all project templates from the template directory"""
        templates = {}
        
        # Load each template configuration
        for config_file in self.template_path.glob("*/template.yaml"):
            try:
                with config_file.open() as f:
                    config = yaml.safe_load(f)
                
                template = ProjectTemplate(
                    name=config["name"],
                    description=config.get("description", ""),
                    files=config["files"],
                    dependencies=config.get("dependencies", {}),
                    configuration=config.get("configuration", {})
                )
                templates[config["name"]] = template
                logger.info(f"Loaded template: {template.name}")
            except Exception as e:
                logger.error(f"Error loading template {config_file}: {e}")
        
        return templates

    def generate_project(
        self,
        name: str,
        template_name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a new project from a template
        
        Args:
            name: Project name
            template_name: Template to use (default: python_package)
            settings: Project-specific settings
            
        Returns:
            Dict containing generation results
        """
        try:
            # Get template
            template_name = template_name or self.parameters["default_template"]
            if template_name not in self.templates:
                raise ValueError(f"Unknown template: {template_name}")
            
            template = self.templates[template_name]
            settings = settings or {}
            
            # Create project directory
            project_dir = Path(f"projects/{name}")
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate files from templates
            generated_files = []
            for file_info in template.files:
                for path, template_name in file_info.items():
                    try:
                        # Render template
                        template = self.env.get_template(f"{template_name}.j2")
                        content = template.render(
                            project_name=name,
                            **settings,
                            **template.configuration
                        )
                        
                        # Write file
                        file_path = project_dir / path
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content)
                        generated_files.append(str(file_path))
                    except Exception as e:
                        logger.error(f"Error generating {path}: {e}")
                        return {
                            "status": "error",
                            "message": f"Failed to generate {path}: {str(e)}"
                        }
            
            # Generate dependency files
            self._generate_dependency_files(project_dir, template, settings)
            
            # Generate project configuration
            config = {
                "name": name,
                "template": template_name,
                "settings": settings,
                "dependencies": template.dependencies,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            config_path = project_dir / "project.json"
            config_path.write_text(json.dumps(config, indent=2))
            
            return {
                "status": "success",
                "message": f"Project {name} generated successfully",
                "path": str(project_dir),
                "files": generated_files,
                "config": config
            }
            
        except Exception as e:
            logger.error(f"Project generation failed: {e}")
            return {
                "status": "error",
                "message": f"Project generation failed: {str(e)}"
            }

    def _generate_dependency_files(
        self,
        project_dir: Path,
        template: ProjectTemplate,
        settings: Dict[str, Any]
    ):
        """Generate dependency management files"""
        try:
            # Python requirements.txt
            if "python" in template.dependencies:
                reqs = template.dependencies["python"]
                if settings.get("python_version"):
                    reqs.append(f"# Python {settings['python_version']}")
                (project_dir / "requirements.txt").write_text("\n".join(reqs))
            
            # Node package.json
            if "node" in template.dependencies:
                pkg = {
                    "name": project_dir.name,
                    "version": "1.0.0",
                    "dependencies": {},
                    "devDependencies": {}
                }
                
                for dep in template.dependencies["node"]:
                    if dep.startswith("-"):
                        pkg["devDependencies"][dep[1:]] = "*"
                    else:
                        pkg["dependencies"][dep] = "*"
                
                (project_dir / "package.json").write_text(
                    json.dumps(pkg, indent=2)
                )
            
            # Docker files
            if settings.get("docker", False):
                dockerfile = self.env.get_template("Dockerfile.j2")
                (project_dir / "Dockerfile").write_text(
                    dockerfile.render(
                        project_name=project_dir.name,
                        **settings
                    )
                )
                
                compose = self.env.get_template("docker-compose.yml.j2")
                (project_dir / "docker-compose.yml").write_text(
                    compose.render(
                        project_name=project_dir.name,
                        **settings
                    )
                )
        
        except Exception as e:
            logger.error(f"Error generating dependency files: {e}")
            raise

    def list_templates(self) -> List[Dict[str, str]]:
        """List available project templates"""
        return [
            {
                "name": template.name,
                "description": template.description
            }
            for template in self.templates.values()
        ]

    def get_template_details(self, template_name: str) -> Dict[str, Any]:
        """Get detailed information about a template"""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
            
        template = self.templates[template_name]
        return {
            "name": template.name,
            "description": template.description,
            "files": [list(f.keys())[0] for f in template.files],
            "dependencies": template.dependencies,
            "configuration": template.configuration
        }

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the project generation capability
        
        Args:
            task: Dictionary containing:
                - name: Project name
                - template: Optional template name
                - settings: Optional project settings
                
        Returns:
            Dictionary containing generation results
        """
        name = task.get("name")
        if not name:
            return {
                "status": "error",
                "message": "Project name is required"
            }

        if task.get("list_templates"):
            return {
                "status": "success",
                "templates": self.list_templates()
            }

        if template_name := task.get("template_details"):
            try:
                return {
                    "status": "success",
                    "template": self.get_template_details(template_name)
                }
            except ValueError as e:
                return {
                    "status": "error",
                    "message": str(e)
                }

        return self.generate_project(
            name,
            task.get("template"),
            task.get("settings")
        )
