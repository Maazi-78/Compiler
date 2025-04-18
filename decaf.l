%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "decaf.tab.h"  // Bison header file

extern int yylineno;  // Tracks line numbers for error reporting
%}

/* Regular Expressions */
%%
"package"    { return T_PACKAGE; }
"func"       { return T_FUNC; }
"int"        { return T_INTTYPE; }
"if"         { return T_IF; }

[a-zA-Z_][a-zA-Z0-9_]*  { yylval.strval = strdup(yytext); return T_ID; }
[0-9]+       { yylval.intval = atoi(yytext); return T_INTLIT; }

"{"          { return T_LCB; }
"}"          { return T_RCB; }
"("          { return T_LPAREN; }
")"          { return T_RPAREN; }
";"          { return T_SEMICOLON; }
"="          { return T_ASSIGN; }
">"          { return T_OP_REL; }
"+"          { return T_OP_ADD; }
"-"          { return T_OP_SUB; }

[ \t]+       { /* Ignore whitespace */ }
\n           { yylineno++; }  // Track line numbers

.            { printf("Unrecognized character: %s at line %d\n", yytext, yylineno); }

%%

int yywrap() { return 1; }