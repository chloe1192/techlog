from .models import Airframe, Company, Aoc
from django.shortcuts import get_object_or_404


def airframe_processor(request):
    current_company = Company.objects.filter(id=request.session.get('current_company_id')).last
    current_operator = Aoc.objects.filter(id=request.session.get('current_operator_id')).last
    current_airframe = Airframe.objects.filter(id=request.session.get('current_airframe_id')).last
    return {
        'current_operator': current_company,
        'current_operator': current_operator,
        'current_airframe': current_airframe
    }