from django import forms
from django.contrib.auth.models import User
from SEI.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.humanize.templatetags.humanize import intcomma

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    user_name = forms.CharField(max_length=40)
    email = forms.EmailField(max_length=40, label="Email", widget=forms.EmailInput())
    password1 = forms.CharField(max_length=40, label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=40, label="Comfirm Password", widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')
        if User.objects.filter(username__exact=user_name):
            raise forms.ValidationError("User name has already taken")
        return user_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except:
            raise forms.ValidationError("Email format is not valid")
        return email

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        return cleaned_data

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ('user', 'activation_key',)

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        return cleaned_data

class ProjectForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    start_date = forms.DateField()
    end_date = forms.DateField()

    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            #'start_date': forms.SelectDateWidget(),
            #'end_date': forms.SelectDateWidget(),
            'project_budget': forms.NumberInput(attrs={'min': 0, 'step':1000}),
         }

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        return cleaned_data

    def clean_PWP_num(self):
        PWP_num = self.cleaned_data.get('PWP_num')
        if Project.objects.filter(PWP_num__exact=PWP_num):
            raise forms.ValidationError("Project PWP_num has already taken")
        return PWP_num

    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if end_date < start_date:
            raise forms.ValidationError("End date must occur after start date")
        return end_date

