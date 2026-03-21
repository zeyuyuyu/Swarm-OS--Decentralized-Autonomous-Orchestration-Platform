# Advanced AI-Powered Code Review and Technical Debt Analysis Module
# Part of DevMind-AI: Intelligent Developer Tools Platform

"""
DevMind-AI: AI-Powered Code Review and Technical Debt Analyzer

This module provides comprehensive static analysis, code quality scoring,
technical debt quantification, and AI-driven remediation suggestions.

Features:
- Multi-language code analysis
- Cyclomatic complexity calculation
- Technical debt tracking and estimation
- AI-powered code smell detection
- Automated refactoring suggestions
- Integration with CI/CD pipelines
- Technical debt ROI calculator
- Code quality trend analysis

Author: DevMind-AI Team
License: MIT
Version: 1.0.0
"""

import ast
import re
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from collections import defaultdict
import math
import statistics
import os
from pathlib import Path

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class SeverityLevel(Enum):
    """Code issue severity classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    def color_code(self) -> str:
        """Return ANSI color code for terminal output."""
        colors = {
            "critical": "\033[91m",
            "high": "\033[93m",
            "medium": "\033[33m",
            "low": "\033[94m",
            "info": "\033[90m"
        }
        return colors.get(self.value, "\033[0m")


class CodeSmellType(Enum):
    """Standard code smell classifications."""
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    DUPLICATED_CODE = "duplicated_code"
    DEAD_CODE = "dead_code"
    MAGIC_NUMBERS = "magic_numbers"
    LONG_PARAMETER_LIST = "long_parameter_list"
    DATA_CLUMP = "data_clump"
   FeatureEnvy = "feature_envy"
    INAPPROPRIATE_INTIMACY = "inappropriate_intimacy"
    REFUSED_BEQUEST = "refused_bequest"
    SWITCH_STATEMENTS = "switch_statements"
    PARALLEL_INHERITANCE = "parallel_inheritance"
    LAZY_CLASS = "lazy_class"
    SPECULATIVE_GENERALITY = "speculative_generality"
    TEMPORARY_FIELD = "temporary_field"
    MESSAGE_CHAINS = "message_chains"
    MIDDLE_MAN = "middle_man"
    INSIDE_CRAWLING = "inside_crawling"
    ALTERNATIVE_CLASSES = "alternative_classes"
    GOD_CLASS = "god_class"


@dataclass
class CodeIssue:
    """Represents a single code issue or smell."""
    issue_id: str
    smell_type: CodeSmellType
    severity: SeverityLevel
    file_path: str
    line_number: int
    end_line: Optional[int] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    description: str = ""
    suggestion: str = ""
    effort_minutes: int = 0
    technical_debt_hours: float = 0.0
    related_issues: List[str] = field(default_factory=list)
    ai_generated: bool = False
    confidence_score: float = 0.0
    remediation_steps: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.description:
            self.description = self._generate_description()
        if not self.suggestion:
            self.suggestion = self._generate_suggestion()

    def _generate_description(self) -> str:
        """Generate human-readable issue description."""
        descriptions = {
            CodeSmellType.LONG_METHOD: "Method exceeds recommended line count",
            CodeSmellType.LARGE_CLASS: "Class has too many responsibilities",
            CodeSmellType.DUPLICATED_CODE: "Similar code pattern detected",
            CodeSmellType.DEAD_CODE: "Unreachable or unused code detected",
            CodeSmellType.MAGIC_NUMBERS: "Unnamed constant values found",
            CodeSmellType.LONG_PARAMETER_LIST: "Method has too many parameters",
            CodeSmellType.DATA_CLUMP: "Same group of parameters passed together",
            CodeSmellType.FeatureEnvy: "Method overly depends on another class",
            CodeSmellType.GOD_CLASS: "Class controls too many other classes",
        }
        return descriptions.get(self.smell_type, "Code smell detected")

    def _generate_suggestion(self) -> str:
        """Generate initial remediation suggestion."""
        suggestions = {
            CodeSmellType.LONG_METHOD: "Consider breaking into smaller, focused methods",
            CodeSmellType.LARGE_CLASS: "Apply Single Responsibility Principle",
            CodeSmellType.DUPLICATED_CODE: "Extract common logic into shared function",
            CodeSmellType.DEAD_CODE: "Remove unused code paths",
            CodeSmellType.MAGIC_NUMBERS: "Define as named constants",
            CodeSmellType.LONG_PARAMETER_LIST: "Consider using parameter object pattern",
            CodeSmellType.GOD_CLASS: "Extract related behaviors into collaborator classes",
        }
        return suggestions.get(self.smell_type, "Review and refactor this code section")


@dataclass
class ComplexityMetrics:
    """Code complexity metrics container."""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    maintainability_index: float = 100.0
    halstead_volume: float = 0.0
    comment_ratio: float = 0.0
    depth_of_inheritance: int = 0
    coupling: int = 0
    cohesion: float = 0.0


@dataclass
class TechnicalDebtRecord:
    """Detailed technical debt information."""
    issue_id: str
    category: str
    description: str
    estimated_hours: float
    interest_rate_percent: float
    first_seen: datetime
    last_seen: datetime
    affected_files: List[str]
    business_impact: str
    remediation_cost: float
    priority: int

    @property
    def age_days(self) -> int:
        """Calculate age in days."""
        return (datetime.now() - self.first_seen).days

    @property
    def compounded_debt(self) -> float:
        """Calculate compounded technical debt with interest."""
        days = self.age_days
        if days == 0:
            return self.estimated_hours
        rate = self.interest_rate_percent / 100
        return self.estimated_hours * ((1 + rate) ** (days / 365))


@dataclass
class FileAnalysisResult:
    """Complete analysis results for a single file."""
    file_path: str
    language: str
    timestamp: datetime
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    issues: List[CodeIssue]
    complexity: ComplexityMetrics
    technical_debt_minutes: int
    quality_score: float
    passed_checks: List[str]
    failed_checks: List[str]
    warnings: List[str]
    hash: str


@dataclass
class ProjectAnalysisReport:
    """Comprehensive project-level analysis report."""
    project_path: str
    analysis_timestamp: datetime
    total_files: int
    total_lines: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    total_technical_debt_hours: float
    average_quality_score: float
    maintainability_rating: str
    file_results: Dict[str, FileAnalysisResult]
    trends: Dict[str, Any]
    recommendations: List[str]
    ai_insights: str

    def to_dict(self) -> Dict:
        """Convert report to dictionary for serialization."""
        result = asdict(self)
        result['analysis_timestamp'] = self.analysis_timestamp.isoformat()
        for fr in result['file_results'].values():
            fr['timestamp'] = fr['timestamp'].isoformat()
        return result


class AdvancedPatternMatcher:
    """Sophisticated pattern detection for code analysis."""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.ml_model_weights = self._load_model_weights()

    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for code smell detection."""
        return {
            'magic_number': re.compile(r'\b\d{1,5}\b'),
            'console_log': re.compile(r'console\.(log|debug|info|warn|error)', re.I),
            'TODO': re.compile(r'(TODO|FIXME|HACK|XXX):?\s*(.*)', re.I),
            'nested_callbacks': re.compile(r'\.then\(|\.catch\(|callback\('),
            'sql_concatenation': re.compile(r'["\'].*?(?:SELECT|INSERT|UPDATE|DELETE).*?["\']\s*\+'),
            'hardcoded_credentials': re.compile(
                r'(?:password|secret|api_key|token)\s*[:=]\s*["\'][^"\'\s]{8,}["\']',
                re.I
            ),
            'print_statements': re.compile(r'print\s*\(|System\.out\.print'),
            'empty_catch': re.compile(r'except\s*\([^)]*\)\s*:\s*pass\s*(?:#|$)', re.I | re.M),
            'complex_regex': re.compile(r're\.compile\([^,]{50,}\)'),
        }

    def _load_model_weights(self) -> Dict[str, float]:
        """Load heuristic weights for pattern scoring."""
        return {
            'magic_number': 0.3,
            'console_log': 0.4,
            'TODO': 0.2,
            'nested_callbacks': 0.5,
            'sql_concatenation': 0.9,
            'hardcoded_credentials': 1.0,
            'print_statements': 0.3,
            'empty_catch': 0.6,
            'complex_regex': 0.4,
        }

    def detect_patterns(self, code: str, line_offset: int = 0) -> List[Dict]:
        """Detect various code patterns and return findings."""
        findings = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, start=1):
            for pattern_name, pattern in self.patterns.items():
                matches = list(pattern.finditer(line))
                for match in matches:
                    weight = self.ml_model_weights.get(pattern_name, 0.5)
                    findings.append({
                        'pattern': pattern_name,
                        'line': line_num + line_offset,
                        'column': match.start(),
                        'matched_text': match.group(),
                        'severity': self._calculate_severity(pattern_name, match),
                        'confidence': weight,
                        'suggestion': self._get_pattern_suggestion(pattern_name)
                    })

        return findings

    def _calculate_severity(self, pattern_name: str, match: re.Match) -> SeverityLevel:
        """Calculate severity based on pattern and context."""
        severity_map = {
            'hardcoded_credentials': SeverityLevel.CRITICAL,
            'sql_concatenation': SeverityLevel.HIGH,
            'empty_catch': SeverityLevel.MEDIUM,
            'magic_number': SeverityLevel.LOW,
            'console_log': SeverityLevel.INFO,
            'print_statements': SeverityLevel.INFO,
        }
        return severity_map.get(pattern_name, SeverityLevel.MEDIUM)

    def _get_pattern_suggestion(self, pattern_name: str) -> str:
        """Get remediation suggestion for pattern."""
        suggestions = {
            'magic_number': 'Replace with named constant',
            'console_log': 'Use structured logging framework',
            'sql_concatenation': 'Use parameterized queries',
            'hardcoded_credentials': 'Use environment variables or secrets manager',
            'empty_catch': 'Handle exception properly or log issue',
            'print_statements': 'Use proper logging framework',
        }
        return suggestions.get(pattern_name, 'Review this code pattern')


