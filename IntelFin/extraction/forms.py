from django.forms import ModelForm
from .models import ExtraCol
from django import forms

class ExtraColForm(ModelForm):
	class Meta():
		model=ExtraCol
		fields=('turnover','market_capitalization')

		labels = {
			
			'turnover': '',
			'market_capitalization': '',
		}
		
		widgets = {
			'turnover': forms.TextInput(attrs={'class':'form-control','placeholder':'Turnover'}),
			'market_capitalization': forms.TextInput(attrs={'class':'form-control','placeholder':'Market Capitalization'}),
		}
			