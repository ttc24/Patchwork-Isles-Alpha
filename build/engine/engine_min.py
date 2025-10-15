#!/usr/bin/env python3
"""
Tag/Trait CYOA Engine — Minimal
- Deterministic: choices are shown only if conditions pass (no greyed-out "teasers").
- Core systems: Tags, Traits, Items, Flags, Faction Reputation (−2..+2).
- No dice, no risk meter, no clocks.
- Save/Load included.
Usage: python3 engine_min.py [world.json]
"""

import hashlib
import json
import os
import sys
import textwrap
from pathlib import Path

# Import new state management system
try:
    from .state_manager import StateManager, create_default_state_manager
    STATE_MANAGEMENT_AVAILABLE = True
except ImportError:
    STATE_MANAGEMENT_AVAILABLE = False

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from engine.options_menu import options_menu
    from engine.save_manager import SaveError, SaveManager
    from engine.settings import Settings, load_settings
    from engine.profile_manager import ProfileManager, select_profile
else:
    from .options_menu import options_menu
    from .save_manager import SaveError, SaveManager
    from .settings import Settings, load_settings
    from .profile_manager import ProfileManager, select_profile

DEFAULT_WORLD_PATH = "world/world.json"
PROFILE_PATH = "profile.json"
BASE_LINE_WIDTH = 80
MIN_LINE_WIDTH = 50
MAX_LINE_WIDTH = 120

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


def compute_line_width(settings: Settings) -> int:
    try:
        scale = float(getattr(settings, "ui_scale", 1.0))
    except (TypeError, ValueError):
        scale = 1.0
    width = int(round(BASE_LINE_WIDTH * scale))
    return max(MIN_LINE_WIDTH, min(MAX_LINE_WIDTH, width))


def default_profile():
    return {
        "unlocked_starts": [],
        "legacy_tags": [],
        "seen_endings": [],
        "flags": {},
    }


