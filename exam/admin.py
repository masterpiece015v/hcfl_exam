from django.contrib import admin
from .models import User,Question,Test
# Register your models here.

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Test)