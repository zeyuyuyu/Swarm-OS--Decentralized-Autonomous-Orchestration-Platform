import ast
from typing import Dict, List, Set, Optional
import os
import re

class CodeQualityScanner:
    def __init__(self):
        self.security_patterns = {
            'sql_injection': r'.*execute\(.*%.*\)',
            'command_injection': r'os\.system\(.*\)|subprocess\.call\(.*\)',
            'unsafe_yaml': r'yaml\.load\(',
            'hardcoded_secrets': r'password\s*=\s*[\'"].*[\'"]|api_key\s*=\s*[\'"].*[\'"]'
        }
        
        self.performance_patterns = {
            'nested_loops': 0,
            'large_memory_ops': [],
            'inefficient_list_ops': []
        }

    def scan_file(self, filepath: str) -> Dict[str, List[str]]:
        """Scan a single file for code quality issues"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'File {filepath} not found')

        with open(filepath, 'r') as f:
            content = f.read()

        issues = {
            'security': self._check_security(content, filepath),
            'performance': self._check_performance(content, filepath),
            'maintainability': self._check_maintainability(content)
        }

        return issues

    def _check_security(self, content: str, filepath: str) -> List[str]:
        """Check for security vulnerabilities"""
        issues = []
        
        for issue_type, pattern in self.security_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(
                    f'{filepath}:{line_num} - Potential {issue_type} vulnerability detected'
                )

        return issues

    def _check_performance(self, content: str, filepath: str) -> List[str]:
        """Analyze code for performance issues"""
        issues = []
        tree = ast.parse(content)

        class PerformanceVisitor(ast.NodeVisitor):
            def __init__(self):
                self.loop_depth = 0
                self.issues = []

            def visit_For(self, node):
                self.loop_depth += 1
                if self.loop_depth > 2:
                    line_num = node.lineno
                    self.issues.append(
                        f'{filepath}:{line_num} - Nested loop detected (depth {self.loop_depth})'
                    )
                self.generic_visit(node)
                self.loop_depth -= 1

            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['copy', 'deepcopy']:
                        self.issues.append(
                            f'{filepath}:{node.lineno} - Large memory operation detected'
                        )
                self.generic_visit(node)

        visitor = PerformanceVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)

        return issues

    def _check_maintainability(self, content: str) -> List[str]:
        """Check code maintainability metrics"""
        issues = []
        tree = ast.parse(content)

        class MaintainabilityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.function_lines = []
                self.complexity = 0
                self.issues = []

            def visit_FunctionDef(self, node):
                func_lines = len(node.body)
                if func_lines > 50:
                    self.issues.append(
                        f'Function {node.name} is too long ({func_lines} lines)'
                    )
                self.generic_visit(node)

            def visit_If(self, node):
                self.complexity += 1
                self.generic_visit(node)

        visitor = MaintainabilityVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)

        if visitor.complexity > 10:
            issues.append(f'High cyclomatic complexity detected ({visitor.complexity})')

        return issues

    def scan_directory(self, directory: str) -> Dict[str, Dict[str, List[str]]]:
        """Scan an entire directory recursively"""
        results = {}
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        results[filepath] = self.scan_file(filepath)
                    except Exception as e:
                        results[filepath] = {'error': [str(e)]}

        return results

    def generate_report(self, scan_results: Dict[str, Dict[str, List[str]]]) -> str:
        """Generate a formatted report from scan results"""
        report = ['Code Quality Scan Report', '=' * 50, '']

        total_issues = 0
        for filepath, issues in scan_results.items():
            file_issues = sum(len(issue_list) for issue_list in issues.values())
            if file_issues > 0:
                report.append(f'\nFile: {filepath}')
                report.append('-' * len(filepath))
                
                for category, category_issues in issues.items():
                    if category_issues:
                        report.append(f'\n{category.title()}:')
                        for issue in category_issues:
                            report.append(f'  - {issue}')
                        total_issues += len(category_issues)

        report.append(f'\nTotal issues found: {total_issues}')
        return '\n'.join(report)
