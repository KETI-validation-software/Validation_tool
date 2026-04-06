# 2026-03-18 UI Alignment Summary

## Scope
- Focused on page 3 (test start page) Figma alignment.
- Main work areas: left navigation, split background, URL header row, API table clipping, monitor spacing, score-summary anchoring, and fullscreen resize behavior.

## Files touched
- ui/common_main_ui.py
- ui/ui_components.py
- ui/system_main_ui.py
- ui/platform_main_ui.py
- assets/image/test_config/btn_back.svg

## What changed
- Added and tuned the top-left previous-screen navigation on page 3.
- Replaced the old back-arrow asset with the Figma-exported SVG.
- Tuned navigation font weight, icon spacing, divider width, and left-panel placement.
- Replaced background-image-only behavior with a code-driven split background:
- left panel background
- center divider
- right content background
- Moved the test URL row into the same horizontal header line as the API title.
- Tuned the test URL label text, label width, input width, and fullscreen resize behavior.
- Fixed API table bottom clipping by aligning resize logic between common, platform, and system UI classes.
- Tuned spacing between:
- API table and monitor label
- monitor box and score-summary label
- label and box spacing inside monitor and score-summary sections
- Tuned the left scenario box height to match the lower right-side alignment target.

## Current layout baseline to preserve
- On page 3, the score-summary label and score-summary box are the current anchor position.
- Further tuning should avoid moving the score-summary region unless explicitly requested.
- If monitor spacing changes, prefer adjusting monitor height and surrounding spacings before moving score-summary.
- The divider under the previous-screen navigation should scale with the same effective width as the left-side selection boxes.
- The test URL input should expand on fullscreen together with the API header width.

## Current known-good intent
- Previous-screen navigation belongs to the left panel, not the right content area.
- The test URL row and the API title should stay on one horizontal line.
- API table, monitor section, and score-summary section should keep visually even vertical rhythm.
- Page 3 should remain the primary Figma-matching target before moving on to page 4.

## Remaining follow-up
- Continue page-3 polish only for new screenshot deltas.
- Start page-4 (test result page) alignment after page-3 anchor positions are considered stable.
- Keep watching for fullscreen-only regressions in divider width and URL-row expansion.

## Verification used today
- After Python edits, the main check was `python -m py_compile` against the edited UI files.
- Successful checks were repeatedly run for:
- ui/common_main_ui.py
- ui/ui_components.py
- ui/system_main_ui.py
- ui/platform_main_ui.py
