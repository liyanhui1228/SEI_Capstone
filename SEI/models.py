from django.db import models
from django.contrib.auth.models import User
import datetime

from phonenumber_field.modelfields import PhoneNumberField

# YEAR_CHOICES = []
# for r in range(1980, (datetime.datetime.now().year+1)):
#     YEAR_CHOICES.append((r,r))

ExpenseCategory = (
    ('T', 'Travel'),
    ('S', 'Subcontractor'),
    ('E', 'Equipment'),
    ('O', 'Others'),
)

SYSTEM_USER_ROLE = (
    ('ADMIN', 'Administrator'),
    ('NM', 'NormalUser'),
    ('ITADMIN', 'ITAdministrator'),
    )
# MonthCategory = (
#     ('January', 'January'),
#     ('February', 'February'),
#     ('March', 'March'),
#     ('April', 'April'),
#     ('May', 'May'),
#     ('June', 'June'),
#     ('July', 'July'),
#     ('August', 'August'),
#     ('September', 'September'),
#     ('October', 'October'),
#     ('November', 'November'),
#     ('December', 'December'),
# )

class Client(models.Model):
    organization_name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    phone = PhoneNumberField(default='')
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)

class Team(models.Model):
    team_name = models.CharField(max_length=50)
    manager = models.ForeignKey('Employee', related_name="manageer", on_delete=models.CASCADE, blank=True, null=True)
    directorate = models.ForeignKey('Employee', related_name="directorate", on_delete=models.CASCADE, blank=True, null=True)
    division = models.CharField(max_length=50)

class Employee(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=200, default="", blank=True)
    last_name = models.CharField(max_length=200, default="", blank=True)
    position = models.CharField(max_length=100,default="", blank=True)
    title = models.CharField(max_length=100,default="", blank=True)
    internal_salary = models.DecimalField(max_digits=8, decimal_places=2)
    external_salary = models.DecimalField(max_digits=8, decimal_places=2)
    team = models.ForeignKey(Team)

class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    activation_key=models.CharField(max_length=300)
    user_role = models.CharField(max_length=20, choices=SYSTEM_USER_ROLE, default='NM')
    permission_description = models.CharField(max_length=200, default="", blank=True)

class Project(models.Model):
    #project_id = models.IntegerField(primary_key=True)
    PWP_num = models.CharField(max_length=20)
    project_description = models.CharField(max_length=200, default="", blank=True)
    project_budget = models.DecimalField(max_digits=8, decimal_places=2)
    is_internal = models.BooleanField(default=True)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    business_manager = models.CharField(max_length=100, default="", blank=True)

class ProjectMonth(models.Model):
    project_date = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee_list = models.ManyToManyField(Employee, related_name='do_project_this_month', symmetrical=False)
    budget = models.DecimalField(max_digits=18, decimal_places=2)

class EmployeeMonth(models.Model):
    project_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    time_use = models.IntegerField(null=True)
    isExternal = models.BooleanField(default=0)
    month_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True)

class ProjectExpense(models.Model):
    project_date = models.DateField()
    cost = models.DecimalField(max_digits=18, decimal_places=2)
    expense_description = models.CharField(max_length=200, default="", blank=True)
    category = models.CharField(max_length=50, choices=ExpenseCategory)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class SalaryHistory(models.Model):
    effective_from = models.DateField()
    effective_until = models.DateField(null=True)
    internal_salary = models.DecimalField(max_digits=8, decimal_places=2)
    external_salary = models.DecimalField(max_digits=8, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

class Log(models.Model):
    date_time = models.DateField(auto_now_add=True)
    change = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class EmployeeAvailability(models.Model):
    date = models.DateField()
    percentage_used = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

class ChargeString(models.Model):
    charge = models.CharField(max_length=100, default="", blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
