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
    return_dict = {}
    
    for tank in tanks:
        return_dict[tank.id] = {}
        for arg in args:
            key = f"{arg}{tank.id}"
            return_dict[tank.id][arg] = post[key]

    return return_dict

def update_fluid_tanks(value, tank):

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
    current_flight.required_fuel_in_kg = fuel_required
    current_flight.block_fuel_in_kg = block_fuel
    current_flight.refuel_is_done = True
    current_flight.save()
    print(f'departure fuel saved:--------------------- fuel required: {fuel_required}, block fuel {block_fuel}')