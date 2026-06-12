from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import AirframeDefect, CurrentFlight

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