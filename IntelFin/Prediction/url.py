from django.urls import path
from . import views

urlpatterns = [
    path('prediction',views.prediction,name='prediction')
]
