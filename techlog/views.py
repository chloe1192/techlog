from datetime import datetime

from django.db import transaction
from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from techlog.api import TechlogClient
from techlog.mapping import from_api, from_api_many
from techlog.state import (
    Action, Airport, EngineeringCompany, FlightFluid, Operator, Airframe,
    AirframeDefect, FluidInstance, CurrentFlight, Flight, Refuel, Route,
)
from techlog.forms import (
    AirframeDefectForm, AirframeForm, AirframeEngineForm, ActionForm,
    CompleteFlightForm, RefuelingForm,
)
from techlog.helpers import (
    fluids_are_done, parse_datetime, save_departure_fuel_data,
    set_flight_fluid, summarize_defect_statuses, update_fluid_tanks,
    loop_trough_fluids,
)
from techlog.services import airframe_service, defect_service, reference_data_service

client = TechlogClient()


def index(request):
    operators = reference_data_service.get_operators()
    return render(request, 'index.html', {'operators': operators})


def routes_list(request, operator_id):
    operator = reference_data_service.get_operator(operator_id)
    routes = from_api_many(Route, client.get(f"operators/{operator_id}/routes/"))
    return render(request, 'airline_management/operator_management/routes/list.html', {
        'operator': operator,
        'routes': routes,
    })


def operator_index(request, operator_id):
    operator = reference_data_service.get_operator(operator_id)
    airframes = from_api_many(Airframe, client.get(f"operators/{operator_id}/airframes/"))

    return render(request, 'operator_index.html', {
        'airframes': airframes,
        'operator': operator,
        'page_title': "Operator Selection",
    })


def airframes_list(request, operator_id):
    airframes = from_api_many(Airframe, client.get(f"operators/{operator_id}/airframes/"))
    return render(request, 'airframes/list.html', {
        'airframes': airframes,
        'page_title': "Operator Selection",
    })


def airframes_create(request, operator_id):
    operator = reference_data_service.get_operator(operator_id)
    operators = [
        op for op in reference_data_service.get_operators()
        if op.company and operator.company and op.company.id == operator.company.id
    ]
    aircraft_types = reference_data_service.get_aircraft_types()
    engine_models = reference_data_service.get_engine_models()

    if request.method == "POST":
        form = AirframeForm(request.POST)
        if form.is_valid():
            reference_data_service.create_airframe(form.cleaned_data)
        else:
            print(form.errors)

    return render(request, 'airframes/create.html', {
        'aircraft_types': aircraft_types,
        'engine_models': engine_models,
        'operators': operators,
        'page_title': "Operator Selection",
    })


def airframes_edit(request, airframe_id):
    request.session['current_operator_id'] = airframe_id
    airframe = airframe_service.get_airframe(request, airframe_id)
    operators = reference_data_service.get_operators()
    aircraft_types = reference_data_service.get_aircraft_types()
    aircraft_type_current = airframe.aircraft_type
    engine_models = reference_data_service.get_engine_models()
    engine_model_current = reference_data_service.get_airframe_engines(airframe_id)
    engine_type_current = engine_model_current[-1] if engine_model_current else None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_engine_instance":
            engine_count = int(request.POST.get("engine_number"))
            form = AirframeEngineForm(request.POST)
            if form.is_valid():
                for k in range(1, engine_count + 1):
                    reference_data_service.create_airframe_engine({
                        "engine_model_id": form.cleaned_data["engine_model"],
                        "airframe_id": airframe_id,
                        "engine_hours": 0,
                        "engine_number": k,
                    })

        elif action == "create_fluids_instance":
            if engine_model_current and engine_type_current:
                templates = reference_data_service.get_fluid_templates_for_airframe(airframe_id)
                for fluid in templates:
                    if fluid.engine_model is not None:
                        for engine in engine_model_current:
                            reference_data_service.create_fluid_instance({
                                "fluid_template_id": fluid.id,
                                "airframe_engine_id": engine.id,
                                "level": fluid.max_level,
                            })
                    if fluid.aircraft_type is not None:
                        reference_data_service.create_fluid_instance({
                            "fluid_template_id": fluid.id,
                            "airframe_id": airframe_id,
                            "level": fluid.max_level,
                        })

        else:
            form = AirframeForm(request.POST)
            if form.is_valid():
                reference_data_service.update_airframe(airframe_id, form.cleaned_data)
            else:
                print(form.errors)

        airframe_service.invalidate_airframe_cache(request, airframe_id)
        airframe = airframe_service.get_airframe(request, airframe_id)

    return render(request, 'airframes/create.html', {
        'airframe': airframe,
        'aircraft_types': aircraft_types,
        'aircraft_type_current': aircraft_type_current,
        'engine_models': engine_models,
        'engine_model_current': engine_model_current,
        'operators': operators,
        'page_title': "Operator Selection",
    })


