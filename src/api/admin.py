from django.contrib import admin

from api.models import CustomUser, Plotter, Pattern

admin.site.register(CustomUser)
admin.site.register(Plotter)
admin.site.register(Pattern)
