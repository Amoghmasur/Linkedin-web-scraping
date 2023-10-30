from django.contrib import admin
from django.urls import path
from Linkapp import views

urlpatterns = [
    path('home', views.dashboard),
    path('comp', views.dashboard1),
    path('scrape',views.scrape),
    path('login',views.user_login),
    path('register',views.register),
    path('logout',views.user_logout),
    path('',views.user_login),
    path('company',views.companysearch),
    path('search',views.searchcomp)
]
