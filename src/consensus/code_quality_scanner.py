import ast
from typing import List, Dict, Any
import tensorflow as tf
import numpy as np
from pathlib import Path

class CodeQualityScanner:
    def __init__(self):
        self.model = self._load_model()
        self.code_embeddings = {}
        self.smell_patterns = {
            'long_method': {'max_lines': 50},
            'complex_condition': {'max_operators': 3},
            'duplicate_code': {'min_similarity': 0.85}
        }

    def _load_model(self) -> tf.keras.Model:
        """Load pre-trained code quality assessment model"""
        model_path = Path(__file__).parent / 'models' / 'code_quality_model'
        if model_path.exists():
            return tf.keras.models.load_model(str(model_path))
        return self._train_default_model()

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for code quality issues"""
        with open(file_path, 'r') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {'error': 'Invalid Python syntax'}

        issues = []
        issues.extend(self._detect_long_methods(tree))
        issues.extend(self._detect_complex_conditions(tree))
        issues.extend(self._detect_duplicate_code(content))

        # Get ML-based code quality score
        quality_score = self._get_quality_score(content)

        return {
            'file_path': file_path,
            'issues': issues,
            'quality_score': quality_score,
            'suggestions': self._generate_suggestions(issues)
        }

    def _detect_long_methods(self, tree: ast.AST) -> List[Dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > self.smell_patterns['long_method']['max_lines']:
                    issues.append({
                        'type': 'long_method',
                        'name': node.name,
                        'line': node.lineno,
                        'severity': 'medium'
                    })
        return issues

    def _detect_complex_conditions(self, tree: ast.AST) -> List[Dict]:
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp):
                operator_count = len(node.values) - 1
                if operator_count > self.smell_patterns['complex_condition']['max_operators']:
                    issues.append({
                        'type': 'complex_condition',
                        'line': node.lineno,
                        'severity': 'high'
                    })
        return issues

    def _detect_duplicate_code(self, content: str) -> List[Dict]:
        issues = []
        chunks = self._split_into_chunks(content)
        
        for i, chunk1 in enumerate(chunks):
            for j, chunk2 in enumerate(chunks[i+1:], i+1):
                similarity = self._calculate_similarity(chunk1, chunk2)
                if similarity > self.smell_patterns['duplicate_code']['min_similarity']:
                    issues.append({
                        'type': 'duplicate_code',
                        'chunk1_start': i * 10 + 1,
                        'chunk2_start': j * 10 + 1,
                        'similarity': similarity,
                        'severity': 'high'
                    })
        return issues

    def _get_quality_score(self, content: str) -> float:
        """Calculate code quality score using ML model"""
        embedding = self._get_code_embedding(content)
        prediction = self.model.predict(np.array([embedding]))
        return float(prediction[0][0])  # Scale 0-1

    def _generate_suggestions(self, issues: List[Dict]) -> List[str]:
        """Generate actionable suggestions for fixing detected issues"""
        suggestions = []
        for issue in issues:
            if issue['type'] == 'long_method':
                suggestions.append(
                    f"Consider breaking down method '{issue['name']}' into smaller functions"
                )
            elif issue['type'] == 'complex_condition':
                suggestions.append(
                    f"Simplify complex condition on line {issue['line']} by extracting conditions into well-named variables"
                )
            elif issue['type'] == 'duplicate_code':
                suggestions.append(
                    f"Extract duplicate code starting at lines {issue['chunk1_start']} and {issue['chunk2_start']} into a shared function"
                )
        return suggestions

    def _calculate_similarity(self, chunk1: str, chunk2: str) -> float:
        """Calculate similarity between two code chunks using embeddings"""
        emb1 = self._get_code_embedding(chunk1)
        emb2 = self._get_code_embedding(chunk2)
        return float(tf.keras.losses.cosine_similarity(emb1, emb2))

    def _get_code_embedding(self, code: str) -> np.ndarray:
        """Get vector embedding for code snippet"""
        if code not in self.code_embeddings:
            # Simple baseline: average word embeddings
            words = code.split()
            word_vectors = [self._get_word_embedding(word) for word in words]
            self.code_embeddings[code] = np.mean(word_vectors, axis=0)
        return self.code_embeddings[code]

    def _get_word_embedding(self, word: str) -> np.ndarray:
        """Get vector embedding for a single word"""
        # Placeholder: Return random embedding
        # In practice, use pre-trained code embeddings
        return np.random.randn(128)

    def _split_into_chunks(self, content: str, chunk_size: int = 10) -> List[str]:
        """Split code into chunks for duplicate detection"""
        lines = content.splitlines()
        return [
            '\n'.join(lines[i:i + chunk_size])
            for i in range(0, len(lines), chunk_size)
        ]

    def _train_default_model(self) -> tf.keras.Model:
        """Train a simple quality assessment model"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(128,)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy')
        return model
