# Decaf Parser Implementation (Assignment 2)

This project implements a Parser for the Decaf programming language in Python, following the recursive descent parsing approach. The implementation includes a comprehensive lexical analyzer and recursive descent parser that generates a parse tree.

## Files Overview

- `decaf_parser.py` - Main parser implementation with lexical analyzer and recursive descent parser
- `test_decaf_parser.py` - Test cases to demonstrate parser functionality with different Decaf programs

## Features

1. **Lexical Analysis**
   - Tokenizes Decaf source code using regular expressions
   - Handles identifiers, keywords, operators, literals, etc.
   - Tracks line numbers for meaningful error messages

2. **Syntax Analysis**
   - Implements a complete recursive descent parser
   - Follows the Decaf grammar specification
   - Generates a detailed parse tree
   - Provides clear error messages with line numbers

3. **Parse Tree Generation**
   - Creates a structured representation of the program
   - Each node represents a grammatical construct
   - Visualizes the hierarchical structure of the program

4. **Error Handling**
   - Detects and reports syntax errors
   - Provides informative error messages with line numbers
   - Handles unexpected tokens and input

## Grammar Implementation

The parser implements the full Decaf grammar including:

- Package declarations
- Class definitions
- Method declarations with parameters
- Variable declarations
- Control structures (if-else, while, for)
- Expressions with operator precedence
- Method calls and object creation

## How to Run

1. Make sure you have Python 3.6+ installed

2. Run the main parser with a sample Decaf program:
   ```
   python decaf_parser.py
   ```

3. To run the test cases with multiple examples:
   ```
   python test_decaf_parser.py
   ```

## Sample Output

When you run the parser on a valid Decaf program, you'll see:

1. Tokenization results (list of tokens)
2. A success message ("Parsing successful!")
3. A visual representation of the parse tree

Example for a simple program:

```
package Test;
class Main {
  func main() int {
    int x = 10;
    if (x > 5) {
      x = x - 1;
    }
    return x;
  }
}
```

The parser generates a parse tree showing the hierarchical structure of the program with nodes for:
- Package declaration
- Class definition
- Method declaration
- Variable declaration
- If statement
- Assignment
- Return statement

## Implementation Details

### Recursive Descent Parser

The parser implements a recursive descent approach with methods for each non-terminal in the grammar:

- `program()` - Entry point for parsing
- `package_decl()` - Package declaration
- `class_decl()` - Class definition
- `method_decl()` - Method declaration
- ... (and many more)

### Parse Tree Structure

The parse tree is built using a `Node` class that contains:
- Node type
- Optional value
- List of children nodes

### Error Handling

Syntax errors are detected when the parser encounters unexpected tokens. Each error message includes:
- Line number
- Expected token
- Actual token found

## Extensions and Improvements

Possible extensions to the current implementation:
- Symbol table construction
- Semantic analysis
- Type checking
- Code generation

## Conclusion

This Decaf parser successfully implements the required functionality for Assignment 2. It can parse valid Decaf programs and generate a parse tree, as well as detect and report syntax errors in invalid programs.