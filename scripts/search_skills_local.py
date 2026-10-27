#!/usr/bin/env python3
"""Windows-compatible, read-only Huawei Cloud skill index search."""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# GitCode 是官方技能索引的数据源；索引文件包含全部技能元数据。
INDEX_URL = (
    "https://gitcode.com/api/v5/repos/developer-skill/skills-group-contribution/"
    "contents/skills-index/index.json?ref=test-for-index"
)
# 中英文映射用于把服务缩写扩展为常见中文名称。
CN_EN_MAP_URL = (
    "https://gitcode.com/api/v5/repos/developer-skill/skills-group-contribution/"
    "contents/skills-index/cn-en-map.json?ref=test-for-index"
)
# 单次请求的网络上限，单位为秒；超时后给出明确错误而不是挂起。
REQUEST_TIMEOUT_SECONDS = 30
# 搜索评分权重与官方技能保持一致，确保本机兼容版本不改变结果含义。
FIELD_WEIGHTS = {
    "name": 10,
    "triggers": 8,
    "description": 5,
    "service": 3,
}
# 中英文映射中存在少量被截断或混入示例文本的脏键；这些字符用于过滤脏值。
DIRTY_MAP_CHARS = (":", "：", '"', "'", "{", "}", "[", "]", "\\")
MAX_MAP_VALUE_LENGTH = 40


def run_curl_json(url: str) -> dict[str, Any]:
    """功能：通过 curl 读取 GitCode JSON，绕过本机不兼容的系统代理。

    输入：url 为公开 GitCode API 地址。
    输出：解析后的 JSON 对象；失败时抛出 RuntimeError。
    """
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise RuntimeError("未找到 curl，请先安装 curl 并加入 PATH")

    command = [
        curl,
        "--noproxy",
        "*",
        "--fail",
        "--silent",
        "--show-error",
        "--location",
        "--retry",
        "3",
        "--retry-all-errors",
        "--connect-timeout",
        "15",
        "--max-time",
        str(REQUEST_TIMEOUT_SECONDS),
        url,
    ]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=REQUEST_TIMEOUT_SECONDS + 5,
        )
        return json.loads(completed.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"读取 GitCode 数据失败：{exc}") from exc


def decode_gitcode_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """功能：解码 GitCode contents API 返回的 Base64 文件内容。

    输入：payload 为 GitCode 文件响应。
    输出：解码后的 JSON 对象；普通 JSON 响应原样返回。
    """
    if payload.get("encoding") != "base64" or "content" not in payload:
        return payload
    decoded = base64.b64decode(payload["content"], validate=True).decode("utf-8")
    return json.loads(decoded)


def load_remote_json(url: str) -> dict[str, Any]:
    """功能：读取并解码一个 GitCode 远程 JSON 文件。

    输入：url 为公开 GitCode API 地址。
    输出：解码后的 JSON 对象；网络或格式错误时抛出 RuntimeError。
    """
    try:
        return decode_gitcode_payload(run_curl_json(url))
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"GitCode 返回内容不是有效 JSON：{exc}") from exc


def is_clean_map_value(value: Any) -> bool:
    """功能：判断中英文映射值是否适合作为检索词。

    输入：value 为映射中的键或值。
    输出：值是干净且长度合理的非空字符串时返回 True，否则返回 False。
    """
    if not isinstance(value, str):
        return False
    if value != value.strip() or not value or len(value) > MAX_MAP_VALUE_LENGTH:
        return False
    return not any(char in value for char in DIRTY_MAP_CHARS)


def expand_keywords(raw_keyword: str, cn_en_map: dict[str, Any]) -> list[str]:
    """功能：把中英文关键词互相扩展，提升云服务检索召回率。

    输入：raw_keyword 为用户输入的关键词串；cn_en_map 为中英文映射。
    输出：去重后的关键词列表，顺序稳定。
    """
    parts = [
        part.strip()
        for separator in (",", ";")
        for chunk in raw_keyword.split(separator)
        for part in chunk.split()
        if part.strip()
    ]
    expanded = list(parts)
    for part in parts:
        part_lower = part.lower()
        mapped = cn_en_map.get(part)
        if is_clean_map_value(mapped):
            expanded.append(mapped)
        elif isinstance(mapped, list):
            expanded.extend(item for item in mapped if is_clean_map_value(item))
        for chinese, english in cn_en_map.items():
            if (
                is_clean_map_value(chinese)
                and isinstance(english, str)
                and english.lower() == part_lower
            ):
                expanded.append(chinese)
    return list(dict.fromkeys(expanded))


