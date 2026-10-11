"""Minimal ABB Robot Web Services client (written for RWS 1.0 / RobotWare 6, HTTP + digest auth).

NOT verified against a real controller. All endpoint paths are collected in EP below: check each
one against the RWS reference for YOUR RobotWare version (RobotWare 7 uses HTTPS and basic auth,
and some paths differ) and edit them here. Fallback that always works: download the .mod file and
load it from RobotStudio or the FlexPendant.
"""
import requests
from requests.auth import HTTPDigestAuth

EP = {
    "mastership_request": "/rw/mastership?action=request",
    "mastership_release": "/rw/mastership?action=release",
    "upload": "/fileservice/$temp/{name}",
    "load_module": "/rw/rapid/tasks/{task}?action=loadmod",
    "set_pp_routine": "/rw/rapid/tasks/{task}/pcp?action=set-pp-routine",
    "motors_on": "/rw/panel/ctrlstate?action=setctrlstate",
    "start": "/rw/rapid/execution?action=start",
    "stop": "/rw/rapid/execution?action=stop",
}


class RWSError(Exception):
    pass


class RWSClient:
    def __init__(self, host, port=80, task="T_ROB1", user="Default User", password="robotics", https=False):
        self.base = f"{'https' if https else 'http'}://{host}:{port}"
        self.task = task
        self.s = requests.Session()
        self.s.auth = HTTPDigestAuth(user, password)
        self.s.verify = False

    def _call(self, method, key, data=None, **fmt):
        url = self.base + EP[key].format(task=self.task, **fmt)
        try:
            r = self.s.request(method, url, data=data, timeout=10)
        except requests.RequestException as e:
            raise RWSError(f"Cannot reach the controller at {self.base}: {e}")
        if r.status_code >= 300:
            raise RWSError(f"{key} failed ({r.status_code}): {r.text[:200]}")
        return r

    def send_program(self, rapid_code):
        self._call("POST", "mastership_request")
        try:
            self._call("PUT", "upload", data=rapid_code.encode(), name="ImageDraw.mod")
            self._call("POST", "load_module", data={"modulepath": "$temp/ImageDraw.mod", "replace": "true"})
            self._call("POST", "set_pp_routine", data={"routine": "DrawImage", "module": "ImageDraw"})
        finally:
            self._call("POST", "mastership_release")

    def start(self):
        self._call("POST", "motors_on", data={"ctrl-state": "motoron"})
        self._call("POST", "start", data={"regain": "continue", "execmode": "continue", "cycle": "once",
                                          "condition": "none", "stopatbp": "disabled", "alltaskbytsp": "false"})

    def stop(self):
        self._call("POST", "stop", data={"stopmode": "stop", "usetsp": "normal"})
