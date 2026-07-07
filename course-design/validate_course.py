#!/usr/bin/env python3
"""Validate course numbering, mappings, Markdown structure and generated XMind files."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COURSE_DESIGN = ROOT / "course-design"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_labs() -> None:
    numbers = []
    for path in (ROOT / "labs").glob("lab*.md"):
        match = re.match(r"lab(\d+)", path.name)
        require(match is not None, f"Invalid lab filename: {path}")
        numbers.append(int(match.group(1)))
    require(sorted(numbers) == list(range(1, 64)), "Labs must be continuous from Lab01 to Lab63")


def validate_units() -> None:
    index = (COURSE_DESIGN / "01-unit-index.md").read_text(encoding="utf-8")
    schedule_path = next(COURSE_DESIGN.glob("04-18*.md"))
    schedule = schedule_path.read_text(encoding="utf-8")

    index_units = sorted(map(int, re.findall(r"^\| U(\d{2}) \|", index, re.M)))
    schedule_units = sorted(map(int, re.findall(r"^\| .*?\| U(\d{2}) \|", schedule, re.M)))
    require(index_units == list(range(1, 73)), "Unit index must contain U01-U72 exactly once")
    require(schedule_units == list(range(1, 73)), "Schedule must contain U01-U72 exactly once")

    for expected in ("24 | 第1-3周", "24 | 第4-6周", "24 | 第7-9周", "32 | 第10-13周", "40 | 第14-18周"):
        require(expected in index, f"Missing module hour/week mapping: {expected}")


def validate_markdown() -> None:
    for path in ROOT.rglob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        fences = sum(1 for line in lines if line.startswith("```"))
        require(fences % 2 == 0, f"Unbalanced Markdown code fences: {path} ({fences})")


def validate_xmind() -> None:
    overview = next(COURSE_DESIGN.glob("03-xmind-*v3.xmind"))
    modules = sorted((COURSE_DESIGN / "xmind-modules").glob("M*.xmind"))
    require(len(modules) == 5, "Exactly five module XMind files are required")
    for path in [overview, *modules]:
        with zipfile.ZipFile(path) as archive:
            require(archive.testzip() is None, f"Damaged XMind ZIP: {path}")
            content = json.loads(archive.read("content.json"))
            require(content and "rootTopic" in content[0], f"Invalid XMind content: {path}")


def validate_projects() -> None:
    project1 = (ROOT / "projects" / "project01-阶段项目-单机部署.md").read_text(encoding="utf-8")
    project2 = (ROOT / "projects" / "project02-综合项目-学生版.md").read_text(encoding="utf-8")
    require("U33-U36" in project1 and "4次大课" in project1, "Project01 must map to U33-U36")
    require("U69-U72" in project2 and "4次大课" in project2, "Project02 must map to U69-U72")

    starter = ROOT / "projects" / "project02-starter"
    required = [
        "README.md", ".env.example", "compose.yaml",
        "backend/Dockerfile", "backend/app.py", "backend/requirements.txt",
        "frontend/Dockerfile", "frontend/nginx.conf", "frontend/index.html",
        "db/init.sql", "ops/acceptance.sh", "ops/backup.sh", "ops/restore.sh",
    ]
    for relative in required:
        require((starter / relative).is_file(), f"Missing Project02 starter file: {relative}")


def main() -> None:
    validate_labs()
    validate_units()
    validate_markdown()
    validate_xmind()
    validate_projects()
    require(not list(COURSE_DESIGN.glob("*.mm")), "Obsolete FreeMind file should not exist")
    print("COURSE_VALIDATION_OK labs=63 units=72 modules=5 xmind=6 projects=2")


if __name__ == "__main__":
    main()
