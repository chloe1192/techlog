from datetime import datetime
from django.db import models
from django.db.models import Q

class FluidTypes(models.IntegerChoices):
    FUEL = 0, "Fuel"
    OIL = 1, "Oil"
    HYD = 2, "Hyd"
    WATER = 3, "Water/Waste"

class UnitsOfMeasure(models.IntegerChoices):
    LT = 0, "Liters"
    QTS = 1, "Quarts"
    PCT = 2, "Percentage"
    GAL = 3, "Gallons"
    KG = 4, "Kilograms"

class FuelPenaltyTypes(models.IntegerChoices):
    NO = 0, "No Penalty"
    PCT = 1, "Percentage"
    KG = 2, "Kilograms"
    LBS = 3, "Pounds"

class ActionTypes(models.IntegerChoices):
    OPEN = 0, "Open",
    CLOSED = 1, "Closed",
    CFWD = 2, "Carry Foward"

class DeferCategory(models.IntegerChoices):
    NA = 0, "Non Airworthiness"
    DML = 1, "DML"
    CDL = 2, "CDL"
    MEL_D = 3, "MEL CAT D - 120 Days"
    MEL_C = 4, "MEL CAT C - 10 Days"
    MEL_B = 5, "MEL CAT B - 3 Days"
    MEL_A = 6, "MEL CAT A"

class CurrentFlightStatus(models.IntegerChoices):
    DRAFT = 0, "Draft"
    IN_PROGRESS = 1, "In Progress"
    READY_TO_SUBMIT = 2, "Ready to Submit"

class AirframeOrEngineFluid(models.IntegerChoices):
    AIRFRAME = 0, "Airframe Fluid"
    ENGINE = 1, "Engine Fluid"

class ProcedureRequired(models.IntegerChoices):
    NONE = 0, "None"
    M = 1, "(M)"
    O = 2, "(O)"
    MO = 3, "(M) (O)"

class FluidOwnerType(models.IntegerChoices):
    AIRFRAME = 0
    ENGINE = 1

class FlightPhase(models.IntegerChoices):
    DEPARTURE = 0
    ARRIVAL = 1

