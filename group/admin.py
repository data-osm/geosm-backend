from django.contrib import admin
from .models import Base_map
from tracking_fields.admin import TrackedObjectMixinAdmin

class BaseMapAdmin(TrackedObjectMixinAdmin):
    pass
# Register your models here.
admin.site.register(Base_map, BaseMapAdmin)