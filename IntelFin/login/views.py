from django.shortcuts import render,redirect 	
from django.http import HttpResponse
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import login, authenticate, logout
from .decorators import unauthenticated_user,allowed_users,admin_only
# Create your views here.
from django.contrib.auth.decorators import login_required
def index(response):
	return HttpResponse("<h1>hii</h1>")

@login_required(login_url='login')
@admin_only
def register(response):
	form=RegisterForm()
	if response.method == "POST" :
		form = RegisterForm(response.POST)
		if form.is_valid():
			user =form.save()
			username = form.cleaned_data.get('username')
			group = Group.objects.get(name='customer')
			user.groups.add(group)
			messages.success(response,'Account created for '+ username)
			return redirect("login")
		#redirect to another page after register
		
	else :
		form = RegisterForm()
	context={"form":form}
	return render(response,"login/register.html",context)
@unauthenticated_user
def loginPage(response):
	if response.method == 'POST':
		username=response.POST.get('username')
		password=response.POST.get('password')
		user = authenticate(response , username=username , password=password)
		if user is not None :
			login(response , user)
			return redirect('/extraction')
		else :
			messages.info(response,'Username or password incorrect')
	context= {}
	return render(response,"registration/login.html",context)

def logoutUser(request):
	logout(request)
	return redirect('login')