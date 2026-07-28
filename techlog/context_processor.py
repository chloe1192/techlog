from datetime import datetime, timezone
from .models import Airframe, Company, Operator
from django.shortcuts import get_object_or_404
from techlog.services import airframe_service


def airframe_processor(request):
    # TODO temp before permission mgmt
    print("----------------------------------------------------------------------------------------")
    request.session['airframe'] = request.resolver_match.kwargs.get("airframe_id")

    airframe_id = request.session.get('airframe')

    if not airframe_id:
        return {}

    try:
        airframe = airframe_service.get_airframe(request, airframe_id)
        company = airframe.operator.company
        operator = airframe.operator
        current_flight = airframe_service.get_current_flight(request, airframe_id)
        airframe_defects = airframe_service.get_airframe_defects(request, airframe_id)
        defect_actions = airframe_service.get_defect_actions(request, airframe_id)
        fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)
        departure_fluids = airframe_service.get_departure_fluids(request, airframe_id)
        arrival_fluids = airframe_service.get_arrival_fluids(request, airframe_id)
    except Exception:
        # API/client hiccup shouldn't break unrelated pages that happen
        # to share this context processor. Views that truly need this
        # data can still fetch it directly and let the error surface.
        return {}

    return {
        'airframe': airframe,
        'company': company,
        'operator': operator,
        'current_flight': current_flight,
        'airframe_defects': airframe_defects,
        'defect_actions': defect_actions,
        'fluid_tanks': fluid_tanks,
        'departure_fluids': departure_fluids,
        'arrival_fluids': arrival_fluids,
    }

def datetime_processor(request):
    """Provide the current datetime to template context."""
    now = datetime.now()
    now_utc = datetime.now(timezone.utc)
    # TODO update everytime a post is sent
    last_sync = datetime.now()

    return {
        'current_date_zulu': now_utc.date(),
        'current_time_local': now.time(),
        'current_time_zulu': now_utc.time(),
    }
