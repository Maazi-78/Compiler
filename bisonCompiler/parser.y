%{
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

typedef struct Node {
    char *name;
    struct Node **children;
    int child_count;
} Node;

Node *create_node(char * name, int child_count, ...) {
    Node *node = (Node *)malloc(sizeof(Node));
    node->name = strdup(name);
    node->child_count = child_count;
    node->children = (Node **)malloc(child_count * sizeof(Node *));

    va_list args;
    va_start(args, child_count);
    for (int i = 0; i < child_count; ++i)
        node->children[i] = va_arg(args, Node *);
    va_end(args);
    return node;
}

Node* ident(char * lexeme) {
    return create_node(lexeme, 0);
}

Node* type(char * lexeme) {
    return create_node(lexeme, 0);
}

Node* const_int(int n) {
    char buf[20];
    sprintf(buf, "%d", n);
    return create_node(buf, 0);
}

Node* const_double(double n) {
    char buf[32];
    sprintf(buf, "%.15g", n);
    return create_node(buf, 0);
}

void flatten(Node *parent, Node *child) {
    if (!child) return;
    parent->children = realloc(parent->children, (parent->child_count + child->child_count) * sizeof(Node *));
    memcpy(parent->children + 1, child->children, child->child_count * sizeof(Node *));
    parent->child_count += child->child_count;
    free(child->children);
    free(child);
}

void print_tree(Node *node, int level) {
    if (!node) return;
    for (int i = 0; i < level; ++i)
        printf("  ");
    printf("%s\n", node->name);
    for (int i = 0; i < node->child_count; ++i) {
        print_tree(node->children[i], level + 1);
    }
}

Node* root;
int yylex();
void yyerror(const char * s);
%}

%precedence IF_WITHOUT_ELSE
%precedence ELSE

%union {
    struct Node *node;
    int ival;
    double dval;
    char *sval;
}

%token <sval> IDENTIFIER CONST_STRING TYPE CONST_BOOL CONST_NULL
%token <ival> CONST_INT
%token <dval> CONST_DOUBLE

%token COMMENT MULTILINE_COMMENT_START MULTILINE_COMMENT_END
%token PACKAGE FUNC IF ELSE WHILE FOR RETURN BREAK CONTINUE THIS CLASS INTERFACE
%token EXTENDS IMPLEMENTS NEW NEW_ARRAY PRINT READ_INTEGER READ_LINE

%token LTE GTE EQ NE LAND LOR LCB RCB LSB RSB LPAREN RPAREN DOT COMMA
%token SEMICOLON ASSIGN PLUS MINUS MULTIPLY DIVIDE MODULUS LT GT LNOT

%token WHITESPACE

%type <node> program type
%type <node> decl_list decl var_decl func_decl class_decl interface_decl variable formals formals_ extension implementations implementations_ prototype_list prototype field_list field var_decl_list
%type <node> stmt_block stmt_list stmt if_stmt while_stmt for_stmt return_stmt break_stmt print_stmt
%type <node> expr expr1 expr2 expr3 expr4 expr5 expr6 expr7 expr8 expr9 expr10 actuals actuals_ expr_list expr_list_

%%

program: PACKAGE IDENTIFIER SEMICOLON decl_list { root = create_node("Program", 2, ident($2), $4); };

decl_list: decl_list decl {
         $$ = $1; 
         $$->children = realloc($$->children, ($$->child_count + 1) * sizeof(Node *)); 
         $$->children[$$->child_count++] = $2; 
         }
         | decl { $$ = create_node("DeclList", 1, $1); };

decl: var_decl { $$ = $1; }
    | func_decl { $$ = $1; }
    | class_decl { $$ = $1; }
    | interface_decl { $$ = $1; };

var_decl: variable SEMICOLON { $$ = create_node("VarDecl", 1, $1); };

variable: type IDENTIFIER {
        $$ = create_node("Var", 2, $1, create_node($2, 0));
        };

type: TYPE { $$ = type($1); }
    | IDENTIFIER { $$ = ident($1); }
    | TYPE LSB RSB { $$ = create_node("ArrayType", 1, type($1)); } 
    | IDENTIFIER LSB RSB { $$ = create_node("ArrayType", 1, ident($1)); };

