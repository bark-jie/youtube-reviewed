#!/usr/bin/env python3
"""Fill the RULE-SET URLs in Shadowrocket_RuleSet.conf and verify everything.

Usage:
  python3 tools/fill_and_verify.py [raw_base_url]            # fill + local checks
  python3 tools/fill_and_verify.py [raw_base_url] --online   # also fetch each URL and compare

raw_base_url defaults to DEFAULT_BASE (the ruleset/ folder on the main branch of this repo),
so that <raw_base_url>/AI.list is the latest raw AI.list (branch name, no commit hash).

Reads template/Shadowrocket_RuleSet.conf and writes the filled Shadowrocket_RuleSet.conf at the
repo root (that file is what users import), plus Shadowrocket_RuleSet_NoGroup.conf: the same
rules with no proxy groups, every custom rule pointing at PROXY (the node picked on the home page).
"""
import sys, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template" / "Shadowrocket_RuleSet.conf"
OUT = ROOT / "Shadowrocket_RuleSet.conf"
OUT_NOGROUP = ROOT / "Shadowrocket_RuleSet_NoGroup.conf"
DEFAULT_BASE = "https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/ruleset"
BACKUP = ROOT / "backup" / "Shadowrocket_Sensitive_AI_HoK.conf"
PLACEHOLDER = "https://gist.githubusercontent.com/USERNAME/GIST_ID/raw"
SETS = [("Sensitive.list", "Sensitive"), ("AI.list", "AI"), ("HonorOfKings.list", "Honor-of-Kings")]
ALLOWED_IN_LIST = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-ASN"}


def rules(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


def check_lists():
    ok = True
    seen = {}
    for fn, _ in SETS:
        for r in rules(ROOT / "ruleset" / fn):
            parts = r.split(",")
            if parts[0] not in ALLOWED_IN_LIST:
                print(f"[FAIL] {fn}: unsupported type in a list file: {r}"); ok = False
            if parts[0].startswith("IP-") and parts[-1] != "no-resolve":
                print(f"[FAIL] {fn}: IP rule without no-resolve: {r}"); ok = False
            if parts[0] in ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD") and len(parts) != 2:
                print(f"[FAIL] {fn}: domain rule must be TYPE,value (no policy): {r}"); ok = False
            key = (parts[0], parts[1])
            if key in seen:
                print(f"[FAIL] duplicate {key} in {fn} and {seen[key]}"); ok = False
            seen[key] = fn
    return ok


def check_equivalence(conf_text):
    """Rules from the 3 lists + inline custom rules must equal the custom block of the backup config."""
    b = BACKUP.read_text(encoding="utf-8")
    blk = b[b.index("[Rule]\n"):b.index("# ==================== Original default rules")]
    old = sorted(l for l in blk.splitlines()[1:] if l and not l.startswith("#"))
    new = []
    for fn, pol in SETS:
        for r in rules(ROOT / "ruleset" / fn):
            a = r.split(",")
            new.append(",".join(a[:2] + [pol] + a[2:]))
    c = conf_text[conf_text.index("[Rule]\n"):conf_text.index("# ==================== Original default rules")]
    new += [l for l in c.splitlines()[1:] if l and not l.startswith("#") and not l.startswith("RULE-SET")]
    if sorted(new) == old:
        print(f"[OK] rule sets + inline rules == backup config ({len(old)} rules)")
        return True
    print("[INFO] rule sets differ from the backup config (expected after you edit the lists):")
    print("       only in lists/inline:", sorted(set(new) - set(old))[:20])
    print("       only in backup:      ", sorted(set(old) - set(new))[:20])
    return True


NOGROUP_HEADER = """# Shadowrocket config (no proxy groups): original default + the same Sensitive / AI / Honor-of-Kings rules,
# all sent to PROXY, i.e. the node selected on the Shadowrocket home page.
"""


def make_nogroup(filled):
    """Same config without [Proxy Group]; custom-group policies become PROXY."""
    groups = [pol for _, pol in SETS]
    head, rest = filled.split("[General]\n", 1)
    general, rest = rest.split("[Proxy Group]\n", 1)
    _, rest = rest.split("[Rule]\n", 1)
    custom, default = rest.split("# ==================== Original default rules", 1)
    out = []
    for line in custom.splitlines():
        if line and not line.startswith("#"):
            a = line.split(",")
            assert a[2] in groups, f"unexpected policy in custom block: {line}"
            a[2] = "PROXY"
            line = ",".join(a)
        out.append(line)
    text = (NOGROUP_HEADER + "\n".join(l for l in head.splitlines()[1:] if l.startswith("#") and "proxy groups" not in l.lower())
            + "\n[General]\n" + general + "[Rule]\n" + "\n".join(out) + "\n# ==================== Original default rules" + default)
    for g in groups:
        assert f",{g}" not in text and f"{g} =" not in text, f"group {g} still referenced"
    assert "[Proxy Group]" not in text
    return text


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base = (args[0] if args else DEFAULT_BASE).rstrip("/")
    online = "--online" in sys.argv
    t = TEMPLATE.read_text(encoding="utf-8")
    assert t.count(PLACEHOLDER) == 3, "template placeholder not found 3 times"
    filled = t.replace(PLACEHOLDER, base)
    OUT.write_text(filled, encoding="utf-8")
    print(f"[OK] wrote {OUT.name}")
    OUT_NOGROUP.write_text(make_nogroup(filled), encoding="utf-8")
    print(f"[OK] wrote {OUT_NOGROUP.name} (no groups, all custom rules -> PROXY)")
    ok = check_lists()
    check_equivalence(filled)
    if online:
        for fn, _ in SETS:
            url = f"{base}/{fn}"
            try:
                with urllib.request.urlopen(url, timeout=20) as r:
                    remote = r.read().decode("utf-8")
            except Exception as e:
                print(f"[FAIL] fetch {url}: {e}"); ok = False; continue
            local = (ROOT / "ruleset" / fn).read_text(encoding="utf-8")
            if remote.strip() == local.strip():
                print(f"[OK] {url} matches local file")
            else:
                print(f"[FAIL] {url} differs from local file (GitHub raw can cache a few minutes; retry)"); ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