def flight_release_maintenance(request, airframe_id):
    departure_fluids = airframe_service.get_departure_fluids(request, airframe_id)
    fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)
    current_flight = airframe_service.get_current_flight(request, airframe_id)
    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    dep_fluids_complete = all(dep_fluids_status.values())

    if current_flight is None:
        current_flight = from_api(
            CurrentFlight,
            client.post("current_flights/", data={"airframe_id": airframe_id})
        )
        airframe_service.invalidate_airframe_cache(request, airframe_id)

    if request.method == "POST":
        maint_release_date = request.POST.get("maint_release_date")
        maint_release_eng_company = request.POST.get("maint_release_eng_company")

        if maint_release_date is not None:
            maint_release_date = parse_datetime(maint_release_date, request.POST.get("maint_release_time"))

            current_flight = from_api(
                CurrentFlight,
                client.put(f"airframes/{airframe_id}/current_flight/", data={
                    "maint_release_date": maint_release_date,
                    "maint_release_eng_company_id": maint_release_eng_company,
                })
            )
            airframe_service.invalidate_airframe_cache(request, airframe_id)

    eng_cpy = reference_data_service.get_engineering_companies()

    return render(request, 'flight_release/maintenance.html', {
        'page_title': "Flight Sign Off",
        'maint_release_not_sent': not bool(current_flight.maint_release_date),
        'acceptance_not_sent': not bool(current_flight.acceptance_date),
        'eng_cpy': eng_cpy,
        'current_flight': current_flight,
        'current_date': datetime.now(),
        'dep_fluids_complete': dep_fluids_complete,
    })


def flight_release_acceptance(request, airframe_id):
    airframe = airframe_service.get_airframe(request, airframe_id)
    last_flight = airframe_service.get_last_flight(request, airframe_id)
    routes = airframe_service.get_routes_departing_from(
        airframe.operator.id, last_flight.actual_arrival.icao_code
    ) if last_flight and last_flight.actual_arrival else []

    departure_fluids = airframe_service.get_departure_fluids(request, airframe_id)
    fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)
    current_flight = airframe_service.get_current_flight(request, airframe_id)
    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    dep_fluids_complete = all(dep_fluids_status.values())

    if request.method == "POST":
        acceptance_date = request.POST.get("acceptance_date")

        if acceptance_date is not None:
            acceptance_date = parse_datetime(acceptance_date, request.POST.get("acceptance_time"))

            current_flight = from_api(
                CurrentFlight,
                client.put(f"airframes/{airframe_id}/current_flight/", data={
                    "acceptance_date": acceptance_date,
                    "planned_flt_number": request.POST.get("planned_flt_number"),
                })
            )
            airframe_service.invalidate_airframe_cache(request, airframe_id)

    eng_cpy = reference_data_service.get_engineering_companies()
    total_fob = sum(tank.level for tank in fluid_tanks)

    return render(request, 'flight_release/acceptance.html', {
        'airframe': airframe,
        'maintenance_release_not_sent': not bool(current_flight.maint_release_date),
        'acceptance_not_sent': not bool(current_flight.acceptance_date),
        'routes': routes,
        'eng_cpy': eng_cpy,
        'current_flight': current_flight,
        'current_date': datetime.now(),
        'page_title': "Flight Sign Off",
        'total_fob': total_fob,
    })


