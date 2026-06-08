from .models import Airframe, Company
from django.shortcuts import get_object_or_404


def airframe_processor(request):
    current_airframe = get_object_or_404(Airframe, id=request.session.get('current_airframe_id'))
    return {
        'current_airframe': current_airframe
    }