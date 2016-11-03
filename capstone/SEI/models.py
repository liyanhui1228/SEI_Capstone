from django.db import models


class System_user(models.Model):
    #need to restrict enumeration type
    SYSTEM_USER_ROLE=(
        ('ADMIN','Administrator'),
        ('NM','NormalUser')
    )
    user_role = models.CharField(max_length=20,choices=SYSTEM_USER_ROLE)
    permission_description = models.CharField(max_length=200)
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)

class Category(models.Model):
    category=models.CharField(max_length=100)

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

class SalaryHistory(models.Model):
    effective_from = models.DateField()
    effective_until = models.DateField(null=True)
    internal_salary = models.FloatField()
    external_salary = models.FloatField()
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)

class Log(models.Model):
    date_time = models.DateField(auto_now_add=True)
    change = models.CharField(max_length=500)
    user = models.ForeignKey(System_user,on_delete=models.CASCADE)

class employee_availability(models.Model):
    year=models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    percentage_used = models.FloatField()
    is_available = models.BooleanField()
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)

class charge_string(models.Model):
    charge=models.FloatField()
    date=models.DateField()
    project=models.ForeignKey(Project, on_delete=models.CASCADE)

class project(models.Model):
    PWP_num=models.IntegerField()
    project_description=models.CharField(max_length=200)
    project_budget=models.FloatField()
    is_internal=models.BooleanField()
    team = models.ForeignKey(Employee,on_delete=models.CASCADE)
    client=models.ForeignKey(Client,on_delete=models.CASCADE)
    start_date=models.DateField()
    end_date=models.DateField()

class team(models.Model):
    team_name=models.CharField(max_length=50)
    manager=models.ForeignKey(Employee,on_delete=models.CASCADE)
    directorate=models.ForeignKey(Employee,on_delete=models.CASCADE)
    division=models.CharField(max_length=50)

class Employee(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    position=models.CharField(max_length=100)
    title=models.CharField(max_length=100)
    internal_salary=models.FloatField()
    external_salary=models.FloatField()
    team=models.ForeignKey(team)
    isActive=models.BooleanField()

class employee_list(models.Model):
    month=models.FloatField()
    time_use=models.FloatField()
    month_cost=models.FloatField()
    employee=models.ForeignKey(Employee)
    project_month=models.ForeignKey(ProjectMonth)
    isExternal=models.BooleanField()