def flight_index(request, airframe_id):
    request.session['current_airframe_id'] = airframe_id

    defect_actions = airframe_service.get_defect_actions(request, airframe_id)
    departure_fluids = airframe_service.get_departure_fluids(request, airframe_id)
    fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)

    dep_fluids_status = fluids_are_done(departure_fluids, fluid_tanks)
    defect_counts = summarize_defect_statuses(defect_actions)

    return render(request, 'flight/index.html', {
        'page_title': "Main Menu",
        'open_defects_count': defect_counts['open'],
        'closed_defects_count': defect_counts['closed'],
        'carry_fwd_defects_count': defect_counts['carry_fwd'],
        'dep_fluids_status': dep_fluids_status,
        'dep_fluids_complete': all(dep_fluids_status.values()),
    })


def flight_details(request, airframe_id):
    defect_actions = airframe_service.get_defect_actions(request, airframe_id)
    fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)
    defect_counts = summarize_defect_statuses(defect_actions)

    last_flight = airframe_service.get_last_flight(request, airframe_id)
    current_flight = airframe_service.get_current_flight(request, airframe_id)
    flight_no_options = airframe_service.get_route_options(current_flight.planned_flt_number) if current_flight.planned_flt_number else []
    airports = reference_data_service.get_airports()
    arrival_fluids = airframe_service.get_arrival_fluids(request, airframe_id)
    arr_fluids_status = fluids_are_done(arrival_fluids, fluid_tanks)

    if request.method == "POST":
        off_blocks = parse_datetime(request.POST.get("departure_date"), request.POST.get("off_blocks"))
        off_ground = parse_datetime(request.POST.get("departure_date"), request.POST.get("off_ground"))
        on_ground = parse_datetime(request.POST.get("arrival_date"), request.POST.get("on_ground"))
        on_blocks = parse_datetime(request.POST.get("arrival_date"), request.POST.get("on_blocks"))

        current_flight = from_api(
            CurrentFlight,
            client.put(f"airframes/{airframe_id}/current_flight/", data={
                "flight_route_id": request.POST.get('flight_number'),
                "date_of_flight": request.POST.get("departure_date"),
                "off_blocks": off_blocks,
                "off_ground": off_ground,
                "on_ground": on_ground,
                "on_blocks": on_blocks,
                "callsign": request.POST.get("callsign"),
                "actual_arrival_id": request.POST.get("actual_arrival"),
            })
        )
        airframe_service.invalidate_airframe_cache(request, airframe_id)
        return JsonResponse({"success": True})

    return render(request, 'flight/details.html', {
        'page_title': "Flight Details",
        'current_flight': current_flight,
        'flight_no_options': flight_no_options,
        'open_defects_count': defect_counts['open'],
        'closed_defects_count': defect_counts['closed'],
        'carry_fwd_defects_count': defect_counts['carry_fwd'],
        'last_flight': last_flight,
        'airports': airports,
        'arr_fluids_status': arr_fluids_status,
    })


