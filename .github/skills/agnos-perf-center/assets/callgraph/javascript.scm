; agnos-perf-center call graph, JavaScript and Node.js (RQ-TRC-050, DEC-TRC-025, DEC-TRC-026). Fixed capture names:
; @definition and @definition.name (a function declaration, a method, or a function or arrow given a name, an object key
; or a member such as "exports.f = function"), @scope and @scope.name (classes; modules are files and make no box),
; @call and @call.name (a call and the expression called), @comment (for the IDs just above a definition).
(function_declaration name: (identifier) @definition.name) @definition
(generator_function_declaration name: (identifier) @definition.name) @definition
(method_definition name: (_) @definition.name) @definition
(variable_declarator
  name: (identifier) @definition.name
  value: [(arrow_function) (function_expression) (generator_function)]) @definition
(pair
  key: (property_identifier) @definition.name
  value: [(arrow_function) (function_expression) (generator_function)]) @definition
(assignment_expression
  left: [(identifier) @definition.name (member_expression property: (property_identifier) @definition.name)]
  right: [(arrow_function) (function_expression) (generator_function)]) @definition
(class_declaration name: (identifier) @scope.name) @scope
(call_expression function: (_) @call.name) @call
(comment) @comment
; The class a class extends (RQ-TRC-126, DEC-TRC-069, DEC-TRC-072).
(class_declaration name: (identifier) @scope.name (class_heritage (_) @scope.base)) @scope