def score_skill(skill: dict[str, Any], keywords: list[str]) -> tuple[int, list[str]]:
    """功能：按名称、触发词、描述和服务字段给技能匹配度评分。

    输入：skill 为单条技能元数据；keywords 为扩展后的关键词列表。
    输出：二元组（总评分，命中关键词列表）。
    """
    name = str(skill.get("name", "")).lower()
    description = str(skill.get("description", "")).lower()
    triggers = [str(item).lower() for item in skill.get("triggers", []) if item]
    services = [str(skill.get("service", "")).lower()]
    services.extend(str(item).lower() for item in skill.get("services", []) if item)

    total = 0
    matched: list[str] = []
    for keyword in keywords:
        token = keyword.lower()
        score = 0
        if token in name:
            score += FIELD_WEIGHTS["name"]
        if any(token in trigger for trigger in triggers):
            score += FIELD_WEIGHTS["triggers"]
        if token in description:
            score += FIELD_WEIGHTS["description"]
        if any(token in service for service in services):
            score += FIELD_WEIGHTS["service"]
        if score:
            total += score
            matched.append(keyword)
    return total, matched


def search_skills(
    skills: list[dict[str, Any]],
    keywords: list[str],
    category: str,
    limit: int,
) -> list[dict[str, Any]]:
    """功能：筛选并排序技能索引。

    输入：skills 为技能列表；keywords 为扩展关键词；category 为空表示不过滤；
          limit 为最多返回条数。
    输出：按评分降序排列的结果字典列表。
    """
    results: list[dict[str, Any]] = []
    for skill in skills:
        if category and skill.get("category") != category:
            continue
        score, matched = score_skill(skill, keywords)
        if keywords and score == 0:
            continue
        results.append(
            {
                "score": score,
                "name": skill.get("name", ""),
                "category": skill.get("category", ""),
                "service": skill.get("service", ""),
                "services": skill.get("services", []),
                "description": skill.get("description", ""),
                "triggers": skill.get("triggers", [])[:8],
                "matched": matched,
            }
        )
    results.sort(key=lambda item: (-item["score"], item["name"]))
    return results[:limit]


def print_text_results(
    keyword: str,
    category: str,
    keywords: list[str],
    results: list[dict[str, Any]],
) -> None:
    """功能：以适合人工阅读的格式输出搜索结果。

    输入：keyword 与 category 为原始条件；keywords 为扩展词；
          results 为排序后的结果列表。
    输出：无返回值，直接写入标准输出。
    """
    heading = f"关键词：{keyword or '(空)'}；分类：{category or '(全部)'}"
    print(heading)
    print(f"扩展词：{', '.join(keywords) if keywords else '(无)'}")
    print(f"命中数量：{len(results)}")
    if not results:
        print("未找到匹配技能。建议改用中英文同义词，或移除分类过滤。")
        return

    for result in results:
        service_scope = ", ".join(result["services"]) or "(未列出)"
        print(
            f"\n[{result['score']}分] {result['name']} "
            f"({result['category']}/{result['service']})"
        )
        print(f"服务范围：{service_scope}")
        print(f"命中词：{', '.join(result['matched'])}")
        print(f"说明：{result['description']}")


def main() -> int:
    """功能：解析命令行参数并执行实时技能索引搜索。

    输入：命令行参数（关键词、分类、结果数、JSON 输出）。
    输出：进程退出码；0 表示搜索完成，2 表示输入错误，1 表示远程错误。
    """
    parser = argparse.ArgumentParser(description="搜索华为云官方技能索引")
    parser.add_argument("-k", "--keyword", default="", help="关键词，支持中英文")
    parser.add_argument("-c", "--category", default="", help="分类过滤")
    parser.add_argument("--limit", type=int, default=10, help="最多显示条数")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    if not args.keyword and not args.category:
        parser.error("至少提供 --keyword 或 --category")
    if args.limit < 1:
        parser.error("--limit 必须大于 0")

    try:
        index = load_remote_json(INDEX_URL)
        cn_en_map = load_remote_json(CN_EN_MAP_URL) if args.keyword else {}
    except RuntimeError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    keywords = expand_keywords(args.keyword, cn_en_map)
    results = search_skills(
        list(index.get("skills", [])),
        keywords,
        args.category,
        args.limit,
    )

    if args.json:
        output = {
            "keyword": args.keyword,
            "category": args.category,
            "expanded_keywords": keywords,
            "generated_at": index.get("generated_at"),
            "total_indexed_skills": index.get("total_skills", len(index.get("skills", []))),
            "results": results,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_text_results(args.keyword, args.category, keywords, results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
