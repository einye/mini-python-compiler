import ply.lex as lex
import ply.yacc as yacc
from semantic import check_semantics, SemanticError
from tac_generator import generate_tac
import pprint
from x86_generator import generate_x86, save_asm

# Lexer

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

# Parser

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

# Productions (Grammar Rules)

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

# Main

if __name__ == '__main__':
    import sys

    # 1. Determine the input file
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r') as f:
                source_code = f.read()
                if not source_code.endswith('\n'):
                    source_code += '\n'
            print(f"Compiling {input_file}...")
        except FileNotFoundError:
            print(f"Error: Could not find file '{input_file}'")
            sys.exit(1)
    else:
        # No input file provided, exit with usage message
        print("Usage: python main.py <source_file.py>")
        exit(1)

    output_file = "program.asm"

    # --- Lexing ---
    lexer.input(source_code)
    tokens_list = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_list.append(tok)

    #You can comment out the following lines if you don't want to see the tokens printed
    print("Tokens:")
    for token in tokens_list:
        print(token)

    # --- Parsing ---
    ast = parser.parse(source_code)
    if not ast:
        print("Parsing failed.")
        sys.exit(1)
        
    print("\nAST generated successfully.")
    # You can comment out the below lies if you don't want to see the AST printed
    print("\nAST:")
    pprint.pprint(ast)

    # --- Semantic Analysis ---
    try:
        # We capture the resulting symbol table (env) here
        symbol_table = check_semantics(ast)
        print("Semantic analysis passed.")
    except SemanticError as e:
        print(f"\nSemantic error: {e}")
        sys.exit(1)

    # --- TAC Generation ---
    tac = generate_tac(ast)
    print("\nThree address code (Quadruples):")
    for quad in tac:
        print(quad)

    # --- x86 Code Generation ---
    # Pass the symbol table so we declare all variables in .data
    asm_code = generate_x86(tac, variables=symbol_table.keys())
    save_asm(output_file, asm_code)
    
    print(f"\nSuccess! Assembly code written to {output_file}")
    print(f"To build and run:")
    print(f"  nasm -f elf32 -o program.o {output_file}")
    print(f"  ld -m elf_i386 program.o -o program")
    print(f"  ./program")