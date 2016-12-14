from django.conf.urls import url
import django.contrib.auth.views
import SEI.views

urlpatterns = [
    #System
    url(r'^$', SEI.views.home, name='home'),
    url(r'^login$', django.contrib.auth.views.login, {'template_name':'SEI/login.html'}, name='login'),
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    
    #Project View
    url(r'^add_project', SEI.views.add_project, name='addProject'),
    url(r'^project/(?P<PWP_num>\w+)$', SEI.views.projectview, name='projectview'),
    url(r'^edit_project/(?P<PWP_num>\w+)$', SEI.views.edit_project, name='edit_project'),
    url(r'^project', SEI.views.search_project, name='projectsearch'),
    url(r'^budget/(?P<PWP_num>\w+)$', SEI.views.budget_view, name='viewBudget'),
    url(r'^overview/(?P<PWP_num>\w+)$', SEI.views.project_overview, name='viewProject'),
    url(r'^resource/(?P<PWP_num>\w+)$', SEI.views.project_resource, name='viewProjectResource'),
    url(r'^report_project/(?P<PWP_num>.*)$', SEI.views.report_project, name="reportProject"),
    
    #Admin View
    url(r'^add_resources/(?P<PWP_num>\w+)/(?P<project_year>\d+)/(?P<project_month>\d+)$', SEI.views.add_resources, name='addResources'),
    url(r'^add_employee/(?P<employee_chosen>.*?)$', SEI.views.add_employee, name='addEmployee'),
    url(r'^edit_employee/(?P<employee_id>\d+?)$', SEI.views.edit_employee, name='edit_employee'),
    url(r'^admin_team$', SEI.views.admin_team, name='adminTeam'),
    url(r'^edit_team/(?P<team_id>\d+)$', SEI.views.edit_team, name='edit_team'),
    url(r'^admin_employee$', SEI.views.admin_employee, name='adminEmployee'),
    url(r'^bulk_upload$',SEI.views.bulk_upload,name="bulkUpload"),
    
    #Employee view
    url(r'^get_employee/(?P<first_name>.*?)/(?P<last_name>.*?)$',SEI.views.get_employee),
    url(r'^get_employee_project/(?P<employee_id>\d+)$',SEI.views.get_employee_project),
    url(r'^employee/(?P<employee_id>\w+)$', SEI.views.employeeview, name='employeeview'),
    url(r'^employee$', SEI.views.search_employee, name='employeesearch'),
    url(r'^report_employee/(?P<employee_id>\w+)$', SEI.views.report_employee, name='reportEmployee'),
    
    #Team View
    url(r'^team/(?P<team_id>\d+)$', SEI.views.view_team, name='teamview'),
    url(r'^team', SEI.views.search_team, name='teamsearch'),
    url(r'^get_team/(?P<team_name>\w*)$',SEI.views.get_team),
    url(r'^get_employee_allocation/(?P<employee_id>\d+)/(?P<year>\d+)$',SEI.views.get_employee_allocation),
    url(r'^chart_team/(?P<team_id>\d+)$',SEI.views.chart_team, name="chart_team"),
    url(r'^report_team/(?P<team_id>\d*)$', SEI.views.report_team, name='reportTeam'),
    
]