class PythonCodeAnalyzer:
    """Specialized Python code analyzer with AST parsing."""

    COMPLEXITY_WEIGHTS = {
        'if': 1,
        'elif': 1,
        'else': 1,
        'for': 1,
        'while': 1,
        'except': 1,
        'with': 1,
        'and': 1,
        'or': 1,
        'try': 1,
        'finally': 1,
    }

    def __init__(self):
        self.max_method_lines = 50
        self.max_parameters = 5
        self.max_class_methods = 20

    def analyze_file(self, file_path: str, content: Optional[str] = None) -> FileAnalysisResult:
        """Perform comprehensive analysis on Python file."""
        if content is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        file_hash = hashlib.md5(content.encode()).hexdigest()

        tree = ast.parse(content)
        lines = content.split('\n')

        complexity = self._calculate_complexity(tree)
        issues = self._detect_code_smells(tree, content, file_path)
        metrics = self._calculate_metrics(tree, content, lines)

        complexity.maintainability_index = self._calculate_maintainability_index(
            metrics.lines_of_code,
            complexity.cyclomatic_complexity,
            metrics.comment_ratio
        )

        technical_debt = sum(issue.technical_debt_hours * 60 for issue in issues)
        quality_score = self._calculate_quality_score(complexity, issues, metrics)

        return FileAnalysisResult(
            file_path=file_path,
            language='python',
            timestamp=datetime.now(),
            lines_of_code=metrics.lines_of_code,
            lines_of_comments=metrics.comment_ratio * metrics.lines_of_code,
            blank_lines=sum(1 for l in lines if not l.strip()),
            issues=issues,
            complexity=complexity,
            technical_debt_minutes=technical_debt,
            quality_score=quality_score,
            passed_checks=self._get_passed_checks(metrics, complexity),
            failed_checks=self._get_failed_checks(issues),
            warnings=self._generate_warnings(issues),
            hash=file_hash
        )

    def _calculate_complexity(self, tree: ast.AST) -> ComplexityMetrics:
        """Calculate cyclomatic and cognitive complexity."""
        complexity = ComplexityMetrics()
        visitor = ComplexityVisitor()
        visitor.visit(tree)

        complexity.cyclomatic_complexity = visitor.cyclomatic
        complexity.cognitive_complexity = visitor.cognitive
        complexity.depth_of_inheritance = visitor.max_depth
        complexity.comment_ratio = visitor.comment_ratio

        return complexity

    def _detect_code_smells(
        self, tree: ast.AST, content: str, file_path: str
    ) -> List[CodeIssue]:
        """Detect various code smells using AST analysis."""
        issues = []
        visitor = CodeSmellVisitor(file_path)
        visitor.visit(tree)

        for smell in visitor.detected_smells:
            issue = CodeIssue(
                issue_id=self._generate_issue_id(file_path, smell['line']),
                smell_type=smell['type'],
                severity=smell['severity'],
                file_path=file_path,
                line_number=smell['line'],
                end_line=smell.get('end_line'),
                function_name=smell.get('function'),
                class_name=smell.get('class'),
                effort_minutes=self._estimate_effort(smell['type']),
                technical_debt_hours=self._estimate_debt(smell['type'], smell['severity']),
                confidence_score=smell.get('confidence', 0.8)
            )
            issues.append(issue)

        return issues

    def _calculate_metrics(
        self, tree: ast.AST, content: str, lines: List[str]
    ) -> ComplexityMetrics:
        """Calculate detailed code metrics."""
        loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        comment_ratio = comment_lines / len(lines) if lines else 0

        metrics = ComplexityMetrics(
            lines_of_code=loc,
            comment_ratio=comment_ratio
        )

        return metrics

    def _calculate_maintainability_index(
        self, loc: int, complexity: int, comment_ratio: float
    ) -> float:
        """Calculate maintainability index (0-100 scale)."""
        if loc == 0:
            return 100.0

        # Halstead volume approximation
        volume = loc * math.log2(max(complexity, 1))

        # Calculate MI using Microsoft formula
        mi = 171 - 5.2 * math.log(volume + 1) - 0.23 * complexity - 16.2 * math.log(loc + 1)
        mi += 50 * math.sin(2.6 * comment_ratio * math.pi / 180)

        return max(0.0, min(100.0, mi))

    def _calculate_quality_score(
        self, complexity: ComplexityMetrics,
        issues: List[CodeIssue], metrics: ComplexityMetrics
    ) -> float:
        """Calculate overall code quality score (0-100)."""
        base_score = 100.0

        # Deduct for complexity
        complexity_penalty = min(30, complexity.cyclomatic_complexity * 0.5)

        # Deduct for maintainability
        maintainability_penalty = max(0, (100 - complexity.maintainability_index) * 0.3)

        # Deduct for issues
        issue_penalties = {
            SeverityLevel.CRITICAL: 15,
            SeverityLevel.HIGH: 8,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.LOW: 1,
            SeverityLevel.INFO: 0.5,
        }
        issue_penalty = sum(issue_penalties[i.severity] for i in issues)

        score = base_score - complexity_penalty - maintainability_penalty - issue_penalty
        return max(0.0, min(100.0, score))

    def _estimate_effort(self, smell_type: CodeSmellType) -> int:
        """Estimate remediation effort in minutes."""
        effort_map = {
            CodeSmellType.LONG_METHOD: 120,
            CodeSmellType.LARGE_CLASS: 240,
            CodeSmellType.DUPLICATED_CODE: 60,
            CodeSmellType.DEAD_CODE: 15,
            CodeSmellType.MAGIC_NUMBERS: 30,
            CodeSmellType.GOD_CLASS: 480,
        }
        return effort_map.get(smell_type, 60)

    def _estimate_debt(self, smell_type: CodeSmellType, severity: SeverityLevel) -> float:
        """Estimate technical debt in hours."""
        base_debt = {
            CodeSmellType.LONG_METHOD: 2.0,
            CodeSmellType.LARGE_CLASS: 4.0,
            CodeSmellType.DUPLICATED_CODE: 1.0,
            CodeSmellType.GOD_CLASS: 8.0,
            CodeSmellType.MAGIC_NUMBERS: 0.5,
        }
        severity_multiplier = {
            SeverityLevel.CRITICAL: 3.0,
            SeverityLevel.HIGH: 2.0,
            SeverityLevel.MEDIUM: 1.0,
            SeverityLevel.LOW: 0.5,
            SeverityLevel.INFO: 0.1,
        }

        base = base_debt.get(smell_type, 1.0)
        multiplier = severity_multiplier.get(severity, 1.0)
        return base * multiplier

    def _generate_issue_id(self, file_path: str, line: int) -> str:
        """Generate unique issue ID."""
        hash_input = f"{file_path}:{line}:{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _get_passed_checks(self, metrics: ComplexityMetrics, complexity: ComplexityMetrics) -> List[str]:
        """Return list of passed quality checks."""
        checks = []
        if metrics.comment_ratio >= 0.15:
            checks.append("good_comment_coverage")
        if complexity.cyclomatic_complexity <= 10:
            checks.append("low_complexity")
        if metrics.lines_of_code <= 500:
            checks.append("reasonable_file_size")
        return checks

    def _get_failed_checks(self, issues: List[CodeIssue]) -> List[str]:
        """Return list of failed quality checks."""
        return [f"issue_{issue.smell_type.value}" for issue in issues]

    def _generate_warnings(self, issues: List[CodeIssue]) -> List[str]:
        """Generate warning messages for issues."""
        warnings = []
        critical = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
        if critical:
            warnings.append(f"Critical issues detected: {len(critical)} require immediate attention")
        return warnings


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor for calculating complexity metrics."""

    def __init__(self):
        self.cyclomatic = 1
        self.cognitive = 0
        self.max_depth = 0
        self.current_depth = 0
        self.comment_ratio = 0.0
        self.total_lines = 0
        self.comment_lines = 0
        self._in_function = False
        self._function_complexity = 0

    def visit(self, node: ast.AST) -> None:
        """Override visit to track depth."""
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        old_complexity = self._function_complexity
        old_depth = self.current_depth
        old_in_func = self._in_function

        self._in_function = True
        self._function_complexity = 1
        self.current_depth = 0

        self.generic_visit(node)

        self.cognitive += self._function_complexity
        self.max_depth = max(self.max_depth, self.current_depth)

        self._function_complexity = old_complexity
        self.current_depth = old_depth
        self._in_function = old_in_func

    def visit_If(self, node: ast.If) -> None:
        """Visit if statement."""
        self.cyclomatic += 1
        self._function_complexity += 1
        if self._in_function:
            self.cognitive += 1 + self.current_depth
        self.current_depth += 1
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_For(self, node: ast.For) -> None:
        """Visit for loop."""
        self.cyclomatic += 1
        self._function_complexity += 1
        if self._in_function:
            self.cognitive += 1 + self.current_depth
        self.current_depth += 1
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node: ast.While) -> None:
        """Visit while loop."""
        self.cyclomatic += 1
        self._function_complexity += 1
        if self._in_function:
            self.cognitive += 1 + self.current_depth
        self.current_depth += 1
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit exception handler."""
        self.cyclomatic += 1
        self._function_complexity += 1
        if self._in_function:
            self.cognitive += 1 + self.current_depth
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        """Visit boolean operations (and/or)."""
        for _ in node.values:
            self.cyclomatic += 1
        self.generic_visit(node)


