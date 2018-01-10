"""emstrack URL Configuration

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
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from login.viewsets import ProfileViewSet

from ambulances.viewsets import AmbulanceViewSet

from hospital.viewsets import HospitalViewSet, HospitalEquipmentViewSet

schema_view = get_swagger_view(title='EMSTrack API')

router = routers.DefaultRouter()

router.register(r'user',
                ProfileViewSet)

router.register(r'ambulance',
                AmbulanceViewSet,
                base_name='ambulance')

router.register(r'hospital',
                HospitalViewSet,
                base_name='hospital')
router.register(r'hospital/(?P<id>[0-9]+)/equipment',
                HospitalEquipmentViewSet)

urlpatterns = [

    # Router API urls
    url(r'^api/', include(router.urls)),
    url(r'^docs/', login_required(schema_view)),

    # ambulances
    url(r'^ambulances/', include('ambulances.urls')),

    # login
    url(r'^auth/', include('login.urls')),

    # admin
    url(r'^admin/', admin.site.urls),
    
    url(r'^$', RedirectView.as_view(url='http://cruzroja.ucsd.edu/wiki')),
    
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
