"""
feature_extractor.py — Unified feature extractor for tree-sitter and native Python ASTs.
"""

import statistics
from collections import Counter
from typing import Optional, Any

import numpy as np

from ast_parser import ASTParser


# ── Generic Node Groups ───────────────────────────────────────────────────────
GENERIC_NODE_TYPES: list[str] = [
    'function_def',
    'class_def',
    'return_stmt',
    'assignment',
    'loop',
    'conditional',
    'try_catch',
    'import_stmt',
    'call_expr',
    'binary_op',
    'identifier',
    'literal',
]

_NODE_INDEX: dict[str, int] = {name: i for i, name in enumerate(GENERIC_NODE_TYPES)}
NUM_NODE_FEATURES: int = len(GENERIC_NODE_TYPES)

# A heuristic mapping from various tree-sitter language node types AND Native AST types to our generic types
NODE_MAPPING = {
    # Functions
    'function_definition': 'function_def', # TS: Python, C++
    'method_declaration': 'function_def',  # TS: Java
    'method_definition': 'function_def',   # TS: JS/C++
    'function_declaration': 'function_def', # TS: JS
    'arrow_function': 'function_def',      # TS: JS
    'FunctionDef': 'function_def',         # Native: Python
    'AsyncFunctionDef': 'function_def',    # Native: Python
    # Classes
    'class_definition': 'class_def',       # TS: Python
    'class_declaration': 'class_def',      # TS: Java, JS
    'class_specifier': 'class_def',        # TS: C++
    'ClassDef': 'class_def',               # Native: Python
    # Returns
    'return_statement': 'return_stmt',     # TS
    'Return': 'return_stmt',               # Native
    # Assignments
    'assignment': 'assignment',            # TS: Python
    'assignment_expression': 'assignment', # TS: JS, Java, C++
    'variable_declarator': 'assignment',   # TS: Java, JS
    'local_variable_declaration': 'assignment', # TS: Java
    'init_declarator': 'assignment',       # TS: C++
    'Assign': 'assignment',                # Native
    'AnnAssign': 'assignment',             # Native
    'AugAssign': 'assignment',             # Native
    # Loops
    'for_statement': 'loop',               # TS
    'while_statement': 'loop',             # TS
    'do_statement': 'loop',                # TS
    'For': 'loop',                         # Native
    'AsyncFor': 'loop',                    # Native
    'While': 'loop',                       # Native
    # Conditionals
    'if_statement': 'conditional',         # TS
    'switch_statement': 'conditional',     # TS
    'If': 'conditional',                   # Native
    # Try/Catch
    'try_statement': 'try_catch',          # TS
    'catch_clause': 'try_catch',           # TS
    'except_clause': 'try_catch',          # TS: Python
    'Try': 'try_catch',                    # Native
    'TryFinally': 'try_catch',             # Native
    'TryExcept': 'try_catch',              # Native
    # Imports
    'import_statement': 'import_stmt',     # TS
    'import_from_statement': 'import_stmt',# TS
    'preproc_include': 'import_stmt',      # TS
    'Import': 'import_stmt',               # Native
    'ImportFrom': 'import_stmt',           # Native
    # Calls
    'call': 'call_expr',                   # TS: Python
    'call_expression': 'call_expr',        # TS: JS, C++
    'method_invocation': 'call_expr',      # TS: Java
    'Call': 'call_expr',                   # Native
    # Binary Ops
    'binary_operator': 'binary_op',        # TS
    'binary_expression': 'binary_op',      # TS
    'boolean_operator': 'binary_op',       # TS
    'BinOp': 'binary_op',                  # Native
    'BoolOp': 'binary_op',                 # Native
    # Identifiers
    'identifier': 'identifier',            # TS
    'name': 'identifier',                  # TS
    'Name': 'identifier',                  # Native
    # Literals
    'integer': 'literal',                  # TS
    'float': 'literal',                    # TS
    'string': 'literal',                   # TS
    'number': 'literal',                   # TS
    'true': 'literal',                     # TS
    'false': 'literal',                    # TS
    'null': 'literal',                     # TS
    'none': 'literal',                     # TS
    'Constant': 'literal',                 # Native
}

