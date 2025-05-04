lexer:
	flex lexer.l
	gcc lex.yy.c -o lexer -lfl

parser:
	bison -d parser.y
	flex lexer.l
	gcc parser.tab.c lex.yy.c -o parser -lfl

test:
	gcc test.c -o test

clean:
	rm lex.yy.c parser.tab.c parser.tab.h parser test

run: clean parser
	./parser < input.decaf
