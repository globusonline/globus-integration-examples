from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'', include('django.contrib.auth.urls')),
    url(r'', include('social_django.urls', namespace='social')),
]
