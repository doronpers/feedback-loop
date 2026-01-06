"""
Feedback Loop Language Server (Proof of Concept)

A minimal Language Server Protocol implementation that demonstrates
real-time pattern detection in IDEs.

Installation:
    pip install pygls

Usage:
    python feedback_loop_lsp.py

Then configure your IDE to use this language server for Python files.
"""

import ast
import logging
from typing import List, Optional

try:
    from pygls.server import LanguageServer
    from pygls.lsp.types import (
        Diagnostic,
        DiagnosticSeverity,
        Position,
        Range,
        CodeAction,
        CodeActionKind,
        TextEdit,
        WorkspaceEdit,
        TEXT_DOCUMENT_DID_OPEN,
        TEXT_DOCUMENT_DID_CHANGE,
        TEXT_DOCUMENT_CODE_ACTION,
    )
    PYGLS_AVAILABLE = True
except ImportError:
    PYGLS_AVAILABLE = False
    print("Warning: pygls not installed. Install with: pip install pygls")

from metrics.pattern_manager import PatternManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternChecker:
    """Checks code for pattern violations."""
    
    def __init__(self):
        """Initialize pattern checker."""
        try:
            self.pattern_manager = PatternManager()
            self.patterns = self.pattern_manager.get_all_patterns()
        except Exception as e:
            logger.warning(f"Failed to load pattern manager: {e}")
            self.pattern_manager = None
            self.patterns = []
        
        # Add simple caching for repeated checks
        self._cache = {}
        self._cache_max_size = 100
    
    def check_code(self, code: str, uri: str) -> List:
        """Check code for pattern violations.
        
        Args:
            code: Python code to check
            uri: File URI
            
        Returns:
            List of Diagnostic objects
        """
        if not PYGLS_AVAILABLE:
            return []
        
        # Check cache first for performance
        code_hash = hash(code)
        if code_hash in self._cache:
            return self._cache[code_hash]
        
        diagnostics = []
        
        try:
            tree = ast.parse(code)
            
            # Check for specific patterns
            diagnostics.extend(self._check_bare_except(tree))
            diagnostics.extend(self._check_print_statements(tree))
            diagnostics.extend(self._check_list_access(tree, code))
            diagnostics.extend(self._check_json_dumps(tree, code))
            
        except SyntaxError:
            # Ignore syntax errors - user might be typing
            pass
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
        
        # Cache result
        if len(self._cache) >= self._cache_max_size:
            # Simple FIFO eviction
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[code_hash] = diagnostics
        
        return diagnostics
    
    def _check_bare_except(self, tree: ast.AST) -> List:
        """Check for bare except clauses."""
        diagnostics = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=node.lineno - 1, character=node.col_offset),
                            end=Position(line=node.lineno - 1, character=node.col_offset + 6)
                        ),
                        message="Use specific exception types (e.g., 'except ValueError:') instead of bare 'except:'. Pattern: specific_exceptions",
                        severity=DiagnosticSeverity.Warning,
                        source="feedback-loop",
                        code="specific_exceptions"
                    ))
        
        return diagnostics
    
    def _check_print_statements(self, tree: ast.AST) -> List:
        """Check for print() statements."""
        diagnostics = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=node.lineno - 1, character=node.col_offset),
                            end=Position(line=node.lineno - 1, character=node.col_offset + 5)
                        ),
                        message="Consider using logger.debug() instead of print() for better debugging. Pattern: logger_debug",
                        severity=DiagnosticSeverity.Information,
                        source="feedback-loop",
                        code="logger_debug"
                    ))
        
        return diagnostics
    
    def _check_list_access(self, tree: ast.AST, code: str) -> List:
        """Check for unsafe list access."""
        diagnostics = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Subscript):
                # Check if accessing a list/array without bounds check
                # Compatible with Python 3.9+ (ast.Index deprecated)
                if isinstance(node.slice, (ast.Constant, ast.Name, ast.Attribute)):
                    # Look for patterns like items[0] without if items check
                    diagnostics.append(Diagnostic(
                        range=Range(
                            start=Position(line=node.lineno - 1, character=node.col_offset),
                            end=Position(line=node.lineno - 1, character=node.col_offset + 10)
                        ),
                        message="Consider checking list bounds before access. Pattern: bounds_checking",
                        severity=DiagnosticSeverity.Hint,
                        source="feedback-loop",
                        code="bounds_checking"
                    ))
        
        return diagnostics
    
    def _check_json_dumps(self, tree: ast.AST, code: str) -> List:
        """Check for json.dumps() that might have NumPy issues."""
        diagnostics = []
        
        # Check if numpy is imported
        has_numpy = any(
            isinstance(node, ast.Import) and any(alias.name == 'numpy' for alias in node.names)
            or isinstance(node, ast.ImportFrom) and node.module == 'numpy'
            for node in ast.walk(tree)
        )
        
        if has_numpy:
            # Check for json.dumps calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if (isinstance(node.func, ast.Attribute) and 
                        node.func.attr == 'dumps' and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == 'json'):
                        
                        diagnostics.append(Diagnostic(
                            range=Range(
                                start=Position(line=node.lineno - 1, character=node.col_offset),
                                end=Position(line=node.lineno - 1, character=node.col_offset + 11)
                            ),
                            message="When using NumPy, consider converting types before JSON serialization. Pattern: numpy_json_serialization",
                            severity=DiagnosticSeverity.Information,
                            source="feedback-loop",
                            code="numpy_json_serialization"
                        ))
        
        return diagnostics
    
    def get_code_actions(self, uri: str, diagnostic: Diagnostic) -> List:
        """Get code actions (quick fixes) for a diagnostic.
        
        Args:
            uri: File URI
            diagnostic: The diagnostic to fix
            
        Returns:
            List of CodeAction objects
        """
        actions = []
        
        if diagnostic.code == "specific_exceptions":
            # Suggest replacing with ValueError
            actions.append(CodeAction(
                title="Replace with 'except ValueError:'",
                kind=CodeActionKind.QuickFix,
                diagnostics=[diagnostic],
                edit=WorkspaceEdit(changes={
                    uri: [TextEdit(
                        range=diagnostic.range,
                        new_text="except ValueError:"
                    )]
                })
            ))
            
            # Suggest replacing with Exception
            actions.append(CodeAction(
                title="Replace with 'except Exception as e:'",
                kind=CodeActionKind.QuickFix,
                diagnostics=[diagnostic],
                edit=WorkspaceEdit(changes={
                    uri: [TextEdit(
                        range=diagnostic.range,
                        new_text="except Exception as e:"
                    )]
                })
            ))
        
        elif diagnostic.code == "logger_debug":
            # Suggest replacing with logger.debug
            actions.append(CodeAction(
                title="Replace with logger.debug()",
                kind=CodeActionKind.QuickFix,
                diagnostics=[diagnostic],
                edit=WorkspaceEdit(changes={
                    uri: [TextEdit(
                        range=diagnostic.range,
                        new_text="logger.debug"
                    )]
                })
            ))
        
        return actions


