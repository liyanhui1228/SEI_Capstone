from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    category=models.CharField(max_length=100)

class Project(models.Model):
    PWP_num=models.CharField(max_length=20)
    project_description=models.CharField(max_length=200, default="", blank=True)
    project_budget=models.FloatField()
    is_internal=models.BooleanField(default=True)
    #team = models.ForeignKey(Employee,on_delete=models.CASCADE)
    #client=models.ForeignKey(Client,on_delete=models.CASCADE)
    start_date=models.DateField()
    end_date=models.DateField()

class Client(models.Model):
    organization_name=models.CharField(max_length=100)
    contact_name=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    address=models.CharField(max_length=200)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=2)
    zipcode=models.CharField(max_length=5)

class ProjectMonth(models.Model):
    year=models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    budget=models.FloatField()
    project=models.ForeignKey(Project, on_delete=models.CASCADE)

class ProjectExpense(models.Model):
    cost=models.FloatField()
    expense_description=models.CharField(max_length=200)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)
    project_month=models.ForeignKey(ProjectMonth, on_delete=models.CASCADE)

class Employee(models.Model):
    SYSTEM_USER_ROLE = (
        ('ADMIN', 'Administrator'),
        ('NM', 'NormalUser'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    activation_key = models.CharField(max_length=255)
    position=models.CharField(max_length=100,default="", blank=True)
    title=models.CharField(max_length=100,default="", blank=True)
    internal_salary=models.FloatField(default=0, blank=True)
    external_salary=models.FloatField(default=0, blank=True)
    #team=models.ForeignKey(Team)
    isActive=models.BooleanField(default=True)
    user_role = models.CharField(max_length=20, choices=SYSTEM_USER_ROLE)
    permission_description = models.CharField(max_length=200, default="", blank=True)

class EmployeeList(models.Model):
    month=models.FloatField()
    time_use=models.FloatField()
    month_cost=models.FloatField()
    employee=models.ForeignKey(Employee)
    project_month=models.ForeignKey(ProjectMonth)
    isExternal=models.BooleanField()

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
    year=models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    percentage_used = models.FloatField()
    is_available = models.BooleanField()
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)

class ChargeString(models.Model):
    charge=models.FloatField()
    date=models.DateField()
    project=models.ForeignKey(Project, on_delete=models.CASCADE)

class Team(models.Model):
    team_name=models.CharField(max_length=50)
    manager=models.ForeignKey(Employee, related_name="manageer", on_delete=models.CASCADE)
    directorate=models.ForeignKey(Employee, related_name="directorate", on_delete=models.CASCADE)
    division=models.CharField(max_length=50)



