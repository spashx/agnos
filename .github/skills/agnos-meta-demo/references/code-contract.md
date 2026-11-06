# Code contract of the demo product (Roombook)

<!-- RQ-DMO-004, RQ-DMO-003 / ADR-DMO-001 (DEC-DMO-001, DEC-DMO-004) -->

Contract given to the code-generating sub-agents. The demo's process documents are in
`assets/content/agnos-process/`; the code goes in `assets/content/service/` (Python) and `assets/content/client/`
(TypeScript). Write original code: copy nothing from an existing project.

## Rules for every file
- Python 3.11, standard library only, type hints, `dataclasses`. Tests use `unittest` (no pytest).
- TypeScript for Node 22.18 or later, executable by type stripping: **erasable syntax only** (no `enum`, no
  `namespace`, no constructor parameter properties; declare fields, assign them in the constructor), relative
  imports with the `.ts` extension, tests with `node:test` and `node:assert/strict`.
- SOLID. No inline literal repeated or meaningful: every string and number is a named constant
  (`UPPER_SNAKE_CASE`) declared once, close to its use.
- Traceability: the first line of each file is a comment listing the requirement and decision IDs it
  implements, for example `# RQ-BKG-003, DEC-BKG-002 (ADR-BKG-001)` or `// RQ-CLI-004, DEC-CLI-002`. Cite
  only IDs defined in `assets/content/agnos-process/`. Each public class or function has a one-line docstring or
  comment with the requirement it serves.
- Tests are named in Gherkin: `test_given_<state>_when_<action>_then_<result>` (Python) or
  `test("given <state>, when <action>, then <result>", ...)` (TypeScript), with `# Given`, `# When`,
  `# Then` comments. At least one test per public function or method. A test never repeats the literal of
  a constant it checks: it imports the constant. Tests assert error `code` or attributes, never message text.
- Do not run git. Create only the files listed for your assignment, under the folders above.

## Python package `service/roombook/` (tests in `service/tests/`, with an empty `service/tests/__init__.py`)

| Task | Source files | Test files |
|---|---|---|
| TASK-BKG-001 | `../pyproject.toml`, `__init__.py`, `domain.py`, `errors.py`, `catalog.py` | `test_domain.py`, `test_catalog.py` |
| TASK-BKG-002 | `ports.py`, `memory_repository.py`, `rules/__init__.py`, `use_cases/__init__.py`, `use_cases/create_reservation.py` | `test_memory_repository.py`, `test_create_reservation.py` |
| TASK-BKG-003 | `rules/overlap_rule.py` | `test_overlap_rule.py` |
| TASK-BKG-004 | `rules/capacity_rule.py`, `rules/room_open_rule.py` | `test_capacity_rule.py`, `test_room_open_rule.py` |
| TASK-BKG-005 | `clock.py`, `use_cases/cancel_reservation.py` | `test_cancel_reservation.py` |
| TASK-BKG-007 | `atomic_file.py`, `file_repository.py` | `test_atomic_file.py`, `test_file_repository.py` |
| TASK-BKG-008 | `repository_factory.py` | `test_repository_factory.py` |
| TASK-NTF-001 | `events.py`, `publishing_create.py` | `test_events.py`, `test_publishing_create.py` |
| TASK-NTF-002 | `notifier.py`, `reminder_scheduler.py` | `test_notifier.py`, `test_reminder_scheduler.py` |
| TASK-NTF-003 | `retrying_notifier.py` | `test_retrying_notifier.py` |
| TASK-CLI-001 | `api.py` | `test_api.py` |

Run from `service/`: `python -m unittest discover -s tests -t .`. A file may use only modules of earlier
rows of the table (a task never needs a later one), except `test_api.py` which wires everything.

### Public API (exact names)
- `domain.py` (RQ-BKG-001, RQ-BKG-002, DEC-BKG-001): `ReservationStatus(str, Enum)` with `CONFIRMED`,
  `CANCELLED`; frozen dataclasses `Room(id, name, capacity, open=True)` (capacity below `MIN_CAPACITY = 1`
  raises `ValueError`), `ReservationRequest(room_id, organizer, start, end, attendees)` (`end` not after
  `start` raises `ValueError`), `Reservation(id, room_id, organizer, start, end, attendees,
  status=CONFIRMED)` with methods `overlaps(start, end) -> bool` (true when `self.start < end and start <
  self.end`) and `cancelled() -> Reservation`. Times are timezone-aware `datetime`.
