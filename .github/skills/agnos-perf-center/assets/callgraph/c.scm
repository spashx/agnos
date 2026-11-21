; agnos-perf-center call graph, C (RQ-TRC-032, DEC-TRC-014). Fixed capture names: @definition and @definition.name (a
; function with a body, and its declared name), @call and @call.name (a call site and the expression called), @comment
; (for the IDs just above a definition). C has no scope that qualifies a function.
(function_definition
  declarator: (function_declarator declarator: (_) @definition.name)) @definition
(function_definition
  declarator: (pointer_declarator declarator: (function_declarator declarator: (_) @definition.name))) @definition
(function_definition
  declarator: (pointer_declarator
    declarator: (pointer_declarator declarator: (function_declarator declarator: (_) @definition.name)))) @definition
(call_expression function: (_) @call.name) @call
(comment) @comment
; The parameters of a definition and the arguments of a call, for the arity (RQ-TRC-127, DEC-TRC-069, DEC-TRC-073).
(function_definition declarator: (function_declarator parameters: (_) @definition.parameters)) @definition
(function_definition declarator: (pointer_declarator declarator: (function_declarator parameters: (_) @definition.parameters))) @definition
(call_expression arguments: (argument_list) @call.arguments) @call
