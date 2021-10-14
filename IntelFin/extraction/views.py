from django.shortcuts import render
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler, StandardScaler
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.svm import SVC 
from pymongo import MongoClient
import gridfs
import base64
from pathlib import Path
import re
import json
import parse
import pdfplumber
import pandas as pd
from collections import namedtuple
from PyPDF2 import PdfFileWriter, PdfFileReader
import textwrap
import os
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required


from .forms import ExtraColForm
from django.http import HttpResponseRedirect
from pandas import DataFrame
from collections import namedtuple
@login_required(login_url='login')
def pdf(request):
    try:
        return FileResponse(open('<file name with path>', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404('not found')
@login_required(login_url='login')
def page2(request):
    return render(request,'frontend/extraction/page2.html')
@login_required(login_url='login')
def page3(request):
    context = {'d': request.session.get("filename","null")} 
    return render(request,'frontend/extraction/page3.html',context)
@login_required(login_url='login')
def page1(request):
    return render(request,'frontend/extraction/page1.html')

# Create your views here.
rmSp = re.compile(r'^\s+',re.MULTILINE)
def Pages_To_Keep(filename,dictionnaire,newpath):
    output = PdfFileWriter()
    lines = []
    pagesIndex = []
    i=0
    with pdfplumber.open('media/'+filename) as pdf:
        pages = pdf.pages
        for page in pdf.pages:
            text = page.extract_text()
            if(text is not None) and (i<23):
                for line in text.split('\n'):
                    if rmSp.match(line):
                        line=textwrap.dedent(line)
                    if line.lower().startswith('etat  de résultat technique de') or line.startswith('Conclusion') or line.startswith('Note') or line.startswith('NOTES') or line.startswith('NOTE') or line.upper().startswith('ETAT DE RÉSULTAT TECHNIQUE') or line.lower().startswith('pages') or line.startswith('AC11') or line.startswith('BILAN - ACTIF ') or line.startswith('BILAN – CAPITAUX') or line.lower().startswith('sommaire') or line.lower().startswith('table des ') or line.startswith('Rapport des commissaires aux comptes') or line.startswith('R3- VARIATIONS DES STOCKS') or line.startswith('Soldes Intermédiaires de Gestion') or line.startswith('I N D E X') or line.startswith('SCHEMA DES SOLDES') or line.startswith('Bilan - actifs :') or line.startswith('Rubrique') or line.startswith('Les reclassements suivants') or line.startswith('F- NOTES RELATIVES') or line.startswith('AC71 Avoirs en banque, CCP et Caisse :') or line.startswith('S O M M A I R E') or line.find('NOTES RELATIVES AU BILAN')!= -1 or line.startswith('P L A N') or line.startswith('F1- Amortissements et provisions') or line.startswith('F10- Encaissements provenant des') or line.lower().startswith('etat de resultat technique ') or line.lower().startswith('3-3-5-') or line.lower().startswith('5.3') or line.startswith('II-') :
                        break
                    if (line.startswith(tuple(dictionnaire)) and (i not in pagesIndex)):
                        pagesIndex.append(i)               
                        break
                i=i+1
        #f = open(file, "rb") 
        infile = PdfFileReader('media/'+filename, 'rb')

        for i in pagesIndex:
            p = infile.getPage(i)
            output.addPage(p)

        with open(newpath+filename, 'wb') as f:
            output.write(f)



@login_required(login_url='login')
def func_page_to_keep(request):
    context = {'d': request.session.get("filename","null")}
    #list = os.listdir('media/')
    list=[request.session.get("filename","null")]
    with open ("dictionnaire.txt", "r",encoding='utf-8') as f:
        data=f.read()
        dictionnaire=data.split('\n')
    newpath ="shortPDF/"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    for l in list:    
        Pages_To_Keep(l,dictionnaire,newpath)
    return render(request,'frontend/extraction/page3.html',context)










@login_required(login_url='login')
def extractionpage(request):
    path="C:/Users/HP/Desktop/IntelFin/"
    df = pd.read_csv(path+"django.csv",sep=",")
    print(df)
    json_records = df.reset_index().to_json(orient ='records',default_handler=str)
    #arr = JSON.parse(JSON.stringify(arr).replace(/\s(?=\w+":)/g, ""))
    data=[]
    data = json.loads(json_records)
    print(data)
    context = {'d': data} 
    return render (request,'frontend/extraction/page4.html',context)


def save_in_MongoDB(path):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['IntelFin_db'] 
    fs = gridfs.GridFS(db)
    # Note, open with the "rb" flag for "read bytes"
    with open(path, "rb") as f:
        encoded_string = base64.b64encode(f.read())
    with fs.new_file(
        chunkSize=800000,
        filename=path) as fp:
        fp.write(encoded_string)


@login_required(login_url='login')
def upload(request):
    if request.method == 'POST' and request.FILES['file']!=None:
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)
        request.session['filename'] = myfile.name
        print(request.session.get("filename","null"))
    return render(request, 'frontend/extraction/page2.html')


        
class Home(TemplateView):
    template_name = 'index.html'


def read_from_MongoDB(filename):
    # Usual setup
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['IntelFin_db'] 
    fs = gridfs.GridFS(db)
    # Standard query to Mongo
    data = fs.find_one(filter=dict(filename=filename))
    with open(filename, "wb") as f:
        f.write(base64.b64decode(data.read()))

def extract_value2(str):
    fin=str.rfind('  ',0,len(str)-4)
    debut=str.rfind('  ',0,fin-2)
    
    ch=str[debut+2:fin].replace('  ',' ')
    verif=re.compile(r'(([\(]?[a-z,A-Z, ,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?)|([\(]?[-][a-z,A-Z,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?))*(.*)')
    valeur=verif.search(ch).group(4)
    if(debut==-1 and fin==-1 and valeur!='' ):
        valeur=get_val(str)
        if(valeur=="0"):
            return valeur
        #verifier si la premiere année commence par le parenthése
        prenthese=re.compile(r'(^[\(][0-9, ]+[\)])(.*)')
        #vérifier si l'année précedente avec parenthese
        prenthese2=re.compile(r'(.*)([\(][0-9, ]+[\)])(.*)')
        #méme que les parentheses mais avec <>
        prenthese3=re.compile(r'(^[<][0-9, ]+[>])(.*)')
        prenthese4=re.compile(r'(.*)([<][0-9, ]+[>])(.*)')
        if(prenthese.search(valeur)):
            val=prenthese.search(valeur).group(1)
        elif(prenthese2.search(valeur)):
            val=prenthese2.search(valeur).group(1)
        elif(prenthese3.search(valeur)):
            val=prenthese3.search(valeur).group(1)
        elif(prenthese4.search(valeur)):
            val=prenthese4.search(valeur).group(1)
    
        
        else:
            #longueur de la valeur de l'année précedente n'est pas multiple de 3
            extrait=re.compile(r'(.+) [-]?([1-9]|[1-9][0-9]) (.+)')
            if(extrait.search(valeur)):
                val=extrait.search(valeur).group(1)
            else:
                if valeur[0]==' ' :
                    valeur=valeur[1:len(valeur)]
                print("erreur:", valeur)
                while valeur[len(valeur)-1]==' ':
                    valeur=valeur[0:len(valeur)-1]
                if(re.compile(r'(^[-]?[1-9][0-9][0-9] )(.+)').search(valeur)):
                    print("val23:",valeur)
                    c=int(valeur.count(' ')  // 2)
                    fin=(3*(c+1))+c
                    val=valeur[0:fin+1]
                    print("val erreur:",val)
                else :
                    print("ici")
                    extrait=re.compile(r'([1-9] |[1-9][0-9] )(.+)')
                    extract=extrait.search(valeur).group(2)
                    c=int(extract.count(' ')  // 2)
                    fin=(3*(c+1))+c

                    chaine=extract[0:fin+1]
                    val=extrait.search(valeur).group(1)+chaine
        ch=val
    return ch


def get_val(valeur):
    #verifier d'abord si la valeur est égale à 0
    verif3=re.compile(r'(--)|(-\((.*)\))')
    #verifier les formes particuliéres
    verif=re.compile(r'(([\(]?(([a-z,A-Z][.,-]?[1-9][1-9]?)|[1-9][.,-][0-9])[\)]?)|[\(][0-9][0-9]?[\)])(.*)')
    #verifier s'il existe un ou 2 entiers avant le signe -
    verif2=re.compile(r'( [1-9][0-9]?) (-[ ]?(.*))')
    if(verif3.search(valeur)):
        valeur="0"
    elif(verif.search(valeur)):
        valeur=verif.search(valeur).group(5)
    elif(verif2.search(valeur)):
        valeur=verif2.search(valeur).group(2)
    else:
        verif=re.compile(r'(([\(]?[a-z,A-Z, ,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?)|([\(]?[-][a-z,A-Z,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?))*(.*)')
        valeur=verif.search(valeur).group(4)
        verif=re.compile(r'^([1-9][1-9]|[1-9]) ([\(][0-9, ]+[\)](.*))')
        verif2=re.compile(r'^([1-9][1-9]|[1-9]) ([<][0-9, ]+[>](.*))')
        if(verif.search(valeur)):
            valeur=verif.search(valeur).group(2)
        elif(verif2.search(valeur)):
            valeur=verif2.search(valeur).group(2)
        else:
            verif=re.compile(r'^([1-9][1-9]|[-]?[1-9]) ([-]?([1-9][1-9]|[1-9]) (.*))')
            if(verif.search(valeur)):
                valeur=verif.search(valeur).group(2)
            else:
                verif=re.compile(r'(([\(]?[a-z,A-Z, ,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?)|([\(]?[-][a-z,A-Z,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?))*(.*)')
                valeur=verif.search(valeur).group(4)
                
    return valeur
def no_double_espace(valeur):
    
    if(valeur=="0"):
        return valeur
    #verifier si la premiere année commence par le parenthése
    prenthese=re.compile(r'(^[\(][0-9, ]+[\)])(.*)')
    #vérifier si l'année précedente avec parenthese
    prenthese2=re.compile(r'(.*)([\(][0-9, ]+[\)])(.*)')
    #méme que les parentheses mais avec <>
    prenthese3=re.compile(r'(^[<][0-9, ]+[>])(.*)')
    prenthese4=re.compile(r'(.*)([<][0-9, ]+[>])(.*)')
    if(prenthese.search(valeur)):
        val=prenthese.search(valeur).group(1)
    elif(prenthese2.search(valeur)):
        val=prenthese2.search(valeur).group(1)
    elif(prenthese3.search(valeur)):
        val=prenthese3.search(valeur).group(1)
    elif(prenthese4.search(valeur)):
        val=prenthese4.search(valeur).group(1)
    

    else:
        #longueur de la valeur de l'année précedente n'est pas multiple de 3
        extrait=re.compile(r'(.+) [-]?([1-9]|[1-9][0-9]) (.+)')
        if(extrait.search(valeur)):
            val=extrait.search(valeur).group(1)
        else:
            if valeur[0]==' ' :
                valeur=valeur[1:len(valeur)]
            while valeur[len(valeur)-1]==' ':
                valeur=valeur[0:len(valeur)-1]
            if(re.compile(r'(^[-]?[1-9][0-9][0-9] )(.+)').search(valeur)):
                c=int(valeur.count(' ')  // 2)
                fin=(3*(c+1))+c
                val=valeur[0:fin+1]
            else :
                extrait=re.compile(r'([1-9] |[1-9][0-9] )(.+)')
                extract=extrait.search(valeur).group(2)
                c=int(extract.count(' ')  // 2)
                fin=(3*(c+1))+c

                chaine=extract[0:fin+1]

                val=extrait.search(valeur).group(1)+chaine
    return val;
  
def extract_value(ch):
    print("input:",ch)
    while(ch.rfind('   ')!=-1):
        ch=ch.replace('   ','  ')
    vir=ch.count(',')

    ch=ch.replace(',', ' ')
    while(ch.rfind('- ')!=-1):
        ch=ch.replace('- ','-')
    
    #Eliminer tous les caractéres
    verif=re.compile(r'(([\(]?[a-z,A-Z, ,ô,è,é,\',:,à,É,ê,’,*,À,&][\)]?)|([\(]?[-][a-z,A-Z,ô,è,é,\',:,à,É,ê,’,*,À,&][\)]?))*(.*)')  
    valeur=verif.search(ch).group(4)
    print("valeur: ",valeur)
    if(valeur=='')|(valeur==' '):
        val=''
    elif(valeur.rfind('  ')!=-1):
        

        val=extract_value2(ch)
        print("ici2:",val)
        #print("ap manel:", val)
        if(val=="-"):
            val="0"
            return val
        if(len(val)<=3):
            ch=ch[len(ch)::-1]
            ch=ch.replace('  ',' ',1)
            ch=ch[len(ch)::-1]
            print("ici3",ch)
            val=extract_value2(ch)
        val=get_val(val)
        print("ici4",val)
        verif=re.compile(r'(([\(]?[a-z,A-Z, ,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?)|([\(]?[-][a-z,A-Z,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?))*(.*)')
        if(verif.search(val).group(1)!=None):
            
            verif=re.compile(r'(([\(]?[a-z,A-Z, ,ô,è,é,\',:,à,É,.,ê,’,*,À,&][\)]?)|([\(]?[-][a-z,A-Z,ô,è,é,\',:,à,É,ê,.,’,*,À,&][\)]?))*(.*)')
            val=verif.search(val).group(4)
        #double espace aprés le premier chiffre de la valeur du de la dérniere année
        verif_extra_int_end=re.compile(r'((.*)[0-9][0-9][0-9]) [0-9]?[0-9]$')
        if(verif_extra_int_end.search(val)):
            val=verif_extra_int_end.search(val).group(1)
        verif_espace=re.compile(r'(^[0-9][0-9]?  )(.+)')
        if(len(val)<3)and(verif_espace.search(valeur)):
            val=no_double_espace(verif_espace.search(valeur).group(2))
            
       
    else:
        valeur=get_val(ch)
        if(valeur=="0"):
            return valeur
        #verifier si la premiere année commence par le parenthése
        prenthese=re.compile(r'(^[\(][0-9, ]+[\)])(.*)')
        #vérifier si l'année précedente avec parenthese
        prenthese2=re.compile(r'(.*)([\(][0-9, ]+[\)])(.*)')
        #méme que les parentheses mais avec <>
        prenthese3=re.compile(r'(^[<][0-9, ]+[>])(.*)')
        prenthese4=re.compile(r'(.*)([<][0-9, ]+[>])(.*)')
        if(prenthese.search(valeur)):
            val=prenthese.search(valeur).group(1)
        elif(prenthese2.search(valeur)):
            val=prenthese2.search(valeur).group(1)
        elif(prenthese3.search(valeur)):
            val=prenthese3.search(valeur).group(1)
        elif(prenthese4.search(valeur)):
            val=prenthese4.search(valeur).group(1)
    

        else:
            #longueur de la valeur de l'année précedente n'est pas multiple de 3
            extrait=re.compile(r'(.+) [-]?([1-9]|[1-9][0-9]) (.+)')
            if(extrait.search(valeur)):
                val=extrait.search(valeur).group(1)
            else:
                if valeur[0]==' ' :
                    valeur=valeur[1:len(valeur)]
                while valeur[len(valeur)-1]==' ':
                    valeur=valeur[0:len(valeur)-1]
                if(re.compile(r'(^[-]?[1-9][0-9][0-9] )(.+)').search(valeur)):
                    c=int(valeur.count(' ')  // 2)
                    fin=(3*(c+1))+c
                    val=valeur[0:fin+1]
                else :
                    extrait=re.compile(r'([1-9] |[1-9][0-9] )(.+)')
                    extract=extrait.search(valeur).group(2)
                    c=int(extract.count(' ')  // 2)
                    fin=(3*(c+1))+c

                    chaine=extract[0:fin+1]

                    val=extrait.search(valeur).group(1)+chaine
    
    if vir==2 :
        if(val[len(val)-1]==(")")):
            val=val[0:len(val)-4] 
            val=val+')'
        else :
            val=val[0:len(val)-3]
            
    return val 

def extract_data_from_bilan(textbilan,dict_bilan):

    TCPP = ''
    CP = ''
    PNC = ''
    TA = ''
    TP = ''
    PC = ''
    RES = ''
    CAP = ''
    ANC = ''
    AC = ''

    for line in textbilan:
        if ((all(x in line.lower() for x in dict_bilan[0].split(' ')) or all(x in line.lower() for x in dict_bilan[1].split(' '))) 
            and ("Notes" not in line)):
            TCPP=extract_value(line) 

        elif(( (all(x in line.lower() for x in dict_bilan[2].split(' ')) and ("et" not in line)) or 
            all(x in line.lower() for x in ['cx','propres']))):

            CP=extract_value(line)            
    
            if (line[0:38] == dict_bilan[13] or line[0:46] == dict_bilan[12]):
                CP=''

        elif all(x in line.lower() for x in dict_bilan[3].split(' ')):
            PNC=extract_value(line)

        elif all(x in line.lower() for x in dict_bilan[4].split(' ')):
            PC=extract_value(line)

        elif ((all(x in line.lower() for x in dict_bilan[5].split(' ')) or all(x in line.lower() for x in dict_bilan[6].split(' ')))
              and ("," not in line)) :
            TP=extract_value(line)

        elif all(x in line.lower() for x in dict_bilan[7].split(' ')):
            ANC=extract_value(line)

        elif all(x in line.lower() for x in dict_bilan[8].split(' ')):
            AC=extract_value(line)

            
        elif (all(x in line.lower() for x in dict_bilan[9].split(' ')) or all(x in line.lower() for x in dict_bilan[10].split(' '))):
            TA=extract_value(line)  
            if(len(TA)>3 and (TA[-2]==' ')):
                TA=TA[0:len(TA)-2]
         
        elif any(x in line.lower() for x in dict_bilan[14].split(' ')):
            if(RES==''):
                RES=extract_value(line)
          #  print(line)
          #  print('reserve ',RES)
        elif any(x in line.lower() for x in dict_bilan[15].split(' ')):
            CAP=extract_value(line)
          #  print(line)
            
    return [TCPP,CP,PNC,TA,TP,PC,ANC,AC,RES,CAP]


def extract_data_from_etat_resultat(textetat,dict_etat_resultat):

   
    TProdExpl =''
    TChargeExpl =''
    R_Expl =''
    R_Exercice =''
    ActOrd ='' 
    Dot = ''

    for line in textetat:
        if ((any(x in line.lower() for x in dict_etat_resultat[0].split(' '))) and 
              (any(x in line.lower() for x in dict_etat_resultat[2].split(' ')))and ("placements" not in line)):
            
            TProdExpl=extract_value(line)

        elif ((any(x in line.lower() for x in dict_etat_resultat[1].split(' '))) and 
              (any(x in line.lower() for x in dict_etat_resultat[2].split(' ')))):
              
            TChargeExpl=extract_value(line)
 

        elif ((any(x in line.lower() for x in dict_etat_resultat[3].split(' '))) and 
              (any(x in line.lower() for x in dict_etat_resultat[4].split(' ')))):
            R_Expl=extract_value(line)


        elif ((any(x in line.lower() for x in dict_etat_resultat[3].split(' '))) and 
              (any(x in line.lower() for x in dict_etat_resultat[5].split(' ')))):
             
            R_Exercice=extract_value(line)

        elif ((any(x in line.lower() for x in dict_etat_resultat[6].split(' '))) and 
              (any(x in line.lower() for x in dict_etat_resultat[7].split(' ')))):
            ActOrd=extract_value(line)
            
        elif ((all(x in line.lower() for x in dict_etat_resultat[8].split(' '))) or
              (any(x in line.lower() for x in dict_etat_resultat[9].split(' ')))):

            print(line)
            if(Dot == ''):
                
             #   line=line[line.rfind('.',)+1:len(line)].replace(',','')
                print(line)
                Dot=extract_value(line[3:len(line)])
            print(Dot)


    return [TProdExpl,TChargeExpl,R_Expl,R_Exercice,ActOrd,Dot ]




def extract_data_from_flux_tresorerie(texttresorerie,dict_flux_tresorerie):
    
   
    FT_Exp =''
    FT_Fin =''
    FT_Inv =''
    Variation =''
    TDeb ='' 
    TFin =''

    for line in texttresorerie:
        if ((any(x in line.lower() for x in dict_flux_tresorerie[0].split(' '))) and 
              (any(x in line.lower() for x in dict_flux_tresorerie[1].split(' ')))):
            FT_Exp=extract_value(line)    

        elif ((any(x in line.lower() for x in dict_flux_tresorerie[0].split(' '))) and 
              (any(x in line.lower() for x in dict_flux_tresorerie[2].split(' ')))):
            FT_Inv=extract_value(line)
 
        elif((any(x in line.lower() for x in dict_flux_tresorerie[0].split(' '))) and 
              (any(x in line.lower() for x in dict_flux_tresorerie[3].split(' ')))):
            FT_Fin=extract_value(line) 

        elif ((any(x in line.lower() for x in dict_flux_tresorerie[4].split(' '))) and 
              (any(x in line.lower() for x in dict_flux_tresorerie[5].split(' ')))):
            TDeb=extract_value(line)

        elif ((any(x in line.lower() for x in dict_flux_tresorerie[4].split(' '))) and 
              (any(x in line.lower() for x in dict_flux_tresorerie[6].split(' ')))):
            TFin=extract_value(line)


        elif ((any(x in line.lower() for x in dict_flux_tresorerie[7].split(' '))) and 
              (any(x in line.lower() for x in dict_flux_tresorerie[8].split(' ')))):
            Variation=extract_value(line)

    return [FT_Exp,FT_Inv,FT_Fin,TDeb,TFin,Variation]

def exception_Bilan(line,dict_etat_resultat):

    R_ExerciceTemp =''
    ActOrdTemp ='' 


    if ((any(x in line.lower() for x in dict_etat_resultat[3].split(' '))) and 
        (any(x in line.lower() for x in dict_etat_resultat[5].split(' ')))):
             
        R_ExerciceTemp=extract_value(line)

    if ((any(x in line.lower() for x in dict_etat_resultat[6].split(' '))) and 
        (any(x in line.lower() for x in dict_etat_resultat[7].split(' ')))):
        ActOrdTemp=extract_value(line)

    return [R_ExerciceTemp,ActOrdTemp ]
@login_required(login_url='login')
def fonctionExtraction(request):
    liste=[request.session.get("filename","null")]
    print(liste)
    with open ("dict_bilan.txt", "r",encoding='utf-8') as f1:
        dict_bilan = f1.read().split('\n')

    with open ("dict_etat_resultat.txt", "r",encoding='utf-8') as f2:
        dict_etat_resultat = f2.read().split('\n')
    
    with open ("dict_flux_tresorerie.txt", "r",encoding='utf-8') as f3:
        dict_flux_tresorerie = f3.read().split('\n')

    ligne = namedtuple('ligne', 'Entreprise Annee TCPP CapitalPropre PassifNonC TActif TPassif PassifCourant ActifNonC ActifCourant Reserves CapitalSociale TProdExploitation TChargeExploitation R_Exploitation Res_Exsercice ActiviteOrdinaire Dotation FT_Exploitation FT_Investisement FT_Financement TDebut TFin Variation')
    lines = []
    rmSp = re.compile(r'^\s+',re.MULTILINE)
    for l in liste :
        s=l[0:(len(l)-4)].split('-')
        Entreprise=s[0]
        Annee=s[-1]
        textbilan = []
        textetat = []
        texttresorerie = []
        tempResExercice=""
        tempActOrd=""
    with pdfplumber.open('shortPDF/'+l) as pdf:
        pages = pdf.pages
        print(l)
        if(len(pages) == 3):
          
      
            for line in pages[0].extract_text().split('\n'):
                if rmSp.match(line):
                    line=textwrap.dedent(line)
                if line.lower().startswith(('total','capitaux','t o ta  l','actif ','passif ','sous-total','réserve','cp','reserves')): 
                    textbilan.append(line)
                    #print(line)
                if (line.lower().startswith('résultat') or line.lower().startswith('resultat') or line.lower().startswith('resultats')) :
                    temp=exception_Bilan(line,dict_etat_resultat)
                    tempResExercice=temp[0]
                    tempActOrd=temp[1]

            
            for line in pages[1].extract_text().split('\n'):
                if rmSp.match(line):
                    line=textwrap.dedent(line)
                if line.lower().startswith(('  résultat','résultat','total','charges','produit','t o tal','resultat','ch','resultats','dotation')): 
                    textetat.append(line)
                  #  print(line)
            
            for line in pages[2].extract_text().split('\n'):
                if rmSp.match(line):
                    line=textwrap.dedent(line)
                if line.lower().startswith(('flux','variation','liquid', 'f l','   trésorerie','total','trésorerie','fluflux','vavariation')): 
                    texttresorerie.append(line)
           
                    
            l1=tuple(extract_data_from_bilan(textbilan,dict_bilan))
            l2=(extract_data_from_etat_resultat(textetat,dict_etat_resultat))
            l3=(extract_data_from_flux_tresorerie(texttresorerie,dict_flux_tresorerie))
            
            if((l2[3]=="") and tempResExercice != ""):
                l2[3]=tempResExercice
                    
            if((l2[3]=="") and tempResExercice != ""):
                l2[3]=tempResExercice
                
            lines.append(ligne(Entreprise,Annee,l1[0],l1[1],l1[2],l1[3],l1[4],l1[5],l1[6],l1[7],l1[8],l1[9],l2[0],l2[1],l2[2],
                        l2[3],l2[4],l2[5],l3[0],l3[1],l3[2],l3[3],l3[4],l3[5]))
        
        elif(len(pages) == 4):
    
            for line in pages[0].extract_text().split('\n'):
                if rmSp.match(line):
                    line=textwrap.dedent(line)

                if line.lower().startswith(('total','t o ta  l','actif ','réserve')): 
                    textbilan.append(line)
    
                    
            for line in pages[1].extract_text().split('\n'):
                if rmSp.match(line):
                    line=textwrap.dedent(line)
                if line.lower().startswith(('total','capitaux','t o ta  l','passif ','réserve','cp','reserves','capital')): 
                    textbilan.append(line)
               # print(line)
                   
                if (line.lower().startswith('résultat') or line.lower().startswith('resultat') or line.lower().startswith('resultats')) :
                    temp=exception_Bilan(line,dict_etat_resultat)
                    tempResExercice=temp[0]
                    tempActOrd=temp[1]

                    
            for line in pages[2].extract_text().split('\n'):
                
                if rmSp.match(line):
                    line=textwrap.dedent(line)
                if line.lower().startswith(('résultat','total','charges','produit','v.6','t o tal','resultat','  résultat','+  dotations','dotation')): 
                    textetat.append(line)
                print(line)

            for line in pages[3].extract_text().split('\n'):
         
                if rmSp.match(line):
                    line=textwrap.dedent(line)
                    
                if line.lower().startswith(('flux','variation','liquid', 'f l','   trésorerie','total','trésorerie','fluflux','vavariation','- trésorerie')): 
                    texttresorerie.append(line)
            
                   
                
            l1=(extract_data_from_bilan(textbilan,dict_bilan))
            l2=(extract_data_from_etat_resultat(textetat,dict_etat_resultat))
            l3=(extract_data_from_flux_tresorerie(texttresorerie,dict_flux_tresorerie))
        
            if((l2[3]=="") and tempResExercice != ""):
                l2[3]=tempResExercice
                    
            if((l2[4]=="") and tempActOrd != ""):
                l2[4]=tempResExercice
                
            lines.append(ligne(Entreprise,Annee,l1[0],l1[1],l1[2],l1[3],l1[4],l1[5],l1[6],l1[7],l1[8],l1[9],l2[0],l2[1],l2[2],l2[3],l2[4],
                          l2[5],l3[0],l3[1],l3[2],l3[3],l3[4],l3[5]))

    df=pd.DataFrame(lines)
    df.replace(to_replace ='\(', value = '-', regex = True,inplace=True)
    df.replace(to_replace ='\<', value = '-', regex = True,inplace=True)
    df.replace(to_replace ='\s', value = '', regex = True,inplace=True)
    df.replace(to_replace ='\)', value = '', regex = True,inplace=True)
    df.replace(to_replace ='\>', value = '', regex = True,inplace=True)
    typ_objet =df.columns
    typ=typ_objet[2:]
    for index, row in df.iterrows():
        for i in range(len(typ)):
            CapitalPropre = df.columns.get_loc(typ[i])
            new_col = pd.to_numeric(df.iloc[:,CapitalPropre], errors='coerce')
            #coerce: the invalid parsing will be set as NaN
            df.iloc[:, CapitalPropre] = pd.Series(new_col)
    #df=pd.DataFrame(  )
    #formule de remplacement du capital propre
#formule de remplacement du capital propre
    df.loc[df.TCPP.isna(),"TCPP"]=df["TActif"]
    df.loc[df.TCPP.isna(),"TCPP"]=df["CapitalPropre"]-df["TPassif"]
    df.loc[df.CapitalPropre.isna(),"CapitalPropre"] = df["TCPP"]-df["TPassif"]
    df.loc[df.TPassif.isnull(),"TPassif"]=df["TCPP"]-df["CapitalPropre"]
#formule de remplacement des passifs dans le bilan
    df.loc[df.PassifNonC.isnull(),"PassifNonC"]=df["TPassif"]-df["PassifCourant"]
    df.loc[df.TPassif.isnull(),"TPassif"]=df["PassifNonC"]+df["PassifCourant"]
    df.loc[df.PassifCourant.isnull(),"PassifCourant"]=df["TPassif"]-df["PassifNonC"]
    df.loc[df.TActif.isna(),"TActif"] = df["TCPP"]
    df.loc[df.ActifCourant.isna(),"ActifCourant"] = df["TActif"]/2
    df.loc[df.ActifNonC.isna(),"ActifNonC"] = df["TActif"]/2
    df.loc[df.PassifNonC.isna(),"PassifCourant"] = df["TPassif"]/2
    df.loc[df.PassifNonC.isna(),"PassifNonC"] = df["TPassif"]/2
    df.loc[df.ActifCourant.isna(),"PassifCourant"] = df["TPassif"]/2
    df.loc[df.ActiviteOrdinaire.isna(),"ActiviteOrdinaire"] = df["Res_Exsercice"]
#Resultat de l'exercice
    df.loc[df.Res_Exsercice.isnull(),"Res_Exsercice"]=df["TActif"]-df["TPassif"]
#formule de remplace des exploitation dans l'etat de resultat
    df.loc[df.R_Exploitation.isnull(),"R_Exploitation"]=df["TProdExploitation"]-df["TChargeExploitation"]
    df.loc[df.TProdExploitation.isnull(),"TProdExploitation"]=df["R_Exploitation"]+df["TChargeExploitation"]
    df.loc[df.TChargeExploitation.isnull(),"TChargeExploitation"]=df["TProdExploitation"]-df["R_Exploitation"]
    df.loc[df.Variation.isna(),"Variation"] = df["TFin"]-df["TDebut"]
    df.loc[df.TFin.isna(),"TFin"] = df["Variation"]-df["TDebut"]
    df.loc[df.TDebut.isna(),"TDebut"] = df["Variation"]-df["TFin"]
    df.loc[df.Reserves.isnull(),"Reserves"]=df["CapitalPropre"]-df["CapitalSociale"]-df["Res_Exsercice"]
    df.loc[df.CapitalSociale.isna(),"CapitalSociale"]=df["CapitalPropre"]-df["Reserves"]-df["Res_Exsercice"]

   # df.apply(lambda x: x['TCPP'] - x['TActif'], axis = 1)
    df.fillna(0, inplace=True)
    df2=df
    print(df2)
    df2.to_csv('django.csv',index=False)
    path="C:/Users/HP/Desktop/IntelFin/"
    df = pd.read_csv(path+"django.csv",sep=",")
    print(df)
    json_records = df.reset_index().to_json(orient ='records',default_handler=str)
    #arr = JSON.parse(JSON.stringify(arr).replace(/\s(?=\w+":)/g, ""))
    data=[]
    data = json.loads(json_records)
    print(data)
    context = {'d': data} 
    return render(request,'frontend/extraction/page4.html',context)

def viewData(request):
    path="C:/Users/HP/Desktop/IntelFin/"
    df = pd.read_csv(path+"django.csv",sep=";")
    print(df)
    #df=pd.DataFrame(  )
    json_records = df.reset_index().to_json(orient ='records',default_handler=str)
    #arr = JSON.parse(JSON.stringify(arr).replace(/\s(?=\w+":)/g, ""))
    data=[]
    data = json.loads(json_records)
    print(data)
    context = {'d': data} 
    #print(countOfrow['Partner'])
    #a=collectionD.find().limit(1)
    #countOfrow = df.to_html(classes=["table-bordered", "table-striped", "table-hover"],header = "true", justify = "center")
    #context={'countOfrow':a}
    return render(request,'frontend/extraction/page1.html',context)

@login_required(login_url='login')
def prediction(request):
    modeling_df= pd.read_csv("TrainDataset.csv")
    ligne= pd.read_csv("django.csv",sep=",")
    dfdashboard=ligne.copy()
    features =  ['TCPP', 'CapitalPropre', 'PassifNonC', 'TActif', 'TPassif', 'PassifCourant', 
    'ActifNonC', 'CapitalSociale', 'TProdExploitation', 'TChargeExploitation', 'R_Exploitation', 
    'Res_Exsercice', 'ActiviteOrdinaire', 'Dotation', 'Variation']
    Y_train=modeling_df['y'].copy()
    X_train=modeling_df[features].copy()
    scaler=StandardScaler()
    X_train=scaler.fit_transform(X_train[features])
    rf = RandomForestClassifier(criterion= 'gini', max_depth= 9, max_features='auto',n_estimators= 50)
    rf.fit(X_train, Y_train)
    ligne[features]=scaler.transform(ligne[features])
    ligne=ligne[features]
    print(ligne)
    d=np.array(ligne)
    #Entreprise Solvable
    pred1=rf.predict(d)

    print(pred1)
    #Test2
    ResultatPrediction2="test with value"
    if pred1==1:
        ResultatPrediction2="Solvent"
    else:
        ResultatPrediction2="Insolvent"


    form=ExtraColForm()
    submitted = False
    chiff =0
    cap = 0
    if request.method == "POST" :
        
        chiff = request.POST.get('turnover')
        cap = request.POST.get('market_capitalization')
        #L=[[entr,annee,chiff,cap]]
        #df = DataFrame (L,columns=['Entreprise','Annee','ChiffreAffaire','CapBourssiere'])
        #data=df.assign(Chiffre_Affaire=df["ChiffreAffaire"],CapBoursiere=df['CapBourssiere'])
        #print(data)
        

        lines=namedtuple('lines','ChiffreAffaire CapBoursiere')
        ligne=[]
        ligne.append(lines(chiff,cap))
        dfr=pd.DataFrame(ligne) 
        dfr.to_csv('manuelvalue.csv',index=False)
        print(dfr)
        dfBig= pd.read_csv("dashboard.csv",sep=",")
        #data=dfBig.assign(ChiffreAffaire=dfr["ChiffreAffaire"],CapBoursiere=dfr['CapBoursiere'])
        dataF = pd.concat([dfBig, dfr.reindex(dfBig.index)], axis=1)
        #print(dataF)
        dataF.to_csv('datasetcomplete.csv',sep=",")
        form = ExtraColForm(request.POST)
        if form.is_valid() :
            form.save()
            dfdashboard['Chiffre_Affaire']=chiff       
            dfdashboard['CapBoursiere']=cap     
            dfdashboard['y']=pred1
            dfdashboard.to_csv('dashboard.csv',index=False)
            df1 = pd.read_csv("C:/Users/HP/Desktop/IntelFin/dashboard/Resources/DatasetDashboard.csv")
            df2 = pd.concat([df1,dfdashboard])
            df2.to_csv("C:/Users/HP/Desktop/IntelFin/dashboard/Resources/DatasetDashboard.csv",index=False)
                    
           
        
        else :
            form = ExtraColForm()
        if 'submitted' in request.GET:
            submitted = True

    

    # context1={"form":form}
    
    return render(request,'frontend/extraction/page4.html',{'result':ResultatPrediction2,"form":form,'submitted':submitted})
  



