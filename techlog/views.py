from datetime import datetime
from decimal import Decimal
from itertools import chain
from django.http import JsonResponse
from django.urls import reverse
from .helpers import fluids_are_done, parse_datetime, parse_date, loop_trough_fluids, save_departure_fuel_data, set_flight_fluid, update_fluid_tanks
from .forms import AcceptanceForm, ActionCreate, AirframeDefectCreateForm, AirframeEdit, AirframeEngineEdit, CompleteFlight, CurrentFlightArrivalFluids, CurrentFlightDepartureFluids, MaintenanceReleaseForm, RefuelingForm, UpdateFluidTanks
from .models import Action, ActionTypes, AircraftFamily, Airframe, AirframeDefect, AircraftType, AirframeEngine, CurrentFlight, DeferCategory, EngineModel, Company, Defect, EngineeringCompany, FlightFluid, FlightPhase, FluidInstance, FluidTemplate, Operator, Flight, Airport, Refuel, Route
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict
from django.db import transaction
from django.db.models import Q
from django.contrib import messages

def index(request):
    operators = Operator.objects.all()
    context = {
        'operators': operators,
    }
    return render(request, 'index.html', context)

def routes_list(request, operator_id):
    operator = get_object_or_404(Operator, id=operator_id)
    routes = Route.objects.filter(operator=operator)
    context = {
        'routes': routes
    }
    return render(request, 'airline_management/operator_management/routes/list.html', context)

def operator_index(request, operator_id):
    operator = get_object_or_404(Operator, id=operator_id)
    page_title = "Operator Selection"
    return_url = reverse("index")
    airframes = Airframe.objects.filter(operator=operator)

    context = {
        'airframes': airframes,
        'operator': operator,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'operator_index.html', context)

def airframes_list(request, airframe_id):
    page_title = "Operator Selection"
    return_url = reverse("index")
    airframes = Airframe.objects.filter(operator=airframe_id)
    return_url = request.META.get("HTTP_REFERER")

    context = {
        'airframes': airframes,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'airframes/list.html', context)

def airframes_create(request, operator_id):
    page_title = "Operator Selection"
    return_url = reverse("operator_index", kwargs={'operator_id': operator_id})
    operator = get_object_or_404(Operator, id=operator_id)
    operators = Operator.objects.filter(company__id=operator.company.id)
    aircraft_types = AircraftType.objects.all()
    engine_models = EngineModel.objects.all()

    if request.method == "POST":
        print(f"form' {request.POST}")

        form = AirframeEdit(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)

    context = {
        'aircraft_types': aircraft_types,
        'engine_models': engine_models,
        'operators': operators,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'airframes/create.html', context)

def airframes_edit(request, airframe_id):
    request.session['current_operator_id'] = airframe_id
    page_title = "Operator Selection"
    return_url = reverse("index")
    airframe = get_object_or_404(Airframe, id=airframe_id)
    return_url = request.META.get("HTTP_REFERER")
    operators = Operator.objects.all()
    aircraft_types = AircraftType.objects.all()
    aircraft_type_current = get_object_or_404(AircraftType, id=airframe.aircraft_type.id)
    engine_models = EngineModel.objects.all()
    engine_model_current = AirframeEngine.objects.filter(airframe=airframe.id)
    engine_type_current = engine_model_current.last()
    print(f"engine; {engine_model_current}")

    if request.method == "POST":
        print(f"form' {request.POST}")
        if request.POST.get("action") == "create_engine_instance":
            engine_count = int(request.POST.get("engine_number"))
            form = AirframeEngineEdit(request.POST)

            if form.is_valid():
                for k in range(1, engine_count + 1):
                    AirframeEngine.objects.create(
                        engine_model=form.cleaned_data["engine_model"],
                        airframe=airframe,
                        engine_hours=0,
                        engine_number=k,
                    )

        if request.POST.get("action") == "create_fluids_instance":
            fluids_template = FluidTemplate.objects.filter(
                Q(engine_model=engine_type_current.engine_model) |
                Q(aircraft_type=aircraft_type_current)
                )
            if engine_model_current.exists():
                for fluid in fluids_template:
                    print("fluid")
                    print(fluid)
                    
                    if fluid.engine_model is not None:
                        for engine in engine_model_current:
                            print("flengineuid")
                            print(engine)
                            print(f"fluid.engine_number; {engine.engine_number} {fluid}")
                            FluidInstance.objects.create(
                                fluid_template = fluid,
                                airframe_engine=engine,
                                level=fluid.max_level
                            )

                    if fluid.aircraft_type is not None:
                        print(f"fluid.engine_number; {fluid.aircraft_type} {fluid}")
                        FluidInstance.objects.create(
                            fluid_template = fluid,
                            airframe=airframe,
                            level=fluid.max_level
                        )

 
            else:
                print("No engines")

        form = AirframeEdit(request.POST, instance=airframe)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)

    context = {
        'airframe': airframe,
        'aircraft_types': aircraft_types,
        'aircraft_type_current': aircraft_type_current,
        'engine_models': engine_models,
        'engine_model_current': engine_model_current,
        'operators': operators,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'airframes/create.html', context)

