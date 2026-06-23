from datetime import datetime, timezone

from .models import Airframe, Company, Operator
from django.shortcuts import get_object_or_404


def airframe_processor(request):
    airframe = None
    airframe_id = None

    if request.resolver_match:
        airframe_id = request.resolver_match.kwargs.get('airframe_id') \
            or request.resolver_match.kwargs.get('pk')

    if airframe_id:
        airframe = Airframe.objects.filter(pk=airframe_id).select_related(
            'aircraft_type', 'aircraft_type__aircraft_family'
        ).first()

    return {
        'current_airframe': airframe,
        'current_operator': airframe.operator if airframe else None,
        'current_company': airframe.operator.company if airframe else None,
    }

def datetime_processor(request):
    now = datetime.now()
    now_utc = datetime.now(timezone.utc)
    # TODO update everytime a post is sent
    last_sync = datetime.now()

    return {
        'current_date_zulu': now_utc.date(),
        'current_time_local': now.time(),
        'current_time_zulu': now_utc.time(),
    }