from django.contrib import admin
from .models import (
    Action,
    Airframe,
    AirframeDefect,
    AircraftType,
    Configuration,
    CurrentFlight,
    EngineDefect,
    EngineModel,
    Company,
    Defect,
    EngineeringCompany,
    FamilyDefect,
    Operator,
    AirframeFluid,
    EngineFluids,
    Airport,
    Flight,
    AirframeEngine,
    Route,
    TypeDefect,
    FlightAirframeFluidsDeparture,
    FlightAirframeFluidsArrival,
    FlightEngineFluidsDeparture,
    FlightEngineFluidsArrival,
    AircraftTypeFluid,
    EngineModelFluid,
    UserSettings
)
class ConpanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']

class EngineModelFluidAdmin(admin.ModelAdmin):
    list_display = ['engine_model', 'item', 'fluid_type']

class AircraftTypeFluidAdmin(admin.ModelAdmin):
    list_display = ['aircraft_type', 'item', 'fluid_type']

class EngineFluidsAdmin(admin.ModelAdmin):
    list_display = ['item', 'level', 'fluid_type', 'updated_at']

class AirframeFluidAdmin(admin.ModelAdmin):
    list_display = ['item', 'level', 'fluid_type', 'updated_at']

class OperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_at', 'updated_at']

class AirframeAdmin(admin.ModelAdmin):
    list_display = ['registration', 'created_at', 'updated_at']

class DefectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')

class AirframeDefectAdmin(admin.ModelAdmin):
    list_display = ('airframe', 'created_at', 'updated_at')

class ActionAdmin(admin.ModelAdmin):
    list_display = ('status', 'airframe_defect')

class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

class EngineModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'thrust', 'created_at', 'updated_at')

class AirportAdmin(admin.ModelAdmin):
    list_display = ('iata_code', 'name', 'created_at', 'updated_at')

class RouteAdmin(admin.ModelAdmin):
    list_display = ('operator', 'departure', 'arrival')
    
class FlightAdmin(admin.ModelAdmin):
    list_display = ('callsign', 'date_of_flight', 'airframe')

class AirframeEngineAdmin(admin.ModelAdmin):    
    list_display = ('engine_model', 'engine_number', 'airframe')

class ConfigurationAdmin(admin.ModelAdmin):    
    list_display = ['airframe']

class FamilyDefectAdmin(admin.ModelAdmin):
    list_display = ['aircraft_family', 'defect']

class EngineDefectAdmin(admin.ModelAdmin):
    list_display = ['engine_model', 'defect']

class TypeDefectAdmin(admin.ModelAdmin):
    list_display = ['aircraft_type', 'defect']

class FlightAirframeFluidsDepartureAdmin(admin.ModelAdmin):
    list_display = (
        'flight',
        'fluid',
        'fluid_level',
    )
    list_filter = (
        'fluid',
    )

class FlightAirframeFluidsArrivalAdmin(admin.ModelAdmin):
    list_display = (
        'flight',
        'fluid',
        'fluid_level',
    )
    list_filter = (
        'fluid',
    )

class FlightEngineFluidsDepartureAdmin(admin.ModelAdmin):
    list_display = (
        'flight',
        'fluid',
        'fluid_level',
    )
    list_filter = (
        'fluid',
    )

class FlightEngineFluidsArrivalAdmin(admin.ModelAdmin):
    list_display = (
        'flight',
        'fluid',
        'fluid_level',
    )
    list_filter = (
        'fluid',
    )

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'crew_code',
        'company_acars'
    ]

class EngineeringCompanyAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name'
    ]

class CurrentFlightAdmin(admin.ModelAdmin):
    list_display = [
        'planned_flt_number'
    ]

admin.site.register(
    CurrentFlight,
    CurrentFlightAdmin
)
admin.site.register(
    EngineeringCompany,
    EngineeringCompanyAdmin
)
admin.site.register(
    UserSettings,
    UserSettingsAdmin
)
admin.site.register(FamilyDefect, FamilyDefectAdmin)
admin.site.register(EngineDefect, EngineDefectAdmin)
admin.site.register(TypeDefect, TypeDefectAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(AirframeEngine, AirframeEngineAdmin)
admin.site.register(
    FlightAirframeFluidsDeparture,
    FlightAirframeFluidsDepartureAdmin
)

admin.site.register(
    FlightAirframeFluidsArrival,
    FlightAirframeFluidsArrivalAdmin
)

admin.site.register(
    FlightEngineFluidsDeparture,
    FlightEngineFluidsDepartureAdmin
)

admin.site.register(
    FlightEngineFluidsArrival,
    FlightEngineFluidsArrivalAdmin
)

admin.site.register(
    EngineModelFluid,
    EngineModelFluidAdmin
)

admin.site.register(
    AircraftTypeFluid,
    AircraftTypeFluidAdmin
)
admin.site.register(EngineFluids, EngineFluidsAdmin)
admin.site.register(AirframeFluid, AirframeFluidAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(Defect, DefectAdmin)
admin.site.register(Company, ConpanyAdmin)
admin.site.register(Airframe, AirframeAdmin)
admin.site.register(AirframeDefect, AirframeDefectAdmin)
admin.site.register(EngineModel, EngineModelAdmin)
admin.site.register(AircraftType, AircraftTypeAdmin)
admin.site.register(Airport, AirportAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Route, RouteAdmin)