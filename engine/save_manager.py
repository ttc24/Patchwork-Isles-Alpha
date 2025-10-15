"""Save management utilities for Patchwork Isles."""

from __future__ import annotations

import copy
import json
import shutil
import string
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional


class SaveError(Exception):
    """Base class for save related failures."""


class SaveCorruptError(SaveError):
    """Raised when a save file cannot be parsed or validated."""


@dataclass
class SlotMetadata:
    slot: str
    saved_at: Optional[str] = None
    player_name: Optional[str] = None
    active_area: Optional[str] = None


class SaveManager:
    """Handle save/load/autosave orchestration with backups."""

    SCHEMA_VERSION = 1
    SAVE_FILENAME = "save_v1.json"
    BACKUP_FILENAME = "save_v1.bak"
    AUTOSAVE_SLOT = "autosave"
    QUICK_SLOT = "quick"
    _VALID_SLOT_CHARS = set(string.ascii_lowercase + string.digits + "-_")

    def __init__(
        self,
        state,
        base_path: Path | str = "saves",
        *,
        input_func: Callable[[str], str] = input,
        print_func: Callable[[str], None] = print,
    ) -> None:
        self.state = state
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.input = input_func
        self.print = print_func

    # ---------- Public API ----------
    def save(self, slot: str, *, label: Optional[str] = None, quiet: bool = False) -> Path:
        normalized = self._normalize_slot(slot)
        path = self._slot_path(normalized)
        path.mkdir(parents=True, exist_ok=True)
        save_path = path / self.SAVE_FILENAME
        backup_path = path / self.BACKUP_FILENAME

        payload = self._build_payload(normalized)
        self._write_payload(save_path, backup_path, payload, make_backup=True)

        if not quiet:
            tag = label or "Saved"
            self.print(f"[{tag}] Slot '{normalized}' written to {save_path}.")
        return save_path

    def load(self, slot: str, *, prefer_backup: bool = False) -> bool:
        normalized = self._normalize_slot(slot)
        path = self._slot_path(normalized)
        save_path = path / self.SAVE_FILENAME
        backup_path = path / self.BACKUP_FILENAME

        target_path = backup_path if prefer_backup else save_path
        if not target_path.exists():
            if not save_path.exists():
                self.print(f"[!] No save found for slot '{normalized}'.")
                return False
            target_path = save_path

        try:
            payload = self._read_payload(target_path)
        except SaveCorruptError as err:
            if backup_path.exists() and target_path != backup_path:
                self.print(f"[!] Save slot '{normalized}' is corrupted: {err}")
                if self._confirm_restore(normalized):
                    try:
                        payload = self._read_payload(backup_path)
                    except SaveError as backup_err:
                        self.print(
                            f"[!] Backup for slot '{normalized}' also failed: {backup_err}"
                        )
                        return False
                    self._write_payload(
                        save_path, backup_path, payload, make_backup=False
                    )
                    self.print(
                        f"[Restore] Backup save applied for slot '{normalized}'."
                    )
                else:
                    self.print("[!] Load cancelled.")
                    return False
            else:
                self.print(
                    f"[!] Failed to load slot '{normalized}': {err}. No backup available."
                )
                return False
        except SaveError as err:
            self.print(f"[!] Failed to load slot '{normalized}': {err}")
            return False

        self._apply_payload(payload)
        self.print(f"[Loaded] Slot '{normalized}' from {target_path}.")
        return True

    def autosave(self) -> Optional[Path]:
        if not getattr(self.state, "current_node", None):
            return None
        return self.save(self.AUTOSAVE_SLOT, label="Autosave", quiet=True)

    def list_slots(self, *, include_special: bool = False) -> List[SlotMetadata]:
        slots: List[SlotMetadata] = []
        if not self.base_path.exists():
            return slots
        for child in sorted(self.base_path.iterdir()):
            if not child.is_dir():
                continue
            name = child.name
            if not include_special and name == self.AUTOSAVE_SLOT:
                continue
            main_path = child / self.SAVE_FILENAME
            if not main_path.exists():
                continue
            metadata = self._read_metadata(main_path)
            slots.append(metadata)
        return slots

    # ---------- Internal helpers ----------
    def _normalize_slot(self, slot: str) -> str:
        slot = (slot or "").strip().lower()
        if slot in {self.AUTOSAVE_SLOT, self.QUICK_SLOT}:
            return slot
        cleaned = "".join(ch for ch in slot if ch in self._VALID_SLOT_CHARS)
        if not cleaned:
            raise SaveError("Slot names must contain letters or numbers.")
        if cleaned == self.AUTOSAVE_SLOT:
            raise SaveError("The autosave slot is reserved.")
        return cleaned

    def _slot_path(self, slot: str) -> Path:
        return self.base_path / slot

    def _build_payload(self, slot: str) -> Dict:
        self.state.ensure_consistency()
        history = copy.deepcopy(self.state.history)
        metadata = {
            "schema": "save_v1",
            "version": self.SCHEMA_VERSION,
            "save_slot": slot,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "world_title": self.state.world.get("title")
            if isinstance(self.state.world, dict)
            else None,
            "world_seed": getattr(self.state, "world_seed", 0),
            "active_area": getattr(self.state, "active_area", None),
            "player_name": self.state.player.get("name"),
        }

        payload = {
            "version": self.SCHEMA_VERSION,
            "metadata": metadata,
            "state": {
                "current_node": self.state.current_node,
                "history": history,
                "start_id": self.state.start_id,
                "player": copy.deepcopy(self.state.player),
                "active_area": getattr(self.state, "active_area", None),
                "world_seed": getattr(self.state, "world_seed", 0),
            },
        }
        return payload

    def _write_payload(
        self,
        save_path: Path,
        backup_path: Path,
        payload: Dict,
        *,
        make_backup: bool,
    ) -> None:
        tmp_path = save_path.with_suffix(save_path.suffix + ".tmp")
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        if make_backup and save_path.exists():
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(save_path, backup_path)
        tmp_path.replace(save_path)

    def _read_payload(self, path: Path) -> Dict:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except FileNotFoundError as exc:
            raise SaveError("Save file missing.") from exc
        except json.JSONDecodeError as exc:
            raise SaveCorruptError(f"Invalid JSON: {exc}") from exc
        self._validate_payload(payload)
        return payload

    def _validate_payload(self, payload: Dict) -> None:
        if not isinstance(payload, dict):
            raise SaveCorruptError("Payload was not an object.")
        version = payload.get("version")
        if version != self.SCHEMA_VERSION:
            raise SaveCorruptError(f"Unsupported schema version: {version!r}")
        state = payload.get("state")
        if not isinstance(state, dict):
            raise SaveCorruptError("State block missing.")
        for key in ("player", "current_node"):
            if key not in state:
                raise SaveCorruptError(f"Missing key: state.{key}")
        if not isinstance(state.get("player"), dict):
            raise SaveCorruptError("Player block malformed.")

    def _apply_payload(self, payload: Dict) -> None:
        state_blob = payload["state"]
        self.state.player = state_blob.get("player", {})
        self.state.current_node = state_blob.get("current_node")
        self.state.history = state_blob.get("history", [])
        self.state.start_id = state_blob.get("start_id")
        self.state.active_area = state_blob.get("active_area", self.state.active_area)
        self.state.world_seed = state_blob.get("world_seed", self.state.world_seed)
        self.state.ensure_consistency()

    def _confirm_restore(self, slot: str) -> bool:
        response = self.input(
            f"Restore backup for slot '{slot}'? [y/N]: "
        ).strip().lower()
        return response in {"y", "yes"}

    def _read_metadata(self, path: Path) -> SlotMetadata:
        try:
            payload = self._read_payload(path)
        except SaveError:
            return SlotMetadata(slot=path.parent.name)
        metadata = payload.get("metadata", {})
        return SlotMetadata(
            slot=path.parent.name,
            saved_at=metadata.get("saved_at"),
            player_name=metadata.get("player_name"),
            active_area=metadata.get("active_area"),
        )
