# techlog/state.py

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import IntEnum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums (mirror Django IntegerChoices — same names/values, so template
# comparisons like `defect.status == ActionTypes.OPEN` keep working)
# ---------------------------------------------------------------------------

class FluidTypes(IntEnum):
    FUEL = 0
    OIL = 1
    HYD = 2
    WATER = 3


class UnitsOfMeasure(IntEnum):
    LT = 0
    QTS = 1
    PCT = 2
    GAL = 3
    KG = 4


class FuelPenaltyTypes(IntEnum):
    NO = 0
    PCT = 1
    KG = 2
    LBS = 3


class ActionTypes(IntEnum):
    OPEN = 0
    CLOSED = 1
    CFWD = 2


class DeferCategory(IntEnum):
    NA = 0
    DML = 1
    CDL = 2
    MEL_D = 3
    MEL_C = 4
    MEL_B = 5
    MEL_A = 6


class CurrentFlightStatus(IntEnum):
    DRAFT = 0
    IN_PROGRESS = 1
    READY_TO_SUBMIT = 2


class AirframeOrEngineFluid(IntEnum):
    AIRFRAME = 0
    ENGINE = 1


class ProcedureRequired(IntEnum):
    NONE = 0
    M = 1
    O = 2
    MO = 3


class FluidOwnerType(IntEnum):
    AIRFRAME = 0
    ENGINE = 1


class FlightPhase(IntEnum):
    DEPARTURE = 0
    ARRIVAL = 1


# ---------------------------------------------------------------------------
# Models (dataclasses mirror Django model field names 1:1)
# ---------------------------------------------------------------------------

@dataclass
class Company:
    id: Optional[int] = None
    name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return self.name


@dataclass
class EngineeringCompany:
    id: Optional[int] = None
    name: str = ""
    code: str = ""

    def __str__(self):
        return f"{self.code} - {self.name}"


@dataclass
class Operator:
    id: Optional[int] = None
    name: str = ""
    iata_code: str = ""
    icao_code: str = ""
    company: Optional[Company] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return self.icao_code


@dataclass
class AircraftFamily:
    id: Optional[int] = None
    name: str = ""
    manufacturer: str = ""

    def __str__(self):
        return self.name


@dataclass
class AircraftType:
    id: Optional[int] = None
    name: str = ""
    aircraft_family: Optional[AircraftFamily] = None
    icao_code: str = ""
    manufacturer_empty_weight: Optional[int] = None
    basic_empty_weight: Optional[int] = None
    operating_empty_weight: Optional[int] = None
    max_zero_fuel_weight: Optional[int] = None
    max_landing_weight: Optional[int] = None
    max_takeoff_weight: Optional[int] = None
    max_ramp_weight: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return self.name


@dataclass
class Defect:
    id: Optional[int] = None
    title: str = ""
    ata_chapter: Optional[int] = None
    ata_section: Optional[int] = None
    ata_item: str = ""
    interval: DeferCategory = DeferCategory.NA
    installed_qty: Optional[int] = None
    required_qty: Optional[int] = None
    procedure: ProcedureRequired = ProcedureRequired.NONE
    maint_note: Optional[str] = None
    operations: Optional[str] = None
    fuel_penalty: Optional[Decimal] = None
    fuel_penalty_type: FuelPenaltyTypes = FuelPenaltyTypes.NO
    aircraft_family: Optional[AircraftFamily] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return f"{self.title} --- {self.ata_chapter}-{self.ata_section}-{self.ata_item}"


@dataclass
class EngineModel:
    id: Optional[int] = None
    name: str = ""
    thrust: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return self.name


@dataclass
class Airframe:
    id: Optional[int] = None
    registration: str = ""
    msn: Optional[int] = None
    date_of_build: Optional[date] = None
    aircraft_type: Optional[AircraftType] = None
    operator: Optional[Operator] = None
    standard_empty_weight: Optional[int] = None
    basic_empty_weight: Optional[int] = None
    manufacturer_empty_weight: Optional[int] = None
    operating_empty_weight: Optional[int] = None
    max_zero_fuel_weight: Optional[int] = None
    max_landing_weight: Optional[int] = None
    max_takeoff_weight: Optional[int] = None
    max_ramp_weight: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return self.registration


@dataclass
class AirframeEngine:
    id: Optional[int] = None
    engine_model: Optional[EngineModel] = None
    airframe: Optional[Airframe] = None
    engine_hours: Optional[int] = None
    engine_number: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return f"{self.airframe} {self.engine_number}"


@dataclass
class FluidTemplate:
    id: Optional[int] = None
    name: str = ""
    owner_type: Optional[FluidOwnerType] = None
    aircraft_type: Optional[AircraftType] = None
    engine_model: Optional[EngineModel] = None
    fluid_type: Optional[FluidTypes] = None
    units_of_measure: Optional[UnitsOfMeasure] = None
    max_level: Optional[Decimal] = None

    def __str__(self):
        if self.owner_type == FluidOwnerType.AIRFRAME:
            return f"{self.name} - {self.aircraft_type}"

        if self.owner_type == FluidOwnerType.ENGINE:
            return f"{self.name} - {self.engine_model} "

        return self.name


@dataclass
class FluidInstance:
    id: Optional[int] = None
    fluid_template: Optional[FluidTemplate] = None
    airframe: Optional[Airframe] = None
    airframe_engine: Optional[AirframeEngine] = None
    level: Optional[Decimal] = None

    def __str__(self):
        if self.fluid_template and self.fluid_template.owner_type == FluidOwnerType.AIRFRAME:
            return f"{self.fluid_template.name} - {self.airframe}"

        if self.fluid_template and self.fluid_template.owner_type == FluidOwnerType.ENGINE:
            return f"{self.fluid_template.name} {self.airframe_engine.engine_number} - {self.airframe_engine} "

        return f"{self.fluid_template} = {self.level}"


@dataclass
class Airport:
    id: Optional[int] = None
    iata_code: str = ""
    icao_code: str = ""
    name: str = ""
    city: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return self.iata_code


@dataclass
class Route:
    id: Optional[int] = None
    operator: Optional[Operator] = None
    flt_number: Optional[str] = None
    departure: Optional[Airport] = None
    arrival: Optional[Airport] = None
    scheduled_off_ground: Optional[time] = None
    scheduled_on_ground: Optional[time] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        dep = self.departure.iata_code if self.departure else ""
        arr = self.arrival.iata_code if self.arrival else ""
        return f"{self.flt_number} - {dep} - {arr}"


@dataclass
class Flight:
    id: Optional[int] = None
    airframe: Optional[Airframe] = None
    flight_route: Optional[Route] = None
    actual_arrival: Optional[Airport] = None
    callsign: str = ""
    date_of_flight: Optional[date] = None
    off_blocks: Optional[datetime] = None
    off_ground: Optional[datetime] = None
    on_ground: Optional[datetime] = None
    on_blocks: Optional[datetime] = None
    required_fuel_in_kg: Optional[int] = None
    block_fuel_in_kg: Optional[int] = None
    maint_release_date: Optional[datetime] = None
    maint_release_eng_company: Optional[EngineeringCompany] = None
    acceptance_date: Optional[datetime] = None
    planned_flt_number: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        registration = self.airframe.registration if self.airframe else ""
        return f"{self.flight_route} {self.date_of_flight} {registration}"


@dataclass
class CurrentFlight:
    id: Optional[int] = None
    airframe: Optional[Airframe] = None
    flight_route: Optional[Route] = None
    status: CurrentFlightStatus = CurrentFlightStatus.DRAFT
    actual_arrival: Optional[Airport] = None
    callsign: Optional[str] = None
    date_of_flight: Optional[date] = None
    off_blocks: Optional[datetime] = None
    off_ground: Optional[datetime] = None
    on_ground: Optional[datetime] = None
    on_blocks: Optional[datetime] = None
    required_fuel_in_kg: Optional[int] = None
    block_fuel_in_kg: Optional[int] = None
    maint_release_date: Optional[datetime] = None
    maint_release_eng_company: Optional[EngineeringCompany] = None
    acceptance_date: Optional[datetime] = None
    planned_flt_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Refuel:
    id: Optional[int] = None
    planned_flt_number: Optional[CurrentFlight] = None
    actual_flight: Optional[Flight] = None
    airframe: Optional[Airframe] = None
    planned_dep_fuel_in_kg: Optional[int] = None
    specific_gravity: Optional[Decimal] = None
    required_uplift_in_lt: Optional[int] = None
    pre_refuel_in_kg: Optional[int] = None
    departure_fob_in_kg: Optional[int] = None
    fuel_supplier: str = ""
    fuel_ticket_no: str = ""
    bowser_uplift_in_lt: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class AirframeDefect:
    id: Optional[int] = None
    airframe: Optional[Airframe] = None
    defect_title: str = ""
    defect: Optional[Defect] = None
    is_pilot_report: bool = True
    is_cabin_log: bool = False
    crs_not_required: bool = False
    is_etops: bool = False
    ecam_message: Optional[str] = None
    defect_text: Optional[str] = None
    flight: Optional[Flight] = None
    status: ActionTypes = ActionTypes.OPEN
    noticed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        registration = self.airframe.registration if self.airframe else ""
        return f"{registration} - {self.defect_title} - {self.noticed_at}"


@dataclass
class Action:
    id: Optional[int] = None
    status: ActionTypes = ActionTypes.CLOSED
    time: Optional[datetime] = None
    desc: Optional[str] = None
    airframe_defect: Optional[AirframeDefect] = None
    category: DeferCategory = DeferCategory.NA
    engineering_company: Optional[EngineeringCompany] = None
    defer_reason: Optional[str] = None
    deferred_at: Optional[datetime] = None
    due_at: Optional[datetime] = None


@dataclass
class Cabin:
    id: Optional[int] = None
    cabin_type: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Cargo:
    id: Optional[int] = None
    pallets: Optional[int] = None
    containers: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Configuration:
    id: Optional[int] = None
    airframe: Optional[Airframe] = None
    cabin_oxy_system: Optional[int] = None
    continuous_ignition: Optional[bool] = None
    camera_system: Optional[bool] = None
    digital_clock: Optional[bool] = None
    new_gen_cdu: Optional[bool] = None
    modern_compass: Optional[bool] = None
    pilot_response_alert_system: Optional[bool] = None
    tcas_7_1: Optional[bool] = None
    segment_displays: Optional[int] = None
    classic_stby_instruments: Optional[bool] = None
    raas: Optional[bool] = None
    aural_altitude_alert: Optional[bool] = None
    units_of_measure: Optional[bool] = None
    wailer_ap_disc: Optional[bool] = None
    config_uncancellable: Optional[bool] = None
    eng_fail_aural_alert: Optional[bool] = None
    vnav_speed_band: Optional[bool] = None
    heading_up_map: Optional[bool] = None
    gs_on_pfd: Optional[bool] = None
    land_alt_ref_bar: Optional[bool] = None
    rising_runway: Optional[bool] = None
    integrated_cue_pfd: Optional[bool] = None
    range_arcs: Optional[bool] = None
    enhanced_rnp: Optional[bool] = None
    eicas_compact_data: Optional[bool] = None
    aoa_indication: Optional[bool] = None
    vsi_tcas_ra_band: Optional[bool] = None
    three_mile_ring: Optional[bool] = None
    flap_vref_spd: Optional[bool] = None
    press_sys_on_eicas: Optional[bool] = None
    altn_pfd_horizon_color: Optional[bool] = None
    alt_alert_zone: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return str(self.airframe)


@dataclass
class FlightFluid:
    id: Optional[int] = None
    flight: Optional[Flight] = None
    current_flight: Optional[CurrentFlight] = None
    fluid: Optional[FluidInstance] = None
    phase: Optional[FlightPhase] = None
    level: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    def __str__(self):
        owner = self.current_flight or self.flight

        if not owner:
            return f"{self.fluid} = {self.level}"

        uom = (
            self.fluid.fluid_template.units_of_measure
            if self.fluid and self.fluid.fluid_template
            else ""
        )
        return f"{owner} = {self.level} {uom}"


@dataclass
class UserSettings:
    id: Optional[int] = None
    crew_code: str = ""
    company_acars: str = ""
    maint_code: str = "12345"