class CodeSmellVisitor(ast.NodeVisitor):
    """AST visitor for detecting code smells."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.detected_smells = []
        self.class_stack = []
        self.function_stack = []
        self.method_lines = defaultdict(int)
        self.class_method_counts = defaultdict(int)
        self.parameter_counts = defaultdict(int)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition and check for smells."""
        self.class_stack.append(node.name)
        method_count = 0

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_count += 1

        if method_count > 20:
            self.detected_smells.append({
                'type': CodeSmellType.LARGE_CLASS,
                'severity': SeverityLevel.HIGH if method_count > 30 else SeverityLevel.MEDIUM,
                'line': node.lineno,
                'end_line': node.end_lineno,
                'class': node.name,
                'confidence': 0.85
            })

        if self._is_god_class(node):
            self.detected_smells.append({
                'type': CodeSmellType.GOD_CLASS,
                'severity': SeverityLevel.CRITICAL,
                'line': node.lineno,
                'end_line': node.end_lineno,
                'class': node.name,
                'confidence': 0.90
            })

        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition and check for smells."""
        self.function_stack.append(node.name)

        # Track method lines
        if self.class_stack:
            class_name = self.class_stack[-1]
            key = f"{class_name}.{node.name}"
            self.method_lines[key] = node.end_lineno - node.lineno + 1 if node.end_lineno else 1
            self.class_method_counts[class_name] += 1

            # Check for long method
            line_count = self.method_lines[key]
            if line_count > 50:
                self.detected_smells.append({
                    'type': CodeSmellType.LONG_METHOD,
                    'severity': SeverityLevel.HIGH if line_count > 100 else SeverityLevel.MEDIUM,
                    'line': node.lineno,
                    'end_line': node.end_lineno,
                    'function': node.name,
                    'class': self.class_stack[-1] if self.class_stack else None,
                    'confidence': min(0.95, 0.6 + (line_count / 200))
                })

        # Check for long parameter list
        param_count = len(node.args.args)
        if param_count > 5:
            self.detected_smells.append({
                'type': CodeSmellType.LONG_PARAMETER_LIST,
                'severity': SeverityLevel.MEDIUM,
                'line': node.lineno,
                'function': node.name,
                'class': self.class_stack[-1] if self.class_stack else None,
                'confidence': 0.80
            })

        # Check for complex nested functions
        nested_depth = self._get_nesting_depth(node)
        if nested_depth > 4:
            self.detected_smells.append({
                'type': CodeSmellType.MESSAGE_CHAINS,
                'severity': SeverityLevel.MEDIUM,
                'line': node.lineno,
                'function': node.name,
                'confidence': 0.75
            })

        self.generic_visit(node)
        self.function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to detect patterns."""
        # Check for print statements
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.detected_smells.append({
                'type': CodeSmellType.MAGIC_NUMBERS,
                'severity': SeverityLevel.INFO,
                'line': node.lineno,
                'confidence': 0.60
            })

        self.generic_visit(node)

    def _is_god_class(self, node: ast.ClassDef) -> bool:
        """Check if class has god class characteristics."""
        public_methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith('_'):
                    public_methods.append(item)

        # Check for many public methods
        if len(public_methods) > 15:
            return True

        # Check for large body
        if node.end_lineno and (node.end_lineno - node.lineno) > 500:
            return True

        return False

    def _get_nesting_depth(self, node: ast.AST) -> int:
        """Calculate nesting depth of a node."""
        depth = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                depth += 1
        return depth


