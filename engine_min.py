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

DEFAULT_WORLD_PATH = "world.json"

class GameState:
    def __init__(self, world):
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
    return world

# ---------- Conditions (minimal set) ----------
def has_all(player_list, value):
    if isinstance(value, str):
        return value in player_list
    return all(v in player_list for v in value)

def meets_condition(cond, state):
    if not cond:
        return True
    t = cond.get("type")
    p = state.player

    if t == "has_item":
        return cond["value"] in p["inventory"]
    if t == "missing_item":
        return cond["value"] not in p["inventory"]
    if t == "flag_eq":
        return p["flags"].get(cond["flag"]) == cond.get("value")
    if t == "has_tag":
        return has_all(p["tags"], cond.get("value"))
    if t == "has_trait":
        return has_all(p["traits"], cond.get("value"))
    if t == "rep_at_least":
        return p["rep"].get(cond["faction"], 0) >= int(cond["value"])
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
        tg = effect["value"]
        if tg not in p["tags"]:
            p["tags"].append(tg); print(f"[#] New Tag unlocked: {tg}")
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
        p["flags"]["__ending__"] = effect.get("value","Unnamed Ending")

def apply_effects(effects, state):
    for eff in effects or []:
        apply_effect(eff, state)

# ---------- Loop ----------
def list_choices(node, state):
    visible = []
    for idx, ch in enumerate(node.get("choices", []), start=1):
        if meets_condition(ch.get("condition"), state):
            visible.append((idx, ch))
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
    for idx, ch in visible:
        print(f"  {idx}. {ch.get('text', f'Choice {idx}')}")
    if state.current_node not in state.world.get("endings", {}):
        print("  S. Save    L. Load    I. Inventory    T. Tags/Traits    Q. Quit")
    return visible

def pick_start(world):
    starts = world.get("starts", [])
    if not starts:
        return "start", []
    print("Choose your origin:")
    for i, s in enumerate(starts, start=1):
        print(f"  {i}. {s.get('title','Start')}  -> node '{s['node']}' | tags {s.get('tags',[])}")
    while True:
        sel = input("> ").strip().lower()
        if sel.isdigit():
            i = int(sel)
            if 1 <= i <= len(starts):
                return starts[i-1]["node"], starts[i-1].get("tags", [])
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
    state.current_node = data["current_node"]
    state.history = data["history"]
    state.start_id = data.get("start_id")
    print(f"[Loaded] {path}"); return True

def main():
    world_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WORLD_PATH
    world = load_world(world_path)
    state = GameState(world)

    print(f"=== {world['title']} ===")
    state.player["name"] = input("Name your character: ").strip() or "Traveler"

    # Initialize faction rep
    for fac in world.get("factions", []):
        state.player["rep"][fac] = 0

    # Pick a start and seed starting tags
    start, start_tags = pick_start(world)
    state.current_node = start
    state.start_id = start
    for t in start_tags:
        if t not in state.player["tags"]:
            state.player["tags"].append(t)

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
            print(f"\n*** Ending reached: {world['endings'][node_id]} ***"); break

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

        _, ch = visible[idx-1]
        apply_effects(ch.get("effects"), state)
        if "__ending__" in state.player["flags"]:
            print(f"\n*** Ending reached: {state.player['flags']['__ending__']} ***"); break

        target = ch.get("target")
        if not target:
            print("[!] Choice had no target; staying put."); continue

        state.history.append((node_id, target, ch.get("text","choice")))
        state.current_node = target

        if state.player["hp"] <= 0:
            print("\n*** You have perished. Ending: 'A Short Tale' ***"); break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Interrupted] Bye.")
