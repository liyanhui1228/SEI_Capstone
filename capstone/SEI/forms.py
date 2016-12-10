from django import forms
from django.contrib.auth.models import User
from SEI.models import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.humanize.templatetags.humanize import intcomma
from datetimewidget.widgets import DateTimeWidget
from django.forms import extras

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

class ProjectModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.team_name)

class ProjectForm(forms.ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'
    start_date = forms.DateField()
    end_date = forms.DateField()
    team = ProjectModelChoiceField(queryset=Team.objects.all())
    
    class Meta:
        model = Project
        fields = '__all__'

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

class ChargeStringForm(forms.ModelForm):
    class Meta:
        model = ChargeString
        fields = ['charge_string']

    def clean(self):
        cleaned_data = super(ChargeStringForm, self).clean()
        return cleaned_data

class ResourceForm(forms.ModelForm):
    month = forms.CharField(max_length=30)
    class Meta:
        model = ProjectExpense
        fields = '__all__'

    def clean(self):
        cleaned_data = super(ResourceForm, self).clean()
        return cleaned_data

class AddEmployeeForm(forms.Form):
    employee_name = forms.CharField(max_length=30)
    month = forms.CharField(max_length=30)
    is_internal = forms.BooleanField()

    def clean(self):
        cleaned_data = super(AddEmployeeForm, self).clean()
        return cleaned_data

class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)

class TeamForm(forms.ModelForm):
    manager = TeamModelChoiceField(queryset=Employee.objects.all(),widget=forms.Select(attrs={'class':'form-control'}))
    directorate = TeamModelChoiceField(queryset=Employee.objects.all(),widget=forms.Select(attrs={'class':'form-control'}))
    class Meta:
        model = Team
        fields = '__all__'
        widgets={
           'team_name' : forms.TextInput(attrs={'class':'form-control'}),
           'division' : forms.TextInput(attrs={'class':'form-control'})
        }

    def clean(self):
        cleaned_data = super(TeamForm, self).clean()
        return cleaned_data

class EmployeeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.team_name)

class EmployeeForm(forms.ModelForm):
    team = EmployeeModelChoiceField(queryset=Team.objects.all(),widget=forms.Select(attrs={'class':'form-control'}))
    
    class Meta:
        model = Employee
        exclude=('employee_uid',)
        widgets={
           'first_name' : forms.TextInput(attrs={'class':'form-control'}),
           'last_name' : forms.TextInput(attrs={'class':'form-control'}),
           'position':forms.TextInput(attrs={'class':'form-control'}),
           'title':forms.TextInput(attrs={'class':'form-control'}),
           'internal_salary':forms.NumberInput(attrs={'class':'form-control'}),
           'external_salary':forms.NumberInput(attrs={'class':'form-control'})
        }

    def clean(self):
        cleaned_data = super(EmployeeForm, self).clean()
        return cleaned_data

class ReportForm(forms.Form):
    query_start_date = forms.DateField(widget=extras.SelectDateWidget)
    query_end_date = forms.DateField(widget=extras.SelectDateWidget)

    # class Meta:
    # #     # dateTimeOptions = {
    # #     # 'format': 'dd/mm/yyyy HH:ii P',
    # #     # 'autoclose': True,
    #     # 'startView': 3
    #     # }
    #     widgets={
    #         'query_start_date': SelectDateWidget(empty_label="Nothing"),
    #         'query_end_date': SelectDateWidget(empty_label="Nothing")
    #     }

    def clean(self):
        cleaned_data = super(ReportForm, self).clean()
        return cleaned_data

class ProjectExpenseForm(forms.ModelForm):
    class Meta:
        model = ProjectExpense
        fields = ('category', 'cost', 'expense_description')
        widgets = {
            'expense_description': forms.Textarea(attrs={'rows': 1}),
         }

    def clean(self):
        cleaned_data = super(ProjectExpenseForm, self).clean()
        return cleaned_data

class EmployeeMonthModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)

class EmployeeMonthForm(forms.ModelForm):
    internal_salary = forms.CharField(label='Internal Salary',disabled=True)
    external_salary = forms.CharField(label='External Salary',disabled=True)
    employee_name = forms.CharField(label='Name',disabled=True)

    class Meta:
        model = EmployeeMonth
        fields = ('employee','time_use', 'isExternal')

    def clean(self):
        cleaned_data = super(EmployeeMonthForm, self).clean()
        return cleaned_data

class ProjectMonthForm(forms.ModelForm):
    class Meta:
        model = ProjectMonth
        fields = ('project_date', 'project')

    def clean(self):
        cleaned_data = super(ProjectMonthForm, self).clean()
        return cleaned_data
