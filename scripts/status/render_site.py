"""The status page: one self-contained HTML file (inline CSS and JS, no external requests), Persian and English."""
import datetime as dt
import html
from zoneinfo import ZoneInfo

from fmt import date_en, date_fa, fa_digits

CSS = """
@font-face{font-family:"Vazirmatn";src:url("fonts/Vazirmatn-Regular.woff2") format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Vazirmatn";src:url("fonts/Vazirmatn-Bold.woff2") format("woff2");font-weight:700;font-display:swap}
:root{--bg:#FBF6EC;--surface:#F4ECDD;--raise:#FFFDF8;--fg:#2B1D14;--muted:#6B5646;--line:#E4D8C3;--accent:#E8A013;--accent-ink:#8A5A00;
--ok:#2F6B3A;--ok-bg:#E3EFDF;--warn:#8A5A00;--warn-bg:#F6EBD3;--bad:#9A3B2E;--bad-bg:#F6E1DC;--info:#2D5A7A;--info-bg:#E0EAF1;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#18110C;--surface:#22180F;--raise:#2A1E14;--fg:#F3EBDD;--muted:#BBA791;--line:#3B2D21;--accent:#E8A013;--accent-ink:#F2BC4B;
--ok:#8CCB97;--ok-bg:#1F3323;--warn:#F2BC4B;--warn-bg:#3A2D12;--bad:#EE9A8B;--bad-bg:#3A1F1A;--info:#9CC3E0;--info-bg:#1A2A36;color-scheme:dark}}
*{box-sizing:border-box}
html[data-lang="fa"] .en{display:none}html[data-lang="en"] .fa{display:none}
body{margin:0;background:var(--bg);color:var(--fg);font-family:"Vazirmatn",Tahoma,"Segoe UI",system-ui,sans-serif;font-size:16px;line-height:1.7;
padding-inline:max(16px,env(safe-area-inset-left,0px)) max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}
.wrap{max-width:1080px;margin-inline:auto;display:grid;gap:44px;min-width:0}
a{color:var(--accent-ink);text-underline-offset:3px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:4px}
h1,h2,h3,p{margin:0}h1{font-size:clamp(1.9rem,5vw,2.7rem);line-height:1.25;font-weight:700;text-wrap:balance}
h2{font-size:1.4rem;font-weight:700;text-wrap:balance}h3{font-size:1.05rem;font-weight:700}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-block:18px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.mark{font-weight:700;font-size:1.35rem;letter-spacing:-.01em}.mark small{font-weight:400;color:var(--muted);font-size:.8rem;margin-inline-start:.5rem;letter-spacing:.14em;text-transform:uppercase}
.lang{display:flex;gap:6px}.lang button{font:inherit;font-size:.9rem;color:var(--fg);background:var(--raise);border:1px solid var(--line);border-radius:999px;padding:.2rem .9rem;cursor:pointer}
.lang button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#2B1D14;font-weight:700}
.hero{display:grid;gap:18px}.lede{font-size:1.2rem;max-width:62ch}.lede b{font-variant-numeric:tabular-nums}
.updated{font-size:.88rem;color:var(--muted)}
.meter{height:.9rem;border-radius:999px;background:var(--line);overflow:hidden}.meter i{display:block;height:100%;background:var(--accent);border-radius:999px}
.big{display:flex;align-items:baseline;gap:.7rem;flex-wrap:wrap}.big .n{font-size:3.2rem;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}
.track{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.seg{background:var(--raise);border:1px solid var(--line);border-radius:12px;padding:10px 12px;display:grid;gap:6px;min-width:0}
.seg[data-state="current"]{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent) inset}
.seg .t{display:flex;justify-content:space-between;gap:8px;font-size:.92rem}.seg .t b{font-weight:700}
.seg .c{font-size:.82rem;color:var(--muted);font-variant-numeric:tabular-nums}
.sec{display:grid;gap:14px;min-width:0}.note{font-size:.9rem;color:var(--muted);max-width:70ch}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.card{background:var(--raise);border:1px solid var(--line);border-radius:14px;padding:16px;display:grid;gap:8px;align-content:start;min-width:0}
.card header{display:flex;justify-content:space-between;align-items:start;gap:8px}
.card .dates,.card .nums,.card .rev{font-size:.88rem;color:var(--muted)}.goal{font-size:.92rem}
.chip{display:inline-block;padding:.05rem .65rem;border-radius:999px;font-size:.8rem;line-height:1.6;border:1px solid var(--line);white-space:nowrap;background:var(--surface);color:var(--muted)}
.chip-ok{background:var(--ok-bg);color:var(--ok);border-color:transparent}.chip-warn{background:var(--warn-bg);color:var(--warn);border-color:transparent}
.chip-bad{background:var(--bad-bg);color:var(--bad);border-color:transparent}.chip-info{background:var(--info-bg);color:var(--info);border-color:transparent}
.chip-accent{background:var(--accent);color:#2B1D14;border-color:transparent;font-weight:700}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--raise)}
table{width:100%;border-collapse:collapse;font-size:.95rem}th,td{padding:.55rem .75rem;text-align:start;vertical-align:top;border-bottom:1px solid var(--line)}
th{font-size:.8rem;color:var(--muted);font-weight:400;white-space:nowrap;background:var(--surface)}tr:last-child td{border-bottom:0}
.num{font-variant-numeric:tabular-nums;white-space:nowrap}.muted{color:var(--muted)}.ltr{direction:ltr;unicode-bidi:isolate;display:inline-block}
.role{font-weight:700;margin-top:6px}
details.wk{background:var(--raise);border:1px solid var(--line);border-radius:12px;padding:10px 14px}
details.wk summary{cursor:pointer;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.crit{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:6px}.crit li{display:flex;gap:10px;align-items:start}.crit .i{width:1.4rem;text-align:center;font-weight:700}
.i-met{color:var(--ok)}.i-not_met{color:var(--bad)}.i-pending{color:var(--muted)}
.people{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.tl{list-style:none;margin:0;padding:0;display:grid;gap:4px;font-size:.9rem}.tl li{display:flex;gap:8px;align-items:baseline}
.foot{font-size:.9rem;color:var(--muted);display:grid;gap:8px;border-top:1px solid var(--line);padding-top:18px}
.foot ul{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:6px 18px}
@media (max-width:680px){
table.stack thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
table.stack,table.stack tbody,table.stack tr,table.stack td{display:block;width:100%}
table.stack tr{padding:.65rem .8rem;border-bottom:1px solid var(--line)}table.stack tr:last-child{border-bottom:0}
table.stack td{border:0;padding:.12rem 0;display:flex;gap:.7rem;align-items:baseline;white-space:normal;min-width:0}
table.stack td>*{min-width:0}
table.stack td::before{content:attr(data-fa);color:var(--muted);font-size:.78rem;min-width:7.2rem;flex:none}
html[data-lang="en"] table.stack td::before{content:attr(data-en)}
}
.sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
@media (prefers-reduced-motion:no-preference){.meter i{transition:width .6s ease}}
"""

