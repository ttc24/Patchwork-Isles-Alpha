# Actionable Issues

Use the entries below to seed GitHub issues for the v0.9 beta milestone. Each issue includes a
suggested title, scope summary, and concrete acceptance criteria.

## Narrative & Content

### 1) Tutorial micro-arc for new arrivals
**Scope**
- Create a self-contained onboarding flow that introduces core mechanics: tags, traits, inventory,
  faction reputation, and the history view.
- Ensure at least one tagless escape route to prevent hard locks for new players.
- Add playtest notes for the new onboarding beats.

**Acceptance Criteria**
- A new start or entry node routes into the tutorial arc.
- At least one branch is accessible without tags or reputation.
- Playtest transcript added in `playtests/` and validator passes.

### 2) Faction reputation clarity pass
**Scope**
- Audit all nodes that change or check faction reputation.
- Normalize language for reputation rewards/penalties and add reminder beats when rep changes.

**Acceptance Criteria**
- All reputation adjustments mention the affected faction in the same format.
- At least one reminder beat appears after a reputation delta.
- `tools/validate.py` passes with no new warnings.

### 3) Unlockable start audit
**Scope**
- Review `starts` entries for missing `locked_title` or missing unlock hooks.
- Document any starts that should remain locked and ensure unlock events exist.

**Acceptance Criteria**
- All locked starts include `locked_title`.
- Every locked start has at least one unlock reward path.
- A short audit summary is added to `docs/planning/`.

### 4) Legacy tag storytelling
**Scope**
- Prototype two arcs that check `legacy_tags` and react to returning players.

**Acceptance Criteria**
- Two new narrative branches conditionally trigger on `legacy_tags`.
- Branches include at least one reward or consequence tied to prior play.
- Validator passes for new content.

## Engine & Systems

### 5) Save-slot selector
**Scope**
- Add a profile selection step at boot with multiple save slots.
- Update save/load logic to target the selected slot.

**Acceptance Criteria**
- Player can choose an existing slot or create a new one.
- Saves persist to distinct profile files.
- README or docs updated with new workflow.

### 6) Session history UX polish
**Scope**
- Improve the `h` history readout with pagination and timestamps.
- Provide a clear way to exit history view.

**Acceptance Criteria**
- History view paginates and shows time or turn counters.
- Usability walkthrough added to playtest notes.

### 7) Accessibility options
**Scope**
- Add text speed, high-contrast mode, and font size toggles.
- Surface these options in the Options screen.

**Acceptance Criteria**
- Options persist in settings.
- Toggling options updates UI output.
- Docs updated with available accessibility settings.

## Tooling & QA

### 8) CI workflow for validators
**Scope**
- Ensure GitHub Actions runs validation, formatting, linting, and type checks on PRs.

**Acceptance Criteria**
- Workflow runs `tools/validate.py`, `ruff check`, `black --check`, and `mypy`.
- CI passes on a clean branch.

### 9) Content lint rules
**Scope**
- Extend `tools/validate.py` to flag missing `locked_title`, duplicate rewards, and unreachable nodes.

**Acceptance Criteria**
- New lint warnings for the three scenarios above.
- Docs updated with examples of the new lint messages.

### 10) Playtest feedback template
**Scope**
- Create a structured template for playtest feedback.

**Acceptance Criteria**
- New template added under `.github/ISSUE_TEMPLATE/` or docs.
- Template covers steps, expected/actual behavior, and narrative feedback.

## Community & Documentation

### 11) Lore bible refresh
**Scope**
- Update `docs/world_bible.md` with current faction politics, glossary, and art references.

**Acceptance Criteria**
- World bible sections updated and consistent with in-game naming.
- Any renamed factions or terms updated across related docs.

### 12) Player-facing landing page
**Scope**
- Draft marketing copy and add a hero image for the README.

**Acceptance Criteria**
- README features a new hero image with alt text.
- README copy updated for player onboarding.
