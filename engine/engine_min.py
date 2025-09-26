#!/usr/bin/env python3
"""
Tag/Trait CYOA Engine — Minimal
- Deterministic: choices are shown only if conditions pass (no greyed-out "teasers").
- Core systems: Tags, Traits, Items, Flags, Faction Reputation (−2..+2).
- No dice, no risk meter, no clocks.
- Save/Load included.
Usage: python3 engine_min.py [world.json]
"""

import json, os, sys

DEFAULT_WORLD_PATH = "world/world.json"
PROFILE_PATH = "profile.json"

TAG_ALIASES = {
    "Diplomat": "Emissary",
    "Emissary": "Emissary",
    "Judge": "Arbiter",
    "Arbiter": "Arbiter",
}


def canonical_tag(tag):
    return TAG_ALIASES.get(tag, tag)


def canonicalize_tag_list(tags):
    seen = []
    for tag in tags or []:
        ctag = canonical_tag(tag)
        if ctag not in seen:
            seen.append(ctag)
    return seen


def canonicalize_tag_value(value):
    if isinstance(value, list):
        return [canonical_tag(v) for v in value]
    if isinstance(value, str):
        return canonical_tag(value)
    return value


def default_profile():
    return {
        "unlocked_starts": [],
        "legacy_tags": [],
        "seen_endings": [],
    }


def load_profile(path=PROFILE_PATH):
    if not os.path.exists(path):
        profile = default_profile()
        save_profile(profile, path)
        return profile
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("unlocked_starts", [])
    data.setdefault("legacy_tags", [])
    data.setdefault("seen_endings", [])

    unlocked = []
    for sid in data["unlocked_starts"]:
        if isinstance(sid, str) and sid not in unlocked:
            unlocked.append(sid)
    data["unlocked_starts"] = unlocked

    data["legacy_tags"] = canonicalize_tag_list(data["legacy_tags"])

    seen = []
    for ending in data["seen_endings"]:
        if isinstance(ending, str) and ending not in seen:
            seen.append(ending)
    data["seen_endings"] = seen

    save_profile(data, path)
    return data


def merge_profile_starts(world, profile):
    starts = world.setdefault("starts", [])
    if not isinstance(starts, list):
        return

    unlocked_ids = set(profile.get("unlocked_starts", []))
    for entry in starts:
        if not isinstance(entry, dict):
            continue
        sid = entry.get("id") or entry.get("node")
        if sid in unlocked_ids:
            entry.pop("locked", None)


def record_seen_ending(state, ending_name):
    if not ending_name:
        return
    seen = state.profile.setdefault("seen_endings", [])
    if ending_name not in seen:
        seen.append(ending_name)
        save_profile(state.profile, state.profile_path)


