from django.contrib import admin
from .models import SingUp
from .forms import SingUpForm


class SingUpAdmin(admin.ModelAdmin):
    list_display = [
        '__unicode__',
        'timestamp',
        'updated',
    ]
    form = SingUpForm
    # class Meta:
    #     model = SingUp

admin.site.register(SingUp, SingUpAdmin)
