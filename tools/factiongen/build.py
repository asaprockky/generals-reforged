"""Build a Reforged faction from a spec in tools/factiongen/specs/<name>.py.

A spec clones retail blocks (objects, weapons, OCLs, upgrades, sciences, special powers, command buttons)
and edits them, so placeholder factions reuse retail art and behaviour with new names, stats and rosters.
Output: one file per block kind under mod/Data/INI/<Kind folder>/Reforged_<Side>.ini, plus string labels
in tools/factiongen/out/<Side>.strings.json (merged into generals.csf by merge_strings.py).

Spec module attributes (see specs/soviet.py for a worked example):
  SIDE      unique side name, e.g. "Soviet"
  FACTION   dict: display, template_clone, base_side, color, command_center, dozer,
            intrinsic_sciences (list), rank_sets {1: [...], 3: [...], 8: [...]}, shortcut_set (list of buttons),
            set (extra PlayerTemplate fields)
  TOKENS    dict of whole-token renames applied to every cloned block (e.g. retail upgrade -> new upgrade)
  BLOCKS    list of block dicts:
              kind (default "Object"), name, clone (retail block to copy) or raw (full text),
              tokens, set {field: value}, remove_fields [...], body {field: value},
              weapon_sets [ {conditions, weapons {SLOT: name}, extra [lines]} ] (replaces all WeaponSets),
              armor_sets [ {conditions, armor, damagefx} ] (replaces all ArmorSets),
              prerequisites [lines] (replaces the Prerequisites block; [] removes it),
              remove_modules [types], remove_tags [tags], add (raw text before End),
              display (in-game name), command_set (CommandSet name),
              button {type: UNIT_BUILD|DOZER_CONSTRUCT, label: "&Name", tooltip, image, clone}
  COMMAND_SETS  {name: {slot: button}}
  STRINGS   {label: text}

Usage: python tools/factiongen/build.py <spec name> [--dry-run]
"""
import importlib.util
import json
import os
import re
import sys

import inilib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
INI_ROOT = os.path.join(inilib.MOD, "Data", "INI")

KIND_FOLDER = {
    "Object": "Object", "Weapon": "Weapon", "ObjectCreationList": "ObjectCreationList",
    "Locomotor": "Locomotor", "SpecialPower": "SpecialPower", "Science": "Science", "Upgrade": "Upgrade",
    "CommandButton": "CommandButton", "CommandSet": "CommandSet", "PlayerTemplate": "PlayerTemplate",
    "Armor": "Armor", "FXList": "FXList",
}


class SpecError(Exception):
    pass


