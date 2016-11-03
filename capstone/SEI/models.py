from django.db import models


USER_TYPE_CHOICES = (
    ('0', 'director'),
    ('1', 'manager'),
    ('2', 'employee'),
)
# Create your models here.
class User(models.Model):
    firstName=models.CharField(max_length=200)
    lastName=models.CharField(max_length=200)
    email=models.CharField(max_length=200)
    role=models.CharField(max_length=1,choices=USER_TYPE_CHOICES)
    password=models.CharField(max_length=200)
    username=models.CharField(max_length=200)

class Category(models.Model):
    category_id=models.IntegerField()
    category=models.CharField(max_length=20)

class Client(models.Model):
    client_id=models.IntegerField()
    organization_name=models.CharField(max_length=20)
    contact_name=models.CharField(max_length=20)
    phone=models.CharField(max_length=20)
    address=models.CharField(max_length=40)
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=2)
    zipcode=models.CharField(max_length=10)

class ProjectMonth(models.Model):
    project_month_id=models.IntegerField()
    month=models.IntegerField()
    budget=models.FloatField()
    project_id=models.ForeignKey(Project, on_delete=models.CASCADE)

class ProjectExpense(models.Model):
    project_expense_id=models.IntegerField()
    cost=models.FloatField()
    expense_description=models.CharField(max_length=50)
    category_id=models.ForeignKey(Category, on_delete=models.CASCADE)
    project_month_id=models.ForeignKey(ProjectMonth, on_delete=models.CASCADE)

class Project(models.Model):
    pass

class Employee(models.Model):
    pass

class SalaryHistory(models.Model):
    salary_history_id=models.IntegerField(primary_key=True)
    effective_from = models.DateField()
    effective_until = models.DateField()
    internal_salary = models.FloatField()
    external_salary = models.FloatField()
    employee_id = models.ForeignKey(Employee,on_delete=models.CASCADE)

class System_user(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_role = models.CharField(max_length=20)
    permission_description = models.CharField(max_length=50)
    employee_id = models.ForeignKey(Employee,on_delete=models.CASCADE)

class log(models.Model):
    log_id = models.IntegerField(primary_key=True)
    date_time = models.DateField()
    change = models.CharField(max_length=500)
    user_id = models.ForeignKey(System_user,on_delete=models.CASCADE)

class employee_availability(models.Model):
    emp_availability_id = models.IntegerField(primary_key=True)
    month = models.IntegerField()
    percentage_used = models.FloatField()
    is_available = models.IntegerField()
    employee_id = models.ForeignKey(Employee,on_delete=models.CASCADE)