def load_profile(path=PROFILE_PATH):
    if not os.path.exists(path):
        profile = default_profile()
        save_profile(profile, path)
        return profile
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("unlocked_starts", [])
    data.setdefault("legacy_tags", [])
    data.setdefault("seen_endings", [])
    data.setdefault("flags", {})

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
    def __init__(
        self,
        world,
        profile,
        profile_path,
        settings=None,
        *,
        world_seed=None,
        active_area=None,
    ):
        self.world = world
        self.player = {
            "name": None,
            "hp": 10,
            "tags": [],           # e.g., ["Sneaky","Diplomat"]
            "traits": [],         # e.g., ["People-Reader"]
            "inventory": [],
            "resources": {},      # e.g., {"gold": 5}
            "flags": {},          # story state
            "rep": {},            # faction -> -2..+2
        }
        self.current_node = None
        self.history = []
        self.choices_made = {}  # Track choices made this run: {node_id: [choice_texts]}
        self.start_id = None
        self.profile = profile
        self.profile_path = profile_path
        self.settings = Settings()
        self.line_width = BASE_LINE_WIDTH
        self.window_mode = "windowed"
        self.vsync_enabled = True
        self.audio_levels = {"master": 1.0, "music": 1.0, "sfx": 1.0}
        self.world_seed = world_seed if world_seed is not None else 0
        self.active_area = active_area or world.get("title") or "Unknown"
        
        # Initialize state manager if available
        if STATE_MANAGEMENT_AVAILABLE:
            self.state_manager = create_default_state_manager()
            # Sync existing player data with state manager
            self.state_manager.player_state = self.state_manager.player_state.__class__.from_dict(self.player)
            self.state_manager.session_state.current_node = self.current_node
            self.state_manager.session_state.start_id = self.start_id
            self.state_manager.session_state.world_seed = self.world_seed
            self.state_manager.session_state.active_area = self.active_area
        else:
            self.state_manager = None

        if settings is None:
            settings = Settings()
        self.apply_settings(settings)
        self.ensure_consistency()

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
        resources = self.player.get("resources", {})
        if isinstance(resources, dict) and resources:
            res = ", ".join(f"{k}:{v}" for k, v in sorted(resources.items()))
        else:
            res = "—"
        return (
            f"HP:{self.player['hp']} | TAGS:[{tags}] | TRAITS:[{traits}] | REP: {rep} | "
            f"INV: {inv} | RES: {res} | FLAGS: {flags}"
        )

    def apply_settings(self, settings):
        if isinstance(settings, Settings):
            sanitized = settings.copy()
        else:
            sanitized = Settings()
        sanitized.clamp()
        self.settings = sanitized
        self.line_width = compute_line_width(sanitized)
        self.window_mode = sanitized.window_mode
        self.vsync_enabled = sanitized.vsync
        self.audio_levels = {
            "master": sanitized.audio_master,
            "music": sanitized.audio_music,
            "sfx": sanitized.audio_sfx,
        }

    def ensure_consistency(self):
        player = self.player or {}
        if not isinstance(player, dict):
            player = {}
        player.setdefault("name", None)
        player.setdefault("hp", 10)
        player.setdefault("tags", [])
        player.setdefault("traits", [])
        player.setdefault("inventory", [])
        player.setdefault("resources", {})
        player.setdefault("flags", {})
        player.setdefault("rep", {})
        if not isinstance(player["inventory"], list):
            player["inventory"] = list(player["inventory"])
        if not isinstance(player["tags"], list):
            player["tags"] = list(player["tags"])
        if not isinstance(player["traits"], list):
            player["traits"] = list(player["traits"])
        if not isinstance(player["flags"], dict):
            player["flags"] = {}
        if not isinstance(player["rep"], dict):
            player["rep"] = {}
        if not isinstance(player["resources"], dict):
            player["resources"] = {}
        player["tags"] = canonicalize_tag_list(player.get("tags", []))
        self.player = player

        normalized_history = []
        if isinstance(self.history, list):
            for entry in self.history:
                if isinstance(entry, dict):
                    origin = entry.get("from")
                    target = entry.get("to")
                    choice = entry.get("choice")
                elif isinstance(entry, (list, tuple)) and len(entry) >= 3:
                    origin, target, choice = entry[:3]
                else:
                    continue
                normalized_history.append(
                    {
                        "from": origin,
                        "to": target,
                        "choice": choice,
                    }
                )
        self.history = normalized_history
        if not isinstance(self.start_id, str):
            self.start_id = self.start_id or None
        if not isinstance(self.active_area, str) or not self.active_area:
            self.active_area = self.world.get("title") or "Unknown"
        if not isinstance(self.world_seed, int):
            try:
                self.world_seed = int(self.world_seed)
            except (TypeError, ValueError):
                self.world_seed = 0

    def record_transition(self, origin, target, choice_text):
        entry = {
            "from": origin,
            "to": target,
            "choice": choice_text,
        }
        self.history.append(entry)
        
        # Track choices made this run for display purposes
        if origin not in self.choices_made:
            self.choices_made[origin] = []
        if choice_text not in self.choices_made[origin]:
            self.choices_made[origin].append(choice_text)


def apply_runtime_settings(
    state: GameState, new_settings: Settings, *, announce: bool = True
) -> Settings:
    if isinstance(new_settings, Settings):
        target = new_settings.copy()
    else:
        target = Settings()
    target.clamp()

    previous = state.settings.copy()
    state.apply_settings(target)

    if not announce:
        return state.settings

    updates = []
    if (
        previous.audio_master != state.settings.audio_master
        or previous.audio_music != state.settings.audio_music
        or previous.audio_sfx != state.settings.audio_sfx
    ):
        updates.append(
            f"[Audio] Master {state.settings.audio_master * 100:.0f}% | "
            f"Music {state.settings.audio_music * 100:.0f}% | "
            f"SFX {state.settings.audio_sfx * 100:.0f}%"
        )
    if previous.window_mode != state.settings.window_mode:
        updates.append(f"[Display] Window mode set to {state.settings.window_mode.title()}.")
    if previous.vsync != state.settings.vsync:
        updates.append(
            f"[Display] VSync {'enabled' if state.settings.vsync else 'disabled'}."
        )
    if previous.ui_scale != state.settings.ui_scale:
        updates.append(
            f"[UI] Scale adjusted to {state.settings.ui_scale:.2f}x "
            f"(line width {state.line_width})."
        )

    for message in updates:
        print(message)

    return state.settings

def load_world(path):
    with open(path, encoding="utf-8") as f:
        world = json.load(f)
    assert (
        "title" in world and "nodes" in world and isinstance(world["nodes"], dict)
    ), "Invalid world.json"
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

