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
  const VIEW_GRAPH = "graph";
  const VIEW_NODES = "nodes";
  const VIEW_RELATIONS = "relations";
  const DEFAULT_VIEW = VIEW_NODES;
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

  const $ = (id) => document.getElementById(id);
  const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
  const tokenNumber = (name) => parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);     // code-point order, as the graph file is sorted

  const state = { model: null, view: DEFAULT_VIEW, selected: null, sort: { [VIEW_NODES]: null, [VIEW_RELATIONS]: null } };

  // ---- view model (RQ-TRC-146, DEC-TRC-089) -------------------------------------------------------------------
  function linkFields(graph) {
    /* The field of each proof line of a refs edge, from the links block: source + target -> line -> field. */
    const fields = new Map();
    for (const [source, target, rows] of graph.links || []) {
      fields.set(source + LINK_KEY_SEPARATOR + target, new Map(rows.map(([line, field]) => [line, field])));
    }
    return fields;
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
    const counts = new Map();
    for (const node of nodes.values()) counts.set(node.type, (counts.get(node.type) || 0) + 1);
    $("type-legend").innerHTML = [...counts].sort((a, b) => compare(a[0], b[0]))
      .map(([type, n]) => `<li>${swatch(type)}${typeLabel(type)}<span class="count">${n}</span></li>`).join("");
  }

  // ---- tables (RQ-TRC-149) ------------------------------------------------------------------------------------
  function nodeRows() {
    return [...state.model.nodes.values()].map((n) => ({
      key: n.id, id: n.id, type: n.type, tri: n.props.tri || NO_VALUE, status: n.props.status || NO_VALUE,
      title: n.props.title || NO_VALUE, location: location(n.props), incoming: n.incoming.length, outgoing: n.outgoing.length,
    }));
  }

  function relationRows() {
    return state.model.relations.map((r) => ({
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
    renderTable($(ID_NODE_TABLE), NODE_COLUMNS, NODE_CELLS, sorted(nodeRows(), VIEW_NODES));
    renderTable($(ID_RELATION_TABLE), RELATION_COLUMNS, RELATION_CELLS, sorted(relationRows(), VIEW_RELATIONS));
    const { nodes, relations } = state.model;
    $("view-count").textContent = state.view === VIEW_RELATIONS ? `${relations.length} relations` : `${nodes.size} nodes`;
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
    panel.innerHTML = `${typeLabel(node.type)}<p class="detail-id">${escapeHtml(node.id)}</p>`
      + `<p class="detail-title">${escapeHtml(node.props.title || "")}</p>`
      + `<h2 class="panel-title">Properties</h2><dl class="properties">${props}</dl>`
      + `<h2 class="panel-title">Relations (${relations.length})</h2><ul class="relations">${relations.join("")}</ul>`;
  }

  function select(id) {
    state.selected = id;
    renderTables();
    renderDetail();
  }

  // ---- views --------------------------------------------------------------------------------------------------
  function showView(view) {
    state.view = view;
    for (const tab of document.querySelectorAll(SELECTOR_TAB)) tab.setAttribute(ATTR_SELECTED, String(tab.dataset.view === view));
    for (const name of [VIEW_GRAPH, VIEW_NODES, VIEW_RELATIONS]) $(`view-${name}`).classList.toggle(CLASS_ACTIVE, name === view);
    if (state.model) renderTables();
  }

  function render() {
    renderHeader();
    renderTables();
    renderDetail();
  }

  // ---- loading (RQ-TRC-145, DEC-TRC-088) ----------------------------------------------------------------------
  function loadGraph(graph) {
    state.model = buildModel(graph);
    state.selected = null;
    render();
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
  showView(DEFAULT_VIEW);
  if (window.AGNOS_GRAPH && Array.isArray(window.AGNOS_GRAPH.elements)) loadGraph(window.AGNOS_GRAPH);
  else $(ID_MESSAGE).textContent = MESSAGE_NO_GRAPH;

  window.agnosExplorer = {                         // test hooks (RQ-TRC-145 to RQ-TRC-154)
    showView, select, loadText,
    counts: () => ({ nodes: state.model ? state.model.nodes.size : 0, relations: state.model ? state.model.relations.length : 0 }),
  };
})();
