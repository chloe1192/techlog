from django.db import models

class FluidTypes(models.IntegerChoices):
    FUEL = 0, "Fuel"
    OIL = 1, "Oil"
    HYD = 2, "Hyd"
    WATER = 3, "Water/Waste"

class UnitsOfMeasureVolume(models.IntegerChoices):
    LT = 0, "Liters"
    QTS = 1, "Quarts"
    PCT = 2, "Percentage"
    GAL = 3, "Gallons"

class Company(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Aoc(models.Model):
    name = models.CharField(max_length=200)
    iata_code = models.CharField(max_length=2, blank=True)
    icao_code = models.CharField(max_length=3, blank=True)
    company = models.ForeignKey(Company, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.icao_code
 
class AircraftType(models.Model):
    name = models.CharField(max_length=200)
    icao_code = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
       
class Defect(models.Model):
    title = models.CharField(max_length=200)
    aicraft_type = models.ForeignKey(AircraftType, on_delete=models.RESTRICT)
    ata_chapter = models.IntegerField()
    ata_section = models.IntegerField()
    ata_item = models.IntegerField()
    ata_item_letter = models.CharField(max_length=1)
    interval = models.CharField(max_length=1)
    installed = models.IntegerField()
    required = models.IntegerField()
    procedure = models.CharField(max_length=1)
    maint_note = models.TextField()
    operations = models.TextField()
    fuel_penalty = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_penalty_type = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
  
class EngineModel(models.Model):
    name = models.CharField(max_length=200)
    thrust = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Airframe(models.Model):
    registration = models.CharField(max_length=200)
    msn = models.IntegerField(blank=True, null=True)
    date_of_build = models.DateField(blank=True, null=True)
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.RESTRICT)
    engine_model = models.ForeignKey(EngineModel, on_delete=models.RESTRICT)
    aoc = models.ForeignKey(Aoc, on_delete=models.RESTRICT)
    manufacturer_empty_weight = models.DecimalField(max_digits=10, decimal_places=2)
    standard_empty_weight = models.DecimalField(max_digits=10, decimal_places=2)
    basic_empty_weight = models.DecimalField(max_digits=10, decimal_places=2)
    operating_empty_weight = models.DecimalField(max_digits=10, decimal_places=2)
    zero_fuel_weight = models.DecimalField(max_digits=10, decimal_places=2)
    ramp_weight = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.registration

class AirframeEngine(models.Model):
    engine_model = models.ForeignKey(EngineModel, on_delete=models.RESTRICT)
    airframe = models.ForeignKey(Airframe, on_delete=models.CASCADE)
    engine_hours = models.IntegerField(blank=True, null=True)
    engine_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.airframe} {self.engine_number}"

class AirframeFluid(models.Model):
    item = models.CharField(max_length=200)
    level = models.DecimalField(max_digits=10, decimal_places=2)
    units_of_measure = models.IntegerField(choices=UnitsOfMeasureVolume, default=UnitsOfMeasureVolume.LT) # 0 lt, 1 qts, 2 pct, 3 gal
    max_level = models.DecimalField(max_digits=10, decimal_places=2)
    airframe = models.ForeignKey(Airframe, on_delete=models.RESTRICT)
    fluid_type = models.IntegerField(choices=FluidTypes, default=FluidTypes.FUEL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item

class EngineFluids(models.Model):
    item = models.CharField(max_length=200)
    level = models.DecimalField(max_digits=10, decimal_places=2)
    airframe_engine = models.ForeignKey(AirframeEngine, on_delete=models.CASCADE)
    units_of_measure = models.IntegerField(choices=UnitsOfMeasureVolume, default=UnitsOfMeasureVolume.LT) # 0 lt, 1 qts, 2 pct
    max_level = models.DecimalField(max_digits=10, decimal_places=2)
    fluid_type = models.IntegerField(choices=FluidTypes, default=FluidTypes.FUEL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item

class AirframeDefect(models.Model):
    airframe = models.ForeignKey(Airframe, on_delete=models.RESTRICT)
    defect = models.ForeignKey(Defect, on_delete=models.RESTRICT)
    action = models.IntegerField(max_length=2, default=0) # 0 open, 1 clodes, 2 carry fwd
    action_desc = models.TextField(blank=True, null=True)
    action_time = models.DateTimeField(blank=True, null=True)
    noticed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.defect.title} {self.airframe.registration}"

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
        return self.registration

class Airport(models.Model):
    iata_code = models.CharField(max_length=3)
    icao_code = models.CharField(max_length=4, blank=True)
    name = models.CharField(max_length=50, blank=True)
    city = models.CharField(blank=True, null=True)
    country = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.iata_code

class Flight(models.Model):
    flt_number = models.CharField(blank=True, null=True)
    airframe = models.ForeignKey(Airframe, on_delete=models.CASCADE)
    callsign = models.CharField(max_length=8, blank=True, null=True)
    departure = models.ForeignKey(Airport, on_delete=models.RESTRICT, related_name='departure_airport')
    arrival = models.ForeignKey(Airport, on_delete=models.RESTRICT, related_name='arrival_airport', blank=True, null=True)
    date_of_flight = models.DateField(blank=True, null=True)
    off_blocks = models.DateTimeField(blank=True, null=True)
    off_ground = models.DateTimeField(blank=True, null=True)
    on_ground = models.DateTimeField(blank=True, null=True)
    on_blocks = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flt_number}"
    
class FlightFluidsDeparture(models.Model):
    flt = models.ForeignKey(Flight, on_delete=models.CASCADE)
    fluid_name = models.ForeignKey(AirframeFluid, on_delete=models.CASCADE)
    fluid_level = models.DecimalField(max_digits=6, decimal_places=2)

class FlightFluidsArrival(models.Model):
    flt = models.ForeignKey(Flight, on_delete=models.CASCADE)
    fluid_name = models.ForeignKey(AirframeFluid, on_delete=models.CASCADE)
    fluid_level = models.DecimalField(max_digits=6, decimal_places=2)
