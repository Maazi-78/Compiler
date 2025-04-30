import re

# Token patterns for lexical analysis
token_patterns = [
    # Order matters - put multi-character operators before single-character ones
    # and keywords before identifiers
    
    # Keywords
    (r'\bpackage\b', 'T_PACKAGE'),
    (r'\bfunc\b', 'T_FUNC'),
    (r'\bint\b', 'T_INTTYPE'),
    (r'\bstring\b', 'T_STRINGTYPE'),
    (r'\bbool\b', 'T_BOOLTYPE'),
    (r'\breturn\b', 'T_RETURN'),
    (r'\bif\b', 'T_IF'),
    (r'\belse\b', 'T_ELSE'),
    (r'\bwhile\b', 'T_WHILE'),
    (r'\bfor\b', 'T_FOR'),
    (r'\bclass\b', 'T_CLASS'),
    (r'\bnew\b', 'T_NEW'),
    (r'\btrue\b|\bfalse\b', 'T_BOOL'),
    (r'\bnull\b', 'T_NULL'),
    (r'\bthis\b', 'T_THIS'),
    (r'\bsuper\b', 'T_SUPER'),
    (r'\bvoid\b', 'T_VOID'),
    
    # Operators (multi-character before single-character)
    (r'==', 'T_EQ'),
    (r'!=', 'T_NEQ'),
    (r'<=', 'T_LTE'),
    (r'>=', 'T_GTE'),
    (r'&&', 'T_AND'),
    (r'\|\|', 'T_OR'),
    (r'->', 'T_ARROW'),
    (r'::', 'T_DOUBLECOLON'),
    
    # Single-character operators
    (r'=', 'T_ASSIGN'),
    (r'\+', 'T_PLUS'),
    (r'\%', 'T_MOD'),
    (r'-', 'T_MINUS'),
    (r'\*', 'T_MULT'),
    (r'/', 'T_DIV'),
    (r'<', 'T_LT'),
    (r'>', 'T_GT'),
    (r'!', 'T_NOT'),
    (r'\.', 'T_DOT'),
    (r':', 'T_COLON'),
    (r'@', 'T_AT'),
    (r'\?', 'T_QUESTION'),
    
    # Literals
    (r'\d+', 'T_INT'),
    (r'".*?"', 'T_STRING'),
    
    # Punctuation
    (r'\{', 'T_LCB'),
    (r'\}', 'T_RCB'),
    (r'\(', 'T_LPAREN'),
    (r'\)', 'T_RPAREN'),
    (r'\[', 'T_LBRACKET'),
    (r'\]', 'T_RBRACKET'),
    (r';', 'T_SEMICOLON'),
    (r',', 'T_COMMA'),
    
    # Identifier (must come after keywords)
    (r'[a-zA-Z_]\w*', 'T_ID'),
    
    # Whitespace and comments
    (r'\n', 'T_NEWLINE'),
    (r'[ \t]+', 'T_WHITESPACE'),
    (r'//.*', 'T_COMMENT'),
]

