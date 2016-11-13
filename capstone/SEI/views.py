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

from SEI.models import *
from SEI.forms import *


@login_required
def home(request):
    return render(request, 'SEI/home.html', {})


@login_required
def projectview(request, PWP_num):
    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    context['project'] = project_item
    return render(request, 'SEI/projectview.html', context)


@login_required
@transaction.atomic
def add_project(request):
    context = {}

    employee_item = get_object_or_404(Employee, user=request.user)
    if employee_item.user_role == 'NM':
        return render(request, 'SEI/permission.html', context)

    form = ProjectForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'SEI/project.html', context)

    new_project = Project(PWP_num=form.cleaned_data['PWP_num'], \
                          project_description=form.cleaned_data['project_description'], \
                          project_budget=form.cleaned_data['project_budget'], \
                          is_internal=form.cleaned_data['is_internal'], \
                          start_date=form.cleaned_data['start_date'], \
                          end_date=form.cleaned_data['end_date'])
    new_project.save()
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

    user_profile = Employee(user=new_user, activation_key=token)
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
        user_profile = Employee.objects.get(user=user_item)
        print(user_profile.activation_key)
        print(token)
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
    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    charge_string = get_object_or_404(ChargeString, project=project_item)
    context['PWP_num'] = project_item.PWP_num
    context['project_description'] = project_item.project_description
    context['project_budget'] = project_item.project_budget
    context['isExternal'] = project_item.isExternal
    context['team_name'] = project_item.team.team_name
    context['organization_name'] = project_item.client.organization_name
    context['start_date'] = project_item.start_date
    context['end_date'] = project_item.end_date
    context['charge_string'] = charge_string
    return HttpResponse(json.dumps(context), content_type="application/json")


@login_required
def budget_view(request, PWP_num):
    now = datetime.datetime.now()
    context = {}
    project_item = get_object_or_404(Project, PWP_num=PWP_num)
    project_month = get_object_or_404(ProjectMonth, project=project_item)
    context['total_budget'] = project_item.project_budget
    total_expense = 0
    total_expense_till_now = 0
    monthly_expense = {}

    for single_project_month in project_month:
        budget_detail = {}
        budget_detail['year'] = single_project_month.year
        budget_detail['month'] = single_project_month.month
        budget_detail['budget'] = single_project_month.budget
        project_month_expense = get_object_or_404(ProjectExpense, project_month=single_project_month)
        month_total_expense = 0
        for month_expense_detail in project_month_expense:
            month_total_expense += month_expense_detail.cost
            total_expense += month_expense_detail.cost
            if single_project_month.year < now.year or \
                    (single_project_month.year == now.year and single_project_month.month <= now.month):
                total_expense_till_now += month_expense_detail.cost
        budget_detail['expense'] = month_total_expense
        monthly_expense[str(single_project_month.year) + '.' + str(single_project_month.month)] = budget_detail

    context['monthly_expense'] = monthly_expense
    context['budget_balance'] = context['total_budget'] - total_expense_till_now
    context['projected_expense'] = total_expense - total_expense_till_now
    context['projected_remain'] = context['total_budget'] - total_expense
    return HttpResponse(json.dumps(context), content_type="application/json")
