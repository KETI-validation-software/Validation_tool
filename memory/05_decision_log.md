# Decision Log

## Record format
| Date | Decision | Context | Options considered | Chosen option | Impact | Owner |
|---|---|---|---|---|---|---|

## Entries
| 2026-03-04 | Keep local memory notes in gitignored folder | Needed persistent local operation context without polluting repository history | Commit notes / local-only notes / external wiki | Local gitignored memory folder | Faster onboarding and troubleshooting continuity per developer machine | - |
| 2026-03-04 | Derive webhook port from test port in constants update flow | Static webhook port caused mismatch with runtime test port and callback failures | Keep static 8081 / manual edit / derive from selected test port | Derive WEBHOOK_PORT from test_port + 1 and persist | Reduced config mismatch and improved webhook setup reliability | - |
| 2026-03-04 | Persist realtime monitor per scenario | Switching scenarios removed prior monitoring context and reduced traceability | Global monitor only / file-based restore / per-scenario UI state restore | Save and restore monitor HTML by spec_id | Better operator continuity while switching between scenarios | - |
| 2026-03-10 | Fix page-1 header title to static asset | Header title changed unexpectedly by target branching logic | Keep branching / static title / runtime image map | Static title image for page 1 only | Stabilized page-1 visual identity while preserving page-2 branching behavior | - |
| 2026-03-11 | Standardize monitor log output readability | Duplicate lines and inconsistent formatting reduced usability | Keep legacy append paths / full rewrite / incremental cleanup | Incremental cleanup with dedup and formatting consistency | Clearer monitoring evidence and lower operator confusion | - |
| 2026-03-18 | Adopt structured project memory templates | Needed consistent local project management view (snapshot, status, design, backlog, decisions) | Free-form notes / single file / structured multi-file templates | Structured multi-file templates under memory/ | Improved planning cadence and easier handover/context recovery | - |\n| 2026-03-19 | Introduce Timer column and synchronize Webhook Badge UI | Needed consistent real-time status and interactive feedback across all validation pages | Results-only timer / static status icons / interactive WebhookBadgeLabel + Timer column | Interactive WebhookBadgeLabel + Timer column (Column 2) | Improved real-time observability and UI consistency across validation stages | - |

| 2026-03-27 | Limit Page-2 checkbox affordance to URL target rows only | Page-2 checkbox behavior became inconsistent across URL target selection and scenario rows | Keep checkbox everywhere / hide checkbox everywhere / scope by row purpose | Show left-aligned checkbox only for URL target selection and hide it for scenario rows | Clearer operator intent and lower UI confusion on test environment setup page | - |
| 2026-03-30 | Enforce encoding-safe edit path for Korean-heavy files | Repeated mojibake incidents were caused by shell-mediated non-ASCII string injection and broad rewrites | Keep current shell-based edits / force UTF-8 rewrites / minimum-scope patching with shell fallback guardrails | Default to `apply_patch`, forbid broad overwrite/replace, and when shell fallback is unavoidable use ASCII-only scripts with Unicode escapes plus immediate syntax/test verification | Reduced risk of recurring Korean string corruption and made recovery procedure explicit | - |
| 2026-04-06 | Consolidate overlapping memory notes into canonical docs plus archive | UI summary notes and todo interpretation notes had started to overlap and made current context harder to scan | Keep every dated note / delete older notes / consolidate active docs and archive superseded notes | Keep canonical files in `memory/`, move superseded notes to `memory/archive/`, and introduce unified UI/todo summaries | Lowered duplication and made the source of truth easier to find | - |

## Usage notes
- Log only meaningful architectural/process decisions.
- Keep each entry concise and evidence-based.
- Link related issue/task IDs where possible.