class Node:
    """Node class for creating a parse tree"""
    def __init__(self, node_type, value=None, children=None):
        self.type = node_type
        self.value = value
        self.children = children if children else []
    
    def add_child(self, child):
        self.children.append(child)
    
    def __str__(self):
        return self._str_helper(0)
    
    def _str_helper(self, level):
        result = "  " * level + f"{self.type}"
        if self.value:
            result += f": {self.value}"
        result += "\n"
        
        for child in self.children:
            if isinstance(child, Node):
                result += child._str_helper(level + 1)
            else:
                result += "  " * (level + 1) + str(child) + "\n"
        
        return result

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t[0] not in ('T_WHITESPACE', 'T_COMMENT', 'T_NEWLINE')]
        self.position = 0
        self.current_line = 1

    def peek(self, n=0):
        """Look at the token n positions ahead without consuming it"""
        if self.position + n < len(self.tokens):
            return self.tokens[self.position + n][0]
        return None
    
    def peek_token(self, n=0):
        """Get the token n positions ahead without consuming it"""
        if self.position + n < len(self.tokens):
            return self.tokens[self.position + n]
        return ('EOF', 'EOF')
        
    def get_token_value(self):
        """Get the value of the current token"""
        if self.position < len(self.tokens):
            return self.tokens[self.position][1]
        return None

    def consume(self, expected_type=None):
        """Consume current token and advance position"""
        if self.position >= len(self.tokens):
            raise SyntaxError(f"Unexpected end of input, expected {expected_type}")
        
        current_token = self.tokens[self.position]
        token_type, token_value = current_token
        
        # Track line numbers from newline tokens (already removed from filtered tokens)
        if token_type == 'T_NEWLINE':
            self.current_line += 1
            
        if expected_type and token_type != expected_type:
            context = []
            # Get some surrounding tokens for context
            start = max(0, self.position - 2)
            end = min(len(self.tokens), self.position + 3)
            
            for i in range(start, end):
                if i == self.position:
                    context.append(f"[{self.tokens[i][0]}: {self.tokens[i][1]}]")
                else:
                    context.append(f"{self.tokens[i][0]}: {self.tokens[i][1]}")
                    
            context_str = ", ".join(context)
            raise SyntaxError(f"Line {self.current_line}: Expected {expected_type} but found {token_type}: '{token_value}' - Context: {context_str}")
        
        self.position += 1
        return current_token

    def parse(self):
        """Start parsing the program and return the parse tree"""
        tree = self.program()
        if self.position < len(self.tokens):
            remaining = self.tokens[self.position:]
            raise SyntaxError(f"Line {self.current_line}: Parsing complete but found additional tokens: {remaining}")
        print("Parsing successful!")
        return tree

    def program(self):
        """Parse program -> [package_decl] (class_decl | function_decl | stmt)*"""
        program_node = Node('Program')
        
        # Optional package declaration
        if self.peek() == 'T_PACKAGE':
            package_node = self.package_decl()
            program_node.add_child(package_node)
        
        # Parse top-level declarations and statements
        while self.position < len(self.tokens):
            if self.peek() == 'T_CLASS':
                node = self.class_decl()
            elif self.peek() == 'T_FUNC':
                node = self.function_decl()  # New method needed
            else:
                node = self.stmt()
            program_node.add_child(node)
        
        return program_node
    
    def function_decl(self):
        """Parse function_decl -> func ID ( params? ) [type] method_body"""
        function_node = Node('FunctionDecl')
        
        # func keyword
        token = self.consume('T_FUNC')
        function_node.add_child(Node('Keyword', token[1]))
        
        # Function name
        token = self.consume('T_ID')
        function_node.add_child(Node('Identifier', token[1]))
        
        # Opening parenthesis
        token = self.consume('T_LPAREN')
        function_node.add_child(Node('Punctuation', token[1]))
        
        # Parameters (optional)
        if self.peek() != 'T_RPAREN':
            params_node = self.params()
            function_node.add_child(params_node)
        
        # Closing parenthesis
        token = self.consume('T_RPAREN')
        function_node.add_child(Node('Punctuation', token[1]))
        
        # Return type (optional)
        if self.peek() in ('T_INTTYPE', 'T_BOOLTYPE', 'T_STRINGTYPE', 'T_VOID'):
            type_node = self.type()
            function_node.add_child(type_node)
        
        # Function body
        body_node = self.method_body()
        function_node.add_child(body_node)
        
        return function_node

    def package_decl(self):
        """Parse package_decl -> package ID ;"""
        package_node = Node('PackageDecl')
        
        token = self.consume('T_PACKAGE')
        package_node.add_child(Node('Keyword', token[1]))
        
        token = self.consume('T_ID')
        package_node.add_child(Node('Identifier', token[1]))
        
        token = self.consume('T_SEMICOLON')
        package_node.add_child(Node('Punctuation', token[1]))
        
        return package_node

    def class_decl(self):
        """Parse class_decl -> class ID { class_body }"""
        class_node = Node('ClassDecl')
        
        token = self.consume('T_CLASS')
        class_node.add_child(Node('Keyword', token[1]))
        
        token = self.consume('T_ID')
        class_node.add_child(Node('Identifier', token[1]))
        
        token = self.consume('T_LCB')
        class_node.add_child(Node('Punctuation', token[1]))
        
        # Parse class body
        body_node = self.class_body()
        class_node.add_child(body_node)
        
        token = self.consume('T_RCB')
        class_node.add_child(Node('Punctuation', token[1]))
        
        return class_node

    def class_body(self):
        """Parse class_body -> method_decl*"""
        body_node = Node('ClassBody')
        
        # Parse methods as long as we see func keyword
        while self.peek() == 'T_FUNC':
            method_node = self.method_decl()
            body_node.add_child(method_node)
        
        return body_node

    def method_decl(self):
        """Parse method_decl -> func ID ( params? ) type method_body"""
        method_node = Node('MethodDecl')
        
        # func keyword
        token = self.consume('T_FUNC')
        method_node.add_child(Node('Keyword', token[1]))
        
        # Method name
        token = self.consume('T_ID')
        method_node.add_child(Node('Identifier', token[1]))
        
        # Opening parenthesis
        token = self.consume('T_LPAREN')
        method_node.add_child(Node('Punctuation', token[1]))
        
        # Parameters (optional)
        if self.peek() != 'T_RPAREN':
            params_node = self.params()
            method_node.add_child(params_node)
        
        # Closing parenthesis
        token = self.consume('T_RPAREN')
        method_node.add_child(Node('Punctuation', token[1]))
        
        # Return type
        type_node = self.type()
        method_node.add_child(type_node)
        
        # Method body
        body_node = self.method_body()
        method_node.add_child(body_node)
        
        return method_node

    def params(self):
        """Parse params -> type ID (, type ID)*"""
        params_node = Node('Parameters')
        
        # First parameter
        type_node = self.type()
        params_node.add_child(type_node)
        
        token = self.consume('T_ID')
        params_node.add_child(Node('Identifier', token[1]))
        
        # Additional parameters
        while self.peek() == 'T_COMMA':
            token = self.consume('T_COMMA')
            params_node.add_child(Node('Punctuation', token[1]))
            
            type_node = self.type()
            params_node.add_child(type_node)
            
            token = self.consume('T_ID')
            params_node.add_child(Node('Identifier', token[1]))
        
        return params_node

    def type(self):
        """Parse type -> int | bool | string | void"""
        type_node = Node('Type')
        
        if self.peek() == 'T_INTTYPE':
            token = self.consume('T_INTTYPE')
        elif self.peek() == 'T_BOOLTYPE':
            token = self.consume('T_BOOLTYPE')
        elif self.peek() == 'T_STRINGTYPE':
            token = self.consume('T_STRINGTYPE')
        elif self.peek() == 'T_VOID':
            token = self.consume('T_VOID')
        else:
            raise SyntaxError(f"Line {self.current_line}: Expected type but found {self.peek_token()}")
        
        type_node.add_child(Node('Keyword', token[1]))
        return type_node

    def method_body(self):
        """Parse method_body -> { stmt* }"""
        body_node = Node('MethodBody')
        
        token = self.consume('T_LCB')
        body_node.add_child(Node('Punctuation', token[1]))
        
        # Parse statements until closing brace
        while self.peek() != 'T_RCB':
            if self.peek() is None:
                raise SyntaxError(f"Line {self.current_line}: Unexpected end of input, expected '}}' to close method body")
            
            stmt_node = self.stmt()
            body_node.add_child(stmt_node)
        
        token = self.consume('T_RCB')
        body_node.add_child(Node('Punctuation', token[1]))
        
        return body_node

    def stmt(self):
        """
        Parse stmt -> var_decl | if_stmt | while_stmt | for_stmt | 
                     return_stmt | block | expr_stmt
        """
        stmt_node = Node('Statement')
        
        if self.peek() in ('T_INTTYPE', 'T_BOOLTYPE', 'T_STRINGTYPE'):
            var_node = self.var_decl()
            stmt_node.add_child(var_node)
        elif self.peek() == 'T_IF':
            if_node = self.if_stmt()
            stmt_node.add_child(if_node)
        elif self.peek() == 'T_WHILE':
            while_node = self.while_stmt()
            stmt_node.add_child(while_node)
        elif self.peek() == 'T_FOR':
            for_node = self.for_stmt()
            stmt_node.add_child(for_node)
        elif self.peek() == 'T_RETURN':
            return_node = self.return_stmt()
            stmt_node.add_child(return_node)
        elif self.peek() == 'T_LCB':
            block_node = self.block()
            stmt_node.add_child(block_node)
        else:
            expr_stmt_node = self.expr_stmt()
            stmt_node.add_child(expr_stmt_node)
        
        return stmt_node

    def var_decl(self):
        """Parse var_decl -> [type] ID (= expr)? ;"""
        var_node = Node('VarDecl')
        
        # Type (optional)
        if self.peek() in ('T_INTTYPE', 'T_BOOLTYPE', 'T_STRINGTYPE'):
            type_node = self.type()
            var_node.add_child(type_node)
        
        # Variable name
        token = self.consume('T_ID')
        var_node.add_child(Node('Identifier', token[1]))
        
        # Optional initialization
        if self.peek() == 'T_ASSIGN':
            token = self.consume('T_ASSIGN')
            var_node.add_child(Node('Operator', token[1]))
            
            # Parse the right-hand side expression
            expr_node = self.expr()
            var_node.add_child(expr_node)
        
        # Semicolon (optional in Python-style)
        if self.peek() == 'T_SEMICOLON':
            token = self.consume('T_SEMICOLON')
            var_node.add_child(Node('Punctuation', token[1]))
        
        return var_node

    def if_stmt(self):
        """Parse if_stmt -> if ( expr ) stmt (else stmt)?"""
        if_node = Node('IfStmt')
        
        # if keyword
        token = self.consume('T_IF')
        if_node.add_child(Node('Keyword', token[1]))
        
        # Opening parenthesis
        token = self.consume('T_LPAREN')
        if_node.add_child(Node('Punctuation', token[1]))
        
        # Condition expression
        expr_node = self.expr()
        if_node.add_child(expr_node)
        
        # Closing parenthesis
        token = self.consume('T_RPAREN')
        if_node.add_child(Node('Punctuation', token[1]))
        
        # If body (can be any statement)
        stmt_node = self.stmt()
        if_node.add_child(Node('ThenClause', children=[stmt_node]))
        
        # Optional else
        if self.peek() == 'T_ELSE':
            token = self.consume('T_ELSE')
            else_keyword = Node('Keyword', token[1])
            
            # Else body
            else_stmt = self.stmt()
            if_node.add_child(Node('ElseClause', children=[else_keyword, else_stmt]))
        
        return if_node

    def while_stmt(self):
        """Parse while_stmt -> while ( expr ) stmt"""
        while_node = Node('WhileStmt')
        
        # while keyword
        token = self.consume('T_WHILE')
        while_node.add_child(Node('Keyword', token[1]))
        
        # Opening parenthesis
        token = self.consume('T_LPAREN')
        while_node.add_child(Node('Punctuation', token[1]))
        
        # Condition expression
        expr_node = self.expr()
        while_node.add_child(expr_node)
        
        # Closing parenthesis
        token = self.consume('T_RPAREN')
        while_node.add_child(Node('Punctuation', token[1]))
        
        # While body
        stmt_node = self.stmt()
        while_node.add_child(stmt_node)
        
        return while_node

    def for_stmt(self):
        """Parse for_stmt -> for ( expr? ; expr? ; expr? ) stmt"""
        for_node = Node('ForStmt')
        
        # for keyword
        token = self.consume('T_FOR')
        for_node.add_child(Node('Keyword', token[1]))
        
        # Opening parenthesis
        token = self.consume('T_LPAREN')
        for_node.add_child(Node('Punctuation', token[1]))
        
        # Initialization (optional)
        init_node = Node('Initialization')
        if self.peek() != 'T_SEMICOLON':
            expr_node = self.expr()
            init_node.add_child(expr_node)
        for_node.add_child(init_node)
        
        # First semicolon
        token = self.consume('T_SEMICOLON')
        for_node.add_child(Node('Punctuation', token[1]))
        
        # Condition (optional)
        cond_node = Node('Condition')
        if self.peek() != 'T_SEMICOLON':
            expr_node = self.expr()
            cond_node.add_child(expr_node)
        for_node.add_child(cond_node)
        
        # Second semicolon
        token = self.consume('T_SEMICOLON')
        for_node.add_child(Node('Punctuation', token[1]))
        
        # Update (optional)
        update_node = Node('Update')
        if self.peek() != 'T_RPAREN':
            expr_node = self.expr()
            update_node.add_child(expr_node)
        for_node.add_child(update_node)
        
        # Closing parenthesis
        token = self.consume('T_RPAREN')
        for_node.add_child(Node('Punctuation', token[1]))
        
        # For body
        stmt_node = self.stmt()
        for_node.add_child(stmt_node)
        
        return for_node

    def return_stmt(self):
        """Parse return_stmt -> return expr? ;"""
        return_node = Node('ReturnStmt')
        
        # return keyword
        token = self.consume('T_RETURN')
        return_node.add_child(Node('Keyword', token[1]))
        
        # Optional expression
        if self.peek() != 'T_SEMICOLON':
            expr_node = self.expr()
            return_node.add_child(expr_node)
        
        # Semicolon
        token = self.consume('T_SEMICOLON')
        return_node.add_child(Node('Punctuation', token[1]))
        
        return return_node

    def block(self):
        """Parse block -> { stmt* }"""
        block_node = Node('Block')
        
        # Opening brace
        token = self.consume('T_LCB')
        block_node.add_child(Node('Punctuation', token[1]))
        
        # Statements
        while self.peek() != 'T_RCB':
            if self.peek() is None:
                raise SyntaxError(f"Line {self.current_line}: Unexpected end of input, expected '}}' to close block")
            
            stmt_node = self.stmt()
            block_node.add_child(stmt_node)
        
        # Closing brace
        token = self.consume('T_RCB')
        block_node.add_child(Node('Punctuation', token[1]))
        
        return block_node

    def expr_stmt(self):
        """Parse expr_stmt -> expr ;"""
        expr_stmt_node = Node('ExprStmt')
        
        # Expression
        expr_node = self.expr()
        expr_stmt_node.add_child(expr_node)
        
        # Semicolon
        token = self.consume('T_SEMICOLON')
        expr_stmt_node.add_child(Node('Punctuation', token[1]))
        
        return expr_stmt_node

    def expr(self):
        """Parse expression with operator precedence"""
        return self.assignment_expr()

    def assignment_expr(self):
        """Parse assignment_expr -> logical_or_expr (= assignment_expr)?"""
        # For assignment, the LHS needs to be a valid target (ID, array access, member access)
        lhs = self.logical_or_expr()
        
        if self.peek() == 'T_ASSIGN':
            # Ensure LHS is valid for assignment
            valid_assign_targets = ('Identifier', 'ArrayAccess', 'MemberAccess')
            
            # Create assignment node
            assign_node = Node('Assignment')
            assign_node.add_child(lhs)
            
            token = self.consume('T_ASSIGN')
            assign_node.add_child(Node('Operator', token[1]))
            
            # Parse the right-hand side expression
            rhs = self.assignment_expr()
            assign_node.add_child(rhs)
            
            return assign_node
        
        return lhs

    def logical_or_expr(self):
        """Parse logical_or_expr -> logical_and_expr (|| logical_and_expr)*"""
        lhs = self.logical_and_expr()
        
        while self.peek() == 'T_OR':
            logical_or_node = Node('LogicalOr')
            logical_or_node.add_child(lhs)
            
            token = self.consume('T_OR')
            logical_or_node.add_child(Node('Operator', token[1]))
            
            rhs = self.logical_and_expr()
            logical_or_node.add_child(rhs)
            
            lhs = logical_or_node
        
        return lhs

    def logical_and_expr(self):
        """Parse logical_and_expr -> equality_expr (&& equality_expr)*"""
        lhs = self.equality_expr()
        
        while self.peek() == 'T_AND':
            logical_and_node = Node('LogicalAnd')
            logical_and_node.add_child(lhs)
            
            token = self.consume('T_AND')
            logical_and_node.add_child(Node('Operator', token[1]))
            
            rhs = self.equality_expr()
            logical_and_node.add_child(rhs)
            
            lhs = logical_and_node
        
        return lhs

    def equality_expr(self):
        """Parse equality_expr -> relational_expr ((==|!=) relational_expr)*"""
        lhs = self.relational_expr()
        
        while self.peek() in ('T_EQ', 'T_NEQ'):
            equality_node = Node('Equality')
            equality_node.add_child(lhs)
            
            token = self.consume(self.peek())
            equality_node.add_child(Node('Operator', token[1]))
            
            rhs = self.relational_expr()
            equality_node.add_child(rhs)
            
            lhs = equality_node
        
        return lhs

    def relational_expr(self):
        """Parse relational_expr -> additive_expr ((>|>=|<|<=) additive_expr)*"""
        lhs = self.additive_expr()
        
        while self.peek() in ('T_GT', 'T_GTE', 'T_LT', 'T_LTE'):
            relational_node = Node('Relational')
            relational_node.add_child(lhs)
            
            token = self.consume(self.peek())
            relational_node.add_child(Node('Operator', token[1]))
            
            rhs = self.additive_expr()
            relational_node.add_child(rhs)
            
            lhs = relational_node
        
        return lhs

    def additive_expr(self):
        """Parse additive_expr -> multiplicative_expr ((+|-) multiplicative_expr)*"""
        lhs = self.multiplicative_expr()
        
        while self.peek() in ('T_PLUS', 'T_MINUS'):
            additive_node = Node('Additive')
            additive_node.add_child(lhs)
            
            token = self.consume(self.peek())
            additive_node.add_child(Node('Operator', token[1]))
            
            rhs = self.multiplicative_expr()
            additive_node.add_child(rhs)
            
            lhs = additive_node
        
        return lhs

    def multiplicative_expr(self):
        """Parse multiplicative_expr -> unary_expr ((*|/|%) unary_expr)*"""
        lhs = self.unary_expr()
        
        while self.peek() in ('T_MULT', 'T_DIV', 'T_MOD'):
            multiplicative_node = Node('Multiplicative')
            multiplicative_node.add_child(lhs)
            
            token = self.consume(self.peek())
            multiplicative_node.add_child(Node('Operator', token[1]))
            
            rhs = self.unary_expr()
            multiplicative_node.add_child(rhs)
            
            lhs = multiplicative_node
        
        return lhs

    def unary_expr(self):
        """Parse unary_expr -> (!|-) unary_expr | postfix_expr"""
        if self.peek() in ('T_NOT', 'T_MINUS'):
            unary_node = Node('Unary')
            
            token = self.consume(self.peek())
            unary_node.add_child(Node('Operator', token[1]))
            
            expr = self.unary_expr()
            unary_node.add_child(expr)
            
            return unary_node
        
        return self.postfix_expr()

    def postfix_expr(self):
        """Parse postfix_expr -> primary_expr (. ID | [expr] | (args?))*"""
        expr = self.primary_expr()
        
        while self.peek() in ('T_DOT', 'T_LBRACKET', 'T_LPAREN'):
            if self.peek() == 'T_DOT':
                # Member access
                dot_node = Node('MemberAccess')
                dot_node.add_child(expr)
                
                token = self.consume('T_DOT')
                dot_node.add_child(Node('Operator', token[1]))
                
                token = self.consume('T_ID')
                dot_node.add_child(Node('Identifier', token[1]))
                
                expr = dot_node
            
            elif self.peek() == 'T_LBRACKET':
                # Array access
                array_node = Node('ArrayAccess')
                array_node.add_child(expr)
                
                token = self.consume('T_LBRACKET')
                array_node.add_child(Node('Punctuation', token[1]))
                
                index_expr = self.expr()
                array_node.add_child(index_expr)
                
                token = self.consume('T_RBRACKET')
                array_node.add_child(Node('Punctuation', token[1]))
                
                expr = array_node
            
            elif self.peek() == 'T_LPAREN':
                # Method call
                call_node = Node('MethodCall')
                call_node.add_child(expr)
                
                token = self.consume('T_LPAREN')
                call_node.add_child(Node('Punctuation', token[1]))
                
                # Arguments (optional)
                if self.peek() != 'T_RPAREN':
                    args_node = self.args()
                    call_node.add_child(args_node)
                
                token = self.consume('T_RPAREN')
                call_node.add_child(Node('Punctuation', token[1]))
                
                expr = call_node
        
        return expr

    def args(self):
        """Parse args -> expr (, expr)*"""
        args_node = Node('Arguments')
        
        # First argument
        expr_node = self.expr()
        args_node.add_child(expr_node)
        
        # Additional arguments
        while self.peek() == 'T_COMMA':
            token = self.consume('T_COMMA')
            args_node.add_child(Node('Punctuation', token[1]))
            
            expr_node = self.expr()
            args_node.add_child(expr_node)
        
        return args_node

    def primary_expr(self):
        """
        Parse primary_expr -> ID | INT | STRING | BOOL | NULL | 
                              THIS | ( expr ) | new ID ( args? )
        """
        if self.peek() == 'T_ID':
            token = self.consume('T_ID')
            return Node('Identifier', token[1])
        
        elif self.peek() == 'T_INT':
            token = self.consume('T_INT')
            return Node('IntLiteral', token[1])
        
        elif self.peek() == 'T_STRING':
            token = self.consume('T_STRING')
            return Node('StringLiteral', token[1])
        
        elif self.peek() == 'T_BOOL':
            token = self.consume('T_BOOL')
            return Node('BoolLiteral', token[1])
        
        elif self.peek() == 'T_NULL':
            token = self.consume('T_NULL')
            return Node('NullLiteral', token[1])
        
        elif self.peek() == 'T_THIS':
            token = self.consume('T_THIS')
            return Node('ThisLiteral', token[1])
        
        elif self.peek() == 'T_LPAREN':
            paren_node = Node('ParenExpr')
            
            token = self.consume('T_LPAREN')
            paren_node.add_child(Node('Punctuation', token[1]))
            
            expr_node = self.expr()
            paren_node.add_child(expr_node)
            
            token = self.consume('T_RPAREN')
            paren_node.add_child(Node('Punctuation', token[1]))
            
            return paren_node
        
        elif self.peek() == 'T_NEW':
            new_node = Node('NewExpr')
            
            token = self.consume('T_NEW')
            new_node.add_child(Node('Keyword', token[1]))
            
            token = self.consume('T_ID')
            new_node.add_child(Node('Identifier', token[1]))
            
            token = self.consume('T_LPAREN')
            new_node.add_child(Node('Punctuation', token[1]))
            
            # Arguments (optional)
            if self.peek() != 'T_RPAREN':
                args_node = self.args()
                new_node.add_child(args_node)
            
            token = self.consume('T_RPAREN')
            new_node.add_child(Node('Punctuation', token[1]))
            
            return new_node
        
        else:
            raise SyntaxError(f"Line {self.current_line}: Unexpected token in expression: {self.peek_token()}")


