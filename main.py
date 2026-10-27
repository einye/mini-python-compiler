import ply.lex as lex
import ply.yacc as yacc
from semantic import check_semantics, SemanticError
from tac_generator import generate_tac
import pprint
from x86_generator import generate_x86, save_asm

# -----------------------------------------------------------------------------
# Lexer
# -----------------------------------------------------------------------------

# List of token names.  This is always required
tokens = (
    'INTEGER',
    'BOOLEAN',
    'IDENTIFIER',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'FLOOR_DIVIDE',
    'EQUAL_EQUAL',
    'NOT_EQUAL',
    'LESS_THAN',
    'GREATER_THAN',
    'LESS_EQUAL',
    'GREATER_EQUAL',
    'AND',
    'OR',
    'NOT',
    'ASSIGN',
    'PRINT',
    'IF',
    'ELSE',
    'WHILE',
    'LEFT_PAREN',
    'RIGHT_PAREN',
    'COLON',
    'NEWLINE',
    'COMMENT' # Include comment in the tokens
)

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_MULTIPLY  = r'\*'
t_FLOOR_DIVIDE = r'//'
t_EQUAL_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'
t_LESS_EQUAL = r'<='
t_GREATER_EQUAL = r'>='
t_ASSIGN   = r'='
t_LEFT_PAREN  = r'\('
t_RIGHT_PAREN = r'\)'
t_COLON = r':'
t_NEWLINE = r'\n'

# Reserved words
reserved = {
    'True': 'BOOLEAN',
    'False': 'BOOLEAN',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
}

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_COMMENT(t):
    r'\#.*'
    pass  # No return value. Token is discarded

# Ignored characters
t_ignore = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------

# Get the token list from the lexer
tokens = tokens

# Operator precedence and associativity
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQUAL_EQUAL', 'NOT_EQUAL', 'LESS_THAN', 'GREATER_THAN', 'LESS_EQUAL', 'GREATER_EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'FLOOR_DIVIDE'),
)

# --- Productions (Grammar Rules) ---

def p_program(p):
    '''program : statement_list'''
    p[0] = ('program', p[1])

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = ('statement_list', (p[1],))
    else:
        p[0] = ('statement_list', p[1][1] + (p[2],))

def p_statement(p):
    '''statement : simple_stmt NEWLINE
                 | compound_stmt'''
    if len(p) == 3:
        p[0] = ('statement', p[1])
    else:
        p[0] = ('statement', p[1])

def p_simple_stmt(p):
    '''simple_stmt : assign_stmt
                   | print_stmt'''
    p[0] = ('simple_stmt', p[1])

def p_assign_stmt(p):
    '''assign_stmt : IDENTIFIER ASSIGN expr'''
    p[0] = ('assign_stmt', ('identifier', p[1]), p[2], p[3])

def p_print_stmt(p):
    '''print_stmt : PRINT LEFT_PAREN expr RIGHT_PAREN'''
    p[0] = ('print_stmt', p[1], p[3])

def p_compound_stmt(p):
    '''compound_stmt : if_stmt
                     | while_stmt'''
    p[0] = ('compound_stmt', p[1])

def p_if_stmt(p):
    '''if_stmt : IF expr COLON NEWLINE statement_list
               | IF expr COLON NEWLINE statement_list ELSE COLON NEWLINE statement_list'''
    if len(p) == 6:
        p[0] = ('if_stmt', p[2], p[5])  #  statement_list
    else:
        p[0] = ('if_stmt', p[2], p[5], p[9]) # statement_list


def p_while_stmt(p):
    '''while_stmt : WHILE expr COLON NEWLINE statement_list'''
    p[0] = ('while_stmt', p[2], p[5])



def p_expr(p):
    '''expr : or_expr'''
    p[0] = ('expr', p[1])

def p_or_expr(p):
    '''or_expr : and_expr
               | or_expr OR and_expr'''
    if len(p) == 2:
        p[0] = ('or_expr', p[1])
    else:
        p[0] = ('or_expr', p[1], p[2], p[3])

def p_and_expr(p):
    '''and_expr : not_expr
                | and_expr AND not_expr'''
    if len(p) == 2:
        p[0] = ('and_expr', p[1])
    else:
        p[0] = ('and_expr', p[1], p[2], p[3])

def p_not_expr(p):
    '''not_expr : NOT not_expr
                | comparison'''
    if len(p) == 2:
        p[0] = ('not_expr', p[1])
    else:
        p[0] = ('not_expr', p[1], p[2])

def p_comparison(p):
    '''comparison : arith_expr
                  | arith_expr comp_op arith_expr'''
    if len(p) == 2:
        p[0] = ('comparison', p[1])
    else:
        p[0] = ('comparison', p[1], p[2], p[3])

def p_comp_op(p):
    '''comp_op : EQUAL_EQUAL
               | NOT_EQUAL
               | LESS_THAN
               | GREATER_THAN
               | LESS_EQUAL
               | GREATER_EQUAL'''
    p[0] = ('comp_op', p[1])


def p_arith_expr(p):
    '''arith_expr : term
                  | arith_expr PLUS term
                  | arith_expr MINUS term'''
    if len(p) == 2:
        p[0] = ('arith_expr', p[1])
    else:
        p[0] = ('arith_expr', p[1], p[2], p[3])

def p_term(p):
    '''term : factor
            | term MULTIPLY factor
            | term FLOOR_DIVIDE factor'''
    if len(p) == 2:
        p[0] = ('term', p[1])
    else:
        p[0] = ('term', p[1], p[2], p[3])

def p_factor(p):
    '''factor : INTEGER
              | BOOLEAN
              | IDENTIFIER
              | LEFT_PAREN expr RIGHT_PAREN'''
    if p[1] == '(':
        p[0] = ('factor', p[2])
    else:
        p[0] = ('factor', ('token', p[1])) # Wrap INTEGER, BOOLEAN, IDENTIFIER in a tuple



def p_error(p):
    if p:
        print("Syntax error at token", p.type, p.value)
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Example usage:
    source_code = """
    x = 0
    while x < 3:
        print(x)
        x = x + 1
    """

    lexer.input(source_code) # Feed the source code to the lexer
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break    # No more input
        tokens.append(tok)

    for token in tokens:
        print(token)

    ast = parser.parse(source_code) # Parse the source code and get the AST
    print("\nAST:")
    pprint.pprint(ast)
    #print(ast)

    #Semantic
    try:
        check_semantics(ast)
        print("\nSemantic analysis passed.")
    except SemanticError as e:
        print(f"Semantic error: {e}")
        exit(1)

    #TAC 
    tac = generate_tac(ast)
    print("\nThree address code (Quadruples):")
    for quad in tac:
        print(quad)

    asm_code = generate_x86(tac)
    save_asm("program.asm",asm_code)
    print("\nAssembly code written to program.asm")
