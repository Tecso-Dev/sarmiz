"""Unit tests for the status model. Run: python3 -m unittest discover -s scripts/status/tests -v"""
import datetime as dt
import pathlib
import sys
import tomllib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import fmt  # noqa: E402
import model  # noqa: E402

CFG = tomllib.loads((HERE.parent / "config.toml").read_text(encoding="utf-8"))
UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 22, 12, 0, tzinfo=UTC)  # Sunday = day 2 of week 1


def issue(number, title, state="OPEN", reason=None, milestone="Week 1: x", labels=(), owners=()):
    return {"number": number, "title": title, "state": state, "stateReason": reason, "url": f"https://x/issues/{number}",
            "labels": [{"name": l} for l in labels],
            "milestone": {"title": milestone} if milestone else None,
            "assignees": [{"login": o} for o in owners]}


def pr(number, author="student", state="OPEN", draft=False, commits=(), reviews=(), requested=(), branch="order/W1-ORD-1-x",
       title="feat: x", additions=10, deletions=0, body=""):
    return {"number": number, "title": title, "body": body, "url": f"https://x/pull/{number}", "state": state,
            "isDraft": draft, "author": {"login": author}, "createdAt": "2026-11-22T10:00:00Z", "updatedAt": "2026-11-22T10:00:00Z",
            "headRefName": branch, "additions": additions, "deletions": deletions, "changedFiles": 1,
            "commits": [{"committedDate": c} for c in commits],
            "reviews": [{"author": {"login": a}, "state": s, "submittedAt": t} for a, s, t in reviews],
            "reviewRequests": [{"login": r} for r in requested], "labels": []}


class FormatTests(unittest.TestCase):
    def test_jalali_known_dates(self):
        self.assertEqual(fmt.to_jalali(dt.date(2026, 11, 22)), (1405, 9, 1))   # 1 Azar 1405
        self.assertEqual(fmt.to_jalali(dt.date(2026, 11, 14)), (1405, 8, 23))  # 23 Aban 1405 (decision 0007)
        self.assertEqual(fmt.date_fa(dt.date(2026, 11, 22)), "۱ آذر")
        self.assertEqual(fmt.date_en(dt.date(2026, 11, 22)), "22 Nov")

    def test_persian_digits_and_bar(self):
        self.assertEqual(fmt.fa_digits(1405), "۱۴۰۵")
        self.assertEqual(fmt.bar(0, 69), "▱" * 10)
        self.assertEqual(fmt.bar(69, 69), "▰" * 10)
        self.assertEqual(fmt.bar(0, 0), "▱" * 10)


class LevelTests(unittest.TestCase):
    def test_level_by_date(self):
        d = dt.date
        self.assertEqual(model.level_now(CFG, d(2026, 11, 20))["phase"], "before")
        self.assertEqual(model.level_now(CFG, d(2026, 11, 21)), {"week": 1, "day": 1, "weekend": False, "phase": "running"})
        self.assertEqual(model.level_now(CFG, d(2026, 11, 22))["day"], 2)
        wed = model.level_now(CFG, d(2026, 11, 25))
        self.assertEqual((wed["week"], wed["day"], wed["weekend"]), (1, 5, False))
        thu = model.level_now(CFG, d(2026, 11, 26))
        self.assertEqual((thu["week"], thu["day"], thu["weekend"]), (1, 5, True))
        self.assertEqual(model.level_now(CFG, d(2026, 11, 28))["week"], 2)
        self.assertEqual(model.level_now(CFG, d(2027, 2, 1))["phase"], "after")

    def test_week_dates(self):
        self.assertEqual(model.week_start(CFG, 1), dt.date(2026, 11, 21))
        self.assertEqual(model.week_end(CFG, 1), dt.date(2026, 11, 25))
        self.assertEqual(model.week_end(CFG, 6), dt.date(2026, 12, 30))

    def test_tehran_date_near_midnight(self):
        late_utc = dt.datetime(2026, 11, 22, 21, 0, tzinfo=UTC)  # 00:30 on the 23rd in Tehran
        self.assertEqual(model.local_today(late_utc, CFG), dt.date(2026, 11, 23))