def flight_release_maintenance(request, airframe_id):
    page_title = "Flight Sign Off"
    return_url = reverse('flight_index', kwargs={'airframe_id': airframe_id})
    airframe = get_object_or_404(Airframe, id=airframe_id)
    current_flight = CurrentFlight.objects.filter(airframe=airframe).first()

    if current_flight is None:
        current_flight = CurrentFlight.objects.create(airframe=airframe)

    if request.method == "POST":
        print(request.POST)
        print(f"request.POST[maint_release_date] {request.POST["maint_release_date"]}")
        maint_release_date = request.POST.get("maint_release_date")
        if maint_release_date is not None:
            maint_release_date = f"{request.POST["maint_release_date"]} {request.POST["maint_release_time"]}"
            maint_release_date = datetime.strptime(maint_release_date, "%Y-%m-%d %H:%M")

            if current_flight is not None:
                form = MaintenanceReleaseForm(request.POST, instance=current_flight)

                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.maint_release_date = maint_release_date
                    obj.airframe = airframe
                    obj.save()
                    return redirect('flight_index', airframe_id=airframe_id)
                else:
                    print(form.errors)

    maint_release_not_sent = True
    if current_flight.maint_release_date:
        print(f"current_flight.maint_release_date {current_flight.maint_release_date}")
        maint_release_not_sent = False

    acceptance_not_sent = True
    if current_flight.acceptance_date:
        acceptance_not_sent = False

    eng_cpy = EngineeringCompany.objects.all()
    current_date = datetime.now()
    context = {
        'airframe': airframe,
        'maint_release_not_sent': maint_release_not_sent,
        'acceptance_not_sent': acceptance_not_sent,
        'eng_cpy': eng_cpy,
        'current_flight': current_flight,
        'current_date': current_date,
        'return_url': return_url,
        'page_title': page_title
    }
    return render(request, 'flight_release/maintenance.html', context)

