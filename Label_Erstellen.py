# -*- coding: iso-8859-1 -*-

# vorher war's cp1252

 
from Tkinter import *
import tkMessageBox
import time
import unicodedata

def verb(zeile,a=0,b=0):
    print zeile

def get_codebook(filename): ##Load the codebook from a given file. Returns a codebook-Dictionary for use within the tool.        
    cb = {}
    cb_file = open(filename, 'r')
    F_list = cb_file.readlines()
    cb_file.close()
    i = 0
    while i < (len(F_list)-1):
        if F_list[i][0] == '[':
            varname = F_list[i][1:-2]
            varfrage = F_list[i+1]
            varanw = F_list[i+2]
            varhilfe = F_list[i+3]

            if varfrage[:6] == 'Frage:':
                varfrage = varfrage[7:]
            if varanw[:10] == 'Anweisung:':
                varanw = varanw[11:]
            if varhilfe[:6] == 'Hilfe:':
                varhilfe = varhilfe[7:]

            i = i + 4
            optionen = []
            codes = []
            while not F_list[i] == '\n':
                cod_zeile = F_list[i]
                cut = cod_zeile.find(':')
                if cut == -1:
                    opt = cod_zeile
                    cod = cod_zeile
                else:
                    opt = cod_zeile[cut+1:-1]
                    cod = cod_zeile[:cut]

                while '#' in opt:
                    c = opt.find('#')
                    opt = opt[:c]+'\n'+opt[c+1:]
                optionen.append(opt)
                codes.append(cod)
                i = i + 1

            verb(varname+str(optionen))

            cb[varname] = []
            cb[varname].append(varfrage) #codebook['variabel'][0] is the question as string (including final linebreak)
            cb[varname].append(varanw)   #codebook['variabel'][1] is the coder information
            cb[varname].append(optionen) #codebook['variabel'][2] is a list containing all labels
            cb[varname].append(codes)    #codebook['variabel'][3] is a list containing all codes (parallel to [2]
            cb[varname].append(varhilfe)    #codebook['variabel'][4] is the helptext
        i = i + 1
    
    verb('Codebook loaded successfully')
    return cb

def namegetter(codebuch,variabel,item):
    varindex = ''
    for i in range(0,len(codebuch[variabel][2])):
        try:
            if codebuch[variabel][3][i] == item:
                varindex = codebuch[variabel][2][i]
        except:
            varindex = 'sonderzeichen!'

    if varindex == '':
        print 'Kein Itemname vorhanden für',item
    else:
        print 'Itemname gefunden: ',varindex

    return varindex


multi_items = ['Art_Source', 'Frame_HI','Frame_Con','Language','Iss_Elab',
                           'Iss_Just','Rhetoric','Emot','Att_Pos','Att_Neg','Att_Impact',
                           'Att_People','Att_Act','Privat','VSymbol','V_Cues']

artikel_tab = ['Medium','Author','Date','Length','Images','Position','Genre',
               'Art_Source','Main_Issue','Frame_HI','Frame_Con','Heartland',
               'Bemerkungen','Fulltext','Count_Speaker','Count_Issues','Count_ActEval']

spr_tab = ['Spr_ID','A_Prom','A_Pres','Quotation','Language','Sp_Situation','VSymbol',
           'Count_Issues_S','Count_ActEval_S','Wording','Fulltext']

iss_tab = ['Iss_Elab','Act_Appoint','Act_Deny','Iss_Pos','Iss_Just','Sourcing','Rhetoric','V_Cues']

act_tab =['#TS','Tgt_ID','Def_Volk','Def_PEli','Def_SupI','Def_SPty','Def_SPer',
          'Def_SGrp','Def_NApp','Def_Othr','Embod','Monolith','Distance','Iss_Link',
          'Att_Pos','Att_Neg','Att_Impact','Att_People','Att_Act','Privat','PrivAtt','Namecall','Stereo']


allin_tab = ['Codierstart_Lab','Medium','Author','Date','Length','Images','Position',
             'Genre','Art_Source','Main_Issue','Frame_HI','Frame_Con','Heartland',
             'Bemerkungen','Count_Speaker','Count_Issues','Count_ActEval','Spr_ID',
             'A_Prom','A_Pres','Quotation','Language','Count_Issues_S',
             'Count_ActEval_S','Iss_ID','Iss_Elab','Iss_Pos','Iss_Just',
             'Sourcing','Rhetoric','Tgt_ID','Def_Volk','Def_PEli','Def_SupI',
             'Def_SPty','Def_SPer','Def_SGrp','Def_NApp','Distance','Iss_Link',
             'Att_Pos','Att_Neg','Att_Impact','Att_Act','Privat','PrivAtt','Namecall','Stereo']

complete_tab = [artikel_tab,spr_tab,iss_tab,act_tab,allin_tab]

codebuch = get_codebook('a_codebuch.ini')
syntax_file = open('syntax_labels.txt','w')

for liste in complete_tab:
    syntax_file.write('\n\n*-------------------------NEW BLOCK--------------.\n\n\n')
    for element in liste:
        if element in codebuch.keys():
            if element in multi_items:
                for i in range(len(codebuch[element][3])):
                    ausp = codebuch[element][3][i]
                    option = codebuch[element][2][i]
                    vname = element + '_' + ausp
                    syntax_file.write('\nVARIABLE LABELS ')
                    syntax_file.write(vname)
                    syntax_file.write(" '")
                    syntax_file.write(codebuch[element][0][:-1]+' - '+option)
                    syntax_file.write("'.\n")
                    syntax_file.write('VARIABLE LEVEL '+vname+'(NOMINAL).\n')
                    syntax_file.write('VALUE LABELS '+vname+' 0 "not selected" 1 "selected".\n\n')                   
            else:       
                syntax_file.write('\nVARIABLE LABELS ')
                syntax_file.write(element)
                syntax_file.write(" '")
                syntax_file.write(codebuch[element][0][:-1])
                syntax_file.write("'.\n")
                if len(codebuch[element][2]) > 0:
                    syntax_file.write('MISSING VALUES ')
                    syntax_file.write(element)
                    syntax_file.write(' (98).\n')
                    syntax_file.write('VARIABLE LEVEL '+element+'(NOMINAL).\n')
                    syntax_file.write('VALUE LABELS ')
                    syntax_file.write(element)
                    for i in range(0,len(codebuch[element][2])):
                        syntax_file.write(" '")
                        syntax_file.write(codebuch[element][3][i])
                        syntax_file.write("' '")
                        syntax_file.write(codebuch[element][2][i])
                        syntax_file.write("'")
                        if i < len(codebuch[element][2])-1:
                            syntax_file.write("\n")
                        else:
                            syntax_file.write(".\n\n\n")
        else:
            syntax_file.write('*CAUTION. MISSING VARIABLE IN SYNTAX: ')
            print element
            syntax_file.write(element)
            syntax_file.write(".\n\n")
           
        syntax_file.write('\n')
    syntax_file.write('\n\n')

