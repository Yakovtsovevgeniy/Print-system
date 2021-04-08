from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('user', views.UserModelView, basename='user')
router.register('plotter', views.PlotterModelView, basename='plotter')
router.register('pattern', views.PatternModelView, basename='pattern')
router.register('plotter_pattern', views.PlotterPatternModelView, basename='plotter_pattern')

urlpatterns = [
    path('', include((router.urls, 'api'))),
]
