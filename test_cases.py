from temp_parser import tokenize, Parser, print_parse_tree

def test_parser():
    """Test the parser with various Decaf programs"""
    
    # Test Case 1: Basic program from the assignment
    print("\n========== TEST CASE 1: Basic Program ==========")
    code1 = """package Test;
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
    run_test(code1)
    
    # Test Case 2: Program with multiple methods
    print("\n========== TEST CASE 2: Multiple Methods ==========")
    code2 = """package Calculator;
class MathOps {
  func add(int a, int b) int {
    return a + b;
  }
  
  func subtract(int a, int b) int {
    return a - b;
  }
  
  func main() int {
    int result = 0;
    result = add(10, 5);
    result = subtract(result, 2);
    return result;
  }
}
"""
    run_test(code2)
    
    # Test Case 3: Program with if-else and while loop
    print("\n========== TEST CASE 3: Control Structures ==========")
    code3 = """package Loops;
class TestControl {
  func factorial(int n) int {
    int result = 1;
    int i = 1;
    
    while (i <= n) {
      result = result * i;
      i = i + 1;
    }
    
    return result;
  }
  
  func main() int {
    int num = 5;
    int result = 0;
    
    if (num > 0) {
      result = factorial(num);
    } else {
      result = 0;
    }
    
    return result;
  }
}
"""
    run_test(code3)

def run_test(code):
    """Run a test with a given code sample"""
    try:
        # Generate tokens
        print("Tokenizing...")
        tokens = tokenize(code)
        
        # Print tokens (optional)
        print("\nTokens:")
        for token_type, token_value in tokens:
            if token_type not in ('T_WHITESPACE', 'T_NEWLINE', 'T_COMMENT'):
                print(f"{token_type}: {token_value}")
        
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
        print(f"Error: {e}")

if __name__ == "__main__":
    test_parser()
