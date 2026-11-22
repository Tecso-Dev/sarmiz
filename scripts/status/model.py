"""The status model: pure functions that turn raw GitHub data into what the page, the pinned issue and the
Telegram messages show. No network and no file access in this file, so all of it is unit-tested
(tests/test_model.py)."""
from __future__ import annotations

import datetime as dt
import re
from zoneinfo import ZoneInfo

TASK_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-[A-Z]+-\d+\b")  # W1-ORD-1, W6-ALL-6, W0-M-1
TASK_PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]*-[A-Z]+-\d+:\s*")
CLOSES_RE = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.I)
ROLE_ORDER = {"orders": 0, "menu": 1, "web": 2, "": 3}
DECISIONS = ("APPROVED", "CHANGES_REQUESTED")


# ---------------------------------------------------------------- small helpers

def parse_ts(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def utc_iso(moment: dt.datetime) -> str:
    return moment.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local_today(now: dt.datetime, cfg) -> dt.date:
    return now.astimezone(ZoneInfo(cfg["timezone"])).date()


def natural_key(text: str):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text or "")]


def week_start(cfg, n: int) -> dt.date:
    return dt.date.fromisoformat(cfg["week1_start"]) + dt.timedelta(days=7 * (n - 1))


def week_end(cfg, n: int) -> dt.date:
    return week_start(cfg, n) + dt.timedelta(days=cfg["working_days"] - 1)


def level_now(cfg, today: dt.date) -> dict:
    """Which week and day the project is in. Week 0 means the project has not started yet."""
    last = max(w["n"] for w in cfg["weeks"])
    first = week_start(cfg, 1)
    if today < first:
        return {"week": 0, "day": 0, "weekend": False, "phase": "before"}
    index = (today - first).days // 7 + 1
    if index > last:
        return {"week": last, "day": cfg["working_days"], "weekend": False, "phase": "after"}
    day = (today - week_start(cfg, index)).days + 1  # 1..7, Saturday = 1
    return {"week": index, "day": min(day, cfg["working_days"]), "weekend": day > cfg["working_days"], "phase": "running"}


# ---------------------------------------------------------------- issues and tasks

def normalize_issue(raw: dict) -> dict:
    labels = [l["name"] for l in raw.get("labels", [])]
    milestone = (raw.get("milestone") or {}).get("title") or ""
    wk = re.match(r"Week (\d+)", milestone)
    closed = (raw.get("state") or "").upper() == "CLOSED"
    reason = (raw.get("stateReason") or "").upper()
    cut = closed and reason in ("NOT_PLANNED", "DUPLICATE")
    release2 = "release-2" in labels or milestone == "Release 2"
    week = int(wk.group(1)) if wk else None
    match = TASK_ID_RE.match(raw["title"])
    return {
        "number": raw["number"],
        "task_id": match.group(0) if match else "",
        "title": TASK_PREFIX_RE.sub("", raw["title"]),
        "url": raw.get("url", ""),
        "state": "closed" if closed else "open",
        "cut": cut,
        "release2": release2,
        "week": week,
        "role": next((l.split(":", 1)[1] for l in labels if l.startswith("role:")), ""),
        "owners": [a["login"] for a in raw.get("assignees", [])],
        "mentor_review": "mentor-review" in labels,
        "planned": (not cut) and (not release2) and week is not None,
        "done": closed and not cut,
        "status": "done" if (closed and not cut) else "open",
    }


# ---------------------------------------------------------------- pull requests

