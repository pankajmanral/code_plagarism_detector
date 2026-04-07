"""
utils.py — Preprocessing utilities for source code.

Handles comment removal, whitespace normalization, and
other transformations before AST parsing.
"""

import re
import textwrap
from typing import Optional


def remove_comments(source_code: str) -> str:
    """
    Remove single-line (#) comments from Python source code.
    
    Handles comments that appear at the start of a line or after code,
    while preserving '#' characters inside string literals.
    """
    lines = source_code.split('\n')
    cleaned_lines: list[str] = []

    for line in lines:
        cleaned = _strip_line_comment(line)
        cleaned_lines.append(cleaned)

    return '\n'.join(cleaned_lines)


def _strip_line_comment(line: str) -> str:
    """Remove trailing # comment from a single line, respecting strings."""
    in_string = False
    string_char: Optional[str] = None
    i = 0
    result: list[str] = []

    while i < len(line):
        char = line[i]

        if in_string:
            result.append(char)
            if char == '\\' and i + 1 < len(line):
                # Escaped character inside string — skip next char
                i += 1
                result.append(line[i])
            elif char == string_char:
                in_string = False
                string_char = None
        elif char in ('"', "'"):
            # Check for triple-quote
            triple = line[i:i + 3]
            if triple in ('"""', "'''"):
                # For simplicity, treat triple-quoted on same line
                in_string = True
                string_char = char
                result.append(char)
            else:
                in_string = True
                string_char = char
                result.append(char)
        elif char == '#':
            # Start of comment — stop here
            break
        else:
            result.append(char)

        i += 1

    return ''.join(result).rstrip()


def remove_docstrings(source_code: str) -> str:
    """
    Remove module, class, and function docstrings from Python source.
    
    Uses regex to strip triple-quoted strings at the start of modules,
    after class/def statements.
    """
    # Remove triple-quoted docstrings (both ''' and \"\"\")
    pattern = r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')'
    # Only remove if they appear as standalone expression statements
    # This is a heuristic — for full accuracy, the AST parser handles it
    result = re.sub(
        r'^\s*(?:\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')\s*$',
        '',
        source_code,
        flags=re.MULTILINE
    )
    return result


def normalize_whitespace(source_code: str) -> str:
    """
    Normalize indentation and blank lines.
    
    - Dedents the code to remove common leading whitespace
    - Collapses multiple blank lines into one
    - Strips trailing whitespace from each line
    """
    # Dedent
    code = textwrap.dedent(source_code)
    
    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in code.split('\n')]
    
    # Collapse multiple blank lines into single blank line
    cleaned: list[str] = []
    prev_blank = False
    for line in lines:
        if line.strip() == '':
            if not prev_blank:
                cleaned.append('')
            prev_blank = True
        else:
            cleaned.append(line)
            prev_blank = False

    return '\n'.join(cleaned).strip()


def preprocess_code(source_code: str) -> str:
    """
    Full preprocessing pipeline for source code before AST parsing.
    
    Steps:
        1. Remove comments
        2. Remove docstrings
        3. Normalize whitespace
    """
    code = remove_comments(source_code)
    code = remove_docstrings(code)
    code = normalize_whitespace(code)
    return code


def validate_code(source_code: str, language: str = 'python') -> tuple[bool, str]:
    """
    Check if the given string is valid code.
    """
    from ast_parser import ASTParser
    try:
        parser = ASTParser(language=language)
        tree = parser.parse(source_code)
        
        # If using tree-sitter, it doesn't raise exceptions on syntax errors;
        # instead, it produces 'ERROR' type nodes in the tree.
        if getattr(parser, 'use_tree_sitter', False):
            error_nodes = [n for n in parser.get_all_nodes(tree) if n.type == 'ERROR']
            if error_nodes:
                return False, f"Syntax error detected in {language} code."
            
        return True, ''
    except Exception as e:
        # ast.parse (Native Python) raises exceptions here
        return False, str(e)
