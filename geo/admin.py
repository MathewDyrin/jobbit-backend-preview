from django.contrib import admin

from . import models


admin.site.register(models.CountryModel)
admin.site.register(models.RegionModel)
admin.site.register(models.CityModel)
admin.site.register(models.SubwayModel)
admin.site.register(models.SubwayBranchModel)
