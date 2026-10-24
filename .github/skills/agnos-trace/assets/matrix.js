/* agnos-trace page script (FTR-TRC-001; ADR-TRC-003: DEC-TRC-005, DEC-TRC-007, DEC-TRC-012; ADR-TRC-002: DEC-TRC-010).
   Views (TASK-TRC-005): overview, search, filters, matrix, quality, detail panel, deep links.
   Panels (TASK-TRC-008): splitter bars, see the "resizable panels" section.
   Graph (TASK-TRC-006): see the "graph" section — the selection's neighbourhood as a traceability flow, columns by type.
   Call graph (FTR-TRC-002, ADR-TRC-004; TASK-TRC-012): functions as nodes, calls in typed arrays, see "call graph".
   Every text taken from the data is inserted with textContent, never as HTML (RQ-TRC-022); every visual value comes
   from the design tokens' custom properties (RQ-TRC-018). */
"use strict";

(function () {

  // RQ-TRC-067: a literal written more than once is a named constant.
  const CSS_VAR_C_GRAPH_ARROW_SCALE = "--c-graph-arrow-scale";
  const CSS_VAR_C_GRAPH_BOX_FILL_OPACITY = "--c-graph-box-fill-opacity";
  const CSS_VAR_C_GRAPH_BOX_LABEL_GAP = "--c-graph-box-label-gap";
  const CSS_VAR_C_GRAPH_BOX_LABEL_SIZE = "--c-graph-box-label-size";
  const CSS_VAR_C_GRAPH_BOX_PADDING = "--c-graph-box-padding";
  const CSS_VAR_C_GRAPH_DIM = "--c-graph-dim";
  const CSS_VAR_C_GRAPH_LABEL_SIZE = "--c-graph-label-size";
  const CSS_VAR_C_GRAPH_NODE_FILL = "--c-graph-node-fill";
  const CSS_VAR_C_GRAPH_NODE_HEIGHT = "--c-graph-node-height";
  const CSS_VAR_C_GRAPH_NODE_SIZE_FILE = "--c-graph-node-size-file";
  const CSS_VAR_C_GRAPH_ROW_GAP = "--c-graph-row-gap";
  const CSS_VAR_C_GRAPH_SELECTED_BORDER = "--c-graph-selected-border";
  const CSS_VAR_C_GRAPH_SELECTED_BORDER_WIDTH = "--c-graph-selected-border-width";
  const CSS_VAR_S_FONT_MONO = "--s-font-mono";
  const CSS_VAR_S_SPACE_XL = "--s-space-xl";
  const CSS_VAR_S_WEIGHT_STRONG = "--s-weight-strong";
  const VALUE_ITEM = ".item";
  const CLASS_KPI_LABEL = "kpi-label";
  const CLASS_KPI_VALUE = "kpi-value";
  const CLASS_CHIP_COUNT = "chip-count";
  const CLASS_QUALITY_SHORTCUT = "quality-shortcut";
  const SVG_RECT = "rect";
  const TEXT_COMMITS = "commits";
  const TEXT_KEPT_SPACED = " kept by the filters";
  const KEY_ARROWLEFT = "ArrowLeft";
  const KEY_ARROWRIGHT = "ArrowRight";
  const TYPE_FILE = "FILE";
  const VALUE_IMPLEMENTATION_DETAIL = "Implementation detail";
  const TYPE_UNDEFINED = "UNDEFINED";
  const KIND_UNDEFINED = "undefined";      // an ID cited but not in the index
  const VALUE_ARIA_EXPANDED = "aria-expanded";
  const VALUE_ARIA_LABEL = "aria-label";
  const VALUE_ARIA_PRESSED = "aria-pressed";
  const VALUE_ARIA_SELECTED = "aria-selected";
  const TAG_ARTICLE = "article";
  const STYLE_BACKGROUND_COLOR = "background-color";
  const STYLE_BACKGROUND_FILL = "background-fill";
  const STYLE_BACKGROUND_OPACITY = "background-opacity";
  const STYLE_BORDER_COLOR = "border-color";
  const STYLE_BORDER_STYLE = "border-style";
  const STYLE_BORDER_WIDTH = "border-width";
  const VALUE_BOXKEY = "boxKey";
  const VALUE_BUTT = "butt";
  const TAG_BUTTON = "button";
  const VALUE_CALL_SITE = "call site";
  const VALUE_CALL_SITES = "call sites";
  const VALUE_CALLS = "calls";
  const VALUE_CENTER = "center";
  const EVENT_CHANGE = "change";
  const VALUE_CHECKBOX = "checkbox";
  const EVENT_CLICK = "click";
  const LINK_KIND_CODE = "code";
  const VALUE_CONTAINS = "contains";
  const VALUE_COVERAGE_FILTER = "coverage-filter";
  const VALUE_COVERAGE_ITEM = "coverage-item";
  const VALUE_COVERAGE_ITEM_LABEL = "coverage-item-label";
  const VALUE_COVERAGE_ITEM_VALUE = "coverage-item-value";
  const STYLE_CURVE_STYLE = "curve-style";
  const VALUE_DASHED = "dashed";
  const CY_DATA_LABEL = "data(label)";
  const CY_DATA_WIDTH = "data(width)";
  const VALUE_DEPTH = "depth";
  const VALUE_DETAIL_LEVEL = "detail-level";
  const VALUE_DROP_TARGET = "drop-target";
  const VALUE_EDGE = "edge";
  const VALUE_EDGES = "edges";
  const VALUE_ELEMENT = "element";
  const VALUE_FADED = "faded";
  const STYLE_FONT_FAMILY = "font-family";
  const STYLE_FONT_SIZE = "font-size";
  const STYLE_FONT_WEIGHT = "font-weight";
  const VALUE_GRAPH = "graph";
  const VALUE_GRAPH_SCROLL = "graph-scroll";
  const TAG_HEADER = "header";
  const VALUE_HOVER = "hover";
  const DOM_INPUT = "input";
  const VALUE_ITEM_2 = "item";
  const EVENT_KEYDOWN = "keydown";
  const EVENT_FOCUS = "focus";
  const EVENT_BLUR = "blur";
  const VALUE_KPI_SUB = "kpi-sub";
  const TAG_LABEL = "label";
  const VALUE_LEGEND_ITEM = "legend-item";
  const VALUE_LINE = "line";
  const STYLE_LINE_COLOR = "line-color";
  const VALUE_MATRIX = "matrix";
  const VALUE_MATRIX_TABLE = "matrix-table";
  const EVENT_MOUSEOUT = "mouseout";
  const EVENT_MOUSEOVER = "mouseover";
  const VALUE_NEAR = "near";
  const VALUE_NODE_ITEM = "node.item";
  const VALUE_NODES = "nodes";
  const VALUE_NONE = "none";
  const VALUE_OVERVIEW = "overview";
  const EVENT_POINTERCANCEL = "pointercancel";
  const EVENT_POINTERMOVE = "pointermove";
  const EVENT_POINTERUP = "pointerup";
  const VALUE_ROUND = "round";
  const VALUE_ROUND_RECTANGLE = "round-rectangle";
  const VALUE_SEARCH_EMPTY = "search-empty";
  const VALUE_SELECTED = "selected";
  const VALUE_SHOW_ENCLOSING = "show-enclosing";
  const VALUE_SHOW_FILES = "show-files";
  const VALUE_SHOW_FUNCTIONS = "show-functions";
  const VALUE_SHOW_HIERARCHY = "show-hierarchy";
  const VALUE_SOLID = "solid";
  const TAG_SPAN = "span";
  const STYLE_TARGET_ARROW_SHAPE = "target-arrow-shape";
  const TAG_TBODY = "tbody";
  const STYLE_TEXT_HALIGN = "text-halign";
  const STYLE_TEXT_VALIGN = "text-valign";
  const TAG_THEAD = "thead";
  const VALUE_TOGGLE = "toggle";
  const VALUE_TRI_TABLE = "tri-table";
  const VALUE_TRUE = "true";
  const VALUE_WIDTH = "width";
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
  const COVERAGE = {
    covered: ["Covered", "a source file cites the requirement"],
    indirect: ["Indirect", "a source file cites a decision, task or ADR linked to it"],
    uncovered: ["Uncovered", "no source file cites it, directly or indirectly"],
  };
  // RQ-TRC-057, ADR-TRC-008: a check's badge by its risk; its title, rule and findings come from the data's `quality` block.
  const CHECK_BADGE = { critical: "error", high: "warn", medium: "warn", low: "warn", informational: "neutral" };
  const INFORMATIONAL = "informational";
  const ITEMS_FILE = "file";
  const ITEMS_FUNCTION = "function";
  const FUNCTIONS_CHECK = "functions-traced";
  const SCORE_MAX = 10;
  const SCORE_DECIMALS = 1;
  const FIX_FIRST_SHOWN = 3;
  const SEARCH_LIMIT = 60;
  const CELL_LIMIT = 3;
  const RANK_TITLE = 3;                 // a search match: ID equal 0, ID start 1, ID part 2, title part 3, none -1
  const RANK_NONE = -1;
  const RESULT_NODE = 3;                // a search result is [rank, type order, label, node]
  const FINDINGS_SHOWN = 60;
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

  // ---- the page's rich tooltip (TASK-HST-009: RQ-HST-016; DEC-HST-007) --------------------------------------------
  // One card for every piece of business information: a bold first line, its details below, beside its target and kept
  // inside the window; shown on hover after a delay token and at once on keyboard focus. The browser's title is left to
  // what a control does.
  const TIP_ID = "tip";
  const TIP_HEAD = "tip-head";
  const TIP_LINE = "tip-line";
  let richTipTimer = null;

  // content: { head, type (a dot of that element type before the head), lines, mono (the lines that are code) }
  function showRichTip(target, content) {
    clearTimeout(richTipTimer);
    const tip = $(TIP_ID);
    const head = el("div", { class: TIP_HEAD }, content.type ? el("span", { class: `dot t-${content.type}` }) : null, content.head);
    clear(tip).append(head, ...(content.lines || []).filter((line) => line !== null && line !== undefined && line !== "")
      .map((line, i) => el("div", { class: `${TIP_LINE}${(content.mono || []).includes(i) ? " tip-mono" : ""}`, text: line })));
    const box = target.getBoundingClientRect ? target.getBoundingClientRect() : target;
    tip.hidden = false;
    const size = tip.getBoundingClientRect();
    const left = box.right + size.width > window.innerWidth ? box.left - size.width : box.right;
    const top = box.bottom + size.height > window.innerHeight ? box.top - size.height : box.bottom;
    tip.style.left = `${Math.max(0, left)}px`;
    tip.style.top = `${Math.max(0, top)}px`;
  }

  function hideRichTip() {
    clearTimeout(richTipTimer);
    $(TIP_ID).hidden = true;
  }

  function scheduleRichTip(target, contentOf, delayToken) {
    clearTimeout(richTipTimer);
    if (!delayToken) { showRichTip(target, contentOf()); return; }           // no delay token: at once, as the charts
    const delay = Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue(delayToken));
    richTipTimer = setTimeout(() => showRichTip(target, contentOf()), delay);
  }

  // A node that raises a rich tooltip: never a browser title of its own (RQ-HST-016).
  function richTip(node, contentOf, delayToken) {
    node.removeAttribute("title");
    node.dataset.richTip = VALUE_TRUE;
    node.addEventListener(EVENT_MOUSEOVER, () => scheduleRichTip(node, contentOf, delayToken));
    node.addEventListener(EVENT_MOUSEOUT, hideRichTip);
    node.addEventListener(EVENT_FOCUS, () => showRichTip(node, contentOf()));
    node.addEventListener(EVENT_BLUR, hideRichTip);
    return node;
  }

  // ---- model --------------------------------------------------------------------------------------------------
  const nodes = new Map();
  const links = new Map();
  for (const e of DATA.elements) {
    nodes.set(e.id, {
      key: e.id, label: e.id, type: e.kind === KIND_UNDEFINED ? TYPE_UNDEFINED : e.type, elementType: e.type,
      kind: e.kind, title: e.title, tri: e.tri, status: e.status, doc: e.doc, first: e.first, last: e.last,
    });
  }
  for (const f of DATA.files) {
    const key = FILE_PREFIX + f.path;
    nodes.set(key, { key, label: f.path, type: TYPE_FILE, kind: "file", title: "", tri: "", path: f.path, ids: f.ids });
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
      const from = kind === LINK_KIND_CODE ? FILE_PREFIX + source : source;
      if (nodes.has(from) && nodes.has(target)) addLink(from, target, kind, lines);
    }
  }

  function indexSearch() {              // the search's index, made once (DEC-TRC-017)
    for (const n of nodes.values()) {
      n.find = n.label.toLowerCase();
      n.findTitle = (n.title || "").toLowerCase();
    }
  }
  const typeOrder = (type) => NODE_TYPES.indexOf(type);
  const requirements = DATA.elements.filter((e) => e.kind === VALUE_ELEMENT && e.type === "RQ").map((e) => nodes.get(e.id));
  const counts = Object.fromEntries(NODE_TYPES.map((t) => [t, 0]));
  for (const n of nodes.values()) counts[n.type] += 1;
  const trigrams = [...new Set(DATA.elements.filter((e) => e.kind === VALUE_ELEMENT).map((e) => e.tri))]
    .sort((a, b) => a.localeCompare(b));
  const CHECKS = DATA.quality.checks;
  const checkBadgeClass = (check) => "badge badge-" + (check.findings.length ? CHECK_BADGE[check.risk] : "ok");
  // A finding is an element's ID, a file's path or the index of a function of the call graph (DEC-TRC-033).
  const findingKey = (check, item) => {
    if (check.items === ITEMS_FILE) return FILE_PREFIX + item;
    return check.items === ITEMS_FUNCTION ? fnKeys[item] : item;
  };
  const findingKeys = (check) => check.findings.map((item) => findingKey(check, item));

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
        proofs.set(fileKey, new Map(links.get(fileKey).filter((l) => l.kind === LINK_KIND_CODE && l.dir === "out")
          .map((l) => [l.key, l.lines])));
      }
      return proofs.get(fileKey).get(id) || [];
    };
    for (const [index, id, lineNumbers] of CALL_GRAPH?.ids || []) {
      const key = fnKeys[index];
      if (!nodes.has(id)) continue;
      const wanted = new Set(lineNumbers);
      addLink(key, id, LINK_KIND_CODE, proofsOf(nodes.get(key).file, id).filter(([no]) => wanted.has(no)));
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
    selected: null, view: VALUE_OVERVIEW, search: "", coverage: "all", sort: { column: "id", dir: 1 },
    types: new Set(NODE_TYPES.filter((t) => t !== "FN")),   // functions off at load (RQ-TRC-034, DEC-TRC-017)
    tris: new Set(trigrams), openChecks: new Set(), moreFindings: new Set(),
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
    return clip(n.type === TYPE_FILE ? n.label.split("/").pop() : n.label);
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
        edges.push({ group: VALUE_EDGES, data: { id: `${key}>${other}>calls`, source: key, target: other, kind: VALUE_CALLS,
          ambiguous: ambiguous === 1, curve: 0 } });
      }
    });
    return edges;
  }

  function createGraph() {
    const container = $("cy");
    const tip = el("div", { class: "graph-tip", role: "tooltip", hidden: true });
    $(VALUE_GRAPH_SCROLL).after(tip);
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
    const showFiles = () => $(VALUE_SHOW_FILES).checked;
    const showHierarchy = () => $(VALUE_SHOW_HIERARCHY).checked;
    const columnOf = (type) => COLUMNS.findIndex((c) => c.includes(type));

    function style() {
      const fontSize = num(CSS_VAR_C_GRAPH_LABEL_SIZE);
      const fill = prop(CSS_VAR_C_GRAPH_NODE_FILL);
      const typeStyles = NODE_TYPES.map((t) => {
        const colour = prop(`--s-type-${t.toLowerCase()}`);
        return { selector: `node.item[type = "${t}"]`, style: { [STYLE_BORDER_COLOR]: colour,
          "background-gradient-stop-colors": [colour, colour, fill, fill],
          "background-gradient-stop-positions": [0, STRIPE_PERCENT, STRIPE_PERCENT, PERCENT] } };
      });
      return [
        { selector: VALUE_NODE_ITEM, style: {
          shape: VALUE_ROUND_RECTANGLE, label: CY_DATA_LABEL, width: CY_DATA_WIDTH, height: num(CSS_VAR_C_GRAPH_NODE_HEIGHT),
          [STYLE_BACKGROUND_COLOR]: prop(CSS_VAR_C_GRAPH_NODE_FILL), [STYLE_BACKGROUND_FILL]: "linear-gradient",
          "background-gradient-direction": "to-right", [STYLE_BORDER_WIDTH]: num("--s-stroke-hairline"),
          color: prop("--c-graph-node-text"), [STYLE_FONT_FAMILY]: prop(CSS_VAR_S_FONT_MONO), [STYLE_FONT_SIZE]: fontSize,
          [STYLE_FONT_WEIGHT]: prop("--s-weight-medium"), [STYLE_TEXT_VALIGN]: VALUE_CENTER, [STYLE_TEXT_HALIGN]: VALUE_CENTER,
          "min-zoomed-font-size": num("--s-space-xs") } },
        ...typeStyles,
        { selector: 'node.item[type = "UNDEFINED"]', style: { [STYLE_BORDER_STYLE]: VALUE_DASHED } },
        // RQ-TRC-047, DEC-TRC-020: a box in the colour of its kind, as a pill or as the frame around its contents.
        ...BOX_KINDS.map((kind) => ({ selector: `node.box-${kind}`, style: { [STYLE_BORDER_COLOR]: prop(`--c-graph-box-${kind}`) } })),
        { selector: "node:parent", style: {
          shape: VALUE_ROUND_RECTANGLE, [STYLE_BACKGROUND_FILL]: VALUE_SOLID, [STYLE_BACKGROUND_OPACITY]: num(CSS_VAR_C_GRAPH_BOX_FILL_OPACITY),
          [STYLE_BORDER_WIDTH]: num("--c-graph-box-border-width"), padding: num(CSS_VAR_C_GRAPH_BOX_PADDING), label: CY_DATA_LABEL,
          [STYLE_FONT_FAMILY]: prop(CSS_VAR_S_FONT_MONO), [STYLE_FONT_SIZE]: num(CSS_VAR_C_GRAPH_BOX_LABEL_SIZE),
          [STYLE_FONT_WEIGHT]: prop(CSS_VAR_S_WEIGHT_STRONG), [STYLE_TEXT_VALIGN]: "top", [STYLE_TEXT_HALIGN]: VALUE_CENTER,
          "text-margin-y": -num(CSS_VAR_C_GRAPH_BOX_LABEL_GAP) } },
        ...BOX_KINDS.map((kind) => ({ selector: `node:parent.box-${kind}`,
          style: { [STYLE_BACKGROUND_COLOR]: prop(`--c-graph-box-${kind}`), color: prop(`--c-graph-box-${kind}`) } })),
        { selector: `node:parent.box-${NAMESPACE_KIND}`, style: { [STYLE_BORDER_STYLE]: VALUE_DASHED } },
        // Its own frame, label and fill only: an opacity on a compound node would fade its pills a second time.
        { selector: "node:parent.faint", style: { "border-opacity": num(CSS_VAR_C_GRAPH_DIM), "text-opacity": num(CSS_VAR_C_GRAPH_DIM),
          [STYLE_BACKGROUND_OPACITY]: num(CSS_VAR_C_GRAPH_BOX_FILL_OPACITY) * num(CSS_VAR_C_GRAPH_DIM) } },
        { selector: "node:parent.selected", style: { [STYLE_BORDER_WIDTH]: num(CSS_VAR_C_GRAPH_SELECTED_BORDER_WIDTH),
          [STYLE_BORDER_COLOR]: prop(CSS_VAR_C_GRAPH_SELECTED_BORDER) } },
        { selector: "node.header", style: {
          shape: "rectangle", label: CY_DATA_LABEL, width: CY_DATA_WIDTH, height: num(CSS_VAR_C_GRAPH_NODE_HEIGHT),
          [STYLE_BACKGROUND_OPACITY]: 0, [STYLE_BORDER_WIDTH]: 0, color: prop("--c-graph-header-color"),
          [STYLE_FONT_FAMILY]: prop("--s-font-sans"), [STYLE_FONT_SIZE]: fontSize, [STYLE_FONT_WEIGHT]: prop(CSS_VAR_S_WEIGHT_STRONG),
          "text-transform": "uppercase", [STYLE_TEXT_VALIGN]: VALUE_CENTER, [STYLE_TEXT_HALIGN]: VALUE_CENTER, events: "no" } },
        ...NODE_TYPES.map((t) => ({ selector: `node.dot[type = "${t}"]`,
          style: { [STYLE_BACKGROUND_COLOR]: prop(`--s-type-${t.toLowerCase()}`) } })),
        { selector: "node.dot", style: { label: "", width: num(CSS_VAR_C_GRAPH_NODE_SIZE_FILE), height: num(CSS_VAR_C_GRAPH_NODE_SIZE_FILE),
          shape: "ellipse", [STYLE_BACKGROUND_FILL]: VALUE_SOLID, [STYLE_BORDER_WIDTH]: 0 } },
        { selector: VALUE_EDGE, style: {
          width: num("--c-graph-edge-width"), [STYLE_LINE_COLOR]: prop("--c-graph-edge"), [STYLE_CURVE_STYLE]: "unbundled-bezier",
          "control-point-distances": "data(curve)", "control-point-weights": BOW_WEIGHT, opacity: num("--s-opacity-muted") } },
        ...Object.entries(EDGE_LOOK).map(([kind, look]) => ({ selector: EDGE_SELECTOR[kind] || `edge[kind = "${kind}"]`,
          style: edgeLook(look) })),
        // Calls: straight, the cheapest edge that still carries an arrow (DEC-TRC-017).
        { selector: 'edge[kind = "calls"]', style: { [STYLE_CURVE_STYLE]: "straight" } },
        { selector: ".dim", style: { opacity: num(CSS_VAR_C_GRAPH_DIM) } },
        { selector: ".faded", style: { opacity: num("--c-graph-faded") } },
        // A link away from the selection is a faint trace without arrow: only the selection's links stand out.
        { selector: "edge.faded", style: { opacity: num("--c-graph-edge-faded"), [STYLE_TARGET_ARROW_SHAPE]: VALUE_NONE } },
        // A highlighted link keeps its relation's colour (RQ-TRC-044): wider and opaque only.
        { selector: "edge.near", style: { width: num("--c-graph-edge-width-highlight"), opacity: 1 } },
        { selector: "node.item.selected", style: { [STYLE_BORDER_WIDTH]: num(CSS_VAR_C_GRAPH_SELECTED_BORDER_WIDTH),
          [STYLE_BORDER_COLOR]: prop(CSS_VAR_C_GRAPH_SELECTED_BORDER), [STYLE_FONT_WEIGHT]: prop("--s-weight-bold") } },
        { selector: "node.item.hover", style: { [STYLE_BORDER_WIDTH]: num("--c-graph-node-border-width") } },
      ];
    }

    const dashOf = (look) => (look.dash ? prop(look.dash).split(/\s+/).map(Number) : []);

    function edgeLook(look) {
      const colour = prop(look.colour);
      return { "line-style": look.dash ? VALUE_DASHED : VALUE_SOLID, ...(look.dash ? { "line-dash-pattern": dashOf(look) } : {}),
        "line-cap": look.dash === EDGE_LOOK.code.dash ? VALUE_ROUND : VALUE_BUTT, [STYLE_LINE_COLOR]: colour,
        [STYLE_TARGET_ARROW_SHAPE]: look.arrow, "target-arrow-color": colour, "arrow-scale": num(CSS_VAR_C_GRAPH_ARROW_SCALE) };
    }

    // The legend's sample of a relation: the same dash, colour, width, opacity and arrow as the graph draws it.
    function edgeSample(look) {
      const ns = "http://www.w3.org/2000/svg";
      const svg = (tag, attributes) => {
        const node = document.createElementNS(ns, tag);
        Object.entries(attributes).forEach(([k, v]) => node.setAttribute(k, String(v)));
        return node;
      };
      const scale = num(CSS_VAR_C_GRAPH_ARROW_SCALE);          // the graph's arrow size, so the sample's matches it
      const middle = SAMPLE_HEIGHT / 2;
      const half = middle * scale;
      const length = SAMPLE_ARROW * scale;
      const tip = SAMPLE_WIDTH;
      const base = SAMPLE_WIDTH - length;
      const head = look.arrow === "vee"
        ? `${base},${middle - half} ${tip},${middle} ${base},${middle + half} ${base + length / 2},${middle}`
        : `${base},${middle - half} ${tip},${middle} ${base},${middle + half}`;
      const line = svg(VALUE_LINE, { x1: 0, y1: middle, x2: base, y2: middle, "stroke-width": num("--c-graph-legend-edge-width"),   // a little thicker than the graph's, to read
        "stroke-dasharray": dashOf(look).join(" ") || VALUE_NONE,
        "stroke-linecap": look.dash === EDGE_LOOK.code.dash ? VALUE_ROUND : VALUE_BUTT });
      line.style.stroke = `var(${look.colour})`;
      const arrow = svg("polygon", { points: head });
      arrow.style.fill = `var(${look.colour})`;
      const box = svg("svg", { class: "legend-edge", viewBox: `0 0 ${SAMPLE_WIDTH} ${SAMPLE_HEIGHT}`, "aria-hidden": VALUE_TRUE });
      box.append(line, arrow);
      return box;
    }

    // RQ-TRC-048: the specification hierarchy only when asked; a file's "defines" goes with the file (nodeAllowed).
    function edgeAllowed(l) { return l.kind !== VALUE_CONTAINS || showHierarchy(); }
    function nodeAllowed(node) { return isVisible(node) && (node.type !== TYPE_FILE || showFiles()); }

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
      const size = Math.abs(to.y - from.y) * BOW_RATIO + num(CSS_VAR_C_GRAPH_NODE_HEIGHT);
      return to.y > from.y ? size : -size;
    }

    function edgesAmong(keys, positions) {
      const kept = new Set(keys);
      const edges = [];
      for (const key of keys) {
        for (const l of links.get(key)) {
          if (l.dir === "out" && kept.has(l.key) && edgeAllowed(l)) {
            const curve = positions ? bow(positions.get(key), positions.get(l.key)) : 0;
            edges.push({ group: VALUE_EDGES, data: { id: `${key}>${l.key}>${l.kind}`, source: key, target: l.key, kind: l.kind,
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
          const curve = kind === VALUE_CALLS ? 0 : bow(positions.get(from), positions.get(to));
          edges.set(id, { group: VALUE_EDGES, data: { id, source: from, target: to, kind, curve } });
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
        if (to(c.key) !== from) mergeCall(add(from, to(c.key), VALUE_CALLS), c, `${key}:`, sites);
      }
    }

    function pillWidth(label) {
      return label.length * num(CSS_VAR_C_GRAPH_LABEL_SIZE) * MONO_CHAR_RATIO + 2 * num("--c-graph-node-padding");
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
      flow.elements.push({ group: VALUE_NODES, classes: TAG_HEADER, data: { id: `header:${c}`, label: header, width: pillWidth(header) },
        position: { x: centre, y: -num("--c-graph-header-gap") } });
      for (const [id, frame] of placed.frames) {
        const box = boxes.get(frame.box);
        const label = frame.parent ? clip(nameIn(box.label, boxName(frame.outer))) : shortLabel(box);
        flow.elements.push({ group: VALUE_NODES, classes: `box box-${box.box}`, data: { id, label, name: box.label, box: box.box,
          boxKey: frame.box, ...(frame.parent ? { parent: frame.parent } : {}) } });
      }
      shown.forEach((key, i) => {
        const n = nodeOf(key);
        const position = placed.points[i];
        const parent = placed.parents[i];
        flow.elements.push({ group: VALUE_NODES, classes: n.box ? `item box box-${n.box}` : VALUE_ITEM_2, data: { id: key, type: n.type,
          label: labels[i], name: n.label, width: pillWidth(labels[i]), level: flow.levels.get(key),
          ...(n.box ? { box: n.box } : {}), ...(parent ? { parent } : {}) }, position });
        flow.positions.set(key, position);
        flow.drawn.push(key);
      });
      if (keys.length > shown.length) {
        const more = `+${keys.length - shown.length} more`;
        flow.elements.push({ group: VALUE_NODES, classes: TAG_HEADER, data: { id: `more:${c}`, label: more, width: pillWidth(more) },
          position: { x: centre, y: placed.bottom } });
      }
      flow.left += Math.max(placed.span, pillWidth(header)) + num("--c-graph-column-gap");
    }

    // Pills in rows, a taller column wrapping into sub-columns.
    function gridRows(shown, left, widest) {
      const rowGap = num(CSS_VAR_C_GRAPH_ROW_GAP);
      const subColumns = Math.ceil(shown.length / MAX_ROWS);
      const rows = Math.ceil(shown.length / subColumns);
      const step = widest + num("--c-graph-sub-gap");
      const points = shown.map((_, i) => ({ x: left + widest / 2 + Math.floor(i / rows) * step, y: (i % rows) * rowGap }));
      return { points, parents: [], frames: new Map(), span: (subColumns - 1) * step + widest, bottom: rows * rowGap };
    }

    // Pills one under the other, each run of one box kept together, room left for the frames that close and open
    // between two pills; a box drawn as a pill of this column is its own frame, the others get one per column.
    function boxedRows(shown, chains, left, widest, c) {
      const rowGap = num(CSS_VAR_C_GRAPH_ROW_GAP);
      const pad = num(CSS_VAR_C_GRAPH_BOX_PADDING);
      const open = pad + num(CSS_VAR_C_GRAPH_BOX_LABEL_SIZE) + num(CSS_VAR_C_GRAPH_BOX_LABEL_GAP);
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
      return { elements: [...keys.map((key) => ({ group: VALUE_NODES, classes: "item dot",
        data: { id: key, type: nodes.get(key).type, label: shortLabel(nodes.get(key)), width: 0 } })), ...edgesAmong(keys)],
      drawn: keys.length, total: keys.length };
    }

    function ensure() {
      if (cy) return cy;
      cy = cytoscape({ container, style: style(), minZoom: num("--c-graph-zoom-min"), maxZoom: num("--c-graph-zoom-max"),
        wheelSensitivity: num("--c-graph-wheel-sensitivity"),            // RQ-TRC-056, DEC-TRC-031
        boxSelectionEnabled: false, autoungrabify: true, hideEdgesOnViewport: Boolean(CALL_GRAPH) });   // DEC-TRC-017
      // A pill selects its element; a frame selects its box (DEC-TRC-022). A tap bubbles to the frames around its
      // target, which keeps the target: one selection.
      cy.on("tap", "node.item, node.box", (event) => select(event.target.data(VALUE_BOXKEY) || event.target.id()));
      cy.on(EVENT_MOUSEOVER, VALUE_NODE_ITEM, (event) => {
        const n = nodeOf(event.target.id());
        event.target.addClass(VALUE_HOVER);
        event.target.connectedEdges().addClass(VALUE_NEAR);
        container.title = n.title ? `${n.label} — ${n.title}` : n.label;
      });
      cy.on(EVENT_MOUSEOUT, VALUE_NODE_ITEM, (event) => {
        event.target.removeClass(VALUE_HOVER);
        if (event.target.id() !== centre) event.target.connectedEdges().removeClass(VALUE_NEAR);
        highlight(centre);
        container.title = "";
      });
      // RQ-TRC-046: a link's tooltip once the pointer rests on it for the token delay.
      cy.on(EVENT_MOUSEOVER, VALUE_EDGE, (event) => {
        clearTimeout(tipTimer);
        const at = event.renderedPosition;
        tipTimer = setTimeout(() => showTip(event.target.id(), at), num("--c-graph-tip-delay"));
      });
      cy.on(EVENT_MOUSEOUT, VALUE_EDGE, hideTip);
      cy.on("viewport", hideTip);
      return cy;
    }

    // The relation of a drawn link, its two ends in their direction, and its proof lines.
    function tipFor(edgeId) {
      const edge = cy.getElementById(edgeId);
      const kind = edge.data("kind");
      const look = kind === VALUE_CALLS && edge.data("ambiguous") ? EDGE_LOOK.ambiguous : EDGE_LOOK[kind];
      const source = edge.data("source");
      const target = edge.data("target");
      const merged = edge.data("count");               // a link merging calls between boxes (DEC-TRC-021)
      let proofs = merged ?? 0;
      if (merged === undefined && kind === VALUE_CALLS) proofs = callSites(source, target);
      else if (merged === undefined && links.has(source)) {
        proofs = links.get(source).filter((l) => l.dir === "out" && l.key === target && l.kind === kind)
          .reduce((sum, l) => sum + l.lines.length, 0);
      }
      let unit = proofs === 1 ? VALUE_LINE : "lines";
      if (merged !== undefined) unit = proofs === 1 ? VALUE_CALL_SITE : VALUE_CALL_SITES;      // RQ-TRC-046: the merged count
      const lines = proofs ? ` · ${proofs} ${unit}` : "";
      return `${look.meaning}: ${nodeOf(source).label} → ${nodeOf(target).label}${lines}`;
    }

    function showTip(edgeId, at) {
      const scroller = $(VALUE_GRAPH_SCROLL);
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
      const frames = key ? cy.nodes().filter((n) => n.data(VALUE_BOXKEY) === key && !n.hasClass(VALUE_ITEM_2)) : cy.collection();
      const own = key ? cy.getElementById(key).union(frames) : cy.collection();
      const centre = own.union(frames.descendants());
      if (centre.empty()) return;
      const near = centre.closedNeighborhood();
      cy.nodes(VALUE_ITEM).not(near).addClass(whole ? VALUE_FADED : "dim");
      // DEC-TRC-020: a frame holding nothing near the selection is faint like its pills, not a veil drawn over them.
      cy.nodes(".box").not(VALUE_ITEM).filter((frame) => frame.descendants(VALUE_ITEM).intersection(near).empty()).addClass("faint");
      cy.edges().not(centre.connectedEdges()).addClass(VALUE_FADED);
      own.addClass(VALUE_SELECTED);
      centre.connectedEdges().addClass(VALUE_NEAR);
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
      const padding = num(CSS_VAR_S_SPACE_XL);
      fitCanvas();
      cy.fit(undefined, padding);
      const floor = num("--c-graph-flow-min-zoom");
      if (!whole && cy.zoom() < floor) {
        const box = cy.elements().boundingBox();
        const scroller = $(VALUE_GRAPH_SCROLL);
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
      container.style.removeProperty(VALUE_WIDTH);
      container.style.removeProperty("height");
      cy.resize();
    }

    const visible = () => state.view === VALUE_GRAPH;

    $(VALUE_DEPTH).addEventListener(EVENT_CLICK, (event) => {
      const b = event.target.closest(TAG_BUTTON);
      if (!b) return;
      depth = Number(b.dataset.depth);
      for (const other of $(VALUE_DEPTH).querySelectorAll(TAG_BUTTON)) other.setAttribute(VALUE_ARIA_PRESSED, String(other === b));
      whole = false;
      dirty = true;
      if (visible()) draw();          // a hidden frame has no size: drawn when the view is shown
    });
    $(VALUE_SHOW_FILES).addEventListener(EVENT_CHANGE, () => draw());
    if (CALL_GRAPH) {       // RQ-TRC-041: the Function type filter, at hand in the graph's own toolbar
      const toggle = el(DOM_INPUT, { type: VALUE_CHECKBOX, id: VALUE_SHOW_FUNCTIONS });
      toggle.addEventListener(EVENT_CHANGE, () => {
        if (toggle.checked) state.types.add("FN"); else state.types.delete("FN");
        renderFilters();
        filtersChanged();
      });
      $(VALUE_SHOW_FILES).closest(TAG_LABEL).after(el(TAG_LABEL, { class: VALUE_TOGGLE, title: IMPLEMENTATION_HINT }, toggle,
        " Implementation"));                                   // RQ-TRC-048
    }
    if (CALL_GRAPH) {       // RQ-TRC-047, RQ-TRC-048, DEC-TRC-022: the implementation detail and the enclosing scopes
      const choice = el("fieldset", { class: "segmented", id: VALUE_DETAIL_LEVEL, [VALUE_ARIA_LABEL]: VALUE_IMPLEMENTATION_DETAIL,
        title: DETAIL_HINT },
      el(TAG_SPAN, { class: "segmented-label", text: VALUE_IMPLEMENTATION_DETAIL }),
      ...DETAIL_CHOICES.map(([level, label, hint]) => el(TAG_BUTTON, { type: TAG_BUTTON, "data-detail": level,
        [VALUE_ARIA_PRESSED]: String(level === detail), title: hint, text: label })));
      choice.addEventListener(EVENT_CLICK, (event) => {
        const b = event.target.closest(TAG_BUTTON);
        if (b) applyDetail(b.dataset.detail);
      });
      const box = el(DOM_INPUT, { type: VALUE_CHECKBOX, id: VALUE_SHOW_ENCLOSING, checked: true });
      box.addEventListener(EVENT_CHANGE, () => applyEnclosing(box.checked));
      $("display").after(choice);                         // Depth, Display, Implementation detail: the reading order
      $(VALUE_SHOW_HIERARCHY).closest(TAG_LABEL).after(el(TAG_LABEL, { class: VALUE_TOGGLE, title: ENCLOSING_HINT }, box,
        " Enclosing scopes"));
      syncImplementationControls();
    }

    // RQ-TRC-048: the detail choice and the enclosing scopes mean something only while the implementation is drawn
    // (whichever of the switch and the Functions type filter turned it off); the scopes' frames need a class level.
    function syncImplementationControls() {
      if (!CALL_GRAPH) return;
      const drawn = state.types.has("FN");
      const choice = $(VALUE_DETAIL_LEVEL);
      choice.disabled = !drawn;
      choice.title = drawn ? DETAIL_HINT : DETAIL_OFF_HINT;
      const box = $(VALUE_SHOW_ENCLOSING);
      box.disabled = !drawn || detail === DETAIL.namespace;
      box.closest(TAG_LABEL).classList.toggle("is-disabled", box.disabled);
    }

    // The level of detail, its button pressed.
    function applyDetail(level) {
      detail = level;
      for (const b of document.querySelectorAll("#detail-level button")) b.setAttribute(VALUE_ARIA_PRESSED, String(b.dataset.detail === level));
      syncImplementationControls();
      dirty = true;
      if (visible()) draw();
    }

    function applyEnclosing(on) {
      enclosing = on;
      if ($(VALUE_SHOW_ENCLOSING)) $(VALUE_SHOW_ENCLOSING).checked = on;
      dirty = true;
      if (visible()) draw();
    }
    $(VALUE_SHOW_HIERARCHY).addEventListener(EVENT_CHANGE, () => draw());
    $("fit").addEventListener(EVENT_CLICK, () => {          // the whole drawing in the frame, any zoom
      if (!cy) return;
      fitCanvas();
      cy.fit(undefined, num(CSS_VAR_S_SPACE_XL));
    });
    $("whole").addEventListener(EVENT_CLICK, () => {
      const count = [...nodes.values()].filter(nodeAllowed).length;
      if (count > WHOLE_GRAPH_WARN && !window.confirm(`Draw all ${count} elements? The layout may take a while.`)) return;
      whole = true;
      draw();
    });

    clear($("legend")).append(...NODE_TYPES.map((t) => el(TAG_SPAN, { class: VALUE_LEGEND_ITEM },
      el(TAG_SPAN, { class: `legend-shape shape-RQ t-${t}` }), TYPE_NAME[t][0])),
    ...Object.values(EDGE_LOOK).map((look) => el(TAG_SPAN, { class: VALUE_LEGEND_ITEM, title: look.meaning },
      edgeSample(look), look.meaning)),
    ...(CALL_GRAPH ? BOX_KINDS.map((kind) => el(TAG_SPAN, { class: VALUE_LEGEND_ITEM, title: BOX_HINT[kind] },   // RQ-TRC-047
      el(TAG_SPAN, { class: `legend-box box-${kind}` }), BOX_NAME[kind])) : []));

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
      zoom() { return cy ? cy.zoom() : 1; },
      wheelSensitivity() { return cy ? cy.renderer().wheelSensitivity : null; },   // RQ-TRC-056: read by the tests
    };
  }

  // ---- header and footer --------------------------------------------------------------------------------------
  function renderHeader() {
    const meta = DATA.meta;
    const item = (label, value, title) => el("div", { class: "meta-item", title: title || value },
      el(TAG_SPAN, { class: "meta-label", text: label }), el(TAG_SPAN, { class: "meta-value", text: value }));
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
      [VALUE_ARIA_LABEL]: `${c.covered} covered, ${c.indirect} indirect, ${c.uncovered} uncovered of ${total}` },
      ...Object.keys(COVERAGE).map((k) => el("div", { class: `stack-part stack-${k}`, title: `${COVERAGE[k][0]}: ${c[k]}`,
        style: { width: `${total ? (PERCENT * c[k]) / total : 0}%` } })));
  }

  function searchPrefix(type) {
    if (type === TYPE_FILE) return FILE_PREFIX;
    if (type === TYPE_UNDEFINED || type === "FN") return "";
    return `${type}-`;
  }

  function renderOverview() {
    const c = coverageCounts(requirements);
    const total = requirements.length;
    const coverageCard = el(TAG_ARTICLE, { class: "card kpi" },
      el(TAG_SPAN, { class: CLASS_KPI_LABEL, text: "Requirements covered by source" }),
      el(TAG_SPAN, { class: CLASS_KPI_VALUE, text: `${pct(c.covered, total)} %` }),
      el(TAG_SPAN, { class: VALUE_KPI_SUB, text: `${c.covered} of ${total} cited by a source file · ${c.indirect} more indirectly` }));
    const typeTiles = el(TAG_ARTICLE, { class: "card kpis-types" },
      ...NODE_TYPES.map((t) => el(TAG_BUTTON, { class: `kpi-type t-${t}`, type: TAG_BUTTON,
        title: `Search ${plural(t, 2).toLowerCase()}`, on: { click: () => searchFor(searchPrefix(t), t) } },
        el(TAG_SPAN, { class: "kpi-type-value", text: counts[t] }), el(TAG_SPAN, { class: "kpi-type-label", text: plural(t, counts[t]) }))));
    clear($("kpis")).append(coverageCard, typeTiles);

    clear($("coverage-chart")).append(stackBar(c, total), el("div", { class: "coverage-legend" },
      ...Object.keys(COVERAGE).map((k) => el(TAG_BUTTON, { class: VALUE_COVERAGE_ITEM, type: TAG_BUTTON, title: COVERAGE[k][1],
        on: { click: () => { setCoverageFilter(k); showView(VALUE_MATRIX); } } },
        el(TAG_SPAN, { class: VALUE_COVERAGE_ITEM_LABEL }, el(TAG_SPAN, { class: `legend-swatch stack-${k}` }), COVERAGE[k][0]),
        el(TAG_SPAN, { class: VALUE_COVERAGE_ITEM_VALUE, text: `${c[k]}` }),
        el(TAG_SPAN, { class: VALUE_KPI_SUB, text: `${pct(c[k], total)} % of ${total}` })))));

    clear($("quality-summary")).append(el("div", { class: "check-rows" }, ...CHECKS.map((check) =>
      el(TAG_BUTTON, { class: "check-row", type: TAG_BUTTON, on: { click: () => openCheck(check.key) } },
        el(TAG_SPAN, { class: "check-row-label", text: check.title }),
        el(TAG_SPAN, { class: "check-row-hint", text: check.rule }),
        el(TAG_SPAN, { class: checkBadgeClass(check), text: check.findings.length })))));

    const rows = trigrams.map((tri) => {
      const list = requirements.filter((r) => r.tri === tri);
      const tc = coverageCounts(list);
      return el("tr", { title: `Show the requirements of ${tri} in the matrix`, on: { click: () => onlyTrigram(tri) } },
        el("td", {}, el(TAG_SPAN, { class: "id", text: tri })),
        el("td", { class: "num", text: list.length }), el("td", { class: "num", text: tc.covered }),
        el("td", { class: "num", text: tc.indirect }), el("td", { class: "num", text: tc.uncovered }),
        el("td", { class: "num", text: list.length ? `${pct(tc.covered, list.length)} %` : "—" }),
        el("td", { class: "bar-cell" }, stackBar(tc, list.length)));
    });
    clear($(VALUE_TRI_TABLE)).append(el("table", { class: "simple" },
      el(TAG_THEAD, {}, el("tr", {}, ...["Trigram", "Requirements", "Covered", "Indirect", "Uncovered", "Coverage", ""].map(
        (h, i) => el("th", { class: i > 0 && i < 6 ? "num" : null, text: h })))),
      el(TAG_TBODY, {}, rows)));
    if (CALL_GRAPH) $(VALUE_TRI_TABLE).closest(".card").before(callGraphCard());
  }

  // RQ-TRC-035: the call graph's counts; the untraced functions are an informational check, not counted among the findings.
  function callGraphCard() {
    const c = CALL_GRAPH.counts;
    const item = (label, value, hint, onClick) => el(onClick ? TAG_BUTTON : "div",
      { class: VALUE_COVERAGE_ITEM, type: onClick ? TAG_BUTTON : null, title: hint, on: onClick ? { click: onClick } : null },
      el(TAG_SPAN, { class: VALUE_COVERAGE_ITEM_LABEL, text: label }), el(TAG_SPAN, { class: VALUE_COVERAGE_ITEM_VALUE, text: value }),
      el(TAG_SPAN, { class: VALUE_KPI_SUB, text: hint }));
    return el(TAG_ARTICLE, { class: "card card-wide" },
      el(TAG_HEADER, { class: "card-header" }, el("h2", { class: "card-title", text: "Call graph" }),
        el(TAG_SPAN, { class: "card-hint", text: `${c.calls} call links between ${c.functions} functions` })),
      el("div", { class: "coverage-legend call-graph-legend" },
        item("Functions", c.functions, "search them by name", () => searchFor("", "FN")),
        item("Call links", c.calls, "one per caller and callee"),
        item("Ambiguous calls", c.ambiguous, "a name matching several definitions"),
        item("External calls", c.external, "a name defined in no scanned file"),
        item("Untraced functions", CHECKS.find((c) => c.key === FUNCTIONS_CHECK).findings.length, "citing no ID · informational", () => openCheck(FUNCTIONS_CHECK))));
  }

  // ---- sidebar ------------------------------------------------------------------------------------------------
  function chip(label, count, pressed, onClick, cls, title) {
    return el(TAG_BUTTON, { class: `chip ${cls || ""}`, type: TAG_BUTTON, [VALUE_ARIA_PRESSED]: String(pressed), title,
      on: { click: onClick } },
    cls ? el(TAG_SPAN, { class: `dot ${cls}` }) : null, label, el(TAG_SPAN, { class: CLASS_CHIP_COUNT, text: count }));
  }

  // RQ-TRC-045: what a filter does, said where it is.
  const typeHint = (t) => (t === "FN"
    ? "Show or hide functions in the graph (the search finds them either way)"
    : `Show or hide ${plural(t, 2).toLowerCase()} in the search and the graph`);

  function renderFilters() {
    if (CALL_GRAPH) $(VALUE_SHOW_FUNCTIONS).checked = state.types.has("FN");
    clear($("type-filters")).append(...NODE_TYPES.map((t) => chip(plural(t, 2), counts[t], state.types.has(t), () => {
      toggle(state.types, t); renderFilters(); filtersChanged();
    }, `t-${t}`, typeHint(t))));
    const triCount = (tri) => DATA.elements.filter((e) => e.kind === VALUE_ELEMENT && e.tri === tri).length;
    clear($("tri-filters")).append(...trigrams.map((tri) => chip(tri, triCount(tri), state.tris.has(tri), () => {
      toggle(state.tris, tri); renderFilters(); filtersChanged();
    }, null, `Show or hide the elements of the ${tri} feature area in the matrix, the search and the graph`)));
    clear($("quality-shortcuts")).append(...CHECKS.map((check) => el("li", {}, el(TAG_BUTTON, { class: CLASS_QUALITY_SHORTCUT, type: TAG_BUTTON,
      title: check.rule, on: { click: () => openCheck(check.key) } }, el(TAG_SPAN, { text: check.title }),
      el(TAG_SPAN, { class: checkBadgeClass(check), text: check.findings.length })))));
  }

  function toggle(set, value) { if (set.has(value)) set.delete(value); else set.add(value); }

  function filtersChanged() { renderMatrix(); graph.refresh(); }

  function onlyTrigram(tri) {
    state.tris = new Set([tri]);
    renderFilters();
    filtersChanged();
    showView(VALUE_MATRIX);
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
    return node.findTitle.includes(q) ? RANK_TITLE : RANK_NONE;
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
    return found.map((f) => f[RESULT_NODE]);
  }

  // RQ-TRC-049, DEC-TRC-024: a result's tooltip, the page's own, beside the list after the quick delay.
  const hideSearchTip = () => hideRichTip();

  // An element as every business tooltip names it: its type, its ID or name, its title, its location, its status.
  function elementTip(n) {
    return { type: n.type, head: n.label, lines: [TYPE_NAME[n.type][0] + (n.status ? ` · ${n.status}` : ""), n.title,
      n.doc ? `${n.doc}:${n.first}-${n.last}` : ""], mono: [2] };
  }

  function showSearchTip(item, n) {
    const row = item.getBoundingClientRect();
    const side = results.getBoundingClientRect();
    showRichTip({ left: side.left, right: side.right, top: row.top, bottom: row.top }, elementTip(n));
  }

  function scheduleSearchTip(item, key) {
    hideSearchTip();
    const row = item.getBoundingClientRect();
    const side = results.getBoundingClientRect();
    scheduleRichTip({ left: side.left, right: side.right, top: row.top, bottom: row.top }, () => elementTip(nodes.get(key)),
      "--c-search-tip-delay");
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
      return el("li", { class: `search-result t-${n.type}`, role: "option", [VALUE_ARIA_SELECTED]: String(i === active),
        on: { mousedown: (event) => { event.preventDefault(); pick(i); },
          mouseenter: (event) => scheduleSearchTip(event.currentTarget, key) } },
        el(TAG_SPAN, { class: "id-link" }, el(TAG_SPAN, { class: `dot t-${n.type}` }), el(TAG_SPAN, { class: "id", text: n.label })),
        n.title ? el(TAG_SPAN, { class: "search-result-title", text: n.title }) : null);
    }) : [el("li", { class: VALUE_SEARCH_EMPTY, text: "No element matches." })]));
    if (found.length > SEARCH_LIMIT) {
      results.append(el("li", { class: VALUE_SEARCH_EMPTY, text: `${found.length - SEARCH_LIMIT} more — refine the search` }));
    }
    results.hidden = false;
    search.setAttribute(VALUE_ARIA_EXPANDED, VALUE_TRUE);
  }

  function closeResults() {
    hideSearchTip();
    results.hidden = true;
    search.setAttribute(VALUE_ARIA_EXPANDED, "false");
  }

  function moveActive(step) {
    if (!resultKeys.length) return;
    active = (active + step + resultKeys.length) % resultKeys.length;
    [...results.children].forEach((li, i) => li.setAttribute(VALUE_ARIA_SELECTED, String(i === active)));
    results.children[active].scrollIntoView({ block: "nearest" });
    scheduleSearchTip(results.children[active], resultKeys[active]);
  }

  function pick(i) {
    if (i < 0 || i >= resultKeys.length) return;
    closeResults();
    select(resultKeys[i]);
    if (state.view === VALUE_OVERVIEW) showView(VALUE_GRAPH);
  }

  function searchFor(text, type) {
    search.value = text;
    search.focus();
    renderResults(type);
  }

  if (CALL_GRAPH) search.placeholder = "Search ID, title, file or function…";
  search.addEventListener(DOM_INPUT, () => renderResults());
  search.addEventListener("focus", () => { if (search.value.trim()) renderResults(); });
  search.addEventListener("blur", closeResults);
  search.addEventListener(EVENT_KEYDOWN, (event) => {
    if (event.key === "ArrowDown") { event.preventDefault(); moveActive(1); }
    else if (event.key === "ArrowUp") { event.preventDefault(); moveActive(-1); }
    else if (event.key === "Enter") { event.preventDefault(); pick(active); }
    else if (event.key === "Escape") { closeResults(); search.blur(); }
  });
  document.addEventListener(EVENT_KEYDOWN, (event) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (event.key === "/" && !typing) { event.preventDefault(); search.focus(); search.select(); }
  });

  // ---- matrix -------------------------------------------------------------------------------------------------
  // The source files citing an element; a function's citation is one of its file's, not one more (DEC-TRC-018).
  const fileCitations = (key) => links.get(key).filter((l) => l.kind === LINK_KIND_CODE && nodes.get(l.key).type === TYPE_FILE);

  function matrixRow(rq) {
    const all = links.get(rq.key);
    const ofTypes = (types, dirs) => all.filter((l) => types.includes(nodes.get(l.key).type) && dirs.includes(l.dir)
      && l.kind !== LINK_KIND_CODE).map((l) => l.key);
    const cited = fileCitations(rq.key);
    const files = cited.map((l) => l.key);
    const lines = cited.reduce((sum, l) => sum + l.lines.length, 0);
    return {
      node: rq, id: rq.key, title: rq.title, status: rq.status,
      feature: all.filter((l) => l.kind === VALUE_CONTAINS && l.dir === "in").map((l) => l.key),
      decisions: unique(ofTypes(["ADR", "DEC"], ["in", "out"])),
      tasks: unique(ofTypes(["TASK", "PLAN"], ["in"])),
      functions: functionsCiting(rq.key),
      files: unique(files), lines, coverage: DATA.coverage[rq.key],
    };
  }

  // RQ-TRC-041: the functions citing an element, in their lines or the comment just above them.
  function functionsCiting(key) {
    return unique(links.get(key).filter((l) => l.kind === LINK_KIND_CODE && l.dir === "in" && nodes.get(l.key).type === "FN")
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
    if (!keys.length) return el(TAG_SPAN, { class: "cell-empty", text: "—" });
    const shown = keys.slice(0, CELL_LIMIT).map((k) => idButton(k, true));
    return el("div", { class: "cell-list" }, shown,
      keys.length > CELL_LIMIT ? el(TAG_SPAN, { class: "cell-more", text: `+${keys.length - CELL_LIMIT}` }) : null);
  }

  function idButton(key, short) {
    const n = nodeOf(key);
    const label = n.type === TYPE_FILE && short ? n.label.split("/").pop() : n.label;
    return el(TAG_BUTTON, { class: `id-link t-${n.type}`, type: TAG_BUTTON, title: n.title || n.label,
      on: { click: (event) => { event.stopPropagation(); select(key); } } },
      el(TAG_SPAN, { class: `dot t-${n.type}` }), el(TAG_SPAN, { class: "id", text: label }));
  }

  function coverageBadge(rating) {
    return el(TAG_SPAN, { class: `badge badge-${rating}`, title: COVERAGE[rating][1], text: COVERAGE[rating][0] });
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
      th.classList.toggle(VALUE_DROP_TARGET, draggedColumn !== key);
    });
    th.addEventListener("dragleave", () => th.classList.remove(VALUE_DROP_TARGET));
    th.addEventListener("drop", (event) => {
      if (!draggedColumn) return;
      event.preventDefault();
      const moved = draggedColumn;
      draggedColumn = null;
      moveColumn(moved, columnOrder.indexOf(key));
    });
    th.addEventListener("dragend", () => { draggedColumn = null; th.classList.remove(VALUE_DROP_TARGET); });
    th.addEventListener(EVENT_KEYDOWN, (event) => {
      if (!event.altKey || (event.key !== KEY_ARROWLEFT && event.key !== KEY_ARROWRIGHT)) return;
      event.preventDefault();
      moveColumn(key, columnOrder.indexOf(key) + (event.key === KEY_ARROWRIGHT ? 1 : -1));
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
        draggable: VALUE_TRUE, tabindex: "0", title: `${c.hint} · click to sort · drag, or Alt+arrow, to move`,
        on: { click: () => { state.sort = { column: c.key, dir: state.sort.column === c.key ? -state.sort.dir : 1 }; renderMatrix(); } } },
      c.label, columnGrip(c));
      columnHeaderMoves(th, c.key);
      return th;
    }));
    const body = rows.map((r) => el("tr", { class: state.selected === r.id ? VALUE_SELECTED : null, "data-key": r.id,
      on: { click: () => select(r.id) } }, ...ordered.map((c) => c.cell(r))));
    $(VALUE_MATRIX_TABLE).classList.toggle("with-functions", Boolean(CALL_GRAPH));
    clear($(VALUE_MATRIX_TABLE)).append(el(TAG_THEAD, {}, head), el(TAG_TBODY, {}, body));
    applyColumnWidths();
    $("matrix-status").textContent = `${rows.length} of ${matrixRows.length} requirements`;
  }

  // ---- column widths (TASK-TRC-018: RQ-TRC-043; DEC-TRC-012) ---------------------------------------------------
  // The first resize freezes every column at its drawn width, so that one column grows or shrinks and the others stay;
  // the table is then as wide as its columns and the frame scrolls (RQ-TRC-042).
  const COLUMNS_KEY = "agnos-trace-columns";
  const columnWidths = loadColumnWidths();
  const cssNumber = (name) => Number.parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  const headers = () => [...$(VALUE_MATRIX_TABLE).querySelectorAll("th[data-column]")];

  function applyColumnWidths() {
    const table = $(VALUE_MATRIX_TABLE);
    const custom = Object.keys(columnWidths).length > 0;
    for (const th of headers()) {
      if (!custom) {
        th.style.removeProperty(VALUE_WIDTH);
        continue;
      }
      columnWidths[th.dataset.column] ??= th.offsetWidth;         // a column not kept yet: as drawn
      th.style.width = `${columnWidths[th.dataset.column]}px`;
    }
    if (custom) {
      table.style.width = `${headers().reduce((sum, th) => sum + (columnWidths[th.dataset.column] || 0), 0)}px`;
      table.style.minWidth = "auto";
    } else {
      table.style.removeProperty(VALUE_WIDTH);
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
      grip.removeEventListener(EVENT_POINTERMOVE, move);
      grip.removeEventListener(EVENT_POINTERUP, end);
      grip.removeEventListener(EVENT_POINTERCANCEL, end);
    };
    grip.addEventListener(EVENT_POINTERMOVE, move);
    grip.addEventListener(EVENT_POINTERUP, end);
    grip.addEventListener(EVENT_POINTERCANCEL, end);
  }

  function columnGrip(c) {
    const grip = el(TAG_SPAN, { class: "col-grip", role: "separator", tabindex: "0", "aria-orientation": "vertical",
      [VALUE_ARIA_LABEL]: `Resize the ${c.label} column`, title: "Drag, or use the arrow keys, to resize · double-click to reset" });
    grip.addEventListener(EVENT_CLICK, (event) => event.stopPropagation());          // a grip never sorts
    grip.addEventListener("dblclick", (event) => { event.stopPropagation(); resetColumnWidths(); });
    grip.addEventListener("pointerdown", (event) => dragColumn(c.key, grip, event));
    grip.addEventListener("mousedown", (event) => event.preventDefault());       // the grip resizes, it never drags the header
    grip.addEventListener(EVENT_KEYDOWN, (event) => {
      if (event.key !== KEY_ARROWLEFT && event.key !== KEY_ARROWRIGHT) return;
      event.preventDefault();
      event.stopPropagation();
      const step = cssNumber("--c-splitter-step");
      setColumnWidth(c.key, grip.parentElement.offsetWidth + (event.key === KEY_ARROWRIGHT ? step : -step));
    });
    return grip;
  }

  function ariaSort(columnKey) {
    if (state.sort.column !== columnKey) return null;
    return state.sort.dir > 0 ? "ascending" : "descending";
  }

  function setCoverageFilter(value) {
    state.coverage = value;
    for (const b of $(VALUE_COVERAGE_FILTER).querySelectorAll(TAG_BUTTON)) b.setAttribute(VALUE_ARIA_PRESSED, String(b.dataset.coverage === value));
    renderMatrix();
  }

  $(VALUE_COVERAGE_FILTER).addEventListener(EVENT_CLICK, (event) => {
    const b = event.target.closest(TAG_BUTTON);
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

  // ---- quality view (TASK-TRC-047, TASK-TRC-048: RQ-TRC-057, RQ-TRC-062; DEC-TRC-034) ----------------------------
  const scoreText = (check) => (check.score === null ? "n/a" : check.score.toFixed(SCORE_DECIMALS));
  const gradeOf = (score) => (score === null ? null : (DATA.quality.scale.find(([, threshold]) => score >= threshold) || DATA.quality.scale.at(-1))[0]);
  const riskWeight = (check) => DATA.quality.risks[check.risk];
  // The lowest score first; an informational check or one with no score last; the heavier risk, then the title, break a tie.
  const isRanked = (check) => check.score !== null && check.risk !== INFORMATIONAL;
  const rankedChecks = () => CHECKS.toSorted((a, b) => (!isRanked(a)) - (!isRanked(b))
    || (a.score ?? 0) - (b.score ?? 0) || riskWeight(b) - riskWeight(a) || a.title.localeCompare(b.title));

  function checkFormula(check) {
    if (check.score === null) return "Nothing to score: the population is empty.";
    return `${SCORE_MAX} × (${check.population} − ${check.findings.length}) ÷ ${check.population} = ${scoreText(check)}`;
  }

  function checkKpis(check) {
    const compliant = check.population - check.findings.length;
    const kpi = (label, value) => el("div", { class: "check-kpi" }, el("span", { class: "check-kpi-value", text: value }),
      el("span", { class: "check-kpi-label", text: label }));
    return el("div", { class: "check-kpis" }, kpi("population", check.population), kpi("compliant", compliant),
      kpi("findings", check.findings.length), kpi("risk", check.risk));
  }

  function checkFindings(check) {
    const keys = findingKeys(check);
    const shown = state.moreFindings.has(check.key) ? keys : keys.slice(0, FINDINGS_SHOWN);
    return [keys.length ? el("ul", { class: "finding-list" }, ...shown.map((key) => {
      const n = nodes.get(key);
      return el("li", {}, el("button", { class: "finding", type: "button", title: n.title || n.label, on: { click: () => select(key) } },
        el("span", { class: `dot t-${n.type}` }), el("span", { class: "id", text: n.label }),
        n.title ? el("span", { class: "finding-title", text: n.title }) : null));
    })) : el("div", { class: "check-none", text: "None — the rule holds." }),
    keys.length > shown.length ? el("button", { class: "link-button", type: "button",
      on: { click: () => { state.moreFindings.add(check.key); renderQuality(); } }, text: `Show all ${keys.length}` }) : null];
  }

  // A check, compact (title, risk, score bar, findings) or detailed behind its chevron (rule, formula, figures, findings).
  function checkCard(check) {
    const open = state.openChecks.has(check.key);
    const grade = isRanked(check) ? gradeOf(check.score) : null;
    const detailId = `check-detail-${check.key}`;
    const toggleCheck = () => { if (open) state.openChecks.delete(check.key); else state.openChecks.add(check.key); renderQuality(); };
    return el("article", { class: `card check-card${open ? " is-open" : ""}`, id: `check-${check.key}`, "data-check": check.key },
      el("header", { class: "check-head" },
        el("button", { class: "check-toggle", type: "button", "aria-expanded": String(open), "aria-controls": detailId,
          title: open ? "Show this check compact" : "Show the rule, the figures and the findings of this check",
          on: { click: toggleCheck } }, el("span", { class: "check-chevron", "aria-hidden": "true" }),
          el("span", { class: "check-card-title", text: check.title })),
        el("span", { class: `badge badge-neutral check-risk risk-${check.risk}`, text: check.risk, title: "Risk level of the check: its weight in the overall score" }),
        el("span", { class: `check-score grade-${grade || VALUE_NONE}`, title: checkFormula(check) },
          el("span", { class: "score-bar" }, el("span", { class: "score-fill", style: { "--score": (check.score ?? 0) * PERCENT / SCORE_MAX } })),
          el("span", { class: "score-text", text: scoreText(check) })),
        el("span", { class: checkBadgeClass(check), text: check.findings.length, title: "Findings: elements that fail this check" })),
      open ? el("div", { class: "check-detail", id: detailId },
        el("p", { class: "check-card-desc", text: check.rule }),
        el("p", { class: "check-formula", text: checkFormula(check) }), checkKpis(check), ...checkFindings(check)) : null);
  }

  // ---- quality charts (TASK-TRC-050: RQ-TRC-061, RQ-TRC-065; DEC-TRC-035) -----------------------------------------
  // Inline SVG drawn from the `quality` block, no library: a radar of the checks, bars per trigram, the coverage shares.
  // Every chart has a title and a description; its items take the keyboard focus and raise the chart tooltip.
  const SVG_NS = "http://www.w3.org/2000/svg";
  const RADAR = { width: 300, height: 180, radius: 56, ring: 4, labelGap: 12, pointRadius: 4 };
  const AREA = { width: 260, rowHeight: 26, barHeight: 14, labelWidth: 38, barWidth: 150, textGap: 6 };
  const SHARE = { width: 260, height: 20, labelHeight: 22 };
  const FULL_TURN = 360;
  const QUARTER_TURN = 90;
  const HALF = 2;

  function svgEl(tag, attrs, ...children) {
    const node = document.createElementNS(SVG_NS, tag);
    for (const [name, value] of Object.entries(attrs || {})) if (!isAbsent(value)) node.setAttribute(name, String(value));
    node.append(...children.flat().filter((child) => !isAbsent(child))
      .map((child) => (child instanceof Node ? child : document.createTextNode(String(child)))));
    return node;
  }

  function chartFrame(width, height, title, description, ...parts) {
    return svgEl("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", class: "chart-svg", "aria-label": title },
      svgEl("desc", {}, description), ...parts);           // DEC-HST-007: an SVG title would raise a second tooltip
  }

  // An item of a chart: focusable, with a text label for screen readers, its tooltip on hover and on focus.
  function chartItem(node, label, lines, onActivate) {
    node.setAttribute("tabindex", "0");
    node.setAttribute("aria-label", label);
    richTip(node, () => ({ head: lines[0], lines: lines.slice(1) }));
    if (onActivate) {
      node.addEventListener("click", onActivate);
      node.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onActivate(); } });
    }
    return node;
  }


  function checkTipLines(check) {
    return [check.title, `score ${scoreText(check)} out of ${SCORE_MAX} · risk ${check.risk}`,
      `population ${check.population} · ${check.findings.length} ${check.findings.length === 1 ? "finding" : "findings"}`];
  }

  function radarChart() {
    const scored = CHECKS.filter((c) => c.score !== null);
    const cx = RADAR.width / HALF;
    const cy = RADAR.height / HALF;
    const at = (i, fraction) => {
      const angle = ((-QUARTER_TURN + (FULL_TURN * i) / scored.length) * Math.PI) / (FULL_TURN / HALF);
      return [cx + Math.cos(angle) * RADAR.radius * fraction, cy + Math.sin(angle) * RADAR.radius * fraction];
    };
    const ring = (n) => svgEl("polygon", { class: "radar-ring", points: scored.map((_, i) => at(i, n / RADAR.ring).join(",")).join(" ") });
    const shape = svgEl("polygon", { class: "radar-shape", points: scored.map((c, i) => at(i, c.score / SCORE_MAX).join(",")).join(" ") });
    const axes = scored.map((check, i) => {
      const [x, y] = at(i, 1);
      const [lx, ly] = at(i, 1 + RADAR.labelGap / RADAR.radius);
      const anchor = Math.abs(lx - cx) < RADAR.labelGap ? "middle" : (lx > cx ? "start" : "end");
      const group = svgEl("g", { class: "radar-axis", "data-check": check.key },
        svgEl("line", { class: "radar-spoke", x1: cx, y1: cy, x2: x, y2: y }),
        svgEl("text", { class: "radar-label", x: lx, y: ly, "text-anchor": anchor, "dominant-baseline": "middle" }, check.label));
      group.addEventListener("click", () => openCheck(check.key));
      return group;
    });
    const points = scored.map((check, i) => {
      const [x, y] = at(i, check.score / SCORE_MAX);
      return chartItem(svgEl("circle", { class: `radar-point grade-${isRanked(check) ? gradeOf(check.score) : VALUE_NONE}`, cx: x, cy: y, r: RADAR.pointRadius, "data-check": check.key }),
        `${check.title}: score ${scoreText(check)} out of ${SCORE_MAX}`, checkTipLines(check), () => openCheck(check.key));
    });
    return chartFrame(RADAR.width, RADAR.height, "Checks radar",
      `Score out of ${SCORE_MAX} of each check, one axis per check: the further from the centre, the better.`,
      ...Array.from({ length: RADAR.ring }, (_, n) => ring(n + 1)), ...axes, shape, ...points);
  }

  function areaBars() {
    const rows = Object.entries(DATA.quality.trigrams);
    const bar = ([tri, t], i) => {
      const y = i * AREA.rowHeight;
      const width = AREA.barWidth * ((t.score ?? 0) / SCORE_MAX);
      const group = svgEl("g", { class: `area-bar grade-${t.grade || VALUE_NONE}`, "data-tri": tri },
        svgEl("text", { class: "area-label", x: 0, y: y + AREA.barHeight, }, tri),
        svgEl(SVG_RECT, { class: "area-track", x: AREA.labelWidth, y, width: AREA.barWidth, height: AREA.barHeight }),
        svgEl(SVG_RECT, { class: "area-fill", x: AREA.labelWidth, y, width, height: AREA.barHeight }),
        svgEl("text", { class: "area-value", x: AREA.labelWidth + AREA.barWidth + AREA.textGap, y: y + AREA.barHeight },
          `${t.grade || "–"} ${scoreOut(t.score)}`));
      return chartItem(group, `${tri}: grade ${t.grade}, score ${scoreOut(t.score)} out of ${SCORE_MAX}`,
        [tri, `grade ${t.grade || VALUE_NONE} · score ${scoreOut(t.score)} out of ${SCORE_MAX}`,
          `${t.checks.reduce((sum, c) => sum + c.findings, 0)} findings in ${t.checks.length} checks`]);
    };
    return chartFrame(AREA.width, Math.max(rows.length, 1) * AREA.rowHeight, "Score by feature area",
      `Overall score out of ${SCORE_MAX} of each feature area (trigram), with its grade.`, ...rows.map(bar));
  }

  function coverageShares() {
    const total = requirements.length;
    const counts = { covered: 0, indirect: 0, uncovered: 0 };
    for (const r of requirements) counts[DATA.coverage[r.key]] += 1;
    let x = 0;
    const parts = Object.keys(COVERAGE).map((k) => {
      const width = total ? (SHARE.width * counts[k]) / total : 0;
      const share = total ? Math.round((PERCENT * counts[k]) / total) : 0;
      const rect = chartItem(svgEl(SVG_RECT, { class: `share-part share-${k}`, x, y: 0, width, height: SHARE.height }),
        `${COVERAGE[k][0]}: ${counts[k]} of ${total} requirements`,
        [COVERAGE[k][0], `${counts[k]} of ${total} requirements · ${share} %`, COVERAGE[k][1]]);
      x += width;
      return rect;
    });
    const legend = Object.keys(COVERAGE).map((k, i) => svgEl("text", { class: "share-label", x: (SHARE.width / Object.keys(COVERAGE).length) * i,
      y: SHARE.height + SHARE.labelHeight }, `${COVERAGE[k][0]} ${counts[k]}`));
    return chartFrame(SHARE.width, SHARE.height + SHARE.labelHeight + AREA.textGap, "Requirement coverage",
      "Share of the requirements covered by a source file, covered indirectly, or uncovered.", ...parts, ...legend);
  }

  function renderCharts() {
    const card = (title, svg) => el("article", { class: "card chart-card" },
      el("header", { class: "card-header" }, el("h3", { class: "card-title", text: title })), svg);
    clear($("quality-charts")).append(card("Checks", radarChart()),
      card("Feature areas", areaBars()),
      card("Coverage", coverageShares()));
  }

  // The grade as a coloured letter: the letter is always written, the colour only repeats it (RQ-TRC-065).
  function gradeChip(grade, score, extra) {
    const meaning = grade ? `Grade ${grade}: ${DATA.quality.verdicts[grade].toLowerCase()}, score ${score.toFixed(SCORE_DECIMALS)} out of ${SCORE_MAX}` : "Not graded";
    return el("span", { class: `grade-chip grade-${grade || VALUE_NONE} ${extra || ""}`, title: meaning, text: grade || "–" });
  }

  const attentionChecks = () => rankedChecks().filter((c) => isRanked(c) && c.score < DATA.quality.attention);

  function scaleStrip(grade) {
    const scale = DATA.quality.scale;
    return el("ol", { class: "scale", "aria-label": "Grade scale" }, ...scale.map(([letter, threshold], i) => {
      const upper = i ? scale[i - 1][1] : SCORE_MAX;
      const range = i ? `${threshold} to under ${upper}` : `${threshold} to ${upper}`;
      return el("li", { class: `scale-step grade-${letter}${letter === grade ? " is-current" : ""}`, text: letter,
        title: `Grade ${letter}: score ${range}`, "aria-current": letter === grade ? "true" : null });
    }));
  }

  const scoreOut = (score) => (score === null ? "n/a" : score.toFixed(SCORE_DECIMALS));

  function verdictText(grade, attention) {
    if (!grade) return "Nothing to score";
    const need = attention === 1 ? "check needs" : "checks need";
    return `${DATA.quality.verdicts[grade]}: ${attention ? `${attention} ${need} attention` : "no check needs attention"}`;
  }

  // RQ-TRC-060: the report card of the decision maker: grade, score, verdict, grade of each trigram, what to fix first.
  function renderReport() {
    const quality = DATA.quality;
    const fixes = rankedChecks().filter((c) => isRanked(c) && c.findings.length).slice(0, FIX_FIRST_SHOWN);
    const fixLink = (c) => el("li", {}, el("button", { class: "fix-link", type: "button", "data-check": c.key,
      title: `${c.rule} Open this check.`, on: { click: () => openCheck(c.key) } },
    el("span", { class: "fix-title", text: c.title }),
    el("span", { class: `check-score grade-${gradeOf(c.score)}` }, el("span", { class: "score-text", text: scoreText(c) }))));
    const area = ([tri, t]) => el("li", { class: "report-trigram", title: `${tri}: score ${scoreOut(t.score)} out of ${SCORE_MAX}` },
      el("span", { class: "report-tri", text: tri }), gradeChip(t.grade, t.score), el("span", { class: "report-tri-score", text: scoreOut(t.score) }));
    clear($("quality-report")).append(
      el("div", { class: "report-main" }, gradeChip(quality.grade, quality.score, "report-grade"),
        el("div", { class: "report-summary" },
          el("div", { class: "report-score", text: quality.score === null ? "n/a" : `${scoreOut(quality.score)} / ${SCORE_MAX}` }),
          el("div", { class: "report-verdict", text: verdictText(quality.grade, attentionChecks().length) }), scaleStrip(quality.grade))),
      el("div", { class: "report-fix" }, el("h3", { class: "report-title", text: "Fix first" }),
        fixes.length ? el("ul", { class: "fix-first" }, ...fixes.map(fixLink)) : el("p", { class: "check-none", text: "Nothing to fix." })),
      el("div", { class: "report-areas" }, el("h3", { class: "report-title", text: "By feature area" }),
        el("ul", { class: "report-trigrams" }, ...Object.entries(quality.trigrams).map(area))));
  }

  function renderGradeChips() {
    for (const id of ["side-grade", "quality-grade", "overview-grade"]) {
      clear($(id)).append(gradeChip(DATA.quality.grade, DATA.quality.score));
    }
  }

  function renderQuality() {
    const total = CHECKS.filter((c) => c.risk !== INFORMATIONAL).reduce((sum, c) => sum + c.findings.length, 0);
    $("quality-count").textContent = total ? String(total) : "";
    renderGradeChips();
    renderReport();
    renderCharts();
    clear($("quality-list")).append(...rankedChecks().map(checkCard));
  }

  $("expand-checks").addEventListener("click", () => { CHECKS.forEach((c) => state.openChecks.add(c.key)); renderQuality(); });
  $("collapse-checks").addEventListener("click", () => { state.openChecks.clear(); renderQuality(); });

  function openCheck(key) {
    state.openChecks.add(key);
    renderQuality();
    showView("quality");
    const card = $(`check-${key}`);
    if (card) card.scrollIntoView({ block: "start" });
  }

  // ---- history view (TASK-HST-004: RQ-HST-007, RQ-HST-014; DEC-HST-005, DEC-HST-006) ----------------------------
  // The `history` block of the data file (FTR-HST-001), drawn as a timeline of inline SVG: one row per process element,
  // or per file and function, one mark per commit that changed it. Only the rows in view are in the document
  // (RQ-HST-013); the page computes no intervention, it filters and draws.
  const HISTORY = DATA.history || null;
  const HISTORY_VIEW = "history";
  const ANGLE_REQUIREMENTS = "requirements";
  const ANGLE_CODE = "code";
  const GROUPING_FILES = "files";
  const KIND_HUMAN = "human";
  const KIND_AGENT = "agent";
  const KIND_TOGETHER = "together";
  const KIND_LABEL = { [KIND_HUMAN]: "human", [KIND_AGENT]: "agent", [KIND_TOGETHER]: "human and agent together" };
  const IDENTITY_TOKENS = 12;           // the identities past these take a golden-angle hue (DEC-HST-005)
  const ROW_OVERSCAN = 6;               // rows drawn above and below the view, so that a scroll shows no gap
  const PAN_FRACTION = 0.1;             // an arrow key moves the period by this share of its width
  const MIN_SPAN_MS = 3600000;          // the narrowest period: one hour
  const DAY_MS = 86400000;
  const WEEK_DAYS = 7;
  const MONDAY_OFFSET_DAYS = 4;         // 1970-01-05, the first Monday after the epoch
  const EDGE_PAD = 0.03;                // the whole history fits with this share of margin on each side
  const WHEEL_NOTCH = 100;              // one wheel notch, in deltaY units
  const TICK_FROM = 0.25;               // an overview tick spans the middle half of the strip
  const TICK_TO = 0.75;
  const DIAMOND_RATIO = 1.25;           // a diamond's half-diagonal, as a share of a circle's radius of the same area
  const FULL_HUE = 360;
  const LOCALE = "en";
  const UTC = "UTC";
  const SVG_CIRCLE = "circle";
  const VALUE_PATH = "path";
  const SVG_GROUP = "g";
  const SVG_TEXT = "text";
  const CLASS_MARK = ".history-mark";
  const CLASS_LABEL = "history-label";
  const CLASS_SWATCH = "history-swatch";
  const IS_PINNED = "is-pinned";
  const EVENT_POINTERDOWN = "pointerdown";
  const KEY_ENTER = "Enter";
  const CLASS_NAME = "history-name";
  const ATTR_PERSON = "data-person";
  const CSS_TIP_DELAY = "--c-history-tip-delay";
  const TEXT_IDENTITIES = "identities";
  const ID_SHOW_EMPTY = "history-show-empty";
  const ID_HISTORY_PEOPLE = "history-people";
  const ID_HISTORY_KIND = "history-kind";
  const CSS_HAIRLINE = "--s-stroke-hairline";
  const CSS_IDENTITY = "--identity";
  const ID_HISTORY_SCROLL = "history-scroll";
  const ID_HISTORY_ROWS = "history-rows";
  const ID_HISTORY_GROUPING = "history-grouping";
  const ID_HISTORY_ANGLE = "history-angle";
  const ID_HISTORY_CARD = "history-card";
  const ID_HISTORY_OVERVIEW = "history-overview";
  const CLASS_CARD_MUTED = "history-card-muted";
  const CLASS_CARD_LIST = "history-card-list";
  const CLASS_RING = "history-ring";
  const CLASS_LEGEND_ITEM = "history-legend-item";
  const CLASS_COUNT = "history-count";
  const CSS_RING_GAP = "--c-history-ring-gap";
  const CSS_MARK_MAX = "--c-history-mark-max";
  const ATTR_VIEWBOX = "viewBox";
  const ATTR_ARIA_HIDDEN = "aria-hidden";
  const MONTHS_PER_QUARTER = 3;
  const MONTHS_PER_YEAR = 12;
  const NUMERIC = "numeric";
  const SHORT = "short";
  const TWO_DIGIT = "2-digit";
  const UNIT_WEEK = "week";
  const UNIT_MONTH = "month";
  const UNIT_QUARTER = "quarter";
  const UNIT_YEAR = "year";
  const DAYS_PER_MONTH = 30;
  const DAYS_PER_QUARTER = 91;
  const DAYS_PER_YEAR = 365;
  const SIX = 6;
  const FORMAT_TIME = { month: SHORT, day: NUMERIC, hour: TWO_DIGIT, minute: TWO_DIGIT };
  const FORMAT_DAY = { month: SHORT, day: NUMERIC };
  const FORMAT_MONTH = { month: SHORT, year: NUMERIC };
  // The steps of the time axis, finest first: [name, approximate width in ms, label format].
  const TICK_UNITS = [
    ["hour", MIN_SPAN_MS, FORMAT_TIME],
    ["six hours", SIX * MIN_SPAN_MS, FORMAT_TIME],
    ["day", DAY_MS, FORMAT_DAY],
    [UNIT_WEEK, WEEK_DAYS * DAY_MS, FORMAT_DAY],
    [UNIT_MONTH, DAYS_PER_MONTH * DAY_MS, FORMAT_MONTH],
    [UNIT_QUARTER, DAYS_PER_QUARTER * DAY_MS, FORMAT_MONTH],
    [UNIT_YEAR, DAYS_PER_YEAR * DAY_MS, { year: NUMERIC }],
  ];
  const DATE_TEXT = new Intl.DateTimeFormat(LOCALE, { timeZone: UTC, year: NUMERIC, ...FORMAT_TIME });
  const DAY_TEXT = new Intl.DateTimeFormat(LOCALE, { timeZone: UTC, year: NUMERIC, ...FORMAT_DAY });

  const KIND_ALL = "all";
  const BAND_DAY_LIMIT = 45;            // a period of at most this many days is drawn day by day (RQ-HST-008)
  const BAND_WEEK_LIMIT = 270;          // up to this many, week by week; beyond, month by month
  const BAND_STACK = [KIND_HUMAN, KIND_TOGETHER, KIND_AGENT];   // from the bottom of a bar
  const hist = {
    angle: ANGLE_REQUIREMENTS, grouping: GROUPING_FILES, span: null, full: null, baseRows: [], rows: [], built: false,
    pinned: null, people: new Set(), kind: KIND_ALL, showEmpty: false, kept: [], shown: [], scope: null,
  };
  const MERGED_TEXT = { email: "e-mail", mailmap: ".mailmap" };
  const commitTime = HISTORY ? HISTORY.commits.map((c) => Date.parse(c.date)) : [];
  const fnIndex = new Map(fnKeys.map((key, i) => [key, i]));
  const maxLines = HISTORY ? Object.values(HISTORY.interventions).flatMap((byKey) => Object.values(byKey))
    .reduce((most, list) => list.reduce((m, [, lines]) => Math.max(m, lines), most), 1) : 1;

  // RQ-HST-014: a colour of its own per identity, from the tokens: twelve categorical ones, then golden-angle hues.
  function identityColour(index) {
    if (index < IDENTITY_TOKENS) return `var(--c-history-identity-${index + 1})`;
    const turn = index - IDENTITY_TOKENS;
    const lightness = cssNumber(turn % 2 ? "--c-history-identity-lightness-alt" : "--c-history-identity-lightness");
    const hue = (cssNumber("--c-history-identity-hue-start") + turn * cssNumber("--c-history-identity-hue-step")) % FULL_HUE;
    return `oklch(${lightness} ${cssNumber("--c-history-identity-chroma")} ${hue})`;
  }
  const colourOf = HISTORY ? HISTORY.people.map((_, i) => identityColour(i)) : [];

  function kindIcon(kind) {
    const icon = svgEl("svg", { class: `kind-icon kind-${kind}`, viewBox: "0 0 24 24", [ATTR_ARIA_HIDDEN]: VALUE_TRUE },
      svgEl("use", { href: `#icon-${kind}` }));
    return icon;
  }

  // An identity as the page names it everywhere: its colour, its kind's icon, its name (never the colour alone).
  function personTag(index) {
    const person = HISTORY.people[index];
    return richTip(el(TAG_SPAN, { class: "history-person", tabindex: "0" },
      el(TAG_SPAN, { class: CLASS_SWATCH, style: { [CSS_IDENTITY]: colourOf[index] } }), kindIcon(person.kind),
      el(TAG_SPAN, { text: person.name })), () => linesTip(identityLines(index)), CSS_TIP_DELAY);
  }

  // ---- rows: the requirements angle, the code angle by file or by requirement ----
  function mergeMarks(lists) {
    const byCommit = new Map();
    for (const [commit, lines] of lists.flat()) byCommit.set(commit, (byCommit.get(commit) || 0) + lines);
    return [...byCommit.entries()].sort((a, b) => a[0] - b[0]);
  }

  function groupedRows(keys, marksOf) {
    const rows = [];
    for (const type of TYPES) {
      const ofType = keys.filter((key) => nodes.get(key).type === type);
      if (!ofType.length) continue;
      rows.push({ group: true, label: plural(type, 2), count: ofType.length });
      for (const key of ofType) {
        const n = nodes.get(key);
        rows.push({ key, label: n.label, name: n.title, depth: 0, marks: marksOf(key) });
      }
    }
    return rows;
  }

  const elementKeys = () => DATA.elements.filter((e) => e.kind === VALUE_ELEMENT).map((e) => e.id);
  const elementMarks = (id) => HISTORY.interventions.elements[id] || [];
  const fileMarks = (key) => HISTORY.interventions.files[nodes.get(key).path] || [];
  const functionMarks = (key) => (HISTORY.interventions.functions || {})[String(fnIndex.get(key))] || [];

  function fileRows() {
    const functionsOf = new Map();
    for (const key of fnKeys) {
      const file = nodes.get(key).file;
      if (!functionsOf.has(file)) functionsOf.set(file, []);
      functionsOf.get(file).push(key);
    }
    const rows = [];
    for (const f of DATA.files) {
      const key = FILE_PREFIX + f.path;
      const cut = f.path.lastIndexOf("/") + 1;                 // the file name first, its folder after it, muted
      rows.push({ key, label: f.path.slice(cut), name: f.path.slice(0, cut), title: f.path, depth: 0, marks: fileMarks(key) });
      for (const fn of functionsOf.get(key) || []) {
        rows.push({ key: fn, label: nodes.get(fn).label, name: "", depth: 1, marks: functionMarks(fn) });
      }
    }
    return rows;
  }

  // RQ-HST-003: an element's code is the functions citing it, and the files citing it outside any function of theirs.
  function codeMarks(id) {
    const citing = links.get(id).filter((l) => l.kind === LINK_KIND_CODE && l.dir === "in").map((l) => l.key);
    const functions = citing.filter((key) => key.startsWith(FN_PREFIX));
    const withFunction = new Set(functions.map((key) => nodes.get(key).file));
    const files = citing.filter((key) => key.startsWith(FILE_PREFIX) && !withFunction.has(key));
    return mergeMarks([...functions.map(functionMarks), ...files.map(fileMarks)]);
  }

  function historyRows() {
    if (hist.angle === ANGLE_REQUIREMENTS) return groupedRows(elementKeys(), elementMarks);
    if (hist.grouping === GROUPING_FILES) return fileRows();
    const cited = elementKeys().filter((id) => links.get(id).some((l) => l.kind === LINK_KIND_CODE && l.dir === "in"));
    return groupedRows(cited, codeMarks);
  }

  // ---- filters (TASK-HST-005: RQ-HST-009) ----
  const filtering = () => hist.people.size > 0 || hist.kind !== KIND_ALL;

  function keptCommits() {
    return HISTORY.commits.map((c) => {
      if (hist.people.size && ![c.author, ...c.coAuthors].some((i) => hist.people.has(i))) return false;
      if (hist.kind === KIND_HUMAN) return c.kind !== KIND_AGENT;
      return hist.kind !== KIND_AGENT || c.kind !== KIND_HUMAN;
    });
  }

  // ---- scope (TASK-HST-006: RQ-HST-011): an element and what it contains, or a file and its functions ----
  function contained(key) {
    const found = new Set([key]);
    const queue = [key];
    while (queue.length) {
      for (const l of links.get(queue.shift())) {
        if (l.kind === VALUE_CONTAINS && l.dir === "out" && !found.has(l.key)) { found.add(l.key); queue.push(l.key); }
      }
    }
    return found;
  }

  function scopeKeys() {
    if (!hist.scope) return null;
    const n = nodes.get(hist.scope);
    if (n.type === TYPE_FILE) return new Set([hist.scope, ...fnKeys.filter((key) => nodes.get(key).file === hist.scope)]);
    if (n.type === "FN") return new Set([hist.scope]);
    const elements = contained(hist.scope);
    if (hist.angle === ANGLE_REQUIREMENTS || hist.grouping !== GROUPING_FILES) return elements;
    const code = new Set();
    for (const id of elements) {
      for (const l of links.get(id)) {
        if (l.kind !== LINK_KIND_CODE || l.dir !== "in") continue;
        code.add(l.key);
        if (l.key.startsWith(FN_PREFIX)) code.add(nodes.get(l.key).file);
      }
    }
    return code;
  }

  function scopeHistory(key) {
    const n = nodes.get(key);
    hist.scope = key;
    showView(HISTORY_VIEW);
    setAngle(n.type === TYPE_FILE || n.type === "FN" ? ANGLE_CODE : ANGLE_REQUIREMENTS, GROUPING_FILES);
  }

  function renderScope() {
    const chipNode = $("history-scope");
    chipNode.hidden = !hist.scope;
    if (!hist.scope) return;
    clear(chipNode).append(el(TAG_SPAN, { text: `Scope: ${nodes.get(hist.scope).label}` }),
      el(TAG_BUTTON, { type: TAG_BUTTON, [VALUE_ARIA_LABEL]: "Remove the scope", title: "Show every row again, the filters kept", text: "×",
        on: { [EVENT_CLICK]: () => { hist.scope = null; applyFilters(); } } }));
  }

  function shownRows() {
    const rows = [];
    const scope = scopeKeys();
    let heading = null;
    for (const row of hist.baseRows) {
      if (row.group) {
        heading = { ...row, count: 0 };
        rows.push(heading);
        continue;
      }
      if (scope && !scope.has(row.key)) continue;
      const marks = row.marks.filter(([ci]) => hist.kept[ci]);
      if (!marks.length && filtering() && !hist.showEmpty) continue;
      rows.push({ ...row, marks });
      if (heading) heading.count += 1;
    }
    return rows.filter((row) => !row.group || row.count);
  }

  function applyFilters() {
    hist.kept = keptCommits();
    hist.rows = shownRows();
    hist.shown = [...new Set(hist.rows.flatMap((row) => (row.group ? [] : row.marks.map(([ci]) => ci))))].sort((a, b) => a - b);
    for (const chipNode of $(ID_HISTORY_PEOPLE).querySelectorAll("[data-person]")) {
      chipNode.setAttribute(VALUE_ARIA_PRESSED, String(hist.people.has(Number(chipNode.dataset.person))));
    }
    for (const b of $(ID_HISTORY_KIND).querySelectorAll(TAG_BUTTON)) b.setAttribute(VALUE_ARIA_PRESSED, String(b.dataset.kind === hist.kind));
    const active = hist.rows.filter((row) => !row.group).length;
    $("history-kept").textContent = `${rowCount(active)} · ${commitCount(hist.shown.length)}${filtering() ? TEXT_KEPT_SPACED : ""}`;
    renderFigures();
    renderScope();
    drawHistory();
  }

  function resetFilters() {
    hist.people.clear();
    hist.kind = KIND_ALL;
    hist.showEmpty = false;
    $(ID_SHOW_EMPTY).checked = false;
    applyFilters();
  }

  // An identity's chip: its colour, its kind's icon, its name, its commits; its tooltip tells how it was merged.
  function identityLines(index) {
    const person = HISTORY.people[index];
    const merged = person.mergedBy.length            // RQ-HST-010 as amended: said only when a merge took place
      ? `Identity merged by ${person.mergedBy.map((how) => MERGED_TEXT[how] || how).join(" and ")}` : null;
    return [`${person.name} (${KIND_LABEL[person.kind]})`, `${person.commits} commits as author, ${person.coCommits} as co-author`,
      `Names: ${person.names.join(", ")}`, `E-mails: ${person.emails.join(", ")}`, merged].filter(Boolean);
  }

  // RQ-HST-010: the sidebar's History section; a click opens the History tab filtered on that identity alone.
  function renderHistorySidebar() {
    $("side-history").hidden = false;
    clear($("history-shortcuts")).append(...HISTORY.people.map((person, i) => {
      const item = el(TAG_BUTTON, { class: CLASS_QUALITY_SHORTCUT, type: TAG_BUTTON, [ATTR_PERSON]: i, [VALUE_ARIA_LABEL]: identityLines(i).join(". "),
        on: { [EVENT_CLICK]: () => openForPerson(i) } },
      el(TAG_SPAN, { class: "history-person-line" }, el(TAG_SPAN, { class: CLASS_SWATCH, style: { [CSS_IDENTITY]: colourOf[i] } }),
        kindIcon(person.kind), el(TAG_SPAN, { class: CLASS_NAME, text: person.name })),
      el(TAG_SPAN, { class: "badge badge-neutral chip-count", text: person.commits + person.coCommits }));
      item.addEventListener(EVENT_MOUSEOVER, () => {
        scheduleRichTip(item, () => linesTip(identityLines(i)), CSS_TIP_DELAY);
      });
      item.addEventListener(EVENT_MOUSEOUT, hideHistoryTip);
      item.addEventListener(EVENT_FOCUS, () => showTipLines(item, identityLines(i)));
      item.addEventListener(EVENT_BLUR, hideHistoryTip);
      return el("li", {}, item);
    }));
  }

  function openForPerson(index) {
    hideHistoryTip();
    showView(HISTORY_VIEW);
    hist.people = new Set([index]);
    hist.kind = KIND_ALL;
    applyFilters();
  }

  function personChip(index, onClick) {
    const person = HISTORY.people[index];
    return richTip(el(TAG_BUTTON, { class: "chip", type: TAG_BUTTON, [ATTR_PERSON]: index, [VALUE_ARIA_PRESSED]: String(hist.people.has(index)),
      [VALUE_ARIA_LABEL]: identityLines(index).join(". "), on: { [EVENT_CLICK]: onClick } },
    el(TAG_SPAN, { class: CLASS_SWATCH, style: { [CSS_IDENTITY]: colourOf[index] } }), kindIcon(person.kind),
    el(TAG_SPAN, { text: person.name }), el(TAG_SPAN, { class: CLASS_CHIP_COUNT, text: person.commits + person.coCommits })),
    () => linesTip(identityLines(index)), CSS_TIP_DELAY);
  }

  function renderPeopleChips() {
    clear($(ID_HISTORY_PEOPLE)).append(...HISTORY.people.map((_, i) => personChip(i, () => {
      toggle(hist.people, i);
      applyFilters();
    })));
  }

  const rowCount = (n) => `${n} ${n === 1 ? "row" : "rows"}`;
  const commitCount = (n) => `${n} ${n === 1 ? "commit" : TEXT_COMMITS}`;

  // ---- figures (RQ-HST-008) ----
  const dayCount = (ms) => { const days = Math.max(1, Math.round(ms / DAY_MS)); return `${days} ${days === 1 ? "day" : "days"}`; };
  function renderFigures() {
    const shown = hist.shown.map((ci) => HISTORY.commits[ci]);
    const people = new Set(shown.flatMap((c) => [c.author, ...c.coAuthors]));
    const ofKind = (kind) => [...people].filter((i) => HISTORY.people[i].kind === kind).length;
    const withAgent = shown.filter((c) => c.kind !== KIND_HUMAN).length;
    const dates = hist.shown.map((ci) => commitTime[ci]);
    const period = dates.length ? `${DAY_TEXT.format(dates[0])} – ${DAY_TEXT.format(dates.at(-1))}` : "—";
    const figure = (key, label, value, sub) => el("div", { class: "kpi", "data-figure": key },
      el(TAG_SPAN, { class: CLASS_KPI_LABEL, text: label }), el(TAG_SPAN, { class: CLASS_KPI_VALUE, text: value }),
      el(TAG_SPAN, { class: VALUE_KPI_SUB, text: sub }));
    clear($("history-kpis")).append(
      figure(TEXT_COMMITS, "Commits", shown.length, filtering() ? TEXT_KEPT_SPACED.trim() : "on the rows shown"),
      figure("humans", "Humans", ofKind(KIND_HUMAN), TEXT_IDENTITIES),
      figure("agents", "Agents", ofKind(KIND_AGENT), TEXT_IDENTITIES),
      figure("share", "With an agent", `${pct(withAgent, shown.length)} %`, `${withAgent} commits, alone or with a human`),
      figure("period", "Period", dates.length ? dayCount(dates.at(-1) - dates[0]) : "—", period));
  }

  // ---- time scale ----
  const rowHeight = () => cssNumber("--c-history-row-height");
  const labelWidth = () => cssNumber("--c-history-label-width");
  const plotWidth = () => Math.max(1, $(ID_HISTORY_SCROLL).clientWidth - labelWidth());
  const plotLeft = () => $(ID_HISTORY_SCROLL).getBoundingClientRect().left + labelWidth();
  const spanWidth = () => hist.span[1] - hist.span[0];
  const localX = (t) => ((t - hist.span[0]) / spanWidth()) * plotWidth();
  const xOf = (t) => plotLeft() + localX(t);
  const timeAt = (clientX) => hist.span[0] + ((clientX - plotLeft()) / plotWidth()) * spanWidth();

  function fullSpan() {
    const first = commitTime.reduce((a, b) => Math.min(a, b), Infinity);
    const last = commitTime.reduce((a, b) => Math.max(a, b), -Infinity);
    const pad = Math.max((last - first) * EDGE_PAD, DAY_MS);
    return [first - pad, last + pad];
  }

  // The period in view, kept inside the whole history and no narrower than an hour.
  function setSpan(start, width) {
    const [full0, full1] = hist.full;
    const w = Math.min(Math.max(width, MIN_SPAN_MS), full1 - full0);
    const s = Math.min(Math.max(start, full0), full1 - w);
    hist.span = [s, s + w];
    drawHistory();
  }

  function zoomAround(t, factor) {
    const width = spanWidth() / factor;
    setSpan(t - ((t - hist.span[0]) / spanWidth()) * width, width);
  }

  const zoomStep = () => cssNumber("--c-history-zoom-step");
  const fitHistory = () => setSpan(hist.full[0], hist.full[1] - hist.full[0]);
  const panBy = (fraction) => setSpan(hist.span[0] + fraction * spanWidth(), spanWidth());

  // ---- the time axis ----
  function floorTo(unit, t) {
    const d = new Date(t);
    if (unit === UNIT_WEEK) return t - ((((t - MONDAY_OFFSET_DAYS * DAY_MS) % (WEEK_DAYS * DAY_MS)) + WEEK_DAYS * DAY_MS) % (WEEK_DAYS * DAY_MS));
    if (unit === UNIT_MONTH) return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1);
    if (unit === UNIT_QUARTER) return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() - (d.getUTCMonth() % MONTHS_PER_QUARTER), 1);
    if (unit === UNIT_YEAR) return Date.UTC(d.getUTCFullYear(), 0, 1);
    const step = TICK_UNITS.find(([name]) => name === unit)[1];
    return t - (t % step);
  }

  function nextTick(unit, t) {
    const d = new Date(t);
    if (unit === UNIT_MONTH) return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1);
    if (unit === UNIT_QUARTER) return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + MONTHS_PER_QUARTER, 1);
    if (unit === UNIT_YEAR) return Date.UTC(d.getUTCFullYear() + 1, 0, 1);
    return t + TICK_UNITS.find(([name]) => name === unit)[1];
  }

  // The finest step whose ticks stand at least the tick-gap token apart, and its ticks in the period in view.
  function axisTicks() {
    const room = plotWidth() / cssNumber("--c-history-tick-gap");
    const unit = TICK_UNITS.find(([, width]) => spanWidth() / width <= room) || TICK_UNITS.at(-1);
    const format = new Intl.DateTimeFormat(LOCALE, { timeZone: UTC, ...unit[2] });
    const ticks = [];
    for (let t = floorTo(unit[0], hist.span[0]); t <= hist.span[1]; t = nextTick(unit[0], t)) {
      if (t >= hist.span[0]) ticks.push({ t, label: format.format(t) });
    }
    return { unit: unit[0], ticks };
  }

  function drawAxis(ticks) {
    const axis = $("history-axis");
    const height = cssNumber("--c-history-axis-height");
    const gap = cssNumber(CSS_VAR_S_SPACE_XL) / 2;
    axis.setAttribute(ATTR_VIEWBOX, `0 0 ${plotWidth()} ${height}`);
    clear(axis).append(...ticks.flatMap(({ t, label }) => [
      svgEl(VALUE_LINE, { x1: localX(t), x2: localX(t), y1: height / 2, y2: height }),
      svgEl(SVG_TEXT, { x: localX(t) + gap / 2, y: height / 2 + gap / 2 }, label)]));
  }

  function drawOverview() {
    const svg = $(ID_HISTORY_OVERVIEW);
    const width = svg.clientWidth || plotWidth();
    const height = cssNumber("--c-history-overview-height");
    const [full0, full1] = hist.full;
    const at = (t) => ((t - full0) / (full1 - full0)) * width;
    svg.setAttribute(ATTR_VIEWBOX, `0 0 ${width} ${height}`);
    const ticks = HISTORY.commits.map((c, i) => svgEl(VALUE_LINE, { class: "history-tick", x1: at(commitTime[i]),
      x2: at(commitTime[i]), y1: height * TICK_FROM, y2: height * TICK_TO, stroke: `var(--c-history-${c.kind})` }));
    const inset = cssNumber(CSS_HAIRLINE);
    const window = svgEl(SVG_RECT, { class: "history-window", x: at(hist.span[0]), y: inset, height: height - 2 * inset,
      width: Math.max(1, at(hist.span[1]) - at(hist.span[0])) });
    clear(svg).append(window, ...ticks);                    // the window under the ticks, which stay visible
  }

  // ---- the activity band (RQ-HST-008): commits per day, week or month of the period in view ----
  function bandUnit() {
    const days = spanWidth() / DAY_MS;
    if (days <= BAND_DAY_LIMIT) return "day";
    return days <= BAND_WEEK_LIMIT ? UNIT_WEEK : UNIT_MONTH;
  }

  function drawBand() {
    const band = $("history-band");
    const width = plotWidth();
    const height = cssNumber("--c-history-band-height");
    const unit = bandUnit();
    band.dataset.unit = unit;
    band.setAttribute(ATTR_VIEWBOX, `0 0 ${width} ${height}`);
    const buckets = [];
    for (let t = floorTo(unit, hist.span[0]); t <= hist.span[1]; t = nextTick(unit, t)) buckets.push({ t, end: nextTick(unit, t), counts: {} });
    let b = 0;
    for (const ci of hist.shown) {
      const at = commitTime[ci];
      while (b < buckets.length && buckets[b].end <= at) b += 1;
      if (b < buckets.length && at >= buckets[b].t) {
        const kind = HISTORY.commits[ci].kind;
        buckets[b].counts[kind] = (buckets[b].counts[kind] || 0) + 1;
      }
    }
    const total = (bucket) => BAND_STACK.reduce((sum, kind) => sum + (bucket.counts[kind] || 0), 0);
    const most = Math.max(1, ...buckets.map(total));
    const gap = cssNumber("--c-history-bar-gap");
    const inset = cssNumber(CSS_HAIRLINE);
    const bars = buckets.filter((bucket) => total(bucket)).map((bucket) => {
      const x = localX(bucket.t) + gap;
      const w = Math.max(inset, localX(bucket.end) - localX(bucket.t) - 2 * gap);
      let y = height - inset;
      const parts = BAND_STACK.filter((kind) => bucket.counts[kind]).map((kind) => {
        const h = ((height - 2 * inset) * bucket.counts[kind]) / most;
        y -= h;
        return svgEl(SVG_RECT, { class: `history-bar-${kind}`, x, y, width: w, height: h });
      });
      const lines = [`${unit === "day" ? "" : `${unit[0].toUpperCase()}${unit.slice(1)} of `}${DAY_TEXT.format(bucket.t)}: ${total(bucket)} commits`,
        ...BAND_STACK.filter((kind) => bucket.counts[kind]).map((kind) => `${bucket.counts[kind]} ${KIND_LABEL[kind]}`)];
      const bar = svgEl(SVG_GROUP, { class: "history-bar", tabindex: "0", role: "img", [VALUE_ARIA_LABEL]: lines.join(", ") }, ...parts);
      bar.addEventListener(EVENT_MOUSEOVER, () => showTipLines(bar, lines));
      bar.addEventListener(EVENT_MOUSEOUT, hideHistoryTip);
      bar.addEventListener(EVENT_FOCUS, () => showTipLines(bar, lines));
      bar.addEventListener(EVENT_BLUR, hideHistoryTip);
      return bar;
    });
    clear(band).append(...bars);
  }

  // ---- rows in view ----
  function markRadius(lines) {
    const low = cssNumber("--c-history-mark-min");
    return low + (cssNumber(CSS_MARK_MAX) - low) * Math.sqrt(lines / maxLines);
  }

  function markLabel(row, ci, lines) {
    const commit = HISTORY.commits[ci];
    const people = [commit.author, ...commit.coAuthors].map((i) => HISTORY.people[i].name).join(" with ");
    return `${commit.hash}, ${DATE_TEXT.format(commitTime[ci])}, ${people}: ${lines} lines changed in ${row.label}`;
  }

  function markElement(row, ci, lines, y) {
    const commit = HISTORY.commits[ci];
    const x = localX(commitTime[ci]);
    const r = markRadius(lines);
    const fill = colourOf[commit.author];
    const shape = commit.kind === KIND_AGENT
      ? svgEl(VALUE_PATH, { d: `M${x} ${y - r * DIAMOND_RATIO}L${x + r * DIAMOND_RATIO} ${y}L${x} ${y + r * DIAMOND_RATIO}L${x - r * DIAMOND_RATIO} ${y}Z`, fill })
      : svgEl(SVG_CIRCLE, { cx: x, cy: y, r, fill });
    const agent = commit.coAuthors.find((i) => HISTORY.people[i].kind === KIND_AGENT);
    const ring = commit.kind === KIND_TOGETHER ? svgEl(SVG_CIRCLE, { class: CLASS_RING, cx: x, cy: y,
      r: r + cssNumber(CSS_RING_GAP), stroke: colourOf[agent ?? commit.coAuthors[0] ?? commit.author] }) : null;
    const mark = svgEl(SVG_GROUP, { class: `history-mark${hist.pinned === ci ? " " + IS_PINNED : ""}`, "data-commit": ci,
      "data-kind": commit.kind, "data-lines": lines, tabindex: "0", role: "img", [VALUE_ARIA_LABEL]: markLabel(row, ci, lines) },
    shape, ring);
    mark.addEventListener(EVENT_FOCUS, () => showHistoryTip(mark, row, ci, lines));
    mark.addEventListener(EVENT_BLUR, hideHistoryTip);
    return mark;
  }

  function rowElement(row, index) {
    const height = rowHeight();
    const top = `${index * height}px`;
    if (row.group) {
      return el("div", { class: "history-row is-group", style: { top } },
        el(TAG_SPAN, { class: CLASS_LABEL }, row.label, el(TAG_SPAN, { class: CLASS_COUNT, text: row.count })), el("div"));
    }
    const label = el(TAG_BUTTON, { class: CLASS_LABEL, type: TAG_BUTTON, title: row.title || (row.name ? `${row.label} — ${row.name}` : row.label),
      style: { "--history-depth": row.depth }, on: { [EVENT_CLICK]: () => select(row.key) } },
    el(TAG_SPAN, { class: "history-id", text: row.label }), row.name ? el(TAG_SPAN, { class: CLASS_NAME, text: row.name }) : null,
    el(TAG_SPAN, { class: CLASS_COUNT, text: row.marks.length || "" }));
    const width = plotWidth();
    const strip = svgEl("svg", { class: "history-strip", [ATTR_VIEWBOX]: `0 0 ${width} ${height}` },
      ...hist.ticks.map(({ t }) => svgEl(VALUE_LINE, { class: "history-grid-line", x1: localX(t), x2: localX(t), y1: 0, y2: height })));
    const reach = cssNumber(CSS_MARK_MAX) * DIAMOND_RATIO + cssNumber(CSS_RING_GAP);
    for (const [ci, lines] of row.marks) {
      const x = localX(commitTime[ci]);
      if (x >= -reach && x <= width + reach) strip.append(markElement(row, ci, lines, height / 2));
    }
    return el("div", { class: "history-row", "data-key": row.key, style: { top } }, label, strip);
  }

  function drawRows() {
    const scroller = $(ID_HISTORY_SCROLL);
    const box = $(ID_HISTORY_ROWS);
    const height = rowHeight();
    box.style.height = `${hist.rows.length * height}px`;
    box.dataset.total = String(hist.rows.length);
    const first = Math.max(0, Math.floor(scroller.scrollTop / height) - ROW_OVERSCAN);
    const last = Math.min(hist.rows.length, Math.ceil((scroller.scrollTop + scroller.clientHeight) / height) + ROW_OVERSCAN);
    clear(box).append(...hist.rows.slice(first, last).map((row, i) => rowElement(row, first + i)));
  }

  function historyStatus() {
    const shown = hist.shown.filter((ci) => commitTime[ci] >= hist.span[0] && commitTime[ci] <= hist.span[1]).length;
    const active = hist.rows.filter((r) => !r.group && r.marks.length).length;
    $("history-status").textContent = `${rowCount(active)} with changes · ${commitCount(shown)} in view · `
      + `${DAY_TEXT.format(hist.span[0])} – ${DAY_TEXT.format(hist.span[1])}`;
  }

  function drawHistory() {
    if (!hist.built || $("view-history").hidden) return;
    const gutter = `${$(ID_HISTORY_SCROLL).offsetWidth - $(ID_HISTORY_SCROLL).clientWidth}px`;   // the rows' scroll bar
    for (const row of document.querySelectorAll(".history-band-row, .history-axis-row, .history-overview-row")) row.style.paddingRight = gutter;
    const { ticks } = axisTicks();
    hist.ticks = ticks;
    drawAxis(ticks);
    drawBand();
    drawOverview();
    drawRows();
    historyStatus();
  }

  // ---- tooltip and pinned card ----
  function tipLines(row, ci, lines) {
    const commit = HISTORY.commits[ci];
    const person = (i) => `${HISTORY.people[i].name} (${HISTORY.people[i].kind})`;
    return [`${commit.hash} · ${DATE_TEXT.format(commitTime[ci])}`,
      person(commit.author) + (commit.coAuthors.length ? ` with ${commit.coAuthors.map(person).join(", ")}` : ""),
      commit.subject, `${lines} lines changed in ${row.title || row.label}`];
  }

  const linesTip = (lines) => ({ head: lines[0], lines: lines.slice(1) });
  const showTipLines = (target, lines) => showRichTip(target, linesTip(lines));
  const hideHistoryTip = () => hideRichTip();

  function showHistoryTip(target, row, ci, lines) {
    showTipLines(target, tipLines(row, ci, lines));
  }

  // Every element, file and function the commit changed, from the interventions (built once, on the first pin).
  let changedBy = null;
  function changedIn(ci) {
    if (!changedBy) {
      changedBy = new Map();
      const add = (key, list) => list.forEach(([c]) => { if (!changedBy.has(c)) changedBy.set(c, []); changedBy.get(c).push(key); });
      Object.entries(HISTORY.interventions.elements).forEach(([id, list]) => add(id, list));
      Object.entries(HISTORY.interventions.files).forEach(([path, list]) => add(FILE_PREFIX + path, list));
    }
    return (changedBy.get(ci) || []).filter((key) => nodes.has(key));
  }

  function pinCommit(row, ci, lines) {
    const commit = HISTORY.commits[ci];
    hist.pinned = ci;
    const card = $(ID_HISTORY_CARD);
    const changed = changedIn(ci);
    clear(card).append(
      el("div", { class: "history-card-head" }, el(TAG_SPAN, { class: "history-card-hash", text: commit.hash }),
        el(TAG_SPAN, { class: CLASS_CARD_MUTED, text: DATE_TEXT.format(commitTime[ci]) }),
        el(TAG_BUTTON, { class: "button history-card-close", type: TAG_BUTTON, title: "Close this commit's card", text: "Close",
          on: { [EVENT_CLICK]: unpinCommit } })),
      el("div", { class: "history-card-subject", text: commit.subject }),
      el("div", { class: CLASS_CARD_LIST }, personTag(commit.author), ...commit.coAuthors.map(personTag)),
      el("div", { class: CLASS_CARD_MUTED, text: `${KIND_LABEL[commit.kind]} · ${lines} lines changed in ${row.label}` }),
      changed.length ? el("div", { class: CLASS_CARD_MUTED, text: `Changed by this commit (${changed.length}):` }) : null,
      changed.length ? el("div", { class: CLASS_CARD_LIST }, ...changed.map((key) => idButton(key, true))) : null);
    card.hidden = false;
    for (const mark of $(ID_HISTORY_ROWS).querySelectorAll(CLASS_MARK)) mark.classList.toggle(IS_PINNED, Number(mark.dataset.commit) === ci);
  }

  function unpinCommit() {
    hist.pinned = null;
    $(ID_HISTORY_CARD).hidden = true;
    for (const mark of $(ID_HISTORY_ROWS).querySelectorAll(CLASS_MARK)) mark.classList.remove(IS_PINNED);
  }

  const rowOfMark = (mark) => hist.rows.find((r) => r.key === mark.closest(".history-row").dataset.key);

  // ---- interactions: hover, click, wheel, drag, keyboard ----
  function setupHistory() {
    const rowsBox = $(ID_HISTORY_ROWS);
    rowsBox.addEventListener(EVENT_MOUSEOVER, (event) => {
      const mark = event.target.closest(CLASS_MARK);
      if (!mark) return;
      scheduleRichTip(mark, () => linesTip(tipLines(rowOfMark(mark), Number(mark.dataset.commit), Number(mark.dataset.lines))),
        cssNumber(CSS_TIP_DELAY));
    });
    rowsBox.addEventListener(EVENT_MOUSEOUT, (event) => { if (event.target.closest(CLASS_MARK)) hideHistoryTip(); });
    const pinFrom = (mark) => pinCommit(rowOfMark(mark), Number(mark.dataset.commit), Number(mark.dataset.lines));
    rowsBox.addEventListener(EVENT_CLICK, (event) => { const mark = event.target.closest(CLASS_MARK); if (mark) pinFrom(mark); });
    rowsBox.addEventListener(EVENT_KEYDOWN, (event) => {
      const mark = event.target.closest(CLASS_MARK);
      if (mark && (event.key === KEY_ENTER || event.key === " ")) { event.preventDefault(); pinFrom(mark); }
    });
    $(ID_HISTORY_SCROLL).addEventListener("scroll", () => { if (hist.built) drawRows(); });
    const plot = $("history-plot");
    plot.addEventListener("wheel", (event) => {
      if (event.clientX < plotLeft()) return;                       // over the labels, the wheel scrolls the rows
      event.preventDefault();
      zoomAround(timeAt(event.clientX), zoomStep() ** (-event.deltaY / WHEEL_NOTCH));
    }, { passive: false });
    let drag = null;
    $(ID_HISTORY_SCROLL).addEventListener(EVENT_POINTERDOWN, (event) => {
      if (event.clientX < plotLeft() || event.target.closest(CLASS_MARK)) return;
      drag = { x: event.clientX, start: hist.span[0] };
      event.currentTarget.setPointerCapture(event.pointerId);
    });
    $(ID_HISTORY_SCROLL).addEventListener(EVENT_POINTERMOVE, (event) => {
      if (drag) setSpan(drag.start - ((event.clientX - drag.x) / plotWidth()) * spanWidth(), spanWidth());
    });
    for (const type of [EVENT_POINTERUP, EVENT_POINTERCANCEL]) $(ID_HISTORY_SCROLL).addEventListener(type, () => { drag = null; });
    const overview = $(ID_HISTORY_OVERVIEW);
    const overviewTime = (event) => {
      const box = overview.getBoundingClientRect();
      return hist.full[0] + ((event.clientX - box.left) / box.width) * (hist.full[1] - hist.full[0]);
    };
    let sliding = false;
    overview.addEventListener(EVENT_POINTERDOWN, (event) => {
      sliding = true;
      overview.setPointerCapture(event.pointerId);
      setSpan(overviewTime(event) - spanWidth() / 2, spanWidth());
    });
    overview.addEventListener(EVENT_POINTERMOVE, (event) => { if (sliding) setSpan(overviewTime(event) - spanWidth() / 2, spanWidth()); });
    for (const type of [EVENT_POINTERUP, EVENT_POINTERCANCEL]) overview.addEventListener(type, () => { sliding = false; });
    plot.addEventListener(EVENT_KEYDOWN, (event) => {
      const centre = (hist.span[0] + hist.span[1]) / 2;
      const keys = { "+": () => zoomAround(centre, zoomStep()), "=": () => zoomAround(centre, zoomStep()),
        "-": () => zoomAround(centre, 1 / zoomStep()), 0: fitHistory,
        [KEY_ARROWLEFT]: () => panBy(-PAN_FRACTION), [KEY_ARROWRIGHT]: () => panBy(PAN_FRACTION) };
      if (keys[event.key] && !event.target.closest(`.${CLASS_LABEL}`)) { event.preventDefault(); keys[event.key](); }
    });
    $("history-fit").addEventListener(EVENT_CLICK, fitHistory);
    $(ID_HISTORY_ANGLE).addEventListener(EVENT_CLICK, (event) => {
      const button = event.target.closest("[data-angle]");
      if (button) setAngle(button.dataset.angle, hist.grouping);
    });
    $(ID_HISTORY_GROUPING).addEventListener(EVENT_CLICK, (event) => {
      const button = event.target.closest("[data-grouping]");
      if (button) setAngle(hist.angle, button.dataset.grouping);
    });
    $(ID_HISTORY_KIND).addEventListener(EVENT_CLICK, (event) => {
      const button = event.target.closest("[data-kind]");
      if (button) { hist.kind = button.dataset.kind; applyFilters(); }
    });
    $(ID_SHOW_EMPTY).addEventListener(EVENT_CHANGE, (event) => { hist.showEmpty = event.target.checked; applyFilters(); });
    $("history-reset").addEventListener(EVENT_CLICK, resetFilters);
    renderPeopleChips();
    new ResizeObserver(() => drawHistory()).observe(plot);
    renderHistoryLegend();
    renderHistoryLimits();
  }

  function setAngle(angle, grouping) {
    hist.angle = angle;
    hist.grouping = grouping;
    for (const b of $(ID_HISTORY_ANGLE).querySelectorAll(TAG_BUTTON)) b.setAttribute(VALUE_ARIA_PRESSED, String(b.dataset.angle === angle));
    for (const b of $(ID_HISTORY_GROUPING).querySelectorAll(TAG_BUTTON)) b.setAttribute(VALUE_ARIA_PRESSED, String(b.dataset.grouping === grouping));
    $(ID_HISTORY_GROUPING).hidden = angle !== ANGLE_CODE;
    hist.baseRows = historyRows();
    $(ID_HISTORY_SCROLL).scrollTop = 0;
    applyFilters();
  }

  // The shapes of the marks, drawn as the timeline draws them, at the largest mark's size (RQ-HST-014).
  function renderHistoryLegend() {
    const r = cssNumber(CSS_MARK_MAX);
    const ring = r + cssNumber(CSS_RING_GAP);
    const reach = Math.max(r * DIAMOND_RATIO, ring + cssNumber("--s-stroke-medium"));
    const sample = (kind, ...shapes) => el(TAG_SPAN, { class: CLASS_LEGEND_ITEM },
      svgEl("svg", { [ATTR_VIEWBOX]: `${-reach} ${-reach} ${2 * reach} ${2 * reach}`, [ATTR_ARIA_HIDDEN]: VALUE_TRUE }, ...shapes),
      KIND_LABEL[kind]);
    const neutral = "var(--s-text-subtle)";               // the shapes alone: the colours are the identities'
    const d = r * DIAMOND_RATIO;
    clear($("history-legend")).append(
      sample(KIND_HUMAN, svgEl(SVG_CIRCLE, { r, fill: neutral })),
      sample(KIND_AGENT, svgEl(VALUE_PATH, { d: `M0 ${-d}L${d} 0L0 ${d}L${-d} 0Z`, fill: neutral })),
      sample(KIND_TOGETHER, svgEl(SVG_CIRCLE, { r, fill: neutral }),
        svgEl(SVG_CIRCLE, { class: CLASS_RING, r: ring, fill: VALUE_NONE, stroke: neutral })),
      el(TAG_SPAN, { class: CLASS_LEGEND_ITEM, text: "Colour: the author · size: the lines changed · wheel over the marks to zoom, drag to pan" }));
  }

  // RQ-HST-001, RQ-HST-012: the limits applied, and a cut history said as such.
  function renderHistoryLimits() {
    const limits = HISTORY.limits;
    const parts = [`${limits.commits} commits`];
    if (limits.since) parts.push(`since ${limits.since}`);
    if (limits.depth) parts.push(`last ${limits.depth}`);
    if (limits.shallow) parts.push("cut: shallow clone");
    const text = parts.join(" · ");
    Object.assign($("history-limits"), { textContent: text, title: `History read: ${text}` });
  }

  const historyView = {
    show() {
      if (!HISTORY) return;
      if (!hist.built) {
        hist.built = true;
        hist.full = fullSpan();
        hist.span = [...hist.full];
        hist.baseRows = historyRows();
        applyFilters();
        return;
      }
      drawHistory();
    },
    span: () => [...hist.span], setSpan, timeAt, xOf, state: hist, redraw: drawHistory,
  };
  if (HISTORY) {
    document.querySelector(`.tab[data-view=${HISTORY_VIEW}]`).hidden = false;
    setupHistory();
    renderHistorySidebar();
  }

  // ---- detail panel -------------------------------------------------------------------------------------------
  function renderDetail() {
    const panel = clear($("detail"));
    const key = state.selected;
    if (key !== pressedFor) { pressedTags.clear(); pressedFor = key; }
    if (!key) {
      panel.append(el("div", { class: "detail-empty" },
        el("span", { class: "detail-empty-title", text: "No element selected" }),
        el("span", { text: "Search an ID, a title or a file, or click any element of the matrix, the quality view or the graph: its links appear here, grouped by type." })));
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
        n.kind === KIND_UNDEFINED ? el("span", { class: "badge badge-error", text: "Not in the index" }) : null),
      n.doc ? el("div", { class: "detail-location", text: `${n.doc}:${n.first}-${n.last}` }) : null,
      el("div", { class: "detail-actions" },
        el("button", { class: "button button-primary", type: "button", text: "Show in graph",
          title: "Open the graph on this element and its links", on: { click: () => showView("graph") } }),
        el("button", { class: "button", type: "button", text: "Copy ID",
          title: "Copy this ID (or name) to the clipboard", on: { click: () => copy(n.label) } }),
        HISTORY && n.kind !== KIND_UNDEFINED ? el(TAG_BUTTON, { class: "button", type: TAG_BUTTON, "data-action": HISTORY_VIEW, text: "History",
          title: "Open the History tab on this element: who changed it, and its code, over time",
          on: { [EVENT_CLICK]: () => scopeHistory(key) } }) : null));
    const groups = linksByType(key);
    const ordered = [...groups.keys()].sort((a, b) => typeOrder(a) - typeOrder(b));
    const summary = el("div", { class: "detail-summary" }, ordered.length ? ordered.map((t) =>
      groupTag(t, t, `${plural(t, groups.get(t).size)} ${groups.get(t).size}`))
      : el("span", { class: "badge badge-error", text: "No link" }));
    const callSections = n.type === "FN" ? callGroups(calls.index.get(key)) : [];
    summary.append(...callSections.map((s) => s.badge));
    if (CALL_GRAPH && n.type === "RQ" && !groups.has("FN")) summary.append(noFunctionBadge(key));   // RQ-TRC-041
    panel.append(detailBand(n.type, head, summary),
      el("div", { class: "detail-body" }, ...callSections.map((s) => s.section), ...ordered.map((t) => linkGroup(t, groups.get(t)))));
    applyTagFilter();
  }

  // RQ-TRC-055, DEC-TRC-030: a tag is a toggle that shows only its group; the pressed tags belong to one selection.
  const pressedTags = new Set();
  let pressedFor = null;

  function groupTag(group, type, text) {
    const tag = el("button", { class: `badge badge-neutral tag t-${type}`, type: "button", "data-group": group,
      "aria-pressed": String(pressedTags.has(group)), title: "Show only this group of links; click again to show them all" },
      el("span", { class: `dot t-${type}` }), text);
    tag.addEventListener("click", () => {
      if (pressedTags.has(group)) pressedTags.delete(group); else pressedTags.add(group);
      tag.setAttribute("aria-pressed", String(pressedTags.has(group)));
      applyTagFilter();
    });
    return tag;
  }

  function grouped(group, section) {
    section.dataset.group = group;
    return section;
  }

  function applyTagFilter() {
    for (const section of $("detail").querySelectorAll(".detail-body .group")) {
      section.hidden = pressedTags.size > 0 && !pressedTags.has(section.dataset.group);
    }
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
        badge: groupTag(title.toLowerCase(), "FN", `${title} ${list.length}`),
        section: grouped(title.toLowerCase(), callGroup(title, rel, list.toSorted(byLabel))),
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
    const summary = el("div", { class: "detail-summary" }, groupTag("inner", "FN", `Inner scopes ${inner.length}`),
      groupTag("FN", "FN", `${plural("FN", members.length)} ${members.length}`), groupTag("RQ", "RQ", `${plural("RQ", cited.length)} ${cited.length}`),
      groupTag("callers", "FN", `Callers ${callers.length}`), groupTag("callees", "FN", `Callees ${callees.length}`));
    panel.append(detailBand("FN", head, summary), el("div", { class: "detail-body" }, ...[
      box.parent ? listGroup("Enclosing scope", [box.parent], keyItem) : null,              // RQ-TRC-048
      inner.length ? grouped("inner", listGroup("Inner scopes", inner, keyItem)) : null,
      grouped("FN", listGroup(plural("FN", own.length), own.sort(byKeyLabel), keyItem)),
      grouped("callers", listGroup("Callers by scope", callers, boxCallItem("called by"))),
      grouped("callees", listGroup("Callees by scope", callees, boxCallItem("calls"))),
      grouped("RQ", listGroup(plural("RQ", cited.length), cited, keyItem, "RQ"))].filter(Boolean)));
    applyTagFilter();
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
      el("span", { class: "link-rel", text: `${rel} · ${count} ${count === 1 ? VALUE_CALL_SITE : VALUE_CALL_SITES}` }));
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
    return el("section", { class: "group", "data-group": type },
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
    if (view === HISTORY_VIEW) historyView.show();
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
    FILE_PREFIX, renderQuality, historyView };
  renderHeader();
  renderFilters();
  renderOverview();
  renderMatrix();
  renderQuality();
  renderDetail();
  setupPanels();
  const initial = hashKey();
  if (initial) { select(initial, { fromHistory: true }); showView("graph"); } else showView("overview");
  const readyMs = Math.round(performance.now());   // since the navigation started, the page's parsing included
  Object.assign(document.documentElement.dataset, { ready: "true", readyMs: String(readyMs) });   // RQ-TRC-037
  console.info(`agnos-trace: interactive ${readyMs} ms after opening, script ${Math.round(readyMs - STARTED)} ms`);
})();
