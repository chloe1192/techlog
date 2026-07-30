from django import forms


class AirframeDefectForm(forms.Form):
    defect_title = forms.CharField(max_length=150)
    defect = forms.IntegerField(required=False)  # Defect catalog id
    is_pilot_report = forms.BooleanField(required=False, initial=True)
    is_cabin_log = forms.BooleanField(required=False)
    crs_not_required = forms.BooleanField(required=False)
    is_etops = forms.BooleanField(required=False)
    ecam_message = forms.CharField(max_length=50, required=False)
    defect_text = forms.CharField(required=False, widget=forms.Textarea)


class RefuelingForm(forms.Form):
    planned_flt_number = forms.IntegerField(required=False)  # CurrentFlight id
    planned_dep_fuel_in_kg = forms.IntegerField()
    specific_gravity = forms.DecimalField(max_digits=3, decimal_places=3)
    required_uplift_in_lt = forms.IntegerField()
    pre_refuel_in_kg = forms.IntegerField()
    departure_fob_in_kg = forms.IntegerField()
    fuel_supplier = forms.CharField(max_length=5, required=False)
    fuel_ticket_no = forms.CharField(max_length=26, required=False)
    bowser_uplift_in_lt = forms.IntegerField()


class AirframeForm(forms.Form):
    registration = forms.CharField(max_length=200)
    msn = forms.IntegerField(required=False)
    date_of_build = forms.DateField(required=False)
    aircraft_type = forms.IntegerField()
    operator = forms.IntegerField()
    standard_empty_weight = forms.IntegerField()
    basic_empty_weight = forms.IntegerField()
    manufacturer_empty_weight = forms.IntegerField()
    operating_empty_weight = forms.IntegerField()
    max_zero_fuel_weight = forms.IntegerField()
    max_landing_weight = forms.IntegerField()
    max_takeoff_weight = forms.IntegerField()
    max_ramp_weight = forms.IntegerField()


class AirframeEngineForm(forms.Form):
    engine_model = forms.IntegerField()
    engine_hours = forms.IntegerField(required=False, initial=0)


class ActionForm(forms.Form):
    status = forms.IntegerField()
    time = forms.DateTimeField()
    desc = forms.CharField(required=False, widget=forms.Textarea)
    category = forms.IntegerField()
    engineering_company = forms.IntegerField()
    defer_reason = forms.CharField(required=False, widget=forms.Textarea)
    deferred_at = forms.DateTimeField(required=False)
    due_at = forms.DateTimeField(required=False)


class CompleteFlightForm(forms.Form):
    airframe = forms.IntegerField()
    flight_route = forms.IntegerField(required=False)
    actual_arrival = forms.IntegerField(required=False)
    callsign = forms.CharField(max_length=8, required=False)
    date_of_flight = forms.DateField(required=False)
    off_blocks = forms.DateTimeField(required=False)
    off_ground = forms.DateTimeField(required=False)
    on_ground = forms.DateTimeField(required=False)
    on_blocks = forms.DateTimeField(required=False)
    required_fuel_in_kg = forms.IntegerField(required=False)
    block_fuel_in_kg = forms.IntegerField(required=False)
    maint_release_date = forms.DateTimeField(required=False)
    maint_release_eng_company = forms.IntegerField(required=False)
    acceptance_date = forms.DateTimeField(required=False)
    planned_flt_number = forms.CharField(max_length=7, required=False)