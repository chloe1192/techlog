"""AirframeDefect + Action data. Two side-effects that used to live in
Django model .save() overrides now happen here explicitly:
  - AirframeDefect: defect_title auto-fills from the linked Defect catalog entry.
  - Action: saving an action also updates its parent AirframeDefect.status.
"""

from techlog.api import TechlogClient
from techlog.mapping import from_api, from_api_many
from techlog.state import AirframeDefect, Action, Defect

client = TechlogClient()


def get_airframe_defects(airframe_id):
    return from_api_many(AirframeDefect, client.get(f"airframes/{airframe_id}/defects/"))


def get_airframe_defect(defect_id):
    return from_api(AirframeDefect, client.get(f"airframe_defects/{defect_id}/"))


def create_airframe_defect(payload):
    if payload.get("defect_id") and not payload.get("defect_title"):
        defect = from_api(Defect, client.get(f"defects/{payload['defect_id']}/"))
        if defect:
            payload["defect_title"] = defect.title
    return from_api(AirframeDefect, client.post("airframe_defects/", data=payload))


def update_airframe_defect(defect_id, payload):
    return from_api(AirframeDefect, client.put(f"airframe_defects/{defect_id}/", data=payload))


def get_actions_for_airframe(airframe_id):
    return from_api_many(Action, client.get(f"airframes/{airframe_id}/actions/"))


def get_actions_for_defect(defect_id):
    return from_api_many(Action, client.get(f"airframe_defects/{defect_id}/actions/"))


def get_action(action_id):
    return from_api(Action, client.get(f"actions/{action_id}/"))


def create_action(payload, airframe_defect_id):
    action = from_api(Action, client.post("actions/", data=payload))
    update_airframe_defect(airframe_defect_id, {"status": payload.get("status")})
    return action


def update_action(action_id, payload, airframe_defect_id):
    action = from_api(Action, client.put(f"actions/{action_id}/", data=payload))
    update_airframe_defect(airframe_defect_id, {"status": payload.get("status")})
    return action