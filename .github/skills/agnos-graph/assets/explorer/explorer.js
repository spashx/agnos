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
  const ID_HIDDEN_LIST = "hidden-list";
  const TOKEN_NODE_SIZE = "--c-graph-node-size";

  const $ = (id) => document.getElementById(id);
  const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
  const tokenNumber = (name) => parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);     // code-point order, as the graph file is sorted

  const state = { model: null, view: DEFAULT_VIEW, selected: null, sort: { [VIEW_NODES]: null, [VIEW_RELATIONS]: null },
                  hiddenTypes: new Set(), hiddenNodes: new Set(), isolate: null };   // RQ-TRC-154: what every view hides
  let cy = null;                                                                       // DEC-TRC-090: the graph view

  // ---- visibility, shared by every view (RQ-TRC-151, RQ-TRC-154) ----------------------------------------------
  const isShown = (node) => !state.hiddenTypes.has(node.type) && !state.hiddenNodes.has(node.id)
    && (!state.isolate || state.isolate.has(node.id));
  const isRelationShown = (relation) => isShown(state.model.nodes.get(relation.source))
    && isShown(state.model.nodes.get(relation.target));

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
    state.hiddenTypes = new Set(types);
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
    state.hiddenTypes = new Set();
    state.hiddenNodes = new Set();
    state.isolate = null;
    refresh();
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
    showView, select, loadText, hideTypes, hide, unhide, isolate, widen, showAll,
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
