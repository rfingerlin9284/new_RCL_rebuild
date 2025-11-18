#!/usr/bin/env python3
"""Runtime guard to assert the expected project root directory name.

Approved token 841921 was provided for structural changes enabling creation of this file.
This guard can be imported or executed directly. It validates that the resolved
project root matches the expected canonical name.

Usage:
    python runtime_guard/root_name_guard.py

Exit codes:
    0 - OK
    10 - Root name mismatch
"""
from __future__ import annotations
import pathlib
import sys
import os

# Canonical expected root directory name for this environment/clone.
#
# In the original environment this was "new_RLC_rebuild". For clean
# clones (e.g. N_RLC_rebuild) the environment/clone addendum in
# AGENT_HANDOFF_841921.md explicitly permits treating the clone's root
# as the active project root while keeping all governance intact.
EXPECTED_ROOTS = {"new_RLC_rebuild", "N_RLC_rebuild"}
# Allow legacy alias or symlink name for informational purposes.
LEGACY_ALIAS = "RICK_ACTIVE"

def get_project_root() -> pathlib.Path:
    # This file resides at <root>/runtime_guard/root_name_guard.py
    return pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    root_path = get_project_root()
    resolved_name = root_path.name

    # When invoked via a symlink path, Path.resolve() yields the real target
    # name. For cloned environments we allow either of the approved root
    # names listed in EXPECTED_ROOTS.
    ok = resolved_name in EXPECTED_ROOTS

    if ok:
        print(f"[root_name_guard] OK: project root resolved as '{resolved_name}'.")
    else:
        expected_str = ", ".join(sorted(EXPECTED_ROOTS))
        print(f"[root_name_guard] MISMATCH: resolved root '{resolved_name}' not in expected set {{{expected_str}}}")
        # Provide hint if it matches legacy alias
        if resolved_name == LEGACY_ALIAS:
            print("[root_name_guard] Legacy alias detected; consider standardizing to canonical name.")
        return 10

    # Optional additional assertion: ensure compatibility symlink exists for legacy tasks
    legacy_symlink = pathlib.Path(f"/home/ing/RICK/{LEGACY_ALIAS}")
    if legacy_symlink.is_symlink():
        try:
            target = legacy_symlink.resolve()
            if target.name != EXPECTED_ROOT:
                print(f"[root_name_guard] WARNING: legacy symlink points to '{target.name}', expected '{EXPECTED_ROOT}'.")
            else:
                print(f"[root_name_guard] Legacy symlink '{LEGACY_ALIAS}' -> '{target.name}' verified.")
        except Exception as e:
            print(f"[root_name_guard] WARNING: unable to resolve legacy symlink: {e}")
    else:
        print(f"[root_name_guard] INFO: legacy symlink '{LEGACY_ALIAS}' not present (may be intentional).")

    return 0

if __name__ == "__main__":
    sys.exit(main())
