from datetime import datetime
from decimal import Decimal
from itertools import chain

from django.urls import reverse

from .forms import AcceptanceForm, AirframeDefectCreateForm, AirframeEdit, AirframeEngineEdit, MaintenanceReleaseForm, RefuelingForm

from .models import Action, AircraftTypeFluid, Airframe, AirframeDefect, AircraftType, AirframeEngine, CurrentFlight, EngineModel, EngineFluids, Company, Defect, EngineModelFluid, EngineeringCompany, Operator, AirframeFluid, Flight, Airport, Refuel
from django.shortcuts import get_object_or_404, redirect, render

def index(request):
    operators = Operator.objects.all()
    context = {
        'operators': operators,
    }
    return render(request, 'index.html', context)

def airframes_list(request, id=0):
    request.session['current_operator_id'] = id
    page_title = "Operator Selection"
    return_url = reverse("index")
    airframes = Airframe.objects.filter(operator=id)
    return_url = request.META.get("HTTP_REFERER")

    context = {
        'airframes': airframes,
        'return_url': return_url,
        'page_title': page_title,
    }
    return render(request, 'airframes/list.html', context)

def airframes_edit(request, id):
    request.session['current_operator_id'] = id
    page_title = "Operator Selection"
    return_url = reverse("index")
    airframe = get_object_or_404(Airframe, id=id)
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
        
        if request.POST.get("action") == "create_engine_fluids_instance":
            engine_type_fluids = EngineModelFluid.objects.filter(engine_model=engine_type_current.engine_model)
            if engine_model_current.exists():
                for fluid in engine_type_fluids:

                    for engine in engine_model_current:
                        if fluid.engine_number == engine.engine_number:
                            print(f"fluid.engine_number; {fluid.engine_number} {fluid}")
                            EngineFluids.objects.create(
                                engine_model_fluid=fluid,
                                item=fluid.item,
                                level=fluid.default_level,
                                units_of_measure=fluid.units_of_measure,
                                max_level=fluid.max_level,
                                fluid_type=fluid.fluid_type,
                                airframe_engine=engine,
                                engine_number=engine.engine_number
                            )
 
            else:
                print("No engines")

        if request.POST.get("action") == "create_airframe_fluids_instance":
            aircraft_type_fluids = AircraftTypeFluid.objects.filter(aircraft_type=aircraft_type_current)
            for fluid in aircraft_type_fluids:
                print(f"fluid; {fluid} {airframe}")
                AirframeFluid.objects.create(
                    aircraft_type_fluid=fluid,
                    item=fluid.item,
                    level=fluid.default_level,
                    units_of_measure=fluid.units_of_measure,
                    max_level=fluid.max_level,
                    fluid_type=fluid.fluid_type,
                    airframe=airframe
                )

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

