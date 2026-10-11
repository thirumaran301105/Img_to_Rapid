Drop this robot's CAD parts here and restart nothing: reload the page and press Simulate robot.

File names (STL or GLB; several files per link are fine, e.g. link3_cover.stl):
  base.stl, link1.stl, link2.stl, link3.stl, link4.stl, link5.stl, link6.stl
  link1 = turns with joint 1 (the column), link2 = upper arm, link3 = forearm,
  link4/5/6 = the three wrist links, link6 includes the flange.

Optional robot.json next to them:
  { "frame": "assembly", "scale": 1 }
  frame "assembly": parts exported from the CAD assembly in the robot's zero pose (all joints 0) - the usual case.
  frame "link":     each part is modelled in its own joint frame, origin at the joint, axes parallel to the base.
  scale 1 = millimetres, 1000 = metres.

Zero pose = upper arm vertical, forearm horizontal pointing forward (+X), flange facing +X.
