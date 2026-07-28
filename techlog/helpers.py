from datetime import datetime

from techlog.forms import CurrentFlightArrivalFluids, CurrentFlightDepartureFluids, UpdateFluidTanks


def parse_datetime(date_str, time_str):
    """
    Returns a datetime or None.
    """
    if not date_str or not time_str:
        return None

    try:
        return datetime.strptime(
            f"{date_str} {time_str}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return None
    
def parse_date(date_str):    
    """
    Returns a datetime or None.
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(
            f"{date_str}",
            "%Y-%m-%d"
        )
    
    except ValueError:
        return None

def loop_trough_fluids(post, tanks, *args):
    """Convert posted fluid values into a structured dictionary for processing."""
    return_dict = {}
    
    for tank in tanks:
        return_dict[tank.id] = {}
        for arg in args:
            key = f"{arg}{tank.id}"
            return_dict[tank.id][arg] = post[key]

    return return_dict

def update_fluid_tanks(value, tank):

    """Update a fluid tank instance with a new fluid value."""
    data = {
        "level": value,
        "fluid": tank
    }
    print(f'fluid tanks update data:   {data}')

    form = UpdateFluidTanks(data=data, instance=tank)

    if form.is_valid():
        form.save()
    else:
        return form.errors

def set_flight_fluid(value, tank, flight, phase, status, flight_fluid_instance=None):

    """Store a flight fluid record for the current flight and phase."""
    print(f'flight fluid val dict:   {value}')
    data = {
        'fluid': tank.id,
        'level': value
    }

    if status == 'draft':
        data['current_flight'] = flight
        print(f'current flight is being updated:   {flight}')

        if phase == 0:

            print(f'flight fluid data for departure dict:   {data}')
            if flight_fluid_instance is not None:
                form = CurrentFlightDepartureFluids(data=data, instance=flight_fluid_instance)
            else:
                form = CurrentFlightDepartureFluids(data=data)

        if phase == 1:

            print(f'flight fluid data for arrival dict:   {data}')
            if flight_fluid_instance is not None:
                form = CurrentFlightArrivalFluids(data=data, instance=flight_fluid_instance)
            else:
                form = CurrentFlightArrivalFluids(data=data)
    
    if form.is_valid():
        obj = form.save()
        print(f'Fluid update form returned valid:   {obj}')
    else:
        print(form.errors)

def save_departure_fuel_data(current_flight, fuel_required, block_fuel):
    """Save departure fuel summary values for the current flight."""
    current_flight.required_fuel_in_kg = fuel_required
    current_flight.block_fuel_in_kg = block_fuel
    current_flight.refuel_is_done = True
    current_flight.save()
    print(f'departure fuel saved:--------------------- fuel required: {fuel_required}, block fuel {block_fuel}')

def fluids_are_done(flight_fluids, fluid_instances):
    """Return completion status for fluid checks across the flight."""
    fluids_statuses = {
        'fuel': False,
        'oil': False,
        'hyd': False,
        'water': False,
    }

    fluid_type_map = {
        'fuel': 0,
        'oil': 1,
        'hyd': 2,
        'water': 3,
    }

    for status_key, fluid_type in fluid_type_map.items():
        instance_count = sum(
            1 for fi in fluid_instances
            if fi.fluid_template.fluid_type == fluid_type
        )
        flight_fluid_count = sum(
            1 for ff in flight_fluids
            if ff.fluid.fluid_template.fluid_type == fluid_type
        )
        fluids_statuses[status_key] = instance_count == flight_fluid_count

    return fluids_statuses

def summarize_defect_statuses(defect_actions):
    counts = {'open': 0, 'closed': 0, 'carry_fwd': 0}
    status_map = {0: 'open', 1: 'closed', 2: 'carry_fwd'}
    for defect in defect_actions:
        key = status_map.get(defect.status)
        if key:
            counts[key] += 1
    return counts
