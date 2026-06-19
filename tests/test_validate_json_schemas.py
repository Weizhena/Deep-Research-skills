#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression test for skills/*/research/validate_json.py.

Guards two bugs that made the validator pass vacuously (a "green" that means nothing):
  1. Only the `field_categories:` schema was parsed. But /research emits fields.yaml as
     `fields: {<category>: [{name, description, detail_level}]}`, which was read as ZERO
     fields -> coverage defaulted to 100% -> every JSON "passed".
  2. `required` defaulted to False, so `valid` (== no missing required) was True even when
     fields were missing.

After the fix, the loader accepts the `field_categories`, `fields:{cat:[...]}` and flat
`fields:[...]` shapes (plus a generic fallback), and treats every field as required when no
explicit `required:` marker is present. A JSON missing a defined field now actually FAILS.

Run:  python tests/test_validate_json_schemas.py   (exit 0 = all pass)
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = sorted(ROOT.glob("skills/*/research/validate_json.py"))

tmp = Path(tempfile.mkdtemp())
# Schema A: field_categories + explicit `required` (one optional field 'notes')
(tmp / "A.yaml").write_text(
    "field_categories:\n"
    "  - category: basic\n"
    "    fields:\n"
    "      - {name: a, required: true}\n"
    "      - {name: b, required: true}\n"
    "      - {name: notes, required: false}\n", encoding="utf-8")
# Schema B: nested fields:{category:[...]} with detail_level, NO `required` markers
(tmp / "B.yaml").write_text(
    "fields:\n"
    "  basic:\n"
    "    - {name: a, detail_level: detailed}\n"
    "    - {name: b, detail_level: brief}\n"
    "    - {name: c, detail_level: moderate}\n"
    "    - {name: d, detail_level: moderate}\n"
    "uncertain: []\n", encoding="utf-8")
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

    aA, rA, _ = m.load_fields_yaml(tmp / "A.yaml")
    check(f"[{tag}] Schema A: parses 3, keeps 'notes' optional", aA == {"a", "b", "notes"} and rA == {"a", "b"})

    aB, rB, cB = m.load_fields_yaml(tmp / "B.yaml")
    check(f"[{tag}] Schema B: parses 4 fields (was 0 before fix)", aB == {"a", "b", "c", "d"})
    check(f"[{tag}] Schema B: all required when unmarked (no vacuous pass)", rB == aB)

    good = m.validate_json(tmp / "good.json", aB, rB, cB)
    bad = m.validate_json(tmp / "bad.json", aB, rB, cB)
    check(f"[{tag}] good.json -> valid", good["valid"])
    check(f"[{tag}] bad.json  -> INVALID (catches missing 'd')", (not bad["valid"]) and "d" in bad["missing_required"])

print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILED -> {fails}")
sys.exit(1 if fails else 0)
