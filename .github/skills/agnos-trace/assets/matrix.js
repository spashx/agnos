/* agnos-trace page script (FTR-TRC-001; ADR-TRC-003: DEC-TRC-005, DEC-TRC-007, DEC-TRC-012; ADR-TRC-002: DEC-TRC-010).
   Views (TASK-TRC-005): overview, search, filters, matrix, gaps, detail panel, deep links.
   Panels (TASK-TRC-008): splitter bars, see the "resizable panels" section.
   Graph (TASK-TRC-006): see the "graph" section — the selection's neighbourhood as a traceability flow, columns by type.
   Call graph (FTR-TRC-002, ADR-TRC-004; TASK-TRC-012): functions as nodes, calls in typed arrays, see "call graph".
   Every text taken from the data is inserted with textContent, never as HTML (RQ-TRC-022); every visual value comes
   from the design tokens' custom properties (RQ-TRC-018). */
"use strict";

(function () {
  const STARTED = performance.now();
  // RQ-TRC-010, DEC-TRC-005 as amended: the data come from <page>.data.js, written beside the page.
  const DATA = window.AGNOS_TRACE_DATA;
  if (!DATA) {
    const missing = document.querySelector("script[src]")?.getAttribute("src") || "the data script";
    document.body.replaceChildren(Object.assign(document.createElement("p"), { className: "data-missing",
      textContent: `The traceability data are missing: ${missing} must stand beside this page (with its .json twin). `
        + "Generate them again with the agnos-trace skill." }));
    return;
  }

  // ---- vocabulary ---------------------------------------------------------------------------------------------
  const TYPES = ["FTR", "RQ", "ADR", "DEC", "PLAN", "TASK"];
  const CALL_GRAPH = DATA.callGraph || null;     // only in a page generated with --call-graph (RQ-TRC-026)
  const NODE_TYPES = [...TYPES, ...(CALL_GRAPH ? ["FN"] : []), "FILE", "UNDEFINED"];
  const TYPE_NAME = {
    FTR: ["Feature", "Features"], RQ: ["Requirement", "Requirements"], ADR: ["ADR", "ADRs"],
    DEC: ["Decision", "Decisions"], PLAN: ["Plan", "Plans"], TASK: ["Task", "Tasks"], FN: ["Function", "Functions"],
    FILE: ["Source file", "Source files"], UNDEFINED: ["Undefined ID", "Undefined IDs"],
  };
  const RELATION = {
    "contains:out": "contains", "contains:in": "part of", "refs:out": "cites", "refs:in": "cited by",
    "code:out": "cites", "code:in": "cited in", "defines:out": "defines", "defines:in": "defined in",
  };
  const UNTRACED = "untraced-functions";     // an informational list, never counted as a gap (RQ-TRC-035, DEC-TRC-018)
  const COVERAGE = {
    covered: ["Covered", "a source file cites the requirement"],
    indirect: ["Indirect", "a source file cites a decision, task or ADR linked to it"],
    uncovered: ["Uncovered", "no source file cites it, directly or indirectly"],
  };
  const GAP = {
    "uncovered": ["Uncovered requirements", "No source file cites them, directly or through a decision, task or ADR linked to them.", "error"],
    "untasked": ["Requirements without a task", "No task of any plan cites them.", "warn"],
    "task-no-rq": ["Tasks without a requirement", "The task cites no requirement itself.", "warn"],
    "adr-no-rq": ["ADRs without a requirement", "Neither the ADR nor any of its decisions cites a requirement.", "warn"],
    "empty": ["Empty containers", "Features without requirements, ADRs without decisions, plans without tasks.", "warn"],
    "isolated": ["Isolated elements", "Nothing cites them and they cite nothing, nor does anything they contain.", "warn"],
    "undefined": ["Undefined IDs", "Cited by the process or the sources, but defined nowhere in the index.", "error"],
    "untraced-files": ["Untraced source files", "Scanned files that cite no ID at all.", "warn"],
    [UNTRACED]: ["Untraced functions", "Functions citing no ID in their lines or the comment just above. Informational: not counted as a gap.", "neutral"],
  };
  const SEARCH_LIMIT = 60;
  const CELL_LIMIT = 3;
  const GAP_ITEMS_SHOWN = 60;
  const EVIDENCE_SHOWN = 3;
  const PERCENT = 100;
  const FILE_PREFIX = "file:";
  const FN_PREFIX = "fn:";
  const CALLS_SHOWN = 50;               // callers or callees listed at first, and added per "more" (DEC-TRC-017)
  // RQ-TRC-047, DEC-TRC-021: the levels of detail, and the boxes drawn in place of functions above the function level.
  const DETAIL = { namespace: "namespace", class: "class", function: "function" };
  const BOX_PREFIX = "box:";            // a box's key: box:<qualified scope name>
  const NAMESPACE_KIND = "namespace";   // a scope's kind in the call graph's scope table (DEC-TRC-019)
  const CLASS_KIND = "class";
  // DEC-TRC-019 as amended (TASK-TRC-028): one box for what stands in no named namespace, anonymous ones included.
  const GLOBAL_BOX = "global";
  const GLOBAL_LABEL = "(global namespace)";                   // RQ-TRC-048
  const GLOBAL_KEY = BOX_PREFIX + "(global)";
  const BOX_KINDS = [NAMESPACE_KIND, CLASS_KIND, GLOBAL_BOX];
  const SEPARATOR_RE = /^[:.]+/;        // what joins a scope's name to an inner name (C++ "::", others ".")
  // RQ-TRC-048, DEC-TRC-023: the words of the toolbar, the legend and the panels.
  const BOX_NAME = { [NAMESPACE_KIND]: "Namespace", [CLASS_KIND]: "Class", [GLOBAL_BOX]: "Global namespace" };
  const DETAIL_CHOICES = [
    [DETAIL.namespace, "Namespace", "Namespaces only, the calls merged between them; the rest in the (global namespace)"],
    [DETAIL.class, "Class", "Classes, the calls merged between them; a namespace's free functions in its own frame"],
    [DETAIL.function, "Function", "Every function, in the frame of its class or namespace"],
  ];
  const ENCLOSING_HINT = "Draw the enclosing scopes: each class inside its namespace, or the global namespace, and each "
    + "function's class inside its namespace; off, each class stands alone. Scopes drawn are namespaces, modules, "
    + "packages and classes; blocks and functions are not. Not available at the Namespace detail";
  const DETAIL_HINT = "How finely the implementation is drawn: by namespace, by class, or function by function in their scopes";
  const DETAIL_OFF_HINT = "Turn on Implementation (or the Functions type filter) to choose how finely it is drawn";
  const IMPLEMENTATION_HINT = "Draw the implementation: the functions, classes or namespaces citing the elements, at the "
    + "chosen detail, and their calls (caller → callee); same as the Functions type filter";
  const BOX_HINT = {
    [NAMESPACE_KIND]: "a namespace, module or package: its classes and functions (dashed frame)",
    [CLASS_KIND]: "a class or struct: its methods",
    [GLOBAL_BOX]: "what stands in no named namespace: global and anonymous-namespace functions, classes outside a namespace",
  };
  const SCOPE_FIELD = 7;                // a function row's scope index (-1: none)

  // ---- DOM helpers (text only) --------------------------------------------------------------------------------
  const isAbsent = (value) => value === undefined || value === null || value === false;

  function setProp(node, key, value) {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key === "on") Object.entries(value).forEach(([type, fn]) => node.addEventListener(type, fn));
    else if (key === "style") Object.entries(value).forEach(([prop, v]) => node.style.setProperty(prop, v));
    else node.setAttribute(key, value === true ? "" : String(value));
  }

  function el(tag, props, ...children) {
    const node = document.createElement(tag);
    Object.entries(props || {}).filter(([, value]) => !isAbsent(value)).forEach(([key, value]) => setProp(node, key, value));
    children.flat().filter((child) => !isAbsent(child))
      .forEach((child) => node.append(child instanceof Node ? child : document.createTextNode(String(child))));
    return node;
  }
  const $ = (id) => document.getElementById(id);
  const clear = (node) => { node.replaceChildren(); return node; };
  const plural = (type, n) => TYPE_NAME[type][n === 1 ? 0 : 1];
  const pct = (part, whole) => (whole ? Math.round((PERCENT * part) / whole) : 0);

  // ---- model --------------------------------------------------------------------------------------------------
  const nodes = new Map();
  const links = new Map();
  for (const e of DATA.elements) {
    nodes.set(e.id, {
      key: e.id, label: e.id, type: e.kind === "undefined" ? "UNDEFINED" : e.type, elementType: e.type,
      kind: e.kind, title: e.title, tri: e.tri, status: e.status, doc: e.doc, first: e.first, last: e.last,
    });
  }
  for (const f of DATA.files) {
    const key = FILE_PREFIX + f.path;
    nodes.set(key, { key, label: f.path, type: "FILE", kind: "file", title: "", tri: "", path: f.path, ids: f.ids });
  }
  const fnKeys = addFunctions();
  for (const key of nodes.keys()) links.set(key, []);
  const addLink = (from, to, kind, lines) => {
    links.get(from).push({ key: to, kind, dir: "out", lines });
    links.get(to).push({ key: from, kind, dir: "in", lines });
  };
  addEdges();
  addFunctionLinks();
  const calls = buildCalls();
  const boxes = buildBoxes();
  const nodeOf = (key) => nodes.get(key) || boxes.get(key);
  const byKeyLabel = (a, b) => nodeOf(a).label.localeCompare(nodeOf(b).label, undefined, { numeric: true });
  indexSearch();

  function addEdges() {
    for (const [source, target, kind, lines] of DATA.edges) {
      const from = kind === "code" ? FILE_PREFIX + source : source;
      if (nodes.has(from) && nodes.has(target)) addLink(from, target, kind, lines);
    }
  }

  function indexSearch() {              // the search's index, made once (DEC-TRC-017)
    for (const n of nodes.values()) {
      n.find = n.label.toLowerCase();
      n.findTitle = (n.title || "").toLowerCase();
    }
  }
  const keyOf = (gapKind, item) => (gapKind === "untraced-files" ? FILE_PREFIX + item : item);
  const typeOrder = (type) => NODE_TYPES.indexOf(type);
  const requirements = DATA.elements.filter((e) => e.kind === "element" && e.type === "RQ").map((e) => nodes.get(e.id));
  const counts = Object.fromEntries(NODE_TYPES.map((t) => [t, 0]));
  for (const n of nodes.values()) counts[n.type] += 1;
  const trigrams = [...new Set(DATA.elements.filter((e) => e.kind === "element").map((e) => e.tri))]
    .sort((a, b) => a.localeCompare(b));
  const gapBadgeClass = (gapKind, count) => "badge badge-" + (count ? GAP[gapKind][2] : "ok");
  const gapKinds = [...DATA.gapKinds, ...(CALL_GRAPH ? [UNTRACED] : [])];
  const gapItems = (gapKind) => (gapKind === UNTRACED ? CALL_GRAPH.untraced.map((i) => fnKeys[i]) : DATA.gaps[gapKind]);

  // ---- call graph (TASK-TRC-012: RQ-TRC-033, RQ-TRC-038; DEC-TRC-016) -------------------------------------------
  // Functions are nodes like the others, contained by their file and citing the IDs of their lines. Their calls stay
  // in typed arrays, compressed rows per caller and per callee, built once: a view asks callers(i) or callees(i) and
  // gets objects for those calls only, never one object per call of the whole graph.
  function addFunctions() {
    if (!CALL_GRAPH) return [];
    return CALL_GRAPH.functions.map(([file, first, last, name, language, text, dup]) => {
      const path = DATA.files[file].path;
      const suffix = dup ? "." + dup : "";
      const key = `${FN_PREFIX}${path}:${first}${suffix}`;
      nodes.set(key, { key, label: name, type: "FN", kind: "function", title: text, tri: "", doc: path, path, first, last,
        file: FILE_PREFIX + path, language: CALL_GRAPH.languages[language] });
      return key;
    });
  }

  // A function's IDs carry the lines of its file's own citations: the proofs are stored once, in the file's links.
  function addFunctionLinks() {
    for (const key of fnKeys) addLink(nodes.get(key).file, key, "defines", []);    // RQ-TRC-048, DEC-TRC-023
    const proofs = new Map();
    const proofsOf = (fileKey, id) => {
      if (!proofs.has(fileKey)) {
        proofs.set(fileKey, new Map(links.get(fileKey).filter((l) => l.kind === "code" && l.dir === "out")
          .map((l) => [l.key, l.lines])));
      }
      return proofs.get(fileKey).get(id) || [];
    };
    for (const [index, id, lineNumbers] of CALL_GRAPH?.ids || []) {
      const key = fnKeys[index];
      if (!nodes.has(id)) continue;
      const wanted = new Set(lineNumbers);
      addLink(key, id, "code", proofsOf(nodes.get(key).file, id).filter(([no]) => wanted.has(no)));
    }
  }

  function buildCalls() {
    if (!CALL_GRAPH) return null;
    const flat = CALL_GRAPH.calls;
    const n = fnKeys.length;
    const m = CALL_GRAPH.counts.calls;
    const from = new Int32Array(m);
    const to = new Int32Array(m);
    const ambiguous = new Uint8Array(m);
    const lineStart = new Int32Array(m + 1);
    const lines = new Int32Array(flat.length);
    let p = 0;
    let caller = 0;
    let c = 0;
    let l = 0;
    while (p < flat.length) {
      caller += flat[p++];
      const first = CALL_GRAPH.functions[caller][1];
      for (let k = flat[p++]; k > 0; k -= 1, c += 1) {
        from[c] = caller;
        to[c] = caller + flat[p++];
        const word = flat[p++];
        ambiguous[c] = word % 2;
        lineStart[c] = l;
        for (let count = Math.floor(word / 2); count > 0; count -= 1) lines[l++] = first + flat[p++];
      }
    }
    lineStart[c] = l;
    const rows = (ends) => {
      const start = new Int32Array(n + 1);
      for (let i = 0; i < m; i += 1) start[ends[i] + 1] += 1;
      for (let i = 0; i < n; i += 1) start[i + 1] += start[i];
      const order = new Int32Array(m);
      const fill = start.slice(0, n);
      for (let i = 0; i < m; i += 1) order[fill[ends[i]]++] = i;
      return { start, order };
    };
    const out = rows(from);
    const into = rows(to);
    const call = (i, other) => ({ key: fnKeys[other], ambiguous: ambiguous[i] === 1,
      lines: Array.from(lines.subarray(lineStart[i], lineStart[i + 1])) });
    const list = (r, i, other) => {
      const found = [];
      for (let j = r.start[i]; j < r.start[i + 1]; j += 1) found.push(call(r.order[j], other[r.order[j]]));
      return found;
    };
    // The graph's walk: visit(other key, ambiguous, direction) per call of the function, with no object per call.
    const each = (i, visit) => {
      for (let j = out.start[i]; j < out.start[i + 1]; j += 1) visit(fnKeys[to[out.order[j]]], ambiguous[out.order[j]], "out");
      for (let j = into.start[i]; j < into.start[i + 1]; j += 1) visit(fnKeys[from[into.order[j]]], ambiguous[into.order[j]], "in");
    };
    return {
      index: new Map(fnKeys.map((key, i) => [key, i])),
      callees: (i) => list(out, i, to),
      callers: (i) => list(into, i, from),
      each,
    };
  }

  // ---- boxes (TASK-TRC-024: RQ-TRC-047; DEC-TRC-019, DEC-TRC-021) ---------------------------------------------
  // A namespace or class of the scope table, or the (global) box of what stands in no named namespace (TASK-TRC-028),
  // drawn in place of its functions at the namespace and class levels. A class outside any namespace is in (global).
  function buildBoxes() {
    const found = new Map();
    const scopes = CALL_GRAPH?.scopes || [];
    const scopeKey = (i) => BOX_PREFIX + scopes[i][0];
    if (CALL_GRAPH) found.set(GLOBAL_KEY, { key: GLOBAL_KEY, label: GLOBAL_LABEL, type: "FN", box: GLOBAL_BOX, parent: null });
    const outerOf = (kind, parent) => {
      if (parent >= 0) return scopeKey(parent);
      return kind === CLASS_KIND ? GLOBAL_KEY : null;
    };
    scopes.forEach(([name, kind, parent], i) => found.set(scopeKey(i), { key: scopeKey(i), label: name, type: "FN",
      box: kind, parent: outerOf(kind, parent), scope: i }));
    // The box standing for function i: itself at the function level, its own scope at the class level, its nearest
    // namespace at the namespace level, else (global).
    const of = (i, level) => {
      if (level === DETAIL.function) return fnKeys[i];
      let scope = CALL_GRAPH.functions[i][SCOPE_FIELD];
      while (level === DETAIL.namespace && scope >= 0 && scopes[scope][1] !== NAMESPACE_KIND) scope = scopes[scope][2];
      return scope >= 0 ? scopeKey(scope) : GLOBAL_KEY;
    };
    const scopeOf = (i) => {                       // the key of a function's own scope box, null when it has none
      const scope = CALL_GRAPH.functions[i][SCOPE_FIELD];
      return scope >= 0 ? scopeKey(scope) : null;
    };
    const get = (key) => found.get(key);
    // The functions a box holds, directly or through its inner boxes: those of a scope and its inner scopes, or, for
    // (global), every function standing in it at the namespace level.
    const members = new Map();
    const within = (i, key) => {
      if (key === GLOBAL_KEY) return of(i, DETAIL.namespace) === key;
      for (let scope = CALL_GRAPH.functions[i][SCOPE_FIELD]; scope >= 0; scope = scopes[scope][2]) {
        if (scopeKey(scope) === key) return true;
      }
      return false;
    };
    const membersOf = (key) => {
      if (!members.has(key)) members.set(key, fnKeys.map((_, i) => i).filter((i) => within(i, key)));
      return members.get(key);
    };
    const innerOf = (key) => [...found.values()].filter((box) => box.parent === key).map((box) => box.key);
    return { get, of, scopeOf, membersOf, innerOf };
  }

  // ---- state --------------------------------------------------------------------------------------------------
  const state = {
    selected: null, view: "overview", search: "", coverage: "all", sort: { column: "id", dir: 1 },
    types: new Set(NODE_TYPES.filter((t) => t !== "FN")),   // functions off at load (RQ-TRC-034, DEC-TRC-017)
    tris: new Set(trigrams), expandedGaps: new Set(),
  };
  const isVisible = (node) => state.types.has(node.type) && (!node.tri || state.tris.has(node.tri));

  // ---- graph (TASK-TRC-006: RQ-TRC-012, RQ-TRC-020; DEC-TRC-006) ------------------------------------------------
  // The neighbourhood of the selection is laid out as a traceability flow: one column per element family, left to
  // right, each node a labelled pill tinted with its type colour. The whole graph uses a force layout of small dots.
  const COLUMNS = [["FTR"], ["RQ"], ["ADR", "DEC"], ["PLAN", "TASK"], ["FN"], ["FILE"], ["UNDEFINED"]];
  const COLUMN_NAME = ["Features", "Requirements", "ADRs · decisions", "Plans · tasks", "Implementation", "Source files",
    "Undefined IDs"];                   // RQ-TRC-048: the code column holds functions, classes or namespaces
  // RQ-TRC-044: one look per relation — dash pattern token (none: solid), colour token, arrow at the target — read by
  // the graph's style and by the legend's drawn samples alike. Each relation has a colour of its own.
  const EDGE_LOOK = {
    contains: { dash: "--c-graph-dash-contains", colour: "--c-graph-edge-contains", arrow: "triangle",
      meaning: "specification hierarchy (feature → requirement, ADR → decision, plan → task)" },
    refs: { dash: "", colour: "--c-graph-edge-cites", arrow: "triangle", meaning: "cites (citing → cited)" },
    code: { dash: "--c-graph-dash-code", colour: "--c-graph-edge-code", arrow: "triangle",
      meaning: "cited in code (file or function → ID)" },
    ...(CALL_GRAPH ? {
      defines: { dash: "--c-graph-dash-defines", colour: "--c-graph-edge-defines", arrow: "triangle",
        meaning: "defines (file → function)" },                // RQ-TRC-048, DEC-TRC-023
      calls: { dash: "", colour: "--c-graph-edge-call", arrow: "triangle", meaning: "calls (caller → callee)" },
      ambiguous: { dash: "", colour: "--c-graph-edge-ambiguous", arrow: "triangle",
        meaning: "ambiguous call (the name matches several definitions)" },
    } : {}),
  };
  const EDGE_SELECTOR = { ambiguous: 'edge[kind = "calls"][?ambiguous]' };
  const SAMPLE_WIDTH = 32;              // the legend's line sample, in its own SVG units
  const SAMPLE_HEIGHT = 10;
  const SAMPLE_ARROW = 7;
  const MAX_DRAWN = 400;                // nodes drawn at most, nearest levels first (RQ-TRC-037, DEC-TRC-017)
  const MAX_ROWS = 18;                  // a taller column wraps into sub-columns
  const MAX_PER_COLUMN = 72;            // beyond this, the column ends with a "+n more" note
  const MONO_CHAR_RATIO = 0.62;         // width of a monospace character, as a share of the font size
  const LABEL_MAX_CHARS = 26;
  const WHOLE_GRAPH_WARN = 1500;        // the whole graph above this many nodes asks before drawing
  const COSE_ITERATIONS = 600;
  const STRIPE_PERCENT = 7;             // the type colour band at the left of a pill, as a share of its width
  const BOW_RATIO = 0.35;               // how far a same-column edge bows out, as a share of its height
  const BOW_WEIGHT = 0.5;               // the bow's control point sits halfway along the edge
  const graph = createGraph();

  function shortLabel(n) {
    return clip(n.type === "FILE" ? n.label.split("/").pop() : n.label);
  }

  function clip(text) {
    return text.length > LABEL_MAX_CHARS ? `${text.slice(0, LABEL_MAX_CHARS - 1)}…` : text;
  }

  // A name drawn inside its box, without the box's own name: "send" in net::Port, "Port" in net (DEC-TRC-020).
  function nameIn(name, outer) {
    return outer && name.startsWith(outer) ? name.slice(outer.length).replace(SEPARATOR_RE, "") || name : name;
  }

  // The nearest levels of a walk (its Map's first entries), the last one cut where MAX_DRAWN falls.
  function nearest(levels) {
    return levels.size > MAX_DRAWN ? new Map([...levels].slice(0, MAX_DRAWN)) : levels;
  }

  // The call-site count of one call link (RQ-TRC-046).
  function callSites(caller, callee) {
    return calls.callees(calls.index.get(caller)).find((c) => c.key === callee)?.lines.length || 0;
  }

  // One call merged into a link between boxes: its call sites, by caller and line, and its ambiguity (DEC-TRC-021).
  function mergeCall(data, call, caller, sites) {
    data.ambiguous = (data.ambiguous ?? true) && call.ambiguous;
    if (!sites.has(data.id)) sites.set(data.id, new Set());
    for (const line of call.lines) sites.get(data.id).add(caller + line);
  }

  // The callers and callees of a selected function (DEC-TRC-017), or null when the selection is no function.
  function callSplit(selected) {
    const index = calls?.index.get(selected);
    if (index === undefined) return null;
    return { callers: new Set(calls.callers(index).map((c) => c.key)), callees: new Set(calls.callees(index).map((c) => c.key)) };
  }

  // The same split by box (DEC-TRC-020): the boxes calling the selection's box, and those it calls, among the walk's.
  function boxSplit(members, drawnOf, centre) {
    if (!boxes.get(centre)) return null;
    const split = { callers: new Set(), callees: new Set() };
    for (const key of members.keys()) {
      const index = calls.index.get(key);
      if (index === undefined || drawnOf(key) !== centre) continue;
      for (const c of calls.callers(index)) if (members.has(c.key)) split.callers.add(drawnOf(c.key));
      for (const c of calls.callees(index)) if (members.has(c.key)) split.callees.add(drawnOf(c.key));
    }
    return split;
  }

  // Where the walk starts: the selection itself, or the functions of a selected box.
  function boxStarts(start) {
    return boxes.get(start) ? boxes.membersOf(start).map((i) => fnKeys[i]) : [start];
  }

  // The order of a boxed column: box by box, the selection's own boxes first at each depth, then by name.
  function chainOrder(chains, selected) {
    const mine = chains.get(selected) || [];
    const byName = (a, b) => nodeOf(a).label.localeCompare(nodeOf(b).label, undefined, { numeric: true });
    return (a, b) => {
      const x = chains.get(a);
      const y = chains.get(b);
      for (let d = 0; d < Math.max(x.length, y.length); d += 1) {
        if (x[d] === y[d]) continue;
        if (x[d] === undefined || y[d] === undefined) return x.length - y.length;
        return (y[d] === mine[d]) - (x[d] === mine[d]) || byName(x[d], y[d]);
      }
      return (b === selected) - (a === selected) || byName(a, b);
    };
  }

  // The calls of one function to the kept nodes, as graph edges.
  function callEdges(index, key, kept) {
    const edges = [];
    calls.each(index, (other, ambiguous, dir) => {
      if (dir === "out" && other !== key && kept.has(other)) {       // a recursive call is not drawn
        edges.push({ group: "edges", data: { id: `${key}>${other}>calls`, source: key, target: other, kind: "calls",
          ambiguous: ambiguous === 1, curve: 0 } });
      }
    });
    return edges;
  }

  function createGraph() {
    const container = $("cy");
    const tip = el("div", { class: "graph-tip", role: "tooltip", hidden: true });
    $("graph-scroll").after(tip);
    let tipTimer = null;
    let cy = null;
    let whole = false;
    let depth = 1;
    let detail = DETAIL.function;       // RQ-TRC-047: the level of detail, the function level by default
    let enclosing = true;               // RQ-TRC-047: the enclosing boxes drawn around the level's own
    let centre = null;                  // the drawn node standing for the selection: itself, or its box
    let dirty = true;
    const prop = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    const num = (name) => Number.parseFloat(prop(name));
    const showFiles = () => $("show-files").checked;
    const showHierarchy = () => $("show-hierarchy").checked;
    const columnOf = (type) => COLUMNS.findIndex((c) => c.includes(type));

    function style() {
      const fontSize = num("--c-graph-label-size");
      const fill = prop("--c-graph-node-fill");
      const typeStyles = NODE_TYPES.map((t) => {
        const colour = prop(`--s-type-${t.toLowerCase()}`);
        return { selector: `node.item[type = "${t}"]`, style: { "border-color": colour,
          "background-gradient-stop-colors": [colour, colour, fill, fill],
          "background-gradient-stop-positions": [0, STRIPE_PERCENT, STRIPE_PERCENT, PERCENT] } };
      });
      return [
        { selector: "node.item", style: {
          shape: "round-rectangle", label: "data(label)", width: "data(width)", height: num("--c-graph-node-height"),
          "background-color": prop("--c-graph-node-fill"), "background-fill": "linear-gradient",
          "background-gradient-direction": "to-right", "border-width": num("--s-stroke-hairline"),
          color: prop("--c-graph-node-text"), "font-family": prop("--s-font-mono"), "font-size": fontSize,
          "font-weight": prop("--s-weight-medium"), "text-valign": "center", "text-halign": "center",
          "min-zoomed-font-size": num("--s-space-xs") } },
        ...typeStyles,
        { selector: 'node.item[type = "UNDEFINED"]', style: { "border-style": "dashed" } },
        // RQ-TRC-047, DEC-TRC-020: a box in the colour of its kind, as a pill or as the frame around its contents.
        ...BOX_KINDS.map((kind) => ({ selector: `node.box-${kind}`, style: { "border-color": prop(`--c-graph-box-${kind}`) } })),
        { selector: "node:parent", style: {
          shape: "round-rectangle", "background-fill": "solid", "background-opacity": num("--c-graph-box-fill-opacity"),
          "border-width": num("--c-graph-box-border-width"), padding: num("--c-graph-box-padding"), label: "data(label)",
          "font-family": prop("--s-font-mono"), "font-size": num("--c-graph-box-label-size"),
          "font-weight": prop("--s-weight-strong"), "text-valign": "top", "text-halign": "center",
          "text-margin-y": -num("--c-graph-box-label-gap") } },
        ...BOX_KINDS.map((kind) => ({ selector: `node:parent.box-${kind}`,
          style: { "background-color": prop(`--c-graph-box-${kind}`), color: prop(`--c-graph-box-${kind}`) } })),
        { selector: `node:parent.box-${NAMESPACE_KIND}`, style: { "border-style": "dashed" } },
        // Its own frame, label and fill only: an opacity on a compound node would fade its pills a second time.
        { selector: "node:parent.faint", style: { "border-opacity": num("--c-graph-dim"), "text-opacity": num("--c-graph-dim"),
          "background-opacity": num("--c-graph-box-fill-opacity") * num("--c-graph-dim") } },
        { selector: "node:parent.selected", style: { "border-width": num("--c-graph-selected-border-width"),
          "border-color": prop("--c-graph-selected-border") } },
        { selector: "node.header", style: {
          shape: "rectangle", label: "data(label)", width: "data(width)", height: num("--c-graph-node-height"),
          "background-opacity": 0, "border-width": 0, color: prop("--c-graph-header-color"),
          "font-family": prop("--s-font-sans"), "font-size": fontSize, "font-weight": prop("--s-weight-strong"),
          "text-transform": "uppercase", "text-valign": "center", "text-halign": "center", events: "no" } },
        ...NODE_TYPES.map((t) => ({ selector: `node.dot[type = "${t}"]`,
          style: { "background-color": prop(`--s-type-${t.toLowerCase()}`) } })),
        { selector: "node.dot", style: { label: "", width: num("--c-graph-node-size-file"), height: num("--c-graph-node-size-file"),
          shape: "ellipse", "background-fill": "solid", "border-width": 0 } },
        { selector: "edge", style: {
          width: num("--c-graph-edge-width"), "line-color": prop("--c-graph-edge"), "curve-style": "unbundled-bezier",
          "control-point-distances": "data(curve)", "control-point-weights": BOW_WEIGHT, opacity: num("--s-opacity-muted") } },
        ...Object.entries(EDGE_LOOK).map(([kind, look]) => ({ selector: EDGE_SELECTOR[kind] || `edge[kind = "${kind}"]`,
          style: edgeLook(look) })),
        // Calls: straight, the cheapest edge that still carries an arrow (DEC-TRC-017).
        { selector: 'edge[kind = "calls"]', style: { "curve-style": "straight" } },
        { selector: ".dim", style: { opacity: num("--c-graph-dim") } },
        { selector: ".faded", style: { opacity: num("--c-graph-faded") } },
        // A link away from the selection is a faint trace without arrow: only the selection's links stand out.
        { selector: "edge.faded", style: { opacity: num("--c-graph-edge-faded"), "target-arrow-shape": "none" } },
        // A highlighted link keeps its relation's colour (RQ-TRC-044): wider and opaque only.
        { selector: "edge.near", style: { width: num("--c-graph-edge-width-highlight"), opacity: 1 } },
        { selector: "node.item.selected", style: { "border-width": num("--c-graph-selected-border-width"),
          "border-color": prop("--c-graph-selected-border"), "font-weight": prop("--s-weight-bold") } },
        { selector: "node.item.hover", style: { "border-width": num("--c-graph-node-border-width") } },
      ];
    }

    const dashOf = (look) => (look.dash ? prop(look.dash).split(/\s+/).map(Number) : []);

    function edgeLook(look) {
      const colour = prop(look.colour);
      return { "line-style": look.dash ? "dashed" : "solid", ...(look.dash ? { "line-dash-pattern": dashOf(look) } : {}),
        "line-cap": look.dash === EDGE_LOOK.code.dash ? "round" : "butt", "line-color": colour,
        "target-arrow-shape": look.arrow, "target-arrow-color": colour, "arrow-scale": num("--c-graph-arrow-scale") };
    }

    // The legend's sample of a relation: the same dash, colour, width, opacity and arrow as the graph draws it.
    function edgeSample(look) {
      const ns = "http://www.w3.org/2000/svg";
      const svg = (tag, attributes) => {
        const node = document.createElementNS(ns, tag);
        Object.entries(attributes).forEach(([k, v]) => node.setAttribute(k, String(v)));
        return node;
      };
      const scale = num("--c-graph-arrow-scale");          // the graph's arrow size, so the sample's matches it
      const middle = SAMPLE_HEIGHT / 2;
      const half = middle * scale;
      const length = SAMPLE_ARROW * scale;
      const tip = SAMPLE_WIDTH;
      const base = SAMPLE_WIDTH - length;
      const head = look.arrow === "vee"
        ? `${base},${middle - half} ${tip},${middle} ${base},${middle + half} ${base + length / 2},${middle}`
        : `${base},${middle - half} ${tip},${middle} ${base},${middle + half}`;
      const line = svg("line", { x1: 0, y1: middle, x2: base, y2: middle, "stroke-width": num("--c-graph-legend-edge-width"),   // a little thicker than the graph's, to read
        "stroke-dasharray": dashOf(look).join(" ") || "none",
        "stroke-linecap": look.dash === EDGE_LOOK.code.dash ? "round" : "butt" });
      line.style.stroke = `var(${look.colour})`;
      const arrow = svg("polygon", { points: head });
      arrow.style.fill = `var(${look.colour})`;
      const box = svg("svg", { class: "legend-edge", viewBox: `0 0 ${SAMPLE_WIDTH} ${SAMPLE_HEIGHT}`, "aria-hidden": "true" });
      box.append(line, arrow);
      return box;
    }

    // RQ-TRC-048: the specification hierarchy only when asked; a file's "defines" goes with the file (nodeAllowed).
    function edgeAllowed(l) { return l.kind !== "contains" || showHierarchy(); }
    function nodeAllowed(node) { return isVisible(node) && (node.type !== "FILE" || showFiles()); }

    // Every neighbour of a node: its links, and for a function its calls (from the typed arrays).
    function eachNeighbour(key, visit) {
      for (const l of links.get(key)) if (edgeAllowed(l)) visit(l.key);
      const index = calls?.index.get(key);
      if (index !== undefined) calls.each(index, (other) => visit(other));
    }

    // The levels around the start, nearest first: the Map's order is the walk's, so its first MAX_DRAWN entries are
    // the nearest levels, the last one cut where the limit falls.
    function neighbourhood(start) {
      const starts = boxStarts(start);              // a selected box: its functions, all at level 0 (DEC-TRC-022)
      const seen = new Map(starts.map((key) => [key, 0]));
      let frontier = starts;
      for (let level = 1; level <= depth && frontier.length; level += 1) {
        const next = [];
        for (const key of frontier) {
          eachNeighbour(key, (other) => {
            if (seen.has(other) || !nodeAllowed(nodes.get(other))) return;
            seen.set(other, level);
            next.push(other);
          });
        }
        frontier = next;
      }
      return seen;
    }

    // An edge between two nodes of one column bows out to the left of it, so that it does not run over the column.
    function bow(from, to) {
      if (!from || !to || from.x !== to.x) return 0;
      const size = Math.abs(to.y - from.y) * BOW_RATIO + num("--c-graph-node-height");
      return to.y > from.y ? size : -size;
    }

    function edgesAmong(keys, positions) {
      const kept = new Set(keys);
      const edges = [];
      for (const key of keys) {
        for (const l of links.get(key)) {
          if (l.dir === "out" && kept.has(l.key) && edgeAllowed(l)) {
            const curve = positions ? bow(positions.get(key), positions.get(l.key)) : 0;
            edges.push({ group: "edges", data: { id: `${key}>${l.key}>${l.kind}`, source: key, target: l.key, kind: l.kind,
              curve } });
          }
        }
        const index = calls?.index.get(key);
        if (index !== undefined) edges.push(...callEdges(index, key, kept));
      }
      return edges;
    }

    // RQ-TRC-047, DEC-TRC-021: the walk's functions replaced by the boxes standing for them at the level of detail,
    // each box at the nearest level of its functions, in the walk's order; the other nodes stay themselves.
    function detailView(levels) {
      if (detail === DETAIL.function) return { levels, drawnOf: (key) => key, edges: edgesAmong, split: callSplit };
      const drawnOf = (key) => {
        const index = calls.index.get(key);
        return index === undefined ? key : boxes.of(index, detail);
      };
      const mapped = new Map();
      for (const [key, level] of levels) {
        const box = drawnOf(key);
        if (!mapped.has(box)) mapped.set(box, level);
      }
      return { levels: mapped, drawnOf, edges: (keys, positions) => boxEdges({ members: levels, drawnOf, keys, positions }),
        split: (centre) => boxSplit(levels, drawnOf, centre) };
    }

    // RQ-TRC-047, DEC-TRC-020: the boxes drawn around a node, outermost first. At the function level, a function's own
    // scope, and with enclosing boxes its outer scopes; at the class level, with enclosing boxes, a box's outer scopes.
    function enclosingChain(key) {
      const index = calls?.index.get(key);
      let inner = null;
      if (index !== undefined && detail === DETAIL.function) inner = boxes.scopeOf(index);
      else if (boxes.get(key) && detail === DETAIL.class && enclosing) inner = boxes.get(key).parent;
      const chain = [];
      for (let box = inner; box; box = enclosing ? boxes.get(box).parent : null) chain.unshift(box);
      return chain;
    }

    // The links among the drawn boxes and nodes, one per relation and ordered pair, nothing inside one box. A link
    // merging calls counts their call sites and is ambiguous only when every merged call is.
    function boxEdges({ members, drawnOf, keys, positions }) {
      const kept = new Set(keys);
      const edges = new Map();
      const sites = new Map();
      const add = (from, to, kind) => {
        const id = `${from}>${to}>${kind}`;
        if (!edges.has(id)) {
          const curve = kind === "calls" ? 0 : bow(positions.get(from), positions.get(to));
          edges.set(id, { group: "edges", data: { id, source: from, target: to, kind, curve } });
        }
        return edges.get(id).data;
      };
      for (const key of members.keys()) {
        const from = drawnOf(key);
        if (kept.has(from)) memberEdges(key, from, { members, drawnOf, kept, add, sites });
      }
      for (const [id, found] of sites) edges.get(id).data.count = found.size;
      return [...edges.values()];
    }

    // The links and calls of one walked node, from the box or node drawn for it to those drawn for the other ends.
    function memberEdges(key, from, { members, drawnOf, kept, add, sites }) {
      const to = (other) => (members.has(other) && kept.has(drawnOf(other)) ? drawnOf(other) : from);
      for (const l of links.get(key)) if (l.dir === "out" && edgeAllowed(l) && to(l.key) !== from) add(from, to(l.key), l.kind);
      const index = calls.index.get(key);
      for (const c of index === undefined ? [] : calls.callees(index)) {
        if (to(c.key) !== from) mergeCall(add(from, to(c.key), "calls"), c, `${key}:`, sites);
      }
    }

    function pillWidth(label) {
      return label.length * num("--c-graph-label-size") * MONO_CHAR_RATIO + 2 * num("--c-graph-node-padding");
    }

    // The flow's columns. Around a selected function, its column splits in three — callers, the function, callees —
    // so that calls run left to right, never along one column (DEC-TRC-017).
    function flowColumns(selected, split) {
      const base = COLUMNS.map((types, c) => ({ name: COLUMN_NAME[c], has: (key) => types.includes(nodeOf(key).type) }));
      if (!split) return base;
      const { callers, callees } = split;
      const isCall = (key, set) => key !== selected && nodeOf(key).type === "FN" && set.has(key);
      const at = columnOf("FN");
      return [...base.slice(0, at),
        { name: "Callers", has: (key) => isCall(key, callers) },
        { name: COLUMN_NAME[at], has: (key) => base[at].has(key) && !isCall(key, callers) && !isCall(key, callees) },
        { name: "Callees", has: (key) => isCall(key, callees) && !callers.has(key) },
        ...base.slice(at + 1)];
    }

    // The flow layout: columns left to right, each as wide as its widest pill, the selection first in its column.
    function flowElements(levels, selected, view) {
      const columns = flowColumns(selected, view.split(selected));
      const byColumn = columns.map(() => []);
      for (const key of levels.keys()) byColumn[columns.findIndex((column) => column.has(key))].push(key);
      const flow = { levels, selected, elements: [], drawn: [], positions: new Map(), left: 0 };
      byColumn.forEach((keys, c) => { if (keys.length) placeColumn(flow, keys, c, columns[c].name); });
      return { elements: [...flow.elements, ...view.edges(flow.drawn, flow.positions)], drawn: flow.drawn.length,
        total: levels.size };
    }

    // One column: its header, its pills — in rows, or one under the other in their boxes (DEC-TRC-020) — and its note.
    function placeColumn(flow, keys, c, name) {
      const chains = new Map(keys.map((key) => [key, enclosingChain(key)]));
      const boxed = [...chains.values()].some((chain) => chain.length);
      keys.sort(boxed ? chainOrder(chains, flow.selected) : (a, b) => (b === flow.selected) - (a === flow.selected)
        || nodeOf(a).label.localeCompare(nodeOf(b).label, undefined, { numeric: true }));
      const shown = keys.slice(0, MAX_PER_COLUMN);
      const boxName = (box) => (box ? boxes.get(box).label : null);
      const labels = shown.map((key) => (chains.get(key).length ? clip(nameIn(nodeOf(key).label, boxName(chains.get(key).at(-1))))
        : shortLabel(nodeOf(key))));
      const widest = Math.max(...labels.map(pillWidth));
      const placed = boxed ? boxedRows(shown, chains, flow.left, widest, c) : gridRows(shown, flow.left, widest);
      const centre = flow.left + placed.span / 2;
      const header = `${name} · ${keys.length}`;
      flow.elements.push({ group: "nodes", classes: "header", data: { id: `header:${c}`, label: header, width: pillWidth(header) },
        position: { x: centre, y: -num("--c-graph-header-gap") } });
      for (const [id, frame] of placed.frames) {
        const box = boxes.get(frame.box);
        const label = frame.parent ? clip(nameIn(box.label, boxName(frame.outer))) : shortLabel(box);
        flow.elements.push({ group: "nodes", classes: `box box-${box.box}`, data: { id, label, name: box.label, box: box.box,
          boxKey: frame.box, ...(frame.parent ? { parent: frame.parent } : {}) } });
      }
      shown.forEach((key, i) => {
        const n = nodeOf(key);
        const position = placed.points[i];
        const parent = placed.parents[i];
        flow.elements.push({ group: "nodes", classes: n.box ? `item box box-${n.box}` : "item", data: { id: key, type: n.type,
          label: labels[i], name: n.label, width: pillWidth(labels[i]), level: flow.levels.get(key),
          ...(n.box ? { box: n.box } : {}), ...(parent ? { parent } : {}) }, position });
        flow.positions.set(key, position);
        flow.drawn.push(key);
      });
      if (keys.length > shown.length) {
        const more = `+${keys.length - shown.length} more`;
        flow.elements.push({ group: "nodes", classes: "header", data: { id: `more:${c}`, label: more, width: pillWidth(more) },
          position: { x: centre, y: placed.bottom } });
      }
      flow.left += Math.max(placed.span, pillWidth(header)) + num("--c-graph-column-gap");
    }

    // Pills in rows, a taller column wrapping into sub-columns.
    function gridRows(shown, left, widest) {
      const rowGap = num("--c-graph-row-gap");
      const subColumns = Math.ceil(shown.length / MAX_ROWS);
      const rows = Math.ceil(shown.length / subColumns);
      const step = widest + num("--c-graph-sub-gap");
      const points = shown.map((_, i) => ({ x: left + widest / 2 + Math.floor(i / rows) * step, y: (i % rows) * rowGap }));
      return { points, parents: [], frames: new Map(), span: (subColumns - 1) * step + widest, bottom: rows * rowGap };
    }

    // Pills one under the other, each run of one box kept together, room left for the frames that close and open
    // between two pills; a box drawn as a pill of this column is its own frame, the others get one per column.
    function boxedRows(shown, chains, left, widest, c) {
      const rowGap = num("--c-graph-row-gap");
      const pad = num("--c-graph-box-padding");
      const open = pad + num("--c-graph-box-label-size") + num("--c-graph-box-label-gap");
      const depth = Math.max(...shown.map((key) => chains.get(key).length));
      const items = new Set(shown);
      const frameId = (box) => (items.has(box) ? box : `${box}@${c}`);
      const placed = { points: [], parents: [], frames: new Map(), span: widest + 2 * depth * pad, bottom: 0 };
      let previous = [];
      let y = 0;
      shown.forEach((key, i) => {
        const chain = chains.get(key);
        let common = 0;
        while (common < chain.length && chain[common] === previous[common]) common += 1;
        y += (i ? rowGap + (previous.length - common) * pad : 0) + (chain.length - common) * open;
        placed.points.push({ x: left + depth * pad + widest / 2, y });
        const ids = chain.map(frameId);
        ids.forEach((id, d) => {
          if (!items.has(chain[d]) && !placed.frames.has(id)) {
            placed.frames.set(id, { box: chain[d], parent: ids[d - 1], outer: chain[d - 1] });
          }
        });
        placed.parents.push(ids.at(-1));
        previous = chain;
      });
      placed.bottom = y + rowGap + previous.length * pad;
      return placed;
    }

    function wholeElements() {
      const keys = [...nodes.keys()].filter((k) => nodeAllowed(nodes.get(k)));
      return { elements: [...keys.map((key) => ({ group: "nodes", classes: "item dot",
        data: { id: key, type: nodes.get(key).type, label: shortLabel(nodes.get(key)), width: 0 } })), ...edgesAmong(keys)],
      drawn: keys.length, total: keys.length };
    }

    function ensure() {
      if (cy) return cy;
      cy = cytoscape({ container, style: style(), minZoom: num("--c-graph-zoom-min"), maxZoom: num("--c-graph-zoom-max"),
        boxSelectionEnabled: false, autoungrabify: true, hideEdgesOnViewport: Boolean(CALL_GRAPH) });   // DEC-TRC-017
      // A pill selects its element; a frame selects its box (DEC-TRC-022). A tap bubbles to the frames around its
      // target, which keeps the target: one selection.
      cy.on("tap", "node.item, node.box", (event) => select(event.target.data("boxKey") || event.target.id()));
      cy.on("mouseover", "node.item", (event) => {
        const n = nodeOf(event.target.id());
        event.target.addClass("hover");
        event.target.connectedEdges().addClass("near");
        container.title = n.title ? `${n.label} — ${n.title}` : n.label;
      });
      cy.on("mouseout", "node.item", (event) => {
        event.target.removeClass("hover");
        if (event.target.id() !== centre) event.target.connectedEdges().removeClass("near");
        highlight(centre);
        container.title = "";
      });
      // RQ-TRC-046: a link's tooltip once the pointer rests on it for the token delay.
      cy.on("mouseover", "edge", (event) => {
        clearTimeout(tipTimer);
        const at = event.renderedPosition;
        tipTimer = setTimeout(() => showTip(event.target.id(), at), num("--c-graph-tip-delay"));
      });
      cy.on("mouseout", "edge", hideTip);
      cy.on("viewport", hideTip);
      return cy;
    }

    // The relation of a drawn link, its two ends in their direction, and its proof lines.
    function tipFor(edgeId) {
      const edge = cy.getElementById(edgeId);
      const kind = edge.data("kind");
      const look = kind === "calls" && edge.data("ambiguous") ? EDGE_LOOK.ambiguous : EDGE_LOOK[kind];
      const source = edge.data("source");
      const target = edge.data("target");
      const merged = edge.data("count");               // a link merging calls between boxes (DEC-TRC-021)
      let proofs = merged ?? 0;
      if (merged === undefined && kind === "calls") proofs = callSites(source, target);
      else if (merged === undefined && links.has(source)) {
        proofs = links.get(source).filter((l) => l.dir === "out" && l.key === target && l.kind === kind)
          .reduce((sum, l) => sum + l.lines.length, 0);
      }
      let unit = proofs === 1 ? "line" : "lines";
      if (merged !== undefined) unit = proofs === 1 ? "call site" : "call sites";      // RQ-TRC-046: the merged count
      const lines = proofs ? ` · ${proofs} ${unit}` : "";
      return `${look.meaning}: ${nodeOf(source).label} → ${nodeOf(target).label}${lines}`;
    }

    function showTip(edgeId, at) {
      const scroller = $("graph-scroll");
      tip.textContent = tipFor(edgeId);
      tip.style.left = `${at.x - scroller.scrollLeft}px`;
      tip.style.top = `${at.y - scroller.scrollTop}px`;
      tip.hidden = false;
    }

    function hideTip() {
      clearTimeout(tipTimer);
      tip.hidden = true;
    }

    function highlight(key) {
      cy.elements().removeClass("selected near faded dim faint");
      // The drawn node, or the frames of a selected box with what they hold (DEC-TRC-022).
      const frames = key ? cy.nodes().filter((n) => n.data("boxKey") === key && !n.hasClass("item")) : cy.collection();
      const own = key ? cy.getElementById(key).union(frames) : cy.collection();
      const centre = own.union(frames.descendants());
      if (centre.empty()) return;
      const near = centre.closedNeighborhood();
      cy.nodes(".item").not(near).addClass(whole ? "faded" : "dim");
      // DEC-TRC-020: a frame holding nothing near the selection is faint like its pills, not a veil drawn over them.
      cy.nodes(".box").not(".item").filter((frame) => frame.descendants(".item").intersection(near).empty()).addClass("faint");
      cy.edges().not(centre.connectedEdges()).addClass("faded");
      own.addClass("selected");
      centre.connectedEdges().addClass("near");
    }

    function draw() {
      const started = performance.now();
      const key = state.selected;
      $("graph-empty").hidden = Boolean(key) || whole;
      ensure();
      cy.resize();
      let built = { elements: [], drawn: 0, total: 0 };
      centre = key;
      if (whole) built = wholeElements();
      else if (key) {
        const view = detailView(neighbourhood(key));      // the 400-node limit applies to what the level draws
        const drawnFor = new Set(boxStarts(key).map(view.drawnOf));   // a box whose functions the level draws as one
        centre = drawnFor.size === 1 ? [...drawnFor][0] : key;
        built = { ...flowElements(nearest(view.levels), centre, view), total: view.levels.size };
      }
      cy.batch(() => { cy.elements().remove(); cy.add(built.elements); });
      if (whole) cy.layout({ name: "cose", animate: false, numIter: COSE_ITERATIONS }).run();
      else cy.layout({ name: "preset" }).run();
      highlight(centre);
      frame();
      const ms = Math.round(performance.now() - started);
      const parts = [`${built.drawn} elements`, `${cy.edges().length} links`];
      if (!whole) parts.push(`depth ${depth}`);
      if (built.total > built.drawn) parts.push(`${built.total - built.drawn} not drawn`);
      parts.push(`${ms} ms`);
      $("graph-status").textContent = parts.join(" · ");
      Object.assign(container.dataset, { graphNodes: String(built.drawn), graphSelected: key || "", graphMs: String(ms) });
      dirty = false;
    }

    // Fit the drawing; in the flow view never below a readable zoom: the canvas then grows to the whole flow at that
    // zoom and the frame scrolls to its top-left corner (RQ-TRC-042).
    function frame() {
      const padding = num("--s-space-xl");
      fitCanvas();
      cy.fit(undefined, padding);
      const floor = num("--c-graph-flow-min-zoom");
      if (!whole && cy.zoom() < floor) {
        const box = cy.elements().boundingBox();
        const scroller = $("graph-scroll");
        container.style.width = `${Math.ceil(Math.max(scroller.clientWidth, box.w * floor + 2 * padding))}px`;
        container.style.height = `${Math.ceil(Math.max(scroller.clientHeight, box.h * floor + 2 * padding))}px`;
        cy.resize();
        cy.zoom(floor);
        cy.pan({ x: padding - box.x1 * floor, y: padding - box.y1 * floor });
        scroller.scrollTo(0, 0);
      }
      container.dataset.graphZoom = cy.zoom().toFixed(2);
    }

    // The canvas back to the frame's size.
    function fitCanvas() {
      container.style.removeProperty("width");
      container.style.removeProperty("height");
      cy.resize();
    }

    const visible = () => state.view === "graph";

    $("depth").addEventListener("click", (event) => {
      const b = event.target.closest("button");
      if (!b) return;
      depth = Number(b.dataset.depth);
      for (const other of $("depth").querySelectorAll("button")) other.setAttribute("aria-pressed", String(other === b));
      whole = false;
      dirty = true;
      if (visible()) draw();          // a hidden frame has no size: drawn when the view is shown
    });
    $("show-files").addEventListener("change", () => draw());
    if (CALL_GRAPH) {       // RQ-TRC-041: the Function type filter, at hand in the graph's own toolbar
      const toggle = el("input", { type: "checkbox", id: "show-functions" });
      toggle.addEventListener("change", () => {
        if (toggle.checked) state.types.add("FN"); else state.types.delete("FN");
        renderFilters();
        filtersChanged();
      });
      $("show-files").closest("label").after(el("label", { class: "toggle", title: IMPLEMENTATION_HINT }, toggle,
        " Implementation"));                                   // RQ-TRC-048
    }
    if (CALL_GRAPH) {       // RQ-TRC-047, RQ-TRC-048, DEC-TRC-022: the implementation detail and the enclosing scopes
      const choice = el("fieldset", { class: "segmented", id: "detail-level", "aria-label": "Implementation detail",
        title: DETAIL_HINT },
      el("span", { class: "segmented-label", text: "Implementation detail" }),
      ...DETAIL_CHOICES.map(([level, label, hint]) => el("button", { type: "button", "data-detail": level,
        "aria-pressed": String(level === detail), title: hint, text: label })));
      choice.addEventListener("click", (event) => {
        const b = event.target.closest("button");
        if (b) applyDetail(b.dataset.detail);
      });
      const box = el("input", { type: "checkbox", id: "show-enclosing", checked: true });
      box.addEventListener("change", () => applyEnclosing(box.checked));
      $("display").after(choice);                         // Depth, Display, Implementation detail: the reading order
      $("show-hierarchy").closest("label").after(el("label", { class: "toggle", title: ENCLOSING_HINT }, box,
        " Enclosing scopes"));
      syncImplementationControls();
    }

    // RQ-TRC-048: the detail choice and the enclosing scopes mean something only while the implementation is drawn
    // (whichever of the switch and the Functions type filter turned it off); the scopes' frames need a class level.
    function syncImplementationControls() {
      if (!CALL_GRAPH) return;
      const drawn = state.types.has("FN");
      const choice = $("detail-level");
      choice.disabled = !drawn;
      choice.title = drawn ? DETAIL_HINT : DETAIL_OFF_HINT;
      const box = $("show-enclosing");
      box.disabled = !drawn || detail === DETAIL.namespace;
      box.closest("label").classList.toggle("is-disabled", box.disabled);
    }

    // The level of detail, its button pressed.
    function applyDetail(level) {
      detail = level;
      for (const b of document.querySelectorAll("#detail-level button")) b.setAttribute("aria-pressed", String(b.dataset.detail === level));
      syncImplementationControls();
      dirty = true;
      if (visible()) draw();
    }

    function applyEnclosing(on) {
      enclosing = on;
      if ($("show-enclosing")) $("show-enclosing").checked = on;
      dirty = true;
      if (visible()) draw();
    }
    $("show-hierarchy").addEventListener("change", () => draw());
    $("fit").addEventListener("click", () => {          // the whole drawing in the frame, any zoom
      if (!cy) return;
      fitCanvas();
      cy.fit(undefined, num("--s-space-xl"));
    });
    $("whole").addEventListener("click", () => {
      const count = [...nodes.values()].filter(nodeAllowed).length;
      if (count > WHOLE_GRAPH_WARN && !window.confirm(`Draw all ${count} elements? The layout may take a while.`)) return;
      whole = true;
      draw();
    });

    clear($("legend")).append(...NODE_TYPES.map((t) => el("span", { class: "legend-item" },
      el("span", { class: `legend-shape shape-RQ t-${t}` }), TYPE_NAME[t][0])),
    ...Object.values(EDGE_LOOK).map((look) => el("span", { class: "legend-item", title: look.meaning },
      edgeSample(look), look.meaning)),
    ...(CALL_GRAPH ? BOX_KINDS.map((kind) => el("span", { class: "legend-item", title: BOX_HINT[kind] },   // RQ-TRC-047
      el("span", { class: `legend-box box-${kind}` }), BOX_NAME[kind])) : []));

    return {
      tipFor,
      setDetail: applyDetail,           // RQ-TRC-047: the level of detail, one of DETAIL's values
      setEnclosing: applyEnclosing,     // RQ-TRC-047: the enclosing boxes drawn or left out
      elements() { return cy ? cy.elements().map((e) => e.data()) : []; },
      show() { if (dirty || !cy) draw(); else cy.resize(); },
      select(key) {
        if (whole && cy) { centre = key; highlight(key); return; }
        dirty = true;
        if (visible()) draw();
      },
      refresh() { syncImplementationControls(); dirty = true; if (visible()) draw(); },
      restyle() { if (cy) cy.style(style()); },
      resize() { cy?.resize(); },
    };
  }

  // ---- header and footer --------------------------------------------------------------------------------------
  function renderHeader() {
    const meta = DATA.meta;
    const item = (label, value, title) => el("div", { class: "meta-item", title: title || value },
      el("span", { class: "meta-label", text: label }), el("span", { class: "meta-value", text: value }));
    clear($("meta")).append(item("Generated", meta.generatedAt), item("Process", meta.process),
      item("Sources", meta.sources.join(", ")));
    $("about").append(el("div", { text: `Generated by agnos-trace · graph by ${meta.library} (MIT)` }));
    document.title = `Traceability matrix — ${meta.title}`;
  }

  // ---- overview -----------------------------------------------------------------------------------------------
  function coverageCounts(list) {
    const c = { covered: 0, indirect: 0, uncovered: 0 };
    for (const rq of list) c[DATA.coverage[rq.key]] += 1;
    return c;
  }

  function stackBar(c, total) {
    return el("div", { class: "stack", role: "img",
      "aria-label": `${c.covered} covered, ${c.indirect} indirect, ${c.uncovered} uncovered of ${total}` },
      ...Object.keys(COVERAGE).map((k) => el("div", { class: `stack-part stack-${k}`, title: `${COVERAGE[k][0]}: ${c[k]}`,
        style: { width: `${total ? (PERCENT * c[k]) / total : 0}%` } })));
  }

  function searchPrefix(type) {
    if (type === "FILE") return FILE_PREFIX;
    if (type === "UNDEFINED" || type === "FN") return "";
    return `${type}-`;
  }

  function renderOverview() {
    const c = coverageCounts(requirements);
    const total = requirements.length;
    const coverageCard = el("article", { class: "card kpi" },
      el("span", { class: "kpi-label", text: "Requirements covered by source" }),
      el("span", { class: "kpi-value", text: `${pct(c.covered, total)} %` }),
      el("span", { class: "kpi-sub", text: `${c.covered} of ${total} cited by a source file · ${c.indirect} more indirectly` }));
    const typeTiles = el("article", { class: "card kpis-types" },
      ...NODE_TYPES.map((t) => el("button", { class: `kpi-type t-${t}`, type: "button",
        title: `Search ${plural(t, 2).toLowerCase()}`, on: { click: () => searchFor(searchPrefix(t), t) } },
        el("span", { class: "kpi-type-value", text: counts[t] }), el("span", { class: "kpi-type-label", text: plural(t, counts[t]) }))));
    clear($("kpis")).append(coverageCard, typeTiles);

    clear($("coverage-chart")).append(stackBar(c, total), el("div", { class: "coverage-legend" },
      ...Object.keys(COVERAGE).map((k) => el("button", { class: "coverage-item", type: "button", title: COVERAGE[k][1],
        on: { click: () => { setCoverageFilter(k); showView("matrix"); } } },
        el("span", { class: "coverage-item-label" }, el("span", { class: `legend-swatch stack-${k}` }), COVERAGE[k][0]),
        el("span", { class: "coverage-item-value", text: `${c[k]}` }),
        el("span", { class: "kpi-sub", text: `${pct(c[k], total)} % of ${total}` })))));

    clear($("gap-summary")).append(el("div", { class: "gap-rows" }, ...gapKinds.map((g) => {
      const n = gapItems(g).length;
      return el("button", { class: "gap-row", type: "button", on: { click: () => openGap(g) } },
        el("span", { class: "gap-row-label", text: GAP[g][0] }),
        el("span", { class: "gap-row-hint", text: GAP[g][1] }),
        el("span", { class: gapBadgeClass(g, n), text: n }));
    })));

    const rows = trigrams.map((tri) => {
      const list = requirements.filter((r) => r.tri === tri);
      const tc = coverageCounts(list);
      return el("tr", { title: `Show the requirements of ${tri} in the matrix`, on: { click: () => onlyTrigram(tri) } },
        el("td", {}, el("span", { class: "id", text: tri })),
        el("td", { class: "num", text: list.length }), el("td", { class: "num", text: tc.covered }),
        el("td", { class: "num", text: tc.indirect }), el("td", { class: "num", text: tc.uncovered }),
        el("td", { class: "num", text: list.length ? `${pct(tc.covered, list.length)} %` : "—" }),
        el("td", { class: "bar-cell" }, stackBar(tc, list.length)));
    });
    clear($("tri-table")).append(el("table", { class: "simple" },
      el("thead", {}, el("tr", {}, ...["Trigram", "Requirements", "Covered", "Indirect", "Uncovered", "Coverage", ""].map(
        (h, i) => el("th", { class: i > 0 && i < 6 ? "num" : null, text: h })))),
      el("tbody", {}, rows)));
    if (CALL_GRAPH) $("tri-table").closest(".card").before(callGraphCard());
  }

  // RQ-TRC-035: the call graph's counts; the untraced functions are listed, not counted among the gaps.
  function callGraphCard() {
    const c = CALL_GRAPH.counts;
    const item = (label, value, hint, onClick) => el(onClick ? "button" : "div",
      { class: "coverage-item", type: onClick ? "button" : null, title: hint, on: onClick ? { click: onClick } : null },
      el("span", { class: "coverage-item-label", text: label }), el("span", { class: "coverage-item-value", text: value }),
      el("span", { class: "kpi-sub", text: hint }));
    return el("article", { class: "card card-wide" },
      el("header", { class: "card-header" }, el("h2", { class: "card-title", text: "Call graph" }),
        el("span", { class: "card-hint", text: `${c.calls} call links between ${c.functions} functions` })),
      el("div", { class: "coverage-legend call-graph-legend" },
        item("Functions", c.functions, "search them by name", () => searchFor("", "FN")),
        item("Call links", c.calls, "one per caller and callee"),
        item("Ambiguous calls", c.ambiguous, "a name matching several definitions"),
        item("External calls", c.external, "a name defined in no scanned file"),
        item("Untraced functions", CALL_GRAPH.untraced.length, "citing no ID · informational", () => openGap(UNTRACED))));
  }

  // ---- sidebar ------------------------------------------------------------------------------------------------
  function chip(label, count, pressed, onClick, cls, title) {
    return el("button", { class: `chip ${cls || ""}`, type: "button", "aria-pressed": String(pressed), title,
      on: { click: onClick } },
    cls ? el("span", { class: `dot ${cls}` }) : null, label, el("span", { class: "chip-count", text: count }));
  }

  // RQ-TRC-045: what a filter does, said where it is.
  const typeHint = (t) => (t === "FN"
    ? "Show or hide functions in the graph (the search finds them either way)"
    : `Show or hide ${plural(t, 2).toLowerCase()} in the search and the graph`);

  function renderFilters() {
    if (CALL_GRAPH) $("show-functions").checked = state.types.has("FN");
    clear($("type-filters")).append(...NODE_TYPES.map((t) => chip(plural(t, 2), counts[t], state.types.has(t), () => {
      toggle(state.types, t); renderFilters(); filtersChanged();
    }, `t-${t}`, typeHint(t))));
    const triCount = (tri) => DATA.elements.filter((e) => e.kind === "element" && e.tri === tri).length;
    clear($("tri-filters")).append(...trigrams.map((tri) => chip(tri, triCount(tri), state.tris.has(tri), () => {
      toggle(state.tris, tri); renderFilters(); filtersChanged();
    }, null, `Show or hide the elements of the ${tri} feature area in the matrix, the search and the graph`)));
    clear($("gap-shortcuts")).append(...gapKinds.map((g) => el("li", {}, el("button", { class: "gap-shortcut", type: "button",
      title: GAP[g][1], on: { click: () => openGap(g) } }, el("span", { text: GAP[g][0] }),
      el("span", { class: gapBadgeClass(g, gapItems(g).length), text: gapItems(g).length })))));
  }

  function toggle(set, value) { if (set.has(value)) set.delete(value); else set.add(value); }

  function filtersChanged() { renderMatrix(); graph.refresh(); }

  function onlyTrigram(tri) {
    state.tris = new Set([tri]);
    renderFilters();
    filtersChanged();
    showView("matrix");
  }

  // ---- search -------------------------------------------------------------------------------------------------
  const search = $("search");
  const results = $("search-results");
  let resultKeys = [];
  let active = -1;

  function rank(node, q) {
    if (node.find === q) return 0;
    if (node.find.startsWith(q)) return 1;
    if (node.find.includes(q)) return 2;
    return node.findTitle.includes(q) ? 3 : -1;
  }

  // Functions are searched even while their type is off: that filter only keeps them out of the graph (RQ-TRC-033).
  const searchable = (node, onlyType) => (onlyType ? node.type === onlyType : node.type === "FN" || isVisible(node));

  function matches(q, onlyType) {
    const found = [];
    for (const node of nodes.values()) {
      if (!searchable(node, onlyType)) continue;
      const r = q ? rank(node, q) : 0;
      if (r >= 0) found.push([r, typeOrder(node.type), node.label, node]);
    }
    found.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2].localeCompare(b[2]));
    return found.map((f) => f[3]);
  }

  // RQ-TRC-049, DEC-TRC-024: a result's tooltip, the page's own, beside the list after the quick delay.
  const searchTip = $("search-tip");
  let searchTipTimer = null;
  const quickDelay = () => Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--c-search-tip-delay"));

  function hideSearchTip() {
    clearTimeout(searchTipTimer);
    searchTip.hidden = true;
  }

  function showSearchTip(item, n) {
    clear(searchTip).append(
      el("div", { class: "search-tip-kind" }, el("span", { class: `dot t-${n.type}` }), TYPE_NAME[n.type][0]),
      el("div", { class: "search-tip-name", text: n.label }),
      n.title ? el("div", { class: "search-tip-title", text: n.title }) : null,
      n.doc ? el("div", { class: "search-tip-location", text: `${n.doc}:${n.first}-${n.last}` }) : null);
    searchTip.hidden = false;
    const row = item.getBoundingClientRect();
    const side = results.getBoundingClientRect();
    searchTip.style.left = `${Math.max(0, Math.min(side.right, window.innerWidth - searchTip.offsetWidth))}px`;
    searchTip.style.top = `${Math.max(0, Math.min(row.top, window.innerHeight - searchTip.offsetHeight))}px`;
  }

  function scheduleSearchTip(item, key) {
    hideSearchTip();
    searchTipTimer = setTimeout(() => showSearchTip(item, nodes.get(key)), quickDelay());
  }
  results.addEventListener("mouseleave", hideSearchTip);
  results.addEventListener("scroll", hideSearchTip);

  function renderResults(onlyType) {
    const q = search.value.trim().toLowerCase();
    state.search = q;
    renderMatrix();
    hideSearchTip();
    if (!q && !onlyType) { closeResults(); return; }
    const found = matches(q, onlyType);
    resultKeys = found.slice(0, SEARCH_LIMIT).map((n) => n.key);
    active = resultKeys.length ? 0 : -1;
    clear(results).append(...(resultKeys.length ? resultKeys.map((key, i) => {
      const n = nodes.get(key);
      return el("li", { class: `search-result t-${n.type}`, role: "option", "aria-selected": String(i === active),
        on: { mousedown: (event) => { event.preventDefault(); pick(i); },
          mouseenter: (event) => scheduleSearchTip(event.currentTarget, key) } },
        el("span", { class: "id-link" }, el("span", { class: `dot t-${n.type}` }), el("span", { class: "id", text: n.label })),
        n.title ? el("span", { class: "search-result-title", text: n.title }) : null);
    }) : [el("li", { class: "search-empty", text: "No element matches." })]));
    if (found.length > SEARCH_LIMIT) {
      results.append(el("li", { class: "search-empty", text: `${found.length - SEARCH_LIMIT} more — refine the search` }));
    }
    results.hidden = false;
    search.setAttribute("aria-expanded", "true");
  }

  function closeResults() {
    hideSearchTip();
    results.hidden = true;
    search.setAttribute("aria-expanded", "false");
  }

  function moveActive(step) {
    if (!resultKeys.length) return;
    active = (active + step + resultKeys.length) % resultKeys.length;
    [...results.children].forEach((li, i) => li.setAttribute("aria-selected", String(i === active)));
    results.children[active].scrollIntoView({ block: "nearest" });
    scheduleSearchTip(results.children[active], resultKeys[active]);
  }

  function pick(i) {
    if (i < 0 || i >= resultKeys.length) return;
    closeResults();
    select(resultKeys[i]);
    if (state.view === "overview") showView("graph");
  }

  function searchFor(text, type) {
    search.value = text;
    search.focus();
    renderResults(type);
  }

  if (CALL_GRAPH) search.placeholder = "Search ID, title, file or function…";
  search.addEventListener("input", () => renderResults());
  search.addEventListener("focus", () => { if (search.value.trim()) renderResults(); });
  search.addEventListener("blur", closeResults);
  search.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") { event.preventDefault(); moveActive(1); }
    else if (event.key === "ArrowUp") { event.preventDefault(); moveActive(-1); }
    else if (event.key === "Enter") { event.preventDefault(); pick(active); }
    else if (event.key === "Escape") { closeResults(); search.blur(); }
  });
  document.addEventListener("keydown", (event) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (event.key === "/" && !typing) { event.preventDefault(); search.focus(); search.select(); }
  });

  // ---- matrix -------------------------------------------------------------------------------------------------
  // The source files citing an element; a function's citation is one of its file's, not one more (DEC-TRC-018).
  const fileCitations = (key) => links.get(key).filter((l) => l.kind === "code" && nodes.get(l.key).type === "FILE");

  function matrixRow(rq) {
    const all = links.get(rq.key);
    const ofTypes = (types, dirs) => all.filter((l) => types.includes(nodes.get(l.key).type) && dirs.includes(l.dir)
      && l.kind !== "code").map((l) => l.key);
    const cited = fileCitations(rq.key);
    const files = cited.map((l) => l.key);
    const lines = cited.reduce((sum, l) => sum + l.lines.length, 0);
    return {
      node: rq, id: rq.key, title: rq.title, status: rq.status,
      feature: all.filter((l) => l.kind === "contains" && l.dir === "in").map((l) => l.key),
      decisions: unique(ofTypes(["ADR", "DEC"], ["in", "out"])),
      tasks: unique(ofTypes(["TASK", "PLAN"], ["in"])),
      functions: functionsCiting(rq.key),
      files: unique(files), lines, coverage: DATA.coverage[rq.key],
    };
  }

  // RQ-TRC-041: the functions citing an element, in their lines or the comment just above them.
  function functionsCiting(key) {
    return unique(links.get(key).filter((l) => l.kind === "code" && l.dir === "in" && nodes.get(l.key).type === "FN")
      .map((l) => l.key));
  }

  function unique(list) { return [...new Set(list)]; }

  // RQ-TRC-051, DEC-TRC-027: each column is declared once, with the cell it draws; the header and every row walk the
  // ordered list of keys (DEFAULT_COLUMN_ORDER, then the reader's order, RQ-TRC-052), so a header and its cells never part.
  const MATRIX_COLUMNS = [
    { key: "feature", label: "Feature", value: (r) => r.feature.join(" "), hint: "The feature that contains it",
      cell: (r) => el("td", {}, idList(r.feature), ...r.feature.map((key) => nodes.get(key).title)   // RQ-TRC-053, DEC-TRC-029
        .filter(Boolean).map((title) => el("div", { class: "cell-title", text: title }))) },
    { key: "id", label: "Requirement", value: (r) => r.id, hint: "The requirement, its title and status",
      cell: (r) => el("td", { class: "cell-requirement" }, idButton(r.id),
        el("div", { class: "cell-title", text: r.title }),
        r.status ? el("span", { class: "badge badge-neutral", text: r.status }) : null) },
    { key: "coverage", label: "Coverage", value: (r) => ["covered", "indirect", "uncovered"].indexOf(r.coverage),
      hint: "Covered: a source file cites it · Indirect: through a linked decision, task, ADR or plan · Uncovered: neither",
      cell: (r) => el("td", {}, coverageBadge(r.coverage)) },
    // A list column sorts by its count but shows IDs: its header aligns left, like its cells (only "Lines" is a number).
    { key: "decisions", label: "ADRs / decisions", value: (r) => r.decisions.length,
      hint: "ADRs and decisions citing it or cited by it", cell: (r) => el("td", {}, idList(r.decisions)) },
    { key: "tasks", label: "Plans / tasks", value: (r) => r.tasks.length, hint: "Plans and tasks citing it",
      cell: (r) => el("td", {}, idList(r.tasks)) },
    ...(CALL_GRAPH ? [{ key: "functions", label: "Functions", value: (r) => r.functions.length,
      hint: "Functions citing it in their lines or the comment just above them",
      cell: (r) => el("td", {}, idList(r.functions)) }] : []),
    { key: "files", label: "Source files", value: (r) => r.files.length, hint: "Source files citing it",
      cell: (r) => el("td", {}, idList(r.files)) },
    { key: "lines", label: "Lines", value: (r) => r.lines, num: true, hint: "Source lines citing it, all files together",
      cell: (r) => el("td", { class: "num", text: r.lines || "—" }) },
  ];
  const DEFAULT_COLUMN_ORDER = MATRIX_COLUMNS.map((c) => c.key);
  const matrixRows = requirements.map(matrixRow);

  function rowMatches(r) {
    if (!state.tris.has(r.node.tri)) return false;
    if (state.coverage !== "all" && r.coverage !== state.coverage) return false;
    const q = state.search;
    if (!q) return true;
    return [r.id, r.title, ...r.feature, ...r.decisions, ...r.tasks, ...r.functions.map((f) => nodes.get(f).label),
      ...r.files.map((f) => nodes.get(f).label)]
      .some((v) => v.toLowerCase().includes(q));
  }

  function idList(keys) {
    if (!keys.length) return el("span", { class: "cell-empty", text: "—" });
    const shown = keys.slice(0, CELL_LIMIT).map((k) => idButton(k, true));
    return el("div", { class: "cell-list" }, shown,
      keys.length > CELL_LIMIT ? el("span", { class: "cell-more", text: `+${keys.length - CELL_LIMIT}` }) : null);
  }

  function idButton(key, short) {
    const n = nodeOf(key);
    const label = n.type === "FILE" && short ? n.label.split("/").pop() : n.label;
    return el("button", { class: `id-link t-${n.type}`, type: "button", title: n.title || n.label,
      on: { click: (event) => { event.stopPropagation(); select(key); } } },
      el("span", { class: `dot t-${n.type}` }), el("span", { class: "id", text: label }));
  }

  function coverageBadge(rating) {
    return el("span", { class: `badge badge-${rating}`, title: COVERAGE[rating][1], text: COVERAGE[rating][0] });
  }

  // ---- column order (TASK-TRC-040: RQ-TRC-052; DEC-TRC-028) ----------------------------------------------------
  // The reader's order is a list of column keys kept in the browser; whatever it lacks or does not know is repaired.
  const ORDER_KEY = "agnos-trace-column-order";
  const columnOrder = repairColumnOrder(loadColumnOrder());
  let draggedColumn = null;
  let resizingColumn = false;                                  // a resize grip never starts a move

  function loadColumnOrder() {
    try { return JSON.parse(localStorage.getItem(ORDER_KEY) || "[]"); } catch (error) { return []; }   // no storage
  }

  function saveColumnOrder() {
    try {
      if (columnOrder.join() === DEFAULT_COLUMN_ORDER.join()) localStorage.removeItem(ORDER_KEY);
      else localStorage.setItem(ORDER_KEY, JSON.stringify(columnOrder));
    } catch (error) { /* the order lasts this visit */ }
  }

  // Unknown or repeated keys are dropped; a column the order lacks comes back after its predecessor in the default order.
  function repairColumnOrder(saved) {
    const order = (Array.isArray(saved) ? saved : []).filter((key, i, all) => DEFAULT_COLUMN_ORDER.includes(key) && all.indexOf(key) === i);
    DEFAULT_COLUMN_ORDER.forEach((key, i) => {
      if (order.includes(key)) return;
      const before = i ? order.indexOf(DEFAULT_COLUMN_ORDER[i - 1]) : -1;
      order.splice(before + 1, 0, key);
    });
    return order;
  }

  function orderedColumns() { return columnOrder.map((key) => MATRIX_COLUMNS.find((c) => c.key === key)); }

  function moveColumn(key, to) {
    const from = columnOrder.indexOf(key);
    if (from < 0 || to < 0 || to >= columnOrder.length || to === from) return;
    columnOrder.splice(from, 1);
    columnOrder.splice(to, 0, key);
    saveColumnOrder();
    renderMatrix();
  }

  function resetColumns() {
    columnOrder.splice(0, columnOrder.length, ...DEFAULT_COLUMN_ORDER);
    saveColumnOrder();
    resetColumnWidths();
    renderMatrix();
  }

  function columnHeaderMoves(th, key) {
    th.addEventListener("dragstart", (event) => {
      if (resizingColumn) { event.preventDefault(); return; }
      draggedColumn = key;
      try { event.dataTransfer.setData("text/plain", key); event.dataTransfer.effectAllowed = "move"; } catch (error) { /* a plain drag */ }
    });
    th.addEventListener("dragover", (event) => {
      if (!draggedColumn) return;
      event.preventDefault();
      th.classList.toggle("drop-target", draggedColumn !== key);
    });
    th.addEventListener("dragleave", () => th.classList.remove("drop-target"));
    th.addEventListener("drop", (event) => {
      if (!draggedColumn) return;
      event.preventDefault();
      const moved = draggedColumn;
      draggedColumn = null;
      moveColumn(moved, columnOrder.indexOf(key));
    });
    th.addEventListener("dragend", () => { draggedColumn = null; th.classList.remove("drop-target"); });
    th.addEventListener("keydown", (event) => {
      if (!event.altKey || (event.key !== "ArrowLeft" && event.key !== "ArrowRight")) return;
      event.preventDefault();
      moveColumn(key, columnOrder.indexOf(key) + (event.key === "ArrowRight" ? 1 : -1));
      document.querySelector(`#matrix-table th[data-column=${key}]`)?.focus();
    });
  }

  function renderMatrix() {
    const column = MATRIX_COLUMNS.find((c) => c.key === state.sort.column);
    const rows = matrixRows.filter(rowMatches).sort((a, b) => {
      const va = column.value(a);
      const vb = column.value(b);
      const order = typeof va === "number" ? va - vb : String(va).localeCompare(String(vb), undefined, { numeric: true });
      return order * state.sort.dir || a.id.localeCompare(b.id);
    });
    const ordered = orderedColumns();
    const head = el("tr", {}, ...ordered.map((c) => {
      const th = el("th", {
        class: `sortable ${c.num ? "num" : ""}`, scope: "col", "aria-sort": ariaSort(c.key), "data-column": c.key,
        draggable: "true", tabindex: "0", title: `${c.hint} · click to sort · drag, or Alt+arrow, to move`,
        on: { click: () => { state.sort = { column: c.key, dir: state.sort.column === c.key ? -state.sort.dir : 1 }; renderMatrix(); } } },
      c.label, columnGrip(c));
      columnHeaderMoves(th, c.key);
      return th;
    }));
    const body = rows.map((r) => el("tr", { class: state.selected === r.id ? "selected" : null, "data-key": r.id,
      on: { click: () => select(r.id) } }, ...ordered.map((c) => c.cell(r))));
    $("matrix-table").classList.toggle("with-functions", Boolean(CALL_GRAPH));
    clear($("matrix-table")).append(el("thead", {}, head), el("tbody", {}, body));
    applyColumnWidths();
    $("matrix-status").textContent = `${rows.length} of ${matrixRows.length} requirements`;
  }

  // ---- column widths (TASK-TRC-018: RQ-TRC-043; DEC-TRC-012) ---------------------------------------------------
  // The first resize freezes every column at its drawn width, so that one column grows or shrinks and the others stay;
  // the table is then as wide as its columns and the frame scrolls (RQ-TRC-042).
  const COLUMNS_KEY = "agnos-trace-columns";
  const columnWidths = loadColumnWidths();
  const cssNumber = (name) => Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  const headers = () => [...$("matrix-table").querySelectorAll("th[data-column]")];

  function applyColumnWidths() {
    const table = $("matrix-table");
    const custom = Object.keys(columnWidths).length > 0;
    for (const th of headers()) {
      if (!custom) {
        th.style.removeProperty("width");
        continue;
      }
      columnWidths[th.dataset.column] ??= th.offsetWidth;         // a column not kept yet: as drawn
      th.style.width = `${columnWidths[th.dataset.column]}px`;
    }
    if (custom) {
      table.style.width = `${headers().reduce((sum, th) => sum + (columnWidths[th.dataset.column] || 0), 0)}px`;
      table.style.minWidth = "auto";
    } else {
      table.style.removeProperty("width");
      table.style.removeProperty("min-width");
    }
  }

  function loadColumnWidths() {
    try { return JSON.parse(localStorage.getItem(COLUMNS_KEY) || "{}"); } catch (error) { return {}; }   // no storage
  }

  function saveColumnWidths() {
    try { localStorage.setItem(COLUMNS_KEY, JSON.stringify(columnWidths)); } catch (error) { /* the widths last this visit */ }
  }

  function setColumnWidth(key, width) {
    if (!Object.keys(columnWidths).length) for (const th of headers()) columnWidths[th.dataset.column] = th.offsetWidth;
    columnWidths[key] = Math.round(Math.max(cssNumber("--c-column-min-width"), width));
    applyColumnWidths();
    saveColumnWidths();
  }

  function resetColumnWidths() {
    for (const key of Object.keys(columnWidths)) delete columnWidths[key];
    applyColumnWidths();
    saveColumnWidths();
  }

  function dragColumn(key, grip, event) {
    event.preventDefault();
    event.stopPropagation();
    grip.setPointerCapture(event.pointerId);
    resizingColumn = true;
    const start = event.clientX;
    const width = grip.parentElement.offsetWidth;
    const move = (e) => setColumnWidth(key, width + e.clientX - start);
    const end = () => {
      resizingColumn = false;
      grip.removeEventListener("pointermove", move);
      grip.removeEventListener("pointerup", end);
      grip.removeEventListener("pointercancel", end);
    };
    grip.addEventListener("pointermove", move);
    grip.addEventListener("pointerup", end);
    grip.addEventListener("pointercancel", end);
  }

  function columnGrip(c) {
    const grip = el("span", { class: "col-grip", role: "separator", tabindex: "0", "aria-orientation": "vertical",
      "aria-label": `Resize the ${c.label} column`, title: "Drag, or use the arrow keys, to resize · double-click to reset" });
    grip.addEventListener("click", (event) => event.stopPropagation());          // a grip never sorts
    grip.addEventListener("dblclick", (event) => { event.stopPropagation(); resetColumnWidths(); });
    grip.addEventListener("pointerdown", (event) => dragColumn(c.key, grip, event));
    grip.addEventListener("mousedown", (event) => event.preventDefault());       // the grip resizes, it never drags the header
    grip.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      event.stopPropagation();
      const step = cssNumber("--c-splitter-step");
      setColumnWidth(c.key, grip.parentElement.offsetWidth + (event.key === "ArrowRight" ? step : -step));
    });
    return grip;
  }

  function ariaSort(columnKey) {
    if (state.sort.column !== columnKey) return null;
    return state.sort.dir > 0 ? "ascending" : "descending";
  }

  function setCoverageFilter(value) {
    state.coverage = value;
    for (const b of $("coverage-filter").querySelectorAll("button")) b.setAttribute("aria-pressed", String(b.dataset.coverage === value));
    renderMatrix();
  }

  $("coverage-filter").addEventListener("click", (event) => {
    const b = event.target.closest("button");
    if (b) setCoverageFilter(b.dataset.coverage);
  });

  function csvCell(value) {
    const text = String(value);
    return /[",\n;]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  }

  // The matrix rows shown, as CSV; with a call graph, a Functions column of qualified names (RQ-TRC-041).
  function csvText() {
    const withFunctions = (row, functions) => (CALL_GRAPH ? [...row, functions] : row);
    const header = [...withFunctions(["Requirement", "Title", "Status", "Feature", "ADRs / decisions", "Plans / tasks"],
      "Functions"), "Source files", "Source lines", "Coverage"];
    const lines = matrixRows.filter(rowMatches).map((r) => [...withFunctions([r.id, r.title, r.status, r.feature.join(" "),
      r.decisions.join(" "), r.tasks.join(" ")], r.functions.map((f) => nodes.get(f).label).join(" ")),
      r.files.map((f) => nodes.get(f).label).join(" "),
      fileCitations(r.id).flatMap((l) => l.lines.map((line) => `${nodes.get(l.key).label}:${line[0]}`)).join(" "),
      r.coverage]);
    return [header, ...lines].map((row) => row.map(csvCell).join(",")).join("\r\n");
  }

  function exportCsv() {
    const url = URL.createObjectURL(new Blob(["﻿", csvText()], { type: "text/csv;charset=utf-8" }));
    const a = el("a", { href: url, download: `traceability-${DATA.meta.title}.csv` });
    document.body.append(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  $("export-csv").addEventListener("click", exportCsv);
  $("reset-columns").addEventListener("click", resetColumns);

  // ---- gaps ---------------------------------------------------------------------------------------------------
  function renderGaps() {
    const total = DATA.gapKinds.reduce((sum, g) => sum + DATA.gaps[g].length, 0);
    $("gaps-count").textContent = total ? String(total) : "";
    clear($("gaps-list")).append(...gapKinds.map((g) => {
      const items = gapItems(g);
      const shown = state.expandedGaps.has(g) ? items : items.slice(0, GAP_ITEMS_SHOWN);
      return el("article", { class: "card gap-card", id: `gap-${g}` },
        el("header", { class: "card-header" },
          el("h2", { class: "card-title gap-card-title" }, GAP[g][0]),
          el("span", { class: gapBadgeClass(g, items.length), text: items.length })),
        el("p", { class: "gap-card-desc", text: GAP[g][1] }),
        items.length ? el("ul", { class: "gap-items" }, ...shown.map((item) => {
          const key = keyOf(g, item);
          const n = nodes.get(key);
          return el("li", {}, el("button", { class: "gap-item", type: "button", title: n.title || n.label, on: { click: () => select(key) } },
            el("span", { class: `dot t-${n.type}` }), el("span", { class: "id", text: n.label }),
            n.title ? el("span", { class: "gap-item-title", text: n.title }) : null));
        })) : el("div", { class: "gap-none", text: "None — the rule holds." }),
        items.length > shown.length ? el("button", { class: "link-button", type: "button",
          on: { click: () => { state.expandedGaps.add(g); renderGaps(); } }, text: `Show all ${items.length}` }) : null);
    }));
  }

  function openGap(g) {
    showView("gaps");
    const card = $(`gap-${g}`);
    if (card) card.scrollIntoView({ block: "start" });
  }

  // ---- detail panel -------------------------------------------------------------------------------------------
  function renderDetail() {
    const panel = clear($("detail"));
    const key = state.selected;
    if (!key) {
      panel.append(el("div", { class: "detail-empty" },
        el("span", { class: "detail-empty-title", text: "No element selected" }),
        el("span", { text: "Search an ID, a title or a file, or click any element of the matrix, the gaps or the graph: its links appear here, grouped by type." })));
      return;
    }
    if (boxes.get(key)) {
      renderBoxDetail(panel, boxes.get(key));
      return;
    }
    const n = nodes.get(key);
    const head = el("div", { class: `detail-head t-${n.type}` },
      el("div", { class: "detail-kind" }, el("span", { class: `dot t-${n.type}` }), TYPE_NAME[n.type][0]),
      el("h2", { class: "detail-id", text: n.label }),
      n.title ? el("p", { class: "detail-title", text: n.title }) : null,
      el("div", { class: "detail-badges" },
        n.status ? el("span", { class: "badge badge-neutral", text: n.status }) : null,
        n.type === "RQ" && DATA.coverage[key] ? coverageBadge(DATA.coverage[key]) : null,
        n.kind === "undefined" ? el("span", { class: "badge badge-error", text: "Not in the index" }) : null),
      n.doc ? el("div", { class: "detail-location", text: `${n.doc}:${n.first}-${n.last}` }) : null,
      el("div", { class: "detail-actions" },
        el("button", { class: "button button-primary", type: "button", text: "Show in graph",
          title: "Open the graph on this element and its links", on: { click: () => showView("graph") } }),
        el("button", { class: "button", type: "button", text: "Copy ID",
          title: "Copy this ID (or name) to the clipboard", on: { click: () => copy(n.label) } })));
    const groups = linksByType(key);
    const ordered = [...groups.keys()].sort((a, b) => typeOrder(a) - typeOrder(b));
    const summary = el("div", { class: "detail-summary" }, ordered.length ? ordered.map((t) =>
      el("span", { class: `badge badge-neutral t-${t}` }, el("span", { class: `dot t-${t}` }), `${plural(t, groups.get(t).size)} ${groups.get(t).size}`))
      : el("span", { class: "badge badge-error", text: "No link" }));
    const callSections = n.type === "FN" ? callGroups(calls.index.get(key)) : [];
    summary.append(...callSections.map((s) => s.badge));
    if (CALL_GRAPH && n.type === "RQ" && !groups.has("FN")) summary.append(noFunctionBadge(key));   // RQ-TRC-041
    panel.append(detailBand(n.type, head, summary),
      el("div", { class: "detail-body" }, ...callSections.map((s) => s.section), ...ordered.map((t) => linkGroup(t, groups.get(t)))));
  }

  // RQ-TRC-054, DEC-TRC-030: the identity and the tags stand in a band that does not scroll, over the body of links.
  function detailBand(type, head, summary) {
    return el("div", { class: `detail-top t-${type}` }, head, summary);
  }

  // {type: {linked key: [links]}} of an element's links.
  function linksByType(key) {
    const groups = new Map();
    for (const l of links.get(key)) {
      const type = nodes.get(l.key).type;
      if (!groups.has(type)) groups.set(type, new Map());
      const byKey = groups.get(type);
      if (!byKey.has(l.key)) byKey.set(l.key, []);
      byKey.get(l.key).push(l);
    }
    return groups;
  }

  function noFunctionBadge(key) {
    const note = fileCitations(key).length ? "cited at file level only" : "no function cites it";
    return el("span", { class: "badge badge-warn t-FN", title: note }, el("span", { class: "dot t-FN" }),
      `${plural("FN", 0)} 0 · ${note}`);
  }

  // RQ-TRC-033: a function's callers and callees, the first CALLS_SHOWN of each, more on request (DEC-TRC-017).
  function callGroups(index) {
    const byLabel = (a, b) => nodes.get(a.key).label.localeCompare(nodes.get(b.key).label, undefined, { numeric: true });
    return [{ title: "Callers", rel: "called by", list: calls.callers(index) },
      { title: "Callees", rel: "calls", list: calls.callees(index) }]
      .map(({ title, rel, list }) => ({
        badge: el("span", { class: "badge badge-neutral t-FN" }, el("span", { class: "dot t-FN" }), `${title} ${list.length}`),
        section: callGroup(title, rel, list.toSorted(byLabel)),
      }));
  }

  function callGroup(title, rel, list) {
    return listGroup(title, list, (c) => callItem(c, rel));
  }

  // A titled list, the first CALLS_SHOWN items at first, more on request (DEC-TRC-017).
  function listGroup(title, list, item, type = "FN") {
    const items = el("ul", { class: "group-items" });
    const more = el("button", { class: "link-button", type: "button" });
    let shown = 0;
    const next = () => {
      items.append(...list.slice(shown, shown + CALLS_SHOWN).map(item));
      shown = Math.min(list.length, shown + CALLS_SHOWN);
      more.hidden = shown >= list.length;
      more.textContent = `Show ${Math.min(CALLS_SHOWN, list.length - shown)} more of ${list.length - shown}`;
    };
    more.addEventListener("click", next);
    next();
    return el("section", { class: "group" },
      el("div", { class: "group-head" }, el("h3", { class: "group-title" }, el("span", { class: `dot t-${type}` }), title),
        el("span", { class: "group-count", text: list.length })),
      items, more);
  }

  // ---- a box's panel (TASK-TRC-026: RQ-TRC-047, RQ-TRC-016; DEC-TRC-022) ---------------------------------------
  // Its kind and name, the box around it, its inner boxes and own functions, its calls in and out by box at its own
  // level, and the requirements its functions cite.
  function renderBoxDetail(panel, box) {
    const members = boxes.membersOf(box.key);
    const inner = boxes.innerOf(box.key).sort(byKeyLabel);
    const own = members.filter((i) => (boxes.scopeOf(i) ?? GLOBAL_KEY) === box.key).map((i) => fnKeys[i]);
    const cited = unique(members.flatMap((i) => links.get(fnKeys[i]).filter((l) => l.kind === "code" && l.dir === "out"
      && nodes.get(l.key).type === "RQ").map((l) => l.key))).sort(byKeyLabel);
    const { callers, callees } = boxCalls(box, members);
    const keyItem = (key) => el("li", { class: "link-item" }, idButton(key));
    const head = el("div", { class: "detail-head t-FN" },
      el("div", { class: "detail-kind" }, el("span", { class: "dot t-FN" }), BOX_NAME[box.box]),
      el("h2", { class: "detail-id", text: box.label }),
      el("div", { class: "detail-actions" },
        el("button", { class: "button button-primary", type: "button", text: "Show in graph",
          title: "Open the graph on this box, its functions and their links", on: { click: () => showView("graph") } }),
        el("button", { class: "button", type: "button", text: "Copy name",
          title: "Copy the box's name to the clipboard", on: { click: () => copy(box.label) } })));
    const badge = (type, text) => el("span", { class: `badge badge-neutral t-${type}` }, el("span", { class: `dot t-${type}` }), text);
    const summary = el("div", { class: "detail-summary" }, badge("FN", `Inner scopes ${inner.length}`),
      badge("FN", `${plural("FN", members.length)} ${members.length}`), badge("RQ", `${plural("RQ", cited.length)} ${cited.length}`),
      badge("FN", `Callers ${callers.length}`), badge("FN", `Callees ${callees.length}`));
    panel.append(detailBand("FN", head, summary), el("div", { class: "detail-body" }, ...[
      box.parent ? listGroup("Enclosing scope", [box.parent], keyItem) : null,              // RQ-TRC-048
      inner.length ? listGroup("Inner scopes", inner, keyItem) : null,
      listGroup(plural("FN", own.length), own.sort(byKeyLabel), keyItem),
      listGroup("Callers by scope", callers, boxCallItem("called by")),
      listGroup("Callees by scope", callees, boxCallItem("calls")),
      listGroup(plural("RQ", cited.length), cited, keyItem, "RQ")].filter(Boolean)));
  }

  // The calls into and out of a box's functions, by the box of the other end at the box's own level, with their
  // call-site counts; calls among its own functions are left out.
  function boxCalls(box, members) {
    const level = box.box === CLASS_KIND ? DETAIL.class : DETAIL.namespace;
    const inside = new Set(members);
    const tally = (list) => {
      const counts = new Map();
      for (const c of list) {
        const other = calls.index.get(c.key);
        if (inside.has(other)) continue;
        const key = boxes.of(other, level);
        counts.set(key, (counts.get(key) || 0) + c.lines.length);
      }
      return [...counts].map(([key, count]) => ({ key, count })).sort((a, b) => byKeyLabel(a.key, b.key));
    };
    return { callers: tally(members.flatMap((i) => calls.callers(i))), callees: tally(members.flatMap((i) => calls.callees(i))) };
  }

  function boxCallItem(rel) {
    return ({ key, count }) => el("li", { class: "link-item" }, idButton(key),
      el("span", { class: "link-rel", text: `${rel} · ${count} ${count === 1 ? "call site" : "call sites"}` }));
  }

  function callItem(c, rel) {
    const sites = c.lines.map((line) => `L${line}`).join(" · ");
    return el("li", { class: "link-item" }, idButton(c.key),
      el("span", { class: "link-rel", title: `call sites in the caller: ${sites}` }, `${rel} · ${sites} `,
        c.ambiguous ? el("span", { class: "badge badge-warn", text: "ambiguous",
          title: "the name matches several definitions; the analysis cannot tell which one is called" }) : null));
  }

  function linkGroup(type, byKey) {
    const items = [...byKey.entries()].sort((a, b) => nodes.get(a[0]).label.localeCompare(nodes.get(b[0]).label, undefined, { numeric: true }));
    return el("section", { class: "group" },
      el("div", { class: "group-head" }, el("h3", { class: "group-title" }, el("span", { class: `dot t-${type}` }), plural(type, items.length)),
        el("span", { class: "group-count", text: items.length })),
      el("ul", { class: "group-items" }, ...items.map(([key, list]) => {
        const n = nodes.get(key);
        const rel = unique(list.map((l) => RELATION[`${l.kind}:${l.dir}`])).join(", ");
        const lines = list.flatMap((l) => l.lines);
        return el("li", { class: "link-item" }, idButton(key), el("span", { class: "link-rel", text: rel }),
          n.title ? el("span", { class: "link-title", text: n.title }) : null,
          lines.length ? evidence(lines) : null);
      })));
  }

  function evidence(lines) {
    const box = el("div", { class: "evidence" });
    const draw = (all) => {
      clear(box).append(...(all ? lines : lines.slice(0, EVIDENCE_SHOWN)).map(([no, text]) => el("div", { class: "evidence-line" },
        el("span", { class: "evidence-no", text: `L${no}` }), el("span", { class: "evidence-text", text }))));
      if (!all && lines.length > EVIDENCE_SHOWN) {
        box.append(el("button", { class: "link-button", type: "button", text: `${lines.length - EVIDENCE_SHOWN} more lines`,
          on: { click: () => draw(true) } }));
      }
    };
    draw(false);
    return box;
  }

  function copy(text) {
    navigator.clipboard?.writeText(text).catch(() => undefined);
  }

  // ---- selection, views, history ------------------------------------------------------------------------------
  // An element, file or function of the model, or a box of the call graph (DEC-TRC-022).
  const isKey = (key) => nodes.has(key) || Boolean(boxes.get(key));

  function hashKey() {
    const raw = decodeURIComponent(location.hash.slice(1));
    return isKey(raw) ? raw : null;
  }

  function select(key, options) {
    if (!isKey(key)) return;
    const fromHistory = options?.fromHistory;
    state.selected = key;
    renderDetail();
    for (const tr of $("matrix-table").querySelectorAll("tbody tr")) tr.classList.toggle("selected", tr.dataset.key === key);
    graph.select(key);
    const hash = `#${encodeURIComponent(key)}`;
    if (!fromHistory && location.hash !== hash) history.pushState({ key }, "", hash);
  }

  function showView(view) {
    state.view = view;
    for (const tab of document.querySelectorAll(".tab")) tab.setAttribute("aria-selected", String(tab.dataset.view === view));
    for (const section of document.querySelectorAll(".view")) section.hidden = section.id !== `view-${view}`;
    if (view === "graph") graph.show();
  }

  document.querySelector(".tabs").addEventListener("click", (event) => {
    const tab = event.target.closest(".tab");
    if (tab) showView(tab.dataset.view);
  });

  function followHash() {
    const key = hashKey();
    if (key) select(key, { fromHistory: true });
  }
  window.addEventListener("popstate", followHash);
  window.addEventListener("hashchange", followHash);

  // ---- resizable panels (TASK-TRC-008: RQ-TRC-025; DEC-TRC-012) ------------------------------------------------
  const PANELS_KEY = "agnos-trace-panels";
  const PANEL = {
    left: { bar: "split-left", property: "--sidebar-size", data: "sidebarWidth", base: "--c-sidebar-width",
      min: "--c-sidebar-min-width", max: "--c-sidebar-max-width", grow: "ArrowRight" },
    right: { bar: "split-right", property: "--detail-size", data: "detailWidth", base: "--c-detail-width",
      min: "--c-detail-min-width", max: "--c-detail-max-width", grow: "ArrowLeft" },
  };

  function setupPanels() {
    const app = $("app");
    const css = (name) => Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
    const widths = {};
    const current = (side) => widths[side] ?? css(PANEL[side].base);

    // A panel stays between its own limits, and never takes the room the main area needs.
    function clamp(side, value) {
      const other = side === "left" ? "right" : "left";
      const room = app.clientWidth - current(other) - 2 * css("--c-splitter-width") - css("--c-main-min-width");
      return Math.round(Math.max(css(PANEL[side].min), Math.min(value, css(PANEL[side].max), room)));
    }

    function apply() {
      for (const side of Object.keys(PANEL)) {
        const p = PANEL[side];
        if (widths[side] === undefined) app.style.removeProperty(p.property);
        else app.style.setProperty(p.property, `${widths[side]}px`);
        const width = String(Math.round(current(side)));
        app.dataset[p.data] = width;
        $(p.bar).setAttribute("aria-valuenow", width);
      }
      graph.resize();
    }

    function save() {
      try { localStorage.setItem(PANELS_KEY, JSON.stringify(widths)); } catch (error) { /* storage unavailable: the widths last this visit */ }
    }

    function set(side, value) {
      widths[side] = clamp(side, value);
      apply();
      save();
    }

    function drag(side, bar, event) {
      event.preventDefault();
      bar.setPointerCapture(event.pointerId);
      bar.classList.add("dragging");
      app.classList.add("resizing");
      const box = app.getBoundingClientRect();
      const move = (e) => set(side, side === "left" ? e.clientX - box.left : box.right - e.clientX);
      const end = () => {
        bar.removeEventListener("pointermove", move);
        bar.removeEventListener("pointerup", end);
        bar.removeEventListener("pointercancel", end);
        bar.classList.remove("dragging");
        app.classList.remove("resizing");
      };
      bar.addEventListener("pointermove", move);
      bar.addEventListener("pointerup", end);
      bar.addEventListener("pointercancel", end);
    }

    try { Object.assign(widths, JSON.parse(localStorage.getItem(PANELS_KEY) || "{}")); } catch (error) { /* no storage */ }
    for (const side of Object.keys(PANEL)) {
      const p = PANEL[side];
      const bar = $(p.bar);
      bar.setAttribute("aria-valuemin", String(css(p.min)));
      bar.setAttribute("aria-valuemax", String(css(p.max)));
      bar.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        const step = css("--c-splitter-step");
        set(side, current(side) + (event.key === p.grow ? step : -step));
      });
      bar.addEventListener("dblclick", () => { delete widths[side]; apply(); save(); });
      bar.addEventListener("pointerdown", (event) => drag(side, bar, event));
      if (widths[side] !== undefined) widths[side] = clamp(side, widths[side]);
    }
    apply();
  }

  // ---- theme --------------------------------------------------------------------------------------------------
  const THEME_KEY = "agnos-trace-theme";
  function effectiveTheme() {
    const set = document.documentElement.dataset.theme;
    if (set) return set;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem(THEME_KEY, theme); } catch (error) { /* storage unavailable: the choice lasts this visit */ }
    graph.restyle();
  }
  try { const saved = localStorage.getItem(THEME_KEY); if (saved) document.documentElement.dataset.theme = saved; } catch (error) { /* no storage */ }
  $("theme-toggle").addEventListener("click", () => applyTheme(effectiveTheme() === "dark" ? "light" : "dark"));
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => graph.restyle());

  // ---- start --------------------------------------------------------------------------------------------------
  window.agnosTrace = { nodes, links, calls, csvText, EDGE_LOOK, state, select, showView, graph, el, $, clear, isVisible, TYPE_NAME, NODE_TYPES,
    FILE_PREFIX };
  renderHeader();
  renderFilters();
  renderOverview();
  renderMatrix();
  renderGaps();
  renderDetail();
  setupPanels();
  const initial = hashKey();
  if (initial) { select(initial, { fromHistory: true }); showView("graph"); } else showView("overview");
  const readyMs = Math.round(performance.now());   // since the navigation started, the page's parsing included
  Object.assign(document.documentElement.dataset, { ready: "true", readyMs: String(readyMs) });   // RQ-TRC-037
  console.info(`agnos-trace: interactive ${readyMs} ms after opening, script ${Math.round(readyMs - STARTED)} ms`);
})();
