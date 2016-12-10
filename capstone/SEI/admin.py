from django.contrib import admin
from SEI.forms import *
from SEI.models import *

# Register your models here.
from django.contrib import admin

admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Employee)
admin.site.register(Team)
admin.site.register(ProjectMonth)
admin.site.register(EmployeeMonth)
admin.site.register(ProjectExpense)
