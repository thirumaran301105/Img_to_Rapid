"""Turns the page's settings (and RAPID lines pasted from your own program) into one resolved job configuration.

Why this exists: a work object's Z axis can point UP or DOWN, and everything depends on it:
  - the tool must point at the paper (tool Z = -wobj Z if Z is up, = wobj Z if Z is down)
  - 'pen up' is +Z in the work object when Z is up, but -Z when Z is down (otherwise the pen lifts INTO the table)
  - the page is mirrored if the handedness is ignored
"""
import json
import math
import re

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
PREDEFINED_SPEEDS = {5, 10, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300, 400, 500, 600, 800, 1000,
                     1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000}
ZONES = ("z0", "z1", "z5", "z10", "fine")
OUR_NAMES = {"pOrigin", "tPen", "wPaper"}          # lines written by this program: never read them back
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,31}$")


# ---------------------------------------------------------------- quaternions [w, x, y, z] (RAPID order q1..q4)
def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def qmat(q):
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
    w, x, y, z = w / n, x / n, y / n, z / n
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def qconj(q):
    return (q[0], -q[1], -q[2], -q[3])


def qnorm(q):
    n = math.sqrt(sum(v * v for v in q)) or 1.0
    q = [v / n for v in q]
    return tuple(-v for v in q) if q[0] < 0 else tuple(q)


def qz(deg):
    a = math.radians(deg) / 2
    return (math.cos(a), 0.0, 0.0, math.sin(a))


def mv(R, v):
    return [sum(R[i][j] * v[j] for j in range(3)) for i in range(3)]


# ---------------------------------------------------------------- reading values pasted from RAPID
def _nums(s):
    return [float(x) for x in re.findall(NUM, s)]


def parse_paste(text):
    """Reads PERS tooldata, PERS wobjdata and CONST robtarget lines (commented or not)."""
    out = {}
    for raw in str(text).splitlines():
        line = raw.strip().lstrip("!").strip()
        m = re.search(r"\b(tooldata|wobjdata|robtarget)\s+(\w+)\s*:?=\s*(.*)", line, re.I)
        if not m:
            continue
        kind, name, body = m.group(1).lower(), m.group(2), re.sub(r'"[^"]*"', "", m.group(3))
        n = _nums(body)
        if name in OUR_NAMES or kind in out:
            continue
        if kind == "tooldata" and len(n) >= 7:
            out["tool"] = {"name": name, "xyz": n[0:3], "quat": n[3:7]}
        elif kind == "wobjdata" and len(n) >= 7:
            out["wobj"] = {"name": name, "pos": n[0:3], "quat": n[3:7],
                           "oframe_used": len(n) >= 14 and any(abs(v) > 1e-6 for v in n[7:10])}
        elif kind == "robtarget" and len(n) >= 11:
            out["target"] = {"name": name, "quat": n[3:7], "conf": [int(round(v)) for v in n[7:11]]}
    return out


# ---------------------------------------------------------------- helpers for the raw settings
def _num(raw, key, default, lo, hi):
    try:
        v = float(str(raw.get(key, "")).strip())
    except ValueError:
        v = float(default)
    return min(max(v, lo), hi)


def _name(raw, key, default):
    s = str(raw.get(key, "") or "").strip()
    return s if NAME_RE.match(s) else default


def _list(raw, key, n, default):
    s = str(raw.get(key, "")).strip()
    if key in raw and s == "":
        return None                                   # explicitly blank
    try:
        v = [float(x) for x in re.split(r"[,\s]+", s) if x != ""]
        return v if len(v) == n else default
    except ValueError:
        return default


def parse_settings(text):
    try:
        raw = json.loads(text or "{}")
    except ValueError:
        raise ValueError("The settings could not be read.")
    return raw if isinstance(raw, dict) else {}