JS = """
(function(){
var root=document.documentElement,KEY='sarmiz-status-lang';
function toFa(n){return String(n).replace(/\\d/g,function(c){return '۰۱۲۳۴۵۶۷۸۹'[c]})}
function setLang(l){root.setAttribute('data-lang',l);root.lang=l;root.dir=l==='fa'?'rtl':'ltr';
try{localStorage.setItem(KEY,l)}catch(e){}
document.querySelectorAll('[data-set-lang]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.setLang===l))})}
var saved=null;try{saved=localStorage.getItem(KEY)}catch(e){}
setLang(saved==='en'?'en':'fa');
document.querySelectorAll('[data-set-lang]').forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.setLang)})});
function rel(ms,lang){var m=Math.round(ms/60000);
if(m<1)return lang==='fa'?'همین الان':'just now';
if(m<60)return lang==='fa'?toFa(m)+' دقیقه پیش':m+' min ago';
var h=Math.round(m/60);if(h<48)return lang==='fa'?toFa(h)+' ساعت پیش':h+' h ago';
var d=Math.round(h/24);return lang==='fa'?toFa(d)+' روز پیش':d+' days ago'}
document.querySelectorAll('[data-ts]').forEach(function(el){var ms=Date.now()-Date.parse(el.dataset.ts);
var fa=el.querySelector('.fa'),en=el.querySelector('.en');if(fa)fa.textContent=rel(ms,'fa');if(en)en.textContent=rel(ms,'en')});
var gen=Date.parse(root.dataset.generated),lim=Number(root.dataset.staleHours)*3600000,s=document.getElementById('stale');
if(gen&&lim&&Date.now()-gen>lim&&s)s.hidden=false;
})();
"""


