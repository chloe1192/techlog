from datetime import datetime

from techlog.api import TechlogClient
from techlog.mapping import from_api
from techlog.services.airframe_service import invalidate_airframe_cache
from techlog.state import FluidInstance, FlightFluid, FlightPhase

client = TechlogClient()


def parse_datetime(date_str, time_str):
    if not date_str or not time_str:
        return None
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(f"{date_str}", "%Y-%m-%d")
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
    """Update a fluid tank instance's current level via the API."""
    res = from_api(FluidInstance, client.put(
        f"fluid_instances/{tank.id}/",
        data={"level": value}
    ))
    return bool(res)


def set_flight_fluid(value, tank, current_flight, phase, flight_fluid_instance=None):
    """
    Create or update a FlightFluid snapshot (historical record) for the
    given current_flight + phase + tank, via the API.
    """
    payload = {
        "fluid_id": tank.id,
        "current_flight_id": current_flight.id,
        "phase": phase,
        "level": value,
    }

    if flight_fluid_instance is not None:
        return from_api(
            FlightFluid,
            client.put(f"flight_fluids/{flight_fluid_instance.id}/", data=payload)
        )

    return from_api(
        FlightFluid,
        client.post("flight_fluids/", data=payload)
    )


def save_departure_fuel_data(request, airframe_id, fuel_required, block_fuel):
    """
    Save the dispatch-required fuel and the actual fuel loaded (block fuel)
    for the current flight, via the API.
    """
    from techlog.state import CurrentFlight

    result = from_api(
        CurrentFlight,
        client.put(f"airframes/{airframe_id}/current_flight/", data={
            "required_fuel_in_kg": fuel_required,
            "block_fuel_in_kg": block_fuel,
        })
    )
    invalidate_airframe_cache(request, airframe_id)
    return result


def fluids_are_done(flight_fluids, fluid_instances):
    fluids_statuses = {'fuel': False, 'oil': False, 'hyd': False, 'water': False}
    fluid_type_map = {'fuel': 0, 'oil': 1, 'hyd': 2, 'water': 3}

    for status_key, fluid_type in fluid_type_map.items():
        instance_count = sum(
            1 for fi in fluid_instances
            if fi.fluid_template and fi.fluid_template.fluid_type == fluid_type
        )
        flight_fluid_count = sum(
            1 for ff in flight_fluids
            if ff.fluid and ff.fluid.fluid_template and ff.fluid.fluid_template.fluid_type == fluid_type
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