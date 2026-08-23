#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression test for skills/*/research/validate_json.py.

The validator accepts EXACTLY ONE schema — the one /research actually emits:

    fields:
      <category>:
        - {name: ..., description: ..., detail_level: ...}
    uncertain: []

Any other shape must be rejected (exit 1), never silently pass with zero fields.
With no explicit `required:` markers, every field is required so incomplete coverage
actually fails. With explicit markers, opt-in semantics are preserved.

Run:  python tests/test_validate_json_schemas.py   (exit 0 = all pass)
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = sorted(ROOT.glob("skills/*/research/validate_json.py"))

tmp = Path(tempfile.mkdtemp())
# The one accepted schema: fields:{<category>:[{name, detail_level}]} with NO `required` markers.
(tmp / "good_schema.yaml").write_text(
    "fields:\n"
    "  basic:\n"
    "    - {name: a, detail_level: detailed}\n"
    "    - {name: b, detail_level: brief}\n"
    "    - {name: c, detail_level: moderate}\n"
    "    - {name: d, detail_level: moderate}\n"
    "uncertain: []\n", encoding="utf-8")
# Same shape but with explicit required markers -> opt-in semantics.
(tmp / "marked_schema.yaml").write_text(
    "fields:\n"
    "  basic:\n"
    "    - {name: a, required: true}\n"
    "    - {name: b, required: true}\n"
    "    - {name: notes, required: false}\n", encoding="utf-8")
# A rejected shape: the old `field_categories:` form.
(tmp / "bad_schema.yaml").write_text(
    "field_categories:\n"
    "  - category: basic\n"
    "    fields:\n"
    "      - {name: a}\n", encoding="utf-8")
(tmp / "good.json").write_text(json.dumps({"a": 1, "b": 1, "c": 1, "d": 1}), encoding="utf-8")
(tmp / "bad.json").write_text(json.dumps({"a": 1, "b": 1, "c": 1}), encoding="utf-8")  # missing 'd'


def load(path, i):
    spec = importlib.util.spec_from_file_location(f"vj{i}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fails = []
def check(label, cond):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        fails.append(label)


assert COPIES, "no validate_json.py copies found under skills/*/research/"
for i, path in enumerate(COPIES):
    tag = path.relative_to(ROOT).parts[1]  # e.g. research-en
    m = load(path, i)

    # 1. The one accepted schema parses all 4 fields; all required (no markers).
    a, r, _ = m.load_fields_yaml(tmp / "good_schema.yaml")
    check(f"[{tag}] good_schema parses 4 fields (was 0 before fix)", a == {"a", "b", "c", "d"})
    check(f"[{tag}] all required when unmarked (no vacuous pass)", r == a)

    # 2. Explicit markers preserve opt-in semantics.
    am, rm, _ = m.load_fields_yaml(tmp / "marked_schema.yaml")
    check(f"[{tag}] marked_schema: 3 fields, 'notes' optional", am == {"a", "b", "notes"} and rm == {"a", "b"})

    # 3. A complete JSON passes; a JSON missing a field actually fails.
    good = m.validate_json(tmp / "good.json", a, r, _)
    bad = m.validate_json(tmp / "bad.json", a, r, _)
    check(f"[{tag}] good.json -> valid", good["valid"])
    check(f"[{tag}] bad.json  -> INVALID (catches missing 'd')", (not bad["valid"]) and "d" in bad["missing_required"])

    # 4. A rejected schema shape must make the CLI exit non-zero (run as subprocess).
    proc = subprocess.run([sys.executable, str(path), "-f", str(tmp / "bad_schema.yaml"), "-d", str(tmp)],
                          capture_output=True, text=True)
    check(f"[{tag}] bad_schema (field_categories) is REJECTED (exit != 0)", proc.returncode != 0)

print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILED -> {fails}")
sys.exit(1 if fails else 0)
