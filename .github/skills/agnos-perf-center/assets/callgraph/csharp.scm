; agnos-perf-center call graph, C# (RQ-TRC-050, DEC-TRC-025, DEC-TRC-026). Fixed capture names: @definition and
; @definition.name (a method, constructor or local function with a block or "=>" body, and its name), @scope and
; @scope.name (namespaces, classes, structs, interfaces, records), @call and @call.name (an invocation and the expression
; invoked), @comment (for the IDs just above a definition; attributes belong to the definition already).
(method_declaration name: (identifier) @definition.name body: (_)) @definition
(constructor_declaration name: (identifier) @definition.name body: (_)) @definition
(local_function_statement name: (identifier) @definition.name body: (_)) @definition
(namespace_declaration name: (_) @scope.name) @scope
; "namespace A.B;" stands before the declarations it qualifies: the whole file is its scope (DEC-TRC-026).
(compilation_unit (file_scoped_namespace_declaration name: (_) @scope.name)) @scope
(class_declaration name: (identifier) @scope.name) @scope
(struct_declaration name: (identifier) @scope.name) @scope
(interface_declaration name: (identifier) @scope.name) @scope
(record_declaration name: (identifier) @scope.name) @scope
(invocation_expression function: (_) @call.name) @call
(comment) @comment
; The bases a class, struct, interface or record derives from (RQ-TRC-126, DEC-TRC-069, DEC-TRC-072).
(class_declaration name: (identifier) @scope.name (base_list [(identifier) (qualified_name) (generic_name)] @scope.base)) @scope
(struct_declaration name: (identifier) @scope.name (base_list [(identifier) (qualified_name) (generic_name)] @scope.base)) @scope
(interface_declaration name: (identifier) @scope.name (base_list [(identifier) (qualified_name) (generic_name)] @scope.base)) @scope
(record_declaration name: (identifier) @scope.name (base_list [(identifier) (qualified_name) (generic_name)] @scope.base)) @scope
; An object's creation, by its class (RQ-TRC-125, DEC-TRC-069); a target-typed new() names none.
(object_creation_expression type: (_) @new.name) @new
; The parameters of a definition and the arguments of a call, for the arity (RQ-TRC-127, DEC-TRC-069, DEC-TRC-073).
(method_declaration parameters: (_) @definition.parameters) @definition
(constructor_declaration parameters: (_) @definition.parameters) @definition
(local_function_statement parameters: (_) @definition.parameters) @definition
(invocation_expression arguments: (_) @call.arguments) @call
(object_creation_expression arguments: (_) @call.arguments) @new
