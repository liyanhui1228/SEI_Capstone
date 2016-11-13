from django.db import models
from django.contrib.auth.models import User
import datetime

YEAR_CHOICES = []
for r in range(1980, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))

ExpenseCategory = (
    ('T', 'Travel'),
    ('S', 'Subcontractor'),
    ('E', 'Equipment'),
    ('O', 'Others'),
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
    organization_name=models.CharField(max_length=100)
    contact_name=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    address=models.CharField(max_length=200)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=2)
    zipcode=models.CharField(max_length=5)

class Team(models.Model):
    team_name=models.CharField(max_length=50)
    manager=models.ForeignKey(User, related_name="manageer", on_delete=models.CASCADE)
    directorate=models.ForeignKey(User, related_name="directorate", on_delete=models.CASCADE)
    division=models.CharField(max_length=50)

class Employee(models.Model):
    SYSTEM_USER_ROLE = (
        ('ADMIN', 'Administrator'),
        ('NM', 'NormalUser'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    activation_key = models.CharField(max_length=255)
    position = models.CharField(max_length=100,default="", blank=True)
    title = models.CharField(max_length=100,default="", blank=True)
    internal_salary = models.DecimalField(max_digits=8, decimal_places=2)
    external_salary = models.DecimalField(max_digits=8, decimal_places=2)
    is_internal = models.BooleanField()
    team=models.ForeignKey(Team)
    isActive = models.BooleanField(default=True)
    user_role = models.CharField(max_length=20, choices=SYSTEM_USER_ROLE)
    permission_description = models.CharField(max_length=200, default="", blank=True)

class Project(models.Model):
    project_id = models.IntegerField(max_length=20, primary_key=True)
    PWP_num = models.CharField(max_length=20)
    project_description = models.CharField(max_length=200, default="", blank=True)
    project_budget = models.DecimalField(max_digits=8, decimal_places=2)
    is_internal = models.BooleanField(default=True)
    team = models.ForeignKey(Employee,on_delete=models.CASCADE)
    client = models.ForeignKey(Client,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class ProjectMonth(models.Model):
    ##should try to find a way to provide only year field??
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    month = models.CharField(max_length=30)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    team = models.ForeignKey(Employee, on_delete=models.CASCADE)

class ProjectExpense(models.Model):
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    expense_description = models.CharField(max_length=200, default="", blank=True)
    category = models.CharField(max_length=50, choices=ExpenseCategory)
    project_month = models.ForeignKey(ProjectMonth, on_delete=models.CASCADE)

class EmployeeList(models.Model):
    month = models.DateField()
    time_use = models.IntegerField()
    month_cost = models.DecimalField(max_digits=8, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project_month = models.ForeignKey(ProjectMonth, on_delete=models.CASCADE)
    isExternal = models.BooleanField()

class SalaryHistory(models.Model):
    effective_from = models.DateField()
    effective_until = models.DateField(null=True)
    internal_salary = models.FloatField()
    external_salary = models.FloatField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

class Log(models.Model):
    date_time = models.DateField(auto_now_add=True)
    change = models.CharField(max_length=500)
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)

class EmployeeAvailability(models.Model):
    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)
    ##wants to illustrate in a project month availablility?? should have foreign key in project month??
    month = models.CharField(max_length=30)
    percentage_used = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

class ChargeString(models.Model):
    charge=models.FloatField()
    date=models.DateField()
    project=models.ForeignKey(Project, on_delete=models.CASCADE)