- `errors.py` (RQ-BKG-003 to RQ-BKG-006): base `RoombookError(Exception)` with a class attribute `code`;
  subclasses `RoomNotFound`, `ReservationNotFound`, `ReservationConflict(conflicting_id)`,
  `CapacityExceeded`, `RoomClosed`, `ReservationAlreadyStarted`, with codes `ROOM_NOT_FOUND`,
  `RESERVATION_NOT_FOUND`, `CONFLICT`, `CAPACITY_EXCEEDED`, `ROOM_CLOSED`, `ALREADY_STARTED` as named
  constants. `ReservationConflict` exposes `conflicting_id`. The module contains **exactly this line**:
  `CONFLICT_MESSAGE_TEMPLATE = "room already booked by reservation {conflicting_id}"` and builds the
  message with `.format(conflicting_id=...)`.
- `catalog.py`: `RoomCatalog` with `add(room)` (duplicate id raises `ValueError`), `get(room_id)` (raises
  `RoomNotFound`), `list()` (sorted by id).
- `ports.py` (DEC-BKG-001): `Protocol`s `ReservationRepository` with `add(reservation)`, `get(id)` (raises
  `ReservationNotFound`), `update(reservation)`, `list_confirmed_for_room(room_id)`, `list_all()`; and
  `Clock` with `now() -> datetime`.
- `memory_repository.py` (DEC-BKG-003): `InMemoryReservationRepository` implementing the port with a dict.
- `rules/__init__.py` (DEC-BKG-002): `Protocol ReservationRule` with `check(room, request, existing)`
  returning `None` or raising a `RoombookError`; `load_rules() -> list[ReservationRule]` which uses
  `pkgutil.iter_modules` on the package, imports each module, takes its `RULE` instance and sorts by the
  module's `RULE_ORDER`.
- `rules/room_open_rule.py` (`RULE_ORDER = 10`), `rules/capacity_rule.py` (`RULE_ORDER = 20`, rejects
  `request.attendees > room.capacity`), `rules/overlap_rule.py` (`RULE_ORDER = 30`, checks the overlap against
  the list it receives, which holds only Confirmed reservations): each defines `RULE` at the bottom.
- `use_cases/create_reservation.py`: `CreateReservation(catalog, repository, rules, id_factory=uuid_id_factory)`
  with `execute(request) -> Reservation` (get room, read confirmed reservations of the room, run every rule,
  build a Confirmed `Reservation`, add it, return it); `uuid_id_factory()` returns a UUID string.
- `clock.py`: `SystemClock` implementing `Clock` with the current UTC time.
- `use_cases/cancel_reservation.py`: `CancelReservation(repository, clock)` with `execute(reservation_id)
  -> Reservation`: already Cancelled returns it unchanged; `clock.now()` at or after its start raises
  `ReservationAlreadyStarted`; otherwise stores and returns `reservation.cancelled()`.
- `atomic_file.py` (RQ-BKG-007, DEC-BKG-004): `write_atomically(path, content, before_replace=None)` writes
  `path + TEMP_SUFFIX` (`TEMP_SUFFIX = ".tmp"`), calls `before_replace()` if given, then `os.replace` to
  `path`.
- `file_repository.py`: `StorageCorrupted(RoombookError)` with code `STORAGE_CORRUPTED`;
  `FileReservationRepository(path)` implementing the port: loads at construction (missing file means empty;
  invalid JSON or wrong shape raises `StorageCorrupted`), rewrites the whole file through
  `write_atomically` after every `add` and `update`. JSON: `{"reservations": [{"id", "roomId",
  "organizer", "start", "end", "attendees", "status"}]}`, times in ISO 8601 with offset.
- `repository_factory.py`: `DATA_FILE_ENV = "ROOMBOOK_DATA_FILE"`; `create_repository(environ)` returns a
  `FileReservationRepository` on that path when the variable is set and non-empty, else an
  `InMemoryReservationRepository`.
- `events.py` (RQ-NTF-001, DEC-NTF-001): frozen dataclass `ReservationCreated(reservation)`; `EventBus` with
  `subscribe(handler)` and `publish(event)` (a handler that raises is logged with `logging` and the other
  handlers still run).
- `publishing_create.py`: `Protocol ReservationCreator` with `execute(request)`; `PublishingCreateReservation(inner,
  bus)` whose `execute` calls `inner.execute`, publishes `ReservationCreated(result)` after success, returns
  the result; nothing is published if `inner` raises.
- `notifier.py` (RQ-NTF-002, DEC-NTF-002): `Protocol Notifier` with `send(recipient, message)`;
  `ConsoleNotifier(stream=sys.stdout)` writes `"<recipient>: <message>"` and a newline.
- `reminder_scheduler.py`: contains **exactly this line** `REMINDER_LEAD_MINUTES = 15`, a
  `REMINDER_MESSAGE_TEMPLATE` constant, and `ReminderScheduler(repository, notifier, clock)` with
  `dispatch_due() -> int`: for each Confirmed reservation from `repository.list_all()` not yet reminded and
  with `start - lead <= clock.now() < start`, send one reminder to its organizer and remember it; return the
  number sent. Tests use the `REMINDER_LEAD_MINUTES` constant, and one test dispatches 1000 reminders and
  asserts the elapsed time is below a `MAX_DISPATCH_SECONDS` constant of the test.
