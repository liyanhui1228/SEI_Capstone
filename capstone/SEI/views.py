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

from SEI.models import *
from SEI.forms import *

@login_required
def home(request):
    return render(request,'SEI/home.html', {})

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

@login_required
@transaction.atomic
def update_profile(request):
    context = {}
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
                    password=form.cleaned_data['password1'],\
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
        if user_profile.activation_key == token:
            user_item.is_active = True
            user_item.save()
            # Logs in the new user and redirects to his/her Employee page
            new_user = authenticate(username=user_item.username, \
                            password=user_item.password)
            login(request, new_user)
        return redirect('home')
    except:
        return redirect('home')




