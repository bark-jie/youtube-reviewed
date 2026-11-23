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


CLASH_DIR = ROOT / "ruleset" / "clash"


def write_clash_yaml():
    """Comment-free classical YAML copies of the lists for Stash / mihomo (Clash Party) rule-providers."""
    CLASH_DIR.mkdir(exist_ok=True)
    out = []
    for fn, _ in SETS:
        rs = list(rules(ROOT / "ruleset" / fn))
        name = fn.replace(".list", ".yaml")
        body = "# Generated from ruleset/%s by tools/fill_and_verify.py. Do not edit; edit the .list file.\npayload:\n" % fn
        body += "".join("  - '%s'\n" % r for r in rs)
        (CLASH_DIR / name).write_text(body, encoding="utf-8")
        out.append(name)
    print(f"[OK] wrote ruleset/clash/{{{','.join(out)}}} (Stash / Clash Party copies)")


# ---------------- Stash / Clash Party overrides (generated) ----------------
# To add an airport: append (name, argument-name, label) here, re-run this script, push.
AIRPORTS = [("SinX", "sinx_url", "SinX"), ("G94cloud", "g94_url", "G94cloud")]
RAW_CLASH = "https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/ruleset/clash"
STASH_OUT = ROOT / "stash" / "RuleSet.stoverride"
PARTY_OUT = ROOT / "clash-party" / "RuleSet.override.yaml"
# Inline-only rules (types not used in list files); "DEST-PORT" is Shadowrocket spelling, Stash/mihomo use DST-PORT.
INLINE = [("DOMAIN-WILDCARD,*.sgameglobal.com.acc.*", "Honor-of-Kings"),
          ("DOMAIN-WILDCARD,hok*.intlgame.com", "Honor-of-Kings"),
          ("DST-PORT,5010", "Honor-of-Kings")]


def q(x):
    return "'" + x.replace("'", "''") + "'"


def groups_yaml(health_key):
    """Each custom group: select between one sub-group per airport; each sub-group: select over that airport's provider."""
    lines = []
    for _, pol in SETS:
        lines += [f"  - name: {q(pol)}", "    type: select", "    proxies:"]
        lines += [f"      - {q(pol + '-' + a)}" for a, _, _ in AIRPORTS]
    for _, pol in SETS:
        for a, _, _ in AIRPORTS:
            lines += [f"  - name: {q(pol + '-' + a)}", "    type: select", "    use:", f"      - {q(a)}"]
            if health_key == "lazy":
                lines += ["    lazy: true"]
    return lines


def rules_yaml():
    lines = [f"  - RULE-SET,rs-{fn[:-5]},{pol}" for fn, pol in SETS]
    lines += [f"  - {r},{pol}" for r, pol in INLINE]
    return lines


def rule_providers_yaml(with_type):
    lines = []
    for fn, _ in SETS:
        n = fn[:-5]
        lines += [f"  rs-{n}:"] + (["    type: http"] if with_type else [])
        lines += ["    behavior: classical", "    format: yaml", f"    url: {RAW_CLASH}/{n}.yaml", "    interval: 86400"]
    return lines


def write_overrides():
    t = TEMPLATE.read_text(encoding="utf-8")
    c = t[t.index("[Rule]\n"):t.index("# ==================== Original default rules")]
    tmpl_inline = sorted(l for l in c.splitlines()[1:] if l and not l.startswith("#") and not l.startswith("RULE-SET"))
    mine = sorted(f"{r.replace('DST-PORT', 'DEST-PORT')},{pol}" for r, pol in INLINE)
    assert mine == tmpl_inline, f"INLINE out of sync with template: {mine} vs {tmpl_inline}"
    names = " / ".join(pol for _, pol in SETS)
    st = [
        "# Generated by tools/fill_and_verify.py. Do not edit by hand.",
        "# Stash override: adds the Sensitive / AI / Honor-of-Kings groups and rules on top of an airport's",
        "# subscribed config. Subscription links are override arguments: entered in the Stash app and stored",
        "# only on the device, never in this file.",
        f"name: {q('分流分组（' + names + '）')}",
        "desc: |-",
        "  在机场订阅配置之上加入三个手动选择的分组和对应规则，规则排在最前面。",
        "  每个组先选机场，再到「组名-机场」里选节点。订阅链接只保存在本机。",
        "arguments-version: 1",
        "arguments:",
    ]
    for a, arg, label in AIRPORTS:
        st += [f"  {arg}:", "    type: input", f"    title: {q(label + ' 订阅链接')}",
               f"    description: {q('填该机场 Stash 或 Clash 格式的订阅链接。暂时没有时先填其他机场的链接，不要留空或乱填，否则这个机场的小组会变成直连。')}",
               "    required: true", "    min-length: 8", "    max-length: 4096"]
    st += ["", "proxy-providers:"]
    for a, arg, _ in AIRPORTS:
        st += [f"  {q(a)}:", f"    url: '${{args.{arg}}}'", "    interval: 86400"]
    st += ["", "proxy-groups:"] + groups_yaml("lazy")
    st += ["", "rule-providers:"] + rule_providers_yaml(False)
    st += ["", "rules:"] + rules_yaml()
    STASH_OUT.parent.mkdir(exist_ok=True)
    STASH_OUT.write_text("\n".join(st) + "\n", encoding="utf-8")

    cp = [
        "# Generated by tools/fill_and_verify.py. Do not edit the copy in the repository by hand.",
        "# Clash Party (mihomo) YAML override: adds the Sensitive / AI / Honor-of-Kings groups and rules on top",
        "# of an airport subscription. Before use, replace each PASTE_..._HERE with that airport's",
        "# Clash/mihomo subscription link IN YOUR LOCAL COPY ONLY. Never put the links back into the repository.",
        "# A provider that fails to load leaves its sub-group empty, which mihomo treats like a direct connection.",
        "",
        "proxy-providers:",
    ]
    for a, arg, _ in AIRPORTS:
        cp += [f"  {q(a)}:", "    type: http", f"    url: {q('PASTE_' + a.upper() + '_SUBSCRIPTION_LINK_HERE')}", "    interval: 86400",
               "    health-check:", "      enable: true", "      url: https://www.gstatic.com/generate_204",
               "      interval: 600", "      lazy: true"]
    cp += ["", "+proxy-groups:"] + groups_yaml(None)
    cp += ["", "rule-providers:"] + rule_providers_yaml(True)
    cp += ["", "+rules:"] + rules_yaml()
    PARTY_OUT.parent.mkdir(exist_ok=True)
    PARTY_OUT.write_text("\n".join(cp) + "\n", encoding="utf-8")
    print(f"[OK] wrote {STASH_OUT.relative_to(ROOT)} and {PARTY_OUT.relative_to(ROOT)}")


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
    write_clash_yaml()
    write_overrides()
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
            yn = fn.replace(".list", ".yaml")
            yurl = f"{base}/clash/{yn}"
            try:
                with urllib.request.urlopen(yurl, timeout=20) as r:
                    yremote = r.read().decode("utf-8")
            except Exception as e:
                print(f"[FAIL] fetch {yurl}: {e}"); ok = False; continue
            if yremote == (CLASH_DIR / yn).read_text(encoding="utf-8"):
                print(f"[OK] {yurl} matches local file")
            else:
                print(f"[FAIL] {yurl} differs from local file (retry after cache expires)"); ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
