# mini-python-compiler

A **compiler for a subset of Python**, written in Python. It takes a restricted Python-like source file, runs it through **lexing → parsing → semantic analysis → Three-Address Code (TAC) → 32-bit x86 assembly**, and produces a runnable Linux ELF binary via `nasm`.

Built from scratch for learning how compilers work, just PLY, a hand-rolled symbol table, and a hand-written x86 code emitter.

## What It Compiles

### Language Specification (The "minipython" Grammar)

This compiler does **not** accept arbitrary Python. It accepts a strict subset designed to keep the backend simple. If you want to write your own test files, here is the exact syntax supported.

### Supported Features

- **Integers**: `42`, `0`, `-5` (as expressions like `0 - 5`)
- **Booleans**: `True`, `False`
- **Variables**: `x`, `my_var`, `count_1`
- **Arithmetic**: `+`, `-`, `*`, `//` (floor division)
- **Comparisons**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Assignment**: `x = expr`
- **Printing**: `print(expr)` (integers only, True and False are 1 and 0 respectively)
- **Control Flow**: `if`, `else`, `while`
- **Comments**: `# this is ignored`
- **Parentheses**: `(expr)`

### Unsupported Features (Do NOT use)

- **Logical operators**: `and`, `or`, `not` (unpredictable)
- **Nested control flow**: An `if` inside a `while`, or a `while` inside an `if` *(will raise a `SemanticError`)*
- **Strings**: `"hello"`, `'world'`
- **Functions**: `def`, `return`
- **Lists / Dicts / Tuples**: `[]`, `{}`, `()`
- **Else-if**: `elif` *(use nested `if` or separate `if` statements instead)*
- **Negative literals**: `-5` *(use `0 - 5`)*
- **Empty blocks**: `if x: ` with no body

### Formal Grammar (EBNF)

If you need the exact rules the parser uses, here is the grammar:

```ebnf
program        ::= statement_list

statement_list ::= statement | statement_list statement

statement      ::= simple_stmt NEWLINE | compound_stmt

simple_stmt    ::= assign_stmt | print_stmt

assign_stmt    ::= IDENTIFIER "=" expr
print_stmt     ::= "print" "(" expr ")"

compound_stmt  ::= if_stmt | while_stmt

if_stmt        ::= "if" expr ":" NEWLINE statement_list
                 | "if" expr ":" NEWLINE statement_list "else" ":" NEWLINE statement_list

while_stmt     ::= "while" expr ":" NEWLINE statement_list

expr           ::= comparison

comparison     ::= arith_expr
                 | arith_expr comp_op arith_expr

comp_op        ::= "==" | "!=" | "<" | ">" | "<=" | ">="

arith_expr     ::= term
                 | arith_expr "+" term
                 | arith_expr "-" term

term           ::= factor
                 | term "*" factor
                 | term "//" factor

factor         ::= INTEGER
                 | BOOLEAN
                 | IDENTIFIER
                 | "(" expr ")"

INTEGER        ::= [0-9]+
BOOLEAN        ::= "True" | "False"
IDENTIFIER     ::= [a-zA-Z_][a-zA-Z0-9_]*
```

#### Important Note on Indentation:
The parser uses the NEWLINE token to separate statements. Indentation is ignored. The blocks for if and while are determined by the statement_list rule, which consumes lines until it hits a token it cannot parse (like else or the next top-level statement).
- Always put a blank line between blocks to ensure the parser knows where a block ends

## Requirements
- Python 3.8+
- PLY (pip install ply)
- NASM (for assembling the generated .asm on Linux)
- ld (GNU linker, usually bundled with binutils)

## Note on architecture

The generated assembly targets 32-bit x86 Linux (int 0x80 syscalls, _start entry). On a 64-bit system you'll need ld -m elf_i386. On macOS, this backend will not run as-is.

## Usage

```bash
# Clone the repo
git clone https://github.com/einye/mini-python-compiler.git

# Run
python compile.py <your-python-input-file.py>
```

## Known Issues/Limitations

- Not nested-control-flow-safe by design. semantic.py throws if you put an if inside a while. If you just delete that check, the TAC generator and backend will probably work but it's untested.

- Register allocation is naive. If a program has more than 4 simultaneous temps, the allocator still assigns edx repeatedly, leading to incorrect results.

- print only handles ints. Printing x where x was assigned a boolean will definitely print 1 for True and 0 for false. Mixed booleans/int results may misbehave.

- No error recovery. A syntax error prints and continues parsing, which can cascade.

- main.py has no CLI. It's hardcoded to a demo string; must edit source to test new files.

- 32-bit only. Won't run on macOS or without 32-bit ELF support.

- Test files should end with a blank line - I just add one if not to handle the syntax error at EOF for now.

## Possible Improvements

- CLI argument: python main.py input.py -o output.asm

- 64-bit backend: target x86_64 with syscall (currently 32-bit int 0x80)

- Strings: add string literals and printing

- Functions: add def, parameters, and a real call stack

- Variables with types: switch from dynamic to inferred/static typing

- Proper register allocation: graph coloring instead of linear scan

- Peephole optimization: mov eax, [x]; mov [x], eax is a no-op

- Nested control flow: the backend can already handle it; remove the restriction

- Constant folding: fold 2 + 3 at compile time

- Better booleans: use 0/1 uniformly and a single string-selection step

- Error line numbers: PLY can track line numbers in p_error

- Unit tests: snapshot-test each stage's output