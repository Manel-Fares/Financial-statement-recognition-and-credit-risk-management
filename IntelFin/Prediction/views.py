from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler, StandardScaler
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.svm import SVC 

# Create your views here.
def prediction(request):

	modeling_Dataset= pd.read_csv("C:/Users/HP/Desktop/IntelFin/Prediction/Resources/modelingDataset.csv")

	y = modeling_Dataset.iloc[:,19]
	X = modeling_Dataset.iloc[:,0:19]
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42,stratify=y)

	features =  ['TCPP', 'CapitalPropre', 'PassifNonC', 'TActif',
       'TPassif', 'PassifCourant', 'ActifNonC', 'ActifCourant', 'Reserves',
       'CapitalSociale', 'TProdExploitation', 'TChargeExploitation',
       'R_Exploitation', 'Res_Exsercice', 'ActiviteOrdinaire', 'Dotation','TDebut','TFin', 'Variation']

	scaler=StandardScaler()
	X_train[features]=scaler.fit_transform(X_train[features])
	X_test[features]=scaler.transform(X_test[features])

	X_train_svm,y_train_svm,X_test_svm,y_test_svm = X_train.copy(),y_train.copy(),X_test.copy(),y_test.copy()

	svm =SVC(C= 1000, gamma= 0.1, kernel= 'rbf')
	svm.fit(X_test_svm, y_test_svm)

	#Entreprise Solvable
	pred1=svm.predict([[-0.126510,0.103500,-0.146528,-0.126510,-0.109804,-0.111210,-0.142509,-0.123526,-0.208551,-0.110742,-0.281978,.110213,-0.203270,0.092419,0.092016,0.026089,0.102752,0.102535,0.096479]])
	#Entreprise Non Solvable
	pred2=svm.predict([[-0.127412,0.101705,-0.146747,-0.127412,-0.108689,-0.108729,-0.191813,-0.115689,0.112079,-0.130034,-0.298298,0.104695,-0.288728,0.055182,0.054716,0.409008,0.099889,0.095522,-0.040609]])
	#Entreprise Solvable
	pred3=svm.predict([[-0.128266,0.102756,-0.146838,-0.128266,-0.109691,-0.110629,-0.179553,-0.118909,-0.123488,-0.115740,-0.293070,0.106816,-0.122318,0.103683,0.105950,-0.251209,0.106719,0.106595,0.103424]])

	#Test1
	ResultatPrediction1="test with value"
	if pred1==1:
		ResultatPrediction1="Entreprise solvable"
	else:
		ResultatPrediction1="Entreprise non solvable"


	#Test2
	ResultatPrediction2="test with value"
	if pred3==1:
		ResultatPrediction2="Entreprise solvable"
	else:
		ResultatPrediction2="Entreprise non solvable"

	Affichage='Test1: ',ResultatPrediction1,'  ____________  ','Test2: ',ResultatPrediction2
	return HttpResponse(Affichage)

