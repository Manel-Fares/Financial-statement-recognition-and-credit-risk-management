
from django.contrib import admin
from django.urls import path,include
from login import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('', include('extraction.urls')),
    path('', include('dashboard.urls')),
    path('login/', v.loginPage,name="login"),
    path('logout/', v.logoutUser, name="logout"),
    path('register/',v.register, name="register"),
    path('', v.index , name="home")
]
