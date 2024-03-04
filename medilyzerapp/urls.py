from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home_view, name="home"),
    path('index', views.index, name = 'index'),
    path('about', views.about, name = 'about'),
    path('convert', views.convert, name = 'convert'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)