def airframe_index(request, airframe_id):
    request.session['current_airframe_id'] = airframe_id
    page_title = "Main Menu"
    current_flight = CurrentFlight.objects.filter(airframe=airframe_id).order_by("-created_at").first()
    airframe = get_object_or_404(Airframe, id=airframe_id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    engine_fluids = EngineFluids.objects.filter(airframe_engine=airframe_id)
    airframe_fluids = AirframeFluid.objects.filter(airframe=airframe)
    defect_actions = Action.objects.filter(airframe_defect__airframe=airframe_id)
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

def flight_index(request, id):
    request.session['current_airframe_id'] = id
    page_title = "Main Menu"
    current_flight = CurrentFlight.objects.filter(airframe=id).order_by("-created_at").first()
    airframe = get_object_or_404(Airframe, id=id)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    engine_fluids = EngineFluids.objects.filter(airframe_engine=id)
    airframe_fluids = AirframeFluid.objects.filter(airframe=airframe)
    defect_actions = Action.objects.filter(airframe_defect__airframe=id)
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
    return render(request, 'flight/index.html', context)

def flight_release_maintenance(request, id):
    page_title = "Flight Sign Off"
    return_url = request.META.get("HTTP_REFERER")
    airframe = get_object_or_404(Airframe, id=id)
    current_flight = CurrentFlight.objects.filter(airframe=airframe).first()

    if current_flight is None:
        current_flight = CurrentFlight.objects.create(airframe=airframe)

    if request.method == "POST":
        print(request.POST)
        print(f"request.POST[maint_release_date] {request.POST["maint_release_date"]}")
        maint_release_date = request.POST.get("maint_release_date")
        acceptance_date = request.POST.get("acceptance_date")
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
                else:
                    print(form.errors)
        if acceptance_date is not None:
            acceptance_date = f"{request.POST["acceptance_date"]} {request.POST["acceptance_time"]}"
            acceptance_date = datetime.strptime(acceptance_date, "%Y-%m-%d %H:%M")

            if current_flight is not None:
                form = AcceptanceForm(request.POST, instance=current_flight)

                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.maint_release_date = maint_release_date
                    obj.airframe = airframe
                    obj.save()
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

def flight_release_acceptance(request, id):
    page_title = "Flight Sign Off"
    return_url = request.META.get("HTTP_REFERER")
    airframe = get_object_or_404(Airframe, id=id)
    current_flight = CurrentFlight.objects.filter(airframe=airframe).first()

    if current_flight is None:
        current_flight = CurrentFlight.objects.create(airframe=airframe)

    if request.method == "POST":
        print('request.POST["maint_release_date"]')
        print(request.POST)
        maint_release_date = request.POST.get("maint_release_date")
        acceptance_date = request.POST.get("acceptance_date")
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
                else:
                    print(form.errors)
        if acceptance_date is not None:
            acceptance_date = f"{request.POST["acceptance_date"]} {request.POST["acceptance_time"]}"
            acceptance_date = datetime.strptime(acceptance_date, "%Y-%m-%d %H:%M")

            if current_flight is not None:
                form = AcceptanceForm(request.POST, instance=current_flight)

                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.maint_release_date = maint_release_date
                    obj.airframe = airframe
                    obj.save()
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
    context = {
        'airframe': airframe,
        'maintenance_release_not_sent': maintenance_release_not_sent,
        'acceptance_not_sent': acceptance_not_sent,
        'eng_cpy': eng_cpy,
        'current_flight': current_flight,
        'current_date': current_date,
        'return_url': return_url,
        'page_title': page_title
    }
    return render(request, 'flight_release/acceptance.html', context)

def operator_index(request, id=0):
    request.session['current_operator_id'] = id
    page_title = "Operator Selection"
    return_url = reverse("index")
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

def defects_this_flight(request, id):
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

def defects_create(request, id):
    airframe = get_object_or_404(Airframe, id=id)

    if request.method == "POST":
        form = AirframeDefectCreateForm(request.POST)
        if form.is_valid():
            print("form")
            obj = form.save(commit=False)
            obj.airframe = airframe
            obj.save()
        else:
            print(form.errors)

    defects = Defect.objects.all()
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    print(airframe_defects)
    context = {
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'defects': defects
    }
    return render(request, 'defects/create.html', context)

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

def servicing(request, id):
    page_title = "Servicing"
    return_url = reverse("flight_index", kwargs={"id": id})
    airframe = get_object_or_404(Airframe, id=id)
    airframe_fluids = AirframeFluid.objects.filter(airframe=airframe)
    engine_fluids = EngineFluids.objects.filter(airframe_engine__airframe=airframe)
    airframe_defects = AirframeDefect.objects.filter(airframe=airframe)
    current_flight = CurrentFlight.objects.filter(airframe=id).order_by("-created_at").first()
    print("refuel_is_done")
    print(current_flight.refuel_is_done)
    print("oil_is_done")
    print(current_flight.oil_is_done)
    print("hyd_is_done")
    print(current_flight.hyd_is_done)
    print("water_is_done")
    print(current_flight.water_is_done)

    context = {
        'page_title': page_title,
        'return_url': return_url,
        'airframe': airframe,
        'airframe_defects': airframe_defects,
        'airframe_fluids': airframe_fluids,
        'engine_fluids': engine_fluids,
        'current_flight': current_flight
    }
    return render(request, 'servicing/index.html', context)

def servicing_fuel(request, id):
    page_title = "Fuel Uplift"
    return_url = reverse("servicing", kwargs={"id": id})
    airframe = get_object_or_404(Airframe, id=id)
    current_flight = CurrentFlight.objects.filter(airframe=id).order_by("-created_at").first()
   
    total_fuel = {
        'max_level': 0,
        'units_of_measure': 0,
        'level': 0,
    }
    fuel_tanks = AirframeFluid.objects.filter(airframe_id=id, fluid_type=0)
    for tank in fuel_tanks:
        total_fuel['max_level'] = tank.max_level + total_fuel['max_level']
        total_fuel['units_of_measure'] = tank.get_units_of_measure_display
        total_fuel['level'] = tank.level + total_fuel['level']
        
    fuel_uplift_not_sent = True

    if request.method == "POST":
        print(request.POST)
        form = RefuelingForm(request.POST)
        print(form.is_valid())
        nil_uplift = request.POST.get('nil_uplift')
        print("request.POST['nil_uplift']")
        print(nil_uplift)
        if nil_uplift == "on":
            print("if nil_uplift == on:") 
            current_flight.refuel_is_done = True
            current_flight.save()
            return redirect("servicing", id=id)
        
        if form.is_valid():
            obj = form.save(commit=False)
            obj.airframe = airframe
            obj.save()
            
            fuel_tanks = AirframeFluid.objects.filter(
                airframe=airframe,
                fluid_type=0  # fuel
            )
            current_flight.refuel_is_done = True
            current_flight.save()

            for tank in fuel_tanks:
                key = f"departure_fob_in_kg_{tank.id}"
                print("key")
                print(key)
                uplift = request.POST.get(key)
                print("uplift")
                print(uplift)

                if uplift:
                    tank.level = uplift
                    print("tank.level")
                    print(tank.level)
                    tank.save()
        else:
            print(form.errors)

    context = {
        'fuel_uplift_not_sent': fuel_uplift_not_sent,
        'page_title': page_title,
        'return_url': return_url,
        'total_fuel': total_fuel,
        'fuel_tanks': fuel_tanks,
        'current_flight': current_flight
    }
    return render(request, 'servicing/fuel.html', context)

def servicing_oil(request, id):
    page_title = "Fuel Uplift"
    return_url = reverse("servicing", kwargs={"id": id})
    airframe = get_object_or_404(Airframe, id=id)
    current_flight = CurrentFlight.objects.filter(airframe=id).order_by("-created_at").first()
    engine_oil_tanks = EngineFluids.objects.filter(airframe_engine__airframe_id=id, fluid_type=1)
    airframe_oil_tanks = AirframeFluid.objects.filter(airframe_id=id, fluid_type=1)
        
    oil_uplift_not_sent = True

    if request.method == "POST":
        print(request.POST)

        nil_uplift = request.POST['nil_uplift']
        print("request.POST['nil_uplift']")
        print(nil_uplift)
        if nil_uplift == "on":
            current_flight.oil_is_done = True
            current_flight.save()
            return redirect("servicing", id=id)

        for key, value in request.POST.items():

            if not key.startswith("oil_uplift_"):
                continue

            if not value.strip():
                continue

            tank_id = key.replace("oil_uplift_", "")
            print("tank_id")
            print(tank_id)

            try:
                tank = EngineFluids.objects.get(
                    id=tank_id,
                    fluid_type=1
                )
                print("tank")
                print(tank)

                uplift = value
                print("uplift")
                print(uplift)

                print("tank.level")
                print(tank.level)

                tank.level = float(tank.level) + float(uplift)
                tank.save(update_fields=["level"])
                print("tank.level")
                print(tank.level)
                current_flight.oil_is_done = True
                current_flight.save()

            except EngineFluids.DoesNotExist:
                print(f"Oil tank {tank_id} not found")

        return redirect("servicing", id=id)

    context = {
        'oil_uplift_not_sent': oil_uplift_not_sent,
        'page_title': page_title,
        'airframe_oil_tanks': airframe_oil_tanks,
        'engine_oil_tanks': engine_oil_tanks,
        'return_url': return_url,
        'current_flight': current_flight
    }
    return render(request, 'servicing/oil.html', context)

def servicing_hyd(request, id):
    page_title = "Fuel Uplift"
    return_url = reverse("servicing", kwargs={"id": id})
    airframe = get_object_or_404(Airframe, id=id)
    current_flight = CurrentFlight.objects.filter(airframe=id).order_by("-created_at").first()
    engine_hyd_tanks = EngineFluids.objects.filter(airframe_engine__airframe_id=id, fluid_type=2)
    airframe_hyd_tanks = AirframeFluid.objects.filter(airframe_id=id, fluid_type=2)
        
    hyd_uplift_not_sent = True

    if request.method == "POST":
        print(request.POST)

        hyd_nil_uplift = request.POST['hyd_nil_uplift']
        print("request.POST['hyd_nil_uplift']")
        print(hyd_nil_uplift)
        if hyd_nil_uplift == "on":
            current_flight.hyd_is_done = True
            current_flight.save()
            return redirect("servicing", id=id)

        for key, value in request.POST.items():

            if not key.startswith("hyd_uplift_"):
                continue

            if not value.strip():
                continue

            tank_id = key.replace("hyd_uplift_", "")
            print("tank_id")
            print(tank_id)

            try:
                tank = AirframeFluid.objects.get(
                    id=tank_id,
                    fluid_type=2
                )
                print("tank")
                print(tank)

                uplift = value
                print("uplift")
                print(uplift)

                print("tank.level")
                print(tank.level)

                tank.level = float(tank.level) + float(uplift)
                tank.save(update_fields=["level"])
                print("tank.level")
                print(tank.level)
                current_flight.hyd_is_done = True
                current_flight.save()

            except AirframeFluid.DoesNotExist:
                print(f"hyd tank {tank_id} not found")

            try:
                tank = EngineFluids.objects.get(
                    id=tank_id,
                    fluid_type=2
                )
                print("tank")
                print(tank)

                uplift = value
                print("uplift")
                print(uplift)

                print("tank.level")
                print(tank.level)

                tank.level = float(tank.level) + float(uplift)
                tank.save(update_fields=["level"])
                print("tank.level")
                print(tank.level)
                current_flight.hyd_is_done = True
                current_flight.save()

            except EngineFluids.DoesNotExist:
                print(f"hyd tank {tank_id} not found")

        return redirect("servicing", id=id)

    context = {
        'hyd_uplift_not_sent': hyd_uplift_not_sent,
        'page_title': page_title,
        'airframe_hyd_tanks': airframe_hyd_tanks,
        'engine_hyd_tanks': engine_hyd_tanks,
        'return_url': return_url,
        'current_flight': current_flight
    }
    return render(request, 'servicing/hyd.html', context)

def servicing_water(request, id):
    page_title = "Fuel Uplift"
    return_url = reverse("servicing", kwargs={"id": id})
    airframe = get_object_or_404(Airframe, id=id)
    current_flight = CurrentFlight.objects.filter(airframe=id).order_by("-created_at").first()
    engine_water_tanks = EngineFluids.objects.filter(airframe_engine__airframe_id=id, fluid_type=3)
    airframe_water_tanks = AirframeFluid.objects.filter(airframe_id=id, fluid_type=3)
        
    water_uplift_not_sent = True

    if request.method == "POST":
        print(request.POST)

        water_nil_uplift = request.POST.get('water_nil_uplift')
        print("request.POST['water_nil_uplift']")
        print(water_nil_uplift)
        if water_nil_uplift == "on":
            current_flight.water_is_done = True
            current_flight.save()
            return redirect("servicing", id=id)

        for key, value in request.POST.items():

            if not key.startswith("water_uplift_"):
                continue

            if not value.strip():
                continue

            tank_id = key.replace("water_uplift_", "")
            print("tank_id")
            print(tank_id)

            try:
                tank = AirframeFluid.objects.get(
                    id=tank_id,
                    fluid_type=3
                )
                print("tank")
                print(tank)

                uplift = value
                print("uplift")
                print(uplift)

                print("tank.level")
                print(tank.level)

                tank.level = float(tank.level) + float(uplift)
                tank.save(update_fields=["level"])
                print("tank.level")
                print(tank.level)
                current_flight.water_is_done = True
                current_flight.save()

            except AirframeFluid.DoesNotExist:
                print(f"water tank {tank_id} not found")

            try:
                tank = EngineFluids.objects.get(
                    id=tank_id,
                    fluid_type=3
                )
                print("tank")
                print(tank)

                uplift = value
                print("uplift")
                print(uplift)

                print("tank.level")
                print(tank.level)

                tank.level = float(tank.level) + float(uplift)
                tank.save(update_fields=["level"])
                print("tank.level")
                print(tank.level)
                current_flight.water_is_done = True
                current_flight.save()

            except EngineFluids.DoesNotExist:
                print(f"water tank {tank_id} not found")

        return redirect("servicing", id=id)

    context = {
        'water_uplift_not_sent': water_uplift_not_sent,
        'page_title': page_title,
        'airframe_water_tanks': airframe_water_tanks,
        'engine_water_tanks': engine_water_tanks,
        'return_url': return_url,
        'current_flight': current_flight
    }
    return render(request, 'servicing/water.html', context)

def servicing_refuel_list(request, airframe_id):
    refuel_list = Refuel.objects.filter(airframe=airframe_id,actual_flight=None)
    context = {
        'refuel_list': refuel_list
        }

    return render(request, 'servicing/refuel_list.html', context)

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
