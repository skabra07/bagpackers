"""oxfordhack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from backpackers import views

urlpatterns = [
    url(r'', include('backpackers.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^search/', views.search, name='search'),
    url(r'^flight/', views.flight, name='flight'),
    url(r'^flight/search/', views.flightSearch, name='flightSearch'),
    url(r'^hotel/', views.hotel, name='hotel'),
    url(r'^hotel/search/', views.hotelSearch, name='hotelSearch'),
    url(r'$', views.index, name='index'),

]
