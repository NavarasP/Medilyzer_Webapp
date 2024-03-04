from django.contrib import admin
from .models import Prescription

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'uploaded_at')

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_full_name.short_description = 'User Full Name'
admin.site.register(Prescription, PrescriptionAdmin)