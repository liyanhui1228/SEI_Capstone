from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
import json
import datetime
import decimal

from SEI.models import *
from SEI.forms import *

from SEI.models import ProjectMonth
from django.forms.formsets import formset_factory

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

    return render(request, 'SEI/home.html', {})


@login_required
def projectview(request, PWP_num):
    #if no project passed in, show search bar only
    if PWP_num == '':
        return render(request, 'SEI/projectview.html')

    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    context['project'] = project_item
    return render(request, 'SEI/projectview.html', context)


@login_required
@transaction.atomic
def add_project(request):
    context = {}

    profile_item = get_object_or_404(Profile, user=request.user)
    #TO DO uncomment once user admin is working
    #if profile_item.user_role == 'NM':
    #    return render(request, 'SEI/permission.html', context)

    ChargeStringFormSet = formset_factory(ChargeStringForm)
    if request.method == "GET":
        form = ProjectForm()
        formset = ChargeStringFormSet()
        context['form'] = form
        context['chargestring_formset'] = formset
        return render(request, 'SEI/project.html', context)
    ##should pass in team and client or select??
    #new_project = Project(team=team, client=client)
    #form = ProjectForm(request.POST, instance=new_project)
    form = ProjectForm(request.POST)
    formset = ChargeStringFormSet(data=request.POST)

    if not form.is_valid():
        return render(request, 'SEI/project.html', context)

    new_project = form.save()

    #save charge strings
    #project_id = new_project.id
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
def edit_project(request, PWP_num):
    context = {}

    employee_item = get_object_or_404(Employee, user=request.user)
    if employee_item.user_role == 'NM':
        return render(request, 'SEI/permission.html', context)

    try:
        project_item = Project.objects.get(PWP_num=PWP_num)
    except:
        project_item = Project(PWP_num=PWP_num)
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, instance=project_item)
        context['form'] = profile_form
        if project_form.is_valid():
            project_form.save()
            return redirect('projectview', PWP_num=PWP_num)
        else:
            return render(request, 'SEI/edit_project.html', context)
    else:
        project_form = ProjectForm(instance=project_item)
        return render(request, 'SEI/edit_project.html', {
            'form': project_form
        })

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
    context['team_name'] = project_item.team.team_name
    context['organization_name'] = project_item.client.organization_name
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
        if now.date() > pm.project_date:
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
def add_employee(request, employee_chosen):
    employee_chosen_json = json.loads(employee_chosen)
    context = {}
    alert = {}
    detail = {} # The alert details
    PWP_num = employee_chosen_json['PWP_num']
    emp_chosen_list = employee_chosen_json['emp_chosen_list']
    project_date = employee_chosen_json['project_date']

    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    project_month = ProjectMonth.objects.filter(project=project_item, project_date=project_date)

    # The key of emp_chosen_list is the employee id
    for ec in emp_chosen_list:
        emp_id = ec
        emp_detail = emp_chosen_list[ec]
        time_to_use = emp_detail['time_to_use']
        is_external = emp_detail['is_external']
        month_cost = emp_detail['month_cost']
        emp = Employee.objects.filter(id=ec)
        
        # Update the project_spending in Project
        project_item.project_spending += month_cost
        project_item.save(update_fields=["project_spending"])

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
    return render(request, "SEI/add_employee_alert.json", context)

@login_required
def add_resources(request, PWP_num):
    context = {}
    messages = []
    context['messages'] = messages
    project_item = get_object_or_404(Project, PWP_num = PWP_num)
    if request.method == 'GET':
        form = ResourceForm()
        context['form'] = form
        return render(request, 'SEI/resource.html', context)

    form = ResourceForm(request.POST)
    if not form.is_valid():
        messages.append("Form contains invalid data")
        return render(request, 'SEI/resource.html', context)

    context['form'] = form
    month = form.cleaned_data['month']
    project_month_item = get_object_or_404(ProjectMonth, project=project_item, month=month)
    new_project_expense = ProjectExpense(project_month = project_month_item,
                                         cost=form.cleaned_data['cost'],
                                         expense_description=form.cleaned_data['expense_description'],
                                         category=form.cleaned_data['category'])
    new_project_expense.save()
    project_month_item.add(new_project_expense)
    project_month_item.save()
    messages.append("Expense has been saved")
    return render(request, 'SEI/resource.html', context)

@login_required
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
def add_team(request):
    user_profile = get_object_or_404(Profile, user = request.user)
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

##@login_required
def view_team(request, team_id):
    user_profile = get_object_or_404(Profile, user = request.user)
    context = {}
    if user_profile.user_role == 'ITADMIN':
        return render(request, 'SEI/permission.html', context)

    team = get_object_or_404(Team, team_id = team_id)

    project_set = Project.objects.filter(team = team)
    employee_set = Employee.objects.filter(team = team)

    ##show team info
    context['team'] = team

    ##show project
    context['projects'] = project_set

    ##show employee
    context['employees'] = employee_set

    return render(request, 'SEI/teamview.html', context)