def normalize_pr(raw: dict, cfg: dict, now: dt.datetime) -> dict:
    mentor = cfg["mentor"]
    author = (raw.get("author") or {}).get("login", "")
    state = (raw.get("state") or "").lower()
    commits = sorted(parse_ts(c["committedDate"]) for c in raw.get("commits", []) if c.get("committedDate"))
    reviews = sorted(
        ({"login": (r.get("author") or {}).get("login", ""), "state": (r.get("state") or "").upper(), "at": parse_ts(r.get("submittedAt"))}
         for r in raw.get("reviews", []) if r.get("submittedAt")),
        key=lambda r: r["at"])
    decisions = {}
    for r in reviews:
        if r["state"] in DECISIONS or r["state"] == "DISMISSED":
            decisions[r["login"]] = (r["state"], r["at"])
    requested = [x.get("login") or x.get("slug") or x.get("name") or "" for x in raw.get("reviewRequests", [])]
    mentor_state, mentor_at = decisions.get(mentor, ("", None))
    if mentor_state == "DISMISSED":
        mentor_state, mentor_at = "", None
    pushed_after = bool(mentor_at) and any(c > mentor_at for c in commits)
    mentor_waiting = mentor in requested
    draft = bool(raw.get("isDraft"))

    if state == "merged":
        status = "merged"
    elif state == "closed":
        status = "closed"
    elif draft:
        status = "draft"
    elif mentor_state == "APPROVED" and not pushed_after and not mentor_waiting:
        status = "approved"
    elif mentor_state == "CHANGES_REQUESTED" and not pushed_after and not mentor_waiting:
        status = "needs_author"
    else:
        status = "needs_mentor"

    created = parse_ts(raw.get("createdAt"))
    additions, deletions = raw.get("additions", 0) or 0, raw.get("deletions", 0) or 0
    return {
        "number": raw["number"],
        "title": raw.get("title", ""),
        "url": raw.get("url", ""),
        "author": author,
        "state": state,
        "draft": draft,
        "status": status,
        "branch": raw.get("headRefName", ""),
        "body": raw.get("body") or "",
        "created_at": utc_iso(created) if created else "",
        "updated_at": raw.get("updatedAt") or "",
        "merged_at": raw.get("mergedAt") or "",
        "closed_at": raw.get("closedAt") or "",
        "merged_by": (raw.get("mergedBy") or {}).get("login", ""),
        "age_days": max(0, (now - created).days) if created else 0,
        "additions": additions,
        "deletions": deletions,
        "lines": additions + deletions,
        "big": additions + deletions > cfg["size_limit_lines"],
        "files": raw.get("changedFiles", 0) or 0,
        "requested": requested,
        "mentor_state": mentor_state.lower(),
        "teammate": [{"login": login, "state": st.lower()} for login, (st, _) in decisions.items()
                     if login not in (mentor, author) and st in DECISIONS],
        "labels": [l["name"] for l in raw.get("labels", [])],
        "reviews": [{"login": r["login"], "state": r["state"].lower(), "at": utc_iso(r["at"])}
                    for r in reviews if r["state"] in DECISIONS + ("COMMENTED",)],
        "tasks": [],
    }


def link_prs(tasks: list, prs: list) -> None:
    """Attach pull requests to tasks (by task id in the branch, title or body, or by 'Closes #N') and set task status."""
    by_id = {t["task_id"]: t for t in tasks if t["task_id"]}
    by_number = {t["number"]: t for t in tasks}
    for pr in prs:
        text = " ".join([pr["title"], pr["branch"], pr["body"]])
        found = {by_id[i]["number"] for i in TASK_ID_RE.findall(text) if i in by_id}
        found |= {int(n) for n in CLOSES_RE.findall(text) if int(n) in by_number}
        pr["tasks"] = sorted(found)
    for task in tasks:
        open_prs = [p for p in prs if p["state"] == "open" and task["number"] in p["tasks"]]
        task["prs"] = [p["number"] for p in open_prs]
        if task["done"]:
            task["status"] = "done"
        elif any(p["status"] in ("needs_mentor", "approved") for p in open_prs):
            task["status"] = "review"      # a pull request is waiting for the mentor (or approved)
        elif open_prs:
            task["status"] = "started"     # a draft, or the author still has changes to make
        else:
            task["status"] = "open"