def format_condition_requirement(cond, state):
    """Format a condition into human-readable requirement text."""
    if not cond:
        return None
        
    if isinstance(cond, list):
        requirements = []
        for c in cond:
            req = format_condition_requirement(c, state)
            if req:
                requirements.append(req)
        if not requirements:
            return None
        return " and ".join(requirements)
    
    t = cond.get("type")
    
    if t == "has_item":
        return f"Need: {cond['value']}"
    if t == "missing_item":
        return f"Must not have: {cond['value']}"
    if t == "flag_eq":
        return f"Flag {cond['flag']} must be {cond.get('value')}"
    if t == "has_tag":
        required = canonicalize_tag_value(cond.get("value"))
        if isinstance(required, list):
            return f"Tags needed: {', '.join(required)}"
        return f"Tag needed: {required}"
    if t == "has_advanced_tag":
        world_adv = canonicalize_tag_list(state.world.get("advanced_tags", []))
        requested = cond.get("value")
        if requested is None:
            required = world_adv
        else:
            requested_list = requested if isinstance(requested, list) else [requested]
            required = canonicalize_tag_list(requested_list)
        if not required:
            return "Advanced tag needed"
        return f"Advanced tag needed: one of {', '.join(required)}"
    if t == "has_trait":
        value = cond.get("value")
        if isinstance(value, list):
            return f"Traits needed: {', '.join(value)}"
        return f"Trait needed: {value}"
    if t == "rep_at_least":
        return f"Need {cond['faction']} reputation ≥{cond['value']}"
    if t == "rep_at_least_count":
        value = int(cond.get("value", 0))
        count = int(cond.get("count", 1))
        factions = cond.get("factions")
        if isinstance(factions, str):
            factions = [factions]
        factions = factions or state.world.get("factions", [])
        return f"Need reputation ≥{value} with {count} of: {', '.join(factions)}"
    if t == "profile_flag_eq":
        return f"Profile flag {cond.get('flag')} must be {cond.get('value')}"
    if t == "profile_flag_is_true":
        return f"Profile flag {cond.get('flag')} must be true"
    if t == "profile_flag_is_false":
        return f"Profile flag {cond.get('flag')} must be false"
    
    return "Unknown requirement"

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
            requested_list = requested if isinstance(requested, list) else [requested]
            required = canonicalize_tag_list(requested_list)
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
    if t == "profile_flag_eq":
        flags = state.profile.get("flags", {})
        return flags.get(cond.get("flag")) == cond.get("value")
    if t == "profile_flag_is_true":
        flags = state.profile.get("flags", {})
        return bool(flags.get(cond.get("flag")))
    if t == "profile_flag_is_false":
        flags = state.profile.get("flags", {})
        return not bool(flags.get(cond.get("flag")))
    return False

# ---------- Effects (minimal set) ----------
def clamp(n, lo, hi): return lo if n<lo else hi if n>hi else n

def apply_effect(effect, state):
    if not effect:
        return
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
    elif t == "set_profile_flag":
        flag = effect.get("flag")
        if not flag:
            return
        flags = state.profile.setdefault("flags", {})
        value = effect.get("value", True)
        previous = flags.get(flag)
        if previous != value:
            flags[flag] = value
            save_profile(state.profile, state.profile_path)
            print(f"[Profile] {flag} set to {value}.")
        else:
            flags[flag] = value
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
    """Return tuple of (available_choices, locked_choices_with_requirements)"""
    available = []
    locked = []
    
    for ch in node.get("choices", []):
        condition = ch.get("condition")
        if meets_condition(condition, state):
            available.append(ch)
        else:
            # Add the choice with its requirement for display
            requirement = format_condition_requirement(condition, state)
            locked.append((ch, requirement))
    
    return available, locked

