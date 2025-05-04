%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylineno;  // Line number tracking
int yylex();  // Explicitly declare yylex() from Flex
void yyerror(const char *s);
%}

/* Declare token value types */
%union {
    int intval;
    char* strval;
}

/* Tokens */
%token T_PACKAGE T_FUNC T_INTTYPE T_IF
%token T_ID T_INTLIT
%token T_LCB T_RCB T_LPAREN T_RPAREN
%token T_ASSIGN T_SEMICOLON T_OP_REL T_OP_ADD T_OP_SUB

/* Operator Precedence and Associativity */
%right T_ASSIGN
%left T_OP_REL
%left T_OP_ADD T_OP_SUB

/* Associate tokens with union fields */
%type <strval> T_ID
%type <intval> T_INTLIT

%%

program:
    T_PACKAGE T_ID T_SEMICOLON func_decl { printf("Parsing successful!\n"); }
    ;

func_decl:
    T_FUNC T_ID T_LPAREN T_RPAREN T_INTTYPE block
    ;

block:
    T_LCB stmt_list T_RCB
    ;

stmt_list:
    stmt stmt_list
    | /* empty */
    ;

stmt:
    var_decl
    | assign_stmt
    | if_stmt
    ;

var_decl:
    T_INTTYPE T_ID T_ASSIGN expr T_SEMICOLON
    ;

assign_stmt:
    T_ID T_ASSIGN expr T_SEMICOLON
    ;

if_stmt:
    T_IF T_LPAREN expr T_OP_REL expr T_RPAREN block
    ;

expr:
    T_ID
    | T_INTLIT
    | expr T_OP_ADD expr
    | expr T_OP_SUB expr
    | expr T_OP_REL expr
    ;

%%

/* Error Handling */
void yyerror(const char *s) {
    fprintf(stderr, "Syntax error at line %d: %s\n", yylineno, s);
}

int main() {
    if (yyparse() == 0) {
        return 0;
    } else {
        return 1;
    }
}