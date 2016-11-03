from django.conf.urls import include, url
import django.contrib.auth.views
import SEI.views

urlpatterns = [
    url(r'^$', SEI.views.home, name='home'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', django.contrib.auth.views.login, {'template_name':'SEI/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', django.contrib.auth.views.logout_then_login, name='logout'),
    #url(r'^register$', SEI.views.register, name='register'),
]