def flight_departure_fluids(request, airframe_id, fluid_type):
    if fluid_type == 0:
        template = 'flight/departure/fuel.html'
        page_title = "Departure Fuel"
    else:
        template = 'flight/departure/fluids.html'
        page_title = {1: "Departure Oil", 2: "Departure Hydraulic"}.get(fluid_type, "Departure Fluids")

    fluid_tanks = from_api_many(FluidInstance, client.get(f"airframes/{airframe_id}/fluid_instances/{fluid_type}/"))
    current_flight = airframe_service.get_current_flight(request, airframe_id)

    total_fluid = {'max_level': 0, 'units_of_measure': None, 'level': 0}
    for f in fluid_tanks:
        total_fluid["max_level"] += f.fluid_template.max_level
        total_fluid["level"] += f.level
        total_fluid["fluid_type"] = f.fluid_template.fluid_type
        total_fluid["units_of_measure"] = f.fluid_template.units_of_measure.name

    if request.method == "POST":
        nil_uplift = request.POST.get('nil_uplift')
        fluid_dict = loop_trough_fluids(request.POST, fluid_tanks, 'fluid_departure_', 'fluid_arrival_')

        try:
            with transaction.atomic():
                if fluid_type == 0:
                    refueling_form = RefuelingForm(request.POST)

                    if nil_uplift == "on":
                        save_departure_fuel_data(
                            request, airframe_id,
                            request.POST.get('planned_dep_fuel_in_kg'),
                            total_fluid['level'],
                        )
                    elif refueling_form.is_valid():
                        payload = dict(refueling_form.cleaned_data)
                        payload['planned_flt_number_id'] = payload.pop('planned_flt_number', None) or current_flight.id
                        payload['airframe_id'] = airframe_id

                        from_api(Refuel, client.post("refuels/", data=payload))
                        airframe_service.invalidate_airframe_cache(request, airframe_id)

                for fluid_id, value in fluid_dict.items():
                    tank = from_api(FluidInstance, client.get(f"fluid_instances/{fluid_id}/"))
                    departure_value = value['fluid_arrival_'] if nil_uplift == 'on' else value['fluid_departure_']

                    update_fluid_tanks(departure_value, tank)

                    existing = airframe_service.get_flight_fluid_snapshot(current_flight.id, 0, fluid_id)
                    set_flight_fluid(departure_value, tank, current_flight, 0, existing)

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('servicing', kwargs={"airframe_id": airframe_id})
            })

        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return render(request, template, {
        'page_title': page_title,
        'fluid_tanks': fluid_tanks,
        'total_fluid': total_fluid,
    })


def flight_arrival_fluids(request, airframe_id, fluid_type):
    page_title = {0: "Arrival Fuel", 1: "Arrival Oil", 2: "Arrival Hydraulic"}.get(fluid_type, "Arrival Fluids")

    current_flight = airframe_service.get_current_flight(request, airframe_id)
    fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)
    departure_fluid_tanks = airframe_service.get_departure_fluids(request, airframe_id)
    arrival_fluid_tanks = airframe_service.get_arrival_fluids(request, airframe_id)

    total_fluid = {'max_level': 0, 'units_of_measure': None, 'level': 0}
    for f in fluid_tanks:
        total_fluid["max_level"] += f.fluid_template.max_level
        total_fluid["level"] += f.level
        total_fluid["fluid_type"] = f.fluid_template.fluid_type

    if request.method == "POST":
        fluid_dict = loop_trough_fluids(request.POST, fluid_tanks, 'fluid_departure_', 'fluid_arrival_')

        try:
            with transaction.atomic():
                for fluid_id, value in fluid_dict.items():
                    tank = from_api(FluidInstance, client.get(f"fluid_instances/{fluid_id}/"))
                    arrival_value = value['fluid_arrival_'] or value['fluid_departure_']

                    update_fluid_tanks(arrival_value, tank)

                    existing = airframe_service.get_flight_fluid_snapshot(current_flight.id, 1, fluid_id)
                    set_flight_fluid(arrival_value, tank, current_flight, 1, existing)

            airframe_service.invalidate_airframe_cache(request, airframe_id)
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('flight_details', kwargs={"airframe_id": airframe_id})
            })

        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return render(request, 'flight/arrival/fluids.html', {
        'page_title': page_title,
        'fluid_tanks': fluid_tanks,
        'total_fluid': total_fluid,
        'departure_fluid_tanks': departure_fluid_tanks,
        'arrival_fluid_tanks': arrival_fluid_tanks,
    })


