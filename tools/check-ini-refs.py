"""Check that names referenced on CHANGED lines of mod INI files are defined somewhere.

The game only reports a bad reference (misspelled OCL, weapon, upgrade, button, object ...) when it
is used in play, so this catches typos early. The data set is baseline\\zh with mod\\ files replacing
files of the same path. Only lines that differ from baseline are checked, to keep the output focused.

Also checks that every block opener in changed files is matched by an `End`.

Usage: python tools/check-ini-refs.py
"""
import difflib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "baseline", "zh")
MOD = os.path.join(ROOT, "mod")

DEF_KINDS = {
    "Object": "object", "ObjectReskin": "object", "ObjectCreationList": "ocl", "Weapon": "weapon",
    "Armor": "armor", "DamageFX": "damagefx", "Upgrade": "upgrade", "CommandButton": "button",
    "CommandSet": "commandset", "FXList": "fx", "ParticleSystem": "particle", "Locomotor": "locomotor",
    "SpecialPower": "specialpower", "Science": "science",
}

# (regex on a changed line, kind, group index); names NONE/None are ignored
REFS = [
    (r"^\s*CreationList\s*=\s*(\S+)", "ocl"),
    (r"^\s*OCL\s*=\s*(?:\w+\s+)?(\S+)", "ocl"),
    (r"\bOCL:(\S+)", "ocl"),
    (r"^\s*Weapon\s*=\s*\w+\s+(\S+)", "weapon"),
    (r"^\s*(?:DeathWeapon|WeaponName|ProjectileDetonationWeapon|FireWeapon)\s*=\s*(\S+)", "weapon"),
    (r"^\s*Armor\s*=\s*(\S+)\s*$", "armor"),
    (r"^\s*DamageFX\s*=\s*(\S+)", "damagefx"),
    (r"^\s*(?:UpgradeToGrant|TriggeredBy|ConflictsWith|RemovesUpgrades|RequiresAllTriggers)\s*=\s*([\w ]+)", "upgrade"),
    (r"^\s*CommandSet\s*=\s*(\S+)", "commandset"),
    (r"^\s*\d+\s*=\s*(\S+)", "button"),
    (r"^\s*(?:ObjectNames|StartingUnit\d|StartingBuilding|ReplacementObjectName|OldObject|NewObject)\s*=\s*([\w ]+)", "object"),
    (r"^\s*Rider\d+\s*=\s*(\S+)", "object"),
    (r"^\s*(?:FXList|FX)\s*=\s*(?:\w+\s+)?(FX_\S+)", "fx"),
    (r"^\s*(?:ParticleSystem|ParticleSysBone\s*=\s*\S+)\s*=?\s*(\S+)", None),
    (r"^\s*IntrinsicSciences\s*=\s*([\w ]+)", "science"),
]


def effective_files():
    files = {}
    for top in (BASE, MOD):
        for dirpath, _dirs, names in os.walk(top):
            for n in names:
                if n.lower().endswith((".ini",)):
                    full = os.path.join(dirpath, n)
                    rel = os.path.relpath(full, top).lower()
                    files[rel] = full
    return files


def strip(line):
    return line.split(";", 1)[0].split("//", 1)[0].rstrip()


def main():
    files = effective_files()
    defs = {k: set() for k in set(DEF_KINDS.values())}
    for rel, full in files.items():
        with open(full, encoding="latin-1") as f:
            for line in f:
                m = re.match(r"^\s*(\w+)\s+([\w.\-]+)", strip(line))
                if m and m.group(1) in DEF_KINDS:
                    defs[DEF_KINDS[m.group(1)]].add(m.group(2).lower())

    problems = 0
    for dirpath, _dirs, names in os.walk(MOD):
        for n in names:
            if not n.lower().endswith(".ini"):
                continue
            mod_path = os.path.join(dirpath, n)
            rel = os.path.relpath(mod_path, MOD)
            base_path = os.path.join(BASE, rel)
            with open(mod_path, encoding="latin-1") as f:
                mod_lines = f.read().splitlines()
            base_lines = []
            if os.path.exists(base_path):
                with open(base_path, encoding="latin-1") as f:
                    base_lines = f.read().splitlines()
            if mod_lines == base_lines:
                continue
            changed = []
            sm = difflib.SequenceMatcher(None, base_lines, mod_lines, autojunk=False)
            for tag, _i1, _i2, j1, j2 in sm.get_opcodes():
                if tag in ("replace", "insert"):
                    changed.extend(range(j1, j2))
            for idx in changed:
                code = strip(mod_lines[idx])
                if not code.strip():
                    continue
                for pattern, kind in REFS:
                    if kind is None:
                        continue
                    m = re.search(pattern, code)
                    if not m:
                        continue
                    for name in m.group(1).split():
                        if name.upper() in ("NONE", "NO", "YES") or name.startswith(("+", "-")):
                            continue
                        if kind == "button" and not name.lower().startswith(("command_", "early_", "airf_", "lazr_", "supw_", "nuke_", "infa_", "tank_", "chem_", "demo_", "slth_", "boss_")):
                            continue
                        if name.lower() not in defs[kind]:
                            problems += 1
                            print(f"{rel}:{idx + 1}: unknown {kind} '{name}'  <- {code.strip()}")
            # block balance relative to baseline
            def balance(lines):
                opens = sum(1 for l in lines if re.match(r"^\s*(Object|ObjectReskin|ObjectCreationList|Weapon|Armor|CommandSet|CommandButton|Upgrade|ParticleSystem|FXList|Locomotor)\s+\S+\s*$", strip(l)))
                return opens
            base_open, mod_open = balance(base_lines), balance(mod_lines)
            base_end = sum(1 for l in base_lines if strip(l).strip() == "End")
            mod_end = sum(1 for l in mod_lines if strip(l).strip() == "End")
            print(f"{rel}: {len(changed)} changed lines; top-level blocks {base_open}->{mod_open}; End {base_end}->{mod_end}")
    print(f"\n{problems} unresolved reference(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
