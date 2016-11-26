from django.conf.urls import url
import django.contrib.auth.views
import SEI.views

urlpatterns = [
    url(r'^$', SEI.views.home, name='home'),
    url(r'^login$', django.contrib.auth.views.login, {'template_name':'SEI/login.html'}, name='login'),
    url(r'^login2$', django.contrib.auth.views.login, {'template_name':'SEI/login2.html'}),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    url(r'^register$', SEI.views.register, name='register'),
    url(r'^profile/(?P<user_name>\w+)$', SEI.views.profile, name='profile'),
    url(r'^confirm-registeration/(?P<user_name>\w+)/(?P<token>[\w.-]+)$', SEI.views.confirm_register, name='confirm'),
    url(r'^edit_profile$', SEI.views.update_profile, name='edit'),
    url(r'^password_reset$', django.contrib.auth.views.password_reset, name='reset'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        django.contrib.auth.views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset_done$', django.contrib.auth.views.password_reset_done, name='password_reset_done'),
    url(r'^password_reset_complete$', django.contrib.auth.views.password_reset_complete, name='password_reset_complete'),
    url(r'^password_change', django.contrib.auth.views.password_change, {'post_change_redirect': '/'}, name='password_change'),
    url(r'^password_change_done', django.contrib.auth.views.password_change_done, name='password_change_done'),
    url(r'^add_project', SEI.views.add_project, name='addProject'),
    #url(r'^edit_project/(?P<PWP_num>\w+)$', SEI.views.edit_project, name='editProject'),
    url(r'^project/(?P<PWP_num>\w+', SEI.views.projectview, name='projectview'),
    url(r'^add_resources/(?P<PWP_num>\w+)$', SEI.views.add_resources, name='addResources'),
    url(r'^add_employee/(?P<employee_chosen>.*?)$', SEI.views.add_employee, name='addEmployee'),
    url(r'^view_employee_list/(?P<PWP_num>\d+)/(?P<project_date_year>\d+)/(?P<project_date_month>\d+)$', SEI.views.view_employee_list, name='viewEmployeeList'),
    url(r'^budget/(?P<PWP_num>\w+)$', SEI.views.budget_view, name='viewBudget'),
    url(r'^overview/(?P<PWP_num>\w+)$', SEI.views.project_overview, name='viewProject'),
    url(r'^view_team/(?P<team_id>\d+)$', SEI.views.team_view, name = 'viewTeam'),
]