def load_spec(name):
    path = os.path.join(HERE, "specs", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"spec_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def weapon_set_text(ws):
    lines = ["  WeaponSet"]
    lines.append(f"    Conditions = {ws.get('conditions', 'None')}")
    for slot, weapon in ws.get("weapons", {}).items():
        lines.append(f"    Weapon = {slot} {weapon}")
    for extra in ws.get("extra", []):
        lines.append(f"    {extra}")
    lines.append("  End")
    return "\r\n".join(lines)


def armor_set_text(a):
    lines = ["  ArmorSet", f"    Conditions = {a.get('conditions', 'None')}", f"    Armor = {a['armor']}"]
    if a.get("damagefx"):
        lines.append(f"    DamageFX = {a['damagefx']}")
    lines.append("  End")
    return "\r\n".join(lines)


def build_block(idx, b, side, tokens, strings):
    kind = b.get("kind", "Object")
    name = b["name"]
    if "raw" in b:
        text = b["raw"].strip("\r\n").replace("\r\n", "\n").replace("\n", "\r\n")
    else:
        text = idx.get(kind, b["clone"])
        text = inilib.rename(text, b["clone"], name)
        if kind == "ObjectReskin":
            raise SpecError(f"{name}: clone a full Object, not an ObjectReskin")
        if text.splitlines()[0].split()[0] == "ObjectReskin":
            raise SpecError(f"{name}: source {b['clone']} is an ObjectReskin; clone its parent Object instead")
    merged = dict(tokens)
    merged.update(b.get("tokens", {}))
    text = inilib.replace_tokens(text, merged)
    if b.get("remove_modules") or b.get("remove_tags"):
        text = inilib.remove_modules(text, b.get("remove_modules", ()), b.get("remove_tags", ()))
    if b.get("remove_fields"):
        text = inilib.remove_fields(text, set(b["remove_fields"]))
    fields = dict(b.get("set", {}))
    if kind == "Object":
        fields.setdefault("Side", side)
        if "display" in b:
            fields["DisplayName"] = f"OBJECT:{name}"
            strings[f"OBJECT:{name}"] = b["display"]
        if "command_set" in b:
            fields["CommandSet"] = b["command_set"]
    if fields:
        text = inilib.set_fields(text, fields)
    if b.get("body"):
        text = inilib.set_module_fields(text, ("Body", None), b["body"])
    if b.get("weapon_sets") is not None:
        text = inilib.replace_nested(text, "WeaponSet", "\r\n".join(weapon_set_text(w) for w in b["weapon_sets"]))
    if b.get("armor_sets") is not None:
        text = inilib.replace_nested(text, "ArmorSet", "\r\n".join(armor_set_text(a) for a in b["armor_sets"]))
    if b.get("prerequisites") is not None:
        pre = ""
        if b["prerequisites"]:
            pre = "\r\n".join(["  Prerequisites"] + [f"    {l}" for l in b["prerequisites"]] + ["  End"])
        text = inilib.replace_nested(text, "Prerequisites", pre)
    if b.get("add"):
        text = inilib.add_before_end(text, b["add"].strip("\r\n").replace("\r\n", "\n").replace("\n", "\r\n"))
    if not inilib.balance_ok(text):
        raise SpecError(f"{kind} {name}: unbalanced block after edits")
    return kind, name, text


def build_button(idx, obj, side, strings):
    btn = obj["button"]
    name = f"Command_Construct{obj['name']}"
    clone = btn.get("clone")
    if not clone and obj.get("clone"):
        # find the retail button that builds the cloned object
        for (kind, lname), (_rel, text) in idx.blocks.items():
            if kind == "CommandButton" and re.search(r"^\s*Object\s*=\s*" + re.escape(obj["clone"]) + r"\s*$",
                                                     text, re.M | re.I):
                clone = text.splitlines()[0].split()[1]
                break
    if clone:
        text = inilib.rename(idx.get("CommandButton", clone), clone, name)
    else:
        text = "\r\n".join([f"CommandButton {name}", "  ButtonBorderType = BUILD", "End"])
    fields = {
        "Command": btn.get("type", "UNIT_BUILD"),
        "Object": obj["name"],
        "TextLabel": f"CONTROLBAR:Construct{obj['name']}",
        "DescriptLabel": f"CONTROLBAR:ToolTipBuild{obj['name']}",
    }
    if btn.get("image"):
        fields["ButtonImage"] = btn["image"]
    text = inilib.remove_fields(text, {"Upgrade", "Science", "SpecialPower"})
    text = inilib.set_fields(text, fields)
    strings[f"CONTROLBAR:Construct{obj['name']}"] = btn.get("label", obj.get("display", obj["name"]))
    strings[f"CONTROLBAR:ToolTipBuild{obj['name']}"] = btn.get("tooltip", "")
    return "CommandButton", name, text


def command_set_text(name, slots):
    lines = [f"CommandSet {name}"]
    for slot in sorted(slots, key=int):
        lines.append(f"  {int(slot)} = {slots[slot]}")
    lines.append("End")
    return "\r\n".join(lines)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    spec_name, dry = argv[0], "--dry-run" in argv
    spec = load_spec(spec_name)
    side = spec.SIDE
    fac = spec.FACTION
    tokens = getattr(spec, "TOKENS", {})
    idx = inilib.Index()
    strings = dict(getattr(spec, "STRINGS", {}))
    out = {}  # kind -> [(name, text)]

    def emit(kind, name, text):
        if any(n.lower() == name.lower() for n, _t in out.get(kind, [])):
            raise SpecError(f"duplicate generated {kind} {name}")
        if idx.has(kind, name) and not idx.blocks[(kind, name.lower())][0].startswith(f"data\\ini\\{KIND_FOLDER.get(kind, kind).lower()}\\reforged_"):
            raise SpecError(f"{kind} {name} already exists in retail data; choose a new name")
        out.setdefault(kind, []).append((name, text))

    for b in spec.BLOCKS:
        emit(*build_block(idx, b, side, tokens, strings))
        if b.get("kind", "Object") == "Object" and b.get("button"):
            emit(*build_button(idx, b, side, strings))

    sets = dict(getattr(spec, "COMMAND_SETS", {}))
    root_science = f"SCIENCE_{side.upper()}"
    rank = fac.get("rank_sets", {})
    for r in (1, 3, 8):
        sets.setdefault(f"SCIENCE_{side.upper()}_CommandSetRank{r}", {i + 1: btn for i, btn in enumerate(rank.get(r, []))})
    sets.setdefault(f"SpecialPowerShortcut{side}", {i + 1: btn for i, btn in enumerate(fac.get("shortcut_set", []))})
    for name, slots in sets.items():
        emit("CommandSet", name, command_set_text(name, slots))

    if not idx.has("Science", root_science) and not any(n == root_science for n, _ in out.get("Science", [])):
        # Same shape as the retail SCIENCE_CHINA root science.
        emit("Science", root_science, "\r\n".join([
            f"Science {root_science}", "  PrerequisiteSciences = None",
            "  SciencePurchasePointCost = 0  ; not purchasable", "  IsGrantable = No", "End"]))

    template = f"Faction{side}"
    pt = inilib.rename(idx.get("PlayerTemplate", fac["template_clone"]), fac["template_clone"], template)
    pt = inilib.remove_fields(pt, {"OldFaction"})
    pt_fields = {
        "Side": side, "BaseSide": fac["base_side"], "PlayableSide": "Yes",
        "PreferredColor": fac["color"],
        "IntrinsicSciences": " ".join([root_science] + fac.get("intrinsic_sciences", [])),
        "PurchaseScienceCommandSetRank1": f"SCIENCE_{side.upper()}_CommandSetRank1",
        "PurchaseScienceCommandSetRank3": f"SCIENCE_{side.upper()}_CommandSetRank3",
        "PurchaseScienceCommandSetRank8": f"SCIENCE_{side.upper()}_CommandSetRank8",
        "SpecialPowerShortcutCommandSet": f"SpecialPowerShortcut{side}",
        "DisplayName": f"INI:{template}",
        "StartingBuilding": fac["command_center"],
        "StartingUnit0": fac["dozer"],
    }
    pt_fields.update(fac.get("set", {}))
    pt = inilib.set_fields(pt, pt_fields)
    emit("PlayerTemplate", template, pt)
    strings[f"INI:{template}"] = fac["display"]
    strings[f"SIDE:{side}"] = fac["display"]

    # -------- validation of references between generated and retail blocks
    def exists(kind, name):
        return idx.has(kind, name) or any(n.lower() == name.lower() for n, _ in out.get(kind, []))

    problems = []
    for name, text in out.get("CommandSet", []):
        for m in re.finditer(r"^\s*\d+\s*=\s*(\S+)", text, re.M):
            if not exists("CommandButton", m.group(1)):
                problems.append(f"CommandSet {name}: unknown button {m.group(1)}")
    for kind in ("Object", "CommandButton", "SpecialPower"):
        for name, text in out.get(kind, []):
            for line in text.splitlines():
                code = inilib.code_part(line)
                for pat, rkind in ((r"^Weapon\s*=\s*\w+\s+(\S+)", "Weapon"), (r"^Object\s*=\s*(\S+)$", "Object"),
                                   (r"^CommandSet\s*=\s*(\S+)", "CommandSet"), (r"^Upgrade\s*=\s*(\S+)", "Upgrade"),
                                   (r"^(?:CreationList|OCL)\s*=\s*(?:\w+\s+)?(\S+)", "ObjectCreationList"),
                                   (r"^SpecialPowerTemplate\s*=\s*(\S+)", "SpecialPower"),
                                   (r"^Locomotor\s*=\s*\w+\s+(\S+)", "Locomotor")):
                    m = re.match(pat, code)
                    if m and m.group(1).upper() != "NONE" and not exists(rkind, m.group(1)):
                        problems.append(f"{kind} {name}: unknown {rkind} {m.group(1)}")
    for name in (fac["command_center"], fac["dozer"]):
        if not exists("Object", name):
            problems.append(f"FACTION: unknown object {name}")
    if problems:
        raise SpecError("reference problems:\n  " + "\n  ".join(problems))

    total = sum(len(v) for v in out.values())
    print(f"{side}: {total} blocks " + ", ".join(f"{k} {len(v)}" for k, v in sorted(out.items())) + f"; {len(strings)} strings")
    if dry:
        return 0
    for kind, items in out.items():
        folder = os.path.join(INI_ROOT, KIND_FOLDER[kind])
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"Reforged_{side}.ini")
        with open(path, "w", encoding="latin-1", newline="") as f:
            f.write(f"; Reforged faction {side} ({fac['display']}): generated by tools/factiongen/build.py from specs/{spec_name}.py. Do not edit by hand.\r\n\r\n")
            f.write("\r\n\r\n".join(text for _n, text in items) + "\r\n")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f"{side}.strings.json"), "w", encoding="utf-8") as f:
        json.dump(strings, f, ensure_ascii=False, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (SpecError, KeyError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)