class Company(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EngineeringCompany(models.Model):
    name = models.TextField()
    code = models.TextField()

    def __str__(self):
        return f"{self.code} - {self.name}"

class Operator(models.Model):
    name = models.CharField(max_length=200)
    iata_code = models.CharField(max_length=2, blank=True)
    icao_code = models.CharField(max_length=3, blank=True)
    company = models.ForeignKey(Company, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.icao_code

class AircraftFamily(models.Model):
    name = models.CharField(max_length=30)
    manufacturer = models.CharField(max_length=30)

    def __str__(self):
        return self.name
 
class AircraftType(models.Model):
    name = models.CharField(max_length=200)
    aircraft_family = models.ForeignKey(AircraftFamily, on_delete=models.RESTRICT)
    icao_code = models.CharField(max_length=4, blank=True)
    manufacturer_empty_weight = models.IntegerField()
    basic_empty_weight = models.IntegerField()
    operating_empty_weight = models.IntegerField()
    max_zero_fuel_weight = models.IntegerField()
    max_landing_weight = models.IntegerField()
    max_takeoff_weight = models.IntegerField()
    max_ramp_weight = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Defect(models.Model):
    title = models.CharField(max_length=200)
    ata_chapter = models.IntegerField()
    ata_section = models.IntegerField()
    ata_item = models.CharField(max_length=6)
    interval = models.IntegerField(choices=DeferCategory,default=DeferCategory.NA)
    installed_qty = models.IntegerField()
    required_qty = models.IntegerField()
    procedure = models.IntegerField(choices=ProcedureRequired,default=ProcedureRequired.NONE)
    maint_note = models.TextField(blank=True, null=True)
    operations = models.TextField(blank=True, null=True)
    fuel_penalty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fuel_penalty_type = models.IntegerField(choices=FuelPenaltyTypes,default=FuelPenaltyTypes.NO)
    aircraft_family = models.ForeignKey(AircraftFamily, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} --- {self.ata_chapter}-{self.ata_section}-{self.ata_item}"
   
class EngineModel(models.Model):
    name = models.CharField(max_length=200)
    thrust = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Airframe(models.Model):
    registration = models.CharField(max_length=200, unique=True)
    msn = models.IntegerField(blank=True, null=True, unique=True)
    date_of_build = models.DateField(blank=True, null=True)
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.RESTRICT)
    operator = models.ForeignKey(Operator, on_delete=models.RESTRICT)
    standard_empty_weight =  models.IntegerField()
    basic_empty_weight =  models.IntegerField()
    manufacturer_empty_weight =  models.IntegerField()
    operating_empty_weight  =  models.IntegerField()
    max_zero_fuel_weight  =  models.IntegerField()
    max_landing_weight  =  models.IntegerField()
    max_takeoff_weight  = models.IntegerField()
    max_ramp_weight = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    """ 
        def save(self, *args, **kwargs):
            if not self.pk:
                at = self.aircraft_type

                self.basic_empty_weight = at.basic_empty_weight
                self.operating_empty_weight = at.operating_empty_weight
                self.standard_empty_weight = at.manufacturer_empty_weight
                self.max_zero_fuel_weight = at.max_zero_fuel_weight
                self.max_landing_weight = at.max_landing_weight
                self.max_takeoff_weight = at.max_takeoff_weight
                self.max_ramp_weight = at.max_ramp_weight

            super().save(*args, **kwargs)

        def create_default_fluids(self):
            templates = AircraftTypeFluid.objects.filter(
                aircraft_type=self.aircraft_type
            )

            for template in templates:
                AirframeFluid.objects.create(
                    airframe=self,
                    aircraft_type_fluid=template
                )
        
        def get_available_defects(self):
            family_defects = Defect.objects.filter(
                familydefect__aircraft_family=self.aircraft_type.aircraft_family
            )

            type_defects = Defect.objects.filter(
                typedefect__aircraft_type=self.aircraft_type
            )

            engine_models = AirframeEngine.objects.filter(
                airframe=self
            ).values_list("engine_model", flat=True)

            engine_defects = Defect.objects.filter(
                enginedefect__engine_model__in=engine_models
            )

            return (family_defects | type_defects | engine_defects).distinct()
    """
    def __str__(self):
        return self.registration

class AirframeEngine(models.Model):
    engine_model = models.ForeignKey(EngineModel, on_delete=models.RESTRICT)
    airframe = models.ForeignKey(Airframe, on_delete=models.CASCADE)
    engine_hours = models.IntegerField(blank=True, null=True)
    engine_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("airframe", "engine_number")

    def create_default_fluids(self):
            templates = EngineModelFluid.objects.filter(
                engine_model=self.engine_model
            )

            for template in templates:
                EngineFluids.objects.create(
                    airframe_engine=self,
                    engine_model_fluid=template
                )

    def __str__(self):
        return f"{self.airframe} {self.engine_number}"

class FluidTemplate(models.Model):
   
    name = models.CharField(
        max_length=200
    )
    owner_type = models.IntegerField(
        choices=FluidOwnerType.choices
    )
    aircraft_type = models.ForeignKey(
        AircraftType,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    engine_model = models.ForeignKey(
        EngineModel,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    fluid_type = models.IntegerField(
        choices=FluidTypes
    )
    units_of_measure = models.IntegerField(
        choices=UnitsOfMeasure
    )
    max_level = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="fluid_template_owner_consistency",
                condition=(
                    models.Q(
                        owner_type=FluidOwnerType.AIRFRAME,
                        aircraft_type__isnull=False,
                        engine_model__isnull=True,
                    )
                    |
                    models.Q(
                        owner_type=FluidOwnerType.ENGINE,
                        aircraft_type__isnull=True,
                        engine_model__isnull=False,
                    )
                ),
            )
        ]
    
    def __str__(self):
        if self.owner_type == FluidOwnerType.AIRFRAME:
            return f"{self.name} - {self.aircraft_type}"
        
        if self.owner_type == FluidOwnerType.ENGINE:
            return f"{self.name} - {self.engine_model} "

class FluidInstance(models.Model):
    fluid_template = models.ForeignKey(
        FluidTemplate, on_delete=models.RESTRICT
    )
    airframe = models.ForeignKey(
        Airframe,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    airframe_engine = models.ForeignKey(
        AirframeEngine,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    level = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="fluid_instance_owner_consistency",
                condition=(
                    models.Q(
                        airframe__isnull=False,
                        airframe_engine__isnull=True,
                    )
                    |
                    models.Q(
                        airframe__isnull=True,
                        airframe_engine__isnull=False,
                    )
                ),
            ),            
            models.UniqueConstraint(
                fields=["fluid_template", "airframe"],
                condition=Q(airframe__isnull=False),
                name="unique_airframe_fluid",
            ),
            models.UniqueConstraint(
                fields=["fluid_template", "airframe_engine"],
                condition=Q(airframe_engine__isnull=False),
                name="unique_engine_fluid",
            ),
        ]
        unique_together = ('fluid_template', 'airframe', 'airframe_engine')

    def __str__(self):
        if self.fluid_template.owner_type == FluidOwnerType.AIRFRAME:
            return f"{self.fluid_template.name} - {self.airframe}"
        
        if self.fluid_template.owner_type == FluidOwnerType.ENGINE:
            return f"{self.fluid_template.name} {self.airframe_engine.engine_number} - {self.airframe_engine} "
   
class Airport(models.Model):
    iata_code = models.CharField(max_length=3)
    icao_code = models.CharField(max_length=4, blank=True)
    name = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.iata_code

class Route(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.RESTRICT)
    flt_number = models.CharField(max_length=7, blank=True, null=True)
    departure = models.ForeignKey(Airport, on_delete=models.RESTRICT, related_name='departure_airport')
    arrival = models.ForeignKey(Airport, on_delete=models.RESTRICT, related_name='arrival_airport', blank=True, null=True)
    scheduled_off_ground = models.TimeField(blank=True, null=True)
    scheduled_on_ground = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flt_number} - {self.departure.iata_code} - {self.arrival.iata_code}"

