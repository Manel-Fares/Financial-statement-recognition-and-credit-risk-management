from django.urls import path
from . import views

urlpatterns = [
    path('table', views.table, name ="table"),
    path('details/<company>/',views.details, name="details")
    
    


]
