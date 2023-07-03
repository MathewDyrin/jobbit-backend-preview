from django.contrib import admin

from . import models


admin.site.register(models.ChatModel)
admin.site.register(models.ParticipantModel)
admin.site.register(models.ChatPermissionsModel)
admin.site.register(models.MessageModel)
