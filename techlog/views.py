from datetime import datetime
from decimal import Decimal
from itertools import chain
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from techlog.mapping import from_api, from_api_many
from techlog.services.airframe_service import get_airframe, get_arrival_fluids, get_defect_actions, get_departure_fluids, get_fluid_tanks, invalidate_airframe_cache,get_current_flight
from techlog.state import Action, Airport, EngineeringCompany, FlightFluid, Operator, Airframe, AirframeDefect, FluidInstance, CurrentFlight, Flight, Route
from .helpers import fluids_are_done, parse_datetime, parse_date, loop_trough_fluids, save_departure_fuel_data, set_flight_fluid, summarize_defect_statuses, update_fluid_tanks
from .forms import AcceptanceForm, ActionCreate, AirframeDefectCreateForm, AirframeEdit, AirframeEngineEdit, CompleteFlight, CurrentFlightArrivalFluids, CurrentFlightDepartureFluids, MaintenanceReleaseForm, RefuelingForm, UpdateFluidTanks
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.forms.models import model_to_dict
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from techlog.api import TechlogClient

client = TechlogClient()

def index(request):
    """Render the index page."""
    operators = from_api_many(Operator, client.get("operators"))
    context = {
        'operators': operators,
    }
    return render(request, 'index.html', context)

def routes_list(request, operator_id):
    """Handle route listing request for list."""
    operator = from_api(Operator, client.get(f"operators/{operator_id}"))
    routes = Route.objects.filter(operator=operator)
    context = {
        'routes': routes
    }
    return render(request, 'airline_management/operator_management/routes/list.html', context)

def operator_index(request, operator_id):
    operator = from_api(Operator, client.get(f"operators/{operator_id}/"))
    page_title = "Operator Selection"
    return_url = reverse("index")
    airframes = from_api_many(Airframe, client.get(f"operators/{operator_id}/airframes/"))

    context = {
        'airframes': airframes,
        'operator': operator,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'operator_index.html', context)

def airframes_list(request, airframe_id):
    """Handle airframe management request for list."""
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
    """Handle airframe management request for create."""
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
    """Handle airframe management request for edit."""
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
    departure_fluids = get_departure_fluids(request, airframe_id)
    fluid_tanks = get_fluid_tanks(request, airframe_id)
    current_flight = from_api(CurrentFlight, client.get(f"airframes/{airframe_id}/current_flight/"))
    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    dep_fluids_complete = all(dep_fluids_status.values())

    if current_flight is None:
        current_flight = from_api(
            CurrentFlight,
            client.post(f"airframes/{airframe_id}/current_flight/", data={
                "airframe": airframe_id,
            })
        )
        invalidate_airframe_cache(request, airframe_id)

    if request.method == "POST":

        maint_release_date = request.POST.get("maint_release_date")
        maint_release_eng_company = request.POST.get("maint_release_eng_company")

        if maint_release_date is not None:
            maint_release_date = f"{request.POST["maint_release_date"]} {request.POST["maint_release_time"]}"
            maint_release_date = datetime.strptime(maint_release_date, "%Y-%m-%d %H:%M")

            if current_flight is not None:

                current_flight = from_api(
                    CurrentFlight,
                    client.put(f"airframes/{airframe_id}/current_flight/", data={
                        "airframe_id": airframe_id,
                        "maint_release_date": maint_release_date,
                        "maint_release_eng_company_id": maint_release_eng_company
                    })
                )
                invalidate_airframe_cache(request, airframe_id)

    maint_release_not_sent = True
    if current_flight.maint_release_date:
        maint_release_not_sent = False

    acceptance_not_sent = True
    if current_flight.acceptance_date:
        acceptance_not_sent = False

    eng_cpy = from_api_many(EngineeringCompany, client.get("eng_cpy/"))
    current_date = datetime.now()
    context = {
        'page_title': "Flight Sign Off",
        'maint_release_not_sent': maint_release_not_sent,
        'acceptance_not_sent': acceptance_not_sent,
        'eng_cpy': eng_cpy,
        'current_flight': current_flight,
        'current_date': current_date,
        'dep_fluids_complete': dep_fluids_complete
    }
    return render(request, 'flight_release/maintenance.html', context)

