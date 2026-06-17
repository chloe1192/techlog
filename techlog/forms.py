from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import Airframe, AirframeDefect, AirframeEngine, CurrentFlight, Refuel, FluidTopUp

class AirframeDefectCreateForm(ModelForm):
    
    class Meta:
        model = AirframeDefect
        fields = [
        'defect_title',
        'defect',
        'is_pilot_report',
        'is_cabin_log',
        'crs_not_required',
        'is_etops',
        'ecam_message',
        'defect_text',
        ]

class MaintenanceReleaseForm(ModelForm):

    class Meta:
        model = CurrentFlight
        fields = [
            'maint_release_date',
            'maint_release_eng_company',
        ]

class AcceptanceForm(ModelForm):

    class Meta:
        model = CurrentFlight
        fields = [
            'acceptance_date',
            'planned_flt_number'
        ]

class RefuelingForm(ModelForm):
    class Meta:
        model = Refuel
        fields = [
            'planned_flt_number',
            'planned_dep_fuel_in_kg',
            'specific_gravity',
            'required_uplift_in_lt',
            'pre_refuel_in_kg',
            'departure_fob_in_kg',
            'fuel_supplier',
            'fuel_ticket_no',
            'bowser_uplift_in_lt'
        ]

class FluidTopUp(ModelForm):
    class Meta:
        model = FluidTopUp
        fields = [
            'planned_flt_number',
            'airframe_or_engine_fluid',
            'quantity',
            'engine_fluid',
            'airframe_fluid',
            'engineering_company'
        ]

class AirframeEdit(ModelForm):
    class Meta:
        model = Airframe
        fields = [
            'registration',
            'msn',
            'date_of_build',
            'aircraft_type',
            'operator',
            'standard_empty_weight',
            'basic_empty_weight',
            'manufacturer_empty_weight',
            'operating_empty_weight',
            'max_zero_fuel_weight',
            'max_landing_weight',
            'max_takeoff_weight',
            'max_ramp_weight'
        ]

class AirframeEngineEdit(ModelForm):
    class Meta:
        model = AirframeEngine
        fields = [
            'engine_model',
            'engine_hours'
        ]