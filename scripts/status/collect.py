"""Reads the raw project data from GitHub with the gh CLI (in GitHub Actions the CLI uses GH_TOKEN)."""
import json
import pathlib
import subprocess
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROLE_KEYS = {"فرانت": "web", "ورود و منو": "menu", "سفارش و زیرساخت": "orders"}
PR_FIELDS = ("number,title,url,state,author,createdAt,updatedAt,mergedAt,closedAt,isDraft,reviewRequests,labels,"
             "additions,deletions,changedFiles,headRefName,commits,reviews,mergedBy,body")


def gh(*args, required=True):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        if required:
            raise RuntimeError(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()[:300]}")
        return None
    return json.loads(result.stdout) if result.stdout.strip() else None


def team_roles() -> dict:
    """{github login: role key} from the roles table in docs/team.md (empty until the students fill it in)."""
    path = ROOT / "docs" / "team.md"
    roles = {}
    if not path.exists():
        return roles
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in ROLE_KEYS and cells[2].strip("` "):
            roles[cells[2].strip("` ")] = ROLE_KEYS[cells[0]]
    return roles


def weekly_review_file() -> dict:
    path = ROOT / "docs" / "status" / "reviews.toml"
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main_health(repo: str):
    runs = gh("run", "list", "--repo", repo, "--workflow", "docs.yml", "--branch", "main", "--limit", "1",
              "--json", "conclusion,status,createdAt,url", required=False)
    return runs[0] if runs else None


def collect(cfg: dict) -> dict:
    repo = cfg["repo"]
    issues = gh("issue", "list", "--repo", repo, "--state", "all", "--limit", "500", "--json",
                "number,title,state,stateReason,labels,milestone,assignees,url")
    milestones = gh("api", f"repos/{repo}/milestones?state=all&per_page=100")
    # One call per PR: listing commits, reviews and comments for all PRs at once exceeds GitHub's GraphQL node limit.
    numbers = [p["number"] for p in (gh("pr", "list", "--repo", repo, "--state", "all", "--limit", "100", "--json", "number") or [])]
    prs = [gh("pr", "view", str(n), "--repo", repo, "--json", PR_FIELDS) for n in numbers]
    return {
        "issues": issues or [],
        "milestones": milestones or [],
        "prs": [p for p in prs if p],
        "roles": team_roles(),
        "reviews_toml": weekly_review_file(),
        "main_health": main_health(repo),
    }