def flight_release_acceptance(request, airframe_id):
    page_title = "Flight Sign Off"
    return_url = request.META.get("HTTP_REFERER")
    airframe = get_object_or_404(Airframe, id=airframe_id)
    fluid_tanks = FluidInstance.objects.filter(
            Q(airframe_id=airframe_id) |
            Q(airframe_engine__airframe_id=airframe_id),
            fluid_template__fluid_type=0
        )
    current_flight = CurrentFlight.objects.filter(airframe=airframe).first()
    routes = Route.objects.filter(operator__airframe=airframe)

    if current_flight is None:
        current_flight = CurrentFlight.objects.create(airframe=airframe)

    if request.method == "POST":
        print(f"post:: ------------- {request.POST}")
        acceptance_date = f"{request.POST.get("acceptance_date")} {request.POST.get("acceptance_time")}"
        if acceptance_date is not None:
            acceptance_date = datetime.strptime(acceptance_date, "%Y-%m-%d %H:%M")
            print(f"maint_release_date:: ------------- {acceptance_date}")

            if current_flight is not None:
                form = AcceptanceForm(request.POST, instance=current_flight)

                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.acceptance_date = acceptance_date
                    obj.airframe = airframe
                    obj.save()
                    return redirect('flight_index', airframe_id=airframe_id)
                else:
                    print(form.errors)

    maintenance_release_not_sent = True
    if current_flight.maint_release_date:
        maintenance_release_not_sent = False

    acceptance_not_sent = True
    if current_flight.acceptance_date:
        acceptance_not_sent = False

    eng_cpy = EngineeringCompany.objects.all()
    current_date = datetime.now()
    total_fob = 0
    for fuel_tank in fluid_tanks:
        total_fob = total_fob + fuel_tank.level
    context = {
        'airframe': airframe,
        'maintenance_release_not_sent': maintenance_release_not_sent,
        'acceptance_not_sent': acceptance_not_sent,
        'routes': routes,
        'eng_cpy': eng_cpy,
        'current_flight': current_flight,
        'current_date': current_date,
        'return_url': return_url,
        'page_title': page_title,
        'total_fob': total_fob
    }
    return render(request, 'flight_release/acceptance.html', context)

def flight_index(request, airframe_id):
    request.session['current_airframe_id'] = airframe_id
    airframe = get_object_or_404(Airframe, id=airframe_id)
    return_url =  reverse("operator_index", kwargs={"operator_id": airframe.operator.id})
    page_title = "Main Menu"
    current_flight = CurrentFlight.objects.filter(airframe=airframe_id).order_by("-created_at").first()
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe_id)
    departure_fluids = FlightFluid.objects.filter(current_flight=current_flight,phase=0)
    fluid_tanks = FluidInstance.objects.filter(
        Q(airframe=airframe) |
        Q(airframe_engine__airframe=airframe)
    ).select_related('fluid_template', 'airframe_engine__engine_model')
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0

    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    dep_fluids_complete = all(dep_fluids_status.values())
    print(dep_fluids_status)

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
        'page_title': page_title,
        'open_defects_count': open_defects_count,
        'closed_defects_count': closed_defects_count,
        'carry_fwd_defects_count': carry_fwd_defects_count,
        'current_flight': current_flight,
        'return_url': return_url,
        'dep_fluids_status': dep_fluids_status,
        'dep_fluids_complete': dep_fluids_complete
    }
    return render(request, 'flight/index.html', context)

def flight_details(request, airframe_id):
    page_title = "Flight Details"
    return_url = reverse("flight_index", kwargs={"airframe_id": airframe_id,})
    last_flight = Flight.objects.filter(airframe=airframe_id).order_by("-created_at").first()
    airframe = get_object_or_404(Airframe, id=airframe_id)
    current_flight = get_object_or_404(CurrentFlight, airframe=airframe)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe_id)
    flight_no_options = Route.objects.filter(flt_number=current_flight.planned_flt_number)
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe_id)
    airports = Airport.objects.all()
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    for defect in airframe_defects:
        if defect.status == 0:
            open_defects_count = open_defects_count + 1
        if defect.status == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.status == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1

    if request.method == "POST":

        off_blocks_datetime = parse_datetime(
            request.POST.get("departure_date"),
            request.POST.get("off_blocks")
        )

        off_ground_datetime = parse_datetime(
            request.POST.get("departure_date"),
            request.POST.get("off_ground")
        )

        on_ground_datetime = parse_datetime(
            request.POST.get("arrival_date"),
            request.POST.get("on_ground")
        )

        on_blocks_datetime = parse_datetime(
            request.POST.get("arrival_date"),
            request.POST.get("on_blocks")
        )

        print(request.POST)
        current_flight.flight_route_id=request.POST.get('flight_number')
        current_flight.date_of_flight = request.POST.get("departure_date")
        current_flight.off_blocks=off_blocks_datetime
        current_flight.off_ground=off_ground_datetime
        current_flight.on_ground=on_ground_datetime
        current_flight.on_blocks=on_blocks_datetime
        current_flight.callsign=request.POST.get("callsign")
        current_flight.actual_arrival_id=request.POST.get("actual_arrival")
        current_flight.save()

        return JsonResponse({
            "success": True
        })
    context = {
        'page_title': page_title,
        'current_flight': current_flight,
        'flight_no_options': flight_no_options,
        'open_defects_count': open_defects_count,
        'closed_defects_count': closed_defects_count,
        'carry_fwd_defects_count': carry_fwd_defects_count,
        'last_flight': last_flight,
        'return_url': return_url,
        'airports': airports
    }
    if request.method == "POST":
        print(request.POST)
    return render(request, 'flight/details.html', context)