func_decl: FUNC IDENTIFIER LPAREN formals RPAREN type stmt_block {
        $$ = create_node("FuncDecl", 4, $6, create_node($2, 0), $4, $7);
        };

formals: variable formals_ {
       $$ = create_node("Formals", 1, $1);
       flatten($$, $2);
} | %empty { $$ = NULL; };

formals_: COMMA variable formals_ { 
        $$ = create_node("Formals_", 1, $2);  
        flatten($$, $3);
} | %empty { $$ = NULL; };

class_decl: CLASS IDENTIFIER extension implementations LCB field_list RCB {
        $$ = create_node("ClassDecl", 4, ident($2), $3, $4, $6);
        };

extension: EXTENDS IDENTIFIER { $$ = create_node("Extension", 1, ident($2)); }
         | %empty { $$ = NULL; };

implementations: IMPLEMENTS IDENTIFIER implementations_ {
       $$ = create_node("Implementations", 1, ident($2));
       flatten($$, $3);
   } | %empty { $$ = NULL; };

implementations_: COMMA IDENTIFIER implementations_ {
        $$ = create_node("Implementations_", 1, create_node($2, 0));  
        flatten($$, $3);
    } | %empty { $$ = NULL; };

field_list: field field_list {
          $$ = create_node("FieldList", 1, $1);
          flatten($$, $2);
      } | %empty { $$ = NULL; }

field: var_decl { $$ = $1; } | func_decl { $$ = $1; };

interface_decl: INTERFACE IDENTIFIER LCB prototype_list RCB {
        $$ = create_node("InterfaceDecl", 2, ident($2), $4);
        };

prototype_list: prototype prototype_list {
              $$ = create_node("PrototypeList", 1, $1);
              flatten($$ ,$2);
          } | %empty { $$ = NULL; };

prototype: FUNC IDENTIFIER LPAREN formals RPAREN type SEMICOLON {
         $$ = create_node("Prototype", 3, $6, ident($2), $4);
         };

stmt_block: LCB var_decl_list stmt_list RCB {
          if ($2 && $3)
            $$ = create_node("StmtBlock", 2, $2, $3);
          else if ($2)
            $$ = create_node("StmtBlock", 1, $2);
          else if ($3)
            $$ = create_node("StmtBlock", 1, $3);
          else
            $$ = create_node("StmtBlock", 0);
          };

var_decl_list: var_decl var_decl_list {
             $$ = create_node("VarDeclList", 1, $1);
             flatten($$, $2);
         } | %empty { $$ = NULL; }

stmt_list: stmt stmt_list {
         $$ = create_node("StmtList", 1, $1);
         flatten($$, $2);
     } | %empty { $$ = NULL; };

stmt: if_stmt { $$ = $1; }
    | while_stmt { $$ = $1; }
    | for_stmt { $$ = $1; }
    | return_stmt { $$ = $1; }
    | break_stmt { $$ = $1; }
    | print_stmt { $$ = $1; }
    | stmt_block { $$ = $1; }
    | expr SEMICOLON { $$ = $1; };

if_stmt: IF LPAREN expr RPAREN stmt ELSE stmt { $$ = create_node("IfStmt", 3, $3, $5, $7); } 
       | IF LPAREN expr RPAREN stmt %prec IF_WITHOUT_ELSE { $$ = create_node("IfStmt", 2, $3, $5); };

while_stmt: WHILE LPAREN expr RPAREN stmt { $$ = create_node("WhileStmt", 2, $3, $5); };

for_stmt: FOR LPAREN expr SEMICOLON expr SEMICOLON expr RPAREN stmt { $$ = create_node("ForStmt", 4, $3, $5, $7, $9); }

return_stmt: RETURN expr SEMICOLON { $$ = create_node("ReturnStmt", 1, $2); };

break_stmt: BREAK SEMICOLON { $$ = create_node("BreakStmt", 0); };

print_stmt: PRINT LPAREN expr_list RPAREN SEMICOLON { $$ = create_node("PrintStmt", 1, $3); };

expr_list: expr expr_list_ {
         $$ = create_node("ExpressionList", 1, $1);
         flatten($$, $2);
         }