if PYGLS_AVAILABLE:
    # Create language server
    server = LanguageServer("feedback-loop", "v0.1")
    checker = PatternChecker()
    
    @server.feature(TEXT_DOCUMENT_DID_OPEN)
    async def did_open(ls: LanguageServer, params):
        """Handle document open event."""
        uri = params.text_document.uri
        text = params.text_document.text
        
        logger.info(f"Document opened: {uri}")
        
        # Analyze document
        diagnostics = checker.check_code(text, uri)
        
        # Publish diagnostics
        ls.publish_diagnostics(uri, diagnostics)
    
    @server.feature(TEXT_DOCUMENT_DID_CHANGE)
    async def did_change(ls: LanguageServer, params):
        """Handle document change event."""
        uri = params.text_document.uri
        
        # Get current text
        doc = ls.workspace.get_document(uri)
        text = doc.source
        
        logger.info(f"Document changed: {uri}")
        
        # Analyze document
        diagnostics = checker.check_code(text, uri)
        
        # Publish diagnostics
        ls.publish_diagnostics(uri, diagnostics)
    
    @server.feature(TEXT_DOCUMENT_CODE_ACTION)
    async def code_action(ls: LanguageServer, params):
        """Provide code actions for diagnostics."""
        uri = params.text_document.uri
        
        actions = []
        for diagnostic in params.context.diagnostics:
            if diagnostic.source == "feedback-loop":
                actions.extend(checker.get_code_actions(uri, diagnostic))
        
        return actions


def main():
    """Start the language server."""
    if not PYGLS_AVAILABLE:
        print("Error: pygls not installed")
        print("Install with: pip install pygls")
        return 1
    
    logger.info("Starting Feedback Loop Language Server...")
    logger.info("Listening on stdin/stdout")
    
    try:
        server.start_io()
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
