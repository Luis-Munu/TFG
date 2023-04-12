from django.db import models


class Property(models.Model):
    _id = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    age = models.IntegerField()
    url = models.URLField()
    rooms = models.IntegerField()
    bathrooms = models.IntegerField()
    m2 = models.FloatField()
    elevator = models.BooleanField()
    floor = models.IntegerField()
    balcony = models.BooleanField()
    terrace = models.BooleanField()
    heating = models.BooleanField()
    air_conditioning = models.BooleanField()
    parking = models.BooleanField()
    pool = models.BooleanField()
    id = models.IntegerField()
    transfer_taxes = models.DecimalField(max_digits=10, decimal_places=2)
    insurance = models.DecimalField(max_digits=10, decimal_places=2)
    ibi = models.DecimalField(max_digits=10, decimal_places=2)
    community = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance = models.DecimalField(max_digits=10, decimal_places=2)
    costs = models.DecimalField(max_digits=10, decimal_places=2)
    amount_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
    total_mortgage = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_mortgage = models.DecimalField(max_digits=10, decimal_places=2)
    incomes = models.DecimalField(max_digits=10, decimal_places=2)
    rentability = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

class Zone(models.Model):
    name = models.CharField(max_length=255)
    parent_zone = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    rent = models.BooleanField(default=False)
    sell = models.BooleanField(default=False)
    subzones = models.ManyToManyField('self', blank=True)
    rentability_sqm1rooms = models.FloatField()
    rentability_sqm3rooms = models.FloatField()
    rentability_sqm2rooms = models.FloatField()
    rentability_sqm4rooms = models.FloatField()
    rentability_terrace = models.FloatField()
    rentability_elevator = models.FloatField()
    rentability_furnished = models.FloatField()
    rentability_parking = models.FloatField()
    rentability_pricepersqm = models.FloatField()
    rentability_b100 = models.FloatField()
    rentability_a100 = models.FloatField()
    avg_rentability = models.FloatField()

    def __str__(self):
        return self.name