def review_log(prs: list, limit: int) -> list:
    rows = []
    for pr in prs:
        for r in pr["reviews"]:
            rows.append({"at": r["at"], "pr": pr["number"], "title": pr["title"], "url": pr["url"],
                         "reviewer": r["login"], "state": r["state"]})
    rows.sort(key=lambda r: r["at"], reverse=True)
    return rows[:limit]


# ---------------------------------------------------------------- weeks, people, summary

def weekly_reviews(parsed_toml: dict) -> dict:
    """Weekly review file (docs/status/reviews.toml) as {week: {...}} with criteria counts."""
    out = {}
    for week in (parsed_toml or {}).get("week", []):
        criteria = [{"fa": c.get("fa", ""), "en": c.get("en", ""), "status": c.get("status", "pending")}
                    for c in week.get("criteria", [])]
        out[int(week["n"])] = {
            "date": week.get("date", ""),
            "decision": week.get("decision", "pending"),
            "note_fa": week.get("note_fa", ""),
            "note_en": week.get("note_en", ""),
            "criteria": criteria,
            "met": sum(1 for c in criteria if c["status"] == "met"),
            "total": len(criteria),
        }
    return out


def build_milestones(cfg, tasks, milestones_raw, weekly, today, level) -> list:
    rows = []
    for w in cfg["weeks"]:
        n = w["n"]
        mine = [t for t in tasks if t["week"] == n and t["planned"]]
        planned, done = len(mine), sum(1 for t in mine if t["done"])
        in_review = sum(1 for t in mine if t["status"] == "review")
        raw = next((m for m in milestones_raw if re.match(rf"Week {n}\b", m.get("title", ""))), {})
        # Without a GitHub due date: a week ends on its last working day; week 0 ends the day before week 1 starts.
        fallback = week_end(cfg, n) if n >= 1 else week_start(cfg, 1) - dt.timedelta(days=1)
        due = (raw.get("due_on") or "")[:10] or fallback.isoformat()
        start = week_start(cfg, n).isoformat() if n >= 1 else ""
        if planned and done == planned:
            state = "done"
        elif n == level["week"] and level["phase"] != "before":
            state = "current"
        elif due and dt.date.fromisoformat(due) < today:
            state = "overdue"
        else:
            state = "upcoming"
        rows.append({
            "n": n, "fa": w["fa"], "en": w["en"], "goal_fa": w["goal_fa"], "goal_en": w["goal_en"],
            "start": start, "due": due, "planned": planned, "done": done, "in_review": in_review,
            "open": planned - done, "state": state,
            "url": f"https://github.com/{cfg['repo']}/milestone/{raw['number']}" if raw.get("number") else "",
            "review": weekly.get(n, {"date": "", "decision": "pending", "note_fa": "", "note_en": "", "criteria": [], "met": 0, "total": 0}),
        })
    return rows


def build_people(cfg, tasks, prs, roles_from_team) -> list:
    people = []
    for login in cfg["students"]:
        mine = [t for t in tasks if t["planned"] and login in t["owners"]]
        role = roles_from_team.get(login, "")
        if not role and mine:
            counts = {}
            for t in mine:
                if t["role"]:
                    counts[t["role"]] = counts.get(t["role"], 0) + 1
            role = max(counts, key=counts.get) if counts else ""
        authored = [p for p in prs if p["author"] == login]
        people.append({
            "login": login, "role": role,
            "tasks_open": sum(1 for t in mine if not t["done"]),
            "tasks_done": sum(1 for t in mine if t["done"]),
            "tasks": [{"number": t["number"], "task_id": t["task_id"], "title": t["title"], "url": t["url"], "status": t["status"]} for t in mine],
            "prs_open": sum(1 for p in authored if p["state"] == "open"),
            "prs_merged": sum(1 for p in authored if p["state"] == "merged"),
        })
    return people