- `retrying_notifier.py` (RQ-NTF-003): contains **exactly this line** `MAX_ATTEMPTS = 3`;
  `RetryingNotifier(inner, logger=None)` whose `send` calls `inner.send` up to `MAX_ATTEMPTS` times, logs one
  error after the last failure and never raises. Tests use the `MAX_ATTEMPTS` constant.
- `api.py` (RQ-CLI-005, DEC-CLI-001): `ReservationApi(catalog, create, cancel)` with `handle(method, path,
  body) -> tuple[int, dict | list | None]` for `GET /rooms` (200, list of `{"id", "name", "capacity",
  "open"}`), `POST /reservations` (201, `{"id", "roomId", "organizer", "start", "end", "attendees",
  "status"}`; body keys `roomId`, `organizer`, `start`, `end`, `attendees`) and `DELETE /reservations/{id}`
  (204, `None`); a `RoombookError` becomes `{"code", "message"}` with the status of an `ERROR_STATUS`
  constant mapping (404 `ROOM_NOT_FOUND` and `RESERVATION_NOT_FOUND`, 409 `CONFLICT` and `ALREADY_STARTED`,
  422 `CAPACITY_EXCEEDED` and `ROOM_CLOSED`); an invalid body gives 400 with code `BAD_REQUEST`; an unknown
  route gives 404 with code `NOT_FOUND`. `serve(api, host, port)` runs `http.server` and only translates
  HTTP to `handle` (JSON in, JSON out).

## TypeScript project `client/` (sources in `client/src/`, tests in `client/tests/`)

| Task | Source files | Test files |
|---|---|---|
| TASK-CLI-002 | `package.json`, `tsconfig.json`, `src/constants.ts`, `src/errors.ts`, `src/transport.ts` | `tests/transport.test.ts` |
| TASK-CLI-003 | `src/types.ts`, `src/client.ts` | `tests/client.test.ts` |
| TASK-CLI-004 | `src/cli.ts` | `tests/cli.test.ts` |

`package.json`: name `roombook-client`, version `0.1.0`, `"type": "module"`, scripts `test` =
`node --test "tests/*.test.ts"` and `build` = `tsc`, dev dependencies `typescript` `^5.8.0` and `@types/node`
`^22.0.0`. `tsconfig.json`: strict, `allowImportingTsExtensions`, `rewriteRelativeImportExtensions`,
`erasableSyntaxOnly`, `outDir` `dist`.

### Public API (exact names)
- `constants.ts` (DEC-CLI-002): contains **exactly this line** `export const REQUEST_TIMEOUT_MS = 5000;`,
  plus `DEFAULT_BASE_URL = "http://localhost:8080"` and the other named constants (routes, header names).
- `errors.ts`: `NetworkError extends Error`; `ServiceError extends Error` with readonly `code`, `message`
  and `status` fields.
- `transport.ts` (RQ-CLI-004): `HttpResponse { status: number; body: unknown }`, `Transport { send(method,
  path, body?): Promise<HttpResponse> }`, `FetchTransport(baseUrl, timeoutMs = REQUEST_TIMEOUT_MS,
  fetchImpl = fetch)` with a readonly `timeoutMs`; it aborts through `AbortController` after `timeoutMs`
  and throws `NetworkError` on abort or network failure. Tests pass a small `timeoutMs` and a fake
  `fetchImpl`.
- `types.ts`: `Room`, `ReservationRequest`, `Reservation` (JSON shapes of `api.py`).
- `client.ts` (RQ-CLI-001, RQ-CLI-002): `RoombookClient(transport)` with `listRooms()`,
  `createReservation(request)`, `cancelReservation(id)`; a status of 400 or more throws `ServiceError` built
  from the body `{code, message}` and the status.
- `cli.ts` (RQ-CLI-003): contains **exactly this line** `export const CLI_USAGE = "usage: roombook
  <rooms|book|cancel> [options]";`, and `run(argv, client, output): Promise<number>` returning the exit code
  (0 on success; non-zero on a `ServiceError`, a `NetworkError`, an unknown command or missing arguments,
  printing `CLI_USAGE` for the last two). Commands: `rooms`, `book <roomId> <organizer> <startIso> <endIso>
  <attendees>` (prints the new reservation id), `cancel <id>`. `output` has `log(text)` and `error(text)`.
  A `main()` at the bottom builds a `FetchTransport` from the `ROOMBOOK_URL` environment variable (default
  `DEFAULT_BASE_URL`) when the file is run directly.
