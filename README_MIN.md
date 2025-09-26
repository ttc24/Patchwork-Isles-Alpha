# Tag/Trait CYOA — Minimal Engine

No dice. No risk meter. No clocks. No greyed-out “teasers.”
Only **Tags/Traits/Items/Flags/Rep** gating choices.

## Run
1) Python 3.8+
2) `python3 engine_min.py` (uses `world.json` by default)

## Authoring cheatsheet
- Gate a choice by Tag:
  ```json
  "condition": {"type": "has_tag", "value": "Sneaky"}
  ```
  Or require multiple Tags (ALL-of):
  ```json
  "condition": {"type": "has_tag", "value": ["Weaver","Diplomat"]}
  ```
- Reward a Tag or Trait:
  ```json
  {"type": "add_tag", "value": "Judge"}
  {"type": "add_trait", "value": "People-Reader"}
  ```
- Use Rep gates/rewards:
  ```json
  "condition": {"type": "rep_at_least", "faction":"Root Court", "value": 1}
  {"type": "rep_delta", "faction":"Wind Choirs", "value": 1}
  ```
- Endings:
  ```json
  {"type": "end_game", "value": "Hidden Docks Escape"}
  ```

**Tip:** Always include a Tagless route somewhere in the arc (e.g., pay an item, use a faction favor) so nothing hard-locks.

Happy building!

## How to add an unlockable start in 3 steps
1. **Author the start entry.** Add a new object to `world/world.json`'s `starts` list with `locked: true`, a `locked_title`, and the `node` that becomes the player's origin after they earn it. Keep tags consistent with the world bible and make sure the node exists.
2. **Deliver the unlock in-play.** Route the hub's capstone beat through a single reward node whose `on_enter` grants the start via `{ "type": "unlock_start", "value": "your_start_id" }` (and optional `{ "type": "grant_legacy_tag", ... }`). Avoid duplicating the effect across multiple branches—funnel completion choices through that node.
3. **QA the loop.** Playtest to confirm the start unlock triggers, run `python tools/validate.py`, and update any documentation or audit lists that track available origins.
