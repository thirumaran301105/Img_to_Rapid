"""Exact-geometry kinematic models for ABB 6-axis robots (spherical wrist, L-shaped forearm).

Zero pose (all joints 0): upper arm vertical, forearm horizontal pointing forward (+X), flange facing +X.
Joint 2 positive leans the arm forward, joint 3 positive lowers the forearm, joint 5 = 90 deg points the
tool straight down. Lengths in mm, limits in degrees.

  a1 = J2 axis offset from J1 axis    d1 = base to J2 axis height   a2 = upper arm
  a3 = forearm rise at the elbow      d4 = forearm length (forward) d6 = wrist centre to flange

"source" says how far each parameter set has been cross-checked. Add a robot by adding an entry here.
"""
import math

MODELS = {
    "irb1600_10_145": dict(
        a1=150, d1=486.5, a2=700, a3=0, d4=600, d6=65,
        limits=[(-180, 180), (-90, 150), (-245, 65), (-200, 200), (-115, 115), (-400, 400)],
        source="Joint limits from the ABB IRB 1600 datasheet (10/1.45). Link lengths from the IRB 1600 DH table "
               "(ARTE) with the 1.45 m upper arm: reach 150+700+600=1450 mm, and the 225 mm height difference to "
               "the 1.2 m variant (1294 vs 1069 mm) agrees.",
        verified=True,
    ),
    # GoFa geometry is used to animate the supplied CAD and check the drawing envelope.
    # These dimensions are an approximation of the 0.95 m reach variant; do not use
    # this model to release a program to hardware until the cell is calibrated.
    "gofa_5_95": dict(
        # Pivot distances matched to the supplied zero-pose STL assembly:
        # shoulder Z ~= 329, elbow Z ~= 757, wrist X ~= 424.
        a1=0, d1=329, a2=428, a3=0, d4=424, d6=50,
        limits=[(-180, 180), (-180, 180), (-225, 85), (-180, 180), (-180, 180), (-270, 270)],
        source="Approximate GoFa CRB 15000-5/0.95 geometry for browser visualization only.",
        verified=False,
    ),
}
JOINT_NAMES = ["J1", "J2", "J3", "J4", "J5", "J6"]


def ik_down(m, x, y, z, pen):
    """Elbow-up joint angles (radians) putting the pen tip at (x, y, z), robot base frame, tool pointing straight down.
    Wrist yaw is held constant (q6 = q1), which is what the controller does for a fixed tool orientation."""
    wx, wy, wz = x, y, z + pen + m["d6"]
    q1 = math.atan2(wy, wx)
    r = math.hypot(wx, wy) - m["a1"]
    zp = wz - m["d1"]
    L3 = math.hypot(m["d4"], m["a3"])
    delta = math.atan2(m["d4"], m["a3"])
    c = (r * r + zp * zp - m["a2"] ** 2 - L3 ** 2) / (2 * m["a2"] * L3)
    ok = abs(c) <= 1
    g = math.acos(max(-1.0, min(1.0, c)))
    q2 = math.atan2(r, zp) - math.atan2(L3 * math.sin(g), m["a2"] + L3 * math.cos(g))
    q3 = g - delta
    q5 = math.pi / 2 - (q2 + q3)
    return [q1, q2, q3, 0.0, q5, q1], ok


def check_reach(strokes, robot, cfg=None):
    """Check every pen-down and pen-up point against reach and joint limits. None = no model available.
    cfg (from job_settings.resolve_job) gives the page frame, tool length and heights."""
    m = MODELS.get(robot.id)
    if m is None:
        return None
    if cfg is None:
        fr = {"origin": list(robot.wobj[:3]), "ex": [1, 0, 0], "ey": [0, 1, 0], "ez": [0, 0, 1]}
        pen, dzs = robot.pen_len, (robot.pen_down, robot.pen_up)
    else:
        fr, pen, dzs = cfg["frame"], cfg["pen_len"], (cfg["dz_draw"], cfg["dz_up"])
    o, ex, ey, ez = fr["origin"], fr["ex"], fr["ey"], fr["ez"]
    reach_bad, limit_bad = 0, {}
    for dz in dzs:
        for s in strokes:
            for px, py in s:
                p = [o[i] + px * ex[i] + py * ey[i] + dz * ez[i] for i in range(3)]
                q, ok = ik_down(m, p[0], p[1], p[2], pen)
                if not ok:
                    reach_bad += 1
                    continue
                for j, (lo, hi) in enumerate(m["limits"]):
                    if not lo <= math.degrees(q[j]) <= hi:
                        limit_bad[JOINT_NAMES[j]] = limit_bad.get(JOINT_NAMES[j], 0) + 1
    issues = []
    if reach_bad:
        issues.append(f"{reach_bad} points are outside the robot's reach")
    issues += [f"{j} exceeds its limit at {n} points" for j, n in limit_bad.items()]
    return {"ok": not issues, "issues": issues}
