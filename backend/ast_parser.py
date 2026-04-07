"""
ast_parser.py — Resilient AST parser with Pure Python Fallback.
"""

import ast
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Tree-sitter imports (optional)
try:
    import tree_sitter
    from tree_sitter_languages import get_language, get_parser
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

class PythonNativeParser:
    """Fallback parser using Python's built-in 'ast' module."""
    def __init__(self):
        pass

    def parse(self, source_code: str):
        return ast.parse(source_code)

    def get_all_nodes(self, tree) -> list:
        return list(ast.walk(tree))

    def get_node_types(self, tree) -> list[str]:
        # Map native AST types to internal generic type names where possible
        # This is a bit tricky, but for structural features, the class names work
        return [type(n).__name__ for n in ast.walk(tree)]

    def get_tree_depth(self, node, _depth: int = 0) -> int:
        max_depth = _depth
        for child in ast.iter_child_nodes(node):
            child_depth = self.get_tree_depth(child, _depth + 1)
            if child_depth > max_depth:
                max_depth = child_depth
        return max_depth

    def get_branching_factors(self, node) -> list[int]:
        factors: list[int] = []
        for n in ast.walk(node):
            children = list(ast.iter_child_nodes(n))
            if children:
                factors.append(len(children))
        return factors

    def count_nodes(self, tree) -> int:
        return sum(1 for _ in ast.walk(tree))

class ASTParser:
    """
    Unified parser that uses tree-sitter when available, and falls back to 
    native 'ast' for Python if tree-sitter is missing.
    """
    def __init__(self, language: str = 'python', normalize: bool = True, strip_comments: bool = True):
        self.language_name = language.lower()
        self.use_tree_sitter = HAS_TREE_SITTER
        self.parser = None

        if self.language_name == 'python' and not HAS_TREE_SITTER:
            self.parser = PythonNativeParser()
            logger.info("Using Native Python AST parser (Tree-sitter not found).")
        elif HAS_TREE_SITTER:
            try:
                self.lang = get_language(self.language_name)
                self.ts_parser = get_parser(self.language_name)
                self.parser = self # Act as the parser proxy
            except Exception as e:
                if self.language_name == 'python':
                    self.parser = PythonNativeParser()
                    self.use_tree_sitter = False
                    logger.warning(f"Failed to load TS for Python, falling back to Native: {e}")
                else:
                    raise RuntimeError(f"Tree-sitter for {language} failed: {e}")
        else:
            if self.language_name != 'python':
                raise RuntimeError(f"Tree-sitter is required for {language} but not installed.")
            self.parser = PythonNativeParser()

    def parse(self, source_code: str):
        if self.use_tree_sitter:
            return self.ts_parser.parse(bytes(source_code, "utf8"))
        return self.parser.parse(source_code)

    def get_all_nodes(self, tree) -> list:
        if self.use_tree_sitter:
            nodes = []
            root = tree.root_node if hasattr(tree, 'root_node') else tree
            if not root: return []
            stack = [root]
            while stack:
                node = stack.pop(0)
                nodes.append(node)
                stack.extend(node.children)
            return nodes
        return self.parser.get_all_nodes(tree)

    def get_node_types(self, tree) -> list[str]:
        if self.use_tree_sitter:
            return [n.type for n in self.get_all_nodes(tree)]
        return self.parser.get_node_types(tree)

    def get_tree_depth(self, tree, _depth: int = 0) -> int:
        if self.use_tree_sitter:
            root = tree.root_node if hasattr(tree, 'root_node') else tree
            if not root: return _depth
            def _max_d(n, d):
                if not n.children: return d
                return max(_max_d(c, d + 1) for c in n.children)
            return _max_d(root, _depth)
        return self.parser.get_tree_depth(tree, _depth)

    def get_branching_factors(self, tree) -> list[int]:
        if self.use_tree_sitter:
            root = tree.root_node if hasattr(tree, 'root_node') else tree
            factors = []
            if not root: return []
            stack = [root]
            while stack:
                n = stack.pop(0)
                if n.children:
                    factors.append(len(n.children))
                    stack.extend(n.children)
            return factors
        return self.parser.get_branching_factors(tree)

    def count_nodes(self, tree) -> int:
        if self.use_tree_sitter:
            return len(self.get_all_nodes(tree))
        return self.parser.count_nodes(tree)
