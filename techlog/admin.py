from django.contrib import admin
from .models import Action, Airframe, AirframeDefect, AircraftType, Configuration, EngineDefect, EngineModel, Company, Defect, FamilyDefect, Operator, AirframeFluid, EngineFluids, Airport, Flight, FlightFluidsDeparture, FlightFluidsArrival, AirframeEngine, Route, TypeDefect

class ConpanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']

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

class FlightFluidsDepartureAdmin(admin.ModelAdmin):
    list_display = ('flt', 'fluid_name')

class FlightFluidsArrivalAdmin(admin.ModelAdmin):
    list_display = ('flt', 'fluid_name')

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

admin.site.register(FamilyDefect, FamilyDefectAdmin)
admin.site.register(EngineDefect, EngineDefectAdmin)
admin.site.register(TypeDefect, TypeDefectAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(AirframeEngine, AirframeEngineAdmin)
admin.site.register(FlightFluidsDeparture, FlightFluidsDepartureAdmin)
admin.site.register(FlightFluidsArrival, FlightFluidsArrivalAdmin)
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