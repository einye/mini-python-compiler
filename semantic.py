# semantic.py

class SemanticError(Exception):
    pass

def check_semantics(ast):
    env = {}  # symbol table for variable -> type

    def walk(node, in_control_block=False):
        kind = node[0]

        if kind == 'program':
            walk(node[1], in_control_block)

        elif kind == 'statement_list':
            def flatten_statement_list(stmt_node):
                if stmt_node[0] == 'statement_list':
                    for s in stmt_node[1]:
                        yield from flatten_statement_list(s)
                else:
                    yield stmt_node
            
            for stmt in flatten_statement_list(node):
                walk(stmt, in_control_block)

        elif kind == 'statement':
            walk(node[1], in_control_block)

        elif kind == 'simple_stmt':
            walk(node[1], in_control_block)

        elif kind == 'assign_stmt':
            var = node[1][1]
            expr_type = evaluate_expr(node[3])
            env[var] = expr_type  # dynamically typed; latest type wins

        elif kind == 'print_stmt':
            _ = evaluate_expr(node[2])

        elif kind == 'compound_stmt':
            if in_control_block:
                raise SemanticError("Nested control flow is not allowed.")
            walk(node[1], True)

        elif kind == 'if_stmt':
            _ = evaluate_expr(node[1])  # condition
            walk(node[2], True)
            if len(node) == 4:
                walk(node[3], True)

        elif kind == 'while_stmt':
            _ = evaluate_expr(node[1])  # condition
            walk(node[2], True)

        else:
            print("Debug node:", node)
            raise SemanticError(f"Unknown node in walk: {kind}")

    def evaluate_expr(expr):
        kind = expr[0]

        if kind == 'expr':
            return evaluate_expr(expr[1])

        elif kind == 'or_expr':
            if len(expr) == 2:
                return evaluate_expr(expr[1])
            left = evaluate_expr(expr[1])
            right = evaluate_expr(expr[3])
            if left != 'bool' or right != 'bool':
                raise SemanticError("Logical OR requires boolean operands")
            return 'bool'

        elif kind == 'and_expr':
            if len(expr) == 2:
                return evaluate_expr(expr[1])
            left = evaluate_expr(expr[1])
            right = evaluate_expr(expr[3])
            if left != 'bool' or right != 'bool':
                raise SemanticError("Logical AND requires boolean operands")
            return 'bool'

        elif kind == 'not_expr':
            if len(expr) == 2:
                return evaluate_expr(expr[1])
            operand = evaluate_expr(expr[2])
            if operand != 'bool':
                raise SemanticError("NOT operation requires a boolean operand")
            return 'bool'

        elif kind == 'comparison':
            left = evaluate_expr(expr[1])
            if len(expr) == 2:
                return left
            right = evaluate_expr(expr[3])
            if left != right:
                raise SemanticError("Comparison requires matching operand types")
            return 'bool'

        elif kind == 'arith_expr':
            if len(expr) == 2:
                return evaluate_expr(expr[1])
            left = evaluate_expr(expr[1])
            right = evaluate_expr(expr[3])
            if left != 'int' or right != 'int':
                raise SemanticError("Arithmetic operations require integer operands")
            return 'int'

        elif kind == 'term':
            if len(expr) == 2:
                return evaluate_expr(expr[1])
            left = evaluate_expr(expr[1])
            right = evaluate_expr(expr[3])
            if left != 'int' or right != 'int':
                raise SemanticError("Term operations require integer operands")
            return 'int'

        elif kind == 'factor':
            val = expr[1]
            if isinstance(val, tuple) and val[0] == 'token':
                tok = val[1]
                if isinstance(tok, int):
                    return 'int'
                elif tok in ('True', 'False', True, False):
                    return 'bool'
                elif isinstance(tok, str):
                    if tok not in env:
                        raise SemanticError(f"Variable '{tok}' used before assignment.")
                    return env[tok]
            else:
                return evaluate_expr(val)

        else:
            raise SemanticError(f"Unknown expression kind: {kind}")

    walk(ast)
    return env  # Return the symbol table for further use if needed