# TODO shcedule logic and limit route per type

# TODO company stands at airports

class Flight(models.Model):
    airframe = models.ForeignKey(Airframe, on_delete=models.CASCADE)
    flight_route = models.ForeignKey(Route, on_delete=models.RESTRICT)
    actual_arrival = models.ForeignKey(Airport, on_delete=models.RESTRICT)
    callsign = models.CharField(max_length=8)
    date_of_flight = models.DateField()
    off_blocks = models.DateTimeField()
    off_ground = models.DateTimeField()
    on_ground = models.DateTimeField()
    on_blocks = models.DateTimeField()
    required_fuel_in_kg = models.IntegerField()
    block_fuel_in_kg = models.IntegerField()
    maint_release_date = models.DateTimeField()
    maint_release_eng_company = models.ForeignKey(EngineeringCompany, on_delete=models.RESTRICT)
    acceptance_date = models.DateTimeField()
    planned_flt_number = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flight_route} {self.date_of_flight} {self.airframe.registration}"
 
class CurrentFlight(models.Model):
    airframe = models.ForeignKey(Airframe, on_delete=models.CASCADE, unique=True)
    flight_route = models.ForeignKey(Route, on_delete=models.RESTRICT, blank=True, null=True)
    status = models.IntegerField(
        choices=CurrentFlightStatus,
        default=CurrentFlightStatus.DRAFT
    )
    actual_arrival = models.ForeignKey(
        Airport,
        on_delete=models.RESTRICT,
        blank=True,
        null=True
    )
    callsign = models.CharField(max_length=8, blank=True, null=True)
    date_of_flight = models.DateField(blank=True, null=True)
    off_blocks = models.DateTimeField(blank=True, null=True)
    off_ground = models.DateTimeField(blank=True, null=True)
    on_ground = models.DateTimeField(blank=True, null=True)
    on_blocks = models.DateTimeField(blank=True, null=True)
    required_fuel_in_kg = models.IntegerField(blank=True, null=True)
    block_fuel_in_kg = models.IntegerField(blank=True, null=True)
    maint_release_date = models.DateTimeField(blank=True, null=True)
    maint_release_eng_company = models.ForeignKey(EngineeringCompany, on_delete=models.RESTRICT, blank=True, null=True)
    # TODO maint defects actioned on a n2n table
    acceptance_date = models.DateTimeField(blank=True, null=True)
    planned_flt_number = models.CharField(max_length=7, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flight_route} {self.date_of_flight} {self.airframe.registration}"

class Refuel(models.Model):
    planned_flt_number = models.ForeignKey(CurrentFlight, on_delete=models.CASCADE, blank=True, null=True)
    actual_flight = models.ForeignKey(Flight, on_delete=models.RESTRICT, blank=True, null=True)
    airframe = models.ForeignKey(Airframe, on_delete=models.RESTRICT)
    planned_dep_fuel_in_kg = models.IntegerField()
    specific_gravity = models.DecimalField(max_digits=3, decimal_places=2)
    required_uplift_in_lt = models.IntegerField()
    pre_refuel_in_kg = models.IntegerField()
    departure_fob_in_kg = models.IntegerField()
    fuel_supplier = models.CharField(max_length=5, default="")
    fuel_ticket_no = models.CharField(max_length=10, default="")
    bowser_uplift_in_lt = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                name="flight_fluid_current_or_saved_consistency",
                condition=(
                    models.Q(
                        actual_flight__isnull=False,
                        planned_flt_number__isnull=True,
                    )
                    |
                    models.Q(
                        actual_flight__isnull=True,
                        planned_flt_number__isnull=False
                    )
                ),
            )
        ]


class AirframeDefect(models.Model):
    airframe = models.ForeignKey(Airframe, on_delete=models.RESTRICT)
    defect_title = models.CharField(max_length=150)
    defect = models.ForeignKey(Defect, on_delete=models.RESTRICT, blank=True, null=True)
    is_pilot_report = models.BooleanField(default=1)
    is_cabin_log = models.BooleanField(default=0)
    crs_not_required = models.BooleanField(default=0)
    is_etops = models.BooleanField(default=0)
    ecam_message = models.CharField(max_length=50, blank=True, null=True)
    defect_text = models.TextField(blank=True, null=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, blank=True, null=True)
    status = models.IntegerField(choices=ActionTypes, default=ActionTypes.OPEN)
    noticed_at = models.DateTimeField(default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.defect and not self.defect_title:
            self.defect_title = self.defect.title
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.airframe.registration} - {self.defect_title} - {self.noticed_at}"
    
