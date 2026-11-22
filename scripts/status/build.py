#!/usr/bin/env python3
"""Builds the project status page and, when asked, updates GitHub and Telegram.

  build.py build --out site                       build the page into ./site (no side effects; good for local checks)
  build.py build --out site --prev prev.json --snapshot snapshot.json --events events.json --labels --issue
                                                  what the GitHub Actions workflow runs
  build.py notify --events events.json            send the events to Telegram (needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

It reads GitHub with the gh CLI, so it needs `gh` signed in locally (or GH_TOKEN in Actions).
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import shutil
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import actions  # noqa: E402
import collect  # noqa: E402
import model  # noqa: E402
import render_issue  # noqa: E402
import render_site  # noqa: E402


def load_config() -> dict:
    return tomllib.loads((HERE / "config.toml").read_text(encoding="utf-8"))


def public_json(status: dict) -> dict:
    """The data published as status.json: everything public, without pull request bodies."""
    clean = json.loads(json.dumps(status))
    clean.pop("all_prs", None)
    for group in ("open", "merged"):
        for pr in clean["prs"][group]:
            pr.pop("body", None)
    return clean


def cmd_build(args) -> int:
    cfg = load_config()
    now = dt.datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else dt.datetime.now(dt.timezone.utc)
    status = model.build_status(collect.collect(cfg), cfg, now)

    out = pathlib.Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    (out / "fonts").mkdir(parents=True)
    for font in (HERE / "assets" / "fonts").iterdir():
        shutil.copy(font, out / "fonts" / font.name)
    (out / "index.html").write_text(render_site.render_page(status, cfg), encoding="utf-8")
    (out / "status.json").write_text(json.dumps(public_json(status), ensure_ascii=False, indent=1), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")

    snap = model.snapshot(status)
    prev = json.loads(pathlib.Path(args.prev).read_text(encoding="utf-8")) if args.prev and pathlib.Path(args.prev).exists() else None
    events = model.diff_events(prev, snap)
    if args.snapshot:
        pathlib.Path(args.snapshot).write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.events:
        pathlib.Path(args.events).write_text(json.dumps(events, ensure_ascii=False), encoding="utf-8")

    lv = status["level"]
    print(f"built {out}/index.html: week {lv['week']} day {lv['day']}, {lv['done']}/{lv['planned']} planned tasks done ({lv['percent']}%), "
          f"{len(status['prs']['open'])} open PRs, {len(events)} new events"
          + (" (first run: nothing announced)" if prev is None else ""))

    if args.labels:
        changes = actions.label_changes(status["all_prs"])
        actions.apply_label_changes(cfg["repo"], changes)
        print(f"PR status labels: {len(changes)} change(s) {changes if changes else ''}")
    if args.issue:
        title, body, digest = render_issue.render_issue(status, cfg)
        print("status issue:", actions.upsert_status_issue(cfg["repo"], title, body, digest))
    return 0


def cmd_notify(args) -> int:
    events = json.loads(pathlib.Path(args.events).read_text(encoding="utf-8")) if pathlib.Path(args.events).exists() else []
    if not events:
        print("no new events to announce")
        return 0
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN", ""), os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        print(f"{len(events)} event(s) not sent: Telegram is not configured (no secrets); they are marked as seen")
        return 0
    sent = actions.send_telegram(events, token, chat)
    print(f"sent {sent} Telegram message(s)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", default="site")
    b.add_argument("--prev", help="previous snapshot.json, to tell what is new")
    b.add_argument("--snapshot", help="write the new snapshot here")
    b.add_argument("--events", help="write the new events here")
    b.add_argument("--labels", action="store_true", help="set PR status labels on GitHub")
    b.add_argument("--issue", action="store_true", help="create or update the pinned status issue")
    b.add_argument("--now", help="pretend it is this UTC time (for testing)")
    n = sub.add_parser("notify")
    n.add_argument("--events", required=True)
    args = parser.parse_args(argv)
    return cmd_build(args) if args.cmd == "build" else cmd_notify(args)


if __name__ == "__main__":
    sys.exit(main())