def E(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def b(fa: str, en: str) -> str:
    """A Persian and an English version of the same text; CSS shows the one for the chosen language."""
    return f'<span class="fa" lang="fa">{fa}</span><span class="en" lang="en">{en}</span>'


def num(value) -> str:
    return b(fa_digits(value), E(value))


def day(iso: str) -> str:
    d = dt.date.fromisoformat(iso[:10])
    return b(date_fa(d), date_en(d))


def clock(iso_utc: str, tz: str) -> str:
    t = dt.datetime.fromisoformat(iso_utc.replace("Z", "+00:00")).astimezone(ZoneInfo(tz))
    hhmm = t.strftime("%H:%M")
    return b(f"{date_fa(t.date())}، ساعت {fa_digits(hhmm)}", f"{date_en(t.date())}, {hhmm} Tehran time")


def wk(n) -> str:
    return b(f"هفته {fa_digits(n)}", f"Week {n}")


def chip(kind: str, fa: str, en: str) -> str:
    return f'<span class="chip chip-{kind}">{b(fa, en)}</span>'


PR_CHIP = {"mentor_own": ("muted", "PR خودِ منتور", "Mentor’s own PR"), "draft": ("info", "پیش‌نویس", "Draft"), "needs_author": ("warn", "منتظر نویسنده", "Waiting for the author"),
           "needs_mentor": ("info", "منتظر منتور", "Waiting for the mentor"), "approved": ("ok", "تأیید شده", "Approved"),
           "merged": ("ok", "merge شد", "Merged"), "closed": ("bad", "بسته شد", "Closed")}
TASK_CHIP = {"done": ("ok", "انجام شد", "Done"), "review": ("info", "در بازبینی", "In review"),
             "started": ("warn", "در دست انجام", "In progress"), "open": ("muted", "باز", "Open")}
MILESTONE_CHIP = {"done": ("ok", "تمام", "Done"), "current": ("accent", "هفته‌ی جاری", "Current week"),
                  "overdue": ("bad", "از موعد گذشته", "Past due"), "upcoming": ("muted", "در راه", "Upcoming")}
DECISION_CHIP = {"pending": ("muted", "هنوز بازبینی نشده", "Not reviewed yet"), "passed": ("ok", "برقرار", "Passed"),
                 "partly": ("warn", "نیمه‌برقرار", "Partly met"), "failed": ("bad", "برقرار نیست", "Not met")}
CRIT_ICON = {"met": ("✓", "برقرار", "met"), "not_met": ("✗", "برقرار نیست", "not met"), "pending": ("○", "هنوز نه", "not yet")}
REVIEW_CHIP = {"approved": ("ok", "تأیید", "Approved"), "changes_requested": ("warn", "تغییر خواست", "Changes requested"),
               "commented": ("muted", "نظر", "Comment")}


def role_name(cfg, key):
    r = cfg["roles"].get(key)
    return b(E(r["fa"]), E(r["en"])) if r else b("کل تیم", "Whole team")


def meter(done, total, label_fa, label_en):
    pct = int(done * 100 / total) if total else 0
    return (f'<div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{pct}" '
            f'aria-label="{E(label_fa)} / {E(label_en)}"><i style="width:{pct}%"></i></div>')


def sec_hero(s, cfg):
    lv = s["level"]
    if lv["phase"] == "before":
        position = b("پروژه هنوز شروع نشده است.", "The project has not started yet.")
    elif lv["phase"] == "after":
        position = b("برنامه‌ی ۶ هفته تمام شده است.", "The six-week plan is over.")
    else:
        d = (b(f"روز {num(lv['day'])} از {num(lv['working_days'])}", f"day {num(lv['day'])} of {num(lv['working_days'])}")
             if not lv["weekend"] else b("پایان هفته", "weekend"))
        position = b(f"هفته {num(lv['week'])} از {num(lv['weeks'])}، {d}.", f"Week {num(lv['week'])} of {num(lv['weeks'])}, {d}.")
    lede = (f'<p class="lede">{position} '
            f'{b(f"{num(lv['done'])} از {num(lv['planned'])} کار انجام شده است ({num(lv['percent'])}٪).", f"{num(lv['done'])} of {num(lv['planned'])} planned tasks are done ({num(lv['percent'])}%).")}'
            f'</p>')
    segs = []
    for m in s["milestones"]:
        if m["n"] < 1:
            continue
        done_pct = int(m["done"] * 100 / m["planned"]) if m["planned"] else 0
        segs.append(
            f'<li class="seg" data-state="{E(m["state"])}"><div class="t"><b>{wk(m["n"])}</b>'
            f'<span class="muted">{b(E(m["fa"]), E(m["en"]))}</span></div>'
            f'<div class="meter" aria-hidden="true"><i style="width:{done_pct}%"></i></div>'
            f'<div class="c">{num(m["done"])} / {num(m["planned"])}</div></li>')
    health = ""
    h = s.get("main_health")
    if h:
        ok = h.get("conclusion") == "success"
        running = h.get("status") in ("in_progress", "queued")
        kind, fa, en = ("info", "در حال اجرا", "running") if running else (("ok", "سبز", "passing") if ok else ("bad", "قرمز", "failing"))
        health = f' · <a href="{E(h.get("url", "#"))}">{b("بررسی مستندات روی main", "docs check on main")}</a> {chip(kind, fa, en)}'
    return (f'<section class="hero" id="level" aria-labelledby="h-level"><h1 id="h-level">{b("وضعیت پروژه", "Project status")}</h1>{lede}'
            f'<p class="note">{b(E(lv["goal_fa"]), E(lv["goal_en"]))}</p>'
            f'{meter(lv["done"], lv["planned"], "پیشرفت کل", "Overall progress")}'
            f'<ol class="track" aria-label="{E("مراحل · weeks")}">{"".join(segs)}</ol>'
            f'<p class="updated">{b("آخرین به‌روزرسانی", "Last updated")}: {clock(s["generated_at"], cfg["timezone"])} '
            f'(<time data-ts="{E(s["generated_at"])}">{b("", "")}</time>) '
            f'<span id="stale" hidden>{chip("bad", "این صفحه چند ساعت است به‌روز نشده.", "This page has not updated for a few hours.")}</span>{health}</p>'
            f'</section>')


def sec_milestones(s):
    cards = []
    for m in s["milestones"]:
        kind, fa, en = MILESTONE_CHIP[m["state"]]
        rk, rfa, ren = DECISION_CHIP.get(m["review"]["decision"], DECISION_CHIP["pending"])
        r = m["review"]
        dates = (f'{day(m["start"])} – {day(m["due"])}' if m["start"] and m["due"] else (day(m["due"]) if m["due"] else ""))
        extra = b(f" · {num(m['in_review'])} در بازبینی", f" · {num(m['in_review'])} in review") if m["in_review"] else ""
        crit = (b(f" · {num(r['met'])} از {num(r['total'])} معیار", f" · {num(r['met'])} of {num(r['total'])} criteria") if r["total"] else "")
        link = f'<a href="{E(m["url"])}">{b("milestone در GitHub", "GitHub milestone")}</a>' if m["url"] else ""
        cards.append(
            f'<article class="card"><header><h3>{wk(m["n"])} · {b(E(m["fa"]), E(m["en"]))}</h3>{chip(kind, fa, en)}</header>'
            f'<p class="dates">{dates}</p><p class="goal">{b(E(m["goal_fa"]), E(m["goal_en"]))}</p>'
            f'{meter(m["done"], m["planned"], "کارهای این مرحله", "Tasks in this stage")}'
            f'<p class="nums">{b(f"{num(m['done'])} از {num(m['planned'])} کار انجام شده", f"{num(m['done'])} of {num(m['planned'])} planned tasks done")}{extra}</p>'
            f'<p class="rev">{b("بازبینی هفتگی", "Weekly review")}: {chip(rk, rfa, ren)}{crit}</p>{link}</article>')
    return (f'<section class="sec" id="milestones" aria-labelledby="h-ms"><h2 id="h-ms">{b("همه‌ی مرحله‌ها (milestoneها)", "All milestones")}</h2>'
            f'<p class="note">{b("پیشرفت فقط از کارهای برنامه‌ریزی‌شده حساب می‌شود؛ کارهای حذف‌شده و کارهای انتشار ۲ شمرده نمی‌شوند.", "Progress counts planned tasks only; cut tasks and Release 2 tasks are not counted.")}</p>'
            f'<div class="grid">{"".join(cards)}</div></section>')


def owners_html(owners):
    if not owners:
        return f'<span class="muted">{b("هنوز صاحب ندارد", "No owner yet")}</span>'
    return " ".join(f'<a class="ltr" href="https://github.com/{E(o)}">{E(o)}</a>' for o in owners)


def table(headers, rows):
    """A table that turns into a list of small cards on narrow screens: every cell carries its column label."""
    head = "".join(f"<th>{b(fa, en)}</th>" for fa, en in headers)
    body = []
    for row in rows:
        cells = "".join(
            f'<td data-fa="{E(h[0])}" data-en="{E(h[1])}"' + (f' class="{cls}"' if cls else "") + f">{content}</td>"
            for h, (content, cls) in zip(headers, row))
        body.append(f"<tr>{cells}</tr>")
    return f'<div class="scroll"><table class="stack"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def sec_week(s, cfg):
    tw = s["this_week"]
    parts = []
    headers = [("کار", "Task"), ("عنوان", "Title"), ("صاحب", "Owner"), ("وضعیت", "Status")]
    for g in tw["groups"]:
        rows = []
        for t in g["tasks"]:
            kind, fa, en = TASK_CHIP[t["status"]]
            mentor = f' {chip("warn", "بازبینی منتور", "mentor review")}' if t["mentor_review"] and not t["done"] else ""
            ident = E(t["task_id"] or f"#{t['number']}")
            rows.append([(f'<a class="ltr" href="{E(t["url"])}">{ident}</a>', "num"), (f'<bdi>{E(t["title"])}</bdi>', ""),
                         (owners_html(t["owners"]), ""), (chip(kind, fa, en) + mentor, "")])
        parts.append(f'<p class="role">{role_name(cfg, g["role"])}</p>{table(headers, rows)}')
    body = "".join(parts) or f'<p class="muted">{b("هنوز کاری برای این هفته ثبت نشده.", "No tasks for this week yet.")}</p>'
    week1_note = (f'<p class="note">{b("همه‌ی تیم این هفته منتظر محیط محلی، شاسی مشترک و CI هستند؛ اگر چیزی عقب است همان روز در گروه بگو.", "In week 1 everyone waits for the local environment, the shared kit and CI; if something slips, say so in the group the same day.")}</p>'
                  if tw["week"] == 1 else "")
    return (f'<section class="sec" id="week" aria-labelledby="h-week"><h2 id="h-week">{b("کارهای این هفته", "This week’s tasks")} '
            f'<span class="chip">{num(tw["done"])} / {num(tw["total"])}</span></h2>'
            f'{week1_note}{body}</section>')


def sec_prs(s):
    headers = [("PR", "PR"), ("عنوان", "Title"), ("نویسنده", "Author"), ("نوبت کیست", "Whose turn"), ("سن", "Age"),
               ("اندازه", "Size"), ("بازبینی هم‌تیمی", "Teammate review"), ("بازبین‌های خواسته‌شده", "Reviewers asked")]
    rows = []
    for p in s["prs"]["open"]:
        kind, fa, en = PR_CHIP[p["status"]]
        big = f' {chip("warn", "بزرگ", "big")}' if p["big"] else ""
        mates = "".join(chip("ok" if t["state"] == "approved" else "warn", t["login"], t["login"]) for t in p["teammate"]) or '<span class="muted">—</span>'
        asked = ", ".join(p["requested"]) or "—"
        rows.append([(f'<a href="{E(p["url"])}">#{num(p["number"])}</a>', "num"), (f'<bdi>{E(p["title"])}</bdi>', ""),
                     (f'<a class="ltr" href="https://github.com/{E(p["author"])}">{E(p["author"])}</a>', ""),
                     (chip(kind, fa, en), ""), (f'{num(p["age_days"])} {b("روز", "d")}', "num"),
                     (f'<span class="ltr">+{num(p["additions"])} −{num(p["deletions"])}</span>{big}', "num"),
                     (mates, ""), (f'<span class="ltr">{E(asked)}</span>', "muted")])
    tbl = table(headers, rows) if rows else f'<p class="muted">{b("الان PR بازی نیست.", "No open pull requests right now.")}</p>'
    merged = "".join(
        f'<li><a href="{E(p["url"])}">#{num(p["number"])}</a> <bdi>{E(p["title"])}</bdi> '
        f'<span class="muted">· <a class="ltr" href="https://github.com/{E(p["author"])}">{E(p["author"])}</a> · {day(p["merged_at"])}</span></li>'
        for p in s["prs"]["merged"]) or f'<li class="muted">{b("هنوز چیزی merge نشده.", "Nothing merged yet.")}</li>'
    return (f'<section class="sec" id="prs" aria-labelledby="h-prs"><h2 id="h-prs">{b("درخواست‌های باز (PR)", "Open pull requests")}</h2>'
            f'<p class="note">{b("هر PR برای merge شدن تأیید منتور لازم دارد. «نوبت کیست» می‌گوید توپ الان دست نویسنده است یا منتور.", "Every PR needs the mentor’s approval to merge. “Whose turn” says whether the ball is with the author or the mentor.")}</p>'
            f'{tbl}<h3>{b("تازه‌ترین کارهای merge‌شده", "Recently merged")}</h3><ul class="tl">{merged}</ul></section>')


def sec_reviews(s, cfg):
    headers = [("زمان", "When"), ("PR", "PR"), ("بازبین", "Reviewer"), ("نتیجه", "Result")]
    rows = []
    for r in s["reviews"]:
        kind, fa, en = REVIEW_CHIP.get(r["state"], REVIEW_CHIP["commented"])
        rows.append([(clock(r["at"], cfg["timezone"]), "num"),
                     (f'<a href="{E(r["url"])}">#{num(r["pr"])}</a> <bdi class="muted">{E(r["title"])}</bdi>', ""),
                     (f'<a class="ltr" href="https://github.com/{E(r["reviewer"])}">{E(r["reviewer"])}</a>', ""), (chip(kind, fa, en), "")])
    body = table(headers, rows) if rows else f'<p class="muted">{b("هنوز بازبینی‌ای ثبت نشده.", "No reviews yet.")}</p>'
    return f'<section class="sec" id="reviews" aria-labelledby="h-rev"><h2 id="h-rev">{b("گزارش بازبینی‌ها", "Review log")}</h2>{body}</section>'


def sec_weekly(s):
    items = []
    for m in s["milestones"]:
        r = m["review"]
        rk, rfa, ren = DECISION_CHIP.get(r["decision"], DECISION_CHIP["pending"])
        crit = "".join(
            f'<li><span class="i i-{E(c["status"])}" aria-hidden="true">{CRIT_ICON[c["status"]][0]}</span>'
            f'<span class="sr">{b(CRIT_ICON[c["status"]][1], CRIT_ICON[c["status"]][2])}</span>'
            f'<span>{b(E(c["fa"]), E(c["en"] or c["fa"]))}</span></li>' for c in r["criteria"])
        note = f'<p class="note">{b(E(r["note_fa"]), E(r["note_en"] or r["note_fa"]))}</p>' if (r["note_fa"] or r["note_en"]) else ""
        when = f' · {day(r["date"])}' if r["date"] else ""
        counts = b(f"{num(r['met'])} از {num(r['total'])}", f"{num(r['met'])} of {num(r['total'])}") if r["total"] else ""
        items.append(f'<details class="wk"{" open" if m["state"] == "current" else ""}><summary><b>{wk(m["n"])} · {b(E(m["fa"]), E(m["en"]))}</b>'
                     f'{chip(rk, rfa, ren)}<span class="muted">{counts}{when}</span></summary>'
                     f'<p class="note">{b(E(m["goal_fa"]), E(m["goal_en"]))}</p><ul class="crit">{crit}</ul>{note}</details>')
    return (f'<section class="sec" id="weekly" aria-labelledby="h-wk"><h2 id="h-wk">{b("بازبینی هفتگی (معیارهای پایان هفته)", "Weekly review (finish criteria)")}</h2>'
            f'<p class="note">{b("منتور بعد از هر بازبینی یا دمو نتیجه را ثبت می‌کند.", "The mentor records the result after each review or demo.")}</p>{"".join(items)}</section>')


def sec_people(s, cfg):
    cards = []
    for p in s["people"]:
        role = role_name(cfg, p["role"]) if p["role"] else f'<span class="muted">{b("نقش هنوز انتخاب نشده", "role not chosen yet")}</span>'
        tasks = "".join(f'<li>{chip(*TASK_CHIP[t["status"]])}<a class="ltr" href="{E(t["url"])}">{E(t["task_id"] or t["number"])}</a> <bdi>{E(t["title"])}</bdi></li>'
                        for t in p["tasks"][:8]) or f'<li class="muted">{b("هنوز کاری به خودش نگرفته.", "No tasks taken yet.")}</li>'
        cards.append(
            f'<article class="card"><header><h3><a class="ltr" href="https://github.com/{E(p["login"])}">{E(p["login"])}</a></h3>{role}</header>'
            f'<p class="nums">{b(f"کار باز {num(p['tasks_open'])} · انجام‌شده {num(p['tasks_done'])} · PR باز {num(p['prs_open'])} · merge‌شده {num(p['prs_merged'])}", f"open tasks {num(p['tasks_open'])} · done {num(p['tasks_done'])} · open PRs {num(p['prs_open'])} · merged {num(p['prs_merged'])}")}</p>'
            f'<ul class="tl">{tasks}</ul></article>')
    return (f'<section class="sec" id="people" aria-labelledby="h-people"><h2 id="h-people">{b("آدم‌ها و کارهایشان", "People and their work")}</h2>'
            f'<p class="note">{b("فقط کارها و PRها؛ نه رتبه‌بندی و نه سنجش فعالیت. هر کس کارهای نقش خودش را به خودش assign می‌کند تا اینجا پر شود.", "Tasks and pull requests only; no ranking and no activity scoring. Everyone assigns the tasks of their own role to themselves so this fills in.")}</p>'
            f'<div class="people">{"".join(cards)}</div></section>')


def sec_footer(s, cfg):
    repo = cfg["repo"]
    links = [
        (f"https://github.com/{repo}/milestones", "milestoneهای GitHub", "GitHub milestones"),
        (f"https://github.com/{repo}/issues?q=is%3Aissue+label%3Astatus-board", "برد وضعیت (issue)", "Status issue"),
        (f"https://github.com/{repo}/blob/main/docs/backlog.md", "فهرست همه‌ی کارها", "Full task list"),
        (f"https://github.com/{repo}/blob/main/docs/team.md", "تیم و تقسیم کار", "Team and roles"),
        (f"https://github.com/{repo}/tree/main/scripts/status", "کد این صفحه", "Source of this page"),
        ("status.json", "داده‌ی خام", "Raw data"),
    ]
    items = "".join(f'<li><a href="{E(u)}">{b(fa, en)}</a></li>' for u, fa, en in links)
    return (f'<footer class="foot"><p>{b("این صفحه خودش با هر بازبینی، PR و تغییر کار به‌روز می‌شود و ساعتی هم یک بار بازسازی می‌شود. زمان‌ها به وقت تهران است.", "This page updates itself on every review, pull request and task change, and is rebuilt every hour. Times are Tehran time.")}</p>'
            f'<ul>{items}</ul></footer>')


def render_page(status: dict, cfg: dict) -> str:
    body = "".join([sec_hero(status, cfg), sec_milestones(status), sec_week(status, cfg), sec_prs(status),
                    sec_reviews(status, cfg), sec_weekly(status), sec_people(status, cfg), sec_footer(status, cfg)])
    return (f'<!doctype html>\n<html lang="fa" dir="rtl" data-lang="fa" data-generated="{E(status["generated_at"])}" data-stale-hours="{cfg["stale_after_hours"]}">\n'
            f'<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="color-scheme" content="light dark"><meta name="robots" content="noindex">'
            f'<title>وضعیت پروژه‌ی سرمیز · Sarmiz project status</title>'
            f'<meta name="description" content="وضعیت پروژه‌ی سرمیز: مرحله‌ها، کارهای انجام‌شده و بازبینی‌ها · Sarmiz project status: milestones, finished work and reviews">'
            f'<style>{CSS}</style></head>\n<body><div class="wrap">'
            f'<header class="top"><div class="mark">سرمیز<small>Sarmiz</small></div>'
            f'<div class="lang" role="group" aria-label="زبان · Language"><button type="button" data-set-lang="fa" aria-pressed="true">فارسی</button>'
            f'<button type="button" data-set-lang="en" aria-pressed="false">English</button></div></header>'
            f'<main class="wrap">{body}</main></div>\n<script>{JS}</script></body></html>\n')
