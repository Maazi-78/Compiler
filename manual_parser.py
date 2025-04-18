import re

token_patterns = [
    (r'\bpackage\b', 'T_PACKAGE'),
    (r'\bfunc\b', 'T_FUNC'),
    (r'\bint\b', 'T_INTTYPE'),
    (r'\breturn\b', 'T_RETURN'),
    (r'\bif\b', 'T_IF'),
    (r'\belse\b', 'T_ELSE'),
    (r'\bwhile\b', 'T_WHILE'),
    (r'\bfor\b', 'T_FOR'),
    (r'\bclass\b', 'T_CLASS'),
    (r'\bnew\b', 'T_NEW'),
    (r'\btrue\b|\bfalse\b', 'T_BOOL'),
    (r'\d+', 'T_INT'),
    (r'".*?"', 'T_STRING'),
    (r';', 'T_SEMICOLON'),
    (r'=', 'T_ASSIGN'),
    (r'\+', 'T_PLUS'),
    (r'-', 'T_MINUS'),
    (r'>', 'T_GT'),
    (r'<', 'T_LT'),
    (r'\{', 'T_LCB'),
    (r'\}', 'T_RCB'),
    (r'\(', 'T_LPAREN'),
    (r'\)', 'T_RPAREN'),
    (r'[a-zA-Z_]\w*', 'T_ID'),
    (r'[0-9]+', 'T_INT'),
    (r'"[^"]*"', 'T_STRING'),
    (r'[ \t\n]+', None),  # Ignore whitespace
]

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def consume(self, expected_type):
        if self.position < len(self.tokens) and self.tokens[self.position][0] == expected_type:
            self.position += 1
        else:
            token = self.tokens[self.position] if self.position < len(self.tokens) else ('EOF', 'EOF')
            raise SyntaxError(f"Expected {expected_type} but found {token}")

    def parse(self):
        self.program()
        print("Parsing successful!")

    def program(self):
        self.consume('T_PACKAGE')
        self.consume('T_ID')
        self.consume('T_SEMICOLON')
        self.consume('T_CLASS')
        self.consume('T_ID')
        self.consume('T_LCB')
        self.class_body()
        self.consume('T_RCB')

    def class_body(self):
        while self.tokens[self.position][0] == 'T_FUNC':
            self.method_decl()

    def method_decl(self):
        self.consume('T_FUNC')
        self.consume('T_ID')
        self.consume('T_LPAREN')
        self.consume('T_RPAREN')
        self.consume('T_INTTYPE')
        self.method_body()

    def method_body(self):
        self.consume('T_LCB')
        self.stmt_list()
        self.consume('T_RCB')

    def stmt_list(self):
        while self.tokens[self.position][0] in ('T_INTTYPE', 'T_IF', 'T_ID'):
            self.stmt()

    def stmt(self):
        if self.tokens[self.position][0] == 'T_INTTYPE':
            self.var_decl()
        elif self.tokens[self.position][0] == 'T_IF':
            self.if_stmt()
        else:
            self.expr_stmt()

    def var_decl(self):
        self.consume('T_INTTYPE')
        self.consume('T_ID')
        self.consume('T_ASSIGN')
        self.expr()
        self.consume('T_SEMICOLON')

    def if_stmt(self):
        self.consume('T_IF')
        self.consume('T_LPAREN')
        self.expr()
        self.consume('T_RPAREN')
        self.method_body()

    def expr_stmt(self):
        if self.tokens[self.position][0] == 'T_ID':  # Check for variable assignment
            self.consume('T_ID')
            if self.tokens[self.position][0] == 'T_ASSIGN':  # Handle assignment
                self.consume('T_ASSIGN')
                self.expr()
        else:
            self.expr()
        self.consume('T_SEMICOLON')


    def expr(self):
        if self.tokens[self.position][0] in ('T_INT', 'T_ID'):
            self.consume(self.tokens[self.position][0])
            while self.position < len(self.tokens) and self.tokens[self.position][0] in ('T_PLUS', 'T_MINUS', 'T_GT', 'T_LT'):
                self.consume(self.tokens[self.position][0])
                self.consume(self.tokens[self.position][0])
        else:
            raise SyntaxError(f"Invalid expression at {self.tokens[self.position]}")

def tokenize(code):
    tokens = []
    while code:
        matched = False
        for pattern, token_type in token_patterns:
            match = re.match(pattern, code)
            if match:
                if token_type:
                    tokens.append((token_type, match.group()))
                code = code[match.end():]
                matched = True
                break
        if not matched:
            raise ValueError(f"Unexpected character: {code[0]}")
    return tokens

if __name__ == "__main__":
    sample_code = """package Test;
class Main {
  func main() int {
    int x = 10;
    if (x > 5) {
      x = x - 1;
    }
  }
}
"""
    tokens = tokenize(sample_code)
    parser = Parser(tokens)
    parser.parse()
