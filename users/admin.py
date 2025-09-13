from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "user_type",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "email", "phone_number")
    list_filter = ["user_type"]


admin.site.register(User, UserAdmin)
