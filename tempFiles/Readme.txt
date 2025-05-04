Compile the Lexer:
flex decaf.l                                    # Generates lex.yy.c
bison -d decaf.y                                # Generates decaf.tab.c and decaf.tab.h
gcc lex.yy.c decaf.tab.c decaf.tab.h -o decaf_parser -lfl   # Compiles the lexer

Run the Lexer:
./decaf_parser < input.decaf     # Reads from a file
./decaf_parser                  # Reads from standard input



