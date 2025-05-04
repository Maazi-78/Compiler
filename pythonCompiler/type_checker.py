class SymbolTable:
    """
    Symbol table to keep track of variables, functions, and their types.
    Supports nested scopes through a scope stack.
    """
    def __init__(self):
        # Initialize with global scope
        self.scopes = [{}]
        self.current_function = None
        self.current_class = None
    
    def enter_scope(self):
        """Create a new scope."""
        self.scopes.append({})
    
    def exit_scope(self):
        """Exit the current scope."""
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Cannot exit global scope")
    
    def define(self, name, type_info):
        """Define a symbol in the current scope."""
        self.scopes[-1][name] = type_info
    
    def lookup(self, name):
        """
        Look up a symbol in all scopes, starting from the innermost.
        Returns None if symbol is not found.
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def set_current_function(self, func_info):
        """Set the current function context."""
        self.current_function = func_info
    
    def set_current_class(self, class_info):
        """Set the current class context."""
        self.current_class = class_info
    
    def get_current_function(self):
        """Get current function info."""
        return self.current_function
    
    def get_current_class(self):
        """Get current class info."""
        return self.current_class


class TypeChecker:
    """
    Type checker for the language. Analyzes AST nodes for type correctness.
    """
    def __init__(self, ast_root):
        self.ast = ast_root
        self.symbol_table = SymbolTable()
        self.errors = []
        
        # Define basic types
        self.types = {
            'int': 'int',
            'string': 'string',
            'bool': 'bool',
            'void': 'void',
            'null': 'null'
        }
        
        # Define type compatibility (what types can be implicitly converted to other types)
        self.type_compatibility = {
            'int': ['int', 'float', 'double'],
            'float': ['float', 'double'],
            'double': ['double'],
            'string': ['string'],
            'bool': ['bool'],
            'void': [],
            'null': [],
        }
    
    def check(self):
        """Start type checking from the root AST node."""
        self.check_node(self.ast)
        return len(self.errors) == 0, self.errors
    
    def check_node(self, node):
        """
        Type check a node in the AST.
        Returns the type of the node if applicable, None otherwise.
        """
        if not hasattr(node, 'type'):
            return None
            
        # Dispatch to appropriate handler method based on node type
        method_name = f'check_{node.type.lower()}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            # Process children for node types without specific handlers
            for child in node.children:
                if hasattr(child, 'type'):
                    self.check_node(child)
            return None
    
    def check_program(self, node):
        """Type check a program node."""
        for child in node.children:
            self.check_node(child)
        return None
    
    def check_classdecl(self, node):
        """Type check a class declaration."""
        # Extract class name (should be the second child after the 'class' keyword)
        class_name = None
        for child in node.children:
            if hasattr(child, 'type') and child.type == 'Identifier':
                class_name = child.value
                break
        
        if class_name:
            # Register class in symbol table
            self.symbol_table.define(class_name, {'kind': 'class', 'name': class_name})
            self.symbol_table.set_current_class({'name': class_name})
            
            # Type check class body
            for child in node.children:
                if hasattr(child, 'type') and child.type == 'ClassBody':
                    self.check_node(child)
            
            self.symbol_table.set_current_class(None)
        
        return None
    
    def check_methoddecl(self, node):
        """Type check a method declaration."""
        # Extract method name and return type
        method_name = None
        return_type = None
        params = []
        
        for child in node.children:
            if hasattr(child, 'type'):
                if child.type == 'Identifier' and not method_name:
                    method_name = child.value
                elif child.type == 'Type':
                    return_type = self.get_type_from_node(child)
                elif child.type == 'Parameters':
                    params = self.extract_parameters(child)
        
        if method_name and return_type:
            # Register method in symbol table
            method_info = {
                'kind': 'method',
                'name': method_name,
                'return_type': return_type,
                'params': params
            }
            self.symbol_table.define(method_name, method_info)
            self.symbol_table.set_current_function(method_info)
            
            # Create new scope for method body
            self.symbol_table.enter_scope()
            
            # Add parameters to scope
            for param_name, param_type in params:
                self.symbol_table.define(param_name, {
                    'kind': 'variable',
                    'type': param_type
                })
            
            # Type check method body
            for child in node.children:
                if hasattr(child, 'type') and child.type == 'MethodBody':
                    self.check_node(child)
            
            # Exit method scope
            self.symbol_table.exit_scope()
            self.symbol_table.set_current_function(None)
        
        return None
    
    def extract_parameters(self, params_node):
        """Extract parameter names and types from a Parameters node."""
        parameters = []
        current_type = None
        
        for child in params_node.children:
            if hasattr(child, 'type'):
                if child.type == 'Type':
                    current_type = self.get_type_from_node(child)
                elif child.type == 'Identifier' and current_type:
                    param_name = child.value
                    parameters.append((param_name, current_type))
                    current_type = None
        
        return parameters
    
    def get_type_from_node(self, type_node):
        """Extract type name from a Type node."""
        for child in type_node.children:
            if hasattr(child, 'type') and child.type == 'Keyword':
                return child.value
        return None
    
    def check_vardecl(self, node):
        """Type check a variable declaration."""
        var_type = None
        var_name = None
        init_expr_type = None
        
        for child in node.children:
            if hasattr(child, 'type'):
                if child.type == 'Type':
                    var_type = self.get_type_from_node(child)
                elif child.type == 'Identifier' and not var_name:
                    var_name = child.value
                elif hasattr(child, 'type') and child.type not in ['Type', 'Identifier', 'Operator', 'Punctuation']:
                    init_expr_type = self.check_node(child)
        
        if var_name and var_type:
            # Check type compatibility if initialization is present
            if init_expr_type and not self.is_compatible(init_expr_type, var_type):
                self.errors.append(
                    f"Type error: Cannot assign value of type '{init_expr_type}' to variable '{var_name}' of type '{var_type}'"
                )
            
            # Register variable in symbol table
            self.symbol_table.define(var_name, {
                'kind': 'variable',
                'type': var_type
            })
        
        return var_type
    
    def check_assignment(self, node):
        """Type check an assignment expression."""
        # Get left-hand side and right-hand side types
        lhs_type = None
        rhs_type = None
        
        if len(node.children) >= 3:
            lhs_node = node.children[0]
            rhs_node = node.children[2]  # Skip the operator in the middle
            
            lhs_type = self.check_node(lhs_node)
            rhs_type = self.check_node(rhs_node)
            
            # Check if assignment is valid
            if lhs_type and rhs_type and not self.is_compatible(rhs_type, lhs_type):
                # Find variable name for better error message
                var_name = self.find_variable_name(lhs_node)
                self.errors.append(
                    f"Type error: Cannot assign value of type '{rhs_type}' to '{var_name}' of type '{lhs_type}'"
                )
        
        return lhs_type
    
    def find_variable_name(self, node):
        """Try to extract variable name from a node for better error messages."""
        if hasattr(node, 'type'):
            if node.type == 'Identifier' and hasattr(node, 'value'):
                return node.value
            for child in node.children:
                result = self.find_variable_name(child)
                if result:
                    return result
        return "expression"
    
    def check_identifier(self, node):
        """Type check an identifier (variable reference)."""
        var_name = node.value
        var_info = self.symbol_table.lookup(var_name)
        
        if not var_info:
            self.errors.append(f"Undefined variable: '{var_name}'")
            return None
        
        if var_info['kind'] == 'variable':
            return var_info['type']
        elif var_info['kind'] == 'method':
            return 'function'
        elif var_info['kind'] == 'class':
            return var_info['name']
        
        return None
    
    def check_intliteral(self, node):
        """Type check an integer literal."""
        return 'int'
    
    def check_stringliteral(self, node):
        """Type check a string literal."""
        return 'string'
    
    def check_boolliteral(self, node):
        """Type check a boolean literal."""
        return 'bool'
    
    def check_nullliteral(self, node):
        """Type check a null literal."""
        return 'null'
    
    def check_addition(self, node):
        """Check additive operators (+, -)."""
        left_type = None
        right_type = None
        operator = None
        
        for i, child in enumerate(node.children):
            if hasattr(child, 'type'):
                if child.type == 'Operator':
                    operator = child.value
                elif i == 0:
                    left_type = self.check_node(child)
                elif i == 2:
                    right_type = self.check_node(child)
        
        if left_type and right_type:
            if operator == '+':
                # String concatenation special case
                if left_type == 'string' or right_type == 'string':
                    return 'string'
                
                # Numeric addition
                if left_type in ['int', 'float', 'double'] and right_type in ['int', 'float', 'double']:
                    # Return the wider type
                    if 'double' in [left_type, right_type]:
                        return 'double'
                    elif 'float' in [left_type, right_type]:
                        return 'float'
                    else:
                        return 'int'
                
                self.errors.append(
                    f"Type error: Cannot apply operator '+' to types '{left_type}' and '{right_type}'"
                )
            elif operator == '-':
                # Numeric subtraction
                if left_type in ['int', 'float', 'double'] and right_type in ['int', 'float', 'double']:
                    # Return the wider type
                    if 'double' in [left_type, right_type]:
                        return 'double'
                    elif 'float' in [left_type, right_type]:
                        return 'float'
                    else:
                        return 'int'
                
                self.errors.append(
                    f"Type error: Cannot apply operator '-' to types '{left_type}' and '{right_type}'"
                )
        
        return None
    
    def check_multiplicative(self, node):
        """Check multiplicative operators (*, /, %)."""
        left_type = None
        right_type = None
        operator = None
        
        for i, child in enumerate(node.children):
            if hasattr(child, 'type'):
                if child.type == 'Operator':
                    operator = child.value
                elif i == 0:
                    left_type = self.check_node(child)
                elif i == 2:
                    right_type = self.check_node(child)
        
        if left_type and right_type:
            # Numeric operations
            if left_type in ['int', 'float', 'double'] and right_type in ['int', 'float', 'double']:
                # Return the wider type
                if 'double' in [left_type, right_type]:
                    return 'double'
                elif 'float' in [left_type, right_type]:
                    return 'float'
                else:
                    return 'int'
            
            self.errors.append(
                f"Type error: Cannot apply operator '{operator}' to types '{left_type}' and '{right_type}'"
            )
        
        return None
    
    def check_relational(self, node):
        """Check relational operators (<, <=, >, >=)."""
        left_type = None
        right_type = None
        
        for i, child in enumerate(node.children):
            if hasattr(child, 'type'):
                if child.type != 'Operator':
                    if i == 0:
                        left_type = self.check_node(child)
                    elif i == 2:
                        right_type = self.check_node(child)
        
        if left_type and right_type:
            # Numeric comparisons
            if left_type in ['int', 'float', 'double'] and right_type in ['int', 'float', 'double']:
                return 'bool'
            # String comparisons (lexicographical order)
            elif left_type == 'string' and right_type == 'string':
                return 'bool'
            else:
                self.errors.append(
                    f"Type error: Cannot compare types '{left_type}' and '{right_type}'"
                )
        
        return 'bool'  # Relational operators always return boolean
    
    def check_equality(self, node):
        """Check equality operators (==, !=)."""
        left_type = None
        right_type = None
        
        for i, child in enumerate(node.children):
            if hasattr(child, 'type'):
                if child.type != 'Operator':
                    if i == 0:
                        left_type = self.check_node(child)
                    elif i == 2:
                        right_type = self.check_node(child)
        
        if left_type and right_type:
            # Check if types are comparable
            if left_type == right_type:
                return 'bool'
            # null can be compared with reference types
            elif left_type == 'null' or right_type == 'null':
                return 'bool'
            # Numeric types are compatible for comparison
            elif left_type in ['int', 'float', 'double'] and right_type in ['int', 'float', 'double']:
                return 'bool'
            else:
                self.errors.append(
                    f"Type error: Cannot compare types '{left_type}' and '{right_type}' for equality"
                )
        
        return 'bool'  # Equality operators always return boolean
    
    def check_logicaland(self, node):
        """Check logical AND operator (&&)."""
        return self.check_logical_operator(node, '&&')
    
    def check_logicalor(self, node):
        """Check logical OR operator (||)."""
        return self.check_logical_operator(node, '||')
    
    def check_logical_operator(self, node, operator):
        """Generic function for logical operators (&&, ||)."""
        left_type = None
        right_type = None
        
        for i, child in enumerate(node.children):
            if hasattr(child, 'type'):
                if child.type != 'Operator':
                    if i == 0:
                        left_type = self.check_node(child)
                    elif i == 2:
                        right_type = self.check_node(child)
        
        if left_type and right_type:
            if left_type == 'bool' and right_type == 'bool':
                return 'bool'
            else:
                self.errors.append(
                    f"Type error: Cannot apply operator '{operator}' to types '{left_type}' and '{right_type}'. Expected 'bool'"
                )
        
        return 'bool'  # Logical operators always return boolean
    
    def check_unary(self, node):
        """Check unary operators (!, -)."""
        operator = None
        expr_type = None
        
        for i, child in enumerate(node.children):
            if hasattr(child, 'type'):
                if child.type == 'Operator':
                    operator = child.value
                else:
                    expr_type = self.check_node(child)
        
        if operator and expr_type:
            if operator == '!' and expr_type == 'bool':
                return 'bool'
            elif operator == '-' and expr_type in ['int', 'float', 'double']:
                return expr_type
            else:
                self.errors.append(
                    f"Type error: Cannot apply unary operator '{operator}' to type '{expr_type}'"
                )
        
        return None
    
    def check_methodcall(self, node):
        """Type check a method call."""
        method_name = None
        arg_types = []
        
        # First child is the method reference
        if len(node.children) > 0:
            method_ref = node.children[0]
            if hasattr(method_ref, 'type') and method_ref.type == 'Identifier':
                method_name = method_ref.value
        
        # Find arguments node (usually after opening parenthesis)
        for child in node.children:
            if hasattr(child, 'type') and child.type == 'Arguments':
                for arg_child in child.children:
                    if hasattr(arg_child, 'type') and arg_child.type != 'Punctuation':
                        arg_type = self.check_node(arg_child)
                        arg_types.append(arg_type)
        
        if method_name:
            method_info = self.symbol_table.lookup(method_name)
            if not method_info:
                self.errors.append(f"Undefined method: '{method_name}'")
                return None
            
            if method_info['kind'] != 'method':
                self.errors.append(f"'{method_name}' is not a method")
                return None
            
            # Check number of arguments
            expected_params = method_info['params']
            if len(arg_types) != len(expected_params):
                self.errors.append(
                    f"Method '{method_name}' expects {len(expected_params)} arguments but got {len(arg_types)}"
                )
            else:
                # Check argument types
                for i, (arg_type, param) in enumerate(zip(arg_types, expected_params)):
                    param_name, param_type = param
                    if arg_type and param_type and not self.is_compatible(arg_type, param_type):
                        self.errors.append(
                            f"Type error: Argument {i+1} of method '{method_name}' expects type '{param_type}' but got '{arg_type}'"
                        )
            
            return method_info['return_type']
        
        return None
    
    def check_returnstmt(self, node):
        """Type check a return statement."""
        expr_type = None
        
        # Check if there's an expression in the return statement
        for child in node.children:
            if hasattr(child, 'type') and child.type not in ['Keyword', 'Punctuation']:
                expr_type = self.check_node(child)
                break
        
        # Check if return type matches current function's return type
        current_func = self.symbol_table.get_current_function()
        if current_func:
            expected_type = current_func['return_type']
            
            # If no expression, treat as void return
            if expr_type is None:
                if expected_type != 'void':
                    self.errors.append(
                        f"Type error: Function '{current_func['name']}' must return a value of type '{expected_type}'"
                    )
            elif not self.is_compatible(expr_type, expected_type):
                self.errors.append(
                    f"Type error: Function '{current_func['name']}' must return a value of type '{expected_type}', but got '{expr_type}'"
                )
        
        return None
    
    def check_ifstmt(self, node):
        """Type check an if statement."""
        # Find and check the condition expression
        for child in node.children:
            if hasattr(child, 'type') and child.type not in ['Keyword', 'Punctuation', 'ThenClause', 'ElseClause']:
                cond_type = self.check_node(child)
                if cond_type != 'bool':
                    self.errors.append(
                        f"Type error: If condition must be of type 'bool', but got '{cond_type}'"
                    )
                break
        
        # Check then and else clauses
        for child in node.children:
            if hasattr(child, 'type'):
                if child.type in ['ThenClause', 'ElseClause']:
                    self.check_node(child)
        
        return None
    
    def check_thenclause(self, node):
        """Type check the then clause of an if statement."""
        for child in node.children:
            self.check_node(child)
        return None
    
    def check_elseclause(self, node):
        """Type check the else clause of an if statement."""
        for child in node.children:
            self.check_node(child)
        return None
    
    def check_whilestmt(self, node):
        """Type check a while statement."""
        # Find and check the condition expression
        cond_checked = False
        for child in node.children:
            if hasattr(child, 'type'):
                if not cond_checked and child.type not in ['Keyword', 'Punctuation']:
                    cond_type = self.check_node(child)
                    if cond_type != 'bool':
                        self.errors.append(
                            f"Type error: While condition must be of type 'bool', but got '{cond_type}'"
                        )
                    cond_checked = True
                elif cond_checked and child.type not in ['Keyword', 'Punctuation']:
                    # Check the body
                    self.check_node(child)
        
        return None
    
    def check_forstmt(self, node):
        """Type check a for statement."""
        # Check initialization, condition, and update expressions
        for child in node.children:
            if hasattr(child, 'type'):
                if child.type == 'Initialization':
                    self.check_node(child)
                elif child.type == 'Condition':
                    # Condition must be boolean if present
                    if child.children:
                        cond_type = self.check_node(child.children[0])
                        if cond_type and cond_type != 'bool':
                            self.errors.append(
                                f"Type error: For loop condition must be of type 'bool', but got '{cond_type}'"
                            )
                elif child.type == 'Update':
                    self.check_node(child)
                elif child.type not in ['Keyword', 'Punctuation']:
                    # Check the body
                    self.check_node(child)
        
        return None
    
    def check_block(self, node):
        """Type check a block statement."""
        self.symbol_table.enter_scope()
        
        for child in node.children:
            if hasattr(child, 'type') and child.type not in ['Punctuation']:
                self.check_node(child)
        
        self.symbol_table.exit_scope()
        return None
    
    def check_exprstmt(self, node):
        """Type check an expression statement."""
        for child in node.children:
            if hasattr(child, 'type') and child.type not in ['Punctuation']:
                self.check_node(child)
        return None

    def check_parenexpr(self, node):
        """Type check a parenthesized expression."""
        for child in node.children:
            if hasattr(child, 'type') and child.type not in ['Punctuation']:
                return self.check_node(child)
        return None
    
    def is_compatible(self, source_type, target_type):
        """
        Check if source_type is compatible with target_type.
        This allows for implicit conversions.
        """
        if source_type == target_type:
            return True
        
        # Handle null assignments to reference types
        if source_type == 'null':
            # In this simple language, only string is a reference type
            return target_type == 'string'
        
        # Check if source can be implicitly converted to target
        if target_type in self.type_compatibility:
            return source_type in self.type_compatibility[target_type]
        
        return False


# Example usage:
def run_type_checker(ast_root):
    """Run type checking on the given AST."""
    checker = TypeChecker(ast_root)
    success, errors = checker.check()
    
    if success:
        print("Type checking passed! No errors found.")
    else:
        print(f"Type checking failed! Found {len(errors)} errors:")
        for error in errors:
            print(f"- {error}")
    
    return success, errors


# Test cases for the assignment tasks

def test_function_overloading():
    """Test case for function overloading conflict (Task 1)."""
    print("\nTask 1: Function Overloading Conflict")
    print("-" * 50)
    
    # Create symbol table
    symbol_table = SymbolTable()
    
    # Define the first function
    symbol_table.define("compute", {
        'kind': 'method',
        'name': 'compute',
        'return_type': 'int',
        'params': [('a', 'int'), ('b', 'int')]
    })
    
    # Define the second function
    symbol_table.define("compute", {
        'kind': 'method',
        'name': 'compute',
        'return_type': 'float',
        'params': [('a', 'int'), ('b', 'float')]
    })
    
    # Try to resolve the call
    print("Checking call: compute(5, 6)")
    
    # In many languages, this would be ambiguous because 6 could be either int or float
    # But in languages like C++, the exact match (int, int) would be preferred
    print("Analysis: This is ambiguous in many type systems. The compiler should:")
    print("1. Either select the first overload (int, int) as it's an exact match")
    print("2. Or raise an ambiguity error requiring explicit casting")
    print("\nThe static type checker should likely raise an ambiguity error here.")


def test_struct_field_violation():
    """Test case for struct field type violation (Task 2)."""
    print("\nTask 2: Struct Field Type Violation")
    print("-" * 50)
    
    print("struct Student { int id; char name[20]; };")
    print("s.id = \"S123\";")
    
    print("\nAnalysis: This is a clear type violation. The 'id' field is declared as 'int'")
    print("but the assignment attempts to store a string value \"S123\".")
    print("\nThe static type checker should reject this code with an error message like:")
    print("\"Type error: Cannot assign value of type 'string' to field 'id' of type 'int'\"")


def test_implicit_conversion_chain():
    """Test case for implicit type conversion chain (Task 3)."""
    print("\nTask 3: Implicit Type Conversion Chain")
    print("-" * 50)
    
    print("int a = 5;")
    print("float b = 2.3;")
    print("double c = a + b;")
    print("char d = c;")
    
    print("\nAnalysis:")
    print("1. 'a + b': int is promoted to float, result is float (2.3 + 5 = 7.3)")
    print("2. 'double c = a + b': float is widened to double (safe)")
    print("3. 'char d = c': double is narrowed to char (unsafe, data loss)")
    
    print("\nThe first two conversions are safe and commonly allowed implicitly.")
    print("The last conversion (double to char) is unsafe and should:")
    print("1. Either be rejected by the type checker")
    print("2. Or generate a warning about potential data loss")
    print("\nGood static type checking should reject or warn about the unsafe conversion.")


if __name__ == "__main__":
    # Run test cases for the assignment tasks
    # test_function_overloading()
    # test_struct_field_violation()
    # test_implicit_conversion_chain()
    
    # You can also test with your parser's output
    from manual_parser import Parser, tokenize
    code = """package Test;
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
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    run_type_checker(ast)