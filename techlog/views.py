from datetime import datetime
from itertools import chain

from .models import Action, Airframe, AirframeDefect, AircraftType, AirframeEngine, EngineModel, EngineFluids, Company, Defect, Operator, AirframeFluid, Flight, Airport
from django.shortcuts import get_object_or_404, redirect, render

def index(request):
    operators = Operator.objects.all()
    context = {
        'operators': operators,
    }
    return render(request, 'index.html', context)

def airframe_index(request, airframe_id):
    request.session['current_airframe_id'] = airframe_id
    page_title = "Main Menu"
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    engine_fluids = EngineFluids.objects.filter(airframe_engine=airframe_id)
    airframe_fluids = AirframeFluid.objects.filter(airframe=airframe)
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe_id)
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    current_flight = Flight.objects.filter(airframe=airframe_id).order_by("-created_at").first()
    return_url = request.META.get("HTTP_REFERER")

    for defect in defect_actions:
        if defect.status == 0:
            open_defects_count = open_defects_count + 1
        if defect.status == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.status == 2:
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
        'current_flight': current_flight,
        'return_url': return_url
    }
    return render(request, 'airframe_index.html', context)

def operator_index(request, id=0):
    request.session['current_operator_id'] = id
    page_title = "Operator Selection"
    airframes = Airframe.objects.filter(operator=id)
    return_url = request.META.get("HTTP_REFERER")

    context = {
        'airframes': airframes,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'operator_index.html', context)

def flight_details(request, id):
    page_title = "Flight Details"
    last_flight = Flight.objects.filter(airframe=id).order_by("-created_at").first()
    airframe_defects = AirframeDefect.objects.filter(airframe=id)
    defect_actions = Action.objects.filter(airframe_defect__airframe=id)
    airports = Airport.objects.all()
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    return_url = request.META.get("HTTP_REFERER")

    for defect in defect_actions:
        if defect.status == 0:
            open_defects_count = open_defects_count + 1
        if defect.status == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.status == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1

    context = {
        'page_title': page_title,
        'open_defects_count': open_defects_count,
        'closed_defects_count': closed_defects_count,
        'carry_fwd_defects_count': carry_fwd_defects_count,
        'last_flight': last_flight,
        'return_url': return_url,
        'airports': airports
    }
    if request.method == "POST":
        print(request.POST)
    return render(request, 'flight_details.html', context)

def defects(request, id):
    airframe = get_object_or_404(Airframe, id=id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)    
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe)
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    carry_fwd_action_overdue = 0

    print("datetime.now()" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for defect in defect_actions:
        if defect.status == 0:
            open_defects_count = open_defects_count + 1
        if defect.status == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.status == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1
            print("defect.due_at" + defect.due_at.strftime("%Y-%m-%d %H:%M:%S"))
            if defect.due_at < datetime.now():
                carry_fwd_action_overdue = carry_fwd_action_overdue + 1
    
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defect_actions': defect_actions,
        'open_defects_count': open_defects_count,
        'closed_defects_count': closed_defects_count,
        'carry_fwd_defects_count': carry_fwd_defects_count,
        'carry_fwd_action_overdue': carry_fwd_action_overdue,
        
    }
    return render(request, 'defects/index.html', context)

def this_flight_defects(request, id):
    airframe = get_object_or_404(Airframe, id=id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe)
    print(airframe_defects)
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defect_actions': defect_actions,
    }
    return render(request, 'defects/this_flight.html', context)

def flight_defects(request, id):
    airframe = get_object_or_404(Airframe, id=id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    print(airframe_defects)
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
    }
    return render(request, 'flight_defects.html', context)

def flight_defects_create(request, id):
    airframe = get_object_or_404(Airframe, id=id)
    defects = Defect.objects.all()
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    print(airframe_defects)
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defects': defects
    }
    return render(request, 'flight_defects_create.html', context)

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

def flight_fuel_levels(request, id):
    current_flight = Flight.objects.filter(airframe=id).order_by("-created_at").first()
    total_fuel = {
        'max_level': 0,
        'units_of_measure': 0,
    }
    fuel_tanks = AirframeFluid.objects.filter(airframe_id=id, fluid_type=0)
    for tank in fuel_tanks:
        total_fuel['max_level'] = tank.max_level + total_fuel['max_level']
        total_fuel['units_of_measure'] = tank.get_units_of_measure_display

    print(total_fuel)
    context = {
        'total_fuel': total_fuel,
        'fuel_tanks': fuel_tanks,
        'current_flight': current_flight
    }
    return render(request, 'flight_fuel_levels.html', context)

def flight_oil_levels(request, id):
    airframe_fluids = AirframeFluid.objects.filter(airframe=id,fluid_type=1)
    engine_fluids = EngineFluids.objects.filter(airframe_engine__airframe=id,fluid_type=1)
    fluids = chain(airframe_fluids, engine_fluids)
    context = {
        'fluids': fluids
    }
    return render(request, 'flight_oil_levels.html', context)

def flight_hydraulic_levels(request, id):
    fluids = AirframeFluid.objects.filter(airframe=id,fluid_type=2)
    context = {
        'fluids': fluids
    }
    return render(request, 'flight_hydraulic_levels.html', context)

def flight_water_levels(request, id):
    fluids = AirframeFluid.objects.filter(airframe=id,fluid_type=3).order_by("item")
    current_flight = Flight.objects.filter(airframe=id).order_by("-created_at").first()
    context = {
        'current_flight': current_flight,
        'fluids': fluids
    }
    return render(request, 'flight_water_levels.html', context)

def flight_ice_protection(request):
    context = {
        
    }
    return render(request, 'ice_protection.html', context)

def planned_maintenance(request):
    context = {

    }
    return render(request, 'planned_maintenance.html', context)

def flight_sign_off(request, id):
    context = {
        
    }
    return render(request, 'flight_sign_off.html', context)