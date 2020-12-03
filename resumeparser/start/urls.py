from django.conf.urls import url
from start import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'start'

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