@require_POST
def flight_save(request, airframe_id):
    """
    TODO: this needs a dedicated API endpoint that performs the
    Refuel/FlightFluid reassignment + CurrentFlight -> Flight
    transaction server-side. Doing it as several client round-trips
    (as below) is NOT atomic across the network — if any call fails
    partway, the two databases can end up inconsistent.
    Flagging this rather than shipping a fake-atomic client version.
    """
    airframe = airframe_service.get_airframe(request, airframe_id)
    current_flight = airframe_service.get_current_flight(request, airframe_id)

    form = CompleteFlightForm({
        "airframe": airframe.id,
        "flight_route": current_flight.flight_route.id if current_flight.flight_route else None,
        "actual_arrival": current_flight.flight_route.arrival.id if current_flight.flight_route else None,
        "callsign": current_flight.callsign,
        "date_of_flight": current_flight.date_of_flight,
        "off_blocks": current_flight.off_blocks,
        "off_ground": current_flight.off_ground,
        "on_ground": current_flight.on_ground,
        "on_blocks": current_flight.on_blocks,
        "required_fuel_in_kg": current_flight.required_fuel_in_kg,
        "block_fuel_in_kg": current_flight.block_fuel_in_kg,
        "maint_release_date": current_flight.maint_release_date,
        "maint_release_eng_company": current_flight.maint_release_eng_company.id if current_flight.maint_release_eng_company else None,
        "acceptance_date": current_flight.acceptance_date,
        "planned_flt_number": current_flight.planned_flt_number,
    })

    if not form.is_valid():
        messages.error(request, f"Failed to save flight: {form.errors}")
        return redirect('flight_details', airframe_id=airframe_id)

    try:
        # See TODO above — belongs server-side as one transaction.
        flight = from_api(Flight, client.post("flights/", data=form.cleaned_data))
        client.delete(f"current_flights/{current_flight.id}/")
        airframe_service.invalidate_airframe_cache(request, airframe_id)
        return redirect('flight_index', airframe_id=airframe_id)

    except Exception as e:
        print(e)
        messages.error(request, f"Failed to save flight: {e}")
        return redirect('flight_details', airframe_id=airframe_id)


def defects(request, airframe_id):
    airframe = airframe_service.get_airframe(request, airframe_id)
    airframe_defects = defect_service.get_airframe_defects(airframe_id)
    defect_actions = defect_service.get_actions_for_airframe(airframe_id)
    defect_counts = summarize_defect_statuses(defect_actions)

    carry_fwd_action_overdue = 0
    for defect in airframe_defects:
        if defect.status == 2:
            last_action = next(
                (a for a in reversed(defect_actions) if a.airframe_defect.id == defect.id), None
            )
            if last_action and last_action.due_at and last_action.due_at < datetime.now():
                carry_fwd_action_overdue += 1

    return render(request, 'defects/index.html', {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defect_actions': defect_actions,
        'open_defects_count': defect_counts['open'],
        'closed_defects_count': defect_counts['closed'],
        'carry_fwd_defects_count': defect_counts['carry_fwd'],
        'carry_fwd_action_overdue': carry_fwd_action_overdue,
    })


def defects_this_flight(request, airframe_id):
    airframe = airframe_service.get_airframe(request, airframe_id)
    airframe_defects = defect_service.get_airframe_defects(airframe_id)
    defect_actions = defect_service.get_actions_for_airframe(airframe_id)

    return render(request, 'defects/this_flight.html', {
        'page_title': "Defects this flight",
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defect_actions': defect_actions,
    })


def defects_create(request, airframe_id):
    airframe = airframe_service.get_airframe(request, airframe_id)

    if request.method == "POST":
        form = AirframeDefectForm(request.POST)
        if form.is_valid():
            payload = dict(form.cleaned_data)
            payload['defect_id'] = payload.pop('defect', None)
            payload['airframe_id'] = airframe_id
            defect_service.create_airframe_defect(payload)
        else:
            print(form.errors)

    catalog_defects = reference_data_service.get_defects_by_family(airframe.aircraft_type.aircraft_family.id)
    airframe_defects = defect_service.get_airframe_defects(airframe_id)

    return render(request, 'defects/create.html', {
        'page_title': "Create a new defect",
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defects': catalog_defects,
    })


