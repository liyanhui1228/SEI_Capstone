from django.shortcuts import render
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from SEI.models import *


@login_required
def home(request):
    return render(request,'home.html',{'user_firstname':request.user.firstName})


def register(request):
    if request.method=='GET':
        return render(request,'registration.html',{})


    firstName=request.POST['firstname']
    lastName=request.POST['lastname']
    userName=request.POST['username']
    email=request.POST['email']
    role=request.POST['role']
    password=request.POST['password']

    user=User(firstName=firstName,lastName=lastName,email=email,role=role,password=password,username=userName)
    user.save()
    
    user=authenticate(username=userName,password=password)
    login(request,user)

    return redirect(reverse('home'))