class IssueTests(unittest.TestCase):
    def test_flags(self):
        done = model.normalize_issue(issue(1, "W1-ORD-1: طرح", state="CLOSED", reason="COMPLETED", labels=["role:orders", "mentor-review"], owners=["a"]))
        cut = model.normalize_issue(issue(2, "W1-ORD-3: x", state="CLOSED", reason="NOT_PLANNED", milestone=None))
        r2 = model.normalize_issue(issue(3, "W1-PA-7: x", milestone="Release 2", labels=["release-2"]))
        open_ = model.normalize_issue(issue(4, "W1-WEB-1: x", labels=["role:web"]))
        self.assertTrue(done["done"] and done["planned"] and done["mentor_review"])
        self.assertEqual((done["task_id"], done["title"], done["role"], done["owners"]), ("W1-ORD-1", "طرح", "orders", ["a"]))
        self.assertTrue(cut["cut"] and not cut["planned"] and not cut["done"])
        self.assertTrue(r2["release2"] and not r2["planned"])
        self.assertTrue(open_["planned"] and not open_["done"])

    def test_cut_task_never_counts_as_done_even_with_a_milestone(self):
        t = model.normalize_issue(issue(5, "W2-WEB-5: x", state="CLOSED", reason="NOT_PLANNED", milestone="Week 2: x"))
        self.assertFalse(t["planned"] or t["done"])


class PullRequestTests(unittest.TestCase):
    def status(self, **kw):
        return model.normalize_pr(pr(1, **kw), CFG, NOW)["status"]

    def test_new_pr_waits_for_the_mentor(self):
        self.assertEqual(self.status(commits=["2026-11-22T09:00:00Z"], requested=["sobhanaz"]), "needs_mentor")

    def test_changes_requested_waits_for_the_author(self):
        reviews = [("sobhanaz", "CHANGES_REQUESTED", "2026-11-22T10:00:00Z")]
        self.assertEqual(self.status(commits=["2026-11-22T09:00:00Z"], reviews=reviews), "needs_author")

    def test_new_push_after_changes_requested_goes_back_to_the_mentor(self):
        reviews = [("sobhanaz", "CHANGES_REQUESTED", "2026-11-22T10:00:00Z")]
        self.assertEqual(self.status(commits=["2026-11-22T09:00:00Z", "2026-11-22T11:00:00Z"], reviews=reviews), "needs_mentor")

    def test_rerequest_goes_back_to_the_mentor(self):
        reviews = [("sobhanaz", "CHANGES_REQUESTED", "2026-11-22T10:00:00Z")]
        self.assertEqual(self.status(commits=["2026-11-22T09:00:00Z"], reviews=reviews, requested=["sobhanaz"]), "needs_mentor")

    def test_approved_and_approval_goes_stale_on_push(self):
        reviews = [("sobhanaz", "APPROVED", "2026-11-22T10:00:00Z")]
        self.assertEqual(self.status(commits=["2026-11-22T09:00:00Z"], reviews=reviews), "approved")
        self.assertEqual(self.status(commits=["2026-11-22T09:00:00Z", "2026-11-22T10:30:00Z"], reviews=reviews), "needs_mentor")

    def test_teammate_approval_does_not_count_for_the_mentor_gate(self):
        reviews = [("friend", "APPROVED", "2026-11-22T10:00:00Z")]
        p = model.normalize_pr(pr(1, commits=["2026-11-22T09:00:00Z"], reviews=reviews), CFG, NOW)
        self.assertEqual(p["status"], "needs_mentor")
        self.assertEqual(p["teammate"], [{"login": "friend", "state": "approved"}])

    def test_mentors_own_pr_is_not_waiting_for_the_mentor(self):
        p = model.normalize_pr(pr(7, author="sobhanaz", commits=["2026-11-22T09:00:00Z"]), CFG, NOW)
        self.assertEqual(p["status"], "mentor_own")

    def test_status_labels_follow_the_status_and_skip_the_mentors_own_pr(self):
        import actions
        prs = [model.normalize_pr(pr(7, author="sobhanaz"), CFG, NOW),
               model.normalize_pr(pr(8, commits=["2026-11-22T09:00:00Z"]), CFG, NOW)]
        prs[0]["labels"] = ["status:needs-mentor"]          # put there by an earlier version
        changes = {c["number"]: c for c in actions.label_changes(prs)}
        self.assertEqual(changes[7], {"number": 7, "add": [], "remove": ["status:needs-mentor"]})
        self.assertEqual(changes[8], {"number": 8, "add": ["status:needs-mentor"], "remove": []})

    def test_draft_merged_closed(self):
        self.assertEqual(self.status(draft=True), "draft")
        self.assertEqual(self.status(state="MERGED"), "merged")
        self.assertEqual(self.status(state="CLOSED"), "closed")

    def test_size_and_age(self):
        p = model.normalize_pr(pr(1, additions=300, deletions=150), CFG, NOW)
        self.assertTrue(p["big"])
        self.assertEqual(p["lines"], 450)
        self.assertEqual(p["age_days"], 0)

    def test_dismissed_mentor_review_is_ignored(self):
        reviews = [("sobhanaz", "APPROVED", "2026-11-22T10:00:00Z"), ("sobhanaz", "DISMISSED", "2026-11-22T10:05:00Z")]
        p = model.normalize_pr(pr(1, commits=["2026-11-22T09:00:00Z"], reviews=reviews), CFG, NOW)
        self.assertEqual((p["status"], p["mentor_state"]), ("needs_mentor", ""))


