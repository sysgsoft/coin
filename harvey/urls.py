"""harvey URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.contrib import admin
#from django.urls import reverse
from django.conf.urls import url,include
from rest_framework import routers
from django.urls import NoReverseMatch
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from api.views import TestAPI
from django.views.generic import TemplateView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'Score', TestAPI, 'TestAPI')


urlpatterns = [
    #url(r'^$', TemplateView.as_view(template_name='sample/index.html')),
    #url(r'^$', views.index, name='index'),
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    #url(r'^employees/', views.employeeList.as_view()),
    
]