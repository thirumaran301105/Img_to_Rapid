// Same maths as backend/kinematics.py (keep the two in step). Base frame is Z up, lengths in mm, angles in radians.
(function (root) {
  const Ry = (v, t) => [v[0] * Math.cos(t) + v[2] * Math.sin(t), v[1], -v[0] * Math.sin(t) + v[2] * Math.cos(t)];
  const Rz = (v, t) => [v[0] * Math.cos(t) - v[1] * Math.sin(t), v[0] * Math.sin(t) + v[1] * Math.cos(t), v[2]];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const R = (v, q1, t) => Rz(Ry(v, t), q1);

  // Elbow-up joints that put the pen tip at p with the tool pointing straight down. Wrist yaw held constant (q6 = q1).
  function ik(m, p, pen) {
    const wx = p[0], wy = p[1], wz = p[2] + pen + m.d6, q1 = Math.atan2(wy, wx);
    const r = Math.hypot(wx, wy) - m.a1, zp = wz - m.d1, L3 = Math.hypot(m.d4, m.a3), delta = Math.atan2(m.d4, m.a3);
    const c = (r * r + zp * zp - m.a2 * m.a2 - L3 * L3) / (2 * m.a2 * L3), ok = Math.abs(c) <= 1;
    const g = Math.acos(Math.max(-1, Math.min(1, c)));
    const q2 = Math.atan2(r, zp) - Math.atan2(L3 * Math.sin(g), m.a2 + L3 * Math.cos(g)), q3 = g - delta;
    return { q: [q1, q2, q3, 0, Math.PI / 2 - (q2 + q3), q1], ok };
  }

  // Joint positions in the base frame: J2, J3, elbow corner C, wrist centre W, flange F, pen tip T.
  function fk(m, q, pen) {
    const th = q[1] + q[2], J2 = Rz([m.a1, 0, m.d1], q[0]), J3 = add(J2, R([0, 0, m.a2], q[0], q[1]));
    const C = add(J3, R([0, 0, m.a3], q[0], th)), W = add(J3, R([m.d4, 0, m.a3], q[0], th));
    const F = add(W, R([m.d6, 0, 0], q[0], th + q[4])), T = add(F, R([pen, 0, 0], q[0], th + q[4]));
    return { J2, J3, C, W, F, T };
  }

  // Names of joints outside their limits (limits in degrees).
  const violations = (m, q) => q.map((a, i) => [i, a * 180 / Math.PI]).filter(([i, d]) => d < m.limits[i][0] || d > m.limits[i][1]).map(([i]) => 'J' + (i + 1));

  const api = { ik, fk, violations };
  if (typeof module !== 'undefined') module.exports = api; else root.Kin = api;
})(typeof window !== 'undefined' ? window : globalThis);