# ---------------------------------------------------------------- the resolver
def resolve_job(robot, raw):
    warn, notes = [], []
    paste = parse_paste(raw.get("paste", ""))

    page_w = _num(raw, "page_w", robot.area_w, 20, 3000)
    page_h = _num(raw, "page_h", robot.area_h, 20, 3000)
    margin = _num(raw, "margin", 5, 0, min(page_w, page_h) / 3)

    # work object
    if "wobj" in paste:
        w = paste["wobj"]
        wpos, wquat, wname, wpasted = w["pos"], w["quat"], w["name"], True
        if w["oframe_used"]:
            warn.append("The work object has an object-frame offset (oframe). The reach check and 3D view ignore it.")
    else:
        wpos, wquat, wname, wpasted = list(robot.wobj[:3]), list(robot.wobj[3:]), "wPaper", False
    wname = _name(raw, "wobj_name", wname)
    Rw = qmat(wquat)
    uz = 1 if Rw[2][2] >= 0 else -1                   # +1: wobj Z points up (away from the table), -1: down
    if abs(Rw[2][2]) < 0.99:
        warn.append("The work object is tilted. The reach check and 3D view assume the paper is horizontal.")

    # tool
    if "tool" in paste:
        t = paste["tool"]
        txyz, tquat, tname, tpasted = t["xyz"], t["quat"], t["name"], True
    else:
        txyz, tquat, tname, tpasted = [0.0, 0.0, robot.pen_len], [1, 0, 0, 0], "tPen", False
    tname = _name(raw, "tool_name", tname)
    pen_len = _num(raw, "pen_len", txyz[2], 1, 2000) if str(raw.get("pen_len", "")).strip() else txyz[2]
    if pen_len != txyz[2]:
        txyz = [txyz[0], txyz[1], pen_len]

    mode = str(raw.get("declare", "auto"))
    declare = (not (tpasted or wpasted)) if mode == "auto" else mode == "declare"

    # where the page sits on the work object
    right = {"+X": (1, 0), "-X": (-1, 0), "+Y": (0, 1), "-Y": (0, -1)}.get(str(raw.get("right", "+X")), (1, 0))
    up = (-right[1], right[0]) if uz > 0 else (right[1], -right[0])   # viewed from above; Z down flips the handedness
    ox, oy = _num(raw, "ox", 0, -5000, 5000), _num(raw, "oy", 0, -5000, 5000)

    # tool orientation: tool Z must point at the paper. A taught target shows an orientation the robot can really reach
    # (including its rotation about the tool Z axis), so use it when pasted. It may be given in the base frame or
    # in the work object: take the one whose tool direction points at the paper, then convert it to work-object
    # coordinates because robtarget orientations follow the active \WObj frame.
    yaw = int(_num(raw, "tool_yaw", 0, 0, 359) // 90 * 90)
    base_q, src = ((1, 0, 0, 0) if uz < 0 else (0, 1, 0, 0)), None
    if "target" in paste:
        tq, tname_t = tuple(paste["target"]["quat"]), paste["target"]["name"]
        cands = {"wobj": tq, "base": qmul(qconj(wquat), tq)}
        want = str(raw.get("target_frame", "auto"))
        for frame_name in (["wobj", "base"] if want == "auto" else [want if want in cands else "wobj"]):
            if qmat(qmul(wquat, cands[frame_name]))[2][2] < -0.9:        # tool Z (in base) points down
                base_q, src = qnorm(cands[frame_name]), frame_name
                break
        if src is None:
            warn.append(f"The tool direction of your taught target {tname_t} does not point at the paper in either frame, "
                        "so the default direction is used.")
    # RAPID robtarget orientations are interpreted in the active work-object
    # frame, just like their position coordinates. Convert the desired
    # base-frame orientation before writing targets.
    tool_base_quat = qnorm(qmul(base_q, qz(yaw)))
    tool_quat = qnorm(qmul(qconj(wquat), tool_base_quat))

    # heights, always measured away from the paper, then signed for the work object's Z
    pen_up = _num(raw, "pen_up", robot.pen_up, 1, 200)
    press = _num(raw, "press", 0, 0, 20)
    dry = _num(raw, "dry", 0, 0, 200)
    if dry:
        pen_up = max(pen_up, dry + 5)
    dz_up, dz_draw = pen_up, (dry if dry else (-press if press else 0.0))

    # axis configuration
    conf = _list(raw, "conf", 4, None) or paste.get("target", {}).get("conf") or [0, 0, 0, 0]
    conf = [int(c) for c in conf]

    # frame for the reach check and the 3D view (base frame, page -> base)
    ex = mv(Rw, [right[0], right[1], 0])
    ey = mv(Rw, [up[0], up[1], 0])
    ez = [ex[1] * ey[2] - ex[2] * ey[1], ex[2] * ey[0] - ex[0] * ey[2], ex[0] * ey[1] - ex[1] * ey[0]]
    org = [a + b for a, b in zip(wpos, mv(Rw, [ox, oy, 0]))]
    if ez[2] < 0.5:
        warn.append("The page normal does not point up. Check the work object.")

    notes.append(f"Work object {wname}: Z points {'up' if uz > 0 else 'DOWN'}"
                 + (", read from your RAPID." if wpasted else ", taken from config.py (not pasted)."))
    notes.append(f"Tool {tname}: length {pen_len:.1f} mm" + (", read from your RAPID." if tpasted else "."))
    if src:
        notes.append(f"Tool orientation taken from your taught target {paste['target']['name']} "
                     f"(read as given {'in the work object' if src == 'wobj' else 'in the base frame'}).")
    if not declare:
        notes.append(f"{tname} and {wname} must already exist on the controller.")

    home = _list(raw, "home_joints", 6, list(robot.home_joints))
    return {
        "robot_name": robot.name, "page_w": page_w, "page_h": page_h, "margin": margin,
        "tool": {"name": tname, "xyz": txyz, "quat": tquat if not tpasted else tquat},
        "tool_decl_quat": paste["tool"]["quat"] if tpasted else [1, 0, 0, 0],
        "wobj": {"name": wname, "pos": wpos, "quat": wquat}, "declare": declare, "uz": uz,
        "place": {"origin": [ox, oy], "right": list(right), "up": list(up)},
        "tool_quat": list(tool_quat), "conf": conf, "strict": bool(raw.get("strict", False)),
        "draw_speed": _num(raw, "draw_speed", robot.draw_speed, 1, 1500),
        "travel_speed": _num(raw, "travel_speed", robot.travel_speed, 1, 1500),
        "approach_speed": _num(raw, "approach_speed", robot.approach_speed, 1, 1500),
        "zone": raw.get("zone") if raw.get("zone") in ZONES else "z0",
        "dz_up": dz_up, "dz_draw": dz_draw, "z_up_w": uz * dz_up + 0.0, "z_draw_w": uz * dz_draw + 0.0,
        "tol_mm": (_num(raw, "tol", 0, 0.02, 2) if str(raw.get("tol", "")).strip() else None),
        "rate": _num(raw, "rate", 40, 5, 500),
        "pen_len": pen_len, "routine": _name(raw, "routine", "DrawImage"),
        "home_routine": _name(raw, "home_routine", "") if str(raw.get("home_routine", "")).strip() else "",
        "home_joints": home,
        "frame": {"origin": org, "ex": ex, "ey": ey, "ez": ez},
        "warnings": warn, "notes": notes,
    }
