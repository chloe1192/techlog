from django.contrib import admin
from .models import Airframe, AirframeDefect, AircraftType, Configuration, EngineModel, Company, Defect, Aoc, AirframeFluid, EngineFluids, Airport, Flight, FlightFluidsDeparture, FlightFluidsArrival, AirframeEngine

class ConpanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']

class EngineFluidsAdmin(admin.ModelAdmin):
    list_display = ['item', 'level', 'fluid_type', 'updated_at']

class AirframeFluidAdmin(admin.ModelAdmin):
    list_display = ['item', 'level', 'fluid_type', 'updated_at']

class AocAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_at', 'updated_at']

class AirframeAdmin(admin.ModelAdmin):
    list_display = ['registration', 'created_at', 'updated_at']

class DefectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')

class AirframeDefectAdmin(admin.ModelAdmin):
    list_display = ('airframe', 'created_at', 'updated_at')

class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')

class EngineModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'thrust', 'created_at', 'updated_at')

class AirportAdmin(admin.ModelAdmin):
    list_display = ('iata_code', 'name', 'created_at', 'updated_at')
    
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flt_number', 'date_of_flight', 'airframe')

class FlightFluidsDepartureAdmin(admin.ModelAdmin):
    list_display = ('flt', 'fluid_name')

class FlightFluidsArrivalAdmin(admin.ModelAdmin):
    list_display = ('flt', 'fluid_name')

class AirframeEngineAdmin(admin.ModelAdmin):    
    list_display = ('engine_model', 'engine_number', 'airframe')

class ConfigurationAdmin(admin.ModelAdmin):    
    list_display = ['airframe']

admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(AirframeEngine, AirframeEngineAdmin)
admin.site.register(FlightFluidsDeparture, FlightFluidsDepartureAdmin)
admin.site.register(FlightFluidsArrival, FlightFluidsArrivalAdmin)
admin.site.register(EngineFluids, EngineFluidsAdmin)
admin.site.register(AirframeFluid, AirframeFluidAdmin)
admin.site.register(Aoc, AocAdmin)
admin.site.register(Defect, DefectAdmin)
admin.site.register(Company, ConpanyAdmin)
admin.site.register(Airframe, AirframeAdmin)
admin.site.register(AirframeDefect, AirframeDefectAdmin)
admin.site.register(EngineModel, EngineModelAdmin)
admin.site.register(AircraftType, AircraftTypeAdmin)
admin.site.register(Airport, AirportAdmin)
admin.site.register(Flight, FlightAdmin)