class LinkingAndCountsTests(unittest.TestCase):
    def build(self, issues, prs, weekly=None):
        raw = {"issues": issues, "prs": prs, "milestones": [], "roles": {}, "reviews_toml": weekly or {}}
        return model.build_status(raw, CFG, NOW)

    def test_pr_links_to_task_by_branch_and_sets_status(self):
        s = self.build([issue(6, "W1-ORD-1: طرح", labels=["role:orders"]), issue(7, "W1-ORD-2: x", labels=["role:orders"])],
                       [pr(92, commits=["2026-11-22T09:00:00Z"], branch="order/W1-ORD-1-order-data-model")])
        tasks = {t["task_id"]: t for g in s["this_week"]["groups"] for t in g["tasks"]}
        self.assertEqual(tasks["W1-ORD-1"]["status"], "review")
        self.assertEqual(tasks["W1-ORD-1"]["prs"], [92])
        self.assertEqual(tasks["W1-ORD-2"]["status"], "open")  # week 2 task is in another milestone only if labelled; here same milestone

    def test_task_is_in_progress_while_the_author_has_changes_to_make(self):
        reviews = [("sobhanaz", "CHANGES_REQUESTED", "2026-11-22T10:00:00Z")]
        s = self.build([issue(6, "W1-ORD-1: x", labels=["role:orders"])],
                       [pr(92, commits=["2026-11-22T09:00:00Z"], reviews=reviews, branch="order/W1-ORD-1-x")])
        task = s["this_week"]["groups"][0]["tasks"][0]
        self.assertEqual(task["status"], "started")

    def test_closes_keyword_links_task(self):
        s = self.build([issue(12, "W1-WEB-1: x", labels=["role:web"])],
                       [pr(5, branch="misc", body="Closes #12", draft=True)])
        task = s["this_week"]["groups"][0]["tasks"][0]
        self.assertEqual(task["status"], "started")

    def test_counts_ignore_cut_and_release2(self):
        issues = [issue(1, "W1-A-1: a", state="CLOSED", reason="COMPLETED"), issue(2, "W1-A-2: b"),
                  issue(3, "W1-A-3: c", state="CLOSED", reason="NOT_PLANNED"),
                  issue(4, "W1-A-4: d", milestone="Release 2", labels=["release-2"])]
        s = self.build(issues, [])
        self.assertEqual((s["level"]["planned"], s["level"]["done"], s["level"]["percent"]), (2, 1, 50))
        week1 = next(m for m in s["milestones"] if m["n"] == 1)
        self.assertEqual((week1["planned"], week1["done"], week1["open"], week1["state"]), (2, 1, 1, "current"))

    def test_overdue_and_upcoming_milestones(self):
        s = self.build([issue(1, "W0-M-1: x", milestone="Week 0: x"), issue(9, "W3-A-1: x", milestone="Week 3: x")], [])
        states = {m["n"]: m["state"] for m in s["milestones"]}
        self.assertEqual(states[0], "overdue")   # due 20 Nov, still open
        self.assertEqual(states[1], "current")
        self.assertEqual(states[3], "upcoming")

    def test_weekly_review_counts(self):
        weekly = {"week": [{"n": 1, "date": "2026-11-25", "decision": "partly",
                            "criteria": [{"fa": "الف", "en": "a", "status": "met"}, {"fa": "ب", "en": "b", "status": "not_met"}]}]}
        s = self.build([], [], weekly)
        r = next(m for m in s["milestones"] if m["n"] == 1)["review"]
        self.assertEqual((r["met"], r["total"], r["decision"]), (1, 2, "partly"))

    def test_groups_follow_role_order(self):
        s = self.build([issue(1, "W1-WEB-1: a", labels=["role:web"]), issue(2, "W1-PA-1: b", labels=["role:orders"]),
                        issue(3, "W1-CORE-1: c", labels=["role:menu"])], [])
        self.assertEqual([g["role"] for g in s["this_week"]["groups"]], ["orders", "menu", "web"])

    def test_people_rows(self):
        s = self.build([issue(1, "W1-WEB-1: a", labels=["role:web"], owners=["Moh4mmadNSZ"]),
                        issue(2, "W1-WEB-2: b", state="CLOSED", reason="COMPLETED", labels=["role:web"], owners=["Moh4mmadNSZ"])],
                       [pr(8, author="Moh4mmadNSZ")])
        p = next(x for x in s["people"] if x["login"] == "Moh4mmadNSZ")
        self.assertEqual((p["tasks_open"], p["tasks_done"], p["prs_open"], p["role"]), (1, 1, 1, "web"))