def flight_release_acceptance(request, airframe_id):
    """Handle flight-related request for release acceptance."""
    page_title = "Flight Sign Off"
    return_url = request.META.get("HTTP_REFERER")
    airframe = get_airframe(request, airframe_id)
    last_flight = from_api(Flight, client.get(f"airframes/{airframe_id}/last_flight/"))
    routes = from_api_many(Route, client.get(f"operator/{airframe.operator.id}/routes/departure/{last_flight.actual_arrival.icao_code}/"))
    print(routes)
    departure_fluids = get_departure_fluids(request, airframe_id)
    fluid_tanks = get_fluid_tanks(request, airframe_id)
    current_flight = from_api(CurrentFlight, client.get(f"airframes/{airframe_id}/current_flight/"))
    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    dep_fluids_complete = all(dep_fluids_status.values())

    if request.method == "POST":
        acceptance_date = request.POST.get("acceptance_date")

        if acceptance_date is not None:
            acceptance_date = f"{request.POST["acceptance_date"]} {request.POST["acceptance_time"]}"
            acceptance_date = datetime.strptime(acceptance_date, "%Y-%m-%d %H:%M")

            if current_flight is not None:

                current_flight = from_api(
                    CurrentFlight,
                    client.put(f"airframes/{airframe_id}/current_flight/", data={
                        "airframe_id": airframe_id,
                        "acceptance_date": acceptance_date,
                        "planned_flt_number": request.POST["planned_flt_number"],
                    })
                )
                invalidate_airframe_cache(request, airframe_id)

    maintenance_release_not_sent = True
    if current_flight.maint_release_date:
        maintenance_release_not_sent = False

    acceptance_not_sent = True
    if current_flight.acceptance_date:
        acceptance_not_sent = False

    eng_cpy = from_api_many(EngineeringCompany, client.get("eng_cpy/"))
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
    # TODO airframe is being stored only in flight_index, if any change happen in another page data is lost

    defect_actions: list[Action] = get_defect_actions(request, airframe_id)
    departure_fluids: list[FlightFluid] = get_departure_fluids(request, airframe_id)
    fluid_tanks: list[FluidInstance] = get_fluid_tanks(request, airframe_id)

    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    defect_counts = summarize_defect_statuses(defect_actions)

    context = {
        'page_title': "Main Menu",
        'open_defects_count': defect_counts['open'],
        'closed_defects_count': defect_counts['closed'],
        'carry_fwd_defects_count': defect_counts['carry_fwd'],
        'dep_fluids_status': dep_fluids_status,
        'dep_fluids_complete': all(dep_fluids_status.values())
    }
    return render(request, 'flight/index.html', context)

def flight_details(request, airframe_id):
    defect_actions: list[Action] = get_defect_actions(request, airframe_id)
    fluid_tanks: list[FluidInstance] = get_fluid_tanks(request, airframe_id)
    defect_counts = summarize_defect_statuses(defect_actions)

    last_flight = from_api(Flight, client.get(f"airframes/{airframe_id}/last_flight/"))
    current_flight = from_api(CurrentFlight, client.get(f"airframes/{airframe_id}/current_flight/"))
    flight_no_options = from_api_many(Route, client.get(f"route/{current_flight.planned_flt_number}/"))
    airports = from_api_many(Airport, client.get("airports/"))
    arrival_fluids: list[FlightFluid] = get_arrival_fluids(request, airframe_id)

    arr_fluids_status: dict = fluids_are_done(arrival_fluids, fluid_tanks)

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

        if current_flight is not None:

            current_flight = from_api(
                CurrentFlight,
                client.put(f"airframes/{airframe_id}/current_flight/", data={
                    "airframe_id": airframe_id,
                    "flight_route_id": request.POST.get('flight_number'),
                    "date_of_flight": request.POST.get("departure_date"),
                    "off_blocks": off_blocks_datetime,
                    "off_ground": off_ground_datetime,
                    "on_ground": on_ground_datetime,
                    "on_blocks": on_blocks_datetime,
                    "callsign": request.POST.get("callsign"),
                    "actual_arrival_id": request.POST.get("actual_arrival")
                })
            )
            invalidate_airframe_cache(request, airframe_id)

        return JsonResponse({
            "success": True
        })
    context = {
        'page_title': "Flight Details",
        'current_flight': current_flight,
        'flight_no_options': flight_no_options,
        'open_defects_count': defect_counts['open'],
        'closed_defects_count': defect_counts['closed'],
        'carry_fwd_defects_count': defect_counts['carry_fwd'],
        'last_flight': last_flight,
        'airports': airports,
        'arr_fluids_status': arr_fluids_status
    }
    if request.method == "POST":
        print(request.POST)
    return render(request, 'flight/details.html', context)

