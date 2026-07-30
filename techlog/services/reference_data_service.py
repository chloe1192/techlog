"""Reference/lookup data — operators, aircraft types, engines, etc.
Not airframe-scoped, so not cached the same way as airframe_service."""

from techlog.api import TechlogClient
from techlog.mapping import from_api, from_api_many
from techlog.state import (
    Operator, AircraftType, EngineModel, AirframeEngine, FluidTemplate,
    Defect, EngineeringCompany, Airport, Airframe,
)

client = TechlogClient()


def get_operators():
    return from_api_many(Operator, client.get("operators/"))


def get_operator(operator_id):
    return from_api(Operator, client.get(f"operators/{operator_id}/"))


def get_aircraft_types():
    return from_api_many(AircraftType, client.get("aircraft_types/"))


def get_aircraft_type(aircraft_type_id):
    return from_api(AircraftType, client.get(f"aircraft_types/{aircraft_type_id}/"))


def get_engine_models():
    return from_api_many(EngineModel, client.get("engine_models/"))


def get_airframe_engines(airframe_id):
    return from_api_many(AirframeEngine, client.get(f"airframes/{airframe_id}/engines/"))


def create_airframe_engine(payload):
    return from_api(AirframeEngine, client.post("airframe_engines/", data=payload))


def get_fluid_templates_for_airframe(airframe_id):
    return from_api_many(FluidTemplate, client.get(f"airframes/{airframe_id}/fluid_templates/"))


def create_fluid_instance(payload):
    from techlog.state import FluidInstance
    return from_api(FluidInstance, client.post("fluid_instances/", data=payload))


def get_defects_by_family(aircraft_family_id):
    return from_api_many(Defect, client.get(f"defects/aircraft_family/{aircraft_family_id}/"))


def get_engineering_companies():
    return from_api_many(EngineeringCompany, client.get("engineering_companies/"))


def get_airports():
    return from_api_many(Airport, client.get("airports/"))


def create_airframe(payload):
    return from_api(Airframe, client.post("airframes/", data=payload))


def update_airframe(airframe_id, payload):
    return from_api(Airframe, client.put(f"airframes/{airframe_id}/", data=payload))