def render_node(node, state):
    import time
    
    settings = getattr(state, "settings", None)
    width = getattr(state, "line_width", BASE_LINE_WIDTH)
    
    # Apply accessibility settings
    if settings and settings.large_text:
        width = min(width, 60)
    
    # Clear and elegant header
    print("\n")
    title = node.get("title", state.world["title"])
    
    if settings and settings.high_contrast:
        print("■" * len(title))
        print(title)
        print("■" * len(title))
    else:
        print(f"═══ {title} ═══")
    
    print()

    # Main story text - clean and readable
    body = node.get("text", "")
    if body:
        paragraphs = body.split("\n")
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                wrapped = textwrap.fill(paragraph, width=width)
                print(wrapped)
                
                # Text speed simulation and pause after text
                if settings:
                    if settings.text_speed < 1.0:
                        time.sleep(0.5 * (1.0 - settings.text_speed))
                    
                    if settings.pause_after_text and i < len(paragraphs) - 1:
                        input("\n  [Press Enter to continue...]")
                        print()
            else:
                print()
    
    # Image placeholder (if any)
    if node.get("image"):
        print(f"  🖼️  {node['image']}")
        print()
    
    # Character status - simplified and clean
    print("━" * min(width, 50))
    
    # Essential info only, beautifully formatted
    player = state.player
    
    # Tags (only show if player has any)
    if player.get("tags"):
        tags_str = " • ".join(player["tags"])
        print(f"🏷️  {tags_str}")
    
    # Traits (only show if player has any) 
    if player.get("traits"):
        traits_str = " • ".join(player["traits"])
        print(f"✨ {traits_str}")
    
    # Inventory (only show if not empty)
    if player.get("inventory"):
        inv_str = " • ".join(player["inventory"])
        print(f"🎒 {inv_str}")
    
    # Show reputation only if player has meaningful relationships
    rep_items = [(f, r) for f, r in player.get("rep", {}).items() if r != 0]
    if rep_items:
        rep_strs = []
        for faction, rep in rep_items:
            if rep > 0:
                rep_strs.append(f"{faction} +{rep}")
            else:
                rep_strs.append(f"{faction} {rep}")
        print(f"🤝 {' • '.join(rep_strs)}")
    
    print("━" * min(width, 50))
    print()
    
    # Choices - clean numbering with locked choice display
    available, locked = list_choices(node, state)
    
    # Get previously made choices for this node
    visited_choices = state.choices_made.get(state.current_node, []) if hasattr(state, 'choices_made') else []
    
    # Show available choices
    for idx, ch in enumerate(available, start=1):
        choice_text = ch.get('text', f'Choice {idx}')
        
        # Check if this choice was previously made
        is_visited = state.settings.show_visited_choices and choice_text in visited_choices
        
        if is_visited:
            print(f"  {idx}. {choice_text} [VISITED]")
        else:
            print(f"  {idx}. {choice_text}")
    
    # Show locked choices with requirements (if any and setting enabled)
    if locked and state.settings.show_locked_choices:
        print()
        print("  🔒 Locked Choices:")
        for ch, requirement in locked:
            choice_text = ch.get('text', 'Locked choice')
            if requirement:
                print(f"     • {choice_text} ({requirement})")
            else:
                print(f"     • {choice_text} (Requirements not met)")
    
    # Commands - simplified and elegant
    if state.current_node not in state.world.get("endings", {}):
        print()
        print("  ⌨️  [I]nfo • [H]istory • [P]ause • [O]ptions • [Q]uit")
    
    print()
    return available

def pick_start(world, profile, open_options=None):
    starts = world.get("starts", [])
    unlocked_ids = set(profile.get("unlocked_starts", []))
    core = []
    unlocked = []
    for s in starts:
        start_id = s.get("id") or s.get("node")
        if s.get("locked") and start_id not in unlocked_ids:
            continue
        entry = (start_id, s)
        if s.get("locked"):
            unlocked.append(entry)
        else:
            core.append(entry)
    if not (core or unlocked):
        return "start", [], None

    while True:
        print("Choose your origin:")
        display = []
        index = 0

        def show_group(title, entries):
            nonlocal index
            if not entries:
                return
            print(title)
            for sid, start in entries:
                index += 1
                display.append((sid, start))
                tags = canonicalize_tag_list(start.get("tags", []))
                tag_str = ", ".join(tags) if tags else "—"
                node = start.get("node", "?")
                print(
                    f"  {index}. {start.get('title','Start')} (Node: {node} | Tags: {tag_str})"
                )
                blurb = start.get("blurb")
                if blurb:
                    for line in blurb.splitlines():
                        print(f"     {line}")
                else:
                    print("     —")
            print("")

        show_group("Core Starts (always available):", core)
        show_group("Unlocked Starts (profile):", unlocked)

        if not display:
            return "start", [], None

        if open_options is not None:
            print("  O. Options")

        selection = input("> ").strip().lower()
        if selection in {"o", "options"} and open_options is not None:
            open_options()
            print("")
            continue
        if selection.isdigit():
            i = int(selection)
            if 1 <= i <= len(display):
                sid, start = display[i - 1]
                tags = canonicalize_tag_list(start.get("tags", []))
                return start["node"], tags, sid
        if open_options is not None:
            print("Pick a valid number or press O for options.")
        else:
            print("Pick a valid number.")

