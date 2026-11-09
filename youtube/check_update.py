#!/usr/bin/env python3
"""Check Maasea/sgmodule for a new youtube.response.js and (optionally) adopt it.

  python3 youtube/check_update.py <work_dir>           # report only
  python3 youtube/check_update.py <work_dir> --adopt   # copy the new script in if every check passes

Prints one status line first:
  STATUS: NO_CHANGE        upstream script is the pinned one
  STATUS: TOO_NEW          changed, but the change is younger than min_age_days (check again later)
  STATUS: NEEDS_REVIEW     changed and old enough, but the scan found new risk indicators
  STATUS: CANDIDATE_OK     changed, old enough, no new risk indicators (still read the report)
  STATUS: ADOPTED          --adopt copied it in and updated state.json (commit + push yourself)
The scan is a heuristic over a minified bundle; it is not a full review.
"""
import sys, json, re, hashlib, subprocess, pathlib, datetime

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE / "state.json"
LOCAL = HERE / "youtube.response.js"
INDICATORS = {
    "httpClient": r"\$httpClient\.",
    "task.fetch": r"\$task\.fetch",
    "fetch_call": r"(?<![A-Za-z_$])fetch\(",
    "XMLHttpRequest": r"XMLHttpRequest",
    "WebSocket": r"WebSocket",
    "eval": r"(?<![A-Za-z_$.])eval\(",
    "new Function": r"new Function\(",
    "atob": r"(?<![A-Za-z_$.])atob\(",
    "fromCharCode": r"fromCharCode",
    "persistentStore.write": r"\$persistentStore\.write|\$prefs\.setValueForKey",
    "notification": r"\$notification\.post|\$notify\(",
    "url_redirect_done": r"\$done\(\{url:",
}
URL_RE = re.compile(r"https?://[A-Za-z0-9.\-]+")
HOST_RE = re.compile(r"[\"'`/]([a-z0-9\-]+(?:\.[a-z0-9\-]+)*\.(?:com|net|org|io|dev|app|xyz|top|cn|me|co|cc|workers\.dev))[\"'`/:?]")


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def scan(text):
    return {
        "counts": {k: len(re.findall(v, text)) for k, v in INDICATORS.items()},
        "urls": sorted(set(URL_RE.findall(text))),
        "hosts": sorted(set(HOST_RE.findall(text))),
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    work = pathlib.Path(sys.argv[1]); work.mkdir(parents=True, exist_ok=True)
    adopt = "--adopt" in sys.argv
    st = json.loads(STATE.read_text())
    repo = work / "sgmodule"
    if repo.exists():
        git("fetch", "-q", "origin", "master", cwd=repo); git("checkout", "-q", "FETCH_HEAD", cwd=repo)
    else:
        git("clone", "-q", "--filter=blob:none", st["upstream_repo"], str(repo))
    head = git("rev-parse", "HEAD", cwd=repo)
    blob = git("rev-parse", f"HEAD:{st['upstream_path']}", cwd=repo)
    print(f"upstream HEAD {head}, script blob {blob} (pinned {st['pinned_blob']})")
    if blob == st["pinned_blob"]:
        print("STATUS: NO_CHANGE"); return
    changed_at = git("log", "-1", "--format=%cI", "--", st["upstream_path"], cwd=repo)
    age = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(changed_at)).days
    new_text = (repo / st["upstream_path"]).read_text(encoding="utf-8")
    old, new = scan(LOCAL.read_text(encoding="utf-8")), scan(new_text)
    flags = []
    for k in INDICATORS:
        if new["counts"][k] > old["counts"][k]:
            flags.append(f"{k}: {old['counts'][k]} -> {new['counts'][k]}")
    for kind in ("urls", "hosts"):
        added = sorted(set(new[kind]) - set(old[kind]))
        if added:
            flags.append(f"new {kind}: {added}")
    log = git("log", "--format=%h %cI %s", f"{st['pinned_commit']}..HEAD", "--", "Script/Youtube", "YouTube.Enhance.sgmodule", cwd=repo)
    print(f"script last changed {changed_at} ({age} days ago); size {LOCAL.stat().st_size} -> {len(new_text.encode())} bytes")
    print("upstream commits since pinned:\n" + (log or "  (none listed)"))
    print("risk indicator changes:", "none" if not flags else "")
    for f in flags:
        print("  - " + f)
    if age < st["min_age_days"]:
        print("STATUS: TOO_NEW"); return
    if flags:
        print("STATUS: NEEDS_REVIEW"); return
    if not adopt:
        print("STATUS: CANDIDATE_OK"); return
    LOCAL.write_text(new_text, encoding="utf-8")
    st.update(pinned_commit=git("log", "-1", "--format=%H", "--", st["upstream_path"], cwd=repo), pinned_blob=blob,
              pinned_sha256=hashlib.sha256(new_text.encode()).hexdigest(), adopted_on=datetime.date.today().isoformat())
    STATE.write_text(json.dumps(st, indent=2) + "\n")
    print("STATUS: ADOPTED")


if __name__ == "__main__":
    main()
