from django.contrib import admin
from jtisite.models import Country, City, Location, Region


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'simp_id', 'region']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'simp_id']