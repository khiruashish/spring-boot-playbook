"""Turn surefire XML reports into short, deterministic per-class summaries (no timings), one file per test class."""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

mode = sys.argv[1] if len(sys.argv) > 1 else "write"
out_dir = pathlib.Path("outputs")
out_dir.mkdir(exist_ok=True)
problems = 0
for xml in sorted(pathlib.Path("target/surefire-reports").glob("TEST-*.xml")):
    suite = ET.parse(xml).getroot()
    cls = suite.get("name").rsplit(".", 1)[-1]
    cases = suite.findall("testcase")
    failed = [c for c in cases if c.find("failure") is not None or c.find("error") is not None]
    lines = [f"{cls}: {len(cases)} tests, {len(failed)} failures"]
    for c in sorted(cases, key=lambda c: c.get("name")):
        name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", c.get("name").removesuffix("()")).replace("_", " · ").lower()
        lines.append(("  ✘ " if c in failed else "  ✔ ") + name)
    text = "\n".join(lines) + "\n"
    target = out_dir / f"{cls}.txt"
    if failed:
        problems += 1
    if mode == "--check":
        if not target.exists() or target.read_text() != text:
            print(f"DIFF  {cls}: run ./run-tests.sh and commit outputs/")
            problems += 1
    else:
        target.write_text(text)
    print(("FAIL  " if failed else "PASS  ") + f"{cls} ({len(cases)} tests)")
sys.exit(1 if problems else 0)
