"""Read and clone top-level blocks of Generals / Zero Hour INI data.

The effective data set is baseline\\zh with files in mod\\ replacing the same paths, so clones start
from our bug-fixed data. A top-level block is `<Type> <Name>` ... `End`; nested blocks (modules,
WeaponSet, ArmorSet, Prerequisites, ConditionState ...) are tracked by depth so the matching `End`
is found exactly.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "baseline", "zh")
MOD = os.path.join(ROOT, "mod")

TOP_TYPES = {
    "Object", "ObjectReskin", "Weapon", "ObjectCreationList", "SpecialPower", "Science", "Upgrade",
    "CommandButton", "CommandSet", "Locomotor", "Armor", "DamageFX", "FXList", "ParticleSystem",
    "PlayerTemplate", "MappedImage", "AudioEvent", "MultiplayerColor", "Rank", "CrateData",
}
# Keys of `Key = value` lines that open a nested block.
NESTED_KEYS = {
    "Behavior", "Draw", "Body", "ClientUpdate", "ConditionState", "TransitionState", "ArmorUpgrade",
    "ClientBehavior",
}
# Bare keywords that open a nested block.
NESTED_WORDS = {
    "WeaponSet", "ArmorSet", "Prerequisites", "UnitSpecificSounds", "UnitSpecificFX", "Turret",
    "AltTurret", "DefaultConditionState", "CreateObject", "CreateDebris", "DeliverPayload",
    "FireWeapon", "Attack", "ApplyRandomForce", "FireSecondaryWeapon", "Nugget", "DeliveryDecal",
    "DelayedNugget", "WeaponNugget", "AttackNugget", "DamageNugget", "ParalyzeNugget",
    "SpawnAndFadeNugget", "FireWeaponNugget", "CursorText", "BeaconRadiusDecal", "LaserBeamUpdate",
    "SoundEffects", "Sound", "ParticleSystem", "FXListAtBonePos", "TracerFX", "LightPulse",
    "ViewShake", "TerrainScorch", "BuffNugget", "DamageFieldNugget", "HealNugget",
    "OCLNugget", "ProjectileNugget", "DOTNugget", "MetaImpactNugget", "Sequential",
}


def code_part(line):
    return line.split(";", 1)[0].split("//", 1)[0].strip()


def is_nested_open(code):
    if not code or code == "End":
        return False
    if "=" in code:
        key = code.split("=", 1)[0].strip()
        return key in NESTED_KEYS
    word = code.split()[0]
    return word in NESTED_WORDS


def effective_ini_files():
    """{relative path (lower) -> absolute path} for every .ini in the effective data set."""
    files = {}
    for top in (BASE, MOD):
        for dirpath, _dirs, names in os.walk(top):
            for n in names:
                if n.lower().endswith(".ini"):
                    full = os.path.join(dirpath, n)
                    files[os.path.relpath(full, top).lower()] = full
    return files


def parse_blocks(text):
    """Yield (type, name, start_line, end_line_inclusive) for top-level blocks in INI text lines."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        code = code_part(lines[i])
        parts = code.split()
        if parts and parts[0] in TOP_TYPES and len(parts) >= 2 and "=" not in code:
            btype, name = parts[0], parts[1]
            depth = 0
            j = i + 1
            while j < len(lines):
                c = code_part(lines[j])
                if c == "End" or c.startswith("End ") or c.lower() == "end":
                    if depth == 0:
                        break
                    depth -= 1
                elif is_nested_open(c):
                    depth += 1
                j += 1
            yield btype, name, i, j
            i = j + 1
        else:
            i += 1


class Index:
    """Index of all top-level blocks in the effective data set."""

    def __init__(self):
        self.blocks = {}  # (type, lower name) -> (file, text)
        self.files = effective_ini_files()
        for rel, full in self.files.items():
            with open(full, encoding="latin-1", newline="") as f:
                text = f.read()
            lines = text.splitlines()
            for btype, name, s, e in parse_blocks(text):
                key = (btype, name.lower())
                self.blocks.setdefault(key, (rel, "\r\n".join(lines[s:e + 1])))

    def get(self, btype, name):
        hit = self.blocks.get((btype, name.lower()))
        if hit is None:
            raise KeyError(f"{btype} {name} not found in retail/mod data")
        return hit[1]

    def has(self, btype, name):
        return (btype, name.lower()) in self.blocks


# ------------------------------------------------------------------------------------------------
# Block editing. A block is handled as a list of lines; depth 1 = directly inside the top block.

def _lines(text):
    return text.splitlines()


def _depth_map(lines):
    """Depth of each line (0 for the header and the final End)."""
    depths = []
    depth = 0
    for idx, line in enumerate(lines):
        c = code_part(line)
        if idx == 0:
            depths.append(0)
            depth = 1
            continue
        if c.lower() == "end" or c.startswith("End "):
            depth -= 1
            depths.append(depth)
            continue
        depths.append(depth)
        if is_nested_open(c):
            depth += 1
    return depths


