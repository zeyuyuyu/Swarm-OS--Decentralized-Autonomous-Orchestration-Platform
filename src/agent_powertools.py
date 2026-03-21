# Agent Powertools - Core capabilities for AI agents

from typing import Dict, List, Optional, Union
import logging
import json
import yaml
from pathlib import Path
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentContext:
    """Stores runtime context for an agent"""
    agent_id: str
    capabilities: List[str]
    working_directory: Path
    config: Dict

class AgentPowertools:
    """Core utilities and capabilities for AI agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.context = None
        self._load_agent_context()
    
    def _load_agent_context(self) -> None:
        """Load agent configuration and set up context"""
        try:
            agent_config_path = Path(f'./agents/{self.agent_id}.yaml')
            if not agent_config_path.exists():
                raise FileNotFoundError(f'No config found for agent {self.agent_id}')
                
            with open(agent_config_path) as f:
                config = yaml.safe_load(f)
                
            self.context = AgentContext(
                agent_id=self.agent_id,
                capabilities=config.get('capabilities', []),
                working_directory=Path('./'),
                config=config
            )
            logger.info(f'Loaded context for agent {self.agent_id}')
            
        except Exception as e:
            logger.error(f'Failed to load agent context: {str(e)}')
            raise
    
    def analyze_codebase(self, path: Union[str, Path]) -> Dict:
        """Analyze a codebase or file and return metrics"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'Path does not exist: {path}')
            
        metrics = {
            'files_analyzed': 0,
            'lines_of_code': 0,
            'file_types': {}
        }
        
        if path.is_file():
            self._analyze_file(path, metrics)
        else:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    self._analyze_file(file_path, metrics)
                    
        return metrics
    
    def _analyze_file(self, file_path: Path, metrics: Dict) -> None:
        """Analyze a single file and update metrics"""
        metrics['files_analyzed'] += 1
        
        extension = file_path.suffix
        if extension not in metrics['file_types']:
            metrics['file_types'][extension] = 0
        metrics['file_types'][extension] += 1
        
        try:
            with open(file_path) as f:
                line_count = sum(1 for _ in f)
                metrics['lines_of_code'] += line_count
        except Exception as e:
            logger.warning(f'Failed to analyze file {file_path}: {str(e)}')
    
    def get_agent_capability(self, capability: str) -> Optional[Dict]:
        """Get configuration for a specific agent capability"""
        if not self.context:
            raise RuntimeError('Agent context not loaded')
            
        if capability not in self.context.capabilities:
            return None
            
        return self.context.config.get('capability_config', {}).get(capability)
    
    def store_analysis_result(self, analysis_type: str, result: Dict) -> None:
        """Store analysis results in a structured format"""
        output_dir = Path('./analysis_results')
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f'{self.agent_id}_{analysis_type}.json'
        
        try:
            with open(output_file, 'w') as f:
                json.dump({
                    'agent_id': self.agent_id,
                    'analysis_type': analysis_type,
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                }, f, indent=2)
            logger.info(f'Stored analysis result in {output_file}')
            
        except Exception as e:
            logger.error(f'Failed to store analysis result: {str(e)}')
            raise
    
    def load_analysis_result(self, analysis_type: str) -> Optional[Dict]:
        """Load previously stored analysis results"""
        result_file = Path(f'./analysis_results/{self.agent_id}_{analysis_type}.json')
        
        if not result_file.exists():
            return None
            
        try:
            with open(result_file) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f'Failed to load analysis result: {str(e)}')
            return None

if __name__ == '__main__':
    # Example usage
    tools = AgentPowertools('code_quality_auditor')
    
    # Analyze codebase
    metrics = tools.analyze_codebase('./src')
    print(f'Codebase metrics: {metrics}')
    
    # Get capability config
    linting_config = tools.get_agent_capability('linting')
    print(f'Linting configuration: {linting_config}')
    
    # Store analysis results
    tools.store_analysis_result('code_quality', {
        'quality_score': 0.85,
        'issues_found': 12,
        'recommendations': ['Fix lint errors', 'Add more comments']
    })