class AICodeReviewer:
    """AI-powered code review integration."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = Anthropic(api_key=self.api_key) if self.api_key and ANTHROPIC_AVAILABLE else None
        self.model = "claude-sonnet-4-20250514"

    def generate_review(
        self, code: str, language: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered code review."""
        if not self.client:
            return self._generate_fallback_review(code, language)

        try:
            prompt = self._build_review_prompt(code, language, context)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system="You are an expert code reviewer with deep knowledge of software engineering best practices, design patterns, and clean code principles. Provide constructive, actionable feedback.",
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                'success': True,
                'review': response.content[0].text,
                'model': self.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'review': self._generate_fallback_review(code, language)
            }

    def _build_review_prompt(
        self, code: str, language: str, context: Optional[Dict]
    ) -> str:
        """Build prompt for AI review."""
        context_str = f"\n\nContext: {json.dumps(context)}" if context else ""

        return f"""Review the following {language} code and provide a comprehensive analysis:

```
{code}
```

{context_str}

Please provide your review in JSON format with the following structure:
{{
    "summary": "Brief overview of code quality",
    "strengths": ["list of positive aspects"],
    "issues": [
        {{
            "severity": "critical|high|medium|low",
            "category": "security|performance|style|maintainability|best_practice",
            "description": "Description of the issue",
            "line_reference": "Line number or range",
            "suggestion": "How to fix",
            "rationale": "Why this matters"
        }}
    ],
    "refactoring_suggestions": ["Specific refactoring ideas"],
    "security_concerns": ["Any security issues found"],
    "performance_tips": ["Performance optimization suggestions"],
    "overall_rating": "A-F grade or 1-10 score"
}}
"""

    def _generate_fallback_review(self, code: str, language: str) -> Dict[str, Any]:
        """Generate basic review when AI is not available."""
        lines = code.split('\n')
        issues = []

        # Basic checks
        if len(lines) > 500:
            issues.append({
                'severity': 'medium',
                'category': 'maintainability',
                'description': 'File is quite large',
                'suggestion': 'Consider breaking into smaller modules'
            })

        # Check for common issues
        if 'print(' in code and language == 'python':
            issues.append({
                'severity': 'low',
                'category': 'best_practice',
                'description': 'Print statement found',
                'suggestion': 'Use proper logging framework'
            })

        return {
            'success': False,
            'review': None,
            'fallback_issues': issues,
            'note': 'AI review unavailable - providing basic pattern analysis'
        }