expr_list_: COMMA expr expr_list_ {
          $$ = create_node("ExpressionList_", 1, $2);
          flatten($$, $3);
      } | %empty { $$ = NULL; };

expr: expr1 { $$ = $1; }
    | expr ASSIGN expr1 { $$ = create_node("Assignment", 2, $1, $3); };

expr1: expr2 { $$ = $1; }
     | expr1 LOR expr2 { $$ = create_node("LogicalOR", 2, $1, $3); };

expr2: expr3 { $$ = $1; }
     | expr2 LAND expr3 { $$ = create_node("LogicalAND", 2, $1, $3); };

expr3: expr4 { $$ = $1; }
     | expr3 EQ expr4 { $$ = create_node("Equality", 2, $1, $3); }
     | expr3 NE expr4 { $$ = create_node("NEquality", 2, $1, $3); };

expr4: expr5 { $$ = $1; }
     | expr4 LT expr5 { $$ = create_node("LessThan", 2, $1, $3); }
     | expr4 GT expr5 { $$ = create_node("GreaterThan", 2, $1, $3); }
     | expr4 LTE expr5 { $$ = create_node("LessOrEqual", 2, $1, $3); }
     | expr4 GTE expr5 { $$ = create_node("GreaterOrEqual", 2, $1, $3); };

expr5: expr6 { $$ = $1; }
     | expr5 PLUS expr6 { $$ = create_node("Add", 2, $1, $3);}
     | expr5 MINUS expr6 { $$ = create_node("Subtract", 2, $1, $3);};

expr6: expr7 { $$ = $1; }
     | expr6 MODULUS expr7 { $$ = create_node("Modulo", 2, $1, $3); }
     | expr6 DIVIDE expr7 { $$ = create_node("Divide", 2, $1, $3); }
     | expr6 MULTIPLY expr7 { $$ = create_node("Multiply", 2, $1, $3); };

expr7: expr8 { $$ = $1; }
     | MINUS expr7 { $$ = create_node("Negation", 1, $2); }
     | LNOT expr7 { $$ = create_node("LogicalNOT", 1, $2); };

expr8: CONST_INT { $$ = create_node("IntConstant", 1, const_int($1)); }
     | CONST_DOUBLE { $$ = create_node("DoubleConstant", 1, const_double($1)); }
     | CONST_BOOL { $$ = create_node("BoolConstant", 1, $1); }
     | CONST_STRING { $$ = create_node("StringConstant", 1, $1); }
     | CONST_NULL { $$ = create_node("NullConstant", 0); }
     | READ_INTEGER LPAREN RPAREN { $$ = create_node("ReadInteger", 0); }
     | READ_LINE LPAREN RPAREN { $$ = create_node("ReadLine", 0); }
     | NEW IDENTIFIER { $$ = create_node("New", 1, ident($2)); }
     | NEW_ARRAY LPAREN expr COMMA type RPAREN { $$ = create_node("NewArray", 2, $3, $5); }
     | expr9 { $$ = $1; };

expr9: expr10 { $$ = $1; }
     | expr9 DOT expr10 { $$ = create_node("MemberAccess", 2, $1, $3); }
     | expr9 LSB expr RSB { $$ = create_node("ArrayIndex", 2, $1, $3); };

expr10: LPAREN expr RPAREN { $$ = $2; }
      | THIS { $$ = create_node("This", 0); }
      | IDENTIFIER { $$ = ident($1); }
      | IDENTIFIER LPAREN actuals RPAREN { $$ = create_node("Call", 2, ident($1), $3); };

actuals: expr actuals_ {
       $$ = create_node("Actuals", 1, $1);
       flatten($$, $2);
       } | %empty { $$ = NULL; };

actuals_: COMMA expr actuals_ {
        $$ = create_node("Actuals_", 1, $2);
        flatten($$, $3);
        } | %empty { $$ = NULL; };

%%

void yyerror(const char * s) {
    fprintf(stderr, "Error: %s\n", s);
}

int main(int agrc, char **argv) {
    if (yyparse() == 0) {
        printf("Parse tree:\n");
        print_tree(root, 0);
    }
    return 0;
}