def show_slot_overview(save_manager):
    slots = save_manager.list_slots()
    if not slots:
        print("📋 No saves found yet.")
        return
        
    print("💾 Available saves:")
    print()
    for meta in slots:
        print(f"  • {meta.slot}")
        if meta.player_name:
            print(f"    📑 Character: {meta.player_name}")
        if meta.active_area:
            print(f"    🗺 Location: {meta.active_area}")
        if meta.saved_at:
            # Format timestamp nicely
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(meta.saved_at.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d at %H:%M')
                print(f"    📅 Saved: {formatted_time}")
            except:
                print(f"    📅 Saved: {meta.saved_at[:16]}")
        print()


def prompt_slot_name(action, save_manager):
    show_slot_overview(save_manager)
    raw = input(f"Enter slot name to {action} (blank to cancel): ").strip()
    if not raw:
        print(f"{action.title()} cancelled.")
        return None
    return raw


def show_character_info(state):
    """Display detailed character information in a clean format."""
    player = state.player
    
    print("\n═══ CHARACTER INFO ═══")
    print(f"Name: {player.get('name', 'Unknown')}")
    print(f"Health: {player.get('hp', 10)} HP")
    print()
    
    # Tags
    if player.get("tags"):
        print("🏷️  SKILLS & ROLES:")
        for tag in player["tags"]:
            print(f"   • {tag}")
        print()
    
    # Traits
    if player.get("traits"):
        print("✨ SPECIAL ABILITIES:")
        for trait in player["traits"]:
            print(f"   • {trait}")
        print()
    
    # Inventory
    if player.get("inventory"):
        print("🎒 INVENTORY:")
        for item in player["inventory"]:
            print(f"   • {item}")
        print()
    
    # Resources
    resources = player.get("resources", {})
    if resources:
        print("💰 RESOURCES:")
        for resource, amount in resources.items():
            print(f"   • {resource}: {amount}")
        print()
    
    # Faction reputation
    rep = player.get("rep", {})
    meaningful_rep = {f: r for f, r in rep.items() if r != 0}
    if meaningful_rep:
        print("🤝 FACTION STANDING:")
        for faction, reputation in meaningful_rep.items():
            if reputation > 0:
                status = "😊 Friendly" if reputation == 1 else "😄 Allied" if reputation == 2 else "Positive"
                print(f"   • {faction}: {status} (+{reputation})")
            else:
                status = "😐 Wary" if reputation == -1 else "😡 Hostile" if reputation == -2 else "Negative"
                print(f"   • {faction}: {status} ({reputation})")
        print()
    
    # Story flags (only interesting ones)
    flags = player.get("flags", {})
    story_flags = {k: v for k, v in flags.items() if not k.startswith("__") and not k.startswith("tutorial")}
    if story_flags:
        print("📋 STORY PROGRESS:")
        for flag, value in story_flags.items():
            print(f"   • {flag}: {value}")
        print()
    
    input("Press Enter to continue...")


def show_history(state, page_size=5):
    """Display paginated session history."""
    history = state.history
    if not history:
        print("No history recorded yet.")
        return
    
    total_entries = len(history)
    total_pages = (total_entries + page_size - 1) // page_size
    current_page = 0
    
    while True:
        print("\n" + "=" * 60)
        print(f"SESSION HISTORY - Page {current_page + 1} of {total_pages}")
        print("=" * 60)
        
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total_entries)
        
        for i in range(start_idx, end_idx):
            entry = history[i]
            from_node = entry.get("from", "Unknown")
            to_node = entry.get("to", "Unknown")
            choice = entry.get("choice", "Unknown choice")
            
            print(f"{i + 1:3d}. {from_node} → {to_node}")
            print(f"     Choice: {choice}")
            if i < end_idx - 1:  # Don't add blank line after last entry
                print()
        
        print("\n" + "-" * 60)
        
        # Navigation options
        options = []
        if current_page > 0:
            options.append("P: Previous page")
        if current_page < total_pages - 1:
            options.append("N: Next page")
        options.extend(["F: First page", "L: Last page", "Q: Back to game"])
        
        print("Navigation: " + "  ".join(options))
        
        choice = input("> ").strip().lower()
        
        if choice == "q":
            break
        elif choice == "p" and current_page > 0:
            current_page -= 1
        elif choice == "n" and current_page < total_pages - 1:
            current_page += 1
        elif choice == "f":
            current_page = 0
        elif choice == "l":
            current_page = total_pages - 1
        elif choice.isdigit():
            # Jump to specific entry
            entry_num = int(choice) - 1
            if 0 <= entry_num < total_entries:
                target_page = entry_num // page_size
                current_page = target_page
            else:
                print(f"Entry {choice} not found. Valid range: 1-{total_entries}")
                input("Press Enter to continue...")
        else:
            print("Invalid option.")
            input("Press Enter to continue...")