def tokenize(code):
    """Tokenize the input code"""
    tokens = []
    line_number = 1
    
    while code:
        matched = False
        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(code)
            if match:
                token_value = match.group()
                tokens.append((token_type, token_value))
                
                # Track line numbers
                if token_type == 'T_NEWLINE':
                    line_number += 1
                
                code = code[len(token_value):]
                matched = True
                break
        
        if not matched:
            if code[0].isspace():
                # Skip additional whitespace that wasn't matched by patterns
                code = code[1:]
            else:
                raise ValueError(f"Line {line_number}: Unexpected character: '{code[0]}'")
    
    return tokens


def print_parse_tree(node, indent=0):
    """Helper function to print parse tree in a more visual format"""
    print("  " * indent + f"└─ {node.type}" + (f": {node.value}" if node.value else ""))
    for child in node.children:
        if isinstance(child, Node):
            print_parse_tree(child, indent + 1)
        else:
            print("  " * (indent + 1) + f"└─ {child}")


def main():
    """Main function to test the parser"""
    sample_code = """package Test;
class Main {
  func main() int {
    int x = 10;
    if (x > 5) {
      x = x - 1;
    }
    return x;
  }
}
"""
    try:
        # Generate tokens
        print("Tokenizing...")
        tokens = tokenize(sample_code)
        
        # Print tokens for debugging
        print("\nTokens:")
        for i, (token_type, token_value) in enumerate(tokens):
            if token_type not in ('T_WHITESPACE', 'T_COMMENT', 'T_NEWLINE'):
                print(f"{i}: {token_type}: {token_value}")
        
        # Parse tokens
        print("\nParsing...")
        parser = Parser(tokens)
        parse_tree = parser.parse()
        
        # Print parse tree
        print("\nParse Tree:")
        print_parse_tree(parse_tree)
        
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except ValueError as e:
        print(f"Lexical Error: {e}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()