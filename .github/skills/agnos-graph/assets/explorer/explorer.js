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
  const VIEW_GRAPH3D = "graph3d";                   // RQ-GXP-010: the 3D graph view
  const VIEWS = [VIEW_GRAPH, VIEW_GRAPH3D, VIEW_NODES, VIEW_RELATIONS];
  const GLOBAL_THREE = "THREE";                     // RQ-GXP-019, DEC-GXP-007: the global three.js sets
  const MESSAGE_NO_THREE = "three.js could not be loaded from cdnjs: the 3D view needs the network once; the other views work without it.";
  const DEFAULT_VIEW = VIEW_GRAPH;
  const LINK_KEY_SEPARATOR = "\u0000";
  const NO_VALUE = "—";
  const ASCENDING = "ascending";
  const DESCENDING = "descending";
  const ATTR_SELECTED = "aria-selected";
  const ATTR_SORT = "aria-sort";
  const CLASS_ACTIVE = "active";
  const CLASS_DRAGGING = "dragging";
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
  const DATA_INDEX = "index";                       // RQ-TRC-151: the relation's index in the view model
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
  const BULK_ALL = "all";                           // RQ-TRC-160
  const BULK_NONE = "none";
  const CLASS_RESIZED = "resized";                  // RQ-TRC-159
  const TOKEN_COLUMN_MIN = "--c-table-column-min-width";
  const ID_LAYOUT = "graph-layout";                 // RQ-TRC-162, RQ-TRC-163
  const ID_MENU = "graph-menu";
  const LAYOUT_COLUMNS = "columns";
  const MENU_LAYOUT = "layout:";
  const MENU_HOPS = "hops:";
  const MENU_FIT = "fit";
  const MENU_SELECT = "select";
  const HOPS = [1, 2, 3];
  const KEY_ESCAPE = "Escape";
  const ID_TIP = "graph-tip";                       // RQ-TRC-167
  const TOKEN_TIP_DELAY = "--c-graph-tip-delay";
  const ID_DIRECTION = "graph-direction";           // RQ-TRC-166
  const DIRECTION_LR = "lr";
  const DIRECTION_TB = "tb";
  const NATURAL_DIRECTION = { [LAYOUT_COLUMNS]: DIRECTION_LR, grid: DIRECTION_LR, breadthfirst: DIRECTION_TB };
  const ID_LEGEND = "graph-legend";                 // RQ-TRC-165
  const CLASS_FOLDED = "folded";
  const KIND_NAMES = { contains: "contains", refs: "refs (cites)", code: "code (cited in code)", call: "call" };
  const TOKEN_NODE_SIZE = "--c-graph-node-size";

  const $ = (id) => document.getElementById(id);
  const escapeHtml = (text) => String(text).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
  const tokenNumber = (name) => parseFloat(getComputedStyle(document.documentElement).getPropertyValue(name));
  const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);     // code-point order, as the graph file is sorted

  const state = { model: null, view: DEFAULT_VIEW, selected: null, sort: { [VIEW_NODES]: null, [VIEW_RELATIONS]: null },
                  hiddenNodes: new Set(), isolate: null,                             // RQ-TRC-154: what every view hides
                  off: { type: new Set(), tri: new Set(), status: new Set(), kind: new Set(), field: new Set() },   // RQ-TRC-151
                  queryNodes: null, queryRelations: null,                            // RQ-TRC-152
                  period: null,                       // RQ-GXP-006, DEC-GXP-003: { start, end, startDay, endDay }, null for the whole history
                  cursor: null, window: 0,            // RQ-GXP-007, RQ-GXP-008: the playback's instant, the window's days (0: cumulative)
                  bounds: null };                     // DEC-GXP-003: { lo, hi } the shown dates, from the three above; null: every date
  let cy = null;                                                                       // DEC-TRC-090: the graph view

  // ---- visibility, shared by every view (RQ-TRC-151, RQ-TRC-152, RQ-TRC-154) ----------------------------------
  const facetAllows = (facet, item) => facet.values(item).some((v) => !state.off[facet.key].has(v));
  // RQ-GXP-006 to RQ-GXP-008, DEC-GXP-003: the time is one more term, so that every view applies it as it applies a facet
  const inPeriod = (node) => !state.bounds || (node.date >= state.bounds.lo && node.date <= state.bounds.hi);
  const isShown = (node) => FACETS.filter((f) => f.of === FACET_NODES).every((f) => facetAllows(f, node))
    && !state.hiddenNodes.has(node.id) && (!state.isolate || state.isolate.has(node.id))
    && (!state.queryNodes || state.queryNodes.has(node.id)) && inPeriod(node);
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
    return { graph, nodes, relations, time: dateNodes(graph, nodes) };   // RQ-GXP-006: once every node exists
  }

  // ---- time (TASK-GXP-005: RQ-GXP-006, RQ-GXP-009; DEC-GXP-003, DEC-GXP-004) -----------------------------------
  const DAY_MS = 86_400_000;
  const RECENT_DAYS = [7, 30];                     // the Time menu's shortcuts
  const ID_TIME_BAR = "time-bar";
  const ID_TIME_START = "time-start";
  const ID_TIME_END = "time-end";
  const PERCENT = 100;

  function dateNodes(graph, nodes) {
    /* DEC-GXP-004: each node's date is its earliest commit in history.interventions, a node without rows the history's first
       commit; returns the history's first and last instants and its days, or null when the graph holds no history. */
    const history = graph.history;
    if (!history?.commits?.length) return null;
    const times = history.commits.map((c) => Date.parse(c.date));
    const limits = history.limits || {};
    const first = Date.parse(limits.first) || Math.min(...times);
    const last = Date.parse(limits.last) || Math.max(...times);
    for (const node of nodes.values()) node.date = first;
    for (const [scope, key] of [["elements", (id) => id], ["files", (path) => path],
                                ["functions", (index) => functionId(graph, Number(index))]]) {
      for (const [id, rows] of Object.entries(history.interventions?.[scope] || {})) {
        const node = nodes.get(key(id));
        if (node && rows.length) node.date = Math.min(...rows.map(([index]) => times[index]));
      }
    }
    const day0 = localMidnight(first);
    const sorted = [...nodes.values()].map((n) => n.date).sort((a, b) => a - b);   // DEC-GXP-006: to tell when the shown set changes
    return { first, last, day0, days: Math.round((localMidnight(last) - day0) / DAY_MS), sorted };
  }

  // Days are the reader's calendar days, counted on the calendar so that a change of summer time shifts no date
  const localMidnight = (instant) => {
    const d = new Date(instant);
    return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  };
  const dayOf = (instant) => Math.round((localMidnight(instant) - state.model.time.day0) / DAY_MS);
  const dayStart = (day) => {
    const d = new Date(state.model.time.day0);
    return new Date(d.getFullYear(), d.getMonth(), d.getDate() + day).getTime();
  };
  const pad2 = (n) => String(n).padStart(2, "0");
  const isoDay = (instant) => {
    const d = new Date(instant);
    return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
  };
  const hasTime = () => Boolean(state.model?.time);

  function renderTimeBar(startDay, endDay) {
    /* The handles, the filled period between them and its first and last days. */
    const { days } = state.model.time;
    $(ID_TIME_START).value = String(startDay);
    $(ID_TIME_END).value = String(endDay);
    const share = (day) => (days ? (day / days) * PERCENT : 0);
    $("time-fill").style.left = `${share(startDay)}%`;
    $("time-fill").style.right = `${PERCENT - share(endDay)}%`;
    renderCursor();
  }

  function setPeriodDays(startDay, endDay) {
    /* RQ-GXP-006: the period from the first to the last day, both included; the whole history is no period at all. */
    const { days } = state.model.time;
    const start = Math.max(0, Math.min(startDay, days));
    const end = Math.max(start, Math.min(endDay, days));
    state.period = start === 0 && end === days ? null
      : { start: dayStart(start), end: dayStart(end + 1) - 1, startDay: start, endDay: end };
    renderTimeBar(start, end);
    refreshTime(true);
  }

  // ---- playback (TASK-GXP-006: RQ-GXP-007, RQ-GXP-008; DEC-GXP-006) ------------------------------------------
  const MS_PER_S = 1000;
  const SPEED_TOKENS = ["--c-time-speed-slow", "--c-time-speed-normal", "--c-time-speed-fast"];
  const SPEED_DEFAULT = 1;                         // the normal speed's place in SPEED_TOKENS
  const LABEL_PLAY = "Play";
  const LABEL_PAUSE = "Pause";
  const playback = { playing: false, loop: false, speed: 0, last: 0, frame: 0, key: "" };

  const periodRange = () => (state.period || { start: state.model.time.day0, end: dayStart(state.model.time.days + 1) - 1 });

  function updateBounds() {
    /* DEC-GXP-003: the shown dates: from the period's start, or the window before the cursor, to the cursor or the period's end. */
    if (!hasTime()) {
      state.bounds = null;
      return;
    }
    const { start, end } = periodRange();
    const hi = state.cursor === null ? end : Math.min(state.cursor, end);
    const lo = state.window ? Math.max(start, hi - state.window * DAY_MS) : start;
    state.bounds = state.period || state.cursor !== null || state.window ? { lo, hi } : null;
  }

  function countAtMost(instant) {
    /* The number of node dates up to the instant, by binary search on the sorted dates. */
    const sorted = state.model.time.sorted;
    let low = 0;
    let high = sorted.length;
    while (low < high) {
      const mid = (low + high) >> 1;
      if (sorted[mid] <= instant) low = mid + 1; else high = mid;
    }
    return low;
  }

  function refreshTime(force) {
    /* DEC-GXP-006: the views are redrawn only when the shown set changes, the cursor at every call. */
    updateBounds();
    const b = state.bounds;
    const key = b ? `${countAtMost(b.hi)}:${countAtMost(b.lo - 1)}` : "";
    if (force || key !== playback.key) {
      playback.key = key;
      refresh();
    }
    renderCursor();
  }

  function renderCursor() {
    const marker = $("time-cursor");
    marker.hidden = state.cursor === null;
    const days = state.model.time.days;
    if (state.cursor !== null && days) {
      const share = Math.min(1, Math.max(0, (state.cursor - state.model.time.day0) / DAY_MS / days));
      marker.style.left = `${share * PERCENT}%`;
    }
    // TASK-GXP-010: the days the handles show, which a drag moves before the period follows
    const handleDay = (id) => isoDay(dayStart(Number($(id).value)));
    const shown = `${handleDay(ID_TIME_START)} → ${handleDay(ID_TIME_END)}`;
    $("time-range").textContent = state.cursor === null ? shown : `${shown} · ${isoDay(state.cursor)}`;
    $("time-play").textContent = playback.playing ? LABEL_PAUSE : LABEL_PLAY;
  }

  function setCursor(instant) {
    state.cursor = instant;
    refreshTime(false);
  }

  function advance(seconds) {
    /* Moves the cursor as the frames of `seconds` would: at the end it starts again WHILE Loop is checked, else it stops there. */
    if (!playback.playing) return;
    const { start, end } = periodRange();
    let next = state.cursor + seconds * playback.speed * DAY_MS;
    if (next >= end) {
      if (playback.loop) {
        next = start;
      } else {
        next = end;
        playback.playing = false;
      }
    }
    setCursor(next);
  }

  function onFrame(now) {
    if (!playback.playing) return;
    advance((now - playback.last) / MS_PER_S);
    playback.last = now;
    if (playback.playing) playback.frame = requestAnimationFrame(onFrame);
  }

  function play() {
    if (!hasTime() || playback.playing) return;
    const { start, end } = periodRange();
    if (state.cursor === null || state.cursor >= end) state.cursor = start;
    playback.playing = true;
    playback.last = performance.now();
    refreshTime(false);
    playback.frame = requestAnimationFrame(onFrame);
  }

  function pause() {
    playback.playing = false;
    cancelAnimationFrame(playback.frame);
    if (hasTime()) renderCursor();
  }

  function stop() {
    pause();
    state.cursor = null;
    if (hasTime()) refreshTime(false);
  }

  function setupPlayback() {
    /* The speeds of the tokens, the normal one chosen; the controls wired. */
    $("time-speed").innerHTML = SPEED_TOKENS.map((token) => `<option value="${tokenNumber(token)}">${tokenNumber(token)} days/s</option>`).join("");
    $("time-speed").selectedIndex = SPEED_DEFAULT;
    playback.speed = Number($("time-speed").value);
    $("time-speed").addEventListener("change", (event) => { playback.speed = Number(event.target.value); });
    $("time-loop").addEventListener("change", (event) => { playback.loop = event.target.checked; });
    $("time-window").addEventListener("change", (event) => {
      state.window = Number(event.target.value);
      if (hasTime()) refreshTime(false);
    });
    $("time-play").addEventListener(EVENT_CLICK, () => (playback.playing ? pause() : play()));
    $("time-stop").addEventListener(EVENT_CLICK, stop);
  }

  function setupTimeBar() {
    /* RQ-GXP-009: no history, no time bar; otherwise its handles span the history's days. */
    $(ID_TIME_BAR).hidden = !hasTime();
    if (!hasTime()) return;
    const { days } = state.model.time;
    for (const id of [ID_TIME_START, ID_TIME_END]) $(id).max = String(days);
    renderTimeBar(0, days);
    refreshTime(true);                             // RQ-GXP-008: a window chosen before keeps applying to the new graph
  }

  // TASK-GXP-010: while a handle is dragged only the bar follows; the views wait until it rests or is released
  const TOKEN_TIME_SETTLE = "--c-time-settle";
  let settleTimer = 0;

  function onTimeHandle(event) {
    /* A handle dragged past the other pushes it along. */
    const start = Number($(ID_TIME_START).value);
    const end = Number($(ID_TIME_END).value);
    const [first, last] = event.target.id === ID_TIME_START ? [start, Math.max(start, end)] : [Math.min(start, end), end];
    clearTimeout(settleTimer);
    if (event.type === "change") {
      setPeriodDays(first, last);
      return;
    }
    renderTimeBar(first, last);
    settleTimer = setTimeout(() => setPeriodDays(first, last), tokenNumber(TOKEN_TIME_SETTLE));
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
    // RQ-TRC-145 (TASK-GXP-008): the generation time as the performance center shows it, its UTC value in the tooltip; no commit,
    // the graph being read from the working tree
    const when = new Date(meta.generatedAt);
    const readable = Number.isNaN(when.getTime()) ? meta.generatedAt || NO_VALUE
      : new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(when);
    const utc = (meta.generatedAt || NO_VALUE).replace("T", " ").replace(/Z$/, " UTC");
    // TASK-GXP-009: no counts here, the view's own count line says them
    $("graph-meta").innerHTML = `<span title="${escapeHtml(utc)}">Generated ${escapeHtml(readable)}</span>`;
    const summary = [["Elements", graph.elements.length], ["Sections", (graph.sections || []).length],
                     ["Files", (graph.files || []).length], ["Nodes", nodes.size], ["Relations", relations.length]];
    $("graph-summary").innerHTML = summary.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("");
    renderFacets();
    renderLegend();
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
        + ` title="Show or hide ${escapeHtml(value)} (${n}); with the query focused, write its term"`
        + `${state.off[facet.key].has(value) ? "" : " checked"}>${facet.key === FACET_TYPE ? `${swatch(value)}${typeLabel(value)}`
        : `<span>${escapeHtml(value)}</span>`}<span class="count">${n}</span></label></li>`).join("");
      // RQ-TRC-160 (TASK-TRC-141): every value of the facet checked or unchecked in one click
      const bulk = [[BULK_ALL, "All", "Check every value"], [BULK_NONE, "None", "Uncheck every value"]]
        .map(([action, label, tip]) => `<button type="button" class="facet-bulk" data-bulk="${action}" title="${tip} of ${facet.title}">${label}</button>`).join("");
      return `<fieldset class="facet" id="facet-${facet.key}" data-facet="${facet.key}"><legend class="panel-title">${facet.title}</legend>`
        + `<div class="facet-bulk-row">${bulk}</div><ul class="facet-values">${values}</ul></fieldset>`;
    }).join("");
  }

  function setFacet(key, checked) {
    /* Checks or unchecks every value of one facet, then applies it to every view (RQ-TRC-160). */
    const facet = FACETS.find((f) => f.key === key);
    state.off[key] = checked ? new Set() : new Set(facetCounts(facet).map(([value]) => value));
    renderFacets();
    refresh();
  }

  // ---- graph legend (RQ-TRC-165, TASK-TRC-145) ----------------------------------------------------------------
  function renderLegend() {
    /* The node types and relation kinds of the loaded graph, each with its count, drawn from the graph's tokens. */
    const { nodes, relations } = state.model;
    const typeCounts = new Map();
    for (const n of nodes.values()) typeCounts.set(n.type, (typeCounts.get(n.type) || 0) + 1);
    const kindCounts = new Map();
    for (const r of relations) kindCounts.set(r.kind, (kindCounts.get(r.kind) || 0) + 1);
    const count = (n) => `<span class="count">${n}</span>`;
    const types = TYPE_ORDER.filter((t) => typeCounts.has(t))
      .map((t) => `<li data-type="${t}">${swatch(t)}${typeLabel(t)}${count(typeCounts.get(t))}</li>`).join("");
    // RQ-GXP-005: a kind is a button choosing its colour
    const kinds = [...kindCounts.keys()].sort(compare)
      .map((k) => `<li data-kind="${escapeHtml(k)}"><button type="button" class="legend-kind" title="Choose the colour of the ${escapeHtml(KIND_NAMES[k] || k)} relations">`
        + `<span class="legend-line" aria-hidden="true"></span><span>${escapeHtml(KIND_NAMES[k] || k)}</span></button>`
        + `${count(kindCounts.get(k))}</li>`).join("");
    $(ID_LEGEND).querySelector(".legend-body").innerHTML = `<ul class="legend">${types}</ul><ul class="legend">${kinds}</ul>`;
    applyRelationColours();
  }

  function toggleLegend() {
    const legend = $(ID_LEGEND);
    const folded = legend.classList.toggle(CLASS_FOLDED);
    legend.querySelector(".legend-toggle").setAttribute("aria-expanded", String(!folded));
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
      + `<input id="saved-label" type="text" title="The button's label" value="${escapeHtml(item.label)}" required>`
      + `<label class="query-label" for="saved-query">Query</label>`
      + `<input id="saved-query" type="text" title="The query the button runs" spellcheck="false" value="${escapeHtml(item.query)}">`
      + `<button type="submit" class="button button-primary" title="Keep this button">Save</button>`
      + `<button type="button" class="button" data-saved="cancel" title="Close without saving">Cancel</button></form>`;
  }

  function renderSaved() {
    /* RQ-TRC-164 (TASK-TRC-144): every tool reads a word and has a tooltip naming its button. */
    const tool = (action, index, text, tip) => `<button type="button" class="saved-tool" data-saved="${action}" data-index="${index}"`
      + ` title="${tip}">${text}</button>`;
    const items = saved.list.map((q, i) => {
      const label = escapeHtml(q.label);
      const tools = saved.managing ? tool("edit", i, "Edit", `Edit the label and query of ${label}`)
        + tool("left", i, "Move left", `Move ${label} one place left`) + tool("right", i, "Move right", `Move ${label} one place right`)
        + tool("delete", i, "Delete", `Delete ${label}`) : "";
      return `<span class="saved-item"><button type="button" class="chip saved-run" data-index="${i}"`
        + ` title="Run: ${escapeHtml(q.query)}">${label}</button>${tools}</span>`;
    });
    const manage = saved.managing
      ? `<button type="button" class="button" data-saved="export" title="Save the buttons to a JSON file">Export…</button>`
        + `<button type="button" class="button" data-saved="import" title="Replace the buttons by those of an exported file">Import…</button>`
        + `<button type="button" class="button" data-saved="done" title="Stop editing the buttons">Done</button>`
      : `<button type="button" class="button" data-saved="manage" title="Edit, move, delete, export or import the buttons">Edit buttons</button>`;
    $(ID_SAVED).innerHTML = `${items.join("")}<button type="button" class="button" data-saved="new" title="Save the current query as a button">+ Save query</button>${manage}`
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
    return `<li><button type="button" class="relation-link" data-node="${escapeHtml(other)}" title="Select ${escapeHtml(other)}">`
      + `<span class="relation-head"><span>${outgoing ? "outgoing →" : "← incoming"}</span>`
      + `<span class="relation-end">${escapeHtml(other)}</span><span class="pill">${escapeHtml(relation.kind)}</span>`
      + `${field === NO_VALUE ? "" : `<span class="pill">${escapeHtml(field)}</span>`}</span>${proofs}</button></li>`;
  }

  // RQ-TRC-146, TASK-TRC-147: an UNDEFINED node's type property is its ID's prefix, not an artifact's type
  const undefinedNote = (node) => (node.type === TYPE_UNDEFINED ? `<p class="detail-empty">${escapeHtml(node.props.type
    ? `A cited ${node.props.type} ID, not defined in the index: no ${node.props.type} carries it.` : "An ID cited but not defined in the index.")}</p>` : "");

  function renderDetail() {
    const panel = $(ID_DETAIL);
    const node = state.selected && state.model.nodes.get(state.selected);
    if (!node) {
      panel.innerHTML = `<p class="detail-empty">Select a node in a view to see every property, its incoming and outgoing `
        + `relations, their link field and their proofs.</p>`;
      return;
    }
    const relations = [...node.outgoing.map((r) => relationItem(r, true)), ...node.incoming.map((r) => relationItem(r, false))];
    const actions = [[ACTION_HIDE, "Hide", "Hide this node in every view"],
                     [ACTION_ISOLATE, "Isolate neighbourhood", "Show only this node and the nodes one relation away"],
                     [ACTION_WIDEN, "Widen by one hop", "Add the nodes one more relation away"]]
      .map(([action, label, tip]) => `<button type="button" class="button" data-action="${action}" title="${tip}">${label}</button>`).join("");
    panel.innerHTML = `${detailHead(node)}<div class="detail-actions">${actions}</div>${propertiesHtml(node)}`
      + `<h2 class="panel-title">Relations (${relations.length})</h2><ul class="relations">${relations.join("")}</ul>`;
  }

  // RQ-TRC-154, RQ-TRC-167 (TASK-TRC-150): the head and properties the detail panel and the hover tooltip share
  const detailHead = (node) => `${typeLabel(node.type)}<p class="detail-id">${escapeHtml(node.id)}</p>`
    + `<p class="detail-title">${escapeHtml(node.props.title || "")}</p>${undefinedNote(node)}`;

  const propertiesHtml = (node) => `<h2 class="panel-title">Properties</h2><dl class="properties">${Object.keys(node.props).sort(compare)
    .map((k) => `<dt>${escapeHtml(k)}</dt><dd>${escapeHtml(propertyValue(node.props[k]))}</dd>`).join("")}</dl>`;

  // ---- hover tooltip (RQ-TRC-167, TASK-TRC-150) ---------------------------------------------------------------
  let tipTimer = null;

  function showTip(node) {
    showTipAt(node.id(), node.renderedPosition());
  }

  function showTipAt(id, at) {
    /* The hovered node's head and properties beside it, inside the shown graph view, 2D or 3D (RQ-GXP-012); the selection
       is left as it is. The view's canvas has the view's name as its ID. */
    const tip = $(ID_TIP);
    $(`view-${state.view}`).append(tip);
    tip.innerHTML = detailHead(state.model.nodes.get(id)) + propertiesHtml(state.model.nodes.get(id));
    const gap = tokenNumber(TOKEN_NODE_SIZE);
    tip.hidden = false;
    const view = $(state.view);
    const left = Math.min(at.x + gap, view.clientWidth - tip.offsetWidth);
    const top = Math.min(at.y + gap, view.clientHeight - tip.offsetHeight);
    tip.style.left = Math.max(0, left) + UNIT_PX;
    tip.style.top = Math.max(0, top) + UNIT_PX;
  }

  function hideTip() {
    clearTimeout(tipTimer);
    tipTimer = null;
    $(ID_TIP).hidden = true;
  }

  function onNodeOver(event) {
    hideTip();
    tipTimer = setTimeout(() => showTip(event.target), tokenNumber(TOKEN_TIP_DELAY));
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
    const nodes = [...model.nodes.values()].map((n) => ({ group: "nodes", data: { id: n.id, [DATA_COLOUR]: typeColour(n.type) },
                                                          position: { ...model.positions.get(n.id) } }));
    const edges = model.relations.map((r, i) => ({ group: "edges", data: { id: `r${i}`, [DATA_INDEX]: i, source: r.source, target: r.target,
      kind: r.kind, [DATA_COLOUR]: relationColour(r.kind) } }));   // RQ-GXP-005: the reader's colour or the kind's token
    return [...nodes, ...edges];
  }

  function applyVisibility() {
    /* Nodes and relations of the graph view follow the facets, the query and the hidden list, as the tables do
       (RQ-TRC-151, TASK-TRC-140): an edge's index in the model is its Cytoscape ID. */
    applyVisibility3d();                           // RQ-GXP-011: the 3D view follows the same filters
    if (!cy) return;
    cy.batch(() => {
      cy.nodes().forEach((n) => n.toggleClass(CLASS_HIDDEN, !isShown(state.model.nodes.get(n.id()))));
      cy.edges().forEach((e) => e.toggleClass(CLASS_HIDDEN, !isRelationShown(state.model.relations[e.data(DATA_INDEX)])));
    });
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
    cy.on("cxttap", openMenu);                                                         // RQ-TRC-163
    cy.on("tap viewport", closeMenu);
    cy.on("mouseover", SELECTOR_NODE, onNodeOver);                                     // RQ-TRC-167
    cy.on("mouseout", SELECTOR_NODE, hideTip);
    cy.on("viewport grab cxttap", hideTip);
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
  // ---- 3D view (RQ-GXP-011; ADR-GXP-002: DEC-GXP-008, DEC-GXP-009) -----------------------------------------------
  const XYZ = 3;                                   // DEC-GXP-008: a position's components
  const RGBA = 4;                                  // DEC-GXP-008: a vertex colour with its alpha
  const ALPHA_INDEX = 3;
  const ALPHA_SHOWN = 1;
  const ALPHA_HIDDEN = 0;
  const HALF = 0.5;
  const FULL_TURN = 2 * Math.PI;
  const POLE_MARGIN = 0.01;                        // DEC-GXP-009: radians kept off the poles, so that "up" stays defined
  const NEAR_RATIO = 1e-3;                         // the camera's near and far planes, as fractions and multiples of its distance
  const FAR_RATIO = 10;
  const WHEEL_NOTCH = 100;                         // DEC-GXP-009: deltaY of one wheel notch, as Cytoscape reads it
  const BUTTON_MIDDLE = 1;
  const START_THETA = Math.PI / 4;                 // DEC-GXP-009: the opening view, from the front right and above
  const START_PHI = Math.PI / 3;
  const ATTR_SCALE = "pointScale";                 // DEC-GXP-011: the per-point size factor of the shader
  const g3 = { renderer: null, scene: null, camera: null, points: null, lines: null, ids: [], index: new Map(), drag: null,
               orbit: { theta: START_THETA, phi: START_PHI, zoom: 1, target: [0, 0, 0] } };

  // ---- 3D dimensions (RQ-GXP-013, RQ-GXP-009; DEC-GXP-011) ----------------------------------------------------
  const DIM_ROLES = ["height", "angle", "radius", "colour", "size"];
  const DIM_ROLE_LABELS = { height: "Height", angle: "Angle", radius: "Radius", colour: "Colour", size: "Size" };
  const DIM_NUMBER = "number";
  const DIM_CATEGORY = "category";
  const RADIUS_FLOOR = 0.1;                        // a numeric radius keeps its lowest points off the axis
  // The process layer of each node type: requirements, architecture, plan, the documents' sections, the code
  const LAYER_ORDER = ["requirements", "architecture", "plan", "documents", "code", "undefined"];
  const LAYER_OF = { FTR: LAYER_ORDER[0], RQ: LAYER_ORDER[0], ADR: LAYER_ORDER[1], DEC: LAYER_ORDER[1], PLAN: LAYER_ORDER[2],
                     TASK: LAYER_ORDER[2], [TYPE_SECTION]: LAYER_ORDER[3], [TYPE_FILE]: LAYER_ORDER[4], [TYPE_FUNCTION]: LAYER_ORDER[4],
                     [TYPE_UNDEFINED]: LAYER_ORDER[5] };

  function historyRows(model) {
    /* Each node's history rows, [commit index, changed lines], from history.interventions (DEC-GXP-004); cached. */
    if (model.rows) return model.rows;
    const graph = model.graph;
    model.rows = new Map();
    for (const [scope, key] of [["elements", (id) => id], ["files", (path) => path],
                                ["functions", (index) => functionId(graph, Number(index))]]) {
      for (const [id, rows] of Object.entries(graph.history?.interventions?.[scope] || {})) model.rows.set(key(id), rows);
    }
    return model.rows;
  }

  const rowsOf = (model, n) => historyRows(model).get(n.id) || [];
  const commitOf = (model, index) => model.graph.history.commits[index];
  const mostFrequent = (values) => {
    const counts = new Map();
    for (const v of values) counts.set(v, (counts.get(v) || 0) + 1);
    return [...counts].sort((a, b) => b[1] - a[1])[0]?.[0];
  };

  // DEC-GXP-011: each dimension, a function from a node to a number or a category; `history` ones need --history
  const DIMENSIONS = [
    { key: "first", label: "First commit date", kind: DIM_NUMBER, history: true, of: (n) => n.date },
    { key: "last", label: "Last commit date", kind: DIM_NUMBER, history: true,
      of: (n, m) => Math.max(n.date, ...rowsOf(m, n).map(([i]) => Date.parse(commitOf(m, i).date))) },
    { key: "commits", label: "Commit count", kind: DIM_NUMBER, history: true, of: (n, m) => rowsOf(m, n).length },
    { key: "lines", label: "Changed lines", kind: DIM_NUMBER, history: true, of: (n, m) => rowsOf(m, n).reduce((s, [, l]) => s + l, 0) },
    { key: "relations", label: "Relation count", kind: DIM_NUMBER, of: (n) => n.incoming.length + n.outgoing.length },
    { key: "tri", label: "Trigram", kind: DIM_CATEGORY, of: (n) => n.props.tri || NO_VALUE },
    { key: "type", label: "Type", kind: DIM_CATEGORY, order: TYPE_ORDER, of: (n) => n.type },
    { key: "status", label: "Status", kind: DIM_CATEGORY, of: (n) => n.props.status || NO_VALUE },
    { key: "author", label: "Main author", kind: DIM_CATEGORY, history: true, of: (n, m) => {
      const who = mostFrequent(rowsOf(m, n).flatMap(([i]) => [commitOf(m, i).author, ...(commitOf(m, i).coAuthors || [])]));
      return who === undefined ? NO_VALUE : m.graph.history.people?.[who]?.name || NO_VALUE;
    } },
    { key: "authorKind", label: "Author kind", kind: DIM_CATEGORY, history: true,
      of: (n, m) => mostFrequent(rowsOf(m, n).map(([i]) => commitOf(m, i).kind)) || NO_VALUE },
    { key: "tier", label: "Task tier", kind: DIM_CATEGORY, of: (n) => n.props.tier || NO_VALUE },
    { key: "layer", label: "Layer", kind: DIM_CATEGORY, order: LAYER_ORDER, of: (n) => LAYER_OF[n.type] },
  ];
  const dimension = (key) => DIMENSIONS.find((d) => d.key === key);
  const dimSelects = () => document.querySelectorAll(".graph3d-control[data-role]");

  function defaultDims(model) {
    /* RQ-GXP-013: height by first commit date, by relation count without history (RQ-GXP-009). */
    return { height: model.time ? "first" : "relations", angle: "tri", radius: "layer", colour: "type", size: "type" };
  }

  function renderDims() {
    /* Each choice lists every dimension, the history's disabled when the graph has none, and shows the current one. */
    for (const select of dimSelects()) {
      select.innerHTML = DIMENSIONS.map((d) => `<option value="${d.key}"${d.history && !state.model.time ? " disabled" : ""}>`
        + `${escapeHtml(d.label)}</option>`).join("");
      select.value = g3.dims[select.dataset.role];
    }
  }

  function scaleOf(key, model) {
    /* A dimension over the nodes: per node, t in [0, 1] and its category's slot; with the category count (1 for numbers). */
    const dim = dimension(key);
    const nodes = [...model.nodes.values()];
    const values = new Map(nodes.map((n) => [n.id, dim.of(n, model)]));
    if (dim.kind === DIM_NUMBER) {
      const all = [...values.values()];
      const low = Math.min(...all);
      const span = Math.max(...all) - low || 1;
      return { count: 1, slot: () => 0, t: (id) => (values.get(id) - low) / span };
    }
    const present = new Set(values.values());
    const order = dim.order ? dim.order.filter((c) => present.has(c)) : [...present].sort(compare);
    const slots = new Map(order.map((c, i) => [c, i]));
    const last = Math.max(order.length - 1, 1);
    return { count: order.length, slot: (id) => slots.get(values.get(id)), t: (id) => slots.get(values.get(id)) / last };
  }

  function place3d(model) {
    /* Each node's [x, y, z] from the reader's height, angle and radius dimensions (DEC-GXP-011). */
    const extent = tokenNumber("--c-graph3d-extent");
    const [height, angle, radius] = ["height", "angle", "radius"].map((role) => scaleOf(g3.dims[role], model));
    const turn = (id) => (angle.count > 1 ? angle.slot(id) / angle.count : angle.t(id)) * FULL_TURN;
    const away = (id) => (radius.count > 1 ? (radius.slot(id) + 1) / radius.count : RADIUS_FLOOR + (1 - RADIUS_FLOOR) * radius.t(id));
    return new Map([...model.nodes.keys()].map((id) => {
      const r = away(id) * extent * HALF;
      return [id, [r * Math.cos(turn(id)), (height.t(id) - HALF) * extent, r * Math.sin(turn(id))]];
    }));
  }

  function pointColours(model) {
    /* DEC-GXP-011: the type colours by type; a category's slot takes the type colours in turn; a number goes from the low to
       the high colour token. */
    const scale = scaleOf(g3.dims.colour, model);
    if (g3.dims.colour === "type") return (id) => typeColour(model.nodes.get(id).type);
    if (scale.count > 1) return (id) => typeColour(TYPE_ORDER[scale.slot(id) % TYPE_ORDER.length]);
    const low = new window.THREE.Color(cssValue("--c-graph3d-colour-low"));
    const high = new window.THREE.Color(cssValue("--c-graph3d-colour-high"));
    return (id) => `#${low.clone().lerp(high, scale.t(id)).getHexString()}`;
  }

  function pointScales(model) {
    /* DEC-GXP-011: a point's size factor between the size tokens: a larger number is larger, a former category larger. */
    const scale = scaleOf(g3.dims.size, model);
    const min = tokenNumber("--c-graph3d-size-min");
    const max = tokenNumber("--c-graph3d-size-max");
    return (id) => (scale.count > 1 ? max - scale.t(id) * (max - min) : min + scale.t(id) * (max - min));
  }

  function setDimension(role, key) {
    /* RQ-GXP-013: the reader's choice redraws the 3D view's points and lines; the camera is kept. */
    g3.dims[role] = key;
    if (!g3.renderer) return;
    disposeScene3d();
    buildScene3d();
    applyVisibility3d();
  }

  function setColour(array, at, css, alpha) {
    const colour = new window.THREE.Color(css);
    array.set([colour.r, colour.g, colour.b, alpha], at * RGBA);
  }

  function paintLines() {
    /* Every 3D line takes its kind's colour, the reader's or the token (RQ-GXP-005), keeping its alpha. */
    if (!g3.lines) return;
    const colours = g3.lines.geometry.getAttribute("color");
    state.model.relations.forEach((r, i) => {
      const css = relationColour(r.kind);
      for (const end of [0, 1]) setColour(colours.array, 2 * i + end, css, colours.array[(2 * i + end) * RGBA + ALPHA_INDEX]);
    });
    colours.needsUpdate = true;
    render3d();
  }

  function buildScene3d() {
    /* Two buffers whatever the graph's size: one Points, one LineSegments, coloured per vertex (DEC-GXP-008). */
    const THREE = window.THREE;
    const places = place3d(state.model);
    g3.ids = [...state.model.nodes.keys()];
    g3.index = new Map(g3.ids.map((id, i) => [id, i]));
    const nodePos = new Float32Array(g3.ids.length * XYZ);
    const nodeCol = new Float32Array(g3.ids.length * RGBA);
    const nodeScale = new Float32Array(g3.ids.length);
    const colourOf = pointColours(state.model);
    const scaleOfPoint = pointScales(state.model);
    g3.ids.forEach((id, i) => {
      nodePos.set(places.get(id), i * XYZ);
      setColour(nodeCol, i, colourOf(id), ALPHA_SHOWN);
      nodeScale[i] = scaleOfPoint(id);
    });
    const relations = state.model.relations;
    const linePos = new Float32Array(relations.length * 2 * XYZ);
    relations.forEach((r, i) => linePos.set([...places.get(r.source), ...places.get(r.target)], i * 2 * XYZ));
    const geometry = (pos, col) => new THREE.BufferGeometry().setAttribute("position", new THREE.BufferAttribute(pos, XYZ))
      .setAttribute("color", new THREE.BufferAttribute(col, RGBA));
    const material = { vertexColors: true, transparent: true, depthWrite: false };
    const pointMaterial = new THREE.PointsMaterial({ ...material, size: tokenNumber("--c-graph3d-point-size"), sizeAttenuation: false });
    pointMaterial.onBeforeCompile = (shader) => {  // DEC-GXP-011: a size factor per point
      shader.vertexShader = `attribute float ${ATTR_SCALE};\n${shader.vertexShader.replace("gl_PointSize = size;",
                                                                                            `gl_PointSize = size * ${ATTR_SCALE};`)}`;
    };
    g3.points = new THREE.Points(geometry(nodePos, nodeCol).setAttribute(ATTR_SCALE, new THREE.BufferAttribute(nodeScale, 1)),
                                 pointMaterial);
    g3.lines = new THREE.LineSegments(geometry(linePos, new Float32Array(relations.length * 2 * RGBA)),
                                      new THREE.LineBasicMaterial(material));
    g3.scene = new THREE.Scene();
    g3.scene.add(g3.lines, g3.points);
    paintLines();
  }

  function applyVisibility3d() {
    /* What isShown refuses gets alpha 0; the buffers are kept (DEC-GXP-008, DEC-GXP-003). */
    if (!g3.points) return;
    const alpha = (shown) => (shown ? ALPHA_SHOWN : ALPHA_HIDDEN);
    const nodes = g3.points.geometry.getAttribute("color");
    g3.ids.forEach((id, i) => { nodes.array[i * RGBA + ALPHA_INDEX] = alpha(isShown(state.model.nodes.get(id))); });
    const lines = g3.lines.geometry.getAttribute("color");
    state.model.relations.forEach((r, i) => {
      for (const end of [0, 1]) lines.array[(2 * i + end) * RGBA + ALPHA_INDEX] = alpha(isRelationShown(r));
    });
    nodes.needsUpdate = true;
    lines.needsUpdate = true;
    render3d();
  }

  // ---- 3D projections (RQ-GXP-014; DEC-GXP-012) ----------------------------------------------------------------
  const ISOMETRIC_PHI = Math.acos(1 / Math.sqrt(3));   // the polar angle of the cube's diagonal: equal axes on screen
  const HALF_TURN = Math.PI;
  const DEGREES = 180;
  // Perspective and Orthographic keep the angles; the others are orthographic presets of them
  const PROJECTIONS = [
    { label: "Perspective", tip: "Draw the 3D view in perspective, the far points smaller", ortho: false },
    { label: "Orthographic", tip: "Draw the 3D view without perspective, from the same angle", ortho: true },
    { label: "Isometric", tip: "Look along the cube's diagonal, without perspective", ortho: true, theta: HALF_TURN / 4, phi: ISOMETRIC_PHI },
    { label: "Top", tip: "Look down the height axis, the angle sectors seen from above", ortho: true, theta: 0, phi: POLE_MARGIN },
    { label: "Front", tip: "Look along the depth axis, the heights level", ortho: true, theta: 0, phi: HALF_TURN / 2 },
    { label: "Side", tip: "Look along the width axis, the heights level", ortho: true, theta: HALF_TURN / 2, phi: HALF_TURN / 2 },
  ];

  function setProjection(projection) {
    /* RQ-GXP-014: switches to the perspective or the orthographic camera, then to the preset's angles if it has any. */
    g3.camera = projection.ortho ? g3.ortho : g3.perspective;
    if (projection.theta !== undefined) Object.assign(g3.orbit, { theta: projection.theta, phi: projection.phi });
    render3d();
  }

  function frameOrtho(distance) {
    /* DEC-GXP-012: the orthographic frustum shows at the target what the perspective one shows there. */
    const half = distance * Math.tan((tokenNumber("--c-graph3d-fov") * Math.PI) / DEGREES / 2);
    Object.assign(g3.ortho, { left: -half * g3.aspect, right: half * g3.aspect, top: half, bottom: -half });
  }

  function placeCamera() {
    /* DEC-GXP-009: the camera on a sphere around the target, its radius the opening distance divided by the zoom. */
    const { theta, phi, zoom, target } = g3.orbit;
    const distance = tokenNumber("--c-graph3d-distance") * tokenNumber("--c-graph3d-extent") / zoom;
    if (g3.camera === g3.ortho) frameOrtho(distance);
    g3.camera.position.set(target[0] + distance * Math.sin(phi) * Math.sin(theta), target[1] + distance * Math.cos(phi),
                           target[2] + distance * Math.sin(phi) * Math.cos(theta));
    g3.camera.near = distance * NEAR_RATIO;
    g3.camera.far = distance * FAR_RATIO;
    g3.camera.updateProjectionMatrix();
    g3.camera.lookAt(...target);
  }

  function render3d() {
    if (!g3.renderer) return;
    placeCamera();
    g3.renderer.render(g3.scene, g3.camera);
  }

  function resize3d() {
    const box = $(VIEW_GRAPH3D);
    if (!g3.renderer || !box.clientWidth || !box.clientHeight) return;
    g3.renderer.setSize(box.clientWidth, box.clientHeight);
    g3.aspect = box.clientWidth / box.clientHeight;
    g3.perspective.aspect = g3.aspect;
    render3d();
  }

  function onDrag3d(event) {
    /* Left drag rotates; middle or Shift drag pans in the screen's plane (DEC-GXP-009). */
    if (!g3.drag) return;
    const speed = tokenNumber("--c-graph3d-rotate-speed");
    const dx = event.clientX - g3.drag.x;
    const dy = event.clientY - g3.drag.y;
    if (!dx && !dy) return;
    g3.drag = { ...g3.drag, x: event.clientX, y: event.clientY, moved: true };
    const orbit = g3.orbit;
    if (g3.drag.pan) {
      const scale = speed * g3.camera.position.distanceTo(new window.THREE.Vector3(...orbit.target));
      const right = new window.THREE.Vector3().setFromMatrixColumn(g3.camera.matrix, 0).multiplyScalar(-dx * scale);
      const up = new window.THREE.Vector3().setFromMatrixColumn(g3.camera.matrix, 1).multiplyScalar(dy * scale);
      orbit.target = orbit.target.map((t, i) => t + right.getComponent(i) + up.getComponent(i));
    } else {
      orbit.theta -= dx * speed;
      orbit.phi = Math.min(Math.PI - POLE_MARGIN, Math.max(POLE_MARGIN, orbit.phi - dy * speed));
    }
    render3d();
  }

  function onWheel3d(event) {
    event.preventDefault();
    const zoom = g3.orbit.zoom * Math.exp((-event.deltaY / WHEEL_NOTCH) * tokenNumber("--c-graph-wheel-sensitivity"));
    g3.orbit.zoom = Math.min(tokenNumber("--c-graph-zoom-max"), Math.max(tokenNumber("--c-graph-zoom-min"), zoom));
    render3d();
  }

  function screenOf(id) {
    /* DEC-GXP-010: a point's position in the canvas, in CSS pixels; null when it is behind the camera or outside the view. */
    const v = new window.THREE.Vector3().fromBufferAttribute(g3.points.geometry.getAttribute("position"), g3.index.get(id))
      .project(g3.camera);
    if (Math.abs(v.x) > 1 || Math.abs(v.y) > 1 || Math.abs(v.z) > 1) return null;
    const canvas = g3.renderer.domElement;
    return { x: (v.x + 1) * HALF * canvas.clientWidth, y: (1 - v.y) * HALF * canvas.clientHeight };
  }

  function pick(x, y) {
    /* DEC-GXP-010: the shown point nearest to (x, y) within the pick radius, or null. */
    let best = null;
    let bestDistance = tokenNumber("--c-graph3d-pick-radius");
    for (const id of g3.ids) {
      if (!isShown(state.model.nodes.get(id))) continue;
      const at = screenOf(id);
      const distance = at ? Math.hypot(at.x - x, at.y - y) : Infinity;
      if (distance <= bestDistance) [best, bestDistance] = [id, distance];
    }
    return best;
  }

  const canvasPoint = (event) => {
    const box = g3.renderer.domElement.getBoundingClientRect();
    return { x: event.clientX - box.left, y: event.clientY - box.top };
  };

  function onHover3d(event) {
    /* RQ-GXP-012, RQ-TRC-167: the tooltip of the point under a resting pointer, after the tooltip delay. */
    if (g3.drag) return;
    const at = canvasPoint(event);
    const id = pick(at.x, at.y);
    if (id === g3.hovered) return;
    hideTip();
    g3.hovered = id;
    if (id) tipTimer = setTimeout(() => showTipAt(id, at), tokenNumber(TOKEN_TIP_DELAY));
  }

  function onRelease3d(event) {
    /* RQ-GXP-012: a press released where it started selects the point under it; a drag selects nothing. */
    const drag = g3.drag;
    g3.drag = null;
    if (!drag || drag.moved || event.button !== 0) return;
    closeMenu();
    const at = canvasPoint(event);
    const id = pick(at.x, at.y);
    if (id) select(id);
  }

  function onContext3d(event) {
    /* RQ-GXP-012, RQ-TRC-163: the node actions of the point under the pointer. */
    event.preventDefault();
    hideTip();
    const at = canvasPoint(event);
    const id = pick(at.x, at.y);
    if (id) openMenuAt(id, at, false); else closeMenu();
  }

  function wire3d(canvas) {
    canvas.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 && event.button !== BUTTON_MIDDLE) return;
      canvas.setPointerCapture(event.pointerId);
      hideTip();
      g3.drag = { x: event.clientX, y: event.clientY, moved: false, pan: event.button === BUTTON_MIDDLE || event.shiftKey };
    });
    canvas.addEventListener(EVENT_POINTER_MOVE, onDrag3d);
    canvas.addEventListener(EVENT_POINTER_MOVE, onHover3d);
    canvas.addEventListener(EVENT_POINTER_UP, onRelease3d);
    canvas.addEventListener("contextmenu", onContext3d);
    canvas.addEventListener("pointerleave", () => { g3.hovered = null; hideTip(); });
    canvas.addEventListener("wheel", onWheel3d, { passive: false });
    if (!g3.observer) {                            // the panel outlives a graph's canvas: observed once
      g3.observer = new ResizeObserver(resize3d);
      g3.observer.observe($(VIEW_GRAPH3D));
    }
  }

  function initGraph3d() {
    /* Draws the 3D view once three.js is loaded and its panel has a size; a new graph draws a new one. */
    if (g3.renderer || !state.model || !window.THREE || state.view !== VIEW_GRAPH3D) return;
    const box = $(VIEW_GRAPH3D);
    g3.renderer = new window.THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    g3.renderer.setPixelRatio(window.devicePixelRatio);
    g3.renderer.setClearColor(cssValue("--c-graph3d-bg"));
    g3.perspective = new window.THREE.PerspectiveCamera(tokenNumber("--c-graph3d-fov"), 1);
    g3.ortho = new window.THREE.OrthographicCamera();   // RQ-GXP-014, DEC-GXP-012
    g3.aspect = 1;
    g3.camera = g3.perspective;
    box.replaceChildren(g3.renderer.domElement);
    wire3d(g3.renderer.domElement);
    g3.dims = g3.dims || defaultDims(state.model);
    renderDims();
    buildScene3d();
    applyVisibility3d();
    resize3d();
  }

  function disposeScene3d() {
    for (const object of [g3.points, g3.lines]) {
      object.geometry.dispose();
      object.material.dispose();
    }
  }

  function disposeGraph3d() {
    g3.dims = null;                                // RQ-GXP-013: a new graph starts from the default dimensions
    if (!g3.renderer) return;
    disposeScene3d();
    g3.renderer.dispose();
    $(VIEW_GRAPH3D).replaceChildren();
    Object.assign(g3, { renderer: null, scene: null, points: null, lines: null, ids: [], index: new Map(), drag: null });
  }

  function camera3d() {
    const p = g3.camera.position;
    return { position: [p.x, p.y, p.z], target: [...g3.orbit.target],
             distance: p.distanceTo(new window.THREE.Vector3(...g3.orbit.target)) };
  }

  function renderHidden() {
    const chips = [...state.hiddenNodes].sort(compare).map((id) => `<button type="button" class="chip" data-unhide="${escapeHtml(id)}"`
      + ` aria-label="Show ${escapeHtml(id)} again" title="Show ${escapeHtml(id)} again">${escapeHtml(id)} ×</button>`);
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

  // ---- layouts and context menu (RQ-TRC-162, RQ-TRC-163; DEC-TRC-094, DEC-TRC-095; TASK-TRC-143) --------------
  function applyLayout(name) {
    /* Arranges the shown nodes with the type columns or a Cytoscape built-in layout, keeps their positions as moved
       positions, and frames them. */
    if (!cy) return;
    $(ID_LAYOUT).value = name;
    // RQ-TRC-166, DEC-TRC-094 (TASK-TRC-149): a layout drawn in its natural direction is transposed when the reader
    // chose the other one; a layout without a direction disables the choice.
    const natural = NATURAL_DIRECTION[name];
    $(ID_DIRECTION).disabled = !natural;
    const swap = Boolean(natural) && $(ID_DIRECTION).value !== natural;
    const transform = (node, p) => (swap ? { x: p.y, y: p.x } : p);
    if (name === LAYOUT_COLUMNS) {
      layoutPositions(state.model);
      cy.batch(() => cy.nodes().forEach((n) => n.position(transform(n, { ...state.model.positions.get(n.id()) }))));
    } else {
      shownNodes().layout({ name, animate: false, fit: false, transform }).run();
    }
    shownNodes().forEach((n) => state.model.positions.set(n.id(), { ...n.position() }));
    fitGraph();
  }

  function isolateHops(id, hops) {
    /* Shows only the node and those at most hops relations away from it, whatever is hidden (RQ-TRC-163). */
    let reached = new Set([id]);
    for (let k = 0; k < hops; k += 1) reached = new Set([...reached].flatMap((n) => [...neighbours(n)]));
    state.isolate = reached;
    select(id);
    refresh();
    arrangeAround(id);
  }

  function menuItems(nodeId, withLayouts) {
    const button = (action, label, tip) => `<button type="button" role="menuitem" data-menu="${action}" title="${tip}">${label}</button>`;
    const layouts = [...$(ID_LAYOUT).options].map((o) => button(`${MENU_LAYOUT}${o.value}`, o.textContent, `Arrange the shown nodes: ${o.textContent}`));
    const node = nodeId ? [`<div class="graph-menu-title">${escapeHtml(nodeId)}</div>`, button(MENU_SELECT, "Select", "Show this node in the detail panel"),
      button(ACTION_HIDE, "Hide", "Hide this node in every view"),
      ...HOPS.map((n) => button(`${MENU_HOPS}${n}`, `Neighbours, ${n} hop${n > 1 ? "s" : ""}`, `Show only the nodes at most ${n} relations away`)), "<hr>"] : [];
    if (!withLayouts) return node.slice(0, -1).join("");   // RQ-GXP-012: the 3D view has the node actions only
    return [...node, `<div class="graph-menu-title">Layout</div>`, ...layouts, "<hr>",
            button(MENU_FIT, "Fit", "Fit the shown nodes to the view")].join("");
  }

  function openMenu(event) {
    /* The menu at the pointer: a node's actions when a node was right-clicked, then the layouts and the fit. */
    const nodeId = event.target === cy ? null : event.target.id();
    openMenuAt(nodeId, event.renderedPosition || { x: cy.width() / 2, y: cy.height() / 2 }, true);
  }

  function openMenuAt(nodeId, at, withLayouts) {
    /* RQ-TRC-163, RQ-GXP-012: the menu inside the shown graph view, 2D or 3D. */
    const menu = $(ID_MENU);
    $(`view-${state.view}`).append(menu);
    menu.dataset.node = nodeId || "";
    menu.innerHTML = menuItems(nodeId, withLayouts);
    menu.style.left = at.x + UNIT_PX;
    menu.style.top = at.y + UNIT_PX;
    menu.hidden = false;
  }

  function closeMenu() {
    $(ID_MENU).hidden = true;
  }

  function onMenuClick(event) {
    const item = event.target.closest("[data-menu]");
    if (!item) return;
    const action = item.dataset.menu;
    const nodeId = $(ID_MENU).dataset.node;
    closeMenu();
    if (action.startsWith(MENU_LAYOUT)) applyLayout(action.slice(MENU_LAYOUT.length));
    else if (action.startsWith(MENU_HOPS)) isolateHops(nodeId, Number(action.slice(MENU_HOPS.length)));
    else ({ [MENU_FIT]: fitGraph, [MENU_SELECT]: () => select(nodeId), [ACTION_HIDE]: () => hide(nodeId) })[action]();
  }

  function showAll() {
    for (const key of Object.keys(state.off)) state.off[key] = new Set();
    state.hiddenNodes = new Set();
    state.isolate = null;
    renderFacets();
    query("");
  }

  // ---- menu bar (TASK-GXP-002: RQ-GXP-001, RQ-TRC-164; DEC-GXP-001) ------------------------------------------
  const ID_MENUBAR = "menubar";
  const SELECTOR_BAR_MENU = "[role=menu]";
  const SELECTOR_BAR_TITLE = "[data-menu-title]";
  const SELECTOR_BAR_ITEM = "[data-item]";
  const ATTR_EXPANDED = "aria-expanded";
  const KEY_DOWN = "ArrowDown";
  const KEY_UP = "ArrowUp";
  const ITEM_SEPARATOR = ":";
  const VIEW_ITEMS = [[VIEW_GRAPH, "Graph 2D"], [VIEW_GRAPH3D, "Graph 3D"], [VIEW_NODES, "Nodes"], [VIEW_RELATIONS, "Relations"]];   // RQ-GXP-010
  let barMenus = [];

  // RQ-GXP-001: each menu, its title and tooltip, and its items (label, tooltip, action, enabled test); null draws a separator
  function menuDefinitions() {
    const always = () => true;
    const loaded = () => Boolean(state.model);
    return [
      { name: "file", title: "File", tip: "Open a graph file, import or export the saved queries", items: [
        { label: "Open graph file…", tip: "Open an agnos-graph.json file from the disk; dropping it on the page works too",
          action: () => $("file-input").click(), enabled: always },
        { label: "Import saved queries…", tip: "Replace the saved query buttons by those of an exported file",
          action: () => $("saved-import-file").click(), enabled: always },
        { label: "Export saved queries…", tip: "Save the saved query buttons to a JSON file", action: downloadSaved, enabled: always },
      ] },
      { name: "view", title: "View", tip: "Choose the view, fit the graph", items: [
        ...VIEW_ITEMS.map(([view, label]) => ({ label, tip: `Show the ${label.toLowerCase()} view`, action: () => showView(view), enabled: always })),
        null,
        { label: "Fit", tip: "Fit the shown nodes to the graph view", action: fitGraph, enabled: () => state.view === VIEW_GRAPH && Boolean(cy) },
        null,                                                                                     // RQ-GXP-014
        ...PROJECTIONS.map((p) => ({ label: p.label, tip: p.tip, action: () => setProjection(p),
          enabled: () => state.view === VIEW_GRAPH3D && Boolean(g3.renderer) })),
      ] },
      { name: "filter", title: "Filter", tip: "Clear the query or show every node", items: [
        { label: "Clear query", tip: "Clear the query and show what the facets allow", action: () => query(""), enabled: loaded },
        { label: "Show all", tip: "Check every facet value, clear the query, the hidden nodes and the isolation", action: showAll, enabled: loaded },
      ] },
      { name: "time", title: "Time", tip: "Show only the nodes first changed in a period", items: [   // RQ-GXP-006, RQ-GXP-009
        { label: "Whole history", tip: "Show the nodes of every date", action: () => setPeriodDays(0, state.model.time.days), enabled: hasTime },
        ...RECENT_DAYS.map((n) => ({ label: `Last ${n} days`, tip: `Show only the nodes first changed in the last ${n} days of the history`,
          action: () => setPeriodDays(state.model.time.days - n + 1, state.model.time.days), enabled: hasTime })),
        null,                                                                                     // RQ-GXP-007
        { label: LABEL_PLAY, tip: "Play the period from its first day", action: play, enabled: () => hasTime() && !playback.playing },
        { label: LABEL_PAUSE, tip: "Pause the playback where it is", action: pause, enabled: () => playback.playing },
        { label: "Stop", tip: "Stop the playback and show the whole period again", action: stop, enabled: () => state.cursor !== null },
      ], enabled: hasTime, offTip: "Build the graph with --history to filter by time" },
      { name: "appearance", title: "Appearance", tip: "Choose the colour of each relation kind", items: [   // RQ-GXP-005
        ...KIND_ORDER.map((kind) => ({ label: `Colour of ${kind}…`, tip: `Choose the colour of the ${KIND_NAMES[kind]} relations in the graph and its legend`,
          action: () => chooseRelationColour(kind), enabled: () => Boolean(state.model) && state.model.relations.some((r) => r.kind === kind) })),
        null,
        { label: "Reset colours", tip: "Give every relation kind its default colour again",
          action: resetRelationColours, enabled: () => Object.keys(appearance.relationColours).length > 0 },
      ] },
      { name: "dimensions", title: "Dimensions", tip: "Choose what the height, angle, radius, colour and size of the 3D view show",
        items: DIM_ROLES.map((role) => ({ label: `${DIM_ROLE_LABELS[role]}…`, tip: `Choose what the ${role} of the 3D points shows`,   // RQ-GXP-013
          action: () => $(`dim-${role}`).focus(), enabled: () => state.view === VIEW_GRAPH3D && Boolean(g3.renderer) })) },
      { name: "help", title: "Help", tip: "The guide of each view, the licences and the About", items: [   // RQ-GXP-002
        { label: "Help", tip: "What the current view shows and how to use it", action: () => openHelp(state.view), enabled: always },
        null,
        { label: "Licenses", tip: "The licences of AGNOS and of the libraries the page loads", action: () => openHelp(HELP_LICENSES), enabled: always },
        { label: "About", tip: "AGNOS, its version and its author", action: () => openHelp(HELP_ABOUT), enabled: always },
      ] },
    ];
  }

  // ---- appearance (TASK-GXP-004: RQ-GXP-005, RQ-TRC-165; DEC-GXP-005) -----------------------------------------
  const COLOUR_STORE_KEY = "agnos-graph-explorer.relation-colours";
  const ID_RELATION_COLOUR = "relation-colour";
  const KIND_ORDER = [KIND_CONTAINS, KIND_REFS, KIND_CODE, KIND_CALL];
  const KIND_TOKEN = { [KIND_CONTAINS]: "contains", [KIND_REFS]: "cites", [KIND_CODE]: "code", [KIND_CALL]: "call" };   // --c-graph-edge-*
  const VAR_KIND_COLOUR = "--kind-colour";
  const appearance = { relationColours: {} };      // DEC-GXP-005: the reader's colours over the tokens, by relation kind

  // the reader's colour of a kind, else its design-system token (DEC-TRC-010: the tokens stay the defaults)
  const relationColour = (kind) => appearance.relationColours[kind] || cssValue(`--c-graph-edge-${KIND_TOKEN[kind] || KIND_TOKEN[KIND_REFS]}`);

  function applyRelationColours() {
    /* Every graph edge and legend line takes its kind's colour. */
    if (cy) cy.batch(() => cy.edges().forEach((e) => e.data(DATA_COLOUR, relationColour(e.data("kind")))));
    paintLines();                                  // RQ-GXP-011: the 3D lines too
    for (const item of $(ID_LEGEND).querySelectorAll("[data-kind]")) {
      const chosen = appearance.relationColours[item.dataset.kind];
      if (chosen) item.style.setProperty(VAR_KIND_COLOUR, chosen); else item.style.removeProperty(VAR_KIND_COLOUR);
    }
  }

  function storeRelationColours() {
    try {
      if (Object.keys(appearance.relationColours).length) localStorage.setItem(COLOUR_STORE_KEY, JSON.stringify(appearance.relationColours));
      else localStorage.removeItem(COLOUR_STORE_KEY);
    } catch (error) {
      $(ID_MESSAGE).textContent = `The colours could not be kept in this browser: ${error.message}`;
    }
  }

  function loadRelationColours() {
    /* The reader's colours from the browser's storage, kept only for known kinds; then drawn. */
    let stored = null;
    try {
      stored = JSON.parse(localStorage.getItem(COLOUR_STORE_KEY));
    } catch (error) {
      stored = null;
    }
    appearance.relationColours = Object.fromEntries(Object.entries(stored || {}).filter(([kind, colour]) => KIND_ORDER.includes(kind)
      && typeof colour === "string"));
    applyRelationColours();
  }

  function setRelationColour(kind, colour) {
    appearance.relationColours[kind] = colour;
    storeRelationColours();
    applyRelationColours();
  }

  function resetRelationColours() {
    appearance.relationColours = {};
    storeRelationColours();
    applyRelationColours();
  }

  function chooseRelationColour(kind) {
    /* Opens the browser's colour picker on the kind's current colour. */
    const input = $(ID_RELATION_COLOUR);
    input.dataset.kind = kind;
    input.value = relationColour(kind).toLowerCase();
    input.click();
  }

  // ---- help (TASK-GXP-003: RQ-GXP-002 to RQ-GXP-004; DEC-GXP-002), copied from the performance center's setupHelp ----
  const HELP_LICENSES = "licenses";
  const HELP_ABOUT = "about";
  const ATTR_CURRENT = "aria-current";
  // RQ-GXP-003, copied from DEC-TRC-058 and DEC-TRC-062: the brand tone of a licence's badge, and its SPDX page
  const LICENCE_TONE = { "AGPL-3.0": "green", MIT: "blue", "Apache-2.0": "yellow" };
  const TONE_DEFAULT = "light";
  const SPDX_URL = "https://spdx.org/licenses/{id}.html";
  const SPDX_ID = "{id}";
  const CLASS_BADGE = "licence-badge";
  const CLASS_BADGE_VALUE = "licence-badge-value";

  function showHelpTopic(topic) {
    for (const part of $("help-dialog").querySelectorAll("[data-help]")) part.hidden = part.dataset.help !== topic;
    for (const button of $("help-list").children) {
      if (button.dataset.topic === topic) button.setAttribute(ATTR_CURRENT, "true"); else button.removeAttribute(ATTR_CURRENT);
    }
    $("help-body").scrollTop = 0;
  }

  function openHelp(topic) {
    showHelpTopic(topic === VIEW_GRAPH3D ? VIEW_GRAPH : topic);   // RQ-GXP-010: the 3D view shares the Graph topic
    $("help-dialog").showModal();
  }

  function linkBadge(badge) {
    /* A badge of a tabled licence becomes a link to its SPDX page in a new tab; any other keeps no link. */
    const id = badge.querySelector(`.${CLASS_BADGE_VALUE}`).textContent;
    if (!Object.hasOwn(LICENCE_TONE, id)) return;
    const link = document.createElement("a");
    link.className = `${CLASS_BADGE} licence-badge-link`;
    link.href = SPDX_URL.replace(SPDX_ID, id);
    link.target = "_blank";
    link.rel = "noopener";
    link.append(...badge.childNodes);
    badge.replaceWith(link);
  }

  function renderLicences() {
    const list = $("licence-list");
    const record = JSON.parse($("library-record").textContent);
    list.insertAdjacentHTML("beforeend", record.map((lib) => `<span class="${CLASS_BADGE}"><span class="licence-badge-label">`
      + `${escapeHtml(lib.name)} ${escapeHtml(lib.version)}</span><span class="${CLASS_BADGE_VALUE}">${escapeHtml(lib.licence)}</span></span>`).join(""));
    for (const value of list.querySelectorAll(`.${CLASS_BADGE_VALUE}`)) value.dataset.tone = LICENCE_TONE[value.textContent] || TONE_DEFAULT;
    for (const badge of list.querySelectorAll(`.${CLASS_BADGE}`)) linkBadge(badge);
  }

  function setupHelp() {
    /* One topic button per guide; the help button opens the guide of the current view. */
    const guides = [...$("help-dialog").querySelectorAll("[data-help]")];
    $("help-list").innerHTML = guides.map((part) => `<button type="button" class="help-topic" data-topic="${part.dataset.help}"`
      + ` title="Show the guide: ${escapeHtml(part.dataset.title)}">${escapeHtml(part.dataset.title)}</button>`).join("");
    $("help-list").addEventListener(EVENT_CLICK, (event) => {
      const button = event.target.closest("[data-topic]");
      if (button) showHelpTopic(button.dataset.topic);
    });
    $("help-button").addEventListener(EVENT_CLICK, () => openHelp(state.view));
    $("help-close").addEventListener(EVENT_CLICK, () => $("help-dialog").close());   // the browser returns the focus to the opener
    renderLicences();
  }

  function renderMenuBar() {
    barMenus = menuDefinitions();
    const item = (entry, m, i) => (entry
      ? `<button type="button" role="menuitem" data-item="${m}${ITEM_SEPARATOR}${i}" title="${escapeHtml(entry.tip)}">${escapeHtml(entry.label)}</button>`
      : "<hr>");
    $(ID_MENUBAR).innerHTML = barMenus.map((menu, m) => `<div class="menubar-item">`
      + `<button type="button" class="menubar-title" role="menuitem" aria-haspopup="menu" ${ATTR_EXPANDED}="false"`
      + ` data-menu-title="${menu.name}" title="${escapeHtml(menu.tip)}">${menu.title}</button>`
      + `<div class="graph-menu menubar-menu" role="menu" data-menu="${menu.name}" aria-label="${menu.title}" hidden>`
      + `${menu.items.map((entry, i) => item(entry, m, i)).join("")}</div></div>`).join("");
  }

  function refreshMenuTitles() {
    /* RQ-GXP-009: a menu with an enabled test is disabled, with a tooltip saying why, when the loaded graph cannot use it. */
    for (const menu of barMenus.filter((m) => m.enabled)) {
      const on = menu.enabled();
      barTitle(menu.name).disabled = !on;
      barTitle(menu.name).title = on ? menu.tip : menu.offTip;
    }
  }

  const barEntry = (button) => {
    const [m, i] = button.dataset.item.split(ITEM_SEPARATOR).map(Number);
    return barMenus[m].items[i];
  };
  const barTitle = (name) => $(ID_MENUBAR).querySelector(`[data-menu-title="${name}"]`);
  const openBarMenu = () => $(ID_MENUBAR).querySelector(`${SELECTOR_BAR_MENU}:not([hidden])`);

  function showBarMenu(name) {
    /* Opens one menu, closes the others, and enables each item by its test on the current graph and view. */
    for (const menu of $(ID_MENUBAR).querySelectorAll(SELECTOR_BAR_MENU)) {
      const open = menu.dataset.menu === name;
      menu.hidden = !open;
      barTitle(menu.dataset.menu).setAttribute(ATTR_EXPANDED, String(open));
      if (open) for (const button of menu.querySelectorAll(SELECTOR_BAR_ITEM)) button.disabled = !barEntry(button).enabled();
    }
  }

  function closeBarMenus(returnFocus) {
    const open = openBarMenu();
    if (!open) return;
    showBarMenu(null);
    if (returnFocus) barTitle(open.dataset.menu).focus();
  }

  function focusBarItem(menu, step) {
    /* Moves the focus to the next or previous enabled item of an open menu, wrapping around. */
    const items = [...menu.querySelectorAll(`${SELECTOR_BAR_ITEM}:not(:disabled)`)];
    if (!items.length) return;
    const at = items.indexOf(document.activeElement);
    items[(at + step + items.length) % items.length].focus();
  }

  function onBarKey(event) {
    const titles = [...$(ID_MENUBAR).querySelectorAll(SELECTOR_BAR_TITLE)];
    const current = event.target.closest(".menubar-item")?.querySelector(SELECTOR_BAR_TITLE);
    if (!current) return;
    const side = { [KEY_RIGHT]: 1, [KEY_LEFT]: -1 }[event.key];
    const down = { [KEY_DOWN]: 1, [KEY_UP]: -1 }[event.key];
    if (side) {
      const next = titles[(titles.indexOf(current) + side + titles.length) % titles.length];
      if (openBarMenu()) showBarMenu(next.dataset.menuTitle);
      next.focus();
    } else if (down) {
      if (!openBarMenu()) showBarMenu(current.dataset.menuTitle);
      focusBarItem(openBarMenu(), down);
    } else if (event.key === KEY_ESCAPE) {
      closeBarMenus(true);
    } else {
      return;
    }
    event.preventDefault();
  }

  function onBarClick(event) {
    const title = event.target.closest(SELECTOR_BAR_TITLE);
    if (title) {
      const open = openBarMenu();
      showBarMenu(open && open.dataset.menu === title.dataset.menuTitle ? null : title.dataset.menuTitle);
      return;
    }
    const button = event.target.closest(SELECTOR_BAR_ITEM);
    if (!button || button.disabled) return;
    closeBarMenus(false);
    barEntry(button).action();
  }

  // ---- views --------------------------------------------------------------------------------------------------
  function showView(view) {
    state.view = view;
    for (const tab of document.querySelectorAll(SELECTOR_TAB)) tab.setAttribute(ATTR_SELECTED, String(tab.dataset.view === view));
    for (const name of VIEWS) $(`view-${name}`).classList.toggle(CLASS_ACTIVE, name === view);
    for (const control of document.querySelectorAll(".graph-control")) control.hidden = view !== VIEW_GRAPH;
    for (const control of document.querySelectorAll(".graph3d-control")) control.hidden = view !== VIEW_GRAPH3D;   // RQ-GXP-013
    if (state.model) renderTables();
    initGraph();
    if (view === VIEW_GRAPH3D) show3d();           // RQ-GXP-019, DEC-GXP-007: three.js on the first show only
  }

  // ---- 3D library (RQ-GXP-019, DEC-GXP-007) -------------------------------------------------------------------
  let threeLoading = null;                         // the promise of the one load of three.js

  function loadThree() {
    /* Loads the lazy library of the record once, by a script element checked by its integrity; resolves when its global is
       set, rejects with the panel's message when cdnjs cannot give it. */
    if (threeLoading) return threeLoading;
    const lib = JSON.parse($("library-record").textContent).find((l) => l.lazy && l.global === GLOBAL_THREE);
    threeLoading = new Promise((resolve, reject) => {
      if (window[GLOBAL_THREE]) return resolve(window[GLOBAL_THREE]);
      const script = document.createElement("script");
      Object.assign(script, { src: lib.url, integrity: lib.integrity, crossOrigin: "anonymous", referrerPolicy: "no-referrer" });
      script.onload = () => resolve(window[GLOBAL_THREE]);
      script.onerror = () => {
        $(VIEW_GRAPH3D).textContent = MESSAGE_NO_THREE;
        reject(new Error(MESSAGE_NO_THREE));
      };
      document.head.append(script);
    });
    return threeLoading;
  }

  // RQ-GXP-011: the 3D view is drawn once three.js is loaded; resolves when it is
  const show3d = () => loadThree().then(() => { initGraph3d(); resize3d(); }, () => {});

  function render() {
    renderHeader();
    renderTables();
    renderDetail();
    renderHidden();
  }

  // ---- loading (RQ-TRC-145, DEC-TRC-088) ----------------------------------------------------------------------
  function loadGraph(graph) {
    pause();                                       // RQ-GXP-007: a new graph is not played
    state.cursor = null;
    state.bounds = null;
    state.model = buildModel(graph);
    state.model.positions = new Map();
    state.selected = null;
    state.hiddenNodes = new Set();
    state.isolate = null;
    state.queryNodes = null;
    state.queryRelations = null;
    state.period = null;                           // RQ-GXP-006: a new graph shows its whole history
    if (cy) {
      cy.destroy();
      cy = null;
    }
    disposeGraph3d();                              // RQ-GXP-011: a new graph draws a new 3D view
    render();
    setupTimeBar();                                // RQ-GXP-006, RQ-GXP-009
    refreshMenuTitles();
    initGraph();
    initGraph3d();
    document.documentElement.dataset.firstViewMs = String(Math.round(performance.now()));   // RQ-TRC-158: read by the tests
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

  // ---- table columns (RQ-TRC-159, TASK-TRC-142) ---------------------------------------------------------------
  function freezeColumns(table) {
    /* On a table's first resize, every column keeps the width it has, and the table becomes fixed. */
    if (table.classList.contains(CLASS_RESIZED)) return;
    const cells = [...table.tHead.rows[0].cells];
    const widths = cells.map((th) => th.getBoundingClientRect().width);
    cells.forEach((th, i) => { th.style.width = widths[i] + UNIT_PX; });
    table.style.width = widths.reduce((a, b) => a + b, 0) + UNIT_PX;
    table.classList.add(CLASS_RESIZED);
  }

  function setColumnWidth(table, th, width) {
    /* A fixed table is as wide as its columns, so that one column grows without shrinking the others. */
    th.style.width = Math.max(tokenNumber(TOKEN_COLUMN_MIN), width) + UNIT_PX;
    table.style.width = [...table.tHead.rows[0].cells].reduce((sum, cell) => sum + Number.parseFloat(cell.style.width), 0) + UNIT_PX;
  }

  function wireColumns(table) {
    for (const th of table.tHead.rows[0].cells) {
      const handle = document.createElement("span");
      handle.className = "col-resize";
      handle.title = `Drag to resize the ${th.textContent} column`;
      th.appendChild(handle);
      handle.addEventListener(EVENT_CLICK, (event) => event.stopPropagation());   // a resize is no sort
      handle.addEventListener("pointerdown", (event) => {
        event.preventDefault();
        event.stopPropagation();
        freezeColumns(table);
        const startX = event.clientX;
        const start = th.getBoundingClientRect().width;
        handle.classList.add(CLASS_DRAGGING);
        const move = (e) => setColumnWidth(table, th, start + e.clientX - startX);
        const up = () => {
          handle.classList.remove(CLASS_DRAGGING);
          document.removeEventListener(EVENT_POINTER_MOVE, move);
          document.removeEventListener(EVENT_POINTER_UP, up);
        };
        document.addEventListener(EVENT_POINTER_MOVE, move);
        document.addEventListener(EVENT_POINTER_UP, up);
      });
    }
  }

  // ---- wiring -------------------------------------------------------------------------------------------------
  function wire() {
    for (const select of dimSelects()) select.addEventListener("change", () => setDimension(select.dataset.role, select.value));   // RQ-GXP-013
    // RQ-GXP-001, DEC-GXP-001: the menu bar
    renderMenuBar();
    refreshMenuTitles();                           // RQ-GXP-009: before any graph, the Time menu is disabled
    setupHelp();                                   // RQ-GXP-002
    for (const id of [ID_TIME_START, ID_TIME_END]) {                                   // RQ-GXP-006, TASK-GXP-010
      for (const type of ["input", "change"]) $(id).addEventListener(type, onTimeHandle);
    }
    setupPlayback();                               // RQ-GXP-007, RQ-GXP-008
    $(ID_MENUBAR).addEventListener(EVENT_CLICK, onBarClick);
    $(ID_MENUBAR).addEventListener(EVENT_KEYDOWN, onBarKey);
    document.addEventListener(EVENT_CLICK, (event) => { if (!event.target.closest(`#${ID_MENUBAR}`)) closeBarMenus(false); });
    wireColumns($(ID_NODE_TABLE));
    wireColumns($(ID_RELATION_TABLE));
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
    // RQ-TRC-162, RQ-TRC-163: the layout selector and the context menu
    $(ID_LAYOUT).addEventListener("change", () => applyLayout($(ID_LAYOUT).value));
    $(ID_DIRECTION).addEventListener("change", () => applyLayout($(ID_LAYOUT).value));          // RQ-TRC-166
    $(ID_MENU).addEventListener(EVENT_CLICK, onMenuClick);
    $(ID_LEGEND).querySelector(".legend-toggle").addEventListener(EVENT_CLICK, toggleLegend);   // RQ-TRC-165
    // RQ-GXP-005: a legend kind opens the colour picker, whose choice is drawn at once
    $(ID_LEGEND).addEventListener(EVENT_CLICK, (event) => {
      const kind = event.target.closest(".legend-kind");
      if (kind) chooseRelationColour(kind.closest("[data-kind]").dataset.kind);
    });
    $(ID_RELATION_COLOUR).addEventListener("input", (event) => setRelationColour(event.target.dataset.kind, event.target.value));
    $(VIEW_GRAPH).addEventListener("contextmenu", (event) => event.preventDefault());
    document.addEventListener(EVENT_KEYDOWN, (event) => { if (event.key === KEY_ESCAPE) closeMenu(); });
    document.addEventListener(EVENT_CLICK, (event) => { if (!event.target.closest(`#${ID_MENU}`)) closeMenu(); });
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
      const bulk = event.target.closest("[data-bulk]");
      if (bulk) {
        setFacet(bulk.closest("[data-facet]").dataset.facet, bulk.dataset.bulk === BULK_ALL);
        return;
      }
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
  loadRelationColours();                           // RQ-GXP-005
  showView(DEFAULT_VIEW);
  if (window.AGNOS_GRAPH && Array.isArray(window.AGNOS_GRAPH.elements)) loadGraph(window.AGNOS_GRAPH);
  else $(ID_MESSAGE).textContent = MESSAGE_NO_GRAPH;

  window.agnosExplorer = {                         // test hooks (RQ-TRC-145 to RQ-TRC-154)
    showView, select, loadText, hideTypes, hide, unhide, isolate, widen, showAll, query,
    saved: { list: () => saved.list, add: addSaved, edit: editSaved, move: moveSaved, remove: removeSaved, load: loadSaved,
             exportText, importText },                                       // RQ-TRC-153
    appearance: { load: loadRelationColours, set: setRelationColour, reset: resetRelationColours, relationColour },   // RQ-GXP-005
    time: { dayOf: (iso) => dayOf(Date.parse(iso)), dateOf: (id) => new Date(state.model.nodes.get(id).date).toISOString(),
            setPeriodDays, period: () => state.period,                                                           // RQ-GXP-006
            advance, cursor: () => state.cursor, setCursor: (iso) => setCursor(Date.parse(iso)) },               // RQ-GXP-007, RQ-GXP-008
    shownIds: () => [...state.model.nodes.values()].filter(isShown).map((n) => n.id),
    counts: () => ({ nodes: state.model ? state.model.nodes.size : 0, relations: state.model ? state.model.relations.length : 0 }),
    view3d: { ready: show3d, camera: camera3d, screenOf, pick, dims: () => ({ ...g3.dims }),   // RQ-GXP-013
              cameraKind: () => (g3.camera === g3.ortho ? "orthographic" : "perspective"),   // RQ-GXP-014
              project: (p) => { const s = new window.THREE.Vector3(...p).project(g3.camera); return { x: s.x, y: s.y }; },
              positionOf: (id) => [...g3.points.geometry.getAttribute("position").array.slice(g3.index.get(id) * XYZ, (g3.index.get(id) + 1) * XYZ)],   // RQ-GXP-019, RQ-GXP-011, RQ-GXP-012, DEC-GXP-007 to DEC-GXP-010
              shownIds: () => g3.ids.filter((id) => isShown(state.model.nodes.get(id))
                && g3.points.geometry.getAttribute("color").array[g3.index.get(id) * RGBA + ALPHA_INDEX] === ALPHA_SHOWN),
              shownRelations: () => { const a = g3.lines.geometry.getAttribute("color").array;
                                      return state.model.relations.filter((r, i) => a[2 * i * RGBA + ALPHA_INDEX] === ALPHA_SHOWN).length; } },
    graph: {                                       // RQ-TRC-150, DEC-TRC-090
      cy: () => cy,
      layout: applyLayout,                         // RQ-TRC-162
      move(id, x, y) { cy.$id(id).position({ x, y }); cy.$id(id).emit(EVENT_DRAG_FREE); },
      position: (id) => cy.$id(id).position(),
      shown: (id) => !cy.$id(id).hasClass(CLASS_HIDDEN),
      shownIds: () => shownNodes().map((n) => n.id()),
      shownEdgeCount: () => cy.edges().filter((e) => !e.hasClass(CLASS_HIDDEN)).length,   // RQ-TRC-151
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
