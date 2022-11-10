from django.db import models


class Region(models.Model):
    name = models.CharField(
        'Region name',
        max_length=200,
    )
    simp_id = models.IntegerField(
        'SIMP id',
    )
    
    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(
        'Country name',
        max_length=200,
        unique=True,
    )
    simp_id = models.IntegerField(
        'SIMP id',
    )
    region = models.ForeignKey(
        Region,
        verbose_name='Region',
        related_name='countries',
        on_delete=models.CASCADE,
    )
    
    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(
        'City name',
        max_length=300,
    )
    country = models.ForeignKey(
        Country,
        verbose_name='Country',
        related_name='cities',
        on_delete=models.CASCADE,
    )
    
    class Meta:
        verbose_name_plural = 'Cities'
        
    def __str__(self):
        return f'{self.name}, {self.country}'


class Location(models.Model):
    lat = models.FloatField(
        'Latitude',
    )
    lon = models.FloatField(
        'Longitude',
    )
    city = models.ForeignKey(
        City,
        verbose_name='City',
        related_name='locations',
        on_delete=models.CASCADE,
    )
    country = models.ForeignKey(
        Country,
        verbose_name='Country',
        related_name='locations',
        on_delete=models.CASCADE,
    )
    
    class Meta:
        unique_together = ('lat', 'lon')
    
    def __str__(self):
        return f'{self.lat}, {self.lon}'
