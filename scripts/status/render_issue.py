"""The pinned issue: a short Persian summary (with an English line) that the workflow rewrites when something changes."""
import datetime as dt
import hashlib

from fmt import bar, date_fa, fa_digits, percent

STATUS_FA = {"draft": "پیش‌نویس", "needs_author": "منتظر نویسنده", "needs_mentor": "منتظر منتور", "approved": "تأیید شده"}
TASK_FA = {"done": "✅ انجام شد", "review": "🔎 در بازبینی", "started": "🛠 در دست انجام", "open": "باز"}
DECISION_FA = {"pending": "هنوز بازبینی نشده", "passed": "برقرار", "partly": "نیمه‌برقرار", "failed": "برقرار نیست"}
ROLE_FA = {"web": "فرانت", "menu": "ورود و منو", "orders": "سفارش و زیرساخت", "": "کل تیم"}


def link(text: str, url: str) -> str:
    return f"[{text}]({url})" if url else text


def profile(login: str) -> str:
    # A link to the profile, not an @mention: mentions would notify people on every rewrite.
    return f"[{login}](https://github.com/{login})"


def render_issue(status: dict, cfg: dict):
    lv = status["level"]
    fa = fa_digits
    day = f"روز {fa(lv['day'])} از {fa(lv['working_days'])}" if lv["phase"] == "running" and not lv["weekend"] else (
        "پایان هفته" if lv["weekend"] else "")
    core = ['<div dir="rtl">', "", "## وضعیت پروژه · Project status", ""]
    head = f"**هفته {fa(lv['week'])} از {fa(lv['weeks'])}** — {lv['name_fa']}"
    core += [head + (f" · {day}" if day else ""), ""]
    core += [f"{bar(lv['done'], lv['planned'], 20)}  **{fa(lv['percent'])}٪** — {fa(lv['done'])} از {fa(lv['planned'])} کار انجام شده", ""]
    core += [f"> هدف این هفته: {lv['goal_fa']}", ""]

    core += ["### همه‌ی مرحله‌ها", "", "| مرحله | موعد | کارها | بازبینی هفتگی |", "|---|---|---|---|"]
    for m in status["milestones"]:
        name = f"Week {m['n']} · {m['fa']}"
        due = date_fa(dt.date.fromisoformat(m["due"])) if m["due"] else "—"
        tasks = f"{bar(m['done'], m['planned'])} {fa(m['done'])}/{fa(m['planned'])}"
        r = m["review"]
        review = f"{fa(r['met'])} از {fa(r['total'])} معیار" if r["total"] and r["decision"] != "pending" else DECISION_FA["pending"]
        if r["decision"] != "pending" and r["decision"] in DECISION_FA:
            review += f" ({DECISION_FA[r['decision']]})"
        core.append(f"| {link(name, m['url'])} | {due} | {tasks} | {review} |")
    core.append("")

    core += [f"### کارهای این هفته ({fa(status['this_week']['done'])} از {fa(status['this_week']['total'])} انجام شده)", ""]
    if not status["this_week"]["groups"]:
        core += ["هنوز کاری برای این هفته نیست.", ""]
    for group in status["this_week"]["groups"]:
        core.append(f"**{ROLE_FA.get(group['role'], group['role'])}**")
        core.append("")
        for t in group["tasks"]:
            owner = "، ".join(profile(o) for o in t["owners"]) if t["owners"] else "هنوز صاحب ندارد"
            extra = " · نیاز به بازبینی منتور" if t["mentor_review"] and not t["done"] else ""
            mark = "x" if t["done"] else " "
            core.append(f"- [{mark}] {link(t['task_id'] or '#' + str(t['number']), t['url'])} {t['title']} — {owner} · {TASK_FA[t['status']]}{extra}")
        core.append("")

    core += ["### درخواست‌های باز (PR)", ""]
    if not status["prs"]["open"]:
        core += ["الان PR بازی نیست.", ""]
    else:
        core += ["| PR | وضعیت | نویسنده | سن | اندازه |", "|---|---|---|---|---|"]
        for p in status["prs"]["open"]:
            big = " ⚠ بزرگ" if p["big"] else ""
            core.append(f"| {link('#' + str(p['number']), p['url'])} {p['title']} | {STATUS_FA.get(p['status'], p['status'])} | {profile(p['author'])} | "
                        f"{fa(p['age_days'])} روز | +{fa(p['additions'])} −{fa(p['deletions'])}{big} |")
        core.append("")

    en = (f"**English:** week {lv['week']} of {lv['weeks']} ({lv['name_en']}). {lv['done']} of {lv['planned']} planned tasks are done "
          f"({lv['percent']}%). Full status page: {status['pages_url']}")
    core += ["</div>", "", en]
    text = "\n".join(core)
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    stamp = status["generated_at"]
    body = f"<!-- status-hash:{digest} -->\n{text}\n\n<sub>Updated automatically when something changes · last change {stamp} · scripts/status</sub>\n"
    return "وضعیت پروژه · Project status", body, digest
