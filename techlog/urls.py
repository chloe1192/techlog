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
from airport_briefing import views as ab_views

urlpatterns = [
    path('', views.index, name='index'),
    path('operator/<int:operator_id>/', views.operator_index, name='operator_index'),
    # operator management
    path('operator/<int:operator_id>/routes/', views.routes_list, name='routes_list'),
    # airframe_editing    
    path('operator/airframes/list/', views.airframes_list, name='airframes_list'),
    path('operator/<int:operator_id>/airframes/create/', views.airframes_create, name='airframes_create'),
    path('operator/airframes/edit/<int:airframe_id>/', views.airframes_edit, name='airframes_edit'),

    path('airframe/<int:airframe_id>/', views.flight_index, name='flight_index'),
    
    path('airframe/<int:airframe_id>/flight_release_maintenance/', views.flight_release_maintenance, name='flight_release_maintenance'),
    path('airframe/<int:airframe_id>/flight_release_acceptance/', views.flight_release_acceptance, name='flight_release_acceptance'),

    # flight
    path('airframe/<int:airframe_id>/flight_details/', views.flight_details, name='flight_details'),
    path('airframe/<int:airframe_id>/flight_save/', views.flight_save, name='flight_save'),
    path('airframe/<int:airframe_id>/flight/departure/fluids/<int:fluid_type>/', views.flight_departure_fluids, name='flight_departure_fluids'),
    path('airframe/<int:airframe_id>/flight/arrival/fluids/<int:fluid_type>/', views.flight_arrival_fluids, name='flight_arrival_fluids'),

    # defects
    path('airframe/<int:airframe_id>/defects/', views.defects, name='defects'),
    path('airframe/<int:airframe_id>/defects/create', views.defects_create, name='defects_create'),
    path('airframe/<int:airframe_id>/defects/<int:defect_id>/details/', views.defects_details, name='defects_details'),
    path('airframe/<int:airframe_id>/defects/this_flight', views.defects_this_flight, name='defects_this_flight'),
    path('airframe/<int:airframe_id>/defects/<int:defect_id>/actions/create/', views.defects_actions_create, name='defects_actions_create'),
    path('airframe/<int:airframe_id>/defects/<int:defect_id>/actions/<int:action_id>/edit/', views.defects_actions_edit, name='defects_actions_edit'),

    # servicing
    path('airframe/<int:airframe_id>/servicing/', views.servicing, name='servicing'),
    path('airframe/<int:airframe_id>/servicing/fuel/', views.servicing_fuel, name='servicing_fuel'),
    path('airframe/<int:airframe_id>/servicing/oil/', views.servicing_oil, name='servicing_oil'),
    path('airframe/<int:airframe_id>/servicing/hyd/', views.servicing_hyd, name='servicing_hyd'),
    path('airframe/<int:airframe_id>/servicing/water/', views.servicing_water, name='servicing_water'),
    path('airframe/<int:airframe_id>/servicing/fuel/list/', views.servicing_refuel_list, name='servicing_refuel_list'),
    
    path('airframe/<int:airframe_id>/planned_maintenance/', views.planned_maintenance, name='planned_maintenance'),

    path('airport_briefing/', ab_views.index, name='airport_briefing_index'),
    path('admin/', admin.site.urls),
]