def build_status(raw: dict, cfg: dict, now: dt.datetime) -> dict:
    today = local_today(now, cfg)
    level = level_now(cfg, today)
    tasks = [normalize_issue(i) for i in raw["issues"]]
    prs = [normalize_pr(p, cfg, now) for p in raw["prs"]]
    link_prs(tasks, prs)
    weekly = weekly_reviews(raw.get("reviews_toml"))
    milestones = build_milestones(cfg, tasks, raw.get("milestones", []), weekly, today, level)

    planned = [t for t in tasks if t["planned"]]
    done = sum(1 for t in planned if t["done"])
    current = next((m for m in milestones if m["n"] == level["week"]), milestones[0])

    groups = []
    week_tasks = sorted((t for t in planned if t["week"] == level["week"]),
                        key=lambda t: (ROLE_ORDER.get(t["role"], 9), natural_key(t["task_id"])))
    for role in ("orders", "menu", "web", ""):
        items = [t for t in week_tasks if t["role"] == role]
        if items:
            groups.append({"role": role, "tasks": items})

    open_prs = sorted((p for p in prs if p["state"] == "open"), key=lambda p: p["number"])
    merged = sorted((p for p in prs if p["state"] == "merged"), key=lambda p: p["merged_at"], reverse=True)

    return {
        "generated_at": utc_iso(now),
        "today": today.isoformat(),
        "repo": cfg["repo"],
        "pages_url": cfg["pages_url"],
        "stale_after_hours": cfg["stale_after_hours"],
        "level": {**level, "name_fa": current["fa"], "name_en": current["en"], "goal_fa": current["goal_fa"],
                  "goal_en": current["goal_en"], "planned": len(planned), "done": done,
                  "percent": int(done * 100 / len(planned)) if planned else 0,
                  "weeks": max(w["n"] for w in cfg["weeks"]), "working_days": cfg["working_days"]},
        "milestones": milestones,
        "this_week": {"week": level["week"], "groups": groups,
                      "done": sum(1 for t in week_tasks if t["done"]), "total": len(week_tasks)},
        "prs": {"open": open_prs, "merged": merged[:cfg["recent_merged"]]},
        "reviews": review_log(prs, cfg["review_log_size"]),
        "people": build_people(cfg, tasks, prs, raw.get("roles", {})),
        "main_health": raw.get("main_health"),
        "all_prs": prs,
    }


# ---------------------------------------------------------------- snapshot and events (Telegram)

def snapshot(status: dict) -> dict:
    """What we remember between runs, to tell what is new."""
    prs = {}
    for p in status["all_prs"]:
        prs[str(p["number"])] = {
            "state": p["state"], "title": p["title"], "url": p["url"], "author": p["author"],
            "requested": p["requested"],
            "reviews": [f"{r['login']}|{r['state'].upper()}|{r['at']}" for r in p["reviews"]],
        }
    return {"generated_at": status["generated_at"], "prs": prs}


def diff_events(prev, cur) -> list:
    """Events since the previous snapshot. With no previous snapshot nothing is announced (first run)."""
    if not prev:
        return []
    events = []
    old_prs = prev.get("prs", {})
    for number in sorted(cur["prs"], key=int):
        c, p = cur["prs"][number], old_prs.get(number)
        base = {"number": int(number), "title": c["title"], "url": c["url"]}
        if p is None:
            if c["state"] == "open":
                events.append({**base, "kind": "pr_opened", "actor": c["author"], "requested": c["requested"]})
            continue
        for entry in c["reviews"]:
            if entry in p["reviews"]:
                continue
            login, state, _ = entry.split("|")
            if state in DECISIONS:
                events.append({**base, "kind": "approved" if state == "APPROVED" else "changes_requested", "actor": login})
        if c["state"] == "open":
            for login in c["requested"]:
                if login not in p["requested"]:
                    events.append({**base, "kind": "review_requested", "actor": login})
        if p["state"] == "open" and c["state"] == "merged":
            events.append({**base, "kind": "merged", "actor": c["author"]})
        elif p["state"] == "open" and c["state"] == "closed":
            events.append({**base, "kind": "closed", "actor": c["author"]})
    return events
