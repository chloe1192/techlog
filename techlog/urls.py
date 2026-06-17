"""
URL configuration for techlog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('operator/<int:id>', views.operator_index, name='operator_index'),

    # airframe_editing    
    path('airframes/list/', views.airframes_list, name='airframes_list'),
    path('airframes/edit/<int:id>/', views.airframes_edit, name='airframes_edit'),

    path('airframe/<int:id>/', views.flight_index, name='flight_index'),
    
    path('airframe/<int:id>/flight_release_maintenance/', views.flight_release_maintenance, name='flight_release_maintenance'),
    path('airframe/<int:id>/flight_release_acceptance/', views.flight_release_acceptance, name='flight_release_acceptance'),

    path('airframe/<int:id>/flight_details/', views.flight_details, name='flight_details'),

    # defects
    path('airframe/<int:id>/defects/', views.defects, name='defects'),
    path('airframe/<int:id>/defects/create', views.defects_create, name='defects_create'),
    path('airframe/<int:id>/defects/<int:defect_id>/details/', views.defects_details, name='defects_details'),
    path('airframe/<int:id>/defects/this_flight', views.defects_this_flight, name='defects_this_flight'),
    path('airframe/<int:id>/defects/<int:defect_id>/actions/create/', views.defects_actions_create, name='defects_actions_create'),
    path('airframe/<int:id>/defects/<int:defect_id>/actions/<int:action_id>/edit/', views.defects_actions_edit, name='defects_actions_edit'),
    path('airframe/<int:id>/flight_defects/', views.flight_defects, name='flight_defects'),
    #path('airframe/<int:id>/flight_defects_create/', views.flight_defects_create, name='flight_defects_create'),

    # servicing
    path('airframe/<int:id>/servicing/', views.servicing, name='servicing'),
    path('airframe/<int:id>/servicing/fuel/', views.servicing_fuel, name='servicing_fuel'),
    path('airframe/<int:id>/servicing/oil/', views.servicing_oil, name='servicing_oil'),
    path('airframe/<int:id>/servicing/hyd/', views.servicing_hyd, name='servicing_hyd'),
    path('airframe/<int:id>/servicing/water/', views.servicing_water, name='servicing_water'),
    path('airframe/<int:airframe_id>/servicing/fuel/list/', views.servicing_refuel_list, name='servicing_refuel_list'),
    
    path('airframe/<int:id>/flight_servicing/', views.flight_servicing, name='flight_servicing'),
    path('airframe/<int:id>/flight_fuel_levels/', views.flight_fuel_levels, name='flight_fuel_levels'),
    path('airframe/<int:id>/flight_oil_levels/', views.flight_oil_levels, name='flight_oil_levels'),
    path('airframe/<int:id>/flight_hydraulic_levels/', views.flight_hydraulic_levels, name='flight_hydraulic_levels'),
    path('airframe/<int:id>/flight_water_levels/', views.flight_water_levels, name='flight_water_levels'),
    path('airframe/<int:id>/flight_ice_protection/', views.flight_ice_protection, name='flight_ice_protection'),
    path('airframe/<int:id>/planned_maintenance/', views.planned_maintenance, name='planned_maintenance'),
    path('admin/', admin.site.urls),
]