class Action(models.Model):
    status = models.IntegerField(choices=ActionTypes, default=ActionTypes.CLOSED) # 0 open, 1 clodes, 2 carry fwd
    time = models.DateTimeField()
    desc = models.TextField(blank=True, null=True)
    airframe_defect = models.ForeignKey(AirframeDefect, on_delete=models.CASCADE)
    category = models.IntegerField(choices=DeferCategory, default=DeferCategory.NA)
    engineering_company = models.ForeignKey(EngineeringCompany, on_delete=models.RESTRICT)
    defer_reason = models.TextField(blank=True, null=True)
    deferred_at = models.DateTimeField(blank=True, null=True)
    due_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.airframe_defect.status = self.status
        self.airframe_defect.save()
        super().save(*args, **kwargs)

class Cabin(models.Model):
    cabin_type = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Cargo(models.Model):
    pallets = models.IntegerField(blank=True, null=True)
    containers = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Configuration(models.Model):
    airframe = models.ForeignKey(Airframe, on_delete=models.CASCADE)
    cabin_oxy_system = models.IntegerField(blank=True, null=True)
    continuous_ignition = models.BooleanField(blank=True, null=True)
    camera_system = models.BooleanField(blank=True, null=True)
    digital_clock = models.BooleanField(blank=True, null=True)
    new_gen_cdu = models.BooleanField(blank=True, null=True)
    modern_compass = models.BooleanField(blank=True, null=True)
    pilot_response_alert_system = models.BooleanField(blank=True, null=True)
    tcas_7_1 = models.BooleanField(blank=True, null=True)
    segment_displays = models.IntegerField(blank=True, null=True)
    classic_stby_instruments = models.BooleanField(blank=True, null=True)
    raas = models.BooleanField(blank=True, null=True)
    aural_altitude_alert = models.BooleanField(blank=True, null=True)
    units_of_measure = models.BooleanField(blank=True, null=True)
    wailer_ap_disc = models.BooleanField(blank=True, null=True)
    config_uncancellable = models.BooleanField(blank=True, null=True)
    eng_fail_aural_alert = models.BooleanField(blank=True, null=True)
    vnav_speed_band = models.BooleanField(blank=True, null=True)
    heading_up_map = models.BooleanField(blank=True, null=True)
    gs_on_pfd = models.BooleanField(blank=True, null=True)
    land_alt_ref_bar = models.BooleanField(blank=True, null=True)
    rising_runway = models.BooleanField(blank=True, null=True)
    integrated_cue_pfd = models.BooleanField(blank=True, null=True)
    range_arcs = models.BooleanField(blank=True, null=True)
    enhanced_rnp = models.BooleanField(blank=True, null=True)
    eicas_compact_data = models.BooleanField(blank=True, null=True)
    aoa_indication = models.BooleanField(blank=True, null=True)
    vsi_tcas_ra_band = models.BooleanField(blank=True, null=True)
    three_mile_ring = models.BooleanField(blank=True, null=True)
    flap_vref_spd = models.BooleanField(blank=True, null=True)
    press_sys_on_eicas = models.BooleanField(blank=True, null=True)
    altn_pfd_horizon_color = models.BooleanField(blank=True, null=True)
    alt_alert_zone = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.airframe)

class FlightFluid(models.Model):
    flight = models.ForeignKey(
        Flight,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    current_flight = models.ForeignKey(
        CurrentFlight,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    fluid = models.ForeignKey(
        FluidInstance,
        on_delete=models.CASCADE
    )
    phase = models.IntegerField(
        choices=FlightPhase
    )
    level = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.CheckConstraint(
                name="flight_fluid_dep_or_arr_consistency",
                condition=(
                    models.Q(
                        flight__isnull=False,
                        current_flight__isnull=True,
                    )
                    |
                    models.Q(
                        flight__isnull=True,
                        current_flight__isnull=False
                    )
                ),
            )
        ]
        unique_together = ("flight", "current_flight", "phase")

    def __str__(self):
        owner = self.current_flight or self.flight

        if not owner:
            return f"{self.fluid} = {self.level}"

        return f"{owner} = {self.level} {self.fluid.fluid_template.units_of_measure}"

# TODO this should be user based
class UserSettings(models.Model):
    crew_code = models.CharField(max_length=10, default="")
    company_acars = models.CharField(max_length=50, default="")
    # TODO change default
    maint_code = models.CharField(max_length=10, default="12345")
