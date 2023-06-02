from django.contrib import admin

from . import models


admin.site.register(models.ClientProfileModel)
admin.site.register(models.ClientFeedbackModel)
admin.site.register(models.ClientVerificationModel)
