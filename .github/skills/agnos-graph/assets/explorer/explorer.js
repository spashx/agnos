/* Graph explorer page script (FTR-TRC-014; ADR-TRC-025: DEC-TRC-084, DEC-TRC-088, DEC-TRC-089, DEC-TRC-091).
   Builds one view model from every block of agnos-graph.json (RQ-TRC-146) and shows it in the tables and the detail panel
   (RQ-TRC-149, RQ-TRC-154), between resizable panels (RQ-TRC-148). Reads the graph from window.AGNOS_GRAPH, set by
   agnos-graph.data.js, or from a file the reader drops or chooses (RQ-TRC-145). Every visual value comes from the design
   tokens (DEC-TRC-010); every text is English (RQ-TRC-155). Test hooks: window.agnosExplorer. */
(() => {
  "use strict";

  // RQ-TRC-067: a literal written more than once is a named constant.
  const KIND_CONTAINS = "contains";
  const KIND_REFS = "refs";
  const KIND_UNDEFINED = "undefined";
  const TYPE_SECTION = "SEC";
  const TYPE_FILE = "FILE";
  const TYPE_UNDEFINED = "UNDEFINED";
  const ORIGIN_EDGES = "edges";
  const ORIGIN_SECTIONS = "sections";
  const ORIGIN_CALL_GRAPH = "callGraph";
  const TYPE_FUNCTION = "FN";
  const KIND_CALL = "call";
  const KIND_CODE = "code";
  const VIEW_GRAPH = "graph";
  const VIEW_NODES = "nodes";
  const VIEW_RELATIONS = "relations";
  const DEFAULT_VIEW = VIEW_GRAPH;
  const LINK_KEY_SEPARATOR = "\u0000";
  const NO_VALUE = "—";
  const ASCENDING = "ascending";
  const DESCENDING = "descending";
  const ATTR_SELECTED = "aria-selected";
  const ATTR_SORT = "aria-sort";
  const CLASS_ACTIVE = "active";
  const CLASS_DRAGGING = "dragging";
  const COMMIT_SHORT = 10;
  const ROW_TAG = "tr";
  const KEY_ENTER = "Enter";
  const KEY_LEFT = "ArrowLeft";
  const KEY_RIGHT = "ArrowRight";
  const ID_FACETS = "facets";
  const ID_DETAIL = "detail";
  const VAR_FACETS = "--facets-size";
  const VAR_DETAIL = "--detail-size";
  const TOKEN_STEP = "--c-splitter-step";
  const TOKEN_MAIN_MIN = "--c-main-min-width";
  const TOKEN_SPLITTER = "--c-splitter-width";
  const LIMITS = {                                  // RQ-TRC-148: each side panel's bounds, from the tokens
    [ID_FACETS]: { min: "--c-sidebar-min-width", max: "--c-sidebar-max-width", variable: VAR_FACETS },
    [ID_DETAIL]: { min: "--c-detail-min-width", max: "--c-detail-max-width", variable: VAR_DETAIL },
  };
  const NODE_COLUMNS = ["id", "type", "tri", "status", "title", "location", "incoming", "outgoing"];
  const RELATION_COLUMNS = ["source", "target", "kind", "field", "line", "proof"];
  const MESSAGE_NO_GRAPH = "No graph loaded: open or drop an agnos-graph.json file.";
  const UNIT_PX = "px";
  const EVENT_CLICK = "click";
  const EVENT_KEYDOWN = "keydown";
  const EVENT_POINTER_MOVE = "pointermove";
  const EVENT_POINTER_UP = "pointerup";
  const ID_MESSAGE = "load-message";
  const ID_NODE_TABLE = "node-table";
  const ID_RELATION_TABLE = "relation-table";
  const SELECTOR_TAB = ".tab";
  // RQ-TRC-150, RQ-TRC-154, DEC-TRC-090: the graph view
  const TYPE_ORDER = ["FTR", "RQ", "ADR", "DEC", "PLAN", "TASK", TYPE_SECTION, TYPE_FILE, "FN", TYPE_UNDEFINED];
  const CLASS_HIDDEN = "hidden";
  const CLASS_PICKED = "picked";
  const DATA_COLOUR = "colour";
  const EVENT_DRAG_FREE = "dragfree";
  const TOKEN_ZOOM_STEP = "--c-graph-zoom-step";
  const MESSAGE_NO_LIBRARY = "Cytoscape.js could not be loaded from cdnjs: the graph view needs the network once; the tables work without it.";
  const ACTION_HIDE = "hide";
  const ACTION_ISOLATE = "isolate";
  const ACTION_WIDEN = "widen";
  const SELECTOR_NODE = "node";
  // RQ-TRC-151, RQ-TRC-152, DEC-TRC-092: facets and the query language
  const FACET_NODES = "nodes";
  const FACET_RELATIONS = "relations";
  const FACET_TYPE = "type";
  const NONE = "(none)";
  const KEY_CITES = "cites";
  const KEY_CITED_BY = "cited-by";
  const OP_CONTAINS = "contains";
  const OP_EQUALS = "equals";
  const EDGE_RE = /^edge(\s+|$)/;
  const KEY_RE = /^[A-Za-z][\w-]*/;
  const LINKED_RE = /^([^[]*)(?:\[(.*)\])?$/;
  const EDGE_KEYS = ["kind", "field", "from", "to", "source", "target"];
  const ID_QUERY = "query";
  const ID_QUERY_MESSAGE = "query-message";
  const CLASS_ERROR = "error";
  const STORE_KEY = "agnos-graph-explorer.saved-queries";   // RQ-TRC-153, DEC-TRC-093
  const EXPORT_NAME = "agnos-graph-explorer-queries.json";
  const EDIT_NEW = "new";
  const ID_SAVED = "saved-queries";
  const FACETS = [
    { key: FACET_TYPE, title: "Node types", of: FACET_NODES, values: (n) => [n.type] },
    { key: "tri", title: "Trigrams", of: FACET_NODES, values: (n) => [n.props.tri || NONE] },
    { key: "status", title: "Status", of: FACET_NODES, values: (n) => [n.props.status || NONE] },
    { key: "kind", title: "Relation kinds", of: FACET_RELATIONS, values: (r) => [r.kind] },
    { key: "field", title: "Link fields", of: FACET_RELATIONS, values: (r) => fieldsOf(r) },
  ];
  const ID_HIDDEN_LIST = "hidden-list";
  const TOKEN_NODE_SIZE = "--c-graph-node-size";

  const $ = (id) => document.getElementById(id);
  const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
  const tokenNumber = (name) => parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);     // code-point order, as the graph file is sorted

  const state = { model: null, view: DEFAULT_VIEW, selected: null, sort: { [VIEW_NODES]: null, [VIEW_RELATIONS]: null },
                  hiddenNodes: new Set(), isolate: null,                             // RQ-TRC-154: what every view hides
                  off: { type: new Set(), tri: new Set(), status: new Set(), kind: new Set(), field: new Set() },   // RQ-TRC-151
                  queryNodes: null, queryRelations: null };                          // RQ-TRC-152
  let cy = null;                                                                       // DEC-TRC-090: the graph view

  // ---- visibility, shared by every view (RQ-TRC-151, RQ-TRC-152, RQ-TRC-154) ----------------------------------
  const facetAllows = (facet, item) => facet.values(item).some((v) => !state.off[facet.key].has(v));
  const isShown = (node) => FACETS.filter((f) => f.of === FACET_NODES).every((f) => facetAllows(f, node))
    && !state.hiddenNodes.has(node.id) && (!state.isolate || state.isolate.has(node.id))
    && (!state.queryNodes || state.queryNodes.has(node.id));
  const isRelationShown = (relation) => isShown(state.model.nodes.get(relation.source))
    && isShown(state.model.nodes.get(relation.target))
    && FACETS.filter((f) => f.of === FACET_RELATIONS).every((f) => facetAllows(f, relation))
    && (!state.queryRelations || state.queryRelations.has(relation));

  function neighbours(id) {
    /* The node and every node one relation away from it, whatever is shown (RQ-TRC-154). */
    const node = state.model.nodes.get(id);
    return new Set([id, ...node.outgoing.map((r) => r.target), ...node.incoming.map((r) => r.source)]);
  }

  // ---- view model (RQ-TRC-146, DEC-TRC-089) -------------------------------------------------------------------
  function linkFields(graph) {
    /* The field of each proof line of a refs edge, from the links block: source + target -> line -> field. */
    const fields = new Map();
    for (const [source, target, rows] of graph.links || []) {
      fields.set(source + LINK_KEY_SEPARATOR + target, new Map(rows.map(([line, field]) => [line, field])));
    }
    return fields;
  }

  // RQ-TRC-146, DEC-TRC-089 (TASK-TRC-137): the call graph block, in agnos-graph's format (callGraph of graph-format.md)
  const functionId = (graph, index) => {
    const [file, , , name, , , suffix] = graph.callGraph.functions[index];
    return `${graph.files[file].path}::${name}${suffix ? `#${suffix}` : ""}`;
  };

  function addCallGraph(graph, add, relate) {
    /* Functions as FN nodes held by their file, calls as call relations, and the IDs a function cites as code relations. */
    const block = graph.callGraph;
    if (!block) return;
    block.functions.forEach(([file, first, last, name, language, text, , scope], i) => {
      add(functionId(graph, i), TYPE_FUNCTION, { name, file: graph.files[file].path, first, last, firstLine: text,
                                                  language: block.languages[language], scope: scope < 0 ? null : block.scopes[scope][0] });
      relate(graph.files[file].path, functionId(graph, i), KIND_CONTAINS, [], ORIGIN_CALL_GRAPH);
    });
    const calls = block.calls;
    let i = 0;
    let caller = 0;
    while (i < calls.length) {
      caller += calls[i];
      const count = calls[i + 1];
      i += 2;
      for (let k = 0; k < count; k += 1) {
        const callee = caller + calls[i];
        const lineCount = Math.floor(calls[i + 1] / 2);
        const first = block.functions[caller][1];
        const lines = calls.slice(i + 2, i + 2 + lineCount).map((offset) => [first + offset, calls[i + 1] % 2 ? "ambiguous" : ""]);
        relate(functionId(graph, caller), functionId(graph, callee), KIND_CALL, lines, ORIGIN_CALL_GRAPH);
        i += 2 + lineCount;
      }
    }
    for (const [fn, id, lines] of block.ids) relate(functionId(graph, fn), id, KIND_CODE, lines.map((l) => [l, ""]), ORIGIN_CALL_GRAPH);
  }

  function addHistory(graph, nodes) {
    /* Each node's commits as "hash date author (lines)", and each delivered task's delivery row, as properties. */
    const history = graph.history;
    if (!history) return;
    const commit = ([index, lines]) => {
      const c = history.commits[index];
      return `${c.hash} ${c.date} ${history.people[c.author].name} (${lines} lines) ${c.subject}`;
    };
    for (const [scope, key] of [["elements", (id) => id], ["files", (path) => path],
                                ["functions", (index) => functionId(graph, Number(index))]]) {
      for (const [id, rows] of Object.entries((history.interventions || {})[scope] || {})) {
        const node = nodes.get(key(id));
        if (node) node.props.history = rows.map(commit);
      }
    }
    for (const [id, tier, retiered, index, lines, type, reworked, reason] of (graph.delivery || {}).tasks || []) {
      if (nodes.has(id)) {
        nodes.get(id).props.delivery = { tier, retiered, commit: history.commits[index].hash, lines, type, reworked, reason };
      }
    }
  }

  function buildModel(graph) {
    /* Nodes: elements, sections, scanned files; relations: edges with their link fields, sections' own relations. */
    const nodes = new Map();
    const relations = [];
    const add = (id, type, props) => { nodes.set(id, { id, type, props, incoming: [], outgoing: [] }); };
    for (const element of graph.elements) {
      add(element.id, element.kind === KIND_UNDEFINED ? TYPE_UNDEFINED : element.type, { ...element });
    }
    for (const section of graph.sections || []) {
      const { refs, ...props } = section;
      add(section.id, TYPE_SECTION, props);
    }
    for (const file of graph.files || []) add(file.path, TYPE_FILE, { ...file });
    for (const [id, task] of Object.entries(graph.tasks || {})) {
      if (nodes.has(id)) Object.assign(nodes.get(id).props, task);
    }
    const fields = linkFields(graph);
    const relate = (source, target, kind, proofs, origin) => {
      const lineFields = kind === KIND_REFS ? fields.get(source + LINK_KEY_SEPARATOR + target) : null;
      relations.push({ source, target, kind, origin,
                       proofs: proofs.map(([line, text]) => ({ line, text, field: lineFields ? lineFields.get(line) || null : null })) });
    };
    for (const [source, target, kind, proofs] of graph.edges || []) relate(source, target, kind, proofs, ORIGIN_EDGES);
    for (const section of graph.sections || []) {
      relate(section.parent, section.id, KIND_CONTAINS, [], ORIGIN_SECTIONS);
      for (const [target, proofs] of section.refs) relate(section.id, target, KIND_REFS, proofs, ORIGIN_SECTIONS);
    }
    addCallGraph(graph, add, relate);
    addHistory(graph, nodes);
    for (const relation of relations) {
      for (const end of [relation.source, relation.target]) {
        if (!nodes.has(end)) add(end, TYPE_UNDEFINED, { id: end, kind: KIND_UNDEFINED });
      }
      nodes.get(relation.source).outgoing.push(relation);
      nodes.get(relation.target).incoming.push(relation);
    }
    return { graph, nodes, relations };
  }

  // ---- shared cells (RQ-TRC-147) ------------------------------------------------------------------------------
  const typeLabel = (type) => `<span class="type-label" data-type="${escapeHtml(type)}">${escapeHtml(type)}</span>`;
  const swatch = (type) => `<span class="swatch" data-type="${escapeHtml(type)}" aria-hidden="true"></span>`;
  const fieldOf = (relation) => {
    const named = [...new Set(relation.proofs.map((p) => p.field).filter(Boolean))];
    return named.length ? named.join(", ") : NO_VALUE;
  };
  // RQ-TRC-151: the facet values of a relation's fields, NONE for a relation without one
  const fieldsOf = (relation) => {
    const named = [...new Set(relation.proofs.map((p) => p.field).filter(Boolean))];
    return named.length ? named : [NONE];
  };
  const location = (props) => (props.doc ? `${props.doc}${props.first ? `:${props.first}-${props.last}` : ""}` : NO_VALUE);

  // ---- header and facets panel (RQ-TRC-145) -------------------------------------------------------------------
  function renderHeader() {
    const { graph, nodes, relations } = state.model;
    const meta = graph.meta || {};
    const commit = meta.commit ? ` · commit <code>${escapeHtml(meta.commit.slice(0, COMMIT_SHORT))}</code>` : "";
    $("graph-meta").innerHTML = `${escapeHtml(meta.generatedAt || NO_VALUE)}${commit} · ${graph.elements.length} elements · `
      + `${nodes.size} nodes · ${relations.length} relations`;
    const summary = [["Elements", graph.elements.length], ["Sections", (graph.sections || []).length],
                     ["Files", (graph.files || []).length], ["Nodes", nodes.size], ["Relations", relations.length]];
    $("graph-summary").innerHTML = summary.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
    renderFacets();
  }

  // ---- facets (RQ-TRC-151) ------------------------------------------------------------------------------------
  function facetCounts(facet) {
    /* Each value of the facet and its number of nodes or relations in the loaded graph. */
    const items = facet.of === FACET_NODES ? [...state.model.nodes.values()] : state.model.relations;
    const counts = new Map();
    for (const item of items) for (const value of facet.values(item)) counts.set(value, (counts.get(value) || 0) + 1);
    return [...counts].sort((a, b) => compare(a[0], b[0]));
  }

  function renderFacets() {
    $("facet-list").innerHTML = FACETS.map((facet) => {
      const values = facetCounts(facet).map(([value, n]) => `<li><label><input type="checkbox" value="${escapeHtml(value)}"`
        + `${state.off[facet.key].has(value) ? "" : " checked"}>${facet.key === FACET_TYPE ? `${swatch(value)}${typeLabel(value)}`
        : `<span>${escapeHtml(value)}</span>`}<span class="count">${n}</span></label></li>`).join("");
      return `<fieldset class="facet" id="facet-${facet.key}" data-facet="${facet.key}"><legend class="panel-title">${facet.title}</legend>`
        + `<ul class="facet-values">${values}</ul></fieldset>`;
    }).join("");
  }

  // ---- query language (RQ-TRC-152, DEC-TRC-092) ---------------------------------------------------------------
  function parseQuery(text) {
    /* {edge, terms: [{neg, key, op, values, type, field}]} or {error}: space-separated terms, key:value, key:a,b,
       key:!value, key:~text, cites:TYPE[field], cited-by:TYPE[field], each negated by a leading "!". */
    let rest = text.trim();
    const edge = EDGE_RE.test(rest);
    if (edge) rest = rest.replace(EDGE_RE, "");
    const terms = [];
    let i = 0;
    while (i < rest.length) {
      if (/\s/.test(rest[i])) { i += 1; continue; }
      const start = i;
      const neg = rest[i] === "!";
      if (neg) i += 1;
      const key = (KEY_RE.exec(rest.slice(i)) || [""])[0];
      i += key.length;
      if (!key || rest[i] !== ":") return { error: `cannot read "${rest.slice(start).split(/\s/)[0]}": a term is key:value` };
      const read = readValue(rest, i + 1);
      if (read.end < 0) return { error: `cannot read "${rest.slice(start)}": a quote is not closed` };
      i = read.end;
      const raw = rest.slice(start, i);
      if (!read.value) return { error: `cannot read "${raw}": no value after ":"` };
      terms.push(termOf(neg, key, read.value, raw));
    }
    return { edge, terms };
  }

  function readValue(text, at) {
    /* A term's value from at: quoted up to its closing quote, else up to a blank, a [bracket] read whole; end -1 when a
       quote is not closed. */
    if (text[at] === "\"") {
      const end = text.indexOf("\"", at + 1);
      return end < 0 ? { value: "", end: -1 } : { value: text.slice(at + 1, end), end: end + 1 };
    }
    let i = at;
    while (i < text.length && !/\s/.test(text[i])) {
      const close = text[i] === "[" ? text.indexOf("]", i) : -1;
      i = close > 0 ? close + 1 : i + 1;
    }
    return { value: text.slice(at, i), end: i };
  }

  function termOf(neg, key, value, raw) {
    if (key === KEY_CITES || key === KEY_CITED_BY) {
      const [, type, field] = LINKED_RE.exec(value);
      return { neg, key, raw, type, field: field || null };
    }
    if (value.startsWith("~")) return { neg, key, raw, op: OP_CONTAINS, values: [value.slice(1).toLowerCase()] };
    if (value.startsWith("!")) return { neg: !neg, key, raw, op: OP_EQUALS, values: value.slice(1).split(",") };
    return { neg, key, raw, op: OP_EQUALS, values: value.split(",") };
  }

  function valuesOf(node, key) {
    if (key === FACET_TYPE) return [node.type];
    const value = node.props[key];
    if (Array.isArray(value)) return value.map(String);
    return [value === undefined || value === null ? "" : String(value)];
  }

  const matches = (term, values) => (term.op === OP_CONTAINS
    ? values.some((v) => v.toLowerCase().includes(term.values[0])) : values.some((v) => term.values.includes(v)));

  function linkedBy(relations, end, term) {
    return relations.some((r) => (!term.type || state.model.nodes.get(r[end]).type === term.type)
      && (!term.field || r.proofs.some((p) => p.field === term.field)));
  }

  function nodeMeets(node, term) {
    let met;
    if (term.key === KEY_CITES) met = linkedBy(node.outgoing, "target", term);
    else if (term.key === KEY_CITED_BY) met = linkedBy(node.incoming, "source", term);
    else met = matches(term, valuesOf(node, term.key));
    return term.neg ? !met : met;
  }

  function relationMeets(relation, term) {
    const typeOf = (id) => state.model.nodes.get(id).type;
    const values = { kind: [relation.kind], field: fieldsOf(relation), from: [typeOf(relation.source)], to: [typeOf(relation.target)],
                     source: [relation.source], target: [relation.target] }[term.key];
    const met = matches(term, values);
    return term.neg ? !met : met;
  }

  function runQuery(text) {
    /* Applies the query to every view, or names the term that does not parse and keeps the former result. */
    const message = $(ID_QUERY_MESSAGE);
    const parsed = text.trim() ? parseQuery(text) : { edge: false, terms: [] };
    const unknown = parsed.edge && parsed.terms && parsed.terms.find((t) => !EDGE_KEYS.includes(t.key));
    if (parsed.error || unknown) {
      message.textContent = parsed.error || `cannot read "${unknown.raw}": an edge query knows ${EDGE_KEYS.join(", ")}`;
      message.classList.add(CLASS_ERROR);
      return false;
    }
    message.classList.remove(CLASS_ERROR);
    if (!parsed.terms.length) {
      state.queryNodes = null;
      state.queryRelations = null;
      message.textContent = "";
    } else if (parsed.edge) {
      state.queryRelations = new Set(state.model.relations.filter((r) => parsed.terms.every((t) => relationMeets(r, t))));
      state.queryNodes = new Set([...state.queryRelations].flatMap((r) => [r.source, r.target]));
      message.textContent = `${state.queryRelations.size} relations, ${state.queryNodes.size} nodes match`;
    } else {
      state.queryNodes = new Set([...state.model.nodes.values()].filter((n) => parsed.terms.every((t) => nodeMeets(n, t))).map((n) => n.id));
      state.queryRelations = null;
      message.textContent = `${state.queryNodes.size} nodes match`;
    }
    refresh();
    return true;
  }

  function query(text) {
    $(ID_QUERY).value = text;
    return runQuery(text);
  }

  // ---- saved query buttons (RQ-TRC-153, DEC-TRC-093) ---------------------------------------------------------
  const saved = { list: [], managing: false, editing: null };

  function defaultQueries() {
    return JSON.parse($("default-queries").textContent).queries.map(({ label, query: q }) => ({ label, query: q }));
  }

  const validQueries = (list) => Array.isArray(list)
    && list.every((q) => q && typeof q.label === "string" && q.label && typeof q.query === "string");

  function loadSaved() {
    /* The reader's buttons from the browser's storage, else the default ones; then shown. */
    let stored = null;
    try {
      stored = JSON.parse(localStorage.getItem(STORE_KEY));
    } catch (error) {
      stored = null;
    }
    saved.list = validQueries(stored) ? stored : defaultQueries();
    renderSaved();
  }

  function storeSaved() {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(saved.list));
    } catch (error) {
      $(ID_QUERY_MESSAGE).textContent = `The buttons could not be kept in this browser: ${error.message}`;
    }
    renderSaved();
  }

  function addSaved(label, q) { saved.list.push({ label, query: q }); storeSaved(); }
  function editSaved(index, label, q) { saved.list[index] = { label, query: q }; storeSaved(); }
  function removeSaved(index) { saved.list.splice(index, 1); storeSaved(); }

  function moveSaved(index, delta) {
    const to = index + delta;
    if (to < 0 || to >= saved.list.length) return;
    const [item] = saved.list.splice(index, 1);
    saved.list.splice(to, 0, item);
    storeSaved();
  }

  const exportText = () => `${JSON.stringify({ queries: saved.list }, null, 2)}\n`;

  function importText(text) {
    /* Replaces the buttons by those of an exported file, or says why it cannot. */
    let list;
    try {
      list = JSON.parse(text).queries;
    } catch (error) {
      list = null;
    }
    if (!validQueries(list)) {
      $(ID_QUERY_MESSAGE).textContent = "The file holds no list of saved queries (queries: [{label, query}])";
      return false;
    }
    saved.list = list.map(({ label, query: q }) => ({ label, query: q }));
    storeSaved();
    return true;
  }

  function downloadSaved() {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([exportText()], { type: "application/json" }));
    link.download = EXPORT_NAME;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function savedEditor() {
    const item = saved.editing === EDIT_NEW ? { label: "", query: $(ID_QUERY).value.trim() } : saved.list[saved.editing];
    return `<form class="saved-editor" id="saved-editor"><label class="query-label" for="saved-label">Label</label>`
      + `<input id="saved-label" type="text" value="${escapeHtml(item.label)}" required>`
      + `<label class="query-label" for="saved-query">Query</label>`
      + `<input id="saved-query" type="text" spellcheck="false" value="${escapeHtml(item.query)}">`
      + `<button type="submit" class="button button-primary">Save</button>`
      + `<button type="button" class="button" data-saved="cancel">Cancel</button></form>`;
  }

  function renderSaved() {
    const tool = (action, index, text, label) => `<button type="button" class="saved-tool" data-saved="${action}" data-index="${index}"`
      + ` aria-label="${label}">${text}</button>`;
    const items = saved.list.map((q, i) => `<span class="saved-item"><button type="button" class="chip saved-run" data-index="${i}"`
      + ` title="${escapeHtml(q.query)}">${escapeHtml(q.label)}</button>${saved.managing ? tool("edit", i, "✎", `Edit ${escapeHtml(q.label)}`)
      + tool("left", i, "‹", "Move left") + tool("right", i, "›", "Move right") + tool("delete", i, "×", `Delete ${escapeHtml(q.label)}`) : ""}</span>`);
    const manage = saved.managing
      ? `<button type="button" class="button" data-saved="export">Export…</button><button type="button" class="button" data-saved="import">Import…</button>`
        + `<button type="button" class="button" data-saved="done">Done</button>`
      : `<button type="button" class="button" data-saved="manage">Edit buttons</button>`;
    $(ID_SAVED).innerHTML = `${items.join("")}<button type="button" class="button" data-saved="new">+ Save query</button>${manage}`
      + `${saved.editing === null ? "" : savedEditor()}`;
  }

  function onSavedClick(event) {
    const run = event.target.closest(".saved-run");
    if (run) {
      query(saved.list[Number(run.dataset.index)].query);
      return;
    }
    const control = event.target.closest("[data-saved]");
    if (!control) return;
    const index = Number(control.dataset.index);
    const actions = {
      new: () => { saved.editing = EDIT_NEW; renderSaved(); },
      cancel: () => { saved.editing = null; renderSaved(); },
      manage: () => { saved.managing = true; renderSaved(); },
      done: () => { saved.managing = false; saved.editing = null; renderSaved(); },
      edit: () => { saved.editing = index; renderSaved(); },
      left: () => moveSaved(index, -1),
      right: () => moveSaved(index, 1),
      delete: () => removeSaved(index),
      export: downloadSaved,
      import: () => $("saved-import-file").click(),
    };
    actions[control.dataset.saved]();
  }

  function onSavedSubmit(event) {
    event.preventDefault();
    const label = $("saved-label").value.trim();
    const q = $("saved-query").value.trim();
    if (!label) return;
    if (saved.editing === EDIT_NEW) addSaved(label, q); else editSaved(saved.editing, label, q);
    saved.editing = null;
    renderSaved();
  }

  function writeTerm(facet, value) {
    /* Writes the facet value's term into the query, an edge query for a relation facet (RQ-TRC-151). */
    const written = /\s/.test(value) ? `"${value}"` : value;
    const term = `${facet.key}:${written}`;
    const input = $(ID_QUERY);
    const current = input.value.trim();
    if (facet.of === FACET_RELATIONS) input.value = EDGE_RE.test(current) ? `${current} ${term}` : `edge ${term}`;
    else input.value = current && !EDGE_RE.test(current) ? `${current} ${term}` : term;
    input.focus();
  }

  // ---- tables (RQ-TRC-149) ------------------------------------------------------------------------------------
  function nodeRows() {
    return [...state.model.nodes.values()].filter(isShown).map((n) => ({
      key: n.id, id: n.id, type: n.type, tri: n.props.tri || NO_VALUE, status: n.props.status || NO_VALUE,
      title: n.props.title || NO_VALUE, location: location(n.props), incoming: n.incoming.length, outgoing: n.outgoing.length,
    }));
  }

  function relationRows() {
    return state.model.relations.filter(isRelationShown).map((r) => ({
      key: r.source, source: r.source, target: r.target, kind: r.kind, field: fieldOf(r),
      line: r.proofs.length ? r.proofs[0].line : NO_VALUE, proof: r.proofs.length ? r.proofs[0].text : NO_VALUE,
    }));
  }

  function sorted(rows, view) {
    const sort = state.sort[view];
    if (!sort) return rows;
    const sign = sort.dir === ASCENDING ? 1 : -1;
    return [...rows].sort((a, b) => sign * compare(a[sort.key], b[sort.key]));
  }

  const NODE_CELLS = {
    id: (row) => `<td class="mono">${escapeHtml(row.id)}</td>`,
    type: (row) => `<td>${typeLabel(row.type)}</td>`,
    location: (row) => `<td class="mono muted" title="${escapeHtml(row.location)}">${escapeHtml(row.location)}</td>`,
    title: (row) => `<td title="${escapeHtml(row.title)}">${escapeHtml(row.title)}</td>`,
  };
  const RELATION_CELLS = {
    source: (row) => `<td class="mono" title="${escapeHtml(row.source)}">${escapeHtml(row.source)}</td>`,
    target: (row) => `<td class="mono">${escapeHtml(row.target)}</td>`,
    proof: (row) => `<td class="mono muted" title="${escapeHtml(row.proof)}">${escapeHtml(row.proof)}</td>`,
  };

  function renderTable(table, columns, cells, rows) {
    const plain = (key) => (row) => `<td>${escapeHtml(row[key])}</td>`;
    table.tBodies[0].innerHTML = rows.map((row) => `<tr tabindex="0" data-key="${escapeHtml(row.key)}"${
      row.key === state.selected ? ` ${ATTR_SELECTED}="true"` : ""}>${columns.map((c) => (cells[c] || plain(c))(row)).join("")}</tr>`).join("");
    for (const th of table.tHead.rows[0].cells) {
      const sort = state.sort[table === $(ID_NODE_TABLE) ? VIEW_NODES : VIEW_RELATIONS];
      if (sort && sort.key === th.dataset.key) th.setAttribute(ATTR_SORT, sort.dir); else th.removeAttribute(ATTR_SORT);
    }
  }

  function renderTables() {
    const nodes = nodeRows();
    const relations = relationRows();
    renderTable($(ID_NODE_TABLE), NODE_COLUMNS, NODE_CELLS, sorted(nodes, VIEW_NODES));
    renderTable($(ID_RELATION_TABLE), RELATION_COLUMNS, RELATION_CELLS, sorted(relations, VIEW_RELATIONS));
    $("view-count").textContent = `${nodes.length} / ${state.model.nodes.size} nodes · `
      + `${relations.length} / ${state.model.relations.length} relations shown`;
  }

  function onSort(view, key) {
    const current = state.sort[view];
    state.sort[view] = { key, dir: current && current.key === key && current.dir === ASCENDING ? DESCENDING : ASCENDING };
    renderTables();
  }

  // ---- detail panel (RQ-TRC-154) ------------------------------------------------------------------------------
  function propertyValue(value) {
    return typeof value === "object" && value !== null ? JSON.stringify(value) : String(value);
  }

  function relationItem(relation, outgoing) {
    const other = outgoing ? relation.target : relation.source;
    const field = fieldOf(relation);
    const proofs = relation.proofs.map((p) => `<span class="proof">L${p.line}  ${escapeHtml(p.text)}${
      p.field ? `  [${escapeHtml(p.field)}]` : ""}</span>`).join("");
    return `<li><button type="button" class="relation-link" data-node="${escapeHtml(other)}">`
      + `<span class="relation-head"><span>${outgoing ? "outgoing →" : "← incoming"}</span>`
      + `<span class="relation-end">${escapeHtml(other)}</span><span class="pill">${escapeHtml(relation.kind)}</span>`
      + `${field === NO_VALUE ? "" : `<span class="pill">${escapeHtml(field)}</span>`}</span>${proofs}</button></li>`;
  }

  function renderDetail() {
    const panel = $(ID_DETAIL);
    const node = state.selected && state.model.nodes.get(state.selected);
    if (!node) {
      panel.innerHTML = `<p class="detail-empty">Select a node in a view to see every property, its incoming and outgoing `
        + `relations, their link field and their proofs.</p>`;
      return;
    }
    const props = Object.keys(node.props).sort(compare)
      .map((k) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(propertyValue(node.props[k]))}</dd>`).join("");
    const relations = [...node.outgoing.map((r) => relationItem(r, true)), ...node.incoming.map((r) => relationItem(r, false))];
    const actions = [[ACTION_HIDE, "Hide"], [ACTION_ISOLATE, "Isolate neighbourhood"], [ACTION_WIDEN, "Widen by one hop"]]
      .map(([action, label]) => `<button type="button" class="button" data-action="${action}">${label}</button>`).join("");
    panel.innerHTML = `${typeLabel(node.type)}<p class="detail-id">${escapeHtml(node.id)}</p>`
      + `<p class="detail-title">${escapeHtml(node.props.title || "")}</p><div class="detail-actions">${actions}</div>`
      + `<h2 class="panel-title">Properties</h2><dl class="properties">${props}</dl>`
      + `<h2 class="panel-title">Relations (${relations.length})</h2><ul class="relations">${relations.join("")}</ul>`;
  }

  function select(id) {
    state.selected = id;
    renderTables();
    renderDetail();
    if (cy) {
      cy.nodes().removeClass(CLASS_PICKED);
      cy.$id(id).addClass(CLASS_PICKED);
    }
  }

  // ---- graph view (RQ-TRC-147, RQ-TRC-150, DEC-TRC-090) -------------------------------------------------------
  const cssValue = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const typeColour = (type) => cssValue(`--s-type-${type.toLowerCase()}`);

  function layoutPositions(model) {
    /* One column per node type, in TYPE_ORDER, wrapped every graph-column-rows nodes; kept in the model, so a moved node
       stays where the reader put it (DEC-TRC-090). */
    const column = tokenNumber("--c-graph-column-gap");
    const row = tokenNumber("--c-graph-row-gap");
    const rows = tokenNumber("--c-graph-column-rows");
    let x = 0;
    for (const type of TYPE_ORDER) {
      const ids = [...model.nodes.values()].filter((n) => n.type === type).map((n) => n.id).sort(compare);
      ids.forEach((id, i) => model.positions.set(id, { x: x + Math.floor(i / rows) * column, y: (i % rows) * row }));
      if (ids.length) x += Math.ceil(ids.length / rows) * column + column;
    }
  }

  function graphStyle() {
    return [
      { selector: SELECTOR_NODE, style: { "background-color": `data(${DATA_COLOUR})`, label: "data(id)", width: tokenNumber(TOKEN_NODE_SIZE),
        height: tokenNumber(TOKEN_NODE_SIZE), "font-size": tokenNumber("--c-graph-label-size"), "font-family": cssValue("--s-font-sans"), color: cssValue("--c-graph-label-color"),
        "min-zoomed-font-size": tokenNumber("--c-graph-label-min-zoomed"), "text-valign": "bottom" } },
      { selector: "edge", style: { width: tokenNumber("--c-graph-edge-width"), "line-color": `data(${DATA_COLOUR})`,
        "target-arrow-color": `data(${DATA_COLOUR})`, "target-arrow-shape": "triangle", "curve-style": "straight" } },
      { selector: `edge[kind = "${KIND_CONTAINS}"]`, style: { "line-style": "dashed" } },
      { selector: `.${CLASS_PICKED}`, style: { "border-width": tokenNumber("--c-graph-selected-border-width"),
        "border-color": cssValue("--c-graph-selected-border") } },
      { selector: `.${CLASS_HIDDEN}`, style: { display: "none" } },
    ];
  }

  function graphElements(model) {
    const kindColour = { contains: "contains", refs: "cites", code: "code", call: "call" };
    const nodes = [...model.nodes.values()].map((n) => ({ group: "nodes", data: { id: n.id, [DATA_COLOUR]: typeColour(n.type) },
                                                          position: { ...model.positions.get(n.id) } }));
    const edges = model.relations.map((r, i) => ({ group: "edges", data: { id: `r${i}`, source: r.source, target: r.target,
      kind: r.kind, [DATA_COLOUR]: cssValue(`--c-graph-edge-${kindColour[r.kind] || kindColour.refs}`) } }));
    return [...nodes, ...edges];
  }

  function applyVisibility() {
    if (!cy) return;
    cy.batch(() => cy.nodes().forEach((n) => n.toggleClass(CLASS_HIDDEN, !isShown(state.model.nodes.get(n.id())))));
  }

  function initGraph() {
    /* Draws the graph once its view is shown, so that the canvas has a size; a new graph draws a new one. */
    if (cy || !state.model || state.view !== VIEW_GRAPH) return;
    if (!window.cytoscape) {
      $(VIEW_GRAPH).textContent = MESSAGE_NO_LIBRARY;
      return;
    }
    if (!state.model.positions.size) layoutPositions(state.model);
    cy = window.cytoscape({ container: $(VIEW_GRAPH), elements: graphElements(state.model), layout: { name: "preset" },
                            style: graphStyle(), minZoom: tokenNumber("--c-graph-zoom-min"), maxZoom: tokenNumber("--c-graph-zoom-max"),
                            wheelSensitivity: tokenNumber("--c-graph-wheel-sensitivity"), boxSelectionEnabled: false });
    cy.on("tap", SELECTOR_NODE, (event) => select(event.target.id()));
    cy.on(EVENT_DRAG_FREE, SELECTOR_NODE, (event) => state.model.positions.set(event.target.id(), { ...event.target.position() }));
    applyVisibility();
    if (state.selected) cy.$id(state.selected).addClass(CLASS_PICKED);
    fitGraph();
  }

  // The nodes not hidden by a class: Cytoscape caches visible(), so the class is the truth (RQ-TRC-154).
  const shownNodes = () => cy.nodes().filter((n) => !n.hasClass(CLASS_HIDDEN));

  function fitGraph() {
    if (cy) cy.fit(shownNodes(), tokenNumber("--c-graph-fit-padding"));
  }

  function zoomBy(factor) {
    if (!cy) return;
    const level = Math.min(cy.maxZoom(), Math.max(cy.minZoom(), cy.zoom() * factor));
    cy.zoom({ level, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  }

  // ---- hiding and isolating (RQ-TRC-154) ----------------------------------------------------------------------
  function renderHidden() {
    const chips = [...state.hiddenNodes].sort(compare).map((id) => `<button type="button" class="chip" data-unhide="${escapeHtml(id)}"`
      + ` aria-label="Show ${escapeHtml(id)} again">${escapeHtml(id)} ×</button>`);
    const parts = [];
    if (chips.length) parts.push(`<span class="chip-note">Hidden:</span>`, ...chips);
    if (state.isolate) parts.push(`<span class="chip-note">Neighbourhood isolated: ${state.isolate.size} nodes</span>`);
    $(ID_HIDDEN_LIST).innerHTML = parts.join("");
  }

  function refresh() {
    applyVisibility();
    renderTables();
    renderHidden();
  }

  function hideTypes(types) {
    state.off[FACET_TYPE] = new Set(types);
    renderFacets();
    refresh();
  }

  function hide(id) {
    state.hiddenNodes.add(id);
    refresh();
  }

  function unhide(id) {
    state.hiddenNodes.delete(id);
    refresh();
  }

  function isolate() {
    if (!state.selected) return;
    state.isolate = neighbours(state.selected);
    refresh();
    arrangeAround(state.selected);
  }

  function widen() {
    if (!state.selected) return;
    const base = state.isolate || new Set([state.selected]);
    state.isolate = new Set([...base].flatMap((id) => [...neighbours(id)]));
    refresh();
    arrangeAround(state.selected);
  }

  function hopsFrom(id, allowed) {
    /* The number of relations between id and each node of allowed, breadth first (RQ-TRC-154). */
    const hops = new Map([[id, 0]]);
    let frontier = [id];
    while (frontier.length) {
      const next = [];
      for (const current of frontier) {
        for (const other of neighbours(current)) {
          if (allowed.has(other) && !hops.has(other)) {
            hops.set(other, hops.get(current) + 1);
            next.push(other);
          }
        }
      }
      frontier = next;
    }
    return hops;
  }

  function arrangeAround(id) {
    /* Lays the isolated nodes in circles around id, one circle per hop, keeps their positions in the model as a move
       would (DEC-TRC-090), and frames them. */
    if (!cy || !state.isolate) return;
    const hops = hopsFrom(id, state.isolate);
    const far = Math.max(...hops.values()) + 1;
    shownNodes().layout({ name: "concentric", animate: false, fit: false, levelWidth: () => 1,
                          minNodeSpacing: tokenNumber("--c-graph-node-spacing"),
                          concentric: (n) => far - (hops.has(n.id()) ? hops.get(n.id()) : far) }).run();
    shownNodes().forEach((n) => state.model.positions.set(n.id(), { ...n.position() }));
    fitGraph();
  }

  function showAll() {
    for (const key of Object.keys(state.off)) state.off[key] = new Set();
    state.hiddenNodes = new Set();
    state.isolate = null;
    renderFacets();
    query("");
  }

  // ---- views --------------------------------------------------------------------------------------------------
  function showView(view) {
    state.view = view;
    for (const tab of document.querySelectorAll(SELECTOR_TAB)) tab.setAttribute(ATTR_SELECTED, String(tab.dataset.view === view));
    for (const name of [VIEW_GRAPH, VIEW_NODES, VIEW_RELATIONS]) $(`view-${name}`).classList.toggle(CLASS_ACTIVE, name === view);
    for (const control of document.querySelectorAll(".graph-control")) control.hidden = view !== VIEW_GRAPH;
    if (state.model) renderTables();
    initGraph();
  }

  function render() {
    renderHeader();
    renderTables();
    renderDetail();
    renderHidden();
  }

  // ---- loading (RQ-TRC-145, DEC-TRC-088) ----------------------------------------------------------------------
  function loadGraph(graph) {
    state.model = buildModel(graph);
    state.model.positions = new Map();
    state.selected = null;
    state.hiddenNodes = new Set();
    state.isolate = null;
    state.queryNodes = null;
    state.queryRelations = null;
    if (cy) {
      cy.destroy();
      cy = null;
    }
    render();
    initGraph();
  }

  function loadText(name, text) {
    /* Shows the graph of a dropped or chosen file, or names the file and the cause and keeps the shown graph. */
    let graph;
    try {
      graph = JSON.parse(text);
    } catch (error) {
      $(ID_MESSAGE).textContent = `${name}: not JSON (${error.message})`;
      return false;
    }
    if (!graph || !Array.isArray(graph.elements)) {
      $(ID_MESSAGE).textContent = `${name}: no elements list, not an agnos-graph file`;
      return false;
    }
    $(ID_MESSAGE).textContent = "";
    loadGraph(graph);
    return true;
  }

  function readFile(file) {
    const reader = new FileReader();
    reader.onload = () => loadText(file.name, reader.result);
    reader.onerror = () => { $(ID_MESSAGE).textContent = `${file.name}: ${reader.error}`; };
    reader.readAsText(file);
  }

  // ---- splitters (RQ-TRC-148, DEC-TRC-012 copied) -------------------------------------------------------------
  function setPanelWidth(panelId, width) {
    const limit = LIMITS[panelId];
    const other = panelId === ID_FACETS ? ID_DETAIL : ID_FACETS;
    const room = $("app").clientWidth - $(other).getBoundingClientRect().width
      - 2 * tokenNumber(TOKEN_SPLITTER) - tokenNumber(TOKEN_MAIN_MIN);
    const bounded = Math.max(tokenNumber(limit.min), Math.min(width, tokenNumber(limit.max), room));
    document.documentElement.style.setProperty(limit.variable, bounded + UNIT_PX);
  }

  function wireSplitter(splitterId, panelId, sign) {
    const splitter = $(splitterId);
    const width = () => $(panelId).getBoundingClientRect().width;
    splitter.addEventListener(EVENT_KEYDOWN, (event) => {
      const delta = { [KEY_RIGHT]: 1, [KEY_LEFT]: -1 }[event.key];
      if (!delta) return;
      event.preventDefault();
      setPanelWidth(panelId, width() + sign * delta * tokenNumber(TOKEN_STEP));
    });
    splitter.addEventListener("pointerdown", (event) => {
      const startX = event.clientX;
      const start = width();
      splitter.setPointerCapture(event.pointerId);
      splitter.classList.add(CLASS_DRAGGING);
      const move = (e) => setPanelWidth(panelId, start + sign * (e.clientX - startX));
      const up = () => {
        splitter.classList.remove(CLASS_DRAGGING);
        splitter.removeEventListener(EVENT_POINTER_MOVE, move);
        splitter.removeEventListener(EVENT_POINTER_UP, up);
      };
      splitter.addEventListener(EVENT_POINTER_MOVE, move);
      splitter.addEventListener(EVENT_POINTER_UP, up);
    });
  }

  // ---- wiring -------------------------------------------------------------------------------------------------
  function wire() {
    for (const tab of document.querySelectorAll(SELECTOR_TAB)) tab.addEventListener(EVENT_CLICK, () => showView(tab.dataset.view));
    for (const [tableId, view] of [[ID_NODE_TABLE, VIEW_NODES], [ID_RELATION_TABLE, VIEW_RELATIONS]]) {
      const table = $(tableId);
      table.tHead.addEventListener(EVENT_CLICK, (event) => {
        const th = event.target.closest("th");
        if (th) onSort(view, th.dataset.key);
      });
      const pick = (event) => {
        const row = event.target.closest(ROW_TAG);
        if (row && row.parentElement === table.tBodies[0]) select(row.dataset.key);
      };
      table.tBodies[0].addEventListener(EVENT_CLICK, pick);
      table.tBodies[0].addEventListener(EVENT_KEYDOWN, (event) => { if (event.key === KEY_ENTER) pick(event); });
    }
    $(ID_DETAIL).addEventListener(EVENT_CLICK, (event) => {
      const link = event.target.closest(".relation-link");
      if (link) select(link.dataset.node);
      const action = event.target.closest("[data-action]");
      if (action) ({ [ACTION_HIDE]: () => hide(state.selected), [ACTION_ISOLATE]: isolate, [ACTION_WIDEN]: widen })[action.dataset.action]();
    });
    $(ID_HIDDEN_LIST).addEventListener(EVENT_CLICK, (event) => {
      const chip = event.target.closest("[data-unhide]");
      if (chip) unhide(chip.dataset.unhide);
    });
    const step = () => tokenNumber(TOKEN_ZOOM_STEP);
    $("graph-zoom-in").addEventListener(EVENT_CLICK, () => zoomBy(step()));
    $("graph-zoom-out").addEventListener(EVENT_CLICK, () => zoomBy(1 / step()));
    $("graph-fit").addEventListener(EVENT_CLICK, fitGraph);
    $("show-all").addEventListener(EVENT_CLICK, showAll);
    // RQ-TRC-153: the saved query buttons
    $(ID_SAVED).addEventListener(EVENT_CLICK, onSavedClick);
    $(ID_SAVED).addEventListener("submit", onSavedSubmit);
    $("saved-import-file").addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (file) file.text().then(importText);
      event.target.value = "";
    });
    // RQ-TRC-151, RQ-TRC-152: the query bar and the facets
    $("query-run").addEventListener(EVENT_CLICK, () => runQuery($(ID_QUERY).value));
    $("query-clear").addEventListener(EVENT_CLICK, () => query(""));
    $(ID_QUERY).addEventListener(EVENT_KEYDOWN, (event) => { if (event.key === KEY_ENTER) runQuery($(ID_QUERY).value); });
    let queryFocused = false;              // a mouse press moves the focus before the click: read it on the press
    $(ID_FACETS).addEventListener("mousedown", () => { queryFocused = document.activeElement === $(ID_QUERY); }, true);
    $(ID_FACETS).addEventListener(EVENT_CLICK, (event) => {
      const box = event.target.closest("input[type=checkbox]");
      if (!box) return;
      const facet = FACETS.find((f) => f.key === box.closest("[data-facet]").dataset.facet);
      if (queryFocused || document.activeElement === $(ID_QUERY)) {
        event.preventDefault();
        queryFocused = false;
        writeTerm(facet, box.value);
        return;
      }
      if (box.checked) state.off[facet.key].delete(box.value); else state.off[facet.key].add(box.value);
      refresh();
    });
    $("file-input").addEventListener("change", (event) => { if (event.target.files[0]) readFile(event.target.files[0]); });
    const zone = $("drop-zone");
    document.addEventListener("dragover", (event) => { event.preventDefault(); zone.hidden = false; });
    zone.addEventListener("dragleave", () => { zone.hidden = true; });
    document.addEventListener("drop", (event) => {
      event.preventDefault();
      zone.hidden = true;
      if (event.dataTransfer.files[0]) readFile(event.dataTransfer.files[0]);
    });
    wireSplitter("split-left", ID_FACETS, 1);
    wireSplitter("split-right", ID_DETAIL, -1);
  }

  wire();
  loadSaved();
  showView(DEFAULT_VIEW);
  if (window.AGNOS_GRAPH && Array.isArray(window.AGNOS_GRAPH.elements)) loadGraph(window.AGNOS_GRAPH);
  else $(ID_MESSAGE).textContent = MESSAGE_NO_GRAPH;

  window.agnosExplorer = {                         // test hooks (RQ-TRC-145 to RQ-TRC-154)
    showView, select, loadText, hideTypes, hide, unhide, isolate, widen, showAll, query,
    saved: { list: () => saved.list, add: addSaved, edit: editSaved, move: moveSaved, remove: removeSaved, load: loadSaved,
             exportText, importText },                                       // RQ-TRC-153
    shownIds: () => [...state.model.nodes.values()].filter(isShown).map((n) => n.id),
    counts: () => ({ nodes: state.model ? state.model.nodes.size : 0, relations: state.model ? state.model.relations.length : 0 }),
    graph: {                                       // RQ-TRC-150, DEC-TRC-090
      cy: () => cy,
      move(id, x, y) { cy.$id(id).position({ x, y }); cy.$id(id).emit(EVENT_DRAG_FREE); },
      position: (id) => cy.$id(id).position(),
      shown: (id) => !cy.$id(id).hasClass(CLASS_HIDDEN),
      shownIds: () => shownNodes().map((n) => n.id()),
      colour: (id) => cy.$id(id).data(DATA_COLOUR).toLowerCase(),
      allInView() {
        const view = cy.extent();
        return shownNodes().every((n) => {
          const box = n.boundingBox();
          return box.x1 >= view.x1 && box.x2 <= view.x2 && box.y1 >= view.y1 && box.y2 <= view.y2;
        });
      },
    },
  };
})();
