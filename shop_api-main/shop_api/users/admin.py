from django import forms
from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        "id", "email", "first_name", "last_name",
        "registration_source", "is_active", "is_staff",
    ]
    list_editable = ["is_active"]
    ordering = ("email",)
    search_fields = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {
            "fields": (
                "first_name", "last_name", "phone_number", "birthdate",
                "registration_source", "is_active", "is_staff", "last_login",
            )
        }),
    )


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))


admin.site.login_form = EmailAuthenticationForm