# TODO check for errors if tank is not uplifted, show departures in value if data was sent
def flight_departure_fluids(request, airframe_id, fluid_type):
    page_title = "Departure Fluids"
    if fluid_type == 0:
        template = 'flight/departure/fuel.html'
    else:
        template = 'flight/departure/fluids.html'

    match fluid_type:
        case 0:
            page_title = "Departure Fuel"
        case 1:
            page_title = "Departure Oil"
        case 2:
            page_title = "Departure Hydraulic"
        case _:
            page_title = "Departure Fluids"
    
    return_url = reverse('servicing', kwargs={'airframe_id': airframe_id})
    current_flight = get_object_or_404(CurrentFlight, airframe_id=airframe_id)
    airframe = Airframe.objects.get(id=airframe_id)
    last_flight = Flight.objects.filter(
        airframe=airframe
    ).last()
    fluid_tanks = {

    }

    fluid_tanks = FluidInstance.objects.filter(
        Q(airframe_id=airframe_id) |
        Q(airframe_engine__airframe_id=airframe_id),
        fluid_template__fluid_type=fluid_type
    )

    if last_flight is not None:

        fluid_tanks_last = FlightFluid.objects.filter(
            phase=1,
            flight__airframe=airframe
        )


    total_fluid = {
        'max_level': 0,
        'units_of_measure': None,
        'level': 0,
    }
    for f in fluid_tanks:
        total_fluid["max_level"] += f.fluid_template.max_level
        total_fluid["level"] = f.level + total_fluid['level']
        total_fluid["fluid_type"] = f.fluid_template.fluid_type
        total_fluid["units_of_measure"] = f.fluid_template.get_units_of_measure_display()

    if request.method == "POST":
        print('POST DATA:  ---------------------------------------')
        print(request.POST)
        print('POST DATA:  ---------------------------------------')
        nil_uplift = request.POST.get('nil_uplift')

        fluid_dict = loop_trough_fluids(
            request.POST,
            fluid_tanks,
            'fluid_departure_',
            "fluid_arrival_"
        )
        print('fluid_dict DATA:  ---------------------------------------')
        print(fluid_dict)
        print('fluid_dict DATA:  ---------------------------------------')

        with transaction.atomic():
            try:
                if fluid_type == 0:
                    
                    refueling_form = RefuelingForm(request.POST)
                    print(f'refueling data is {nil_uplift}')

                    if nil_uplift == "on":
                        print(f'saving departure fuel no uplift')
                        save_departure_fuel_data(current_flight, request.POST.get('planned_dep_fuel_in_kg'), total_fluid['level'])
                    
                    if refueling_form.is_valid() and nil_uplift != 'on':
                        refueling_obj = refueling_form.save(commit=False)
                        print(f'saving departure fuel with uplift')
                        refueling_obj.airframe = airframe
                        refueling_obj.save()
                        save_departure_fuel_data(current_flight, refueling_obj.planned_dep_fuel_in_kg, refueling_obj.departure_fob_in_kg)

                for fluid_id, value in fluid_dict.items():
                    instance = FlightFluid.objects.filter(
                        current_flight=current_flight,
                        fluid_id=fluid_id,
                        phase=0
                    ).first()

                    tank = FluidInstance.objects.filter(
                        id=fluid_id
                    ).first()

                    if nil_uplift == 'on':
                        value['fluid_departure_'] = value['fluid_arrival_'] 

                    update_fluid_tanks(value['fluid_departure_'], tank)
                    set_flight_fluid(value['fluid_departure_'], tank, current_flight, 0, 'draft', instance)
                            
            except Exception as e:
                print(e)

    context = {
        'page_title': page_title,
        'return_url': return_url,
        'current_flight': current_flight,
        'fluid_tanks': fluid_tanks,
        'total_fluid': total_fluid
    }
    return render(request, template, context)

