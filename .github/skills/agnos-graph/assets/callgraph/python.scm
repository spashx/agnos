; agnos-perf-center call graph, Python (RQ-TRC-050, DEC-TRC-025, DEC-TRC-026). Fixed capture names: @definition and
; @definition.name (a def, and its name), @scope and @scope.name (classes; modules are files and make no box), @call and
; @call.name (a call and the expression called), @comment (for the IDs just above a definition).
(function_definition name: (identifier) @definition.name) @definition
(class_definition name: (identifier) @scope.name) @scope
(call function: (_) @call.name) @call
(comment) @comment
; A decorator stands between the comment block and its def: taken as part of the block, it lets the block reach the def.
(decorator) @comment
; The bases a class derives from (RQ-TRC-126, DEC-TRC-069, DEC-TRC-072); a keyword argument (metaclass=) is none.
(class_definition name: (identifier) @scope.name superclasses: (argument_list [(identifier) (attribute)] @scope.base)) @scope
; The parameters of a definition and the arguments of a call, for the arity (RQ-TRC-127, DEC-TRC-069, DEC-TRC-073).
(function_definition parameters: (parameters) @definition.parameters) @definition
(call arguments: (argument_list) @call.arguments) @call