# TODO check for errors if tank is not uplifted, show departures in value if data was sent
def flight_departure_fluids(request, airframe_id, fluid_type):
    """Handle flight-related request for departure fluids."""
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
    fluid_tanks = {

    }

    fluid_tanks = FluidInstance.objects.filter(
        Q(airframe_id=airframe_id) |
        Q(airframe_engine__airframe_id=airframe_id),
        fluid_template__fluid_type=fluid_type
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

        try:
            with transaction.atomic():
                print(fluid_type)
                if fluid_type == 0:
                    
                    refueling_form = RefuelingForm(request.POST)
                    print(f'refueling data is {nil_uplift}')
                    print(f'REFUEL: {refueling_form}')

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
                print("Inside atomic")
                            
            print("ex atomic")
            print('Transaction done, return to services page')
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('servicing', kwargs={"airframe_id": airframe_id})
            })
            
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
    """Handle flight-related request for arrival fluids."""
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

        try:
            with transaction.atomic():

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

                
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('flight_details', kwargs={"airframe_id": airframe_id})
            })

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
    """Handle flight-related request for save."""
    airframe = get_object_or_404(Airframe, id=airframe_id)
    print(airframe)
    current_flight = get_object_or_404(CurrentFlight, airframe=airframe)
    print(current_flight)
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
                # TODO handles response in js
                return redirect('flight_index', airframe_id=airframe_id)
            
            except Exception as e:
                print(e)  # or logger.exception(...)
                messages.error(request, f"Failed to save flight: {e}")
                return redirect('flight_details', airframe_id=airframe_id)
        else:
            print(form.errors)
            return JsonResponse({"success": False})

def defects(request, airframe_id):
    """Defects."""
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)    
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe)
    open_defects_count = 0
    closed_defects_count = 0
    carry_fwd_defects_count = 0
    carry_fwd_action_overdue = 0

    for defect in airframe_defects:
        print(defect)
        current_defect_actions = defect_actions.filter(airframe_defect=defect).last()
        if defect.status == 0:
            open_defects_count = open_defects_count + 1
        if defect.status == 1:
            closed_defects_count = closed_defects_count + 1
        if defect.status == 2:
            carry_fwd_defects_count = carry_fwd_defects_count + 1
            if current_defect_actions.due_at is not None:
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
    """Handle defects request for this flight."""
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
    """Handle defects request for create."""
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
    """Handle defects request for details."""
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
    """Handle defects request for actions create."""
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
    """Handle defects request for actions edit."""
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
    """Servicing."""
    page_title = "Servicing"
    return_url = reverse("flight_index", kwargs={"airframe_id": airframe_id})
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    current_flight = CurrentFlight.objects.filter(airframe=airframe_id).order_by("-created_at").first()
    departure_fluids = FlightFluid.objects.filter(current_flight=current_flight,phase=0)
    fluid_tanks = FluidInstance.objects.filter(
        Q(airframe=airframe) |
        Q(airframe_engine__airframe=airframe)
    ).select_related('fluid_template', 'airframe_engine__engine_model')

    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)

    context = {
        'page_title': page_title,
        'return_url': return_url,
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'current_flight': current_flight,
        'dep_fluids_status': dep_fluids_status
    }
    return render(request, 'servicing/index.html', context)

def servicing_refuel_list(request, airframe_id):
    """Handle servicing request for refuel list."""
    refuel_list = Refuel.objects.filter(airframe=airframe_id,actual_flight=None)
    context = {
        'refuel_list': refuel_list
        }

    return render(request, 'servicing/refuel_list.html', context)

def flight_ice_protection(request):
    """Handle flight-related request for ice protection."""
    context = {
        
    }
    return render(request, 'ice_protection.html', context)

def planned_maintenance(request):
    """Render the planned maintenance page."""
    context = {

    }
    return render(request, 'planned_maintenance.html', context)
