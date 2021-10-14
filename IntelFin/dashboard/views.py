from django.shortcuts import render, redirect
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import json
from django.contrib.auth.decorators import login_required  

# Create your views here.
@login_required(login_url='login') 

# Create your views here.
def table(request):
    df = pd.read_csv("C:/Users/HP/Desktop/IntelFin/dashboard/Resources/DatasetDashboard.csv")
    NBClient=len(df['Entreprise'].unique())
    solvalble=df['y']
    nonsolavable=df['y']
    NBLigne = len(df)
    # parsing the DataFrame in json format.
    json_records = df.reset_index().to_json(orient ='records')
    dataset = []
    dataset = json.loads(json_records)
    #Bar chart
    k = json.loads(df[['Entreprise','Annee']].groupby(['Entreprise']).count().reset_index().to_json(orient ='records'))
    companies = []
    Nombre_Doc =[]
    for i in k:
        Nombre_Doc.append(i['Annee'])
        companies.append(i['Entreprise'])
    Nombre_Doc.append("")
    companies.append(0)
    labels = []
    data = []
    labels.append("Solvent ")
    x=round((df['y'].tolist().count(1)/NBLigne*100),2)
    y=round((df['y'].tolist().count(0)/NBLigne*100),2)
    data.append(x)
    labels.append("Insolvent ")
    data.append(y)
    
    context = {'d': dataset, 'labels': labels,
        'data': data, 'companies': companies, 'Nombre_Doc': Nombre_Doc, 
        'NBClient':NBClient,'x':x, 'y':y, 'NBLigne':NBLigne}

    return render(request, 'table.html', context)

@login_required(login_url='login')                       
def details(request, company):
    df = pd.read_csv("C:/Users/HP/Desktop/IntelFin/dashboard/Resources/DatasetDashboard.csv")
    #nom = format(company)
    Name=company
    data=df.loc[df['Entreprise'] == Name].sort_values(by=['Annee'])
    NBLigne = len(data)
    json_records = data.reset_index().to_json(orient ='records')
    dataset = []
    dataset = json.loads(json_records)
    Annee = []
    ChiffresAffaires = []
    for i in dataset:
        Annee.append(i['Annee'])
        ChiffresAffaires.append(i['Chiffre_Affaire'])

    #Ratio entabilité actif
    Rentability=[]
    polarChart=[]
    capb = 0
    for d in dataset:
        if d['TActif']!=0:
            Rentability.append(d['TPassif']/d['TActif'])
        FExploiation = d['FT_Exploitation']
        FFinancement = d['FT_Financement']
        FInvestissement = d['FT_Investisement']
        capb = d['CapBoursiere']


    polarChart.append(FExploiation)
    polarChart.append(FFinancement)
    polarChart.append(FInvestissement)


    context = {'d': dataset,'Name':Name,'Annee':Annee,'ChiffresAffaires': ChiffresAffaires,
    'NBLigne':NBLigne, 'Rentability':Rentability, 'polarChart':polarChart,
    'capb':capb, 'AnneePolarchart':Annee[-1]}


   # return HttpResponse(context)
    return render(request, 'dashboardDetails.html', context)
                      
