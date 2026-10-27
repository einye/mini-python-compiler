# tac_generator.py

temp_counter = 0
label_counter = 0

def new_temp():
    global temp_counter
    temp_name = f"t{temp_counter}"
    temp_counter += 1
    return temp_name

def new_label():
    global label_counter
    label_name = f"L{label_counter}"
    label_counter += 1
    return label_name

def generate_tac(ast):
    code = []

    def walk(node):
        kind = node[0]

        if kind == 'program':
            walk(node[1])

        elif kind == 'statement_list':
            for stmt in node[1]:
                walk(stmt)

        elif kind == 'statement':
            walk(node[1])

        elif kind == 'simple_stmt':
            walk(node[1])

        elif kind == 'assign_stmt':
            var = node[1][1]
            temp = eval_expr(node[3])
            code.append(('=', temp, None, var))

        elif kind == 'print_stmt':
            temp = eval_expr(node[2])
            code.append(('print', temp, None, None))

        elif kind == 'compound_stmt':
            walk(node[1])

        elif kind == 'if_stmt':
            cond = eval_expr(node[1])
            label_true = new_label()
            label_end = new_label()

            code.append(('ifnz', cond, None, label_true))
            if len(node) == 4:
                walk(node[3])  # else block
            code.append(('goto', None, None, label_end))
            code.append(('label', None, None, label_true))
            walk(node[2])      # if block
            code.append(('label', None, None, label_end))
        
        elif kind == 'while_stmt':
            label_start = new_label()
            label_cond = new_label()

            code.append(('goto', None, None, label_cond))
            code.append(('label', None, None, label_start))
            walk(node[2])
            code.append(('label', None, None, label_cond))
            cond = eval_expr(node[1])
            code.append(('ifnz', cond, None, label_start))

    def eval_expr(expr):
        kind = expr[0]

        if kind == 'expr':
            return eval_expr(expr[1])

        elif kind == 'or_expr' or kind == 'and_expr':
            if len(expr) == 2:
                return eval_expr(expr[1])
            left = eval_expr(expr[1])
            right = eval_expr(expr[3])
            temp = new_temp()
            op = 'or' if kind == 'or_expr' else 'and'
            code.append((op, left, right, temp))
            return temp

        elif kind == 'not_expr':
            if len(expr) == 2:
                return eval_expr(expr[1])
            val = eval_expr(expr[2])
            temp = new_temp()
            code.append(('not', val, None, temp))
            return temp

        elif kind == 'comparison':
            if len(expr) == 2:
                return eval_expr(expr[1])
            left = eval_expr(expr[1])
            op = expr[2][1]
            right = eval_expr(expr[3])
            temp = new_temp()
            code.append((op, left, right, temp))
            return temp

        elif kind == 'arith_expr' or kind == 'term':
            if len(expr) == 2:
                return eval_expr(expr[1])
            left = eval_expr(expr[1])
            op = expr[2]
            right = eval_expr(expr[3])
            temp = new_temp()
            code.append((op, left, right, temp))
            return temp

        elif kind == 'factor':
            val = expr[1]
            if isinstance(val, tuple) and val[0] == 'token':
                return val[1]  # literal or variable name
            else:
                return eval_expr(val)

        else:
            raise Exception(f"Unknown expression kind: {kind}")

    walk(ast)
    return code
