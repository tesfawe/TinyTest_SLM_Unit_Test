import libcst as cst

class DocstringRemover(cst.CSTTransformer):
    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        # Remove module-level docstrings
        if not updated_node.body:
            return updated_node
        
        first_stmt = updated_node.body[0]
        if self._is_docstring(first_stmt):
            return updated_node.with_changes(body=updated_node.body[1:])
        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        # Remove function docstrings
        if not updated_node.body.body:
            return updated_node
            
        first_stmt = updated_node.body.body[0]
        if self._is_docstring(first_stmt):
            new_body = updated_node.body.with_changes(body=updated_node.body.body[1:])
            return updated_node.with_changes(body=new_body)
        return updated_node

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        # Remove class docstrings
        if not updated_node.body.body:
            return updated_node
            
        first_stmt = updated_node.body.body[0]
        if self._is_docstring(first_stmt):
            new_body = updated_node.body.with_changes(body=updated_node.body.body[1:])
            return updated_node.with_changes(body=new_body)
        return updated_node

    def _is_docstring(self, node: cst.BaseStatement) -> bool:
        if isinstance(node, cst.SimpleStatementLine):
            if len(node.body) == 1 and isinstance(node.body[0], cst.Expr):
                expr = node.body[0].value
                if isinstance(expr, cst.SimpleString):
                    return True
                if isinstance(expr, cst.ConcatenatedString):
                    return True
        return False

def strip_docstrings(code: str) -> str:
    """
    Remove docstrings from the given Python code using LibCST.
    Preserves other comments and formatting.
    """
    try:
        source_tree = cst.parse_module(code)
        transformer = DocstringRemover()
        modified_tree = source_tree.visit(transformer)
        return modified_tree.code
    except Exception as e:
        print(f"Warning: Failed to strip docstrings: {e}")
        return code
