from django.conf.urls import url

from . import views

app_name = 'core'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^process/$', views.process, name='process'),
    url(r'^download/$', views.download, name='download')
]
