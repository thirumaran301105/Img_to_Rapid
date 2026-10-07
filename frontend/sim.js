// 3D simulation driven by the robot's real link lengths and joint limits (see backend/kinematics.py).
// Links are drawn as simple tubes, not ABB's CAD meshes.
window.RobotSim = (function () {
  const UP = new THREE.Vector3(0, 1, 0);
  let S = null, raf = 0;
  const P = v => new THREE.Vector3(v[0], v[2], -v[1]);        // base frame (Z up) -> three.js (Y up)

  function setLink(m, a, b) {
    const d = b.clone().sub(a), l = Math.max(d.length(), 1e-3);
    m.position.copy(a).addScaledVector(d, .5);
    m.quaternion.setFromUnitVectors(UP, d.divideScalar(l));
    m.scale.y = l;
  }

  // ---- optional CAD parts: one or more STL/GLB files per link (slot 0 = base, 1..6 = links) ----
  let CAD = null;                       // { id, parts: {slot: Group}, frame }
  const LINK_COLORS = [0x2b3138, 0x2b3138, 0xff6a13, 0xff6a13, 0xdfe3e7, 0xff6a13, 0x2b3138];
  const slotOf = name => {
    const s = name.toLowerCase().replace(/\.[^.]+$/, '');
    const k = s.match(/(?:link|axis|joint|j)[_ -]?([0-6])/) || s.match(/^([0-6])$/);
    return k ? +k[1] : (/base|foot|pedestal/.test(s) ? 0 : -1);
  };
  async function parse(name, buf, scale) {
    const ext = name.split('.').pop().toLowerCase();
    if (ext === 'stl') { const geo = new THREE.STLLoader().parse(buf); geo.scale(scale, scale, scale); return new THREE.Mesh(geo); }
    if (ext === 'glb' || ext === 'gltf') {
      const gltf = await new Promise((ok, no) => new THREE.GLTFLoader().parse(buf, '', ok, no));
      gltf.scene.scale.setScalar(scale); return gltf.scene;
    }
    throw new Error('Unsupported file: ' + name);
  }
  // files: [{name, buf}]. frame 'assembly' = parts exported in the robot's zero pose; 'link' = each part in its joint frame.
  async function loadCad(id, files, { scale = 1, frame = 'assembly' } = {}) {
    const parts = {}, skipped = [];
    for (const { name, buf } of files) {
      const k = slotOf(name);
      if (k < 0) { skipped.push(name); continue; }
      try {
        const o = await parse(name, buf, scale);
        if (o.isMesh) o.material = new THREE.MeshLambertMaterial({ color: LINK_COLORS[k] });
        (parts[k] || (parts[k] = Object.assign(new THREE.Group(), { matrixAutoUpdate: false }))).add(o);
      } catch (e) { skipped.push(name + ' (unreadable)'); }
    }
    CAD = Object.keys(parts).length ? { id, parts, frame } : null;
    const found = Object.keys(parts).map(Number).sort();
    return { found, missing: [0, 1, 2, 3, 4, 5, 6].filter(k => !(k in parts)), skipped };
  }
  // Link frames in the base frame (Z up). All axes are parallel to the base at zero pose, origins at the joints.
  function frames(m, q) {
    const tr = (x, y, z) => new THREE.Matrix4().makeTranslation(x, y, z);
    const rx = a => new THREE.Matrix4().makeRotationX(a), ry = a => new THREE.Matrix4().makeRotationY(a), rz = a => new THREE.Matrix4().makeRotationZ(a);
    const T1 = rz(q[0]);
    const T2 = T1.clone().multiply(tr(m.a1, 0, m.d1)).multiply(ry(q[1]));
    const T3 = T2.clone().multiply(tr(0, 0, m.a2)).multiply(ry(q[2]));
    const T4 = T3.clone().multiply(tr(m.d4, 0, m.a3)).multiply(rx(q[3]));
    const T5 = T4.clone().multiply(ry(q[4]));
    const T6 = T5.clone().multiply(rx(q[5])).multiply(tr(m.d6, 0, 0));
    return [new THREE.Matrix4(), T1, T2, T3, T4, T5, T6];
  }

  function ensure(el) {
    if (S) return S;
    const W = el.clientWidth, H = Math.round(W * 0.62);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(W, H); renderer.setPixelRatio(devicePixelRatio); renderer.setClearColor(0xdfe3e7);
    el.innerHTML = ''; el.appendChild(renderer.domElement);
    const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(40, W / H, 1, 30000);
    scene.add(new THREE.AmbientLight(0xffffff, .75));
    const dl = new THREE.DirectionalLight(0xffffff, .6); dl.position.set(1, 2, 1); scene.add(dl);
    S = { renderer, scene, cam, az: .9, pol: .95, dist: 1000, target: new THREE.Vector3(), homeTarget: new THREE.Vector3(), group: null, reach: 1000 };
    let drag = null; const cv = renderer.domElement;
    cv.style.cssText = 'width:100%;display:block;touch-action:none;cursor:grab';
    cv.oncontextmenu = e => e.preventDefault();
    cv.onpointerdown = e => {
      drag = { x: e.clientX, y: e.clientY, pan: e.button === 2 || e.shiftKey };
      cv.style.cursor = drag.pan ? 'move' : 'grabbing';
      cv.setPointerCapture(e.pointerId);
    };
    cv.onpointerup = () => { drag = null; cv.style.cursor = 'grab'; };
    cv.onpointermove = e => {
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (drag.pan) {
        const scale = S.dist / Math.max(1, cv.clientHeight) * 1.7;
        S.target.x -= (Math.cos(S.az) * dx) * scale;
        S.target.z -= (Math.sin(S.az) * dx) * scale;
        S.target.y += dy * scale;
      } else {
        S.az -= dx * .008;
        S.pol = Math.min(1.5, Math.max(.2, S.pol - dy * .008));
      }
      drag.x = e.clientX; drag.y = e.clientY; render();
    };
    cv.onwheel = e => {
      e.preventDefault();
      S.dist = Math.min(S.reach * 8, Math.max(S.reach * .35, S.dist * (e.deltaY > 0 ? 1.08 : .92)));
      render();
    };
    cv.ondblclick = () => resetView();
    new ResizeObserver(() => {
      const w = el.clientWidth, h = Math.max(1, Math.round(w * .62));
      renderer.setSize(w, h, false);
      cam.aspect = w / h;
      cam.updateProjectionMatrix();
      render();
    }).observe(el);
    return S;
  }

  function resetView() {
    if (!S) return;
    S.az = .9; S.pol = .95; S.dist = S.reach * 2.4;
    S.target.copy(S.homeTarget);
    render();
  }

  function render() {
    const { cam, target, az, pol, dist, renderer, scene } = S;
    cam.position.set(target.x + dist * Math.sin(pol) * Math.sin(az), target.y + dist * Math.cos(pol), target.z + dist * Math.sin(pol) * Math.cos(az));
    cam.lookAt(target); renderer.render(scene, cam);
  }

  function run(el, robot, job, cb) {
    cancelAnimationFrame(raf); ensure(el);
    if (S.group) S.scene.remove(S.group);
    const g = S.group = new THREE.Group(); S.scene.add(g);

    const mo = job.motion || {}, m = robot.kin, pen = mo.pen_len || robot.pen_len, reach = robot.reach_mm;
    S.reach = reach;
    const { w, h } = job.area, up = mo.dz_up ?? robot.pen_up, down = mo.dz_draw ?? robot.pen_down;
    const fr = job.frame || { origin: robot.wobj, ex: [1, 0, 0], ey: [0, 1, 0], ez: [0, 0, 1] };
    const O = fr.origin, EX = fr.ex, EY = fr.ey, EZ = fr.ez;    // page (x, y, height above paper) -> robot base frame
    const place = (x, y, dz) => [0, 1, 2].map(i => O[i] + x * EX[i] + y * EY[i] + dz * EZ[i]);
    const mArm = new THREE.MeshLambertMaterial({ color: 0xff6a13 }), mDark = new THREE.MeshLambertMaterial({ color: 0x2b3138 });
    const cyl = (r, mat) => { const x = new THREE.Mesh(new THREE.CylinderGeometry(r, r, 1, 16), mat); g.add(x); return x; };
    const ball = (r, mat) => { const x = new THREE.Mesh(new THREE.SphereGeometry(r, 16, 12), mat); g.add(x); return x; };
    const rA = reach * .04;
    const base = cyl(reach * .07, mDark), shoulder = cyl(rA * 1.1, mDark), upper = cyl(rA, mArm);
    const fore1 = cyl(rA * .85, mArm), fore2 = cyl(rA * .85, mArm), wrist = cyl(rA * .6, mDark), tool = cyl(3, mDark);
    const jS = ball(rA * 1.25, mDark), jE = ball(rA * 1.1, mDark), jW = ball(rA * .8, mDark);
    const tip = ball(5, new THREE.MeshBasicMaterial({ color: 0xd9111c }));
    setLink(base, P([0, 0, 0]), P([0, 0, m.d1]));
    const tubes = [base, shoulder, upper, fore1, fore2, wrist, jS, jE, jW];
    const useCad = !!(CAD && CAD.id === robot.id);
    let inv0 = null;
    if (useCad) {
      const rob = new THREE.Group(); rob.rotation.x = -Math.PI / 2; g.add(rob);   // Z-up robot frame -> three.js Y-up
      for (const k in CAD.parts) rob.add(CAD.parts[k]);
      tubes.forEach(t => t.visible = false);
      if (CAD.frame === 'assembly') inv0 = frames(m, [0, 0, 0, 0, 0, 0]).map(T => T.clone().invert());
    }
    g.add(new THREE.GridHelper(reach * 3, 12, 0x9aa6b2, 0xc3cad1));
    const paper = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide }));
    const pc = place(w / 2, h / 2, .3), rootZ = new THREE.Group(); rootZ.rotation.x = -Math.PI / 2; g.add(rootZ);
    paper.matrixAutoUpdate = false;
    paper.matrix.makeBasis(new THREE.Vector3(...EX), new THREE.Vector3(...EY), new THREE.Vector3(...EZ)).setPosition(pc[0], pc[1], pc[2]);
    rootZ.add(paper);

    // waypoints in the base frame; seg i runs from wp[i-1] to wp[i]
    const f = place;
    const wp = [f(w / 2, h / 2, up + 60)], pdown = [false];
    for (const s of job.strokes) {
      wp.push(f(s[0][0], s[0][1], up)); pdown.push(false);
      wp.push(f(s[0][0], s[0][1], down)); pdown.push(false);
      for (let i = 1; i < s.length; i++) { wp.push(f(s[i][0], s[i][1], down)); pdown.push(true); }
      const e = s[s.length - 1]; wp.push(f(e[0], e[1], up)); pdown.push(false);
    }
    wp.push(f(w / 2, h / 2, up + 60)); pdown.push(false);

    const len = wp.map((p, i) => i ? Math.hypot(p[0] - wp[i-1][0], p[1] - wp[i-1][1], p[2] - wp[i-1][2]) : 0);
    const slot = []; let nSlots = 0; pdown.forEach((d, i) => { if (d) nSlots++; slot[i] = nSlots; });
    const trail = new Float32Array(Math.max(1, nSlots) * 6), tg = new THREE.BufferGeometry();
    tg.setAttribute('position', new THREE.BufferAttribute(trail, 3)); tg.setDrawRange(0, 0);
    g.add(new THREE.LineSegments(tg, new THREE.LineBasicMaterial({ color: 0x17202b })));

    function pose(p) {
      const { q, ok } = Kin.ik(m, p, pen), k = Kin.fk(m, q, pen);
      setLink(shoulder, P([0, 0, m.d1]), P(k.J2)); setLink(upper, P(k.J2), P(k.J3));
      setLink(fore1, P(k.J3), P(k.C)); setLink(fore2, P(k.C), P(k.W));
      setLink(wrist, P(k.W), P(k.F)); setLink(tool, P(k.F), P(k.T));
      if (useCad) {
        const T = frames(m, q);
        for (const i in CAD.parts) { const M = T[i].clone(); if (inv0) M.multiply(inv0[i]); CAD.parts[i].matrix.copy(M); CAD.parts[i].matrixWorldNeedsUpdate = true; }
      }
      jS.position.copy(P(k.J2)); jE.position.copy(P(k.J3)); jW.position.copy(P(k.W)); tip.position.copy(P(k.T));
      return { q, ok };
    }

    // pre-scan: reach and joint limits over the whole path
    const bad = new Set(); let outOfReach = false;
    wp.forEach(p => { const r = Kin.ik(m, p, pen); if (!r.ok) outOfReach = true; Kin.violations(m, r.q).forEach(j => bad.add(j)); });
    cb.onCheck && cb.onCheck({ outOfReach, limits: [...bad].sort() });

    S.homeTarget.copy(P(place(w / 2, h / 2, 50)));
    S.target.copy(S.homeTarget); S.dist = reach * 2.4;
    pose(wp[0]); render();

    const total = len.reduce((a, b) => a + b, 0), speed = Math.max(300, total / 30);
    let i = 1, segT = 0, last = performance.now();
    const posAt = (i, t) => { const a = wp[i - 1], b = wp[i], u = len[i] ? t / len[i] : 1; return a.map((v, k) => v + (b[k] - v) * u); };
    const wr3 = (n, a, b) => { const A = P(a), B = P(b); A.y += .6; B.y += .6; trail.set([A.x, A.y, A.z, B.x, B.y, B.z], n * 6); };
    function frame(now) {
      let budget = speed * Math.min(.05, (now - last) / 1000); last = now;
      while (budget > 0 && i < wp.length) {
        const remain = len[i] - segT;
        if (budget >= remain) { if (pdown[i]) wr3(slot[i] - 1, wp[i - 1], wp[i]); budget -= remain; i++; segT = 0; }
        else { segT += budget; budget = 0; }
      }
      const done = i >= wp.length, cur = done ? wp[wp.length - 1] : posAt(i, segT);
      if (!done && pdown[i]) wr3(slot[i] - 1, wp[i - 1], cur);
      tg.setDrawRange(0, (done ? nSlots : slot[i]) * 2); tg.attributes.position.needsUpdate = true;
      const r = pose(cur); render();
      cb.onJoints && cb.onJoints(r.q.map(a => a * 180 / Math.PI));
      if (done) { cb.onDone && cb.onDone(); return; }
      raf = requestAnimationFrame(frame);
    }
    raf = requestAnimationFrame(frame);
  }
  return { run, loadCad, hasCad: id => !!(CAD && CAD.id === id), resetView };
})();
