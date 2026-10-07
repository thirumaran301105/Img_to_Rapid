import json
import pathlib
import types
import uuid

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import LIVE, ROBOTS
from curve_fit import lines_to_ops
from image_to_paths import build_paths, path_stats
from job_settings import parse_settings, resolve_job
from kinematics import check_reach
from rapid_generator import generate_module
from rws_client import RWSClient, RWSError

BASE = pathlib.Path(__file__).parent
JOBS_DIR = BASE / "jobs"
JOBS_DIR.mkdir(exist_ok=True)
JOBS = {}
CAD_DIR = BASE.parent / "frontend" / "robots"


def cad_manifest(robot_id):
    """CAD parts dropped into frontend/robots/<robot id>/ (see the README in that folder)."""
    d = CAD_DIR / robot_id
    if not d.is_dir():
        return None
    files = {f.name: f"/robots/{robot_id}/{f.name}" for f in sorted(d.iterdir())
             if f.suffix.lower() in (".stl", ".glb", ".gltf")}
    if not files:
        return None
    cfg = {}
    if (d / "robot.json").exists():
        try:
            cfg = json.loads((d / "robot.json").read_text())
        except ValueError:
            pass
    return {"files": files, "scale": cfg.get("scale", 1), "frame": cfg.get("frame", "assembly")}
app = FastAPI(title="ABB image plotter")


class StartBody(BaseModel):
    confirm: bool = False


def _job(job_id):
    if job_id not in JOBS:
        raise HTTPException(404, "Unknown job. Preview the image again.")
    return JOBS[job_id]


def _client(robot):
    return RWSClient(robot.host, robot.port, robot.task)


@app.get("/api/robots")
def robots():
    return [{**r.public(), "cad": cad_manifest(r.id)} for r in ROBOTS.values()]


def _robot(robot_id):
    robot = ROBOTS.get(robot_id)
    if not robot:
        raise HTTPException(404, "Unknown robot.")
    return robot


def _cfg(robot, settings):
    try:
        return resolve_job(robot, parse_settings(settings))
    except ValueError as e:
        raise HTTPException(422, str(e))


def _make_job(robot, cfg, mm, ops, box, info):
    rapid = generate_module(ops, cfg)
    job_id = uuid.uuid4().hex[:8]
    (JOBS_DIR / f"{job_id}.mod").write_text(rapid)
    JOBS[job_id] = {"robot": robot, "rapid": rapid}
    speeds = types.SimpleNamespace(draw_speed=cfg["draw_speed"], travel_speed=cfg["travel_speed"])
    st = path_stats(mm, speeds)
    n_moves = sum(len(o["segs"]) for o in ops)
    avg = st["draw_mm"] / max(1, n_moves)
    limit = cfg["rate"] * avg                                   # speed the controller can sustain at this move length
    eff = min(cfg["draw_speed"], limit)
    st.update({"moves": n_moves, "avg_move_mm": round(avg, 2), "controller_limit": round(limit),
               "est_seconds": round(st["draw_mm"] / eff + st["travel_mm"] / cfg["travel_speed"] + len(ops) * 0.8)})
    return {"job_id": job_id, "area": {"w": cfg["page_w"], "h": cfg["page_h"]},
            "strokes": [s.tolist() for s in mm], "stats": st, "box": box, "info": info,
            "reach": check_reach(mm, robot, cfg), "frame": cfg["frame"],
            "motion": {"pen_len": cfg["pen_len"], "dz_up": cfg["dz_up"], "dz_draw": cfg["dz_draw"]},
            "warnings": cfg["warnings"], "notes": cfg["notes"], "live": LIVE}


@app.post("/api/preview")
async def preview(image: UploadFile = File(...), robot_id: str = Form(...), mode: str = Form("lines"),
                  detail: float = Form(0.5), pen_mm: float = Form(0.6), settings: str = Form("{}")):
    robot = _robot(robot_id)
    data = await image.read()
    if len(data) > 15_000_000:
        raise HTTPException(413, "Image is larger than 15 MB.")
    cfg = _cfg(robot, settings)
    try:
        mm, ops, box, info = build_paths(data, cfg["page_w"], cfg["page_h"], mode, detail, pen_mm,
                                         margin=cfg["margin"], tol_mm=cfg["tol_mm"])
    except ValueError as e:
        raise HTTPException(422, str(e))
    return _make_job(robot, cfg, mm, ops, box, info)


@app.post("/api/test-pattern")
def test_pattern(robot_id: str = Form(...), settings: str = Form("{}")):
    """A page border and a letter F: shows at a glance whether the drawing is mirrored, rotated or misplaced."""
    robot = _robot(robot_id)
    cfg = _cfg(robot, settings)
    w, h, m = cfg["page_w"], cfg["page_h"], cfg["margin"]
    x0, y0, s = m + 0.1 * (w - 2 * m), m + 0.1 * (h - 2 * m), min(w - 2 * m, h - 2 * m) * 0.7
    mm = [np.array(p, float).round(2) for p in (
        [[m, m], [w - m, m], [w - m, h - m], [m, h - m], [m, m]],
        [[x0, y0], [x0, y0 + s], [x0 + .55 * s, y0 + s]],
        [[x0, y0 + .55 * s], [x0 + .4 * s, y0 + .55 * s]])]
    return _make_job(robot, cfg, mm, lines_to_ops(mm), None, {"tol_mm": 0})


@app.get("/api/jobs/{job_id}/program.mod")
def download(job_id: str):
    _job(job_id)
    return FileResponse(JOBS_DIR / f"{job_id}.mod", filename="ImageDraw.mod")


@app.post("/api/jobs/{job_id}/send")
def send(job_id: str):
    job = _job(job_id)
    if not LIVE:
        return {"message": "Dry run: nothing was sent. Download the .mod file, or start the server with ROBOT_LIVE=1."}
    try:
        _client(job["robot"]).send_program(job["rapid"])
    except RWSError as e:
        raise HTTPException(502, str(e))
    return {"message": f"Program loaded on {job['robot'].name}. Check the paper frame and pen, then start."}


@app.post("/api/jobs/{job_id}/start")
def start(job_id: str, body: StartBody):
    job = _job(job_id)
    if not body.confirm:
        raise HTTPException(400, "Start must be confirmed by the operator.")
    if not LIVE:
        return {"message": "Dry run: robot not started."}
    try:
        _client(job["robot"]).start()
    except RWSError as e:
        raise HTTPException(502, str(e))
    return {"message": "Drawing started."}


@app.post("/api/jobs/{job_id}/stop")
def stop(job_id: str):
    job = _job(job_id)
    if LIVE:
        try:
            _client(job["robot"]).stop()
        except RWSError as e:
            raise HTTPException(502, str(e))
    return {"message": "Stop sent." if LIVE else "Dry run: nothing running."}


app.mount("/", StaticFiles(directory=BASE.parent / "frontend", html=True), name="ui")