class FeatureExtractor:
    def __init__(self, parser: Optional[ASTParser] = None, language: str = 'python'):
        self.parser = parser or ASTParser(language=language)
        self.language = language

    def _get_node_type(self, node: Any) -> str:
        if hasattr(node, 'type'): return node.type # TS
        return type(node).__name__ # Native

    def _get_children(self, node: Any) -> list:
        if hasattr(node, 'children'): return node.children # TS
        import ast
        return list(ast.iter_child_nodes(node)) # Native

    def extract(self, source_code: str) -> np.ndarray:
        tree = self.parser.parse(source_code)
        all_nodes = self.parser.get_all_nodes(tree)
        
        node_types = []
        for n in all_nodes:
            raw_type = self._get_node_type(n)
            mapped = NODE_MAPPING.get(raw_type, None)
            if mapped:
                node_types.append(mapped)

        total_nodes = len(all_nodes)
        
        freq_vec = self._node_type_frequencies(node_types, total_nodes)
        struct_vec = self._structural_metrics(tree, all_nodes, total_nodes)
        sem_vec = self._semantic_counts(node_types)
        ratio_vec = self._ratio_features(node_types, total_nodes)

        return np.concatenate([freq_vec, struct_vec, sem_vec, ratio_vec])

    def _node_type_frequencies(self, node_types: list[str], total: int) -> np.ndarray:
        counter = Counter(node_types)
        vec = np.zeros(NUM_NODE_FEATURES, dtype=np.float64)
        for name, idx in _NODE_INDEX.items():
            vec[idx] = counter.get(name, 0)
        if total > 0:
            vec /= total
        return vec

    def _structural_metrics(
        self, tree, all_nodes: list, total: int
    ) -> np.ndarray:
        max_depth = self.parser.get_tree_depth(tree)
        
        # Branching factors helper
        branching = self.parser.get_branching_factors(tree)

        # Leaf nodes
        leaf_count = sum(1 for n in all_nodes if len(self._get_children(n)) == 0)
        avg_branching = float(statistics.mean(branching)) if branching else 0.0

        depths = self._compute_all_depths(tree)
        avg_depth = float(statistics.mean(depths)) if depths else 0.0

        unique_types = len(set(self._get_node_type(n) for n in all_nodes))

        return np.array([
            total,
            max_depth,
            avg_depth,
            leaf_count,
            avg_branching,
            unique_types,
        ], dtype=np.float64)

    def _semantic_counts(self, node_types: list[str]) -> np.ndarray:
        c = Counter(node_types)
        return np.array([
            c.get('function_def', 0),
            c.get('class_def', 0),
            c.get('loop', 0),
            c.get('conditional', 0),
            c.get('try_catch', 0),
            c.get('import_stmt', 0),
            c.get('assignment', 0),
            c.get('return_stmt', 0),
            c.get('call_expr', 0),
            c.get('binary_op', 0),
        ], dtype=np.float64)

    def _ratio_features(self, node_types: list[str], total: int) -> np.ndarray:
        if total == 0:
            return np.zeros(6, dtype=np.float64)

        c = Counter(node_types)
        return np.array([
            c.get('loop', 0) / total,
            c.get('conditional', 0) / total,
            c.get('function_def', 0) / total,
            c.get('call_expr', 0) / total,
            c.get('assignment', 0) / total,
            c.get('identifier', 0) / total,
        ], dtype=np.float64)

    def _compute_all_depths(self, tree) -> list[int]:
        depths: list[int] = []
        root = tree.root_node if hasattr(tree, 'root_node') else tree
        if root is None: return []
        
        stack: list[tuple] = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            depths.append(depth)
            for child in self._get_children(node):
                stack.append((child, depth + 1))
        return depths

    @staticmethod
    def feature_names() -> list[str]:
        names: list[str] = [f'freq_{nt}' for nt in GENERIC_NODE_TYPES]
        names += [
            'total_nodes', 'max_depth', 'avg_depth',
            'leaf_count', 'avg_branching', 'unique_node_types',
        ]
        names += [
            'sem_functions', 'sem_classes', 'sem_loops',
            'sem_conditionals', 'sem_try', 'sem_imports',
            'sem_assignments', 'sem_returns',
            'sem_calls', 'sem_binary_ops',
        ]
        names += [
            'ratio_loops', 'ratio_conditionals', 'ratio_functions',
            'ratio_calls', 'ratio_assignments', 'ratio_names',
        ]
        return names
