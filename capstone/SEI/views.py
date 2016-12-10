from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required,permission_required
from django.db import transaction
# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
import json
from datetime import date, datetime
import decimal
from SEI.models import *
from SEI.forms import *
from SEI.models import ProjectMonth
from django.core import serializers
from django.forms.models import model_to_dict
from django.forms.formsets import formset_factory
from django.forms import inlineformset_factory
import collections
import csv
from django.utils.encoding import smart_str
import pdb
from django.utils.dateparse import parse_datetime
from dateutil.relativedelta import relativedelta


# Reset the percentage_used in employee availability table to 0 at the beginning of every month
def reset_employee_availability_at_begin_of_month():
    pass


# For solving the decimal is not serializable error when dumping json
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

@login_required
def home(request):
    ####TO DO
    #If IT Admin will redirect to add users page

    #Else Need to check for team record
    #If person is manager or direcorate show their team view

    #elif show their employee view

    #otherwise show project search
    return render(request, 'SEI/home.html')


@login_required
def projectview(request, PWP_num):
    #if no project passed in, show search bar only
    if PWP_num == '':
        return render(request, 'SEI/projectview.html')

    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    context['project'] = project_item
    context['report'] = ReportForm()
    return render(request, 'SEI/projectview.html', context)


@login_required
@transaction.atomic
@permission_required('SEI.add_project')
def add_project(request):
    context = {}

    #TO DO uncomment once user admin is working
    #profile_item = get_object_or_404(Profile, user=request.user)
    #if profile_item.user_role == 'NM':
    #    return render(request, 'SEI/permission.html', context)

    ChargeStringFormSet = formset_factory(ChargeStringForm)
    if request.method == "GET":
        form = ProjectForm()
        formset = ChargeStringFormSet()
        context['form'] = form
        context['chargestring_formset'] = formset
        return render(request, 'SEI/project.html', context)

    form = ProjectForm(request.POST)
    formset = ChargeStringFormSet(data=request.POST)

    if not form.is_valid():
        return render(request, 'SEI/project.html', context)

    new_project = form.save()

    #save charge strings
    if formset.is_valid():
        for cs_form in formset:
            if 'charge_string' in cs_form.cleaned_data and cs_form.cleaned_data['charge_string'] != '':
                new_charge_string = ChargeString(charge_string=cs_form.cleaned_data['charge_string'],\
                    project = new_project)
                new_charge_string.save()

    return redirect('projectview', PWP_num=form.cleaned_data['PWP_num'])


##not working
@login_required
@transaction.atomic
@permission_required('SEI.change_project')
def edit_project(request, PWP_num):
    
    ChargeStringFormSet = formset_factory(ChargeStringForm)
    if request.method == 'GET':
        project_item = get_object_or_404(Project,PWP_num=PWP_num)
        project_form = ProjectForm(instance=project_item)
        formset = ChargeStringFormSet()
        context={}
        context['form'] = project_form
        context['PWP_num']=project_item.PWP_num
        context['chargestring_formset'] = formset
        return render(request, 'SEI/edit_project.html', context)
    
    project_item = get_object_or_404(Project,PWP_num=PWP_num)
    project_form=ProjectForm(request.POST,instance=project_item)
    formset = ChargeStringFormSet(data=request.POST)

    if project_form.is_valid():
        project_form.save()
        return redirect(reverse('projectsearch'))

    #save charge strings
    if formset.is_valid():
        for cs_form in formset:
            if 'charge_string' in cs_form.cleaned_data and cs_form.cleaned_data['charge_string'] != '':
                new_charge_string = ChargeString(charge_string=cs_form.cleaned_data['charge_string'],\
                    project = new_project)
                new_charge_string.save()

    return render(request,'SEI/edit_project.html',{'form':project_form})


        

@login_required
def profile(request, user_name):
    context = {}
    user_item = get_object_or_404(User, username=user_name)
    try:
        user_profile = Employee.objects.get(user=user_item)
    except:
        user_profile = Employee(user=user_item)
    context['employee'] = user_profile

    return render(request, 'SEI/employee.html', context)