class TechnicalDebtCalculator:
    """Calculate and track technical debt."""

    DEBT_INTEREST_RATES = {
        CodeSmellType.LONG_METHOD: 0.05,
        CodeSmellType.LARGE_CLASS: 0.08,
        CodeSmellType.DUPLICATED_CODE: 0.03,
        CodeSmellType.GOD_CLASS: 0.12,
        CodeSmellType.MAGIC_NUMBERS: 0.02,
    }

    def __init__(self):
        self.records: List[TechnicalDebtRecord] = []

    def calculate_total_debt(
        self, issues: List[CodeIssue], project_age_days: int = 365
    ) -> Dict[str, Any]:
        """Calculate total technical debt from issues."""
        total_hours = 0.0
        by_category = defaultdict(float)
        by_severity = defaultdict(lambda: {'count': 0, 'hours': 0.0})

        for issue in issues:
            debt = issue.technical_debt_hours
            interest_rate = self.DEBT_INTEREST_RATES.get(
                issue.smell_type, 0.05
            )

            # Apply compounding interest
            compounded = debt * ((1 + interest_rate) ** (project_age_days / 365))
            total_hours += compounded

            by_category[issue.smell_type.value] += compounded
            by_severity[issue.severity.value]['count'] += 1
            by_severity[issue.severity.value]['hours'] += compounded

        return {
            'total_hours': round(total_hours, 2),
            'total_days': round(total_hours / 8, 2),
            'by_category': dict(by_category),
            'by_severity': dict(by_severity),
            'remediation_priority': self._calculate_priority(by_severity)
        }

    def calculate_roi(
        self, debt_hours: float, fix_cost_hours: float, annual_maintenance_hours: float
    ) -> Dict[str, float]:
        """Calculate ROI for debt remediation."""
        current_annual_cost = annual_maintenance_hours
        post_fix_annual_cost = annual_maintenance_hours * 0.3  # 70% reduction estimate

        annual_savings = current_annual_cost - post_fix_annual_cost
        payback_months = (fix_cost_hours / annual_savings) * 12 if annual_savings > 0 else float('inf')

        roi_1_year = ((annual_savings - fix_cost_hours) / fix_cost_hours) * 100 if fix_cost_hours > 0 else 0

        return {
            'roi_percentage': round(roi_1_year, 2),
            'payback_months': round(payback_months, 1),
            'annual_savings_hours': round(annual_savings, 2),
            'net_benefit_3yr': round((annual_savings * 3) - fix_cost_hours, 2)
        }

    def _calculate_priority(
        self, by_severity: Dict[str, Dict]
    ) -> List[Dict[str, Any]]:
        """Calculate remediation priority order."""
        priority = []

        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                priority.append({
                    'severity': severity,
                    'count': by_severity[severity]['count'],
                    'hours': by_severity[severity]['hours']
                })

        return priority


