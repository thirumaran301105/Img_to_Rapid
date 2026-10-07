# ABB image drawing robot

Upload an image on a web page, pick an ABB robot, preview the toolpath, and have the robot draw it.

```
Browser -> FastAPI -> OpenCV (image to strokes) -> order + scale to the chosen robot's paper area
        -> RAPID module (ImageDraw.mod) -> ABB Robot Web Services -> robot draws
```

## Simulation first, then the real robot
After previewing, press **Simulate robot**: a 3D arm in the browser draws the image on the paper. Drag to rotate, scroll to zoom. **Send to robot** stays locked until the simulation has finished once. The arm uses each robot's real link lengths and joint limits (`backend/kinematics.py`), solves the joint angles for every point, shows J1 to J6 live, and keeps **Send** locked if any point is out of reach or breaks a joint limit. The same check also runs on the server when you preview.

Robots in this project: **ABB IRB 1600-10/1.45** (10 kg, 1.45 m) and **ABB GoFa CRB 15000-5/0.95** (5 kg, 0.95 m). Add or remove robots in `backend/config.py`.

- IRB 1600-10/1.45 has an exact kinematic model (link lengths and datasheet joint limits, see `backend/kinematics.py`), so it can be simulated, reach-checked and sent.
- GoFa has an approximate browser visualization model whose pivot distances are matched to the supplied zero-pose CAD assembly. It can be simulated with its CAD assets, but sending is intentionally locked until the dimensions are calibrated against the actual robot.

### Using your own CAD models
Two ways, both optional:
1. **In the page:** under "Robot CAD", pick the files for the selected robot. They stay in your browser.
2. **Permanently:** copy them into `frontend/robots/<robot id>/` (`gofa_5_95`, `irb1600_10_145`). Each folder has a README.txt with the naming rules.

Name the files `base`, `link1` ... `link6` (STL or GLB; several files per link are fine). Export them from the ABB CAD download either as an assembly in the robot's zero pose (the default) or each in its own joint frame, and set the units. The 3D view then moves your real parts using the exact joint angles. Without CAD, simple tubes are drawn.

Limits of the simulation: only the elbow-up solution with the tool pointing straight down is modelled, and collisions with your cell are not checked. Confirm in RobotStudio before real hardware.

## Page, speed and RAPID settings (all in the page)
Open the four panels on the left: **Paper and placement** (page size, margin, which work object axis the page's left-to-right runs along, where its bottom-left corner is), **Tool and work object**, **Speed and pen**, and **Program** (routine name, home routine). Settings are remembered per robot in your browser.

**Paste your own RAPID.** Paste your `PERS tooldata ...`, `PERS wobjdata ...` and optionally a taught `CONST robtarget ...` into the Tool and work object panel. The program then uses your tool and work object names, reads the tool length, detects which way the work object's Z axis points, and does not redeclare them.

**Why this matters.** If a work object's Z axis points down (common when it is taught on a table), three things flip: the tool must point along +Z of the work object, "pen up" is -Z (otherwise the pen lifts into the table), and the page is mirrored unless the handedness is handled. This is now automatic when you paste the work object. Press **Test pattern** to draw a border and a letter F: if the F is mirrored or turned on the real paper, change "Page right runs along" or the tool yaw. Use **Dry run height** first so the pen stays in the air.

## Speed and accuracy
A drawing sent as thousands of tiny straight moves crawls on an ABB controller (it can only process so many instructions per second, so the robot runs far below the speed you set) and the curves come out faceted. The program now fits long straight lines (`MoveL`) and true circular arcs (`MoveC`) to the traced path, within the **Accuracy** tolerance (blank = a quarter of the pen width, about 0.15 mm). A typical drawing becomes a few hundred moves instead of thousands. Targets are written inline, with no `Offs` call, which the controller evaluates faster.

The page shows moves, average move length and a **controller limit** (moves per second x average move length). If that is below your draw speed, raise the Accuracy tolerance or lower the detail. The default of 40 moves per second is a rule of thumb: time one drawing on your robot and set **Controller moves per second** to what you actually see.

**Tool orientation.** If you paste a taught `CONST robtarget`, the tool orientation (including its rotation about the tool Z axis) is taken from it, read in whichever frame, base or work object, points the tool at the paper. This fixes the case where the generated targets were turned 180 degrees about Z compared with an orientation the robot can reach. "Extra tool yaw" rotates it further if a joint limit is still hit.

## Run it
```
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```
Open http://127.0.0.1:8000.

The server starts in **dry-run mode**: it builds the toolpath and the RAPID file, but sends nothing to a controller. Use "Download RAPID file" and load it in RobotStudio or on the FlexPendant. Set `ROBOT_LIVE=1` only when you are ready to talk to a controller.

## Test in RobotStudio first
1. Build a station with your robot, a pen tool, and a flat surface for the paper.
2. Run the virtual controller (RWS is on 127.0.0.1:80 by default).
3. Load the generated `ImageDraw.mod`, set the program pointer to `DrawImage`, and run it in simulation.
4. When it draws correctly, repeat with `ROBOT_LIVE=1` against the virtual controller to test the web flow.

## Calibrate before using a real robot (edit `backend/config.py`)
- `wobj`: the paper frame. Teach a user frame on the paper (3 points) and copy the values.
- `pen_len`: flange to pen tip distance. Better: define the real tooldata on the robot.
- `area_w`, `area_h`: keep the paper area well inside the robot's reach.
- `home_joints`: make sure the home pose is collision-free in your cell.
- `host`: controller IP per robot (or set `IRB1200_HOST=192.168.x.x` etc.).
- Use a spring-loaded pen holder, and start with a low `draw_speed`.

## Files
- `backend/image_to_paths.py`: image to strokes, ordering, scaling to mm, bounds check
- `backend/rapid_generator.py`: strokes to RAPID (`MoveL` with `Offs` in the paper frame)
- `backend/rws_client.py`: upload, load, motors on, start, stop over RWS
- `backend/config.py`: robot catalogue
- `frontend/index.html`: upload, robot picker, preview, replay, send/start/stop

## Known limits
- The RWS endpoint paths in `rws_client.py` were not tested against a real controller. Check them against the RWS reference for your RobotWare version (RW7 uses HTTPS and different auth).
- Robot values in `config.py` are placeholders, not measured.
- Output is line art only (no shading or hatching), and arcs are approximated by short straight moves.
- Jobs are kept in memory, and there is no login. Do not expose this server beyond a trusted network.