def defects_details(request, airframe_id, defect_id):
    airframe = airframe_service.get_airframe(request, airframe_id)
    airframe_defect = defect_service.get_airframe_defect(defect_id)
    catalog_defects = reference_data_service.get_defects_by_family(airframe.aircraft_type.aircraft_family.id)
    actions = defect_service.get_actions_for_defect(defect_id)

    if request.method == "POST":
        form = AirframeDefectForm(request.POST)
        defect_template_id = request.POST.get('defect_template')

        if form.is_valid():
            payload = dict(form.cleaned_data)
            if defect_template_id:
                payload['defect_id'] = defect_template_id
            defect_service.update_airframe_defect(defect_id, payload)
            return redirect('defects_this_flight', airframe_id=airframe_id)
        else:
            print(form.errors)

    defect_actions = defect_service.get_actions_for_airframe(airframe_id)

    return render(request, 'defects/details.html', {
        'airframe': airframe,
        'airframe_defect': airframe_defect,
        'actions': actions,
        'defects': catalog_defects,
        'defect_actions': defect_actions,
    })


def defects_actions_create(request, airframe_id, defect_id):
    airframe = airframe_service.get_airframe(request, airframe_id)
    airframe_defect = defect_service.get_airframe_defect(defect_id)
    engineering_companies = reference_data_service.get_engineering_companies()

    if request.method == "POST":
        form = ActionForm(request.POST)
        deferred_at = parse_datetime(request.POST.get("deferred_at_date"), request.POST.get("deferred_at_time"))

        if form.is_valid():
            payload = dict(form.cleaned_data)
            payload['engineering_company_id'] = payload.pop('engineering_company')
            payload['airframe_defect_id'] = defect_id
            payload['deferred_at'] = deferred_at
            defect_service.create_action(payload, defect_id)
        else:
            print(form.errors)

    return render(request, 'defects/actions/create.html', {
        'page_title': f"Create action for {airframe_defect.defect_title}",
        'airframe': airframe,
        'engineering_companies': engineering_companies,
        'airframe_defect': airframe_defect,
    })


def defects_actions_edit(request, airframe_id, defect_id, action_id):
    airframe = airframe_service.get_airframe(request, airframe_id)
    airframe_defect = defect_service.get_airframe_defect(defect_id)
    engineering_companies = reference_data_service.get_engineering_companies()
    action = defect_service.get_action(action_id)

    if request.method == "POST":
        form = ActionForm(request.POST)
        deferred_at = parse_datetime(request.POST.get("deferred_at_date"), request.POST.get("deferred_at_time"))

        if form.is_valid():
            payload = dict(form.cleaned_data)
            payload['engineering_company_id'] = payload.pop('engineering_company')
            payload['deferred_at'] = deferred_at
            defect_service.update_action(action_id, payload, defect_id)
            return redirect('defects_details', airframe_id=airframe_id, defect_id=defect_id)
        else:
            print(form.errors)

    return render(request, 'defects/actions/create.html', {
        'page_title': "Action Edit",
        'airframe': airframe,
        'action': action,
        'engineering_companies': engineering_companies,
        'airframe_defect': airframe_defect,
    })


def servicing(request, airframe_id):
    fluid_tanks = airframe_service.get_fluid_tanks(request, airframe_id)
    departure_fluid_tanks = airframe_service.get_departure_fluids(request, airframe_id)
    dep_fluids_status = fluids_are_done(departure_fluid_tanks, fluid_tanks)

    return render(request, 'servicing/index.html', {
        'page_title': "Servicing",
        'dep_fluids_status': dep_fluids_status,
    })


def servicing_refuel_list(request, airframe_id):
    refuel_list = from_api_many(Refuel, client.get(f"airframes/{airframe_id}/refuels/"))
    refuel_list = [r for r in refuel_list if r.actual_flight is None]
    return render(request, 'servicing/refuel_list.html', {'refuel_list': refuel_list})


def flight_ice_protection(request):
    return render(request, 'ice_protection.html', {})


def planned_maintenance(request):
    return render(request, 'planned_maintenance.html', {})