# TODO check for errors if tank is not uplifted, show departure fluid instead of current level
def flight_arrival_fluids(request, airframe_id, fluid_type):
    page_title = "Arrival Fluids"

    match fluid_type:
        case 0:
            page_title = "Arrival Fuel"
        case 1:
            page_title = "Arrival Oil"
        case 2:
            page_title = "Arrival Hydraulic"
        case _:
            page_title = "Arrival Fluids"
    
    return_url = reverse('flight_details', kwargs={'airframe_id': airframe_id})
    current_flight = get_object_or_404(CurrentFlight, airframe_id=airframe_id)

    from django.db.models import Q

    fluid_tanks = FluidInstance.objects.filter(
        Q(airframe_id=airframe_id) |
        Q(airframe_engine__airframe_id=airframe_id),
        fluid_template__fluid_type=fluid_type
    )
    departure_fluid_tanks = FlightFluid.objects.filter(
        Q(fluid__fluid_template__fluid_type=fluid_type),
        current_flight=current_flight,
        phase=0
    ).order_by('fluid__fluid_template__name')
    arrival_fluid_tanks = FlightFluid.objects.filter(
        Q(fluid__fluid_template__fluid_type=fluid_type),
        current_flight=current_flight,
        phase=1
    )
    print(fluid_type)
    print(current_flight)
    total_fluid = {
        'max_level': 0,
        'units_of_measure': None,
        'level': 0,
    }
    for f in fluid_tanks:
        total_fluid["max_level"] += f.fluid_template.max_level
        total_fluid["level"] = f.level + total_fluid['level']
        total_fluid["fluid_type"] = f.fluid_template.fluid_type
        total_fluid["units_of_measure"] = f.fluid_template.get_units_of_measure_display()

    if request.method == "POST":

        fluid_dict = loop_trough_fluids(
            request.POST,
            fluid_tanks,
            'fluid_departure_',
            "fluid_arrival_"
        )

        with transaction.atomic():
            try:

                for fluid_id, value in fluid_dict.items():
                    instance = FlightFluid.objects.filter(
                        current_flight=current_flight,
                        fluid_id=fluid_id,
                        phase=1
                    ).first()

                    tank = FluidInstance.objects.filter(
                        id=fluid_id
                    ).first()
                    if value['fluid_arrival_'] == '':
                        value['fluid_arrival_'] = value['fluid_departure_']

                    print(value)

                    update_fluid_tanks(value['fluid_arrival_'], tank)
                    set_flight_fluid(value['fluid_arrival_'], tank, current_flight, 1, 'draft', instance)

            except Exception as e:
                print(e)

    context = {
        'page_title': page_title,
        'return_url': return_url,
        'fluid_tanks': fluid_tanks,
        'total_fluid': total_fluid,
        'departure_fluid_tanks': departure_fluid_tanks,
        'arrival_fluid_tanks': arrival_fluid_tanks
    }
    return render(request, 'flight/arrival/fluids.html', context)

@require_POST
def flight_save(request, airframe_id):
    airframe = get_object_or_404(Airframe, id=airframe_id)
    current_flight = get_object_or_404(CurrentFlight, airframe=airframe)
    refuels = Refuel.objects.filter(planned_flt_number=current_flight)
    flight_fluids = FlightFluid.objects.filter(current_flight=current_flight)

    if request.method == 'POST':

        current_flight_post = model_to_dict(current_flight)
        print("request.POST")
        print(current_flight_post)
        current_flight_post['actual_arrival'] = current_flight.flight_route.arrival
        form = CompleteFlight(current_flight_post)

        if form.is_valid():

            try:
                with transaction.atomic():

                    obj = form.save()

                    if refuels is not None:
                        for refuel in refuels:
                            refuel.planned_flt_number = None
                            refuel.actual_flight = obj
                            print(f'refueling saved to flight:  {refuel.bowser_uplift_in_lt}--------------')
                            refuel.save()

                    if flight_fluids is not None:
                        for fluid in flight_fluids:
                            fluid.current_flight = None
                            fluid.flight = obj
                            print(f'flight_fluids saved to flight:  {fluid}--------------')
                            fluid.save()
                    
                    current_flight.delete()

                print("obj")
                print(obj)                
                return redirect('flight_index', airframe_id=airframe_id)
            
            except Exception as e:
                print(e)  # or logger.exception(...)
                messages.error(request, f"Failed to save flight: {e}")
                return redirect('flight_details', airframe_id=airframe_id)
        else:
            print(form.errors)
            return JsonResponse({"success": False})

def defects(request, airframe_id):
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)    
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe)
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    carry_fwd_action_overdue = 0

    print("datetime.now()" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    for defect in airframe_defects:
        print(defect)
        current_defect_actions = defect_actions.filter(airframe_defect=defect).last()
        if defect.status == 0:
            open_defects_count = open_defects_count + 1
        if defect.status == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.status == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1
            print("defect.due_at" + current_defect_actions.due_at.strftime("%Y-%m-%d %H:%M:%S"))
            if current_defect_actions.due_at < datetime.now():
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

def defects_this_flight(request, airframe_id):
    return_url = reverse('flight_index', kwargs={'airframe_id': airframe_id})
    page_title = "Defects this flight"
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe)
    print(airframe_defects)
    context = {
        'return_url': return_url,
        'page_title': page_title,
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defect_actions': defect_actions,
    }
    return render(request, 'defects/this_flight.html', context)

def defects_create(request, airframe_id):
    return_url = reverse('defects_this_flight', kwargs={'airframe_id': airframe_id})
    page_title = "Create a new defect"
    airframe = get_object_or_404(Airframe, id=airframe_id)

    if request.method == "POST":
        form = AirframeDefectCreateForm(request.POST)
        if form.is_valid():
            print("form")
            obj = form.save(commit=False)
            obj.airframe = airframe
            obj.save()
        else:
            print(form.errors)

    defects = Defect.objects.filter(aircraft_family=airframe.aircraft_type.aircraft_family)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    print(airframe_defects)
    context = {
        'return_url': return_url,
        'page_title': page_title,
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defects': defects
    }
    return render(request, 'defects/create.html', context)

def defects_details(request, airframe_id, defect_id):
    return_url = reverse('defects_this_flight', kwargs={'airframe_id': airframe_id})
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defect = get_object_or_404(AirframeDefect, airframe=airframe, id=defect_id)
    engine_model = AirframeEngine.objects.filter(airframe=airframe).last()    
    defects = Defect.objects.filter(aircraft_family=airframe.aircraft_type.aircraft_family)
    actions = Action.objects.filter(airframe_defect=airframe_defect)

    print(airframe_defect.defect)

    if request.method == "POST":
        print(request.POST)
        form = AirframeDefectCreateForm(request.POST, instance=airframe_defect)
        if request.POST.get('defect_template') is not "":
            defect_instance = Defect.objects.get(id=request.POST.get('defect_template'))
        if form.is_valid():
            print("form")
            obj = form.save(commit=False)
            if request.POST.get('defect_template') is not "":
                obj.defect = defect_instance
            obj.save()
            return redirect('defects_this_flight', airframe_id=airframe_id)
        else:
            print(form.errors)

    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe)
    context = {
        'return_url': return_url,
        'airframe': airframe,
        'airframe_defect': airframe_defect,
        'actions': actions,
        'defects': defects,
        'defect_actions': defect_actions,
    }
    return render(request, 'defects/details.html', context)

