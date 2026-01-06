#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON字段验证脚本
验证JSON文件是否完整覆盖fields.yaml中定义的所有字段
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple

# Category中英文映射
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


def load_fields_yaml(fields_path: Path) -> Tuple[Set[str], Set[str], Dict[str, str]]:
    """
    加载fields.yaml，返回：
    - all_fields: 所有字段名集合
    - required_fields: required=true的字段名集合
    - field_categories: 字段名到类别的映射
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
    从JSON中提取所有字段名（支持扁平和嵌套结构）
    """
    if category_mapping is None:
        category_mapping = CATEGORY_MAPPING

    # 获取所有可能的嵌套key
    nested_keys = set()
    for keys in category_mapping.values():
        nested_keys.update(keys)

    fields = set()

    def collect_fields(d: Dict, is_top_level: bool = True):
        for k, v in d.items():
            # 跳过内部字段
            if k in {"_source_file", "uncertain"}:
                continue
            # 如果是嵌套结构的顶级key，递归进入
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
    验证单个JSON文件
    返回验证结果字典
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    json_fields = extract_json_fields(data)

    # 计算覆盖情况
    covered = all_fields & json_fields
    missing = all_fields - json_fields
    extra = json_fields - all_fields

    # 分类缺失字段
    missing_required = missing & required_fields
    missing_optional = missing - required_fields

    # 按类别分组缺失字段
    missing_by_category = {}
    for field in missing:
        cat = field_categories.get(field, "未知")
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
        "valid": len(missing_required) == 0,  # required字段全覆盖则valid
    }


def print_result(result: Dict, verbose: bool = True):
    """打印验证结果"""
    status = "PASS" if result["valid"] else "FAIL"
    print(f"\n{'='*60}")
    print(f"[{status}] {result['file']}")
    print(f"{'='*60}")
    print(f"覆盖率: {result['coverage_rate']:.1f}% ({result['covered']}/{result['total_defined']})")

    if result["missing_required"]:
        print(f"\n[ERROR] 缺失必需字段 ({len(result['missing_required'])}):")
        for field in result["missing_required"]:
            print(f"  - {field}")

    if verbose and result["missing_optional"]:
        print(f"\n[WARN] 缺失可选字段 ({len(result['missing_optional'])}):")
        for cat, fields in result["missing_by_category"].items():
            optional_fields = [f for f in fields if f not in result["missing_required"]]
            if optional_fields:
                print(f"  [{cat}]: {', '.join(optional_fields)}")

    if verbose and result["extra_fields"]:
        print(f"\n[INFO] 额外字段 ({len(result['extra_fields'])}):")
        print(f"  {', '.join(result['extra_fields'][:10])}")
        if len(result["extra_fields"]) > 10:
            print(f"  ... 及 {len(result['extra_fields']) - 10} 个其他字段")


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="验证JSON文件是否覆盖fields.yaml定义的所有字段")
    parser.add_argument("--fields", "-f", type=str, help="fields.yaml路径", default="fields.yaml")
    parser.add_argument("--json", "-j", type=str, nargs="*", help="要验证的JSON文件路径")
    parser.add_argument("--dir", "-d", type=str, help="JSON文件目录", default="results")
    parser.add_argument("--quiet", "-q", action="store_true", help="只显示摘要")
    args = parser.parse_args()

    # 定位fields.yaml
    fields_path = Path(args.fields)
    if not fields_path.exists():
        # 尝试在当前目录和父目录查找
        for p in [Path.cwd() / "fields.yaml", Path.cwd().parent / "fields.yaml"]:
            if p.exists():
                fields_path = p
                break

    if not fields_path.exists():
        print(f"[ERROR] fields.yaml不存在: {fields_path}")
        sys.exit(1)

    print(f"字段定义文件: {fields_path}")
    all_fields, required_fields, field_categories = load_fields_yaml(fields_path)
    print(f"总字段数: {len(all_fields)} (必需: {len(required_fields)}, 可选: {len(all_fields) - len(required_fields)})")

    # 收集JSON文件
    json_files = []
    if args.json:
        json_files = [Path(p) for p in args.json]
    else:
        json_dir = Path(args.dir)
        if json_dir.exists():
            json_files = sorted(json_dir.glob("*.json"))

    if not json_files:
        print(f"[WARN] 未找到JSON文件")
        sys.exit(0)

    # 验证每个文件
    results = []
    for json_path in json_files:
        if not json_path.exists():
            print(f"[WARN] 文件不存在: {json_path}")
            continue
        result = validate_json(json_path, all_fields, required_fields, field_categories)
        results.append(result)
        print_result(result, verbose=not args.quiet)

    # 汇总
    print(f"\n{'='*60}")
    print("汇总")
    print(f"{'='*60}")
    passed = sum(1 for r in results if r["valid"])
    avg_coverage = sum(r["coverage_rate"] for r in results) / len(results) if results else 0
    print(f"验证通过: {passed}/{len(results)}")
    print(f"平均覆盖率: {avg_coverage:.1f}%")

    if passed < len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
