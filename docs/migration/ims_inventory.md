# IMS inventory migration map

This document captures an initial file-level migration inventory for the legacy IMS C codebase.
It is intentionally focused on structure only so the Python port can start with a shared vocabulary before any business logic is migrated.

## Scope

- Establish a first-pass mapping from likely central C modules into Python package areas.
- Keep the migration plan explicit about boundaries.
- Do not imply that functional parity exists yet.

## Proposed legacy-to-python mapping

| Legacy C file | Current role in legacy system | Planned Python target | Notes |
| --- | --- | --- | --- |
| `inventory_context.c` / `inventory_context.h` | Runtime context assembly and shared state bootstrap | `python_port/context/` | Start with dataclasses and typed containers only. |
| `inventory_entities.c` / `inventory_entities.h` | Core inventory entities and record definitions | `python_port/entities/` | Port shape and naming later; keep domain behavior out for now. |
| `inventory_scheduler.c` / `inventory_scheduler.h` | Scheduling, ordering, and orchestration entry points | `python_port/scheduler/` | Initial Python scaffold only models deterministic ordering. |
| `inventory_main.c` | CLI / process entry point | Future `python_port/__main__.py` or app runner | Not created in this PR. |
| `inventory_io.c` / `inventory_io.h` | File or stream I/O adapters | Future `python_port/io/` | Deferred until interfaces are clearer. |
| `inventory_rules.c` / `inventory_rules.h` | Business rules and validation logic | Future domain services package | Explicitly out of scope for this scaffold PR. |

## Migration sequencing

1. Create package skeletons for context, entities, and scheduler.
2. Add tests that lock in structural expectations such as scheduler ordering.
3. Introduce interfaces and typed models before moving business rules.
4. Port domain logic incrementally with characterization tests from the legacy implementation.

## Out of scope in this PR

- Porting any business logic from C to Python.
- Reproducing legacy I/O behavior.
- Establishing final package boundaries for every module.
