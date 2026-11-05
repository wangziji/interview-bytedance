#!/usr/bin/env python3
"""Assemble public/js/data.js from tested snippets and interview copy."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site_src"))

from meta import HOME, PLAN, PROJECT  # noqa: E402
from problems import PROBLEMS  # noqa: E402
from quiz import QUIZ  # noqa: E402
from tracks_lang import ANDROID_CARDS, GO_CARDS, JAVA_CARDS, PYTHON_CARDS  # noqa: E402
from tracks_lbs import LBS_CARDS  # noqa: E402
from tracks_hot import HOT_CARDS  # noqa: E402
from tracks_system import AGENT_CARDS, BACKEND_CARDS, DESIGNS, REC_CARDS  # noqa: E402


def extract(path: Path, pattern: str) -> dict[str, str]:
    text = path.read_text()
    found = {}
    for match in re.finditer(pattern, text, re.S):
        found[match.group(1)] = match.group(2).strip("\n")
    return found


def dedent_java(snippet: str) -> str:
    lines = []
    for line in snippet.splitlines():
        lines.append(line[4:] if line.startswith("    ") else line)
    return "\n".join(lines).strip("\n")


def main() -> None:
    java = {}
    for path in sorted((ROOT / "code/java").glob("*.java")):
        java.update({
            key: dedent_java(value)
            for key, value in extract(
                path,
                r"/\* SNIP:(\w+) \*/\n(.*?)[ \t]*/\* END:\1 \*/",
            ).items()
        })
    go = {}
    for path in sorted((ROOT / "code/go").glob("*.go")):
        if path.name.endswith("_test.go"):
            continue
        go.update(extract(path, r"// SNIP:(\w+)\n(.*?)// END:\1"))
    python = {}
    for path in sorted((ROOT / "code/python").glob("*.py")):
        python.update(extract(path, r"# SNIP:(\w+)\n(.*?)# END:\1"))

    problems = []
    for problem in PROBLEMS:
        snip = problem["snip"]
        missing = [lang for lang, bag in (("java", java), ("go", go), ("python", python)) if snip not in bag]
        if missing:
            raise SystemExit(f"{snip} missing in {missing}")
        item = dict(problem)
        item["code"] = {"Java": java[snip], "Go": go[snip], "Python": python[snip]}
        problems.append(item)

    tracks = [
        {
            "id": "lbs",
            "title": "LBS 领域",
            "blurb": "坐标系、索引、轨迹、围栏、路径。这是 LBS 岗和通用后台岗的分界。",
            "cards": LBS_CARDS,
        },
        {
            "id": "hot",
            "title": "高频追问",
            "blurb": "3-1、3-2 会从面经里的这些点追到实现和取舍：MySQL、Redis、Kafka、限流、一致性、网络。",
            "cards": HOT_CARDS,
        },
        {
            "id": "java",
            "title": "Java",
            "blurb": "并发、JVM 和事务。地理服务只是这些基础题的场景，不会替你挡掉基础追问。",
            "cards": JAVA_CARDS,
        },
        {
            "id": "go",
            "title": "Go",
            "blurb": "调度、channel、错误和进程内合并请求。适合高连接数的位置网关。",
            "cards": GO_CARDS,
        },
        {
            "id": "python",
            "title": "Python",
            "blurb": "把 Python 放在合适的层：编排、离线和模型。热路径的阻塞调用要主动讲。",
            "cards": PYTHON_CARDS,
        },
        {
            "id": "android",
            "title": "Android",
            "blurb": "权限、功耗、坐标系和系统围栏上限。不讲绕过后台限制的做法。",
            "cards": ANDROID_CARDS,
        },
        {
            "id": "backend",
            "title": "后台开发",
            "blurb": "容量、Redis GEO、分片热点、轨迹管道和幂等。",
            "cards": BACKEND_CARDS,
        },
        {
            "id": "rec",
            "title": "推荐算法",
            "blurb": "本地生活的目标、距离约束、召回顺序、偏差和实验溢出。",
            "cards": REC_CARDS,
        },
        {
            "id": "agent",
            "title": "Agent 开发",
            "blurb": "工具协议、坐标系、回链校验和下单确认。提示词不是校验器。",
            "cards": AGENT_CARDS,
        },
    ]

    site = {
        "home": HOME,
        "plan": PLAN,
        "project": PROJECT,
        "tracks": tracks,
        "problems": problems,
        "designs": DESIGNS,
        "quiz": QUIZ,
    }
    out = ROOT / "public/js/data.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(site, ensure_ascii=False, separators=(",", ":"))
    out.write_text("window.SITE = " + payload + ";\n", encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes), problems={len(problems)}, quiz={len(QUIZ)}")


if __name__ == "__main__":
    main()