def _sub_blocks(lines, depths, opener_test):
    """Spans [start, end] of depth-1 nested blocks whose opener line satisfies opener_test."""
    spans = []
    i = 1
    while i < len(lines) - 1:
        c = code_part(lines[i])
        if depths[i] == 1 and is_nested_open(c) and opener_test(c):
            j = i + 1
            while j < len(lines) and not (depths[j] == 1 and code_part(lines[j]).lower() in ("end",) or (depths[j] == 1 and code_part(lines[j]).startswith("End "))):
                j += 1
            spans.append((i, j))
            i = j + 1
        else:
            i += 1
    return spans


def rename(text, old, new):
    """Rename the top-level block header."""
    lines = _lines(text)
    lines[0] = re.sub(r"^(\s*\w+\s+)" + re.escape(old) + r"\b", r"\g<1>" + new, lines[0])
    return "\r\n".join(lines)


def replace_tokens(text, mapping):
    """Whole-token replacement of names (object, upgrade, weapon ... names) in code parts."""
    if not mapping:
        return text
    pattern = re.compile(r"(?<![\w])(" + "|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True)) + r")(?![\w])")
    out = []
    for line in _lines(text):
        code, sep, comment = line.partition(";")
        out.append(pattern.sub(lambda m: mapping[m.group(1)], code) + sep + comment)
    return "\r\n".join(out)


def set_fields(text, fields, indent="  "):
    """Set depth-1 `Key = value` fields; replace existing (first occurrence) or insert before End."""
    lines = _lines(text)
    depths = _depth_map(lines)
    for key, value in fields.items():
        done = False
        for i in range(1, len(lines) - 1):
            c = code_part(lines[i])
            if depths[i] == 1 and "=" in c and c.split("=", 1)[0].strip() == key and not is_nested_open(c):
                lines[i] = f"{indent}{key} = {value} ; Reforged"
                done = True
                break
        if not done:
            lines.insert(len(lines) - 1, f"{indent}{key} = {value} ; Reforged")
            depths.insert(len(depths) - 1, 1)
    return "\r\n".join(lines)


def remove_fields(text, keys):
    lines = _lines(text)
    depths = _depth_map(lines)
    keep = [l for i, l in enumerate(lines)
            if not (0 < i < len(lines) - 1 and depths[i] == 1 and "=" in code_part(l)
                    and code_part(l).split("=", 1)[0].strip() in keys and not is_nested_open(code_part(l)))]
    return "\r\n".join(keep)


def replace_nested(text, word, new_blocks):
    """Replace all depth-1 nested blocks opened by `word` (e.g. WeaponSet) with new_blocks (raw text).

    The new text is inserted where the first old block was (or before End if there was none).
    """
    lines = _lines(text)
    depths = _depth_map(lines)
    spans = _sub_blocks(lines, depths, lambda c: c.split()[0] == word)
    insert_at = spans[0][0] if spans else len(lines) - 1
    for s, e in reversed(spans):
        del lines[s:e + 1]
        if s < insert_at:
            insert_at -= (e - s + 1)
    new_lines = _lines(new_blocks) if new_blocks else []
    lines[insert_at:insert_at] = new_lines
    return "\r\n".join(lines)


def remove_modules(text, module_types=(), module_tags=()):
    """Remove depth-1 module blocks (Behavior/Draw/Body = <Type> <Tag>) by type or tag."""
    lines = _lines(text)
    depths = _depth_map(lines)

    def test(c):
        if "=" not in c:
            return False
        key, rest = c.split("=", 1)
        parts = rest.split()
        if key.strip() not in ("Behavior", "Draw", "Body", "ClientUpdate", "ClientBehavior") or not parts:
            return False
        return parts[0] in module_types or (len(parts) > 1 and parts[1] in module_tags)

    for s, e in reversed(_sub_blocks(lines, depths, test)):
        del lines[s:e + 1]
    return "\r\n".join(lines)


def set_module_fields(text, module_key_type, fields):
    """Set `Key = value` lines inside depth-1 modules whose opener matches, e.g. ('Body', None)."""
    lines = _lines(text)
    depths = _depth_map(lines)
    want_key, want_type = module_key_type

    def test(c):
        if "=" not in c:
            return False
        key, rest = c.split("=", 1)
        parts = rest.split()
        return key.strip() == want_key and (want_type is None or (parts and parts[0] == want_type))

    for s, e in _sub_blocks(lines, depths, test):
        for key, value in fields.items():
            for i in range(s + 1, e):
                c = code_part(lines[i])
                if "=" in c and c.split("=", 1)[0].strip() == key:
                    lead = re.match(r"^\s*", lines[i]).group(0)
                    lines[i] = f"{lead}{key} = {value} ; Reforged"
                    break
    return "\r\n".join(lines)


def add_before_end(text, raw):
    lines = _lines(text)
    lines[len(lines) - 1:len(lines) - 1] = _lines(raw)
    return "\r\n".join(lines)


def balance_ok(text):
    lines = _lines(text)
    depths = _depth_map(lines)
    return depths[-1] == 0 and code_part(lines[-1]).lower() == "end"
