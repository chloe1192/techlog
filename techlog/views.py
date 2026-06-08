from .models import Airframe, AirframeDefect, AircraftType, EngineModel, EngineFluids, Company, Defect, Aoc, AirframeFluid, Flight
from django.shortcuts import get_object_or_404, redirect, render

def index(request):
    operators = Aoc.objects.all()
    context = {
        'operators': operators,
    }
    return render(request, 'index.html', context)

def airframe_index(request, airframe_id):
    request.session['current_airframe_id'] = airframe_id
    page_title = "Main Menu"
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    engine_model = airframe.engine_model
    engine_fluids = EngineFluids.objects.filter(airframe_engine=airframe_id)
    airframe_fluids = AirframeFluid.objects.filter(airframe=airframe)
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    current_flight = Flight.objects.filter(airframe=airframe_id).order_by("-created_at").first()

    for defect in airframe_defects:
        print(defect.action)
        if defect.action == 0:
            open_defects_count = open_defects_count + 1
        if defect.action == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.action == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1

    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'engine_fluids': engine_fluids,
        'airframe_fluids': airframe_fluids,
        'page_title': page_title,
        'open_defects_count': open_defects_count,
        'closed_defects_count': closed_defects_count,
        'carry_fwd_defects_count': carry_fwd_defects_count,
        'current_flight': current_flight
    }
    return render(request, 'airframe_index.html', context)

def operator_index(request, id):
    request.session['current_operator_id'] = id
    page_title = "Operator Selection"
    airframes = Airframe.objects.filter(aoc=id)
    print(airframes)
    context = {
        'airframes': airframes
    }
    return render(request, 'operator_index.html', context)

def flight_details(request, id):
    
    last_flight = Flight.objects.filter(airframe=id).order_by("-created_at").first()
    airframe_defects = AirframeDefect.objects.filter(airframe=id)
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0

    for defect in airframe_defects:
        print(defect.action)
        if defect.action == 0:
            open_defects_count = open_defects_count + 1
        if defect.action == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.action == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1

    context = {
        'open_defects_count': open_defects_count,
        'closed_defects_count': closed_defects_count,
        'carry_fwd_defects_count': carry_fwd_defects_count,
        'last_flight': last_flight
    }
    return render(request, 'flight_details.html', context)

def flight_defects(request, id):
    airframe = get_object_or_404(Airframe, id=id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    print(airframe_defects)
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
    }
    return render(request, 'flight_defects.html', context)

def flight_servicing(request, id):
    airframe = get_object_or_404(Airframe, id=id)
    airframe_fluids = AirframeFluid.objects.filter(airframe=airframe)
    engine_fluids = EngineFluids.objects.filter(airframe_engine__airframe=airframe)
    print(engine_fluids)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'airframe_fluids': airframe_fluids,
    }
    return render(request, 'flight_servicing.html', context)

def flight_oil_levels(request, id):
    airframe_fluids = AirframeFluid.objects.filter(airframe=id,fluid_type=1)
    engine_fluids = EngineFluids.objects.filter(airframe_engine__airframe=id,fluid_type=1)
    context = {
        'airframe_fluids': airframe_fluids,
        'engine_fluids': engine_fluids
    }
    return render(request, 'flight_oil_levels.html', context)