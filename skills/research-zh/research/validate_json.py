#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml

CATEGORY_MAPPING = {
    "基本信息": ["basic_info", "基本信息"],
    "技术特性": ["technical_features", "technical_characteristics", "技术特性"],
    "性能指标": ["performance_metrics", "performance", "性能指标"],
    "里程碑意义": ["milestone_significance", "milestones", "里程碑意义"],
    "商业信息": ["business_info", "commercial_info", "商业信息"],
    "竞争与生态": ["competition_ecosystem", "competition", "竞争与生态"],
    "历史沿革": ["history", "历史沿革"],
    "市场定位": ["market_positioning", "market", "市场定位"],
}

_SKIP_KEYS = {"_source_file", "uncertain"}


def _iter_field_defs(node, category="(uncategorized)"):
    """Generic fallback: yield (field_dict, category) for any dict carrying a 'name'."""
    if isinstance(node, dict):
        if isinstance(node.get("name"), (str, int, float)):
            yield node, category
            return
        for k, v in node.items():
            if k in _SKIP_KEYS:
                continue
            sub = category if k in ("fields", "field_categories") else str(k)
            yield from _iter_field_defs(v, sub)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_field_defs(item, category)


def load_fields_yaml(fields_path):
    """Parse fields.yaml, tolerating the shapes the research skills actually emit:
      A) field_categories: [ {category, fields: [{name, required?}]} ]   (validator-native)
      B) fields: { <category>: [ {name, description, detail_level} ] }   (research-skill docs)
      C) fields: [ {name, ...} ]                                         (flat list)
      *) anything else -> generic walk for {name: ...} dicts

    Required semantics (so the validator can never pass vacuously / "lie"):
      - if ANY field carries an explicit `required:` key -> opt-in, preserve original behaviour
      - else (detail_level-style, no markers)            -> ALL fields required, because the
        script's stated purpose is COMPLETE field coverage.
    """
    with fields_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    defs = []  # (name, category, required_or_None)

    def add(field, category):
        if isinstance(field, dict) and "name" in field:
            defs.append((str(field["name"]), str(category), field.get("required", None)))

    fc = data.get("field_categories")
    if isinstance(fc, list):                                       # Schema A
        for cat in fc:
            if isinstance(cat, dict):
                cname = cat.get("category", "(uncategorized)")
                for field in cat.get("fields", []) or []:
                    add(field, cname)

    if not defs:                                                   # Schema B / C
        fn = data.get("fields")
        if isinstance(fn, dict):
            for cname, flist in fn.items():
                if isinstance(flist, list):
                    for field in flist:
                        add(field, cname)
                else:
                    add(flist, cname)
        elif isinstance(fn, list):
            for field in fn:
                add(field, "(uncategorized)")

    if not defs:                                                   # generic fallback
        for field, cat in _iter_field_defs(data):
            add(field, cat)

    all_fields = {n for n, _, _ in defs}
    if any(r is not None for _, _, r in defs):
        required_fields = {n for n, _, r in defs if r}
    else:
        required_fields = set(all_fields)
    field_categories = {n: c for n, c, _ in defs}
    return all_fields, required_fields, field_categories


def extract_json_fields(data, category_mapping=None, extra_nested_keys=None):
    category_mapping = CATEGORY_MAPPING if category_mapping is None else category_mapping
    nested_keys = {k for keys in category_mapping.values() for k in keys}
    if extra_nested_keys:
        nested_keys |= {str(k) for k in extra_nested_keys}
    fields = set()
    stack = [(data, True)]
    while stack:
        obj, is_category_level = stack.pop()
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in _SKIP_KEYS:
                    continue
                if is_category_level and k in nested_keys:
                    if isinstance(v, dict):
                        stack.append((v, True))
                    continue
                fields.add(k)
        elif isinstance(obj, list):
            stack.extend((item, is_category_level) for item in obj if isinstance(item, dict))
    return fields


def validate_json(json_path, all_fields, required_fields, field_categories):
    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)
    json_fields = extract_json_fields(data, extra_nested_keys=set(field_categories.values()))
    covered = all_fields & json_fields
    missing = all_fields - json_fields
    extra = json_fields - all_fields
    missing_required = missing & required_fields
    missing_by_category = defaultdict(list)
    for field in missing:
        missing_by_category[field_categories.get(field, "未知")].append(field)
    return {
        "file": json_path.name,
        "total_defined": len(all_fields),
        "covered": len(covered),
        "missing": len(missing),
        "extra": len(extra),
        "coverage_rate": len(covered) / len(all_fields) * 100 if all_fields else 100,
        "missing_required": sorted(missing_required),
        "missing_optional": sorted(missing - required_fields),
        "missing_by_category": {k: sorted(v) for k, v in missing_by_category.items()},
        "extra_fields": sorted(extra),
        "valid": len(missing_required) == 0,
    }


def print_result(result, verbose=True):
    status = "通过" if result["valid"] else "失败"
    line = "=" * 60
    print(f"\n{line}")
    print(f"[{status}] {result['file']}")
    print(line)
    print(f"覆盖率: {result['coverage_rate']:.1f}% ({result['covered']}/{result['total_defined']})")
    if result["missing_required"]:
        print(f"\n[错误] 缺少必填字段 ({len(result['missing_required'])}):")
        print("\n".join(f"  - {f}" for f in result["missing_required"]))
    if verbose and result["missing_optional"]:
        missing_required = set(result["missing_required"])
        print(f"\n[警告] 缺少可选字段 ({len(result['missing_optional'])}):")
        for cat in sorted(result["missing_by_category"]):
            optional = [f for f in result["missing_by_category"][cat] if f not in missing_required]
            if optional:
                print(f"  [{cat}]: {', '.join(optional)}")
    if verbose and result["extra_fields"]:
        extra = result["extra_fields"]
        print(f"\n[信息] 额外字段 ({len(extra)}):")
        print(f"  {', '.join(extra[:10])}")
        if len(extra) > 10:
            print(f"  ... 还有 {len(extra) - 10} 个")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="验证JSON文件是否覆盖fields.yaml中定义的所有字段")
    parser.add_argument("--fields", "-f", type=str, help="fields.yaml路径", default="fields.yaml")
    parser.add_argument("--json", "-j", type=str, nargs="*", help="要验证的JSON文件路径")
    parser.add_argument("--dir", "-d", type=str, help="包含JSON文件的目录", default="results")
    parser.add_argument("--quiet", "-q", action="store_true", help="仅显示摘要")
    args = parser.parse_args()
    fields_path = Path(args.fields)
    if not fields_path.exists():
        for p in (Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"):
            if p.exists():
                fields_path = p
                break
    if not fields_path.exists():
        print(f"[错误] 找不到fields.yaml: {fields_path}")
        sys.exit(1)
    print(f"字段定义文件: {fields_path}")
    all_fields, required_fields, field_categories = load_fields_yaml(fields_path)
    print(f"总字段数: {len(all_fields)} (必填: {len(required_fields)}, 可选: {len(all_fields) - len(required_fields)})")
    json_files = (
        [Path(p) for p in args.json]
        if args.json
        else sorted(Path(args.dir).glob("*.json")) if Path(args.dir).exists() else []
    )
    if not json_files:
        print("[警告] 未找到JSON文件")
        sys.exit(0)
    results = []
    for json_path in json_files:
        if not json_path.exists():
            print(f"[警告] 文件不存在: {json_path}")
            continue
        result = validate_json(json_path, all_fields, required_fields, field_categories)
        results.append(result)
        print_result(result, verbose=not args.quiet)
    line = "=" * 60
    print(f"\n{line}")
    print("汇总")
    print(line)
    passed = sum(1 for r in results if r["valid"])
    avg_coverage = sum(r["coverage_rate"] for r in results) / len(results) if results else 0
    print(f"验证通过: {passed}/{len(results)}")
    print(f"平均覆盖率: {avg_coverage:.1f}%")
    if passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