def pause_menu(state, save_manager, open_options=None):
    while True:
        print("\n═══ GAME PAUSED ═══")
        print()
        print("💾 Save & Load:")
        print("  1. Save Game")
        print("  2. Load Game") 
        print("  3. Quick Save")
        print("  4. Quick Load")
        print()
        if open_options is not None:
            print("⚙️  5. Options")
            print()
        print("▶️  [R]esume Game")
        print("🚪 [Q]uit to Desktop")
        print()
        choice = input("📋 Choice: ").strip().lower()

        if choice in {"r", "resume"}:
            return "resume"
        if choice in {"q", "quit"}:
            return "quit"
        if choice == "1":
            slot = prompt_slot_name("save", save_manager)
            if not slot:
                continue
            try:
                save_manager.save(slot)
            except SaveError as exc:
                print(f"[!] {exc}")
            continue
        if choice == "2":
            slot = prompt_slot_name("load", save_manager)
            if not slot:
                continue
            try:
                if save_manager.load(slot):
                    return "loaded"
            except SaveError as exc:
                print(f"[!] {exc}")
            continue
        if choice == "3":
            save_manager.save(save_manager.QUICK_SLOT, label="Quick Save")
            continue
        if choice == "4":
            if save_manager.load(save_manager.QUICK_SLOT):
                return "loaded"
            continue
        if choice == "5" and open_options is not None:
            open_options()
            continue
        print("Pick a valid pause option.")

