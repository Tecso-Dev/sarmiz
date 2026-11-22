"""Things the build does to GitHub and Telegram: PR status labels, the pinned status issue, Telegram messages."""
import html
import json
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

STATUS_LABELS = {"needs_author": "status:needs-author", "needs_mentor": "status:needs-mentor", "approved": "status:approved"}
ALL_STATUS_LABELS = set(STATUS_LABELS.values())
BOARD_LABEL = "status-board"
MAX_MESSAGES = 8


def gh(*args, input_text=None):
    result = subprocess.run(["gh", *args], capture_output=True, text=True, input=input_text)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()[:300]}")
    return result.stdout


# ---------------------------------------------------------------- PR status labels

def label_changes(prs: list) -> list:
    """For each PR: which status label to add and which to remove, so exactly one status label is shown."""
    changes = []
    for pr in prs:
        want = STATUS_LABELS.get(pr["status"]) if pr["state"] == "open" else None
        have = {l for l in pr["labels"] if l in ALL_STATUS_LABELS}
        add = [want] if want and want not in have else []
        remove = sorted(have - ({want} if want else set()))
        if add or remove:
            changes.append({"number": pr["number"], "add": add, "remove": remove})
    return changes


def apply_label_changes(repo: str, changes: list) -> None:
    for c in changes:
        args = ["pr", "edit", str(c["number"]), "--repo", repo]
        for label in c["add"]:
            args += ["--add-label", label]
        for label in c["remove"]:
            args += ["--remove-label", label]
        gh(*args)


# ---------------------------------------------------------------- the pinned status issue

def upsert_status_issue(repo: str, title: str, body: str, digest: str) -> str:
    """Create or update the one open issue that carries the status-board label. Returns what happened."""
    found = json.loads(gh("issue", "list", "--repo", repo, "--label", BOARD_LABEL, "--state", "open",
                          "--json", "number,body") or "[]")
    if not found:
        gh("issue", "create", "--repo", repo, "--title", title, "--body-file", "-", "--label", BOARD_LABEL, input_text=body)
        return "created"
    current = found[0]
    match = re.search(r"status-hash:([0-9a-f]+)", current.get("body") or "")
    if match and match.group(1) == digest:
        return "unchanged"
    gh("issue", "edit", str(current["number"]), "--repo", repo, "--body-file", "-", input_text=body)
    return "updated"


# ---------------------------------------------------------------- Telegram

def esc(text: str) -> str:
    return html.escape(text or "", quote=False)


def format_event(ev: dict) -> str:
    """One short Persian message per event. Names are links to the GitHub profile, never @mentions."""
    def person(login):
        return f'<a href="https://github.com/{esc(login)}">{esc(login)}</a>'
    pr = f'<a href="{esc(ev["url"])}">PR #{ev["number"]}</a>'
    title = esc(ev["title"])
    kind = ev["kind"]
    if kind == "pr_opened":
        asked = "، ".join(person(r) for r in ev.get("requested", []))
        return f"🆕 {pr} باز شد: {title}\nاز {person(ev['actor'])}" + (f" · بازبین: {asked}" if asked else "")
    if kind == "review_requested":
        return f"👀 برای {pr} از {person(ev['actor'])} بازبینی خواسته شد.\n{title}"
    if kind == "approved":
        return f"✅ {pr} تأیید شد ({person(ev['actor'])}).\n{title}"
    if kind == "changes_requested":
        return (f"✋ {pr}: {person(ev['actor'])} تغییر خواسته است.\n{title}\n"
                "موارد را داخل PR ببین و وقتی تمام شد دوباره بازبینی بخواه.")
    if kind == "merged":
        return f"🎉 {pr} merge شد: {title}"
    if kind == "closed":
        return f"🚪 {pr} بدون merge بسته شد: {title}"
    return f"{pr}: {title}"


def send_telegram(events: list, token: str, chat_id: str) -> int:
    """Send the events. Raises on failure so the run is retried next time. The token is never printed."""
    sent = 0
    for ev in events[:MAX_MESSAGES]:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": format_event(ev), "parse_mode": "HTML",
                                       "disable_web_page_preview": "true"}).encode()
        request = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                response.read()
        except urllib.error.HTTPError as err:
            raise RuntimeError(f"Telegram refused the message (HTTP {err.code}).") from None
        except urllib.error.URLError as err:
            raise RuntimeError(f"Could not reach Telegram ({type(err.reason).__name__}).") from None
        sent += 1
    return sent