class ProjectAnalyzer:
    """Main project analyzer coordinating all analysis."""

    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cs': 'csharp',
    }

    def __init__(self, api_key: Optional[str] = None):
        self.python_analyzer = PythonCodeAnalyzer()
        self.pattern_matcher = AdvancedPatternMatcher()
        self.ai_reviewer = AICodeReviewer(api_key)
        self.debt_calculator = TechnicalDebtCalculator()
        self.cache: Dict[str, FileAnalysisResult] = {}

    def analyze_project(
        self,
        project_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        use_ai_review: bool = False,
        incremental: bool = False
    ) -> ProjectAnalysisReport:
        """Perform comprehensive project analysis."""

        project_path = Path(project_path)
        include_patterns = include_patterns or ['**/*.py']
        exclude_patterns = exclude_patterns or [
            '__pycache__', '*.pyc', '.git', 'node_modules',
            '.venv', 'venv', 'build', 'dist', '.pytest_cache'
        ]

        file_results = {}
        all_issues = []

        for pattern in include_patterns:
            for file_path in project_path.glob(pattern):
                if self._should_exclude(file_path, exclude_patterns):
                    continue

                result = self.analyze_file(str(file_path), incremental)
                file_results[str(file_path)] = result
                all_issues.extend(result.issues)

        # Calculate totals
        total_files = len(file_results)
        total_lines = sum(r.lines_of_code for r in file_results.values())

        issue_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }
        for issue in all_issues:
            issue_counts[issue.severity.value] += 1

        total_debt = self.debt_calculator.calculate_total_debt(all_issues)
        avg_quality = statistics.mean([r.quality_score for r in file_results.values()]) if file_results else 100.0

        # Generate AI insights if enabled
        ai_insights = ""
        if use_ai_review and all_issues:
            top_issues = sorted(all_issues, key=lambda x: x.severity.value)[:5]
            ai_insights = self._generate_ai_insights(top_issues)

        return ProjectAnalysisReport(
            project_path=str(project_path),
            analysis_timestamp=datetime.now(),
            total_files=total_files,
            total_lines=total_lines,
            total_issues=len(all_issues),
            critical_issues=issue_counts['critical'],
            high_issues=issue_counts['high'],
            medium_issues=issue_counts['medium'],
            low_issues=issue_counts['low'],
            total_technical_debt_hours=total_debt['total_hours'],
            average_quality_score=round(avg_quality, 2),
            maintainability_rating=self._get_maintainability_rating(avg_quality),
            file_results=file_results,
            trends=self._calculate_trends(file_results),
            recommendations=self._generate_recommendations(issue_counts, total_debt),
            ai_insights=ai_insights
        )

    def analyze_file(
        self, file_path: str, use_cache: bool = False
    ) -> FileAnalysisResult:
        """Analyze a single file."""
        file_path = Path(file_path)

        if use_cache and str(file_path) in self.cache:
            return self.cache[str(file_path)]

        ext = file_path.suffix.lower()
        language = self.LANGUAGE_EXTENSIONS.get(ext, 'unknown')

        if language == 'python':
            result = self.python_analyzer.analyze_file(str(file_path))
        else:
            # Generic analysis for other languages
            result = self._generic_analysis(file_path, language)

        # Add pattern-based detection
        content = file_path.read_text(errors='ignore')
        patterns = self.pattern_matcher.detect_patterns(content)

        for pattern in patterns:
            issue = CodeIssue(
                issue_id=self._generate_id(),
                smell_type=CodeSmellType.MAGIC_NUMBERS,
                severity=pattern['severity'],
                file_path=str(file_path),
                line_number=pattern['line'],
                description=f"Pattern detected: {pattern['pattern']}",
                suggestion=pattern['suggestion'],
                technical_debt_hours=0.5,
                confidence_score=pattern['confidence'],
                ai_generated=False
            )
            result.issues.append(issue)

        # Update quality score
        result.quality_score = self._recalculate_quality(result)

        self.cache[str(file_path)] = result
        return result

    def _generic_analysis(
        self, file_path: Path, language: str
    ) -> FileAnalysisResult:
        """Perform generic analysis for unsupported languages."""
        content = file_path.read_text(errors='ignore')
        lines = content.split('\n')

        loc = len([l for l in lines if l.strip()])
        comments = len([l for l in lines if l.strip().startswith(('//', '#', '/*', '*'))])

        metrics = ComplexityMetrics(
            lines_of_code=loc,
            comment_ratio=comments / loc if loc > 0 else 0
        )

        return FileAnalysisResult(
            file_path=str(file_path),
            language=language,
            timestamp=datetime.now(),
            lines_of_code=loc,
            lines_of_comments=comments,
            blank_lines=sum(1 for l in lines if not l.strip()),
            issues=[],
            complexity=metrics,
            technical_debt_minutes=0,
            quality_score=85.0,
            passed_checks=['generic_analysis'],
            failed_checks=[],
            warnings=[],
            hash=hashlib.md5(content.encode()).hexdigest()
        )

    def _should_exclude(self, path: Path, patterns: List[str]) -> bool:
        """Check if path should be excluded."""
        path_str = str(path)
        for pattern in patterns:
            if pattern in path_str:
                return True
        return False

    def _recalculate_quality(self, result: FileAnalysisResult) -> float:
        """Recalculate quality score after adding pattern issues."""
        base = result.quality_score
        for issue in result.issues:
            penalties = {
                SeverityLevel.CRITICAL: 15,
                SeverityLevel.HIGH: 8,
                SeverityLevel.MEDIUM: 3,
                SeverityLevel.LOW: 1,
            }
            base -= penalties.get(issue.severity, 0.5)
        return max(0.0, min(100.0, base))

    def _generate_id(self) -> str:
        """Generate unique ID."""
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12]

    def _get_maintainability_rating(self, score: float) -> str:
        """Get maintainability rating from score."""
        if score >= 90:
            return "A - Excellent"
        elif score >= 80:
            return "B - Good"
        elif score >= 70:
            return "C - Moderate"
        elif score >= 50:
            return "D - Problematic"
        else:
            return "F - Critical"

    def _calculate_trends(self, file_results: Dict[str, FileAnalysisResult]) -> Dict[str, Any]:
        """Calculate quality trends."""
        if not file_results:
            return {}

        quality_scores = [r.quality_score for r in file_results.values()]
        debt_hours = [r.technical_debt_minutes / 60 for r in file_results.values()]

        return {
            'avg_quality_trend': 'stable',
            'quality_distribution': {
                'excellent': len([s for s in quality_scores if s >= 90]),
                'good': len([s for s in quality_scores if 80 <= s < 90]),
                'moderate': len([s for s in quality_scores if 70 <= s < 80]),
                'problematic': len([s for s in quality_scores if s < 70]),
            },
            'debt_distribution': {
                'min_hours': min(debt_hours) if debt_hours else 0,
                'max_hours': max(debt_hours) if debt_hours else 0,
                'avg_hours': statistics.mean(debt_hours) if debt_hours else 0,
            }
        }

    def _generate_recommendations(
        self, issue_counts: Dict[str, int], debt_info: Dict
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if issue_counts['critical'] > 0:
            recommendations.append(
                f"🚨 Address {issue_counts['critical']} critical issues immediately - they pose significant risk"
            )

        if issue_counts['high'] > 0:
            recommendations.append(
                f"⚠️ Plan to fix {issue_counts['high']} high-severity issues in current sprint"
            )

        if debt_info['total_hours'] > 40:
            recommendations.append(
                f"📊 Technical debt: {debt_info['total_hours']:.1f} hours ({(debt_info['total_hours']/8):.1f} days). "
                "Consider dedicated refactoring sprints."
            )

        # Category-specific recommendations
        by_category = debt_info.get('by_category', {})
        if by_category.get('long_method', 0) > 10:
            recommendations.append(
                "📝 Multiple long methods detected. Consider applying Extract Method pattern."
            )

        if by_category.get('duplicated_code', 0) > 5:
            recommendations.append(
                "🔄 Code duplication found. Extract common logic into shared utilities."
            )

        return recommendations

    def _generate_ai_insights(self, top_issues: List[CodeIssue]) -> str:
        """Generate AI-powered insights for top issues."""
        if not self.ai_reviewer.client:
            return "AI insights unavailable (no API key configured)"

        # Batch review for efficiency
        insights = []
        for issue in top_issues[:3]:
            try:
                file_path = Path(issue.file_path)
                content = file_path.read_text(errors='ignore')
                lines = content.split('\n')

                # Extract context around issue
                start = max(0, issue.line_number - 10)
                end = min(len(lines), issue.line_number + 10)
                context = '\n'.join(lines[start:end])

                result = self.ai_reviewer.generate_review(
                    context,
                    'python',
                    {
                        'issue_type': issue.smell_type.value,
                        'severity': issue.severity.value,
                        'function': issue.function_name
                    }
                )

                if result.get('success'):
                    insights.append(result['review'])

            except Exception:
                continue

        return '\n\n---\n\n'.join(insights) if insights else "Unable to generate AI insights"


class CIIntegration:
    """CI/CD pipeline integration utilities."""

    @staticmethod
    def generate_sarif_report(report: ProjectAnalysisReport) -> Dict:
        """Generate SARIF format report for CI integration."""
        results = []

        for file_path, file_result in report.file_results.items():
            for issue in file_result.issues:
                results.append({
                    'ruleId': f'devmind/{issue.smell_type.value}',
                    'level': issue.severity.value,
                    'message': {
                        'text': issue.description,
                        'properties': {
                            'suggestion': issue.suggestion,
                            'confidence': issue.confidence_score,
                            'technicalDebtHours': issue.technical_debt_hours
                        }
                    },
                    'locations': [{
                        'physicalLocation': {
                            'artifactLocation': {
                                'uri': file_path
                            },
                            'region': {
                                'startLine': issue.line_number,
                                'endLine': issue.end_line or issue.line_number
                            }
                        }
                    }]
                })

        return {
            'version': '2.1.0',
            '$schema': 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json',
            'runs': [{
                'tool': {
                    'driver': {
                        'name': 'DevMind-AI',
                        'version': '1.0.0',
                        'informationUri': 'https://github.com/devmind-ai/devmind-ai'
                    }
                },
                'results': results
            }]
        }

    @staticmethod
    def generate_github_annotations(report: ProjectAnalysisReport) -> List[Dict]:
        """Generate GitHub Actions annotations."""
        annotations = []

        for file_path, file_result in report.file_results.items():
            for issue in file_result.issues:
                if issue.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                    annotations.append({
                        'path': file_path,
                        'start_line': issue.line_number,
                        'end_line': issue.end_line or issue.line_number,
                        'annotation_level': 'failure' if issue.severity == SeverityLevel.CRITICAL else 'warning',
                        'message': f"[{issue.smell_type.value}] {issue.description} - {issue.suggestion}",
                        'title': issue.smell_type.value.replace('_', ' ').title()
                    })

        return annotations

    @staticmethod
    def generate_junit_xml(report: ProjectAnalysisReport) -> str:
        """Generate JUnit XML format for CI integration."""
        test_cases = []

        for file_path, file_result in report.file_results.items():
            for issue in file_result.issues:
                test_cases.append(f"""
        <testcase name="{issue.smell_type.value}" classname="{file_path}" time="0">
            <failure message="{issue.description}" type="{issue.severity.value}">
                {issue.suggestion}
            </failure>
        </testcase>
                """)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="DevMind-AI Code Analysis" tests="{report.total_issues}" failures="{report.critical_issues + report.high_issues}">
    {''.join(test_cases)}
</testsuite>
"""


class ReportExporter:
    """Export analysis reports in various formats."""

    @staticmethod
    def export_json(report: ProjectAnalysisReport, output_path: str) -> None:
        """Export report as JSON."""
        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

    @staticmethod
    def export_html(report: ProjectAnalysisReport, output_path: str) -> None:
        """Export report as HTML dashboard."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevMind-AI Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ color: #666; font-size: 0.9em; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .stat-card.critical .value {{ color: #e74c3c; }}
        .stat-card.high .value {{ color: #f39c12; }}
        .stat-card.medium .value {{ color: #3498db; }}
        .issues-list {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .issue {{ padding: 15px; border-left: 4px solid; margin-bottom: 10px; background: #f9f9f9; border-radius: 5px; }}
        .issue.critical {{ border-color: #e74c3c; }}
        .issue.high {{ border-color: #f39c12; }}
        .issue.medium {{ border-color: #3498db; }}
        .issue-header {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
        .severity {{ padding: 2px 8px; border-radius: 3px; font-size: 0.8em; color: white; }}
        .severity.critical {{ background: #e74c3c; }}
        .severity.high {{ background: #f39c12; }}
        .severity.medium {{ background: #3498db; }}
        .recommendations {{ background: white; border-radius: 10px; padding: 20px; margin-top: 20px; }}
        .recommendation {{ padding: 10px; margin-bottom: 10px; background: #f0f8ff; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DevMind-AI Analysis Report</h1>
            <p>Project: {report.project_path}</p>
            <p>Analyzed: {report.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Quality Score</h3>
                <div class="value">{report.average_quality_score:.1f}</div>
            </div>
            <div class="stat-card critical">
                <h3>Critical Issues</h3>
                <div class="value">{report.critical_issues}</div>
            </div>
            <div class="stat-card high">
                <h3>High Issues</h3>
                <div class="value">{report.high_issues}</div>
            </div>
            <div class="stat-card medium">
                <h3>Medium Issues</h3>
                <div class="value">{report.medium_issues}</div>
            </div>
            <div class="stat-card">
                <h3>Tech Debt (hrs)</h3>
                <div class="value">{report.total_technical_debt_hours:.1f}</div>
            </div>
            <div class="stat-card">
                <h3>Maintainability</h3>
                <div class="value">{report.maintainability_rating}</div>
            </div>
        </div>

        <div class="recommendations">
            <h2>Recommendations</h2>
            {''.join(f'<div class="recommendation">{r}</div>' for r in report.recommendations)}
        </div>
    </div>
</body>
</html>"""

        with open(output_path, 'w') as f:
            f.write(html)


# Main CLI Interface
def main():
    """CLI entry point for DevMind-AI analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='DevMind-AI Code Analysis Tool')
    parser.add_argument('project_path', help='Path to project to analyze')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'html', 'sarif', 'junit'],
                        default='json', help='Output format')
    parser.add_argument('--ai-review', action='store_true', help='Enable AI-powered review')
    parser.add_argument('--include', '-i', action='append', help='Include patterns')
    parser.add_argument('--exclude', '-e', action='append', help='Exclude patterns')
    parser.add_argument('--incremental', action='store_true', help='Use cached results')

    args = parser.parse_args()

    analyzer = ProjectAnalyzer(api_key=os.getenv('ANTHROPIC_API_KEY'))
    report = analyzer.analyze_project(
        args.project_path,
        include_patterns=args.include,
        exclude_patterns=args.exclude,
        use_ai_review=args.ai_review,
        incremental=args.incremental
    )

    if args.output:
        if args.format == 'json':
            ReportExporter.export_json(report, args.output)
        elif args.format == 'html':
            ReportExporter.export_html(report, args.output)
        elif args.format == 'sarif':
            sarif = CIIntegration.generate_sarif_report(report)
            with open(args.output, 'w') as f:
                json.dump(sarif, f, indent=2)
        elif args.format == 'junit':
            junit = CIIntegration.generate_junit_xml(report)
            with open(args.output, 'w') as f:
                f.write(junit)
    else:
        print(json.dumps(report.to_dict(), indent=2, default=str))


if __name__ == '__main__':
    main()
