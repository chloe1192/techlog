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
    path('airframe/<int:airframe_id>/', views.airframe_index, name='airframe_index'),
    path('operator/<int:id>', views.operator_index, name='operator_index'),    
    path('airframe/<int:id>/flight_details/', views.flight_details, name='flight_details'),
    path('airframe/<int:id>/flight_defects/', views.flight_defects, name='flight_defects'),
    path('airframe/<int:id>/flight_servicing/', views.flight_servicing, name='flight_servicing'),
    path('airframe/<int:id>/flight_oil_levels/', views.flight_oil_levels, name='flight_oil_levels'),
    path('admin/', admin.site.urls),
]