class EventTests(unittest.TestCase):
    def snap(self, **prs):
        return {"prs": prs}

    def entry(self, state="open", requested=(), reviews=()):
        return {"state": state, "title": "T", "url": "u", "author": "a", "requested": list(requested), "reviews": list(reviews)}

    def test_first_run_announces_nothing(self):
        self.assertEqual(model.diff_events(None, self.snap(**{"1": self.entry()})), [])

    def test_new_pr_and_requested_reviewers(self):
        ev = model.diff_events(self.snap(), self.snap(**{"5": self.entry(requested=["sobhanaz"])}))
        self.assertEqual([(e["kind"], e["number"]) for e in ev], [("pr_opened", 5)])
        self.assertEqual(ev[0]["requested"], ["sobhanaz"])

    def test_review_decision_and_rerequest(self):
        prev = self.snap(**{"5": self.entry()})
        cur = self.snap(**{"5": self.entry(requested=["sobhanaz"], reviews=["sobhanaz|CHANGES_REQUESTED|2026-11-22T10:00:00Z"])})
        kinds = [e["kind"] for e in model.diff_events(prev, cur)]
        self.assertEqual(kinds, ["changes_requested", "review_requested"])

    def test_old_reviews_are_not_repeated(self):
        e = self.entry(reviews=["sobhanaz|APPROVED|2026-11-22T10:00:00Z"])
        self.assertEqual(model.diff_events(self.snap(**{"5": e}), self.snap(**{"5": e})), [])

    def test_comment_only_reviews_are_not_announced(self):
        prev = self.snap(**{"5": self.entry()})
        cur = self.snap(**{"5": self.entry(reviews=["sobhanaz|COMMENTED|2026-11-22T10:00:00Z"])})
        self.assertEqual(model.diff_events(prev, cur), [])

    def test_merged_and_closed(self):
        prev = self.snap(**{"5": self.entry(), "6": self.entry()})
        cur = self.snap(**{"5": self.entry(state="merged"), "6": self.entry(state="closed")})
        self.assertEqual([e["kind"] for e in model.diff_events(prev, cur)], ["merged", "closed"])

    def test_snapshot_roundtrip_is_stable(self):
        s = model.build_status({"issues": [], "prs": [pr(1, reviews=[("sobhanaz", "APPROVED", "2026-11-22T10:00:00Z")])],
                                "milestones": [], "roles": {}, "reviews_toml": {}}, CFG, NOW)
        snap = model.snapshot(s)
        self.assertEqual(model.diff_events(snap, snap), [])
        self.assertEqual(snap["prs"]["1"]["reviews"], ["sobhanaz|APPROVED|2026-11-22T10:00:00Z"])


if __name__ == "__main__":
    unittest.main()