def save_profile(profile, path=PROFILE_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
        f.write("\n")


class GameState:
    def __init__(self, world, profile, profile_path):
        self.world = world
        self.player = {
            "name": None,
            "hp": 10,
            "tags": [],           # e.g., ["Sneaky","Diplomat"]
            "traits": [],         # e.g., ["People-Reader"]
            "inventory": [],
            "flags": {},          # story state
            "rep": {},            # faction -> -2..+2
        }
        self.current_node = None
        self.history = []
        self.start_id = None
        self.profile = profile
        self.profile_path = profile_path

    def rep_str(self):
        if not self.player["rep"]:
            return "—"
        return ", ".join(f"{k}:{v}" for k,v in sorted(self.player["rep"].items()))

    def summary(self):
        inv = ", ".join(self.player["inventory"]) if self.player["inventory"] else "—"
        tags = ", ".join(self.player["tags"]) or "—"
        traits = ", ".join(self.player["traits"]) or "—"
        flags = ", ".join(f"{k}={v}" for k,v in sorted(self.player["flags"].items())) or "—"
        rep = self.rep_str()
        return (f"HP:{self.player['hp']} | TAGS:[{tags}] | TRAITS:[{traits}] | "
                f"REP: {rep} | INV: {inv} | FLAGS: {flags}")

def load_world(path):
    with open(path, "r", encoding="utf-8") as f:
        world = json.load(f)
    assert "title" in world and "nodes" in world and isinstance(world["nodes"], dict), "Invalid world.json"
    world.setdefault("starts", [])
    world.setdefault("endings", {})
    world.setdefault("factions", [])
    world.setdefault("advanced_tags", [])
    return world


def get_start_title(world, start_id):
    for start in world.get("starts", []):
        sid = start.get("id") or start.get("node")
        if sid == start_id:
            return start.get("title") or start_id
    return start_id

# ---------- Conditions (minimal set) ----------
def has_all(player_list, value):
    if isinstance(value, str):
        return value in player_list
    return all(v in player_list for v in value)

def meets_condition(cond, state):
    if not cond:
        return True
    if isinstance(cond, list):
        return all(meets_condition(c, state) for c in cond)
    t = cond.get("type")
    p = state.player

    if t == "has_item":
        return cond["value"] in p["inventory"]
    if t == "missing_item":
        return cond["value"] not in p["inventory"]
    if t == "flag_eq":
        return p["flags"].get(cond["flag"]) == cond.get("value")
    if t == "has_tag":
        required = canonicalize_tag_value(cond.get("value"))
        player_tags = set(canonicalize_tag_list(p["tags"]))
        if isinstance(required, list):
            return all(r in player_tags for r in required)
        return required in player_tags
    if t == "has_advanced_tag":
        world_adv = canonicalize_tag_list(state.world.get("advanced_tags", []))
        requested = cond.get("value")
        if requested is None:
            required = world_adv
        else:
            required = canonicalize_tag_list(requested if isinstance(requested, list) else [requested])
        if not required:
            return False
        player_tags = set(canonicalize_tag_list(p["tags"]))
        return any(r in player_tags for r in required)
    if t == "has_trait":
        return has_all(p["traits"], cond.get("value"))
    if t == "rep_at_least":
        return p["rep"].get(cond["faction"], 0) >= int(cond["value"])
    if t == "rep_at_least_count":
        value = int(cond.get("value", 0))
        count = int(cond.get("count", 1))
        factions = cond.get("factions")
        if isinstance(factions, str):
            factions = [factions]
        factions = factions or state.world.get("factions", [])
        met = sum(1 for fac in factions if p["rep"].get(fac, 0) >= value)
        return met >= count
    return False

# ---------- Effects (minimal set) ----------
def clamp(n, lo, hi): return lo if n<lo else hi if n>hi else n

def apply_effect(effect, state):
    if not effect: return
    t = effect.get("type")
    p = state.player

    if t == "add_item":
        it = effect["value"]
        if it not in p["inventory"]:
            p["inventory"].append(it); print(f"[+] You gain '{it}'.")
    elif t == "remove_item":
        it = effect["value"]
        if it in p["inventory"]:
            p["inventory"].remove(it); print(f"[-] '{it}' removed.")
    elif t == "set_flag":
        p["flags"][effect["flag"]] = effect.get("value", True)
        print(f"[*] Flag {effect['flag']} set to {p['flags'][effect['flag']]}")
    elif t == "add_tag":
        tg = canonical_tag(effect["value"])
        if tg not in p["tags"]:
            p["tags"].append(tg); print(f"[#] New Tag unlocked: {tg}")
        p["tags"] = canonicalize_tag_list(p["tags"])
    elif t == "add_trait":
        tr = effect["value"]
        if tr not in p["traits"]:
            p["traits"].append(tr); print(f"[✦] New Trait gained: {tr}")
    elif t == "rep_delta":
        fac = effect["faction"]; dv = int(effect.get("value",0))
        p["rep"][fac] = clamp(p["rep"].get(fac,0)+dv, -2, 2)
        print(f"[≈] Rep {fac} {'+' if dv>=0 else ''}{dv} -> {p['rep'][fac]}")
    elif t == "hp_delta":
        dv = int(effect.get("value",0))
        p["hp"] += dv; print(f"[♥] HP {'+' if dv>=0 else ''}{dv} -> {p['hp']}")
    elif t == "teleport":
        goto = effect["target"]; print(f"[~] You are moved to '{goto}'."); state.current_node = goto
    elif t == "end_game":
        p["flags"]["__ending__"] = effect.get("value", "Unnamed Ending")
        record_seen_ending(state, p["flags"]["__ending__"])
    elif t == "unlock_start":
        start_id = effect.get("value")
        if not start_id:
            return
        unlocked = state.profile.setdefault("unlocked_starts", [])
        if start_id not in unlocked:
            unlocked.append(start_id)
            save_profile(state.profile, state.profile_path)
            title = get_start_title(state.world, start_id)
            print(f"[#] Origin unlocked: {title}")
        merge_profile_starts(state.world, state.profile)
    elif t == "grant_legacy_tag":
        legacy = canonical_tag(effect.get("value"))
        if not legacy:
            return
        tags = state.profile.setdefault("legacy_tags", [])
        if legacy not in tags:
            tags.append(legacy)
            save_profile(state.profile, state.profile_path)
            print(f"[#] Legacy Tag granted: {legacy}")

def apply_effects(effects, state):
    for eff in effects or []:
        apply_effect(eff, state)

# ---------- Loop ----------
def list_choices(node, state):
    visible = []
    for ch in node.get("choices", []):
        if meets_condition(ch.get("condition"), state):
            visible.append(ch)
    return visible

def render_node(node, state):
    print("\n" + "="*80)
    print(node.get("title", state.world["title"]))
    print("-"*80)
    print(node.get("text",""))
    if node.get("image"):
        print(f"[Image: {node['image']}]")
    print("\n" + state.summary())
    print("-"*80)
    visible = list_choices(node, state)
    for idx, ch in enumerate(visible, start=1):
        print(f"  {idx}. {ch.get('text', f'Choice {idx}')}")
    if state.current_node not in state.world.get("endings", {}):
        print("  S. Save    L. Load    I. Inventory    T. Tags/Traits    Q. Quit")
    return visible

def pick_start(world, profile):
    starts = world.get("starts", [])
    unlocked_ids = set(profile.get("unlocked_starts", []))
    available = []
    for s in starts:
        start_id = s.get("id") or s.get("node")
        if s.get("locked") and start_id not in unlocked_ids:
            continue
        available.append((start_id, s))
    if not available:
        return "start", [], None
    print("Choose your origin:")
    for i, (sid, s) in enumerate(available, start=1):
        tags = canonicalize_tag_list(s.get("tags", []))
        print(f"  {i}. {s.get('title','Start')}  -> node '{s['node']}' | tags {tags}")
    while True:
        sel = input("> ").strip().lower()
        if sel.isdigit():
            i = int(sel)
            if 1 <= i <= len(available):
                sid, start = available[i-1]
                tags = canonicalize_tag_list(start.get("tags", []))
                return start["node"], tags, sid
        print("Pick a valid number.")

def save_game(state, path="savegame.json"):
    data = {
        "player": state.player,
        "current_node": state.current_node,
        "history": state.history,
        "start_id": state.start_id,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[Saved] {path}")

def load_game(state, path="savegame.json"):
    if not os.path.exists(path):
        print("[!] No save file found."); return False
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    state.player = data["player"]
    state.player.setdefault("tags", [])
    state.player["tags"] = canonicalize_tag_list(state.player["tags"])
    state.current_node = data["current_node"]
    state.history = data["history"]
    state.start_id = data.get("start_id")
    print(f"[Loaded] {path}"); return True

def main():
    world_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WORLD_PATH
    world = load_world(world_path)
    profile = load_profile(PROFILE_PATH)
    merge_profile_starts(world, profile)
    state = GameState(world, profile, PROFILE_PATH)

    print(f"=== {world['title']} ===")
    state.player["name"] = input("Name your character: ").strip() or "Traveler"

    # Initialize faction rep
    for fac in world.get("factions", []):
        state.player["rep"][fac] = 0

    # Pick a start and seed starting tags
    start_node, start_tags, start_id = pick_start(world, profile)
    state.current_node = start_node
    state.start_id = start_id or start_node
    for t in canonicalize_tag_list(start_tags):
        if t not in state.player["tags"]:
            state.player["tags"].append(t)
    state.player["tags"] = canonicalize_tag_list(state.player["tags"])

    legacy_tags = canonicalize_tag_list(profile.get("legacy_tags", []))
    newly_applied = []
    for t in legacy_tags:
        if t not in state.player["tags"]:
            state.player["tags"].append(t)
            newly_applied.append(t)
    state.player["tags"] = canonicalize_tag_list(state.player["tags"])
    if newly_applied:
        print(f"[#] Legacy Tags active this run: {', '.join(newly_applied)}")

    while True:
        node_id = state.current_node
        node = world["nodes"].get(node_id)
        if not node:
            print(f"[!] Missing node '{node_id}'. Exiting."); break

        apply_effects(node.get("on_enter"), state)
        if "__ending__" in state.player["flags"]:
            print(f"\n*** Ending reached: {state.player['flags']['__ending__']} ***"); break

        visible = render_node(node, state)

        if node_id in world.get("endings", {}):
            ending_name = world["endings"][node_id]
            record_seen_ending(state, ending_name)
            print(f"\n*** Ending reached: {ending_name} ***"); break

        choice = input("> ").strip().lower()
        if choice == "q":
            print("Goodbye!"); break
        if choice == "i":
            print("Inventory:", ", ".join(state.player["inventory"]) or "Empty"); continue
        if choice == "t":
            print("Tags:", ", ".join(state.player["tags"]) or "—")
            print("Traits:", ", ".join(state.player["traits"]) or "—"); continue
        if choice == "s":
            save_game(state); continue
        if choice == "l":
            if load_game(state): continue
            else: continue
        if not choice.isdigit():
            print("Enter a number or S/L/I/T/Q."); continue
        idx = int(choice)
        if not (1 <= idx <= len(visible)):
            print("Pick a valid choice number."); continue

        ch = visible[idx-1]
        apply_effects(ch.get("effects"), state)
        if "__ending__" in state.player["flags"]:
            print(f"\n*** Ending reached: {state.player['flags']['__ending__']} ***"); break

        target = ch.get("target")
        if not target:
            print("[!] Choice had no target; staying put."); continue

        state.history.append((node_id, target, ch.get("text","choice")))
        state.current_node = target

        if state.player["hp"] <= 0:
            demise = "A Short Tale"
            record_seen_ending(state, demise)
            print(f"\n*** You have perished. Ending: '{demise}' ***"); break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Interrupted] Bye.")