def main():
    try:
        world_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WORLD_PATH
        if not Path(world_path).exists():
            print(f"Error: World file not found: {world_path}")
            print(f"Please check the path or run from the repository root.")
            return False
        
        world = load_world(world_path)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in world file: {e}")
        print(f"Please run 'python tools/validate.py {world_path}' to check for issues.")
        return False
    except FileNotFoundError:
        print(f"Error: World file not found: {world_path}")
        print(f"Make sure you're running from the correct directory.")
        return False
    except Exception as e:
        print(f"Unexpected error loading world: {e}")
        return False
    try:
        settings = load_settings()
    except Exception as e:
        print(f"Warning: Could not load settings, using defaults: {e}")
        settings = Settings()
    
    # Set up profile manager and let user select profile
    try:
        profile_manager = ProfileManager()
    except Exception as e:
        print(f"Error: Could not initialize profile manager: {e}")
        print("This may be a permissions issue with the profiles directory.")
        return False
    
    def open_options_menu():
        nonlocal settings
        updated, changed = options_menu(
            settings,
            apply_callback=lambda new_settings: settings.__dict__.update(new_settings.__dict__),
        )
        if changed:
            settings = updated
        return changed
    
    try:
        profile_name, profile_path = select_profile(profile_manager, open_options_menu)
        profile = profile_manager.load_profile_data(profile_name)
        merge_profile_starts(world, profile)
    except KeyboardInterrupt:
        print("\n[Interrupted] Goodbye!")
        return False
    except Exception as e:
        print(f"Error during profile selection: {e}")
        return False
    world_seed = world.get("seed") if isinstance(world, dict) else None
    if isinstance(world_seed, str):
        try:
            world_seed = int(world_seed, 0)
        except ValueError:
            world_seed = None
    if not isinstance(world_seed, int):
        digest = hashlib.sha1(world_path.encode("utf-8")).hexdigest()
        world_seed = int(digest[:8], 16)
    active_area = world.get("title") if isinstance(world, dict) else "Unknown"
    state = GameState(
        world,
        profile,
        str(profile_path),
        settings,
        world_seed=world_seed,
        active_area=active_area,
    )
    save_manager = SaveManager(state)

    def open_options_game_menu():
        updated, changed = options_menu(
            state.settings,
            apply_callback=lambda new_settings: apply_runtime_settings(state, new_settings),
        )
        if changed:
            apply_runtime_settings(state, updated, announce=False)
        return changed

    print(f"\n═══ {world['title']} ═══")
    print("Welcome to the archipelago of political intrigue!")
    print()
    
    name = input("📑 Character name: ").strip()
    state.player["name"] = name or "Traveler"
    
    if not name:
        print(f"✨ Welcome, {state.player['name']}!")
    else:
        print(f"✨ Welcome, {name}!")
    print()

    # Initialize faction rep
    for fac in world.get("factions", []):
        state.player["rep"][fac] = 0

    # Pick a start and seed starting tags
    start_node, start_tags, start_id = pick_start(world, profile, open_options_game_menu)
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

    save_manager.autosave()
    
    # Performance tracking
    node_visit_count = 0
    max_history_size = 1000  # Limit history to prevent memory bloat

    while True:
        node_id = state.current_node
        node_visit_count += 1
        
        # Manage memory by trimming history if it gets too long
        if len(state.history) > max_history_size:
            state.history = state.history[-max_history_size//2:]  # Keep most recent half
            print("[System] Trimmed old history to save memory.")
        
        node = world["nodes"].get(node_id)
        if not node:
            print(f"[!] Missing node '{node_id}'. This suggests content corruption.")
            print(f"Try running 'python tools/validate.py {world_path}' to check for issues.")
            break
        apply_effects(node.get("on_enter"), state)
        if "__ending__" in state.player["flags"]:
            print(f"\n*** Ending reached: {state.player['flags']['__ending__']} ***"); break

        visible = render_node(node, state)

        try:
            save_manager.autosave()
        except SaveError as e:
            print(f"[Warning] Autosave failed: {e}")
            print("Your progress may not be saved automatically.")

        if node_id in world.get("endings", {}):
            ending_name = world["endings"][node_id]
            record_seen_ending(state, ending_name)
            print(f"\n*** Ending reached: {ending_name} ***"); break

        choice = input("> ").strip().lower()
        if choice == "q":
            print("Goodbye!"); break
        if choice == "p":
            action = pause_menu(state, save_manager, open_options_game_menu)
            if action == "quit":
                print("Goodbye!"); break
            if action == "loaded":
                save_manager.autosave()
            continue
        if choice in ("i", "info"):
            show_character_info(state)
            continue
        if choice == "t":
            print("Tags:", ", ".join(state.player["tags"]) or "—")
            print("Traits:", ", ".join(state.player["traits"]) or "—")
            continue
        if choice == "h":
            show_history(state)
            continue
            try:
                save_manager.save(save_manager.QUICK_SLOT, label="Quick Save")
            except SaveError as exc:
                print(f"[!] {exc}")
            continue
        if choice == "l":
            if save_manager.load(save_manager.QUICK_SLOT):
                save_manager.autosave()
            continue
        if choice == "o":
            open_options_game_menu()
            continue
        if not choice.isdigit():
            print("🤔 Enter a choice number, or try: [I]nfo, [H]istory, [P]ause, [O]ptions, [Q]uit")
            continue
        idx = int(choice)
        if not (1 <= idx <= len(visible)):
            print("🤔 Please pick a valid choice number.")
            continue

        ch = visible[idx-1]
        if "__ending__" in state.player["flags"]:
            print(f"\n*** Ending reached: {state.player['flags']['__ending__']} ***"); break

        target = ch.get("target")
        if not target:
            print("[!] Choice had no target; staying put."); continue

        state.record_transition(node_id, target, ch.get("text","choice"))
        state.current_node = target

        if state.player["hp"] <= 0:
            demise = "A Short Tale"
            record_seen_ending(state, demise)
            print(f"\n*** You have perished. Ending: '{demise}' ***"); break

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[Interrupted] Bye.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[Fatal Error] {e}")
        print("If this persists, please report it as a bug with steps to reproduce.")
        sys.exit(1)