def defects_actions_create(request, airframe_id, defect_id):
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defect = get_object_or_404(AirframeDefect, id=defect_id)
    engineering_companies = EngineeringCompany.objects.all()
    return_url = reverse('defects_details', kwargs={'airframe_id': airframe_id, 'defect_id': defect_id})
    page_title = f"Create action for {airframe_defect.defect_title}"
    categories = DeferCategory
    statuses = ActionTypes

    if request.method == "POST":

        print(f"request.POST: ----------- {request.POST}")
        form = ActionCreate(request.POST)
        deferred_at_date = f"{request.POST["deferred_at_date"]} {request.POST["deferred_at_time"]}"
        deferred_at_date = datetime.strptime(deferred_at_date, "%Y-%m-%d %H:%M")

        if form.is_valid():
            obj = form.save(commit=False)
            obj.airframe_defect = airframe_defect
            obj.deferred_at = deferred_at_date
            obj.save()
            airframe_defect.status = obj.status
            airframe_defect.save()
            print(f"obj: ----------- {obj}")
        else:
            print(form.errors)

    print(airframe_defect.defect)
    context = {
        'return_url': return_url,
        'page_title': page_title,
        'airframe': airframe,
        'engineering_companies': engineering_companies,
        'categories': categories,
        'statuses': statuses,
        'airframe_defect': airframe_defect
    }
    return render(request, 'defects/actions/create.html', context)

def defects_actions_edit(request, airframe_id, defect_id, action_id):
    page_title = "Action Edit"
    return_url = reverse("defects_details", kwargs={"airframe_id": airframe_id, "defect_id": defect_id})
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defect = get_object_or_404(AirframeDefect, id=defect_id)
    engineering_companies = EngineeringCompany.objects.all()
    categories = DeferCategory
    statuses = ActionTypes
    action = get_object_or_404(Action, id=action_id)

    if request.method == "POST":

        print(f"request.POST: ----------- {request.POST}")
        form = ActionCreate(request.POST, instance=action)
        deferred_at_date = f"{request.POST["deferred_at_date"]} {request.POST["deferred_at_time"]}"
        deferred_at_date = datetime.strptime(deferred_at_date, "%Y-%m-%d %H:%M")

        if form.is_valid():
            obj = form.save(commit=False)
            obj.airframe_defect = airframe_defect
            obj.deferred_at = deferred_at_date
            obj.save()
            airframe_defect.status = obj.status
            airframe_defect.save()
            print(f"obj: ----------- {obj}")
            return redirect(defects_details, airframe_id=airframe_id, defect_id=defect_id)
        else:
            print(form.errors)

    print(airframe_defect.defect)
    print(f"action: {action}")
    context = {
        'return_url': return_url,
        'page_title': page_title,
        'airframe': airframe,
        'action': action,
        'engineering_companies': engineering_companies,
        'categories': categories,
        'statuses': statuses,
        'airframe_defect': airframe_defect
    }
    return render(request, 'defects/actions/create.html', context)

def servicing(request, airframe_id):
    page_title = "Servicing"
    return_url = reverse("flight_index", kwargs={"airframe_id": airframe_id})
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    current_flight = CurrentFlight.objects.filter(airframe=airframe_id).order_by("-created_at").first()
    """ 
    print("refuel_is_done")
    print(current_flight.refuel_is_done)
    print("oil_is_done")
    print(current_flight.oil_is_done)
    print("hyd_is_done")
    print(current_flight.hyd_is_done)
    print("water_is_done")
    print(current_flight.water_is_done) """

    context = {
        'page_title': page_title,
        'return_url': return_url,
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'current_flight': current_flight
    }
    return render(request, 'servicing/index.html', context)

def servicing_refuel_list(request, airframe_id):
    refuel_list = Refuel.objects.filter(airframe=airframe_id,actual_flight=None)
    context = {
        'refuel_list': refuel_list
        }

    return render(request, 'servicing/refuel_list.html', context)

def flight_ice_protection(request):
    context = {
        
    }
    return render(request, 'ice_protection.html', context)

def planned_maintenance(request):
    context = {

    }
    return render(request, 'planned_maintenance.html', context)
