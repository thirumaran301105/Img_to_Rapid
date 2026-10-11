"""Strokes (mm on the page) -> ABB RAPID module, using the resolved job settings (see job_settings.py)."""
from datetime import datetime

from job_settings import PREDEFINED_SPEEDS

LINES_PER_PROC = 120
ZERO_EAX = "[9E9,9E9,9E9,9E9,9E9,9E9]"


def _g(v):
    return f"{v:.8g}".replace("e", "E")      # RAPID writes exponents with a capital E


def _speed(name, v, ori, decls):
    """Predefined name (v80) when it exists, otherwise declare a CONST speeddata."""
    if float(v).is_integer() and int(v) in PREDEFINED_SPEEDS:
        return f"v{int(v)}"
    decls.append(f"  CONST speeddata {name}:=[{_g(v)},{ori},5000,1000];")
    return name


def generate_module(ops, cfg):
    (ox, oy), (rx, ry), (ux, uy) = cfg["place"]["origin"], cfg["place"]["right"], cfg["place"]["up"]
    zu, zd = cfg["z_up_w"], cfg["z_draw_w"]
    tool, wobj = cfg["tool"]["name"], cfg["wobj"]["name"]
    tail = f",{tool}\\WObj:={wobj};"
    zone = cfg["zone"]
    q = ",".join(_g(v) for v in cfg["tool_quat"])
    cf = ",".join(str(c) for c in cfg["conf"])
    decls = []
    vD = _speed("vDraw", cfg["draw_speed"], 100, decls)
    vA = _speed("vApproach", cfg["approach_speed"], 100, decls)
    vT = _speed("vTravel", cfg["travel_speed"], 200, decls)

    def T(x, y, z):          # inline robtarget (no Offs call: much cheaper for the controller to evaluate)
        return f"[[{ox + x * rx + y * ux:.2f},{oy + x * ry + y * uy:.2f},{z:.2f}],[{q}],[{cf}],{ZERO_EAX}]"

    lines = []
    for op in ops:
        x0, y0 = op["start"]
        lines.append(f"MoveL {T(x0, y0, zu)},{vT},z5{tail}")
        lines.append(f"MoveL {T(x0, y0, zd)},{vA},{zone}{tail}")
        last = len(op["segs"]) - 1
        for j, sg in enumerate(op["segs"]):
            z = "fine" if j == last else zone
            if sg[0] == "L":
                lines.append(f"MoveL {T(sg[1][0], sg[1][1], zd)},{vD},{z}{tail}")
            else:
                lines.append(f"MoveC {T(sg[1][0], sg[1][1], zd)},{T(sg[2][0], sg[2][1], zd)},{vD},{z}{tail}")
        xe, ye = op["segs"][-1][-1]
        lines.append(f"MoveL {T(xe, ye, zu)},{vA},z5{tail}")

    chunks = [lines[i:i + LINES_PER_PROC] for i in range(0, len(lines), LINES_PER_PROC)]
    on = "On" if cfg["strict"] else "Off"
    up_dir = "-Z" if cfg["uz"] < 0 else "+Z"
    out = [
        "MODULE ImageDraw",
        f"  ! Generated {datetime.now():%Y-%m-%d %H:%M} for {cfg['robot_name']}: {len(ops)} strokes, "
        f"{sum(len(o['segs']) for o in ops)} line/arc moves",
        f"  ! Page {cfg['page_w']:g} x {cfg['page_h']:g} mm. Work object {wobj}: Z points {'DOWN' if cfg['uz'] < 0 else 'up'},"
        f" so pen-up is {up_dir} and the tool uses orientation [{q}].",
    ]
    if cfg["declare"]:
        tx, ty, tz = cfg["tool"]["xyz"]
        tq = ",".join(_g(v) for v in cfg["tool_decl_quat"])
        wx, wy, wz = cfg["wobj"]["pos"]
        wq = ",".join(_g(v) for v in cfg["wobj"]["quat"])
        out += [f"  PERS tooldata {tool}:=[TRUE,[[{_g(tx)},{_g(ty)},{_g(tz)}],[{tq}]],[0.3,[0,0,{_g(tz / 2)}],[1,0,0,0],0,0,0]];",
                f"  PERS wobjdata {wobj}:=[FALSE,TRUE,\"\",[[{_g(wx)},{_g(wy)},{_g(wz)}],[{wq}]],[[0,0,0],[1,0,0,0]]];"]
    else:
        out.append(f"  ! Uses the tool '{tool}' and work object '{wobj}' that already exist on the controller.")
    hj = cfg["home_joints"]
    if not cfg["home_routine"] and hj:
        out.append(f"  CONST jointtarget jHome:=[[{','.join(_g(a) for a in hj)}],{ZERO_EAX}];")
    out += decls + ["", f"  PROC {cfg['routine']}()", "    SingArea\\Wrist;", f"    ConfL\\{on};", f"    ConfJ\\{on};"]
    home = ([f"    {cfg['home_routine']};"] if cfg["home_routine"]
            else [f"    MoveAbsJ jHome\\NoEOffs,{vT},fine,{tool};"] if hj else [])
    out += home + [f"    DrawPart{i};" for i in range(1, len(chunks) + 1)] + home + ["  ENDPROC", ""]
    for i, ch in enumerate(chunks, 1):
        out += [f"  PROC DrawPart{i}()"] + [f"    {l}" for l in ch] + ["  ENDPROC", ""]
    out.append("ENDMODULE")
    return "\n".join(out)
