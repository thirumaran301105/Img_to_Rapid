"""Robot catalogue. EVERY number here is a placeholder: measure your own cell and edit.

wobj  = paper frame relative to the robot base: (x, y, z, q1, q2, q3, q4), mm + quaternion.
        Teach it on the real robot (3-point user frame) and copy the values here.
pen_len = distance from the tool flange to the pen tip along tool Z, mm.
area_w/area_h = usable drawing area on the paper, mm (must be inside the robot's reach).
"""
import os
from dataclasses import dataclass

from kinematics import MODELS

# Safe by default: nothing is sent to a controller unless you start the server with ROBOT_LIVE=1.
LIVE = os.getenv("ROBOT_LIVE") == "1"


@dataclass
class Robot:
    id: str
    name: str
    reach_mm: int
    area_w: float
    area_h: float
    wobj: tuple
    pen_len: float = 120.0
    pen_up: float = 6.0       # clearance above paper while travelling, mm (a small lift = much less time)
    pen_down: float = 0.0     # Z in the paper frame while drawing (use a spring-loaded pen holder)
    draw_speed: int = 40      # mm/s
    travel_speed: int = 250   # mm/s
    approach_speed: int = 60  # mm/s, pen touch-down and lift
    home_joints: tuple = (0, 0, 0, 0, 30, 0)   # CHECK this is collision-free in your cell
    host: str = "127.0.0.1"   # 127.0.0.1 = RobotStudio virtual controller
    port: int = 80
    task: str = "T_ROB1"

    def public(self):
        model = MODELS.get(self.id)
        return {"id": self.id, "name": self.name, "reach_mm": self.reach_mm,
                "area_w": self.area_w, "area_h": self.area_h, "wobj": list(self.wobj[:3]),
                "pen_len": self.pen_len, "pen_up": self.pen_up, "pen_down": self.pen_down,
                "defaults": {"page_w": self.area_w, "page_h": self.area_h, "margin": 5, "draw_speed": self.draw_speed,
                             "travel_speed": self.travel_speed, "approach_speed": self.approach_speed,
                             "pen_up": self.pen_up, "pen_len": self.pen_len, "home_joints": list(self.home_joints)},
                "kin": model, "exact": model is not None,
                "verified": bool(model and model.get("verified", False))}


def _host(key):
    return os.getenv(f"{key.upper()}_HOST", "127.0.0.1")


ROBOTS = {r.id: r for r in [
    Robot("gofa_5_95", "ABB GoFa CRB 15000-5/0.95", 950, 250, 180, (350, -90, 0, 1, 0, 0, 0), host=_host("gofa")),
    Robot("irb1600_10_145", "ABB IRB 1600-10/1.45", 1450, 500, 350, (700, -175, 0, 1, 0, 0, 0), host=_host("irb1600")),
]}
