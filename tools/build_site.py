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
from tracks_more import BACKEND_MORE, ES_CARDS, GO_MORE, MYSQL_CARDS, REDIS_CARDS  # noqa: E402
from tracks_lbs import LBS_CARDS  # noqa: E402
from tracks_resume import RESUME_CARDS  # noqa: E402
from tracks_hot import HOT_CARDS  # noqa: E402
from tracks_system import AGENT_CARDS, BACKEND_CARDS, DESIGNS, REC_CARDS  # noqa: E402
from primers import PRIMERS  # noqa: E402
from walks_lbs import LBS_WALKS  # noqa: E402
from walks_resume import RESUME_WALKS  # noqa: E402
from walks_more import MORE_WALKS  # noqa: E402
from walks_rest import REST_WALKS  # noqa: E402


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

    walks = {**LBS_WALKS, **REST_WALKS, **MORE_WALKS, **RESUME_WALKS}

    def with_walks(track_id, cards):
        attached = []
        for card in cards:
            key = f"{track_id}/{card['id']}"
            if key not in walks:
                raise SystemExit(f"missing code walkthrough for {key}")
            item = dict(card)
            item["walks"] = walks[key]
            attached.append(item)
        return attached

    def with_primer(track_id, cards):
        attached = []
        for card in cards:
            key = f"{track_id}/{card['id']}"
            primer = PRIMERS.get(key)
            if not primer:
                raise SystemExit(f"missing primer for {key}")
            context = (primer.get("context") or "").strip()
            principle = (primer.get("principle") or "").strip()
            focus = primer.get("focus") or []
            if len(context) < 80 or len(principle) < 160 or len(focus) < 4:
                raise SystemExit(f"primer too thin for {key}")
            item = dict(card)
            item["primer"] = {"context": context, "principle": principle, "focus": list(focus)}
            attached.append(item)
        return attached

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
            "id": "resume",
            "title": "简历追问",
            "blurb": "按简历里的项目准备追问：猜你想去、酒店排序与补贴、Agent、网关加密、车机地图和全景。数字先对口径。",
            "cards": with_primer("resume", with_walks("resume", RESUME_CARDS)),
        },
        {
            "id": "lbs",
            "title": "LBS 领域",
            "blurb": "坐标系、索引、轨迹、围栏、路径。每张卡片都按执行顺序把代码拆开讲。",
            "cards": with_primer("lbs", with_walks("lbs", LBS_CARDS)),
        },
        {
            "id": "hot",
            "title": "高频追问",
            "blurb": "3-1、3-2 会从面经里的这些点追到实现和取舍：MySQL、Redis、Kafka、限流、一致性、网络。",
            "cards": with_primer("hot", with_walks("hot", HOT_CARDS)),
        },
        {
            "id": "java",
            "title": "Java",
            "blurb": "并发、JVM 和事务。地理服务只是这些基础题的场景，不会替你挡掉基础追问。",
            "cards": with_primer("java", with_walks("java", JAVA_CARDS)),
        },
        {
            "id": "go",
            "title": "Go",
            "blurb": "调度、channel、错误、退出和超时。位置网关用有界队列，不靠无界 goroutine。",
            "cards": with_primer("go", with_walks("go", GO_CARDS + GO_MORE)),
        },
        {
            "id": "python",
            "title": "Python",
            "blurb": "把 Python 放在合适的层：编排、离线和模型。热路径的阻塞调用要主动讲。",
            "cards": with_primer("python", with_walks("python", PYTHON_CARDS)),
        },
        {
            "id": "android",
            "title": "Android",
            "blurb": "权限、功耗、坐标系和系统围栏上限。不讲绕过后台限制的做法。",
            "cards": with_primer("android", with_walks("android", ANDROID_CARDS)),
        },
        {
            "id": "backend",
            "title": "后台开发",
            "blurb": "容量、分片、超时预算、发件箱、背压和降级。",
            "cards": with_primer("backend", with_walks("backend", BACKEND_CARDS + BACKEND_MORE)),
        },
        {
            "id": "mysql",
            "title": "MySQL",
            "blurb": "执行计划、覆盖索引、间隙锁、死锁、主从延迟、binlog 和版本更新。",
            "cards": with_primer("mysql", with_walks("mysql", MYSQL_CARDS)),
        },
        {
            "id": "redis",
            "title": "Redis",
            "blurb": "大 key、穿透击穿、管道和 Lua、淘汰、集群槽位、GEO 误差。",
            "cards": with_primer("redis", with_walks("redis", REDIS_CARDS)),
        },
        {
            "id": "es",
            "title": "Elasticsearch",
            "blurb": "text 与 keyword、倒排、过滤、地理字段、刷新、深分页和批量版本。",
            "cards": with_primer("es", with_walks("es", ES_CARDS)),
        },
        {
            "id": "rec",
            "title": "推荐算法",
            "blurb": "本地生活的目标、距离约束、召回顺序、偏差和实验溢出。",
            "cards": with_primer("rec", with_walks("rec", REC_CARDS)),
        },
        {
            "id": "agent",
            "title": "Agent 开发",
            "blurb": "工具协议、坐标系、回链校验和下单确认。提示词不是校验器。",
            "cards": with_primer("agent", with_walks("agent", AGENT_CARDS)),
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
