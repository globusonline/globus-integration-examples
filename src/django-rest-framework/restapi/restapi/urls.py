from django.conf.urls import url, include
from restapi import views


urlpatterns = [
    url(r'^endpoint/', views.EndpointAPIView.as_view()),
]
