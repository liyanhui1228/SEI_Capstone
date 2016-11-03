from django.conf.urls import include, url
from SEI import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^register$',views.register),
    url(r'^login$',views.login)
]