%{
#include <stdio.h>
#include <stdlib.h>
#include "parser.tab.h"
%}

%option noyywrap

%%
"//".*                         { /* Ignore entire single-line comment */ }
"/\*"([^*]|\*+[^*/])*\*+"/\*"  { /* Ignore multi-line comment */ }
"func"                         { return FUNC; }
"package"                      { return PACKAGE; }
"if"                           { return IF; }
"else"                         { return ELSE; }
"while"                        { return WHILE; }
"for"                          { return FOR; }
"return"                       { return RETURN; }
"break"                        { return BREAK; }
"continue"                     { return CONTINUE; }
"this"                         { return THIS; }
"class"                        { return CLASS; }
"interface"                    { return INTERFACE; }
"extends"                      { return EXTENDS; }
"implements"                   { return IMPLEMENTS; }
"new"                          { return NEW; }
"NewArray"                     { return NEW_ARRAY; }
"Print"                        { return PRINT; }
"ReadInteger"                  { return READ_INTEGER; }
"ReadLine"                     { return READ_LINE; }
"void"|"int"|"double"|"bool"|"string" { yylval.sval = strdup(yytext); return TYPE; }
[0-9]+                         { yylval.ival = atoi(yytext); return CONST_INT; }
[0-9]+\.[0-9]+                 { yylval.dval = strtod(yytext, NULL); return CONST_DOUBLE; }
"true"|"false"                 { return CONST_BOOL; }
"null"                         { return CONST_NULL; }
\"([^\"\\]|\\.)*\"             { yylval.sval = strdup(yytext); return CONST_STRING; }
"<="                           { return LTE; }
">="                           { return GTE; }
"=="                           { return EQ; }
"!="                           { return NE; }
"&&"                           { return LAND; }
"\|\|"                         { return LOR; }
"{"                            { return LCB; }
"}"                            { return RCB; }
"\["                           { return LSB; }
"\]"                           { return RSB; }
"\("                           { return LPAREN; }
"\)"                           { return RPAREN; }
"\."                           { return DOT; }
","                            { return COMMA; }
";"                            { return SEMICOLON; }
"="                            { return ASSIGN; }
"\+"                           { return PLUS; }
"-"                            { return MINUS; }
"\*"                           { return MULTIPLY; }
"/"                            { return DIVIDE; }
"%"                            { return MODULUS; }
"<"                            { return LT; }
">"                            { return GT; }
"!"                            { return LNOT; }
[ \t\n\r]+                     { /* ignore whitespace */ }
[a-zA-Z_][a-zA-Z0-9_]*         { yylval.sval = strdup(yytext); return IDENTIFIER; }
%%
