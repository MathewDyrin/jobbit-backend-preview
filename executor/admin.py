from django.contrib import admin

from . import models

admin.site.register(models.ExecutorProfileModel)
admin.site.register(models.ExecutorExperienceModel)
admin.site.register(models.ExecutorExperienceFileModel)
admin.site.register(models.ExecutorServicesModel)
admin.site.register(models.ExecutorFeedbackModel)
admin.site.register(models.ExecutorPortfolioModel)
admin.site.register(models.ExecutorAddressModel)
admin.site.register(models.ExecutorVerificationModel)
admin.site.register(models.ExecutorGeoModel)
admin.site.register(models.ExecutorPortfolioAlbumModel)

