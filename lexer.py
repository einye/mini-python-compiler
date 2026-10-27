import re

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0

    def get_next_token(self):
        if self.position >= len(self.source_code):
            return None, None  # End of input

        # Define the regular expressions for our tokens, in order of priority
        token_patterns = [
            (r'\d+', 'INTEGER'),
            (r'True|False', 'BOOLEAN'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
            (r'//', 'FLOOR_DIVIDE'),
            (r'==', 'EQUAL_EQUAL'),
            (r'!=', 'NOT_EQUAL'),
            (r'<=', 'LESS_EQUAL'),
            (r'>=', 'GREATER_EQUAL'),
            (r'+', 'PLUS'),
            (r'-', 'MINUS'),
            (r'\*', 'MULTIPLY'),
            (r'/', 'DIVIDE'), # Note: We specified '//' for floor division
            (r'<', 'LESS_THAN'),
            (r'>', 'GREATER_THAN'),
            (r'=', 'ASSIGN'),
            (r'print', 'PRINT'),
            (r'if', 'IF'),
            (r'else', 'ELSE'),
            (r'while', 'WHILE'),
            (r'\(', 'LEFT_PAREN'),
            (r'\)', 'RIGHT_PAREN'),
            (r':', 'COLON'),
            (r'and', 'AND'),
            (r'or', 'OR'),
            (r'not', 'NOT'),
            (r'#.*', 'COMMENT'),
            (r'[ \t\n]+', None),  # Whitespace (ignored)
        ]

        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(self.source_code, self.position)
            if match:
                lexeme = match.group(0)
                self.position = match.end()
                if token_type:
                    return token_type, lexeme
                else:
                    # Whitespace, continue to the next token
                    return self.get_next_token()

        # If no pattern matches at the current position, it's an error
        invalid_char = self.source_code[self.position]
        self.position += 1
        return 'ERROR', invalid_char

# Example Usage:
source = """x = 10
y = True
if x > 5:
print(y)
else:
z = x // 2 # Integer division
print(z)"""

lexer = Lexer(source)
tokens = []
token_type, lexeme = lexer.get_next_token()
while token_type:
    tokens.append((token_type, lexeme))
    token_type, lexeme = lexer.get_next_token()

for token in tokens:
    print(token)