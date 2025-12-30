#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Field Validation Script
Validate if JSON files completely cover all fields defined in fields.yaml
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple

# Category mapping (supports both Chinese and English)
CATEGORY_MAPPING = {
    "Basic Info": ["basic_info", "Basic Info"],
    "Technical Features": ["technical_features", "technical_characteristics", "Technical Features"],
    "Performance Metrics": ["performance_metrics", "performance", "Performance Metrics"],
    "Milestone Significance": ["milestone_significance", "milestones", "Milestone Significance"],
    "Business Info": ["business_info", "commercial_info", "Business Info"],
    "Competition & Ecosystem": ["competition_ecosystem", "competition", "Competition & Ecosystem"],
    "History": ["history", "History"],
    "Market Positioning": ["market_positioning", "market", "Market Positioning"],
}


def load_fields_yaml(fields_path: Path) -> Tuple[Set[str], Set[str], Dict[str, str]]:
    """
    Load fields.yaml, returns:
    - all_fields: Set of all field names
    - required_fields: Set of field names where required=true
    - field_categories: Mapping from field name to category
    """
    with open(fields_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    all_fields = set()
    required_fields = set()
    field_categories = {}

    for category_info in data.get("field_categories", []):
        category_name = category_info["category"]
        for field in category_info.get("fields", []):
            field_name = field["name"]
            all_fields.add(field_name)
            field_categories[field_name] = category_name
            if field.get("required", False):
                required_fields.add(field_name)

    return all_fields, required_fields, field_categories


def extract_json_fields(data: Dict, category_mapping: Dict = None) -> Set[str]:
    """
    Extract all field names from JSON (supports flat and nested structures)
    """
    if category_mapping is None:
        category_mapping = CATEGORY_MAPPING

    # Get all possible nested keys
    nested_keys = set()
    for keys in category_mapping.values():
        nested_keys.update(keys)

    fields = set()

    def collect_fields(d: Dict, is_top_level: bool = True):
        for k, v in d.items():
            # Skip internal fields
            if k in {"_source_file", "uncertain"}:
                continue
            # If it's a nested structure top-level key, recurse into it
            if is_top_level and k in nested_keys:
                if isinstance(v, dict):
                    collect_fields(v, is_top_level=False)
            else:
                fields.add(k)
                if isinstance(v, dict):
                    collect_fields(v, is_top_level=False)

    collect_fields(data)
    return fields


def validate_json(json_path: Path, all_fields: Set[str], required_fields: Set[str],
                  field_categories: Dict[str, str]) -> Dict:
    """
    Validate a single JSON file
    Returns validation result dictionary
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_fields = extract_json_fields(data)

    # Calculate coverage
    covered = all_fields & json_fields
    missing = all_fields - json_fields
    extra = json_fields - all_fields

    # Categorize missing fields
    missing_required = missing & required_fields
    missing_optional = missing - required_fields

    # Group missing fields by category
    missing_by_category = {}
    for field in missing:
        cat = field_categories.get(field, "Unknown")
        if cat not in missing_by_category:
            missing_by_category[cat] = []
        missing_by_category[cat].append(field)

    return {
        "file": json_path.name,
        "total_defined": len(all_fields),
        "covered": len(covered),
        "missing": len(missing),
        "extra": len(extra),
        "coverage_rate": len(covered) / len(all_fields) * 100 if all_fields else 100,
        "missing_required": list(missing_required),
        "missing_optional": list(missing_optional),
        "missing_by_category": missing_by_category,
        "extra_fields": list(extra),
        "valid": len(missing_required) == 0,  # Valid if all required fields are covered
    }


def print_result(result: Dict, verbose: bool = True):
    """Print validation result"""
    status = "PASS" if result["valid"] else "FAIL"
    print(f"\n{'='*60}")
    print(f"[{status}] {result['file']}")
    print(f"{'='*60}")
    print(f"Coverage: {result['coverage_rate']:.1f}% ({result['covered']}/{result['total_defined']})")

    if result["missing_required"]:
        print(f"\n[ERROR] Missing required fields ({len(result['missing_required'])}):")
        for field in result["missing_required"]:
            print(f"  - {field}")

    if verbose and result["missing_optional"]:
        print(f"\n[WARN] Missing optional fields ({len(result['missing_optional'])}):")
        for cat, fields in result["missing_by_category"].items():
            optional_fields = [f for f in fields if f not in result["missing_required"]]
            if optional_fields:
                print(f"  [{cat}]: {', '.join(optional_fields)}")

    if verbose and result["extra_fields"]:
        print(f"\n[INFO] Extra fields ({len(result['extra_fields'])}):")
        print(f"  {', '.join(result['extra_fields'][:10])}")
        if len(result["extra_fields"]) > 10:
            print(f"  ... and {len(result['extra_fields']) - 10} more fields")


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Validate if JSON files cover all fields defined in fields.yaml")
    parser.add_argument("--fields", "-f", type=str, help="Path to fields.yaml", default="fields.yaml")
    parser.add_argument("--json", "-j", type=str, nargs="*", help="JSON file paths to validate")
    parser.add_argument("--dir", "-d", type=str, help="JSON files directory", default="results")
    parser.add_argument("--quiet", "-q", action="store_true", help="Show summary only")
    args = parser.parse_args()

    # Locate fields.yaml
    fields_path = Path(args.fields)
    if not fields_path.exists():
        # Try to find in current and parent directory
        for p in [Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"]:
            if p.exists():
                fields_path = p
                break

    if not fields_path.exists():
        print(f"[ERROR] fields.yaml not found: {fields_path}")
        sys.exit(1)

    print(f"Field definitions file: {fields_path}")
    all_fields, required_fields, field_categories = load_fields_yaml(fields_path)
    print(f"Total fields: {len(all_fields)} (required: {len(required_fields)}, optional: {len(all_fields) - len(required_fields)})")

    # Collect JSON files
    json_files = []
    if args.json:
        json_files = [Path(p) for p in args.json]
    else:
        json_dir = Path(args.dir)
        if json_dir.exists():
            json_files = sorted(json_dir.glob("*.json"))

    if not json_files:
        print(f"[WARN] No JSON files found")
        sys.exit(0)

    # Validate each file
    results = []
    for json_path in json_files:
        if not json_path.exists():
            print(f"[WARN] File not found: {json_path}")
            continue
        result = validate_json(json_path, all_fields, required_fields, field_categories)
        results.append(result)
        print_result(result, verbose=not args.quiet)

    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r["valid"])
    avg_coverage = sum(r["coverage_rate"] for r in results) / len(results) if results else 0
    print(f"Validation passed: {passed}/{len(results)}")
    print(f"Average coverage: {avg_coverage:.1f}%")

    if passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