##still need to check whether normal user can edit his/her own file, should have one more parameter
##can add a if tag in the template to hide salary and role from normal user
@login_required
@transaction.atomic
def update_profile(request):
    context = {}

    employee_item = get_object_or_404(Employee, user=request.user)
    if employee_item.user_role == 'NM':
        return render(request, 'SEI/permission.html', context)

    try:
        user_profile = Employee.objects.get(user=request.user)
    except:
        user_profile = Employee(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = EmployeeForm(request.POST, instance=user_profile)
        context['form'] = profile_form
        context['sub_form'] = user_form
        if all([user_form.is_valid(), profile_form.is_valid()]):
            user_form.save()
            profile_form.save()
            return redirect('profile', user_name=request.user.username)
        else:
            return render(request, 'SEI/edit_profile.html', context)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = EmployeeForm(instance=user_profile)
    return render(request, 'SEI/edit_profile.html', {
        'sub_form': user_form,
        'form': profile_form
    })


@transaction.atomic
@permission_required('SEI.add_user')
def register(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'SEI/registration.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'SEI/registration.html', context)

    ## create new_user
    new_user = User.objects.create_user(username=form.cleaned_data['user_name'], \
                                        first_name=form.cleaned_data['first_name'], \
                                        last_name=form.cleaned_data['last_name'], \
                                        password=form.cleaned_data['password1'], \
                                        email=form.cleaned_data['email'])
    new_user.is_active = False
    new_user.save()

    token = default_token_generator.make_token(new_user)

    user_profile = Profile(user=new_user, activation_key=token)
    user_profile.save()

    email_body = """
Welcome to ! Please click the link below to verify your email address and complete the registration of your account:
http://%s%s
    """ % (request.get_host(),
           reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email account",
              message=email_body,
              from_email="siyangli@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'SEI/needs-confirmation.html', context)


@transaction.atomic
@permission_required('SEI.add_user')
def confirm_register(request, user_name, token):
    try:
        user_item = User.objects.get(username=user_name)
        user_profile = Profile.objects.get(user=user_item)
        if user_profile.activation_key == token:
            user_item.is_active = True
            user_item.save()
            # Logs in the new user and redirects to his/her Employee page
            # this doesn't work because we need to put raw password here rather than the hashed password
            # maybe because the authentication backend have some mechanism to hash the password.
            # new_user = authenticate(username=user_name, password='123')
            # login(request, new_user)
            # print("in here")
            return redirect(reverse('home'))
        else:
            print("sorry")
    except Exception as e:
        print(e)
        return redirect(reverse('home'))


@login_required
def project_overview(request, PWP_num):
    """
    get the JSON for overall project model information plus client and team information
    :param request: Request
    :param PWP_num: PWP_num,unique identifier for a project
    :return: JSON format of project overview
    """
    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num) 
    charge_string = ChargeString.objects.filter(project=project_item)
    context['PWP_num'] = project_item.PWP_num
    context['project_description'] = project_item.project_description
    context['project_budget'] = project_item.project_budget
    context['isExternal'] = project_item.is_internal
    if project_item.team != None:
        context['team_name'] = project_item.team.team_name
    else:
        context['team_name'] = ""
    context['organization_name'] = project_item.client_name
    context['start_date'] = project_item.start_date
    context['end_date'] = project_item.end_date
    context['charge_string'] = charge_string
    return render(request,'SEI/overview.json',context)


@login_required
def budget_view(request, PWP_num):
    """
    view the overall and monthly budget and expense information for a specific project
    including employee salary and other categories expense
    :param request: Request
    :param PWP_num: PWP_num,unique identifier for a project
    :return: JSON format of budget
    """
    now = datetime.datetime.now()
    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    project_month_list = ProjectMonth.objects.filter(project=project_item)
    context['total_budget'] = project_item.project_budget
    total_expense = 0
    total_expense_till_now = 0

    resource_allocation = {}
    for pm in project_month_list:
        monthly_cost = {}
        project_expense = ProjectExpense.objects.filter(project=project_item, project_date=pm.project_date)
        employee_month = EmployeeMonth.objects.filter(project=project_item, project_date=pm.project_date)

        # Get the total Person cost in this month for this project
        person_cost = 0
        for em in employee_month:
            person_cost += em.month_cost

        monthly_cost['person'] = person_cost

        # Get the Travel, Subcontractor, Equipment, Other cost in this month for this project
        travel_cost = 0
        subcontractor_cost = 0
        equipment_cost = 0
        other_cost = 0
        for pe in project_expense:
            if pe.category == "('T', 'Travel')":
                travel_cost += pe.cost
            if pe.category == "('S', 'Subcontractor')":
                subcontractor_cost += pe.cost
            if pe.category == "('E', 'Equipment')":
                equipment_cost += pe.cost
            if pe.category == "('O', 'Others')":
                other_cost += pe.cost

        monthly_cost['travel'] = travel_cost
        monthly_cost['subcontractor'] = subcontractor_cost
        monthly_cost['equipment'] = equipment_cost
        monthly_cost['other'] = other_cost
        monthly_total_cost = travel_cost + subcontractor_cost + equipment_cost + other_cost + person_cost
        monthly_cost['monthly_total_expense'] = monthly_total_cost
        total_expense += monthly_total_cost
        #if now.date() > pm.project_date:
        total_expense_till_now += monthly_total_cost
        monthly_cost['monthly_budget'] = pm.budget
        # Store all the 5 kinds of cost in JSON, the key is project_date
        resource_allocation[pm.project_date] = monthly_cost

    context['resource_allocation'] = resource_allocation
    context['budget_balance'] = context['total_budget'] - total_expense_till_now
    context['projected_expense'] = total_expense - total_expense_till_now
    context['projected_remaining'] = context['total_budget'] - total_expense
    return render(request, "SEI/budget_view.json",context)

@login_required
def project_resource(request, PWP_num):
    """
    Gets the project resources for a given project and year to display in the project view graph
    returns the JSON for d3 chart in
    :param request: Request
    :param PWP_num: PWP_num,unique identifier for a project
    :return: JSON format of budget
    """
    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    #project_month_list = ProjectMonth.objects.filter(project=project_item, project_date__year = 2016)

    resource_chart = collections.defaultdict(list)
    resource_names = {}
    #for pm in project_month_list:
    
    project_expense = ProjectExpense.objects.filter(project=project_item)
    employee_month = EmployeeMonth.objects.filter(project=project_item)

    #get all employees assigned for the given date
    for em in employee_month:
        resource_chart[em.employee.id].append([str(em.project_date), em.time_use])
        resource_names[em.employee.id] = em.employee.first_name + " " + em.employee.last_name

    # Get the Travel, Subcontractor, Equipment, Other cost in this month for this project
    travel_cost = 0
    subcontractor_cost = 0
    equipment_cost = 0
    other_cost = 0
    for pe in project_expense:
        resource_chart[pe.id].append([project_date, pe.cost])
        resource_names[pe.id] = (pe.category, pe.expense_description)

    # Store all the 5 kinds of cost in JSON, the key is project_date
    context['resource_allocation'] = [{'measure':value, 'data':resource_chart[key]} for key, value in resource_names.items()]
    return HttpResponse(json.dumps(context))

@login_required
def view_employee_list(request, PWP_num, project_date_year, project_date_month):
    context = {}
    project_year_month = str(project_date_year) + '-' + str(project_date_month) + '-01'
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    project_month = ProjectMonth.objects.get_or_create(project=project_item, project_date=project_year_month)
    employee_list_all = Employee.objects.filter()

    employee_list_projectmonth = project_month[0].employee_list.all()

    employee_in_this_project = {}
    employee_not_available = []
    employee_available = {}

    # Get the employee already doing this project in this month, which is to be excluded
    for el in employee_list_projectmonth:
        employee_in_this_project[el.id] = el.first_name + ' ' + el.last_name
        employee_not_available.append(el.id)

    # Get the employee available for choosing, and show their availability
    for emp in employee_list_all:
        if(emp.id not in employee_not_available):
            employee_availability = EmployeeAvailability.objects.get_or_create(employee=emp, date=project_year_month)
            percentage_used = employee_availability[0].percentage_used
            emp_detail = {}
            emp_detail['name'] = emp.first_name + ' ' + emp.last_name
            emp_detail['percentage_used'] = percentage_used
            employee_available[emp.id] = emp_detail

    emp_list_result = {}
    emp_list_result['employee_in_this_project'] = employee_in_this_project
    emp_list_result['employee_available'] = employee_available
    emp_list_result = json.dumps(emp_list_result, default=decimal_default)

    context['employee_list'] = emp_list_result
    return render(request, "SEI/employee_list.json", context)

@login_required
@permission_required('SEI.add_project')
def add_employee(employee_chosen, PWP_num, project_date):
    context = {}
    alert = {}
    detail = {} # The alert details
    #PWP_num = employee_chosen_json['PWP_num']
    #emp_chosen_list = employee_chosen_json['emp_chosen_list']
    #project_date = employee_chosen_json['project_date']
    emp_detail = employee_chosen.cleaned_data
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    project_month = ProjectMonth.objects.filter(project=project_item, project_date=project_date)

    # The key of emp_chosen_list is the employee id
    #for emp_detail in emp_chosen_list:
    emp_id = emp_detail['employee']
    time_to_use = emp_detail['time_use']
    is_external = emp_detail['isExternal']
    emp = Employee.objects.filter(id=emp_id)
    rate = emp_detail.external_salary if is_external else emp_detail.internal_salary
    month_cost = float(time_to_use)/100*rate

    # Insert a new record to EmployeeMonth
    employee_month, created = EmployeeMonth.objects.get_or_create(project_date=project_date, project=project_item, employee=emp[0])
    employee_month.time_use=time_to_use
    employee_month.isExternal=is_external
    employee_month.month_cost=month_cost
    employee_month.save()

    # Add this employee to employee_list in ProjectMonth
    project_month[0].employee_list.add(emp[0])

    # Update the percentage_used in EmployeeAvailability, if over 100%, send back the alert, alert is null means no alert
    emp_availability, created = EmployeeAvailability.objects.get_or_create(employee=emp[0], date=project_date)
    emp_availability.percentage_used += time_to_use
    if(emp_availability.percentage_used >= 100):
        emp_availability.is_available = 0
        detail[emp[0].id] = emp_availability.percentage_used
    emp_availability.save()
    print(emp_availability.percentage_used)
    alert['alert'] = detail
    alert = json.dumps(alert, default=decimal_default)
    context['alert'] = alert
    return context

@login_required
def get_employee(request,first_name, last_name):
    employees=Employee.objects.filter(first_name=first_name, last_name=last_name)
    employee_list = []
    for emp in employees:
        emp_detail = model_to_dict(emp)
        emp_detail['team_name'] = emp.team.team_name
        employee_list.append(emp_detail)
    emp_list_result = json.dumps(employee_list, default=decimal_default)
    return HttpResponse(emp_list_result, content_type="application/json")

def get_employee_project(request,employee_id):
    today = datetime.datetime.today()
    employee=get_object_or_404(Employee,id=employee_id)
    five_month_before_date= today - datetime.timedelta(5*365/12)
    five_month_before = str(five_month_before_date.year) + '-' + str(five_month_before_date.month) + '-01'
    current_month = str(today.year) + '-' + str(today.month) + '-01'
    Tasks=EmployeeMonth.objects.filter(employee=employee,project_date__gt=five_month_before,project_date__lte=current_month)
    print(len(Tasks))
    time_sum={}
    projects={}
    for task in Tasks:
        print(task.project)
        dateKey=task.project_date
        print(dateKey)
        project={}
        project['PWP_num']=task.project.PWP_num
        project['time_use']=task.time_use
        time_sum[str(dateKey)]= time_sum.get(str(dateKey),0) + task.time_use
        if str(dateKey) in projects:
            projects[str(dateKey)].append(project)
        else:
            project_list=[]
            project_list.append(project)
            projects[str(dateKey)]=project_list

    for date in projects:
        total_time=time_sum.get(str(date),0)
        if total_time != 0:
            for project in projects[str(date)]:
                project['percentage']="%.2f" %  (project['time_use']*100.0/total_time)

    return HttpResponse(json.dumps(projects))

@login_required
def get_employee_allocation(request,employee_id,year):
    context = {}
    employee = get_object_or_404(Employee, id = employee_id)
    employee_month_list = EmployeeMonth.objects.filter(employee=employee, project_date__year=year)

    resource_chart = collections.defaultdict(list)
    for em in employee_month_list:
        resource_chart[em.project.PWP_num].append([str(em.project_date), em.time_use])

    context['resource_chart_data'] = [{'measure':key, 'data':value} for key, value in resource_chart.items()]

    return HttpResponse(json.dumps(context))

@login_required
@permission_required('SEI.add_projectmonth')
def add_resources(request, PWP_num, project_year, project_month):
    context = {}
    messages = []
    context['messages'] = messages
    project_item = get_object_or_404(Project, PWP_num = PWP_num)
    project_team_emp = Employee.objects.filter(team = project_item.team)
    project_date = str(project_year) + '-' + str(project_month) + '-01'

    ProjectExpenseFormSet = formset_factory(ProjectExpenseForm)
    EmployeeMonthFormSet = formset_factory(EmployeeMonthForm)

    if request.method == "GET":
        form = ProjectMonthForm()
        otherexpense = ProjectExpenseFormSet(prefix="otherexpense")
        employeeexpense = EmployeeMonthFormSet(prefix="employeeexpense")

        for index, emp in enumerate(project_team_emp):
            emp_name = emp.first_name + ' ' + emp.last_name
            em = EmployeeMonthForm(initial={'employee': emp, 'internal_salary': emp.internal_salary, 'external_salary': emp.external_salary, 'employee_name': emp_name})
            if index == 0:
                employeeexpense.forms[0] = em
            else:
                employeeexpense.forms.append(em)

        context['otherexpense'] = otherexpense
        context['employeeexpense'] = employeeexpense
        context['project'] = project_item
        context['project_year'] = project_year
        context['project_month'] = project_month
        return render(request, 'SEI/resource.html', context)

    if request.method == "POST":
        form = ProjectMonthForm(request.POST)
        otherexpense = ProjectExpenseFormSet(request.POST, prefix="otherexpense")
        employeeexpense = EmployeeMonthFormSet(request.POST, prefix="employeeexpense")

        if otherexpense.is_valid():
            for othexp in otherexpense:
                #if 'charge_string' in cs_form.cleaned_data and cs_form.cleaned_data['charge_string'] != '':
                if othexp.is_valid() and 'cost' in othexp.cleaned_data and 'category' in othexp.cleaned_data:
                    new_project_expense = ProjectExpense(project_date = project_date,
                                     cost=othexp.cleaned_data['cost'],
                                     expense_description=othexp.cleaned_data['expense_description'],
                                     category=othexp.cleaned_data['category'],
                                     project=project_item)
                    new_project_expense.save()

        if employeeexpense.is_valid():
            for empexp in employeeexpense:
                #if 'charge_string' in cs_form.cleaned_data and cs_form.cleaned_data['charge_string'] != '':
                if empexp.is_valid() and 'time_use' in empexp.cleaned_data:
                    add_employee(empexp, PWP_num, project_date)

        context['otherexpense'] = otherexpense
        context['employeeexpense'] = employeeexpense
        context['project'] = project_item
        context['project_year'] = project_year
        context['project_month'] = project_month

        #project_month_item.add(new_project_expense)
        #project_month_item.save()
        messages.append("Expense has been saved")

    return render(request, 'SEI/resource.html', context)

@login_required
@permission_required('SEI.add_projectmonth')
def add_expense(request,expense_detail):
    """
    add expense_detail for a specific project in category: travel, subcontractor, etc
    :param request: Request
    :param expense_detail: Expense detail in JSON format
    :return: confirmation page?
    """
    expense_detail_json = json.load(expense_detail)
    PWP_num = expense_detail_json['PWP_num']
    project_date = expense_detail_json['project_date']
    cost=expense_detail_json['cost']
    expense_description = expense_detail_json['expense_description']
    category=expense_detail_json['category']
    project=get_object_or_404(Project,PWP_num = PWP_num)
    new_expense_detail=ProjectExpense(project_date=project_date,cost=cost,\
                                      expense_description=expense_description,category=category,\
                                      project=project)
    new_expense_detail.save()

@login_required
def employeeview(request, employee_id):
    #if no project passed in, show search bar only

    if employee_id == '' or employee_id == None:
        #add call to get system user information by default
        #user = request.user
        #employee_item = get_object_or_404(Employee, first_name=user.first_name and )
        return render(request, 'SEI/employeeview.html')

    context = {}
    employee_item = get_object_or_404(Employee, id=employee_id)
    context['employee'] = employee_item

    return render(request, 'SEI/employeeview.html', context)

# @login_required
# @transaction.atomic
@permission_required('SEI.add_team')
def add_team(request):
    #user_profile = get_object_or_404(Profile, user = request.user)
    context = {}
    messages = []
    context['messages'] = messages
    if user_profile.user_role == 'ITADMIN' or user_profile.user_role == 'ADMIN':
        return render(request, 'SEI/permission.html', context)

    if request.method == 'GET':
        form = TeamForm()
        context['form'] = form
        return render(request, 'SEI/addTeam.html', context)

    form = TeamForm(request.POST)
    if not form.is_valid():
        context['form'] = form
        messages.append("Form contained invalid data")
        return render(request, 'SEI/addTeam.html', context)

    form.save()
    messages.append("A new team has been added")
    return render(request, 'SEI/addTeam.html', context)

# @login_required
# @transaction.atomic
@permission_required('SEI.add_team')
def admin_team(request):
    #user_profile = get_object_or_404(Profile, user = request.user)
    context = {}
    messages = []
    #if user_profile.user_role == 'ITADMIN' or user_profile.user_role == 'ADMIN':
    #    return render(request, 'SEI/permission.html', context)

    teams = Team.objects.all()
    context['teams'] = teams

    if request.method == 'GET':
        form = TeamForm()
        context['form'] = form
        return render(request, 'SEI/admin_team.html', context)

    form = TeamForm(request.POST)
    if not form.is_valid():
        context['form'] = form
        messages.append("Form contained invalid data")
        return render(request, 'SEI/admin_team.html', context)
    else:
        form.save()
        messages.append("A new team has been added")
        form = TeamForm()
        context['form'] = form

    return render(request, 'SEI/admin_team.html', context)

@login_required
@permission_required('SEI.change_team')
def edit_team(request,team_id):

    if request.method=='GET':
        team = get_object_or_404(Team,id=team_id)
        form=TeamForm(instance=team)
        return render(request,'SEI/edit_team.html',{'form':form,'id':team.id})

    team=get_object_or_404(Team,id=team_id)
    form=TeamForm(request.POST,instance=team)
    if not form.is_valid():
        context['form']=form
        return render(request,'SEI/edit_team.html',context)
    else:
        form.save()
        return redirect(reverse('adminTeam'))

@login_required
@permission_required('SEI.change_employee')
def edit_employee(request,employee_id):

    if request.method=='GET':
        employee = get_object_or_404(Employee,id=employee_id)
        form=EmployeeForm(instance=employee)
        return render(request,'SEI/edit_employee.html',{'form':form,'id':employee.id})

    employee=get_object_or_404(Employee,id=employee_id)
    form=EmployeeForm(request.POST,instance=employee)
    if not form.is_valid():
        context['form']=form
        return render(request,'SEI/edit_employee.html',context)
    else:
        form.save()
        return redirect(reverse('search_employee'))


##@login_required
def view_team(request, team_id):
    #user_profile = get_object_or_404(Profile, user = request.user)
    context = {}
    #if user_profile.user_role == 'ITADMIN':
    #    return render(request, 'SEI/permission.html', context)

    if team_id != None:
        team = get_object_or_404(Team, id = team_id)

    project_set = Project.objects.filter(team = team)
    employee_set = Employee.objects.filter(team = team)

    ##show team info
    context['team'] = team

    ##show project
    context['projects'] = project_set

    ##show employee
    context['employees'] = employee_set

    return render(request, 'SEI/teamview.html', context)

def admin_employee(request):
    #user_profile = get_object_or_404(Profile, user = request.user)
    context = {}
    messages = []
    #if user_profile.user_role == 'ITADMIN' or user_profile.user_role == 'ADMIN':
    #    return render(request, 'SEI/permission.html', context)

    employees = Employee.objects.all()
    context['employees'] = employees

    if request.method == 'GET':
        form = EmployeeForm()
        context['form'] = form
        return render(request, 'SEI/admin_employee.html', context)

    form = EmployeeForm(request.POST)
    if not form.is_valid():
        context['form'] = form
        messages.append("Form contained invalid data")
        return render(request, 'SEI/admin_employee.html', context)
    else:
        form.save()
        messages.append("A new employee has been added")
        form = EmployeeForm()
        context['form'] = form

    return render(request, 'SEI/admin_employee.html', context)

@login_required
def search_team(request):
    #user_profile = get_object_or_404(Profile, user = request.user)
    #if user_profile.user_role == 'ITADMIN':
    #    return render(request, 'SEI/permission.html')

    return render(request, 'SEI/teamview.html')

@login_required
def search_employee(request):
    #user_profile = get_object_or_404(Profile, user = request.user)
    #if user_profile.user_role == 'ITADMIN':
    #    return render(request, 'SEI/permission.html')

    return render(request, 'SEI/employeeview.html')

@login_required
def search_project(request):
    #user_profile = get_object_or_404(Profile, user = request.user)
    #if user_profile.user_role == 'ITADMIN':
    #   return render(request, 'SEI/permission.html')
    context = {}
    context['report'] = ReportForm()
    print("here")
    return render(request, 'SEI/projectview.html', context)

@login_required
def get_team(request,team_name):
    teams=Team.objects.filter(team_name__contains=team_name)
    team_list = []
    for team in teams:
        team_list.append(model_to_dict(team))
    team_list_result = json.dumps(team_list, default=decimal_default)
    return HttpResponse(team_list_result, content_type="application/json")

@login_required
@permission_required('SEI.add_employee')
def bulk_upload(request,file_path="/Users/eccco_yao/Desktop/example.csv"):
    """
    bulk upload the employee information from csv file path
    csv file format:
    uid,first_name,last_name,position,title,internal_salary,external_salary,team_name
    :param request: Request
    :param file_path: csv path
    :return: message that indicats if it's successful or not, but how to return ???
    """
    failed_row = []
    created_row = 0
    updated_row = 0
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for index,row in enumerate(reader):
            if len(row) != 8:
                return "invalid csv format, should be 8 rows"
            if row[0]=='uid':
                pass
            else:
                employee_info = employee_validation(row)
                if employee_info:
                    response = update_or_create_employee(employee_info)
                    if response == 0:
                        failed_row.append(str(index+1))
                    elif response == 1:
                        created_row += 1
                    else:
                        updated_row += 1
                else:
                    failed_row.append(str(index+1))
    print ("successfully create: " + str(created_row) + " records, update: " + str(updated_row) + " records, the row index: " + ",".join(failed_row) + " failed.")

@permission_required('SEI.add_employee')
def update_salary_history(employee_uid, internal_salary, external_salary):
    employee = get_object_or_404(Employee,employee_uid=employee_uid)
    emp_salary_history = SalaryHistory.objects.filter(employee=employee)
    now_datetime = datetime.datetime.now()
    now_date = str(now_datetime.year) + '-' + str(now_datetime.month) + '-' + str(now_datetime.day)
    if not emp_salary_history:
        emp_salary_history = SalaryHistory.objects.create(employee=employee, internal_salary = internal_salary, external_salary = external_salary, effective_from = now_date)
        emp_salary_history.save()
    else:
        emp_salary_history_latest = emp_salary_history.latest()
        internal_recent = emp_salary_history_latest.internal_salary
        external_recent = emp_salary_history_latest.external_salary
        if internal_recent != internal_salary or external_recent != external_salary:
            emp_salary_history_latest.effective_until = now_date
            emp_salary_history_latest.save(update_fields=["effective_until"])
            new_salary = SalaryHistory.objects.create(employee=employee, internal_salary=internal_salary, external_salary=external_salary, effective_from=now_date)
            new_salary.save()



def employee_validation(row):
    """
    validate the employee row
    :param row: employee information
    :return: if correct, return a dictionary with employee information, if not, then return None
    validate: row[0] -- > uid, row[5] -- > internal salary, row[6] --> external salary, row[7] --> team name
    """
    employee_info = {}
    if row[0] == None or row[0] == '':
        return None
    employee_info['employee_uid'] = row[0]
    try:
        employee_info['internal_salary']=float(row[5])
        employee_info['external_salary']=float(row[6])
        employee_info['team'] = get_object_or_404(Team, team_name = row[7])
    except:
        return None
    if row[1] != None and row[1] != '':
        employee_info['first_name'] = row[1]
    if row[2] != None and row[2] != '':
        employee_info['last_name'] = row[2]
    if row[3] != None and row[3] != '':
        employee_info['title'] = row[3]
    if row[4] != None and row[4] != '':
        employee_info['position'] = row[4]
    return employee_info

@permission_required('SEI.add_employee')
def update_or_create_employee(employee):
    """
    update or create a new employee object and save
    :param employee: Employee dictionary
    :return: create: 1, update: 2, exception: 0
    """
    try:
        obj, created = Employee.objects.update_or_create(
            employee_uid=employee['employee_uid'],
            defaults=employee,
        )
        update_salary_history(employee['employee_uid'], employee['internal_salary'],
                              employee['external_salary'])

        if created:
            return 1
        else:return 2
    except:
        return 0


@login_required
def chart_team(request, team_id):
    """
    view the team budget and expense in a given year
    :param request: Request
    :param team_id: id for team object
    :param year: year requested
    :return: JSON format result
    """
    year = datetime.datetime.now().year
    team = get_object_or_404(Team,id=team_id)
    project_set = Project.objects.filter(team=team)

    context = {}

    resource_allocation = []
    for month in (1,2,3,4,5,6,7,8,9,10,11,12):
        date = datetime.date(year,month,1)
        monthly_cost = {}
        project_month_list = ProjectMonth.objects.filter(project__in=project_set, project_date = date)
        project_expense = ProjectExpense.objects.filter(project__in=project_set, project_date = date)
        employee_month = EmployeeMonth.objects.filter(project__in=project_set, project_date = date)

        # Get the Travel, Subcontractor, Equipment, Other cost in this month for this project
        travel_cost = 0
        subcontractor_cost = 0
        equipment_cost = 0
        other_cost = 0
        for pe in project_expense:
            if pe.category == "('T', 'Travel')":
                travel_cost += pe.cost
            if pe.category == "('S', 'Subcontractor')":
                subcontractor_cost += pe.cost
            if pe.category == "('E', 'Equipment')":
                equipment_cost += pe.cost
            if pe.category == "('O', 'Others')":
                other_cost += pe.cost

        monthly_cost["month"]=str(month)
        monthly_cost["travel"] = str(travel_cost)
        monthly_cost["subcontractor"] = str(subcontractor_cost)
        monthly_cost["equipment"] = str(equipment_cost)
        monthly_cost["other"] = str(other_cost)

        # Get the total Person cost in this month for this project
        person_cost = 0
        for em in employee_month:
            person_cost += em.month_cost

        monthly_cost["person"] = str(person_cost)


        month_budget = 0
        for pm in project_month_list:
            if pm.budget:
                month_budget += pm.budget
        monthly_cost["monthly_budget"] = str(month_budget)
        # Store all the 5 kinds of cost in JSON, the key is project_date

        resource_allocation.append(monthly_cost)

    context["resource_allocation"] = resource_allocation
    #pdb.set_trace()
    #context["resource_allocation"] = resource_allocation
    #print(context)
    return HttpResponse(json.dumps(context, default=decimal_default))

# @login_required
def report_project(request, PWP_num):
    context = {}
    messages = []
    context['messages'] = messages
    project_item = get_object_or_404(Project, PWP_num=PWP_num)

    form = ReportForm(request.POST)

    if not form.is_valid():
        messages.append("Form contained invalid data")
        render(request, "SEI/error.html", context)

    query_start_date = form.cleaned_data['query_start_date']
    query_end_date = form.cleaned_data['query_end_date']

    ##check date range
    # if query_start_date < project_item.start_date:
    #     query_start_date = project_item.start_date
    #     print(project_item.start_date)
    #     print(query_start_date)
    # if query_end_date > project_item.end_date:
    #     query_end_date = project_item.end_date
    #     print(project_item.end_date)
    #     print(query_end_date)
    print(query_start_date)
    print(query_end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ProjectReport.csv"'
    writer = csv.writer(response)
    ##Project Info
    writer.writerow([smart_str(u"Project Info"), smart_str(u"PWP_num"), smart_str(u"client name"), \
                     smart_str(u"business manager"), smart_str(u"is internal"), smart_str(u"start date"), \
                     smart_str(u"end date"), smart_str(u"project budget")])
    writer.writerow(['', smart_str(project_item.PWP_num), smart_str(project_item.client_name), \
                     smart_str(project_item.business_manager), smart_str(project_item.is_internal), \
                     smart_str(project_item.start_date), smart_str(project_item.end_date), \
                     smart_str(project_item.project_budget)])

    ##Employee Section
    writer.writerow([smart_str(u"Employee Section")])
    header_list = ['employee uid', 'first name', 'last name', 'position', 'title']
    subtractor_header_list = ['expense description']
    travel_header_list = ['expense description']
    equipment_header_list = ['expense description']
    others_header_list = ['expense description']

    project_start_year = query_start_date.year
    project_start_month = query_start_date.month
    project_end_year = query_end_date.year
    project_end_month = query_end_date.month

    length = 0
    if project_start_year == project_end_year:
        length = length + project_end_month - project_start_month + 1
        for i in range(0, project_end_month - project_start_month + 1):
            header = str(project_start_year) + "/" + str(project_start_month + i)
            header_list.append(header)
            subtractor_header_list.append(header)
            travel_header_list.append(header)
            equipment_header_list.append(header)
            others_header_list.append(header)
    else:
        length = length + 12 - project_start_month + 1
        length = length + (project_end_year - project_start_year - 1) * 12
        length = length + project_end_month + 1
        for i in range(0, 12 - project_start_month + 1):
            header = str(project_start_year) + "/" + str(project_start_month + i)
            header_list.append(header)
            subtractor_header_list.append(header)
            travel_header_list.append(header)
            equipment_header_list.append(header)
            others_header_list.append(header)
        for k in range(0, project_end_year - project_start_year - 1):
            for m in range(0, 12):
                year = project_start_year + k + 1
                header = str(year) + "/" + str(m + 1)
                header_list.append(header)
                subtractor_header_list.append(header)
                travel_header_list.append(header)
                equipment_header_list.append(header)
                others_header_list.append(header)
        for j in range(0, project_end_month + 1):
            header = str(project_end_year) + "/" + str(project_end_month + j)
            header_list.append(header)
            subtractor_header_list.append(header)
            travel_header_list.append(header)
            equipment_header_list.append(header)
            others_header_list.append(header)

    print(length)
    ##get all employees
    project_month = ProjectMonth.objects.filter(project=project_item).filter(project_date__gte=query_start_date).filter( \
        project_date__lte=query_end_date)
    list = Employee.objects.none()
    for pm in project_month:
        employee_list = pm.employee_list
        list = list | employee_list
    list = list.distinct()

    writer.writerow(header_list)

    ##create a set for each queried month
    date_range = []
    filtered_set = []
    date_range.append(query_start_date)
    if project_start_month < 12:
        next_date = date(project_start_year, project_start_month + 1, 1)
    else:
        next_date = date(project_start_year + 1, 1, 1)

    start_set = EmployeeMonth.objects.filter(project=project_item).filter(project_date__gte=query_start_date).filter(project_date__lt=next_date)

    filtered_set.append(start_set)
    if length > 2:
        for i in range(1, length - 1):
            date_range.append(next_date)
            temp = next_date + relativedelta(months=+1)
            temp_set = EmployeeMonth.objects.filter(project_date__gte=next_date).filter(project_date__lt=temp)
            filtered_set.append(temp_set)
            next_date = temp

    date_range.append(next_date)
    date_range.append(query_end_date)
    end_set = EmployeeMonth.objects.filter(project=project_item).filter(project_date__gte=next_date).filter(project_date__lt=query_end_date)
    filtered_set.append(end_set)

    print(date_range)
    print(filtered_set)
    total_FTE = [0] * length
    for employee_item in list:
        content = [employee_item.employee_uid, employee_item.first_name, employee_item.last_name, employee_item.position, employee_item.title]
        for i in range(0, length):
            employee_set = filtered_set[i] ## employeemonth set for this month
            try:
                employee_month = employee_set.get(employee=employee_item)
                total_FTE[i] = total_FTE[i] + employee_month.time_use
                content.append(str(employee_month.time_use))
            except:
                content.append('')
        writer.writerow(content)
    total_content = ['total in FTE', '', '', '', '']
    total_content.extend(total_FTE)
    writer.writerow(total_content)

    ##Subtractor Section
    writer.writerow([smart_str(u"Subtractor Section")])
    writer.writerow(subtractor_header_list)

    subtractor_content = []
    subtractor_total_set = ProjectExpense.objects.filter(project=project_item).filter(category='S').filter(project_date__gte=query_start_date).filter(project_date__lte=query_end_date)

    ## create monthly substractor_set
    subtractor_set = []
    index = 0

    for i in range(0, length):
        temp = subtractor_total_set.filter(project_date__gte=date_range[index], project_date__lt=date_range[index + 1])
        subtractor_set.append(temp)
        index = index + 1

    for subtractor_item in subtractor_total_set:
        subtractor_content.append(subtractor_item.expense_description)
        for i in range(0, length):
            subtractor_month_set = subtractor_set[i]
            if subtractor_item in subtractor_month_set:
                subtractor_content.append(str(subtractor_item.cost))
            else:
                subtractor_content.append('')
        writer.writerow(subtractor_content)

    ##Travel Section
    writer.writerow([smart_str(u"Travel Section")])
    writer.writerow(travel_header_list)

    travel_content = []
    travel_total_set = ProjectExpense.objects.filter(project=project_item).filter(category='T').filter(
        project_date__gte=query_start_date).filter(project_date__lte=query_end_date)

    ## create monthly substractor_set
    travel_set = []
    index = 0
    for i in range(0, length):
        temp = travel_total_set.filter(project_date__gte=date_range[index], project_date__lt=date_range[index + 1])
        travel_set.append(temp)
        index = index + 1

    for travel_item in travel_total_set:
        travel_content.append(travel_item.expense_description)
        for i in range(0, length):
            travel_month_set = travel_set[i]
            if travel_item in travel_month_set:
                travel_content.append(str(travel_item.cost))
            else:
                travel_content.append('')
        writer.writerow(travel_content)
    ## call functions to get the total amount
    writer.writerow(['total'])

    ##Equipment Section
    writer.writerow([smart_str(u"Equipment Section")])
    writer.writerow(equipment_header_list)

    equipment_content = []
    equipment_total_set = ProjectExpense.objects.filter(project=project_item).filter(category='E').filter(
        project_date__gte=query_start_date).filter(project_date__lte=query_end_date)

    ## create monthly substractor_set
    equipment_set = []
    index = 0
    for i in range(0, length):
        temp = equipment_total_set.filter(project_date__gte=date_range[index], project_date__lt=date_range[index + 1])
        equipment_set.append(temp)
        index = index + 1

    for equipment_item in equipment_total_set:
        equipment_content.append(equipment_item.expense_description)
        for i in range(0, length):
            equipment_month_set = equipment_set[i]
            if equipment_item in equipment_month_set:
                equipment_content.append(str(equipment_item.cost))
            else:
                equipment_content.append('')
        writer.writerow(equipment_content)
    ## call functions to get the total amount
    writer.writerow(['total'])

    ##Others Section
    writer.writerow([smart_str(u"Others Section")])
    writer.writerow(others_header_list)

    others_content = []
    others_total_set = ProjectExpense.objects.filter(project=project_item).filter(category='O').filter(
        project_date__gte=query_start_date).filter(project_date__lte=query_end_date)

    ## create monthly substractor_set
    others_set = []
    index = 0
    for i in range(0, length):
        temp = others_total_set.filter(project_date__gte=date_range[index], project_date__lt=date_range[index + 1])
        others_set.append(temp)
        index = index + 1

    for others_item in others_total_set:
        others_content.append(others_item.expense_description)
        for i in range(0, length):
            others_month_set = others_set[i]
            if others_item in others_month_set:
                others_content.append(str(others_item.cost))
            else:
                others_content.append('')
        writer.writerow(others_content)
    ## call functions to get the total amount
    writer.writerow(['total'])

    return response



