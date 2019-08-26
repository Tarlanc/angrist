# -*- coding: utf-8 -*-

###############################################################################################
##                                                                                           ##
##                              ANGRIST 1.2 - Coder Interface                                ##
##                              -----------------------------                                ##
##                                                                                           ##
##  Programmer: Martin Wettstein,                                                            ##
##              University of Zürich                                                         ##
##              m.wettstein@ipmz.uzh.ch                                                      ##
##                                                                                           ##
##  For detailed references, see:                                                            ##
##              http://www.ipmz.uzh.ch/Abteilungen/Medienpsychologie/Recource/Angrist.html   ##
##                                                                                           ##
##                                                                                           ##
###############################################################################################


from Tkinter import *
import tkMessageBox
import tkFileDialog
import time
import math
import unicodedata
import os
try:
    from aeglos import predict
except:
    i = 1


class CMD: #Auxilliary function for callbacks using parameters.
           #Syntax: CMD(function, argument1, argument2, ...)
    def __init__(s1, func, *args):
        s1.func = func
        s1.args = args
    def __call__(s1, *args):
        args = s1.args+args
        apply(s1.func, args)
        
class Anzeige(Frame):
    def __init__(self, master=None):        
        Frame.__init__(self,master)
        top=self.winfo_toplevel() #Flexible Toplevel of the window
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.grid(sticky=N+S+W+E)
        self.rowconfigure(6, weight=1) #Only expandable row in the
                                       #grid is row 6 (above bottomline frame)
        self.columnconfigure(3, weight=1) #Only expandable column in
                                          #the grid is column 15 (text field)
        self.bind_all("<F1>",self.debug_on)
        self.bind_all("<F2>",self.show_path)
        self.bind_all("<F3>",self.show_verb)
        self.bind_all("<F4>",self.show_storage)
        self.bind_all("<F5>",self.comment)
        self.bind_all("<F8>",display_page)
        self.bind_all("<F7>",self.submit)

        root.title("ANGRIST 1.2 - Coder Interface")
        self.fuellen()
        
    def fuellen(self):
        global codebook #codebook, entsprechend der Datei 'codebook.ini'
        global storage #Variabeltupel, das angibt,
                       #welche Variable wie belegt ist
        global dta_pos #Aktuelle Position im Codierbaum. Ein Tupel der Form:
                       #(Artikel, Development, Element)
        dta_pos = 'NO DATA YET'
        global prog_pos #Aktuelle Position im codebook. Ein String, der angibt,
                        #bei welcher Variable das Programm steht.
        prog_pos = 'NO POSITION YET'
        global def_val #Default-Werte für einzelne Variablen in einem Directory
        def_val = {}
        global settings #Dictionary for flexible settings and entries.
        settings['Break_Time'] = 0
        settings['Session_Text'] = settings['Session_Text'] + 1

        #Just trying to remove everything on the screen. Only useful in the case
        #of critical aborts that are redirected to fuellen()
        try:
            self.f_review.destroy()
            self.f_location.destroy()
            self.f_explanation.destroy()
            self.f_questions.destroy()
            self.f_bottomline.destroy()
            self.Artikel.destroy()
            self.etui.destroy()
            self.yscroller.destroy()
        except:
            verb("Start of the session.",1)

        #Just a spacer to keep the window size constant
        self.spacer = Text(self,width=1,height=45, bg=settings['BG_Color'],
                           relief=FLAT,takefocus = 0)
        self.spacer.grid(row=0,column=0,rowspan=8)

        ##
        ## Below this point all global variables and settings are defined
        ##
        #All settings values set below are overwritten as soon as a
        #file for coder settings is found to specify other settings.

        settings['Highlight_Buttons'] = [['Speaker','Spr','#ffff66'],
                                         ['Issue','Iss','#66ff66'],
                                         ['Target','Tgt','#99aaff']]
        settings['Multi_Items'] = ['Art_Source', 'Frame_HI','Frame_Con',
                                   'Frame_PRF','Frame_Neg','Language',
                                   'Iss_Elab','Argument','Iss_Just','Rhetoric',
                                   'Sourcing','Emot','Att_Pos','Att_Neg','Att_Impact',
                                   'Att_People','Att_Act','Att_Power','Privat',
                                   'CFB_Feel','CFB_Fun','CFB_Background',
                                   'CFB_Disturbance','CFB_Breaks','VSymbol','V_Cues']
        settings['First_Page'] = 'end of project'
        #settings['First_Page']='change_text'
        #settings['Fulltext']='' #Location for the storage of the
                                #currently coded text
        settings['Country']='unknown'

        if 'Speaker' in settings.keys():
            del settings['Speaker']

            
        ##
        ## Below external sources are included to load additional settings
        ##

        global cini
        if available('Settings'):
            cini = get_codebook(settings['Settings'])
        else:
            cini = get_codebook('a_settings.ini') #Loading coder information
                                                  #from a_settings.ini

        if available('Out_Log'):
            settings['Logging_Info']=[]

        if 'Coder-Settings' in cini.keys():
            for i in range(0,len(cini['Coder-Settings'][3])):
                cod = cini['Coder-Settings'][3][i]
                val = cini['Coder-Settings'][2][i]
                settings[cod] = val
        if 'Default-Values' in cini.keys():
            dv = self.load_cset(cini['Default-Values'])
            for i in range(0,len(dv[3])):
                def_val[dv[3][i]] = dv[2][i]
            verb('Default_Values:'+str(def_val))
        
          
        codebook = {}
        if available('Codebook'):
            codebook = get_codebook(settings['Codebook'])
        else:
            codebook = get_codebook('a_codebook.ini')
        
        iss_cod = get_codebook('a_issuelist.txt')
        for v in iss_cod.keys():
            codebook[v] = iss_cod[v]

        for v in sorted(codebook.keys()):
            verb(v+'; ',nl=0)
        verb('\n'+str(len(codebook.keys()))+'Variables in Codebook.')


        if available('Package_Todo'):
            art_name = get_todo(settings['Package_Todo'])
            if not art_name == '':                
                settings['Todo'] = '.\\' + art_name + settings['Todo']
                settings['Text_Folder'] = '.\\' + art_name + '\\'
        else:
            art_name = ''

        if available('Todo'):
            art_id = get_todo(settings['Todo'])
        else:
            verb('No Todo-list')
            art_id = ''
               

        storage = {}
        storage['#TS'] = (time.ctime(), time.time())
             #Timestamp of beginning of coding. Tuple of
             #the shape (String describing time, timestamp in seconds)
        storage['Breaks'] = 0
        storage['Helptexts'] = 0
        storage['Backs'] = 0
        storage['Remove_item'] = 0
        storage['ID'] = art_id
        storage['Discard'] = 0
        storage['Highlight'] = {}
        storage['Highlight']['Spr']={}
        storage['Medium_Type']=''
        storage['#T_Brutto'] = 0
        storage['#T_Netto'] = 0
        storage['#T_Break'] = 0

        if available('Out_Log'):
            outlog = open(settings['Out_Log'],'a')
            outlog.write(settings['Coder']+'\t----Tool started on: '+str(time.ctime())+'\n')
            outlog.close()

        if not art_id == '':
            settings['Fulltext'] = artikelholen(storage['ID'])
            if storage['ID'][:2] in ['gr','bu','pl']:
                storage['Fulltext'] = bereinigen(settings['Fulltext'],encod='utf-8')
            else:
                storage['Fulltext'] = bereinigen(settings['Fulltext'])
            settings['PDF-Page'] = os.getcwd()+'\\Texts\\'+art_id[:-4]+'.jpg'
            #settings['PDF-Page'] = settings['Text_Folder']+art_id[:-4]+'.jpg'
            #print [settings['PDF-Page']]
            
        else:
            verb('ERROR: No valid identifier')
            #self.message('Runtime-Error02')
    

        if len(settings['Out_Track']) > 0:
            tf = open(settings['Out_Track'], 'a')
            tf.write('\n-------------\n')
            tf.write(str(storage['ID']))
            tf.write(': ')
            tf.write(str(time.ctime()))
            tf.write('\n-------------\n')
            tf.close()

        dta_pos = ['-', '-', '-', '-']
        
        if storage['ID'] == '':
            prog_pos = 'Art_ID_erfassen'
        elif settings['Fulltext'] == '':
            verb('ERROR: Article: "' + storage['ID'] + '" in Folder: "' +
                 settings['Text_Folder'] +'" does not exist.')
            codebook['ID'] = codebook['ID2']
            prog_pos = 'Art_ID_erfassen'
        else:
            self.anzeigen(settings['Fulltext'])
            prog_pos = settings['First_Page']
            self.load_countryspec()

        for i in range(0,len(cini['Default-Values'][3])):
            def_val[cini['Default-Values'][3][i]] = cini['Default-Values'][2][i]
        verb('Defaul_Values:'+str(def_val))

        verb('Coder: '+settings['Coder'])
        verb('Font: '+settings['Font'])
        verb('Articles folder: '+settings['Text_Folder'])

        self.set_window() #Start coding.


###################################
#                                 #
#    ASK-Function                 #
#                                 #
###################################

       
    def ask(self):
        global prog_pos
        global dta_pos
        global codebook
        global settings
        global storage
        log('\nCalling Function: ASK')
        #The ASK function is the core of this interface. In this function
        #all pages of the questionnaire are defined.
        #A variety of self.question-functions may be used in the questionnaire
        #   self.question_dd(variabel, Position): Dropdown selection
        #   self.question_cb(variabel, Position): Checkbox (Multiple selection)
        #   self.question_txt(variabel, Position): Text input (one line)
        #   self.question_txt2(variabel, Position[, width][, height]): Text input (multiple lines)
        #   self.question_rb(variabel, Position): Radiobutton selection (Single item selection)
        #   self.question_rating(variabel, Position): Multiple Items with rating scale
        #   self.question_ls(variabel, listenvariabel): List selection
        #   self.question_lseek(variable,listvariable): Searchable list selection
        #   self.question_ladd(variable,listvariable): Creating a sub-list of a large list
        #   self.question_bt(variabel, Position): Up to four buttons to press (each one has to be defined in this function)

        if prog_pos == 'choose_addition':
            dta_pos = ['-','-','-','-']

        if available('Out_Log'):
            if len(settings['Logging_Info']) > 5:
                verb('Writing Log-File (temporary storage)')
                outlog = open(settings['Out_Log'],'a')
                for page in settings['Logging_Info']:
                    outlog.write(settings['Coder']+'\t')
                    outlog.write(storage['ID']+'\t')
                    outlog.write(str(page[0])+'\t')
                    outlog.write(str(page[1])+'\t')
                    if len(page)>2:
                        outlog.write(str(page[-1])+'\n')
                    else:
                        outlog.write('0\n')
                outlog.close()
                settings['Logging_Info'] = []
            settings['Logging_Info'].append([prog_pos,time.time()])

        
        settings['Page_History'].append(prog_pos)
        self.intronase()
        storage['#TS2']=(time.ctime(), time.time())
        self.hide_review()
        if 'Location' in codebook.keys():
            self.locate('Current','Stat','Tow')
       
        if len(settings['Out_Track']) > 0:
            tf = open(settings['Out_Track'], 'a')
            tf.write(str(settings['Page_History']))
            tf.write('\t')
            tf.write(prog_pos)
            tf.write('\t')
            tf.write(str(dta_pos))
            tf.write('\n')
            tf.close()

       
        settings['Curr_Page'] = [['',''],['',''],['','']]

        if prog_pos == 'Art_ID_erfassen': #First page if no ID was found in any to-do list
            self.f_location.angabe.delete('1.0', END)
            self.buttons()
            self.ausblenden()
            self.question_txt('ID',1)

        elif prog_pos == 'change_text':
            self.buttons()
            self.question_change('Make_Changes',1)

        elif prog_pos == 'end of project':
            self.buttons(0,0,0,0)
            self.anzeigen('\n\nImportant notice:\n----------------\n\nDear coders,\n\nas of today, the content analysis is concluded. We thank you for your effort in the past months and years.\n\nBest regards,\nMartin')

            
        elif prog_pos == 'artspez1':
            if settings['Auto_Highlight'] in [1,'1'] and settings['Text_Aktiv']==1:           
                self.mark('worddetect') #Bisherige Markierung weg
            self.buttons(1,1,1,1)
            self.question_dd('Medium',1)
            self.question_dd('Author',2)
            if storage['Medium_Type']=='PDF':
                self.question_txt('Date',3)
            self.f_bottomline.b_abort['bg']='#ff8888'
            self.f_bottomline.b_abort['text']='Discard Text'
            

        elif prog_pos == 'author':
            self.buttons()
            self.question_lseek('Author_ID','Spr_ID')

        elif prog_pos == 'artspez2':
            self.buttons()
            if storage['Medium_Type'] in ['TV','Talk']:
                self.question_txt('TS_Beginning',1)
            else:
                self.question_txt('Length',1)
                if not storage['Medium_Type'] in ['EW','CD']:
                    self.question_dd('Position',3)

        elif prog_pos == 'artspez3':
            self.buttons()
            if storage['Medium_Type']=='SM':
                self.question_dd('Genre_SM',1)
            elif storage['Medium_Type']=='PR':
                self.question_dd('Genre_PR',1)
            elif storage['Medium_Type'] in ['TV','Talk']:
                self.question_dd('Genre_TV',1)
            else:
                self.question_dd('Genre',1)
            #self.question_cb('Art_Source',2)

        elif prog_pos == 's_markieren':
            self.buttons(0,0,1,1)
            if settings['Auto_Highlight'] in [1,'1']:           
                self.mark('worddetect') #Bisherige Markierung weg
                self.mark('worddetect',settings['Speakerlist'])
            self.question_mark_units('Mark_Text',['Spr','Iss','Tgt'])

        elif prog_pos == 'art_issue':
            self.buttons(1,1,1,1)           
            self.question_lseek('Main_Issue','Issuelist',1)
            self.f_bottomline.b_abort['bg']='#ff8888'
            self.f_bottomline.b_abort['text']='Discard Text'

            #self.question_txt2('Other_Issue',2,width=60,height=5,getselect=1)


        elif prog_pos == 'choose_addition':
            create_addlist('Choose_Addition_tmp',storage['Medium_Type'])
            self.buttons(0,1,1,1)            
            self.question_menu('Choose_Addition_tmp',1)
            
            self.f_bottomline.b_abort['text']='Coding complete'
            self.f_bottomline.b_abort['bg']="#a0eea0"
                 

        elif prog_pos == 's_auswahl':
            if available('Out_Tmp'):
                self.store_coding(settings['Out_Tmp']) ##Temporary storage of current coding. Just in case.
            if settings['Text_Aktiv']==1:
                self.buttons(1,0,1,1)
                self.clean_all_tags(['Spr']) ##Remove all highlights for speaker. Leave Statement highlights.
                self.show_review('Speaker',1)
                self.question_sel_units('Choose_Speaker','Spr')
                if self.f_questions.Aspliste.size() == 1:
                    self.f_questions.Aspliste.selection_set(0)
                elif self.f_questions.Aspliste.size() == 0:
                    self.middlebutton()
            else:
                self.buttons(0,0,1,1)
                self.question_bt('Dec_Speaker')
                

        elif prog_pos == 's_identity':
            if not dta_pos[1]=='Journ':
                self.buttons()
                self.question_lseek('Spr_ID','Spr_ID')
                if not storage['Medium_Type'] in ['EW','CD']:
                    self.question_dd('A_Prom',2)
                if not 'Spr_ID' in curr().keys():
                    self.cutback_list('Spr_ID',storage[dta_pos[0]][dta_pos[1]]['Wording'],broadseek=1)
                verb('Wording: '+str(storage[dta_pos[0]][dta_pos[1]]['Wording']))
            else:
                prog_pos = 's_pres'
                self.middlebutton()

        elif prog_pos == 's_pres': ##Has to be an if to redirect nonsensical Journalist Identity Codings right here.
            self.buttons()
            if storage['Medium_Type'] == 'TV':
                self.question_dd('A_Pres_TV',1)
                if not dta_pos[1]=='Journ':
                    self.question_dd('Quotation',2)
                self.question_cb('Language',3)
            elif storage['Medium_Type'] in ['EW','CD']:
                self.question_cb('Language',2)
            elif storage['Medium_Type'] == 'Talk':
                if dta_pos[1]=='Journ':
                    def_val['Quotation']='2'
                    self.question_dd('Quotation',2)
                    settings['Page_History'] = settings['Page_History'][:-1] ##Forget this page was ever on.
                    self.submit() ##Pretend the user just submitted.
                else:
                    def_val['Quotation']='2'
                    self.question_dd('Quotation',1)
                    self.question_cb('Language',2)
            else:        
                if not dta_pos[1]=='Journ':
                    self.question_dd('A_Pres',1)
                    self.question_dd('Quotation',2)
                self.question_cb('Language',3)

        elif prog_pos == 's_pres_tv':
            self.buttons()
            self.question_dd('Sp_Situation',1)
            self.question_cb('VSymbol',2)
            

        elif prog_pos == 'statements':
            if settings['Text_Aktiv'] == 1:              
                self.buttons(abort=1)
                self.clean_all_tags(['Iss','Tgt'])
                self.show_review(['Issue','Target'],1)
                self.question_sel_units('Choose_Statement',['Iss','Tgt'])
                self.f_bottomline.b_abort['text']='Next Speaker / End'
                self.f_bottomline.b_abort['bg']=settings['BG_Color']
            else:
                self.buttons(0,0,0,1)
                self.show_review(['Issue','Target'])
                self.question_bt('Dec_Statement',2)        

        elif prog_pos == 'i_identity':
            self.buttons()
            self.question_lseek('Iss_ID','Issuelist',1)
            if storage['Medium_Type'] in ['EW','CD']:
                self.question_cb('Iss_Elab_EW',2)
            else:
                self.question_cb('Iss_Elab',2)

        elif prog_pos == 'i_appdeny':
            self.buttons()
            self.question_dd('Act_Appoint',1)
            self.question_dd('Act_Deny',2)

        elif prog_pos == 'i_position':
            self.buttons()
            if len(codebook['Iss_Central'][2]) > 1:
                self.question_rb('Iss_Central',1)
            else:
                self.question_dd('Iss_Pos',2)
            if not storage['Medium_Type'] in ['EW','CD']:
                if curr()['Iss_Elab']['cons'] == 1:
                    self.question_dd('Iss_Effect',3)

        elif prog_pos == 'i_argument':
            self.buttons()
            if storage['Medium_Type'] in ['EW','CD']:
                self.question_cb('Iss_Just_EW',2)
            else:
                self.question_cb('Iss_Just',2)
                self.question_cb('Argument',3)

        elif prog_pos == 'i_source':
            self.buttons()
            self.question_cb('Sourcing',1)
            if storage['Medium_Type'] in ['EW','CD']:
                self.submit()
        
        elif prog_pos == 'i_style':
            self.buttons()
            if storage['Medium_Type']=='TV':
                self.question_cb('V_Cues',1,'hor')
                
            if storage['Medium_Type'] in ['EW','CD']:
                self.question_cb('Rhetoric_EW',2,'hor3')
            else:
                self.question_cb('Rhetoric',2,'hor3')
                if storage[dta_pos[0]][dta_pos[1]]['Language']['emot'] == 1:
                    self.question_cb('Emot',3,'hor3')

        elif prog_pos == 'e_target':
            self.buttons()
            self.question_dd('Tgt_ID',1)

        elif prog_pos == 'e_spec':
            self.buttons()
            tartype = curr()['Tgt_ID'][1]
            if tartype == 'Volk':
                self.question_dd('Def_Volk',1)
            elif tartype == 'Elit':
                self.question_dd('Def_Elit',1)
            elif tartype == 'SupI':
                self.question_dd('Def_SupI',1)
            elif tartype == 'SPty':
                self.question_dd('Def_SPty',1)
            elif tartype == 'SPer':
                self.question_lseek('Def_SPer','Def_SPer')
                if not 'Def_SPer' in curr().keys():
                    self.cutback_list('Def_SPer',getcaps(storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Wording']),broadseek=1)
            elif tartype == 'MPer':
                self.question_lseek('Def_MPer','All_Actors',1)
            elif tartype == 'ForC':
                self.question_dd('Def_ForC',1)
            elif tartype == 'Othr':
                self.question_txt('Def_Othr',1)
            elif tartype == 'OwnP':
                self.question_dd('Def_OwnP',1)
                self.question_dd('Embod',2)

            if tartype in ['Volk','Eli']:
                if not storage['Medium_Type'] in ['EW','CD']:
                    self.question_dd('Distance',2)

            self.question_dd('Iss_Link',3)

        elif prog_pos == 'e_link':
            self.buttons()
            self.question_lseek('Iss_Link_Other','Issuelist')

        elif prog_pos == 'monolith':
            self.buttons()
            self.question_dd('Monolith',1)

        elif prog_pos == 'agree':
            self.buttons()
            self.question_dd('Agreement',1)
            if not codebook['Iss_Link_Pos'][2] == []:
                self.question_dd('Iss_Link_Pos',2)
            if storage['Medium_Type'] in ['EW','CD']:
                self.submit()
            

        elif prog_pos == 'att_pos':
            self.buttons()
            self.question_rating('Att_Pos',1,['Attri-\nbution','Denial','Not\nMentioned'],['1','-1','9'],defval='9') 

        elif prog_pos == 'att_neg':
            self.buttons()
            self.question_rating('Att_Neg',1,['Attri-\nbution','Denial','Not\nMentioned'],['1','-1','9'],defval='9') 

        elif prog_pos == 'att_impact':
            self.buttons()
            self.question_rating('Att_Impact',1,
                                 ['Attri-\nbution','Denial','Not\nMentioned'],
                                 ['1','-1','9'],defval='9') 
##            self.question_rating('Att_Power',2,
##                                 ['Attri-\nbution','Should\nhave','Should not\nhave',
##                                  'Denial','Not\nMentioned'],
##                                 ['1','2','-2','-1','9'],defval='9')

        elif prog_pos == 'att_power':
            self.buttons()
            self.question_rating('Att_Power',1,
                                 ['Attri-\nbution','Should\nhave','Should not\nhave',
                                  'Denial','Not\nMentioned'],
                                 ['1','2','-2','-1','9'],defval='9') 
            
            
        elif prog_pos == 'att_ppl':
            self.buttons()
            self.question_rating('Att_People',1,['Attri-\nbution','Denial','Not\nMentioned'],['1','-1','9'],defval='9') 

        elif prog_pos == 'att_action':
            self.buttons()
            self.question_rating('Att_Act',1,
                                 ['Attri-\nbution','Should\ndo','Should\nnot do',
                                  'Denial','Not\nMentioned'],
                                 ['1','2','-2','-1','9'],defval='9') 

        elif prog_pos == 'privat':
            self.buttons()
            tartype = curr()['Tgt_ID'][1]
            if tartype == 'SPer':
                self.question_cb('Privat',1)
                self.question_dd('PrivAtt',2)
            elif tartype == 'Volk':
                self.question_dd('Stereo',2)
            self.question_dd('Namecall',3)
            if storage['Medium_Type'] in ['EW','CD']:
                self.submit()


        elif prog_pos == 'a_source':
            self.buttons()
            self.question_cb('Sourcing',1)
            if storage['Medium_Type'] in ['EW','CD']:
                self.submit()
            

        elif prog_pos == 'a_style':
            self.buttons()
            if storage['Medium_Type']=='TV':
                self.question_cb('V_Cues',1,'hor')
            if storage['Medium_Type'] in ['EW','CD']:
                self.question_cb('Rhetoric_EW',2,'hor3')
            else:
                self.question_cb('Rhetoric',2,'hor3')
            if storage[dta_pos[0]][dta_pos[1]]['Language']['emot'] == 1 and not storage['Medium_Type'] in ['EW','CD']:
                self.question_cb('Emot',3,'hor3')

        elif prog_pos == 'last_review':
            self.buttons(0,0,0,1)
            self.show_review('Speaker',1,10)
            self.question_bt('Last_Rev',2)
            self.f_questions.bu2_1['command']=self.submit
            self.f_questions.bu2_2['command']=self.abort

            ####Highlight all text passages
            verb('Highlighting all Units of analysis')
            if settings['Text_Aktiv']==1:             
                if 'Speaker' in storage.keys():
                    for s in storage['Speaker'].keys():
                        verb('-Speaker: '+s)
                        if 'HL_Start' in storage['Speaker'][s].keys():
                            self.Artikel.tag_add('Spr',storage['Speaker'][s]['HL_Start'],storage['Speaker'][s]['HL_End'])
                        if 'Issue' in storage['Speaker'][s].keys():
                            for i in storage['Speaker'][s]['Issue'].keys():
                                verb('---Issue: '+i)
                                if 'HL_Start' in storage['Speaker'][s]['Issue'][i].keys():
                                    self.Artikel.tag_add('Iss',storage['Speaker'][s]['Issue'][i]['HL_Start'],storage['Speaker'][s]['Issue'][i]['HL_End'])
                        if 'Target' in storage['Speaker'][s].keys():
                            for i in storage['Speaker'][s]['Target'].keys():
                                verb('---Target: '+i)
                                if 'HL_Start' in storage['Speaker'][s]['Target'][i].keys():
                                    self.Artikel.tag_add('Tgt',storage['Speaker'][s]['Target'][i]['HL_Start'],storage['Speaker'][s]['Target'][i]['HL_End'])
            #####---------------------------
                                    
        elif prog_pos == 'journ':
            self.buttons(0,0,0,0)
            self.clean_all_tags(['Spr','Iss','Tgt'])
            if settings['Text_Aktiv']==1:
                self.question_bt('Journ_Statement',2)
            elif storage['Medium_Type']=='Talk':
                self.question_bt('Journ_Statement_Talk',2)
            else:
                self.question_bt('Journ_Statement_Notext',2)
                
            self.f_questions.bu2_1['command']=self.submit

        elif prog_pos == 'art_summ':
            self.buttons()
            self.question_txt2('Short_Summary',2)
            if storage['Medium_Type']=='TV':
                self.question_txt('TS_End',1)
           

        elif prog_pos == 'art_frame':
            self.buttons()
            self.question_rating('Frame_HI',1,['No','Present','Dominant'],['0','1','2'],defval='0')
            self.question_rating('Frame_Con',2,['No','Present','Dominant'],['0','1','2'],defval='0')

        elif prog_pos == 'art_frame2':
            self.buttons()
            self.question_rating('Frame_PRF',1,['No','Present','Dominant'],['0','1','2'],defval='0')
            self.question_rating('Frame_Neg',2,['No','Present','Dominant'],['0','1','2'],defval='0')

 
        elif prog_pos == 'final_remarks':
            self.buttons()
            if storage['Discard'] == 1:
                self.question_cb('Discard_Reason',1,'vert')
            elif not storage['Medium_Type'] in ['EW','CD']:
                self.question_rating('CFB_Diff',1,['Very\nEasy','','','','Very\nDifficult'],['1','2','3','4','5'],defval='0')
            self.question_txt2('Bemerkungen',3,60,10)
           
        elif prog_pos == 'otherart':
            self.buttons(0,0,0,1)
            self.ausblenden()

            ##------Automatically generate some variables by counting and transforming existing values
            storage['Codierstart_Lab'] = storage['#TS'][0]
            storage['#TS2'] = (time.ctime(), time.time())
            storage['Session_Text'] = settings['Session_Text']

            self.recode_strategies() ##This function also counts all speakers and statements
            self.recode_styles()
                                    
            ##---------------------------------------------------------


            ##------Export all Data to various Output-Files

##            try:
##                fname = '.\\SNA\\'+settings['Coder']+'_'+storage['ID']+'.graphml'
##                visonout(fname)
##            except:
##                verb('ERROR: Could not output Visone')
                
            if len(settings['Out_Tree'])>0:            
                baum_export(settings['Out_Tree'])

            if len(settings['Out_JSON'])>0:                
                json = str(storage)
                js_out = open(settings['Out_JSON'],'a')
                js_out.write(json)
                js_out.write('\n')
                js_out.close()

            text_var = ['#TS','#TS2','Codierstart_Lab','Medium','Author',
                        'Author_ID','Date','Length','TS_Beginning','TS_End','Images','Position',
                        'Genre','Main_Issue','Frame_HI','Frame_Con',
                        'Frame_PRF','Frame_Neg','Bemerkungen',
                        'Count_Speaker','Count_Issues','Count_ActEval',
                        'STYLE_Negativ','STYLE_Emot',
                        'Fulltext']
            speaker_var = ['#TS','Spr_ID','A_Prom','A_Pres','Quotation','Sp_Situation',
                           'VSymbol','Language','Count_Issues_S','Count_ActEval_S',
                           'STYLE_Colloquial','STYLE_Casual',
                           'Wording','Fulltext']
            issue_var = ['#TS','Spr_ID','Auto_Coding','Iss_ID','Iss_Elab',
                         'Iss_Central','Act_Appoint','Act_Deny','Iss_Pos','Iss_Effect',
                         'Iss_Just','Argument','Sourcing','Rhetoric','V_Cues','Emot',
                         'STYLE_Facts','STYLE_Sense','STYLE_BlackWhite',
                         'STYLE_Sarcasm','STYLE_Drama',
                         'STYLE_EmoTone','Wording','Fulltext']
            target_var = ['#TS','Spr_ID','Auto_Coding','Tgt_ID','Def_Actor',
                          'Def_Volk','Def_Elit','Def_ForC',
                          'Def_MPer','Def_Othr','Def_OwnP','Embod','Monolith',
                          'Distance','Iss_Link','Iss_Link_Pos','Agreement',
                          'Att_Pos','Att_Neg','Att_Impact','Impact_Tgt',
                          'Att_People','Att_Act','Att_Power',
                          'Privat','PrivAtt','Namecall','Stereo',
                          'Sourcing','Rhetoric','V_Cues','Emot',
                          'STYLE_Facts','STYLE_Sense','STYLE_BlackWhite',
                          'STYLE_Sarcasm','STYLE_Drama',
                          'STYLE_EmoTone','STYLE_CommMan',
                          'STYLE_UsThem','STYLE_Privat',
                          'STRAT_ShiftingBlame','STRAT_Closeness',
                          'STRAT_Exclusion','STRAT_Virtues','STRAT_Denouncing',
                          'STRAT_Sovereignty','STRAT_Monolith',
                          'Wording','Fulltext']


            self.export_data([],text_var,'_Text.txt')          
            self.export_data(['Speaker'],speaker_var,'_Speaker.txt')            
            self.export_data(['Speaker','Issue'],issue_var,'_Issue.txt')
            self.export_data(['Speaker','Target'],target_var,'_Target.txt')

            if available('Out_Log'):
                settings['Logging_Info'].append(['DATA STORED',time.time()])


            #Debug-Files
            if settings['Debugging']=='1':
                self.export_data([],text_var,'d_Text.txt',1)  
                self.export_data(['Speaker'],speaker_var,'d_Speaker.txt',1)
                self.export_data(['Speaker','Issue'],issue_var,'d_Issue.txt',1)
                self.export_data(['Speaker','Target'],target_var,'d_Target.txt',1)

            allin_var = text_var + speaker_var[1:] + issue_var[2:] + target_var[3:]
            while 'Fulltext' in allin_var:
                allin_var.remove('Fulltext')
            while 'Wording' in allin_var:
                allin_var.remove('Wording')
            allin_var = allin_var + ['Wording_Spr','Wording_Iss','Wording_Tgt']
            

            try:
                f = florinize(storage, allin_var)
                allin_var = ['Unit_Speaker','Unit_Issue','Unit_Target']+allin_var
                storage['Lowest_Level']={}
                verb('all in one: ',nl=0)
                for fk in f.keys():
                    verb(str(fk),nl=0)
                    storage['Lowest_Level'][str(fk)]=f[fk]
                    storage['Lowest_Level'][str(fk)]['Statement_Nr']=fk
                verb('\n'+str(storage['Lowest_Level'].keys()))
                self.export_data(['Lowest_Level'],allin_var,'_AllIn.txt')         
                if settings['Debugging']=='1':
                    self.export_data(['Lowest_Level'],allin_var,'d_AllIn.txt',1)
            except Exception as fehler:
                err = open('..\\ERROR.txt','a')
                err.write('\n\nNEW ERROR:\n-----------\n')
                err.write(str(time.ctime())+'\n')
                err.write(settings['Coder']+'\n')
                err.write(str(settings['Verb_Log']))


            ##--------------------------------------------------

            ##-----Finalize Todo-List for next article
            verb('Finalizing todo-list')
            try:
                todo_file = open(settings['Todo'],'r')
                todo_list = todo_file.readlines()
                todo_file.close()
                just_done = storage['ID'] + '\n'
                if just_done in todo_list:
                    todo_list.remove(just_done)
                todo_file = open(settings['Todo'],'w')
                for element in todo_list:
                    todo_file.write(element)
                todo_file.close()
                verb('New Todo-List: '+str(todo_list))
                if todo_list == []:
                    verb('End of Todo-List')
            except:
                verb('No ToDo-List')
            ##--------------------------------

            if available('Out_Log'):
                settings['Logging_Info'].append(['PROMPTING Otherart',time.time()])


            if storage['Medium_Type'] in ['TV','Talk']:
                self.question_bt('Otherart_TV',1)
            elif storage['Medium_Type']=='PDF' or storage['ID'][-4:].lower()=='.pdf':
                self.question_bt('Otherart_PDF',1)
            else:
                self.question_bt('Otherart',1)
            self.f_questions.bu1_1.bind('<Return>',self.submit)
            self.f_questions.bu1_1.focus()

            if available('Out_Log'):
                verb('Writing Log-File')
                outlog = open(settings['Out_Log'],'a')
                for page in settings['Logging_Info']:
                    outlog.write(settings['Coder']+'\t')
                    outlog.write(storage['ID']+'\t')
                    outlog.write(str(page[0])+'\t')
                    outlog.write(str(page[1])+'\t')
                    if len(page)>2:
                        outlog.write(str(page[-1])+'\n')
                    else:
                        outlog.write('0\n')
                outlog.close()

            verb('Writing Coder information')
            self.cini_schreiben()        
            
        elif prog_pos == 'ende':
            self.buttons(0,0,0,0)
            self.f_questions.Frage2.insert(INSERT,self.namegetter('Location','End'), 'fett')


        elif prog_pos == 'cfb1':
            self.buttons()
            self.ausblenden()
            self.question_dd('CFB_Lookup',1)
            self.question_sd('CFB_Feel',2)
            self.question_rating('CFB_Fun',3)
            

        elif prog_pos == 'cfb2':
            self.buttons()
            self.question_cb('CFB_Background',1,'vert')
            self.question_rating('CFB_Disturbance',2)

        elif prog_pos == 'cfb3':
            self.buttons()
            self.question_cb('CFB_Breaks',1,'vert')

        elif prog_pos == 'cfb_end':
            self.buttons(0,0,0,0)
            storage['Session_Duration'] = time.time()-settings['Session_Start']
            storage['Finish'] = time.ctime()

            self.export_data([],['Finish','CFB_Lookup','CFB_Feel','CFB_Fun',
                                 'CFB_Background','CFB_Disturbance',
                                 'CFB_Breaks','Session_Duration'],'_cfb.txt')  

            self.f_questions.Frage2.insert(INSERT,self.namegetter('Location','End'), 'fett')
 
          
        else:
            verb('Unknown program position for MCP: ' + prog_pos)
                


############################################
##                                        ##
##       SUBMIT - FUNCTION                ##
##                                        ##
############################################
        
    def submit(self,overspill=0):
        global prog_pos
        global dta_pos
        global settings
        global storage
        global codebook
        log('\nCalling Function: SUBMIT')
        #The Submit-Function takes all entries as soon as the Check-Button is klicked by the user (or any other button directing
        #to this function).
        #All Values are stored to the central dictionary 'storage'. This may be done using the function self.store_var.
        #If any invalid entry was made, the submit-function is not executed. In this case, an error message will be shown to the coder.
        #At the end of storage and cleaning up, a new program position has to be defined and the MCP-function has to be called again.
        #
        #If necessary, the submit-Function will take one argument (overspill) which may be used in the handling of entries.
        #The overspill-parameter will also catch the event when binding a widget-event to the submit function.

        accept_entry = 0 #Only if the entry is valid, acceptance is set to 1
        accept_entry = self.check_entries() #Checking for any invalid entries. Returning 1 if everything is OK

        if accept_entry == 1:
            if available('Out_Log'):
                settings['Logging_Info'][-1].append(time.time()-settings['Logging_Info'][-1][1])

            if prog_pos == 'Art_ID_erfassen':
                entered_id = self.store_var('ID')
                
                if len(entered_id) > 1:
                    fname = settings['Text_Folder'] + entered_id +'.txt'
                    verb('-Loading File: '+fname)
                    settings['Fulltext'] = artikelholen(storage['ID'])
                    storage['Fulltext'] = bereinigen(settings['Fulltext'])
                    settings['PDF-Page'] = os.getcwd()+'\\'+settings['Text_Folder']+storage['ID'][:-4]+'.jpg'
                else:
                    self.message("Runtime-Error03")                

                if settings['Fulltext'] == '':
                    if self.message('Runtime-Error06',3):
                        self.clean_up_all()
                        prog_pos = settings['First_Page']  #Go to the page set as first page of the analysis
                        self.load_countryspec()
                        self.ask()
                else:
                    self.anzeigen(settings['Fulltext'])
                    self.clean_up_all()
                    prog_pos = settings['First_Page']
                    self.load_countryspec()
                    self.ask()
                    
            elif prog_pos == 'test':
                self.store_var_all()
                self.clean_up_all()
                self.ask()

            elif prog_pos == 'change_text':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'artspez1'
                self.ask()


            elif prog_pos == 'artspez1':
                self.store_var_all()
                a = self.store_var('Author',store=0)
                self.clean_up_all()
                if a[1]=='2':
                    prog_pos = 'author'
                else:
                    if a[1]=='1':
                        storage['Author_ID']='9'+storage['Medium'][1]
                    elif a[1]=='3':
                        storage['Author_ID']='99010'
                    elif a[1]=='4':
                        storage['Author_ID']='99004'
                    else:
                        storage['Author_ID']='99999'      
                    prog_pos = 'artspez2'

                verb('--Setting Medium Type: ')
                if storage['Medium'][1] in ['9901','9902']:
                    storage['Medium_Type']='SM'
                    storage['Author'] = '2'
                    storage['Author_ID'] = [storage['ID'][9:14]]
                    storage['Position'] = '99'
                    storage['Genre'] = '7'
                    verb('Set to Social Media')

                elif storage['Medium'][1][-2] == '5':
                    storage['Medium_Type']='PR'
                    storage['Author'] = '2'
                    storage['Position'] = '99'
                    storage['Genre'] = '7'
                    verb('Set to Press Release')

                elif storage['Medium'][-2] == '6':
                    storage['Medium_Type']='PM'
                    storage['Author'] = '2'
                    storage['Position'] = '99'
                    storage['Genre'] = '6'

                elif storage['Medium'][1][-2] == '7':
                    storage['Medium_Type']='TV'
                    verb('Set to TV')

                elif storage['Medium'][1] == '1361':
                    storage['Medium_Type']='EW'
                    storage['Author'] = '2'
                    storage['Genre'] = '6'
                    verb('Set to Edwadrs special kind')

                elif storage['Medium'][1] in ['2401','2402']:
                    storage['Medium_Type']='CD'
                    verb('Set to Regulas special kind')
                elif storage['Medium_Type']=='PDF':
                    verb('PDF already set')
                else:
                    storage['Medium_Type']='Print'
                    verb('Set to Print')

                verb('Are you there?')

                if storage['Medium'][1] in ['1373','1374','1375','1573','1574','1577',
                                         '1773','1774','1873','1874','1875','2273',
                                         '2274','2374','2375','2376']:
                    storage['Medium_Type']='Talk'
                    def_val['Genre_TV']='51'
                    verb('Set to Talkwhow')


                if len(codebook['Spr_ID'][2]) < 2:
                    self.load_countryspec()

                if storage['Medium_Type']=='Print' and settings['Text_Aktiv']==0:
                    storage['Medium_Type']='PDF'
                
                self.ask()


            elif prog_pos == 'author':
                a = self.store_var('Author_ID',store=0,setdef=1)
                if len(a[0]) > 0:                  
                    storage['Author_ID']=(a[0][0],a[1][0])
                    self.clean_up_all()
                    if storage['Medium'][1] in ['9901','9902']:
                        prog_pos = 'artspez3'
                    elif storage['Medium'][1][-2] == '5':
                        prog_pos = 'artspez3'
                    else:
                        prog_pos = 'artspez2'
                    self.ask()
                else:
                    self.message('Invalid-Selection01')

            elif prog_pos == 'artspez2':
                self.store_var_all()
                if 'TS_Beginning' in storage.keys():
                    if len(storage['TS_Beginning']) == 8 and storage['TS_Beginning'][2]==storage['TS_Beginning'][5]:
                        self.clean_up_all()
                        prog_pos = 'artspez3'
                        self.ask()
                    else:
                        self.message('Timestamp Format')
                else:            
                    self.clean_up_all()
                    prog_pos = 'artspez3'
                    self.ask()

            elif prog_pos == 'artspez3':
                self.store_var_all()
                self.clean_up_all()
                if 'Genre_SM' in storage.keys():
                    storage['Genre'] = storage['Genre_SM']
                if 'Genre_PR' in storage.keys():
                    storage['Genre'] = storage['Genre_PR']
                if 'Genre_TV' in storage.keys():
                    storage['Genre'] = storage['Genre_TV']

                if settings['Text_Aktiv']==1:
                    prog_pos = 's_markieren'
                else:
                    prog_pos = 'art_issue'
                self.ask()

            elif prog_pos == 's_markieren':
                self.store_var_all()
                self.clean_up_all()
                #self.unit_confirm('Speaker',['Spr','Iss','Tgt'])   #Storage of text highlights             
                prog_pos = 'art_issue'
                self.ask()

            elif prog_pos == 'art_issue':
                iss = self.store_var('Main_Issue')
                #tex = self.store_var('Other_Issue')
                tex = ''
                if len(iss[0]) > 0:
                    self.clean_up_all()
                    if 'Iss_ID' in def_val.keys():
                        def_val['Iss_ID'] = def_val['Iss_ID'] + iss[1]
                    else:
                        def_val['Iss_ID'] = iss[1]
                    verb('Issue-Coding stored: '+str(def_val['Iss_ID']))


                    if len(iss[0])==1:
                        iss_name = iss[0][0]
                    else:
                        iss_name = ''
                        for il in iss[0]:
                            iss_name = iss_name + il[:25] + ' / '
                        iss_name = iss_name[:-3]
                    codebook['Iss_Link'][2].append(iss_name)
                    codebook['Iss_Link'][3].append(iss[1])

                    if settings['Text_Aktiv']==1:
                        prog_pos = 's_auswahl'
                    else:
                        prog_pos = 'journ'
                    self.ask()

                elif len(tex) > 5:
                    self.clean_up_all()
                    if 'Iss_ID' in def_val.keys():
                        def_val['Iss_ID'] = def_val['Iss_ID'] + [tex[:40]+'...']
                    else:
                        def_val['Iss_ID'] = [tex[:40]+'...']
                    codebook['Issuelist'][2].append(tex[:40]+'...')
                    codebook['Issuelist'][3].append('OTHER')
                    verb('Issue-Coding stored: '+str(def_val['Iss_ID']))

                    codebook['Iss_Link'][2].append(tex[:40]+'...')
                    codebook['Iss_Link'][3].append('OTHER')

                    storage['Main_Issue'] = tex
                    prog_pos = 's_auswahl'                
                    self.ask()
                else:
                    self.message('Invalid-Selection01')

            elif prog_pos == 's_auswahl':
                self.clean_all_tags(['Spr'])
                #self.unit_select('Speaker')
                if self.level_down('Choose_Speaker','Speaker')==1:
                    properties = self.store_var('Choose_Speaker',store=0)
                    self.clean_up_all()
                    storage[dta_pos[0]][dta_pos[1]]['Fulltext'] = properties['Fulltext']
                    storage[dta_pos[0]][dta_pos[1]]['Wording'] = properties['Wording']
                    storage[dta_pos[0]][dta_pos[1]]['Wording_Spr'] = properties['Wording']
                    storage[dta_pos[0]][dta_pos[1]]['HL_Start'] = properties['Start']
                    storage[dta_pos[0]][dta_pos[1]]['HL_End'] = properties['End']
                    prog_pos = 's_identity'
                    self.ask()
                else:
                    self.message('Invalid-Selection01')
                    verb('ERROR: Unable to go down one level')



            elif prog_pos == 'choose_addition':
                o = overspill
                if type(o) == str:
                    if o == 'Add_Spr':
                        #print 'Add Speaker'
                        idlab = 'Spr'
                        idnr = 1
                        ident = idlab + '{0:02}'.format(idnr)
                        while ident in storage['Speaker'].keys():
                            idnr = idnr + 1
                            ident = idlab + '{0:02}'.format(idnr)
                        storage['Speaker'][ident] = {'#TN':'New Speaker','Wording':'', '#TS':time.time()}
                        dta_pos = ['Speaker',ident,'-','-']
                        self.clean_up_all()
                        prog_pos = 's_identity'
                        self.ask()
                elif type(o) == tuple:
                    if o[1] == 'Add_Iss':
                        spr = o[0]
                        if not 'Issue' in storage['Speaker'][spr]:
                            storage['Speaker'][spr]['Issue'] = {}
                        idlab = 'Iss'
                        idnr = 1
                        ident = idlab + '{0:02}'.format(idnr)
                        while ident in storage['Speaker'][spr]['Issue'].keys():
                            idnr = idnr + 1
                            ident = idlab + '{0:02}'.format(idnr)
                        storage['Speaker'][spr]['Issue'][ident] = {'#TN':'New Issue','Wording':'','Fulltext':'', '#TS':time.time()}
                        storage['Speaker'][spr]['Issue'][ident]['Spr_ID']=storage['Speaker'][spr]['Spr_ID']
                        dta_pos = ['Speaker',spr,'Issue',ident,'-','-']
                        self.clean_up_all()
                        prog_pos = 'i_identity'
                        self.ask()
                    elif o[1] == 'Add_Tgt':
                        spr = o[0]
                        if not 'Target' in storage['Speaker'][spr]:
                            storage['Speaker'][spr]['Target'] = {}
                        idlab = 'Tgt'
                        idnr = 1
                        ident = idlab + '{0:02}'.format(idnr)
                        while ident in storage['Speaker'][spr]['Target'].keys():
                            idnr = idnr + 1
                            ident = idlab + '{0:02}'.format(idnr)
                        storage['Speaker'][spr]['Target'][ident] = {'#TN':'New Target Evaluation','Wording':'','Fulltext':'', '#TS':time.time()}
                        storage['Speaker'][spr]['Target'][ident]['Spr_ID']=storage['Speaker'][spr]['Spr_ID']
                        dta_pos = ['Speaker',spr,'Target',ident,'-','-']
                        self.clean_up_all()
                        prog_pos = 'e_target'
                        self.ask()
                    elif o[1] == 'Edit_Spr':
                        spr = o[0]
                        dta_pos = ['Speaker',spr,'-','-']
                        self.clean_up_all()
                        prog_pos = 's_identity'
                        self.ask()
                    elif o[1] == 'Edit_Iss':
                        spr = o[0]
                        iss = o[2]
                        dta_pos = ['Speaker',spr,'Issue',iss,'-','-']
                        self.clean_up_all()
                        prog_pos = 'i_identity'
                        self.ask()
                    elif o[1] == 'Edit_Tgt':
                        spr = o[0]
                        tgt = o[2]
                        dta_pos = ['Speaker',spr,'Target',tgt,'-','-']
                        self.clean_up_all()
                        prog_pos = 'e_target'
                        self.ask()
                    elif o[1] == 'Rem_Spr':
                        spr = o[0]
                        if not spr=='Journ':
                            if self.message('Remove Element',3):
                                del storage['Speaker'][spr]
                                self.clean_up_all()
                                self.ask()
                    elif o[1] == 'Rem_Iss':
                        spr = o[0]
                        iss = o[2]
                        if self.message('Remove Element',3):
                            del storage['Speaker'][spr]['Issue'][iss]
                            self.clean_up_all()
                            self.ask()
                    elif o[1] == 'Rem_Tgt':
                        spr = o[0]
                        tgt = o[2]
                        if self.message('Remove Element',3):
                            del storage['Speaker'][spr]['Target'][tgt]
                            self.clean_up_all()
                            self.ask()
                    else:
                        self.verbout('ERROR: INVALID TUPLE: '+str(o))
                else:
                    self.verbout('ERROR: INVALID OPTION: '+str(o))
                    
                

            elif prog_pos == 's_identity':
                s = self.store_var('Spr_ID',store=0)
                if len(s[0]) > 0:
                    self.store_var_all()
                    self.clean_up_all()
                    if type(storage[dta_pos[0]][dta_pos[1]]['Spr_ID'][1]) == list:
                        t =  (storage[dta_pos[0]][dta_pos[1]]['Spr_ID'][0][0],storage[dta_pos[0]][dta_pos[1]]['Spr_ID'][1][0])
                        storage[dta_pos[0]][dta_pos[1]]['Spr_ID'] = t   
                    settings['Curr_Speaker'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID'][0]
                    storage[dta_pos[0]][dta_pos[1]]['#TN'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID'][0]

                    if 'Other' in storage[dta_pos[0]][dta_pos[1]]['#TN']:
                        markierung = curr()['Wording'][:20]
                        if len(curr()['Wording'])>20: markierung = markierung + '...'
                        storage[dta_pos[0]][dta_pos[1]]['#TN'] = curr()['#TN']+' ('+markierung+')'


                    prog_pos = 's_pres'
                    self.ask()
                else:
                    self.message('Invalid-Selection01')

            elif prog_pos == 's_pres':
                self.store_var_all()
                self.clean_up_all()
                if 'A_Pres_TV' in storage.keys():
                    storage['A_Pres']=storage['A_Pres_TV']

                if settings['Text_Aktiv'] == 1:
                    prog_pos = 'statements'
                else:
                    if not dta_pos[1] == 'Journ':
                        if not 'Target' in storage['Speaker']['Journ'].keys():
                            storage['Speaker']['Journ']['Target'] = {}
                        found = 0
                        for t in storage['Speaker']['Journ']['Target'].keys():
                            sid = storage['Speaker']['Journ']['Target'][t]['Def_Actor']
                            if sid == storage[dta_pos[0]][dta_pos[1]]['Spr_ID']:
                                found = 1
                        if found == 0:
                            slab = 'Tgt_'+dta_pos[1]
                            storage['Speaker']['Journ']['Target'][slab] = self.empty_statement('Target')
                            storage['Speaker']['Journ']['Target'][slab]['#TN'] = storage[dta_pos[0]][dta_pos[1]]['#TN']+' (without attributions)'
                            storage['Speaker']['Journ']['Target'][slab]['Def_Actor'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
                            storage['Speaker']['Journ']['Target'][slab]['Tgt_ID'] = ('Specific person', 'SPer')
                            storage['Speaker']['Journ']['Target'][slab]['Spr_ID'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
                            storage['Speaker']['Journ']['Target'][slab]['Att_Act']['other']='1'
                    if storage['Medium_Type'] == 'TV':
                        prog_pos = 's_pres_tv'
                    else:
                        prog_pos = 'choose_addition'
                self.ask()


            elif prog_pos == 's_pres_tv':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'choose_addition'
                self.ask()


            elif prog_pos=='statements':
                if settings['Text_Aktiv']==1:
                    self.clean_all_tags(['Iss','Tgt'])
                    if self.level_down('Choose_Statement','Statement')==1:
                        properties = self.store_var('Choose_Statement',store=0)
                        self.clean_up_all()
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Fulltext'] = properties['Fulltext']
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Wording'] = properties['Wording']
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['HL_Start'] = properties['Start']
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['HL_End'] = properties['End']

                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Spr_ID']=storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
                        self.clean_up_all()
                        if dta_pos[2]=='Issue':
                            storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Wording_Iss'] = properties['Wording']
                            prog_pos = 'i_identity'
                        elif dta_pos[2]=='Target':
                            storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Wording_Tgt'] = properties['Wording']
                            prog_pos = 'e_target'
                        self.ask()
                    else:
                        self.message('Invalid-Selection01')
                        verb('ERROR: Unable to go down one level')
                else:                                    
                    #Event if issue has been selected
                    if overspill == 1: ##Issue
                        lvl = 'Issue'
                        idn = 'Iss'
                        prog_pos = 'i_identity'
                    elif overspill == 2:
                        lvl = 'Target'
                        idn = 'Tgt'
                        prog_pos = 'e_target'
                    if overspill in [1,2]:
                        self.clean_up_all()
                        if not lvl in storage[dta_pos[0]][dta_pos[1]].keys():
                            storage[dta_pos[0]][dta_pos[1]][lvl]={}
                        idnr = 1
                        ident = idn + "{0:02}".format(idnr)
                        while ident in storage[dta_pos[0]][dta_pos[1]][lvl].keys():
                            idnr = idnr + 1
                            ident = idn + "{0:02}".format(idnr)

                        dta_pos = [dta_pos[0],dta_pos[1],lvl,ident,'-','-']
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]] = {}
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TS']=time.time()
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Spr_ID']=storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']='Statement ('+lvl+')'
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Fulltext']=''
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Wording']=''
                        self.ask()                    
                    else:
                        #No more Statements. The speaker has been coded completely
                        self.clean_up_all()
                        settings[dta_pos[0]][dta_pos[1]]['Done'] = 1
                        ##----Automatically code a blank Actor-Evaluation for the Journalist:
##                        if not dta_pos[1]=='Journ':
##                            if not 'Tmp_Journ_AE' in settings.keys():
##                                settings['Tmp_Journ_AE'] = {}
##                            idnr = len(settings['Tmp_Journ_AE'].keys())+1
##                            aid = 'Speaker'+'{0:02}'.format(idnr)
##                            settings['Tmp_Journ_AE'][aid] = self.empty_statement('Target')
##                            settings['Tmp_Journ_AE'][aid]['#TN'] = storage[dta_pos[0]][dta_pos[1]]['#TN']+' (without attributions)'
##                            settings['Tmp_Journ_AE'][aid]['Def_Actor'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
##                            settings['Tmp_Journ_AE'][aid]['Tgt_ID']=('Specific person', 'SPer')
##                            settings['Tmp_Journ_AE'][aid]['Spr_ID']=('Author of this text', storage['Author_ID'])
##                            settings['Tmp_Journ_AE'][aid]['Att_Act']['other']='1'
##                            if 'Issue' in storage[dta_pos[0]][dta_pos[1]].keys():
##                                if len(storage[dta_pos[0]][dta_pos[1]]['Issue'].keys()) == 1:
##                                    i = storage[dta_pos[0]][dta_pos[1]]['Issue'].keys()[0]
##                                    iss = storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID'][1][0]
##                                    verb('--Automatically assigning one issue to this speaker: '+ str(iss) + ' from: ' + str(storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID']))
##                                    settings['Tmp_Journ_AE'][aid]['Iss_Link'] = ('Automated attribution',iss)
##                                elif len(storage[dta_pos[0]][dta_pos[1]]['Issue'].keys()) > 1:
##                                    settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (self.namegetter('Iss_Link','1'),'1')
##                                else:
##                                    settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (self.namegetter('Iss_Link','0'),'0')
##                            else:
##                                settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (self.namegetter('Iss_Link','0'),'0')
                        ##----------------------------------------------------------------------
                        self.level_up()
                        prog_pos = 's_auswahl'
                        self.ask()

            elif prog_pos == 'i_identity':
                i = self.store_var('Iss_ID',store=0)
                accept = 1
                if len(i[0])==0:
                    self.message('Invalid-Selection01')
                    accept = 0
                for issue in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]].keys():
                    if not issue == dta_pos[3] and not storage['Medium_Type'] in ['EW','CD']:
                        if 'Iss_ID' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][issue].keys():
                            if storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][issue]['Iss_ID'] == i:
                                self.message('Double Issue')
                                accept = 0               
                if accept == 1:
                    self.store_var_all()
                    self.clean_up_all()

                    if 'Iss_Elab_EW' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Elab'] = storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Elab_EW']
                        

                    ###Add this issue to default issues for this text
                    if 'Iss_ID' in def_val.keys():
                        def_val['Iss_ID'] = def_val['Iss_ID'] + i[1]
                    else:
                        def_val['Iss_ID'] = i[1]
                    def_val['Iss_ID'] = get_unique(def_val['Iss_ID'])
                    verb('Issue-Coding stored: '+str(def_val['Iss_ID']))
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN'] = i[0][0]

                    codebook['Iss_Central'][2] = []
                    codebook['Iss_Central'][3] = []
                    for iss in range(len(i[0])):
                        codebook['Iss_Central'][2].append(i[0][iss])
                        codebook['Iss_Central'][3].append(i[1][iss])

                    if len(i[0])==1:
                        iss_code = i[1]
                        iss_name = i[0][0]
                    else:
                        iss_code = i[1]
                        iss_name = ''
##                        for ic in i[1]:
##                            iss_code = iss_code + ic + '/'
##                        iss_code = iss_code[:-1]
                        for il in i[0]:
                            iss_name = iss_name + il[:25] + ' / '
                        iss_name = iss_name[:-3]


                    if not iss_code in codebook['Iss_Link'][3]:         
                        codebook['Iss_Link'][2].append(iss_name)
                        codebook['Iss_Link'][3].append(iss_code)

                    prog_pos = 'i_source'

                    ###Set the Position Variable
                    iss = i[1][0]
                    if iss in codebook.keys():
                        codebook['Iss_Pos'] = codebook[iss]
                        prog_pos = 'i_position'
                    else:
                        codebook['Iss_Pos'] = ''

                    if not storage['Medium_Type'] in ['EW','CD']:
                        if curr()['Iss_Elab']['cons'] == 1:
                            prog_pos = 'i_position'

                    if curr()['Iss_Elab']['power']==1:
                        prog_pos = 'i_appdeny'

                    self.ask()


            elif prog_pos == 'i_appdeny':
                plus = self.store_var('Act_Appoint')
                minus = self.store_var('Act_Deny')
                self.clean_up_all()

                if not plus[1] == '0':
                    ### Add empty targets with power attributions
                    if plus[1] in ['1','9']:
                        tgt = 'Volk'
                        tn = 'The People (No elaboration, just power attribution)'
                    elif plus[1] in ['2','3','4','5','6']:
                        tgt = 'Elit'
                        tn = 'The Elite (No elaboration, just power attribution)'
                    elif plus[1] in ['7','99']:
                        tgt = 'Elit'
                        tn = 'Other (No elaboration, just power attribution)'
                    elif plus[1] in ['8']:
                        tgt = 'SupI'
                        tn = 'Supranational Inst. (No elaboration, just power attribution)'

                    if not 'Target' in storage[dta_pos[0]][dta_pos[1]].keys():
                        storage[dta_pos[0]][dta_pos[1]]['Target'] = {}

                    ilab = 'Tgt_Link'
                    inr = 1
                    ident = ilab + "{0:02}".format(inr)
                    while ident in storage[dta_pos[0]][dta_pos[1]]['Target'].keys():
                        inr = inr + 1
                        ident = ilab + "{0:02}".format(inr)

                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident] = self.empty_statement('Target')
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['#TN'] = tn
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Fulltext'] = curr()['Fulltext']
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Wording'] = curr()['Fulltext']
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Tgt_ID'] = tgt
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Att_Power'] = {'gain':'9','lose':'9','have':'2','limit':'9'}
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Iss_Link'] = ('Automated Link',curr()['Iss_ID'][1][0])                    

                    ###-------------------------------------------

                if not minus[1] == '0':
                    ### Add empty targets with power attributions
                    if minus[1] in ['1','9']:
                        tgt = 'Volk'
                        tn = 'The People (No elaboration, just power attribution)'
                    elif minus[1] in ['2','3','4','5','6']:
                        tgt = 'Elit'
                        tn = 'The Elite (No elaboration, just power attribution)'
                    elif minus[1] in ['7','99']:
                        tgt = 'Elit'
                        tn = 'Other (No elaboration, just power attribution)'
                    elif minus[1] in ['8']:
                        tgt = 'SupI'
                        tn = 'Supranational Inst. (No elaboration, just power attribution)'

                    if not 'Target' in storage[dta_pos[0]][dta_pos[1]].keys():
                        storage[dta_pos[0]][dta_pos[1]]['Target'] = {}

                    ilab = 'Tgt_Link'
                    inr = 1
                    ident = ilab + "{0:02}".format(inr)
                    while ident in storage[dta_pos[0]][dta_pos[1]]['Target'].keys():
                        inr = inr + 1
                        ident = ilab + "{0:02}".format(inr)

                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident] = self.empty_statement('Target')
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['#TN'] = tn
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Fulltext'] = curr()['Fulltext']
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Wording'] = curr()['Fulltext']
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Tgt_ID'] = tgt
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Att_Power'] = {'gain':'9','lose':'9','have':'-2','limit':'9'}
                    storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Iss_Link'] = ('Automated Link',curr()['Iss_ID'][1][0])

                    ###-------------------------------------------
                 
                
                if codebook['Iss_Pos'] == '' and curr()['Iss_Elab']['cons'] == 0:
                    prog_pos = 'i_source'
                else:
                    prog_pos = 'i_position'
                self.ask()
              

            elif prog_pos == 'i_position':
                self.store_var_all()
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Pos'] = self.store_var(pos=1,store=0)
                self.clean_up_all()

                if not 'Iss_Central' in curr().keys():
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Central'] = curr()['Iss_ID'][1][0]


                ### Automatically assign target actors for issue 'Direct Democracy'

                if not 'Act_Appoint' in curr().keys(): #Would make double empty targets otherwise.
                    if curr()['Iss_Central']=='1104' or curr()['Iss_Central'][1] == '1104':
                        tgt = 'Volk'
                        tn = 'People. (No elaboration, no power attribution)'
                        power = {'gain':'9','lose':'9','have':'9','limit':'9'}
                        if curr()['Iss_Pos'][1] == '2':
                            tgt = 'Volk'
                            power = {'gain':'9','lose':'9','have':'2','limit':'9'}
                            tn = 'People. (No elaboration, just power attribution)'
                        elif curr()['Iss_Pos'][1] == '5':
                            tgt = 'Elit'
                            power = {'gain':'9','lose':'9','have':'2','limit':'9'}
                            tn = 'Elite. (No elaboration, just power attribution)'
                        elif curr()['Iss_Pos'][1] == '3':
                            tgt = 'Volk'
                            power = {'gain':'9','lose':'9','have':'-2','limit':'9'}
                            tn = 'People. (No elaboration, not more power attribution)'
                        elif curr()['Iss_Pos'][1] == '4':
                            tgt = 'Elit'
                            power = {'gain':'9','lose':'9','have':'-2','limit':'9'}
                            tn = 'Elite. (No elaboration, not more power attribution)'

                        if not 'Target' in storage[dta_pos[0]][dta_pos[1]].keys():
                            storage[dta_pos[0]][dta_pos[1]]['Target'] = {}

                        ilab = 'Tgt_Link'
                        inr = 1
                        ident = ilab + "{0:02}".format(inr)
                        while ident in storage[dta_pos[0]][dta_pos[1]]['Target'].keys():
                            inr = inr + 1
                            ident = ilab + "{0:02}".format(inr)

                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident] = self.empty_statement('Target')
                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['#TN'] = tn
                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Fulltext'] = curr()['Fulltext']
                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Wording'] = curr()['Fulltext']
                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Tgt_ID'] = tgt
                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Att_Power'] = power
                        storage[dta_pos[0]][dta_pos[1]]['Target'][ident]['Iss_Link'] = ('Automated Link',curr()['Iss_ID'][1][0])

                    ### -------------------------------------------------------------------------

                prog_pos = 'i_source'
                if curr()['Iss_Pos'][1] in ['2','3','4','5','6','7']:
                    prog_pos = 'i_argument'
                if 'Iss_Effect' in curr().keys():
                    if not curr()['Iss_Effect'][1] == '9':                        
                        prog_pos = 'i_argument'
                self.ask()

            elif prog_pos == 'i_argument':
                self.store_var_all()
                if 'Iss_Just_EW' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Just'] = storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Just_EW']

                self.clean_up_all()
                prog_pos = 'i_source'
                self.ask()

            elif prog_pos == 'i_source':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'i_style'
                self.ask()

            elif prog_pos == 'i_style':
                self.store_var_all()
                if 'Rhetoric_EW' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Rhetoric'] = storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Rhetoric_EW']
                self.clean_up_all()

                if not 'Iss_Central' in curr().keys(): ##Security fallback
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Central'] = curr()['Iss_ID'][1][0]

                if settings['Text_Aktiv']==1:
                    try:
                        storage['Highlight']['Iss'][dta_pos[3]]['Done']=1
                    except Exception as fehler:
                        verb('ERROR: Unit could not be marked done. '+str(fehler))
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Auto_Coding']=0
                self.level_up()

                if settings['Text_Aktiv']==1:
                    prog_pos = 'statements'
                else:
                    prog_pos = 'choose_addition'
                self.ask()

##            elif prog_pos == 'i_emot':
##                self.store_var_all()
##                self.clean_up_all()
##                if settings['Text_Aktiv']==1:
##                     storage['Highlight']['Iss'][dta_pos[3]]['Done']=1
##                self.level_up()
##                prog_pos = 'statements'
##                self.ask()

            elif prog_pos == 'e_target':
                a = self.store_var('Tgt_ID')
                self.clean_up_all()
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']=a[0]
                prog_pos = 'e_spec'
                self.ask()

            elif prog_pos == 'e_spec':
                accept = 1
                if curr()['Tgt_ID'][1] == 'SPer':
                    tgt = self.store_var('Def_SPer',store=0)
                    if tgt[0] == []:
                        self.message('Invalid-Selection01')
                        accept = 0
                    else:
                        tgt = (tgt[0][0],tgt[1][0])
                elif curr()['Tgt_ID'][1] == 'SPty':
                    tgt = self.store_var('Def_SPty',store=0)
                elif curr()['Tgt_ID'][1] == 'MPer':
                    tgt = self.store_var('Def_MPer')
                elif curr()['Tgt_ID'][1] == 'SupI':
                    tgt = self.store_var('Def_SupI',store=0)
                elif curr()['Tgt_ID'][1] == 'Elit':
                    tgt = self.store_var('Def_Elit')
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']= 'Elite: '+tgt[0]
                elif curr()['Tgt_ID'][1] == 'Volk':
                    tgt = self.store_var('Def_Volk')
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']= 'People: '+tgt[0][:40]
                elif curr()['Tgt_ID'][1] == 'ForC':
                    tgt = self.store_var('Def_ForC')
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']= 'Foreign: '+tgt[0]
                elif curr()['Tgt_ID'][1] == 'OwnP':
                    tgt = self.store_var('Def_OwnP')
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']= 'Own Person: '+tgt[0]
                elif curr()['Tgt_ID'][1] == 'Othr':
                    tgt = self.store_var('Def_Othr')
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']= 'Other: '+tgt


                if accept == 1:
                    verb('--Checking previously coded instances of: '+str(tgt))
                    for target in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]].keys():
                        verb('----Target: '+str(target))
                        if not target == dta_pos[3]:
                            if 'Def_Actor' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][target].keys():
                                if storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][target]['Def_Actor'][1] == tgt[1]:
                                    if not 'Other' in tgt[0]:
                                        self.message('Double Target')
                                        accept = 0

                if storage['Medium_Type'] in ['EW']:
                    accept = 1

                if accept == 1:
                    self.store_var('Iss_Link')
                    if curr()['Tgt_ID'][1] in ['SPer','SPty','Def_SupI']:
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Def_Actor']=tgt
                        storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN']= tgt[0]
                        if 'Other' in curr()['Def_Actor'][0]:
                            markierung = curr()['Wording'][:20]
                            if len(curr()['Wording'])>20: markierung = markierung + '...'
                            storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN'] = curr()['#TN']+' ('+markierung+')'                      

                    
                    self.clean_up_all()
                    try: ##Linking to issue
                        if not curr()['Iss_Link'][1] in ['0','1','9']:
                            iss = curr()['Iss_Link'][1] ##Issue in list notation
                            iss_nolist = ''
                            if len(iss) == 1:
                                iss_nolist = iss[0]
                            else:
                                for ic in iss:
                                    iss_nolist = iss_nolist + ic + '/'
                                iss_nolist = iss_nolist[:-1]
                            verb('--Looking for Issue in previous codings: '+str(iss))
                            iss_present = 0
                            if 'Issue' in storage[dta_pos[0]][dta_pos[1]].keys():
                                for ci in storage[dta_pos[0]][dta_pos[1]]['Issue'].keys():
                                    verb('----'+str(ci))
                                    if iss == storage[dta_pos[0]][dta_pos[1]]['Issue'][ci]['Iss_ID'][1]:
                                        verb('--Found previous coding of this issue: '+str(ci))
                                        iss_present = 1
                            if iss_present == 0: #Not present in this speaker's statement
                                verb('--Did not find it in the statements of current speaker')
                                ##Create an empty statement on an issue

                                if not 'Issue' in storage[dta_pos[0]][dta_pos[1]].keys():
                                    storage[dta_pos[0]][dta_pos[1]]['Issue'] = {}

                                ilab = 'Iss_Link'
                                inr = 1
                                ident = ilab + "{0:02}".format(inr)
                                while ident in storage[dta_pos[0]][dta_pos[1]]['Issue'].keys():
                                    inr = inr + 1
                                    ident = ilab + "{0:02}".format(inr)

                                storage[dta_pos[0]][dta_pos[1]]['Issue'][ident] = self.empty_statement('Issue')
                                storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['#TN'] = curr()['Iss_Link'][0][:40] + ' (No elaboration. Link to target)'
                                storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Fulltext'] = curr()['Fulltext']
                                storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Wording'] = curr()['Fulltext']
                                storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Iss_ID'] = (curr()['Iss_Link'][0],curr()['Iss_Link'][1])
                                storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Iss_Central'] = iss_nolist
                                     
                                ##-------------------------------------
                            i = iss[0]
                            verb('Looking for positions to issue',str(i))
                            if i in codebook.keys():
                                codebook['Iss_Link_Pos'][2] = codebook[i][2]
                                codebook['Iss_Link_Pos'][3] = codebook[i][3]
                                verb('Found:\n'+str(codebook['Iss_Link_Pos']))
                            else:
                                codebook['Iss_Link_Pos'][2] = []
                        else:
                            codebook['Iss_Link_Pos'][2] = []

                    except Exception as fehler:
                        verb('ERROR: Could not link Target to issue. Error: '+str(fehler))

                    if curr()['Iss_Link'][1] == '9':
                        prog_pos = 'e_link'
                    elif curr()['Tgt_ID'][1] == 'Volk':
                        prog_pos = 'monolith'
                    else:
                        prog_pos = 'agree'

                    self.ask()

            elif prog_pos == 'e_link':
                iss = self.store_var('Iss_Link_Other',store=0)
                if len(iss[1]) > 0:
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Iss_Link'] = (self.namegetter('Iss_Link','9'),iss[1])
                    self.clean_up_all()

                    ##Create an empty statement on an issue

                    if not 'Issue' in storage[dta_pos[0]][dta_pos[1]].keys():
                        storage[dta_pos[0]][dta_pos[1]]['Issue'] = {}
                    create = 1
                    verb('Looking up previously coded issues with this ID...')
                    for i in storage[dta_pos[0]][dta_pos[1]]['Issue'].keys():
                        verb('---'+str(i)+': '+str(storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID']))
                        if storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID'] == iss:
                            verb('Found one. will not create another one')
                            create =0
                    if create == 1:
                        ilab = 'Iss_Link'
                        inr = 1
                        ident = ilab + "{0:02}".format(inr)
                        while ident in storage[dta_pos[0]][dta_pos[1]]['Issue'].keys():
                            inr = inr + 1
                            ident = ilab + "{0:02}".format(inr)

                        storage[dta_pos[0]][dta_pos[1]]['Issue'][ident] = self.empty_statement('Issue')
                        storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['#TN'] = iss[0][0][:40] + ' (No elaboration. Link to target)'
                        storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Fulltext'] = curr()['Fulltext']
                        storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Wording'] = curr()['Fulltext']
                        storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Iss_ID'] = iss
                        storage[dta_pos[0]][dta_pos[1]]['Issue'][ident]['Iss_Central'] = iss[1][0]
                         
                    ##-------------------------------------

                    i = iss[1][0]
                    if i in codebook.keys():
                        codebook['Iss_Link_Pos'][2] = codebook[i][2]
                        codebook['Iss_Link_Pos'][3] = codebook[i][3]
                    else:
                        codebook['Iss_Link_Pos'][2] = []
                        
                    
                    if curr()['Tgt_ID'][1] == 'Volk':
                        prog_pos = 'monolith'
                    else:
                        prog_pos = 'agree'
                    self.ask()
                else:
                    self.message('Invalid-Selection01')

            elif prog_pos == 'monolith':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'agree'
                self.ask()


            elif prog_pos == 'agree':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='att_pos'
                self.ask()

            elif prog_pos == 'att_pos':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='att_neg'
                self.ask()

            elif prog_pos == 'att_neg':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='att_impact'
                self.ask()

            elif prog_pos == 'att_impact':
                self.store_var_all()
                self.clean_up_all()
                if curr()['Tgt_ID'][1] in ['Elit','SupI','SPty','SPer','MPer','OwnP','Othr']:
                    prog_pos='att_ppl'
                else:
                    prog_pos='att_power'

                self.ask()
                
            elif prog_pos == 'att_ppl':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='att_power'
                self.ask()

            elif prog_pos == 'att_power':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='att_action'
                self.ask()

            elif prog_pos == 'att_action':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='privat'
                self.ask()

            elif prog_pos == 'privat':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='a_source'
                self.ask()               

            elif prog_pos == 'a_source':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'a_style'
                self.ask()

            elif prog_pos in 'a_style':
                self.store_var_all()
                if 'Rhetoric_EW' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Rhetoric'] = storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Rhetoric_EW']

                self.clean_up_all()
                if settings['Text_Aktiv']==1:
                    try:
                        storage['Highlight']['Tgt'][dta_pos[3]]['Done']=1
                    except Exception as fehler:
                        verb('ERROR: Unit could not be marked done. '+str(fehler))
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['Auto_Coding']=0
                if '(without attributions)' in curr()['#TN']:
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN'] = curr()['#TN'][:-23]
                self.level_up()

                if settings['Text_Aktiv']==1:
                    prog_pos = 'statements'
                else:
                    prog_pos = 'choose_addition'
                    
                self.ask()               
            
            elif prog_pos == 'last_review':
                self.clean_up_all()
                self.hide_review()
                prog_pos='journ'
                if 'Speaker' in storage.keys():
                    if 'Journ' in storage['Speaker'].keys():
                        if storage['Medium_Type'] in ['SM','PR','EW','CD']:
                            prog_pos = 'final_remarks'
                        else:
                            prog_pos = 'art_frame'
                self.ask()

            elif prog_pos == 'journ':
                self.clean_up_all()
                dta_pos[0]='Speaker'
                dta_pos[1]='Journ'
                if not dta_pos[0] in storage.keys():
                    storage[dta_pos[0]] = {}
                if not dta_pos[1] in storage[dta_pos[0]].keys():
                    storage[dta_pos[0]][dta_pos[1]] = {}
                storage[dta_pos[0]][dta_pos[1]]['Spr_ID'] = storage['Author_ID']
                storage[dta_pos[0]][dta_pos[1]]['#TN'] = 'Author of this text'
                storage[dta_pos[0]][dta_pos[1]]['#TS'] = time.time()
                storage[dta_pos[0]][dta_pos[1]]['Fulltext'] = ''
                storage[dta_pos[0]][dta_pos[1]]['Wording'] = ''
                storage['Highlight']['Spr']['Journ'] = {}
                
                storage[dta_pos[0]][dta_pos[1]]['Target'] = {}

                for speaker in storage['Speaker'].keys():
                    if speaker == 'Journ':
                        sdic = 0
                    elif not 'Spr_ID' in storage['Speaker'][speaker].keys():
                        verb('ERROR: Invalid speaker (will be removed): Speaker '+str(speaker) + ': '+str(storage['Speaker'][speaker]))
                        del storage['Speaker'][speaker]
                    else:
                        sdic = storage['Speaker'][speaker]
                        slab = 'Tgt_'+speaker
                        storage[dta_pos[0]][dta_pos[1]]['Target'][slab] = self.empty_statement('Target')
                        storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['#TN'] = sdic['#TN']+' (without attributions)'
                        storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Def_Actor'] = sdic['Spr_ID']
                        storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Tgt_ID'] = ('Specific person', 'SPer')
                        storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Spr_ID'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
                        storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Att_Act']['other']='1'
                       
                        if 'Issue' in sdic.keys():
                            if len(sdic['Issue'].keys()) == 1:
                                i = sdic['Issue'].keys()[0]
                                iss = sdic['Issue'][i]['Iss_ID'][1][0]
                                verb('--Automatically assigning one issue to this speaker: '+ str(iss) + ' from: ' + str(sdic['Issue'][i]['Iss_ID']))
                                storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Iss_Link'] = ('Automated attribution',iss)
                            elif len(sdic['Issue'].keys()) > 1:
                                storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Iss_Link'] = (self.namegetter('Iss_Link','1'),'1')
                            else:
                                storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Iss_Link'] = (self.namegetter('Iss_Link','0'),'0')
                        else:
                            storage[dta_pos[0]][dta_pos[1]]['Target'][slab]['Iss_Link'] = (self.namegetter('Iss_Link','0'),'0')
                
                settings['Curr_Speaker'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID'][0]
                if type(settings['Curr_Speaker']) == list:
                    settings['Curr_Speaker'] = settings['Curr_Speaker'][0]
                prog_pos = 's_pres'
                self.ask()

            elif prog_pos == 'art_summ':
                self.store_var_all()
                if 'TS_End' in storage.keys():
                    if len(storage['TS_End']) == 8 and storage['TS_End'][2]==storage['TS_End'][5]:
                        self.clean_up_all()
                        prog_pos = 'art_frame'
                        self.ask()
                    else:
                        self.message('Timestamp Format')
                else:            
                    self.clean_up_all()
                    if storage['Medium_Type'] in ['EW','CD','Talk']:
                        prog_pos = 'final_remarks'
                    else:
                        prog_pos = 'art_frame'
                    self.ask()


            elif prog_pos == 'art_frame':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='art_frame2'
                self.ask()

            elif prog_pos == 'art_frame2':
                self.store_var_all()
                self.clean_up_all()
                prog_pos='final_remarks'
                self.ask()

            elif prog_pos == 'final_remarks':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'otherart'
                self.ask()             
        
            elif prog_pos == 'otherart':
                if overspill in [0,1]:
                    self.fuellen()
                if overspill == 2:
                    self.clean_up_all()
                    prog_pos = 'cfb1'
                    self.ask()
                if overspill == 3:
                    newid = self.create_newid(storage['ID'])
                    t = open(settings['Todo'],'r')
                    tl = t.readlines()
                    t.close()
                    tl = [newid+'\n']+tl
                    t2 = open(settings['Todo'],'w')
                    for text in tl:
                        t2.write(text)
                    t2.close()
                    self.fuellen()


            elif prog_pos == 'cfb1':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'cfb2'
                self.ask()             

            elif prog_pos == 'cfb2':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'cfb3'
                self.ask()             

            elif prog_pos == 'cfb3':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'cfb_end'
                self.ask()             



                         
            else:
                verb("Error: The program position '"+prog_pos+"' is not defined for SUBMIT")
        else:
            verb('Invalid Entries')


############################################
##                                        ##
##       Individual Functions             ##
##       for each project                 ##
##                                        ##
############################################

    def create_newid(self,idstring):
        ext = ''
        numb = 0
        if len(idstring)>4:
            if idstring[-4]=='.':
                ext = idstring[-3:]
                idstring = idstring[:-4]
            elif idstring[-3]=='.':
                ext = idstring[-2:]
                idstring = idstring[:-3]

        if len(idstring)>3:
            if idstring[-3]=='-':
                try:
                    numb = int(idstring[-2:])
                    idstring = idstring[:-3]
                except:
                    idstring = idstring

        numb = numb + 1
        try:
            outid = idstring + '-' + "{0:02}".format(numb) + '.' + ext
        except:
            outid = idstring + 'p.' + ext

        return outid


#--------------------------------------------------------- Just for the Populism-Codebook
    def load_countryspec(self):
        global codebook
        global settings
        log('Calling Function: Load_Countryspec')
        tmp_cb = get_codebook('a_actorlist.txt')

        accept = 1

        settings['Country']=storage['ID'][:2]
        verb('--Got the country: '+settings['Country'])

        try:         
            if not storage['Medium_Type'] == 'PDF':
                storage['Medium_Type']='Print'
        except:
            storage['Medium_Type']='Print'
       
        if storage['ID'][:5]=='au_st': storage['Medium']='1101'
        elif storage['ID'][:5]=='au_ps': storage['Medium']='1102'
        elif storage['ID'][:5]=='au_kr': storage['Medium']='1103'
        elif storage['ID'][:5]=='au_he': storage['Medium']='1104'
        elif storage['ID'][:5]=='au_pf': storage['Medium']='1105'
        elif storage['ID'][:5]=='au_ne': storage['Medium']='1106'
        elif storage['ID'][:5]=='au_pr': storage['Medium']='1150'
        elif storage['ID'][:5]=='au_pm': storage['Medium']='1160'
        elif storage['ID'][:5]=='bu_dn': storage['Medium']='1201'
        elif storage['ID'][:5]=='bu_st': storage['Medium']='1202'
        elif storage['ID'][:5]=='bu_tr': storage['Medium']='1203'
        elif storage['ID'][:5]=='bu_ch': storage['Medium']='1204'
        elif storage['ID'][:5]=='bu_ca': storage['Medium']='1205'
        elif storage['ID'][:5]=='bu_at': storage['Medium']='1206'
        elif storage['ID'][:5]=='bu_pr': storage['Medium']='1250'
        elif storage['ID'][:5]=='bu_pm': storage['Medium']='1260'
        elif storage['ID'][:5]=='cd_nz': storage['Medium']='1301'
        elif storage['ID'][:5]=='cd_ta': storage['Medium']='1302'
        elif storage['ID'][:5]=='cd_zm': storage['Medium']='1303'
        elif storage['ID'][:5]=='cd_bl': storage['Medium']='1304'
        elif storage['ID'][:5]=='cd_ww': storage['Medium']='1305'
        elif storage['ID'][:5]=='cd_wo': storage['Medium']='1306'
        elif storage['ID'][:5]=='cd_tz': storage['Medium']='1307'
        elif storage['ID'][:5]=='cd_ws': storage['Medium']='1308'
        elif storage['ID'][:5]=='cd_wz': storage['Medium']='1309'
        elif storage['ID'][:5]=='cd_zo': storage['Medium']='1310'
        elif storage['ID'][:5]=='cd_pr': storage['Medium']='1350'
        elif storage['ID'][:5]=='cd_pm': storage['Medium']='1360'
        elif storage['ID'][:5]=='cf_lt': storage['Medium']='1401'
        elif storage['ID'][:5]=='cf_lm': storage['Medium']='1402'
        elif storage['ID'][:5]=='cf_pr': storage['Medium']='1450'
        elif storage['ID'][:5]=='cf_pm': storage['Medium']='1460'
        elif storage['ID'][:5]=='de_fz': storage['Medium']='1501'
        elif storage['ID'][:5]=='de_sz': storage['Medium']='1502'
        elif storage['ID'][:5]=='de_bi': storage['Medium']='1503'
        elif storage['ID'][:5]=='de_bz': storage['Medium']='1504'
        elif storage['ID'][:5]=='de_sp': storage['Medium']='1505'
        elif storage['ID'][:5]=='de_fo': storage['Medium']='1506'
        elif storage['ID'][:5]=='de_be': storage['Medium']='1507'
        elif storage['ID'][:5]=='de_bk': storage['Medium']='1508'
        elif storage['ID'][:5]=='de_bm': storage['Medium']='1509'
        elif storage['ID'][:5]=='de_ts': storage['Medium']='1510'
        elif storage['ID'][:5]=='de_ma': storage['Medium']='1511'
        elif storage['ID'][:5]=='de_mo': storage['Medium']='1512'
        elif storage['ID'][:5]=='de_pr': storage['Medium']='1550'
        elif storage['ID'][:5]=='de_pm': storage['Medium']='1560'
        elif storage['ID'][:5]=='dk_bt': storage['Medium']='1601'
        elif storage['ID'][:5]=='dk_po': storage['Medium']='1602'
        elif storage['ID'][:5]=='dk_mx': storage['Medium']='1603'
        elif storage['ID'][:5]=='dk_jp': storage['Medium']='1604'
        elif storage['ID'][:5]=='dk_pw': storage['Medium']='1605'
        elif storage['ID'][:5]=='dk_bn': storage['Medium']='1606'
        elif storage['ID'][:5]=='dk_pr': storage['Medium']='1650'
        elif storage['ID'][:5]=='dk_pm': storage['Medium']='1660'
        elif storage['ID'][:5]=='fr_lm': storage['Medium']='1701'
        elif storage['ID'][:5]=='fr_fi': storage['Medium']='1702'
        elif storage['ID'][:5]=='fr_me': storage['Medium']='1703'
        elif storage['ID'][:5]=='fr_vm': storage['Medium']='1704'
        elif storage['ID'][:5]=='fr_ex': storage['Medium']='1705'
        elif storage['ID'][:5]=='fr_no': storage['Medium']='1706'
        elif storage['ID'][:5]=='fr_po': storage['Medium']='1706'
        elif storage['ID'][:5]=='fr_lp': storage['Medium']='1706'
        elif storage['ID'][:5]=='fr_pa': storage['Medium']='1707'
        elif storage['ID'][:5]=='fr_re': storage['Medium']='1708'
        elif storage['ID'][:5]=='fr_pn': storage['Medium']='1709'
        elif storage['ID'][:5]=='fr_pr': storage['Medium']='1750'
        elif storage['ID'][:5]=='fr_pm': storage['Medium']='1760'
        elif storage['ID'][:5]=='it_cs': storage['Medium']='1801'
        elif storage['ID'][:5]=='it_re': storage['Medium']='1802'
        elif storage['ID'][:5]=='it_le': storage['Medium']='1803'
        elif storage['ID'][:5]=='it_me': storage['Medium']='1804'
        elif storage['ID'][:5]=='it_pa': storage['Medium']='1805'
        elif storage['ID'][:5]=='it_es': storage['Medium']='1806'
        elif storage['ID'][:5]=='it_pr': storage['Medium']='1850'
        elif storage['ID'][:5]=='it_pm': storage['Medium']='1860'
        elif storage['ID'][:5]=='nl_vo': storage['Medium']='1901'
        elif storage['ID'][:5]=='nl_nh': storage['Medium']='1902'
        elif storage['ID'][:5]=='nl_te': storage['Medium']='1903'
        elif storage['ID'][:5]=='nl_nt': storage['Medium']='1903' ##NUR FÜR SCHULUNG MAINZ
        elif storage['ID'][:5]=='nl_me': storage['Medium']='1904'
        elif storage['ID'][:5]=='nl_el': storage['Medium']='1905'
        elif storage['ID'][:5]=='nl_es': storage['Medium']='1905'
        elif storage['ID'][:5]=='nl_vn': storage['Medium']='1906'
        elif storage['ID'][:5]=='nl_pr': storage['Medium']='1950'
        elif storage['ID'][:5]=='nl_pm': storage['Medium']='1960'
        elif storage['ID'][:5]=='pl_gw': storage['Medium']='2001'
        elif storage['ID'][:5]=='pl_rz': storage['Medium']='2002'
        elif storage['ID'][:5]=='pl_se': storage['Medium']='2003'
        elif storage['ID'][:5]=='pl_fa': storage['Medium']='2004'
        elif storage['ID'][:5]=='pl_nw': storage['Medium']='2005'
        elif storage['ID'][:5]=='pl_ur': storage['Medium']='2005'
        elif storage['ID'][:5]=='pl_po': storage['Medium']='2006'
        elif storage['ID'][:5]=='se_dn': storage['Medium']='2101'
        elif storage['ID'][:5]=='se_sd': storage['Medium']='2102'
        elif storage['ID'][:5]=='se_ab': storage['Medium']='2103'
        elif storage['ID'][:5]=='se_me': storage['Medium']='2104'
        elif storage['ID'][:5]=='se_av': storage['Medium']='2105'
        elif storage['ID'][:5]=='se_te': storage['Medium']='2106'
        elif storage['ID'][:5]=='se_pr': storage['Medium']='2150'
        elif storage['ID'][:5]=='se_pm': storage['Medium']='2160'
        elif storage['ID'][:5]=='uk_ti': storage['Medium']='2201'
        elif storage['ID'][:5]=='uk_gu': storage['Medium']='2202'
        elif storage['ID'][:5]=='uk_su': storage['Medium']='2203'
        elif storage['ID'][:5]=='uk_dm': storage['Medium']='2204'
        elif storage['ID'][:5]=='uk_sp': storage['Medium']='2205'
        elif storage['ID'][:5]=='uk_ex': storage['Medium']='2206'
        elif storage['ID'][:5]=='uk_am': storage['Medium']='2207'
        elif storage['ID'][:5]=='uk_es': storage['Medium']='2208'
        elif storage['ID'][:5]=='uk_bs': storage['Medium']='2209'
        elif storage['ID'][:5]=='uk_mc': storage['Medium']='2210'
        elif storage['ID'][:5]=='uk_mk': storage['Medium']='2211'
        elif storage['ID'][:5]=='uk_pr': storage['Medium']='2250'
        elif storage['ID'][:5]=='uk_pm': storage['Medium']='2260'
        elif storage['ID'][:5]=='us_nt': storage['Medium']='2301'
        elif storage['ID'][:5]=='us_wp': storage['Medium']='2302'
        elif storage['ID'][:5]=='us_ut': storage['Medium']='2303'
        elif storage['ID'][:5]=='us_me': storage['Medium']='2304'
        elif storage['ID'][:5]=='us_nw': storage['Medium']='2305'
        elif storage['ID'][:5]=='us_ti': storage['Medium']='2306'
        elif storage['ID'][:5]=='us_ny': storage['Medium']='2307'
        elif storage['ID'][:5]=='us_ws': storage['Medium']='2308'
        elif storage['ID'][:5]=='us_nr': storage['Medium']='2309'
        elif storage['ID'][:5]=='gr_ka': storage['Medium']='2401'
        elif storage['ID'][:5]=='gr_tn': storage['Medium']='2402'
        elif storage['ID'][:5]=='pt_pr': storage['Medium']='2650'
        elif storage['ID'][:5]=='es_pr': storage['Medium']='2550'

        ##Social
        
        elif storage['ID'][:5]=='cd_tw': storage['Medium']='9901'
        elif storage['ID'][:5]=='cd_fb': storage['Medium']='9902'
        elif storage['ID'][:5]=='de_tw': storage['Medium']='9901'
        elif storage['ID'][:5]=='de_fb': storage['Medium']='9902'
        elif storage['ID'][:5]=='fr_tw': storage['Medium']='9901'
        elif storage['ID'][:5]=='fr_fb': storage['Medium']='9902'
        elif storage['ID'][:5]=='it_tw': storage['Medium']='9901'
        elif storage['ID'][:5]=='it_fb': storage['Medium']='9902'
        elif storage['ID'][:5]=='uk_tw': storage['Medium']='9901'
        elif storage['ID'][:5]=='uk_fb': storage['Medium']='9902'
        elif storage['ID'][:5]=='us_tw': storage['Medium']='9901'
        elif storage['ID'][:5]=='us_fb': storage['Medium']='9902'

        ##TV

        elif storage['ID'][:5]=='au_zi': storage['Medium']='1171'
        elif storage['ID'][:5]=='au_aa': storage['Medium']='1172'
        elif storage['ID'][:5]=='bu_bn': storage['Medium']='1271'
        elif storage['ID'][:5]=='bu_bt': storage['Medium']='1272'
        elif storage['ID'][:5]=='cd_ts': storage['Medium']='1371'
        elif storage['ID'][:5]=='cd_zz': storage['Medium']='1372'
        elif storage['ID'][:5]=='cd_ar': storage['Medium']='1373'
        elif storage['ID'][:5]=='cd_st': storage['Medium']='1374'
        elif storage['ID'][:5]=='cd_cl': storage['Medium']='1375'
        elif storage['ID'][:5]=='cf_lj': storage['Medium']='1471'
        elif storage['ID'][:5]=='de_ta': storage['Medium']='1571'
        elif storage['ID'][:5]=='de_ra': storage['Medium']='1572'
        elif storage['ID'][:5]=='de_gj': storage['Medium']='1573'
        elif storage['ID'][:5]=='de_mi': storage['Medium']='1574'
        elif storage['ID'][:5]=='de_tt': storage['Medium']='1575'
        elif storage['ID'][:5]=='de_he': storage['Medium']='1576'
        elif storage['ID'][:5]=='de_hf': storage['Medium']='1577'        
        elif storage['ID'][:5]=='fr_lv': storage['Medium']='1771'
        elif storage['ID'][:5]=='fr_jo': storage['Medium']='1772'
        elif storage['ID'][:5]=='fr_lg': storage['Medium']='1773'
        elif storage['ID'][:5]=='fr_gj': storage['Medium']='1774'
        elif storage['ID'][:5]=='it_tu': storage['Medium']='1871'
        elif storage['ID'][:5]=='it_tc': storage['Medium']='1872'
        elif storage['ID'][:5]=='it_ba': storage['Medium']='1873'
        elif storage['ID'][:5]=='it_sp': storage['Medium']='1874'
        elif storage['ID'][:5]=='it_qc': storage['Medium']='1875'
        elif storage['ID'][:5]=='nl_no': storage['Medium']='1971'
        elif storage['ID'][:5]=='nl_rn': storage['Medium']='1972'
        elif storage['ID'][:5]=='nl_hv': storage['Medium']='1973'
        elif storage['ID'][:5]=='pl_fy': storage['Medium']='2071'
        elif storage['ID'][:5]=='pl_wi': storage['Medium']='2072'
        elif storage['ID'][:5]=='se_ra': storage['Medium']='2171'
        elif storage['ID'][:5]=='se_ny': storage['Medium']='2172'
        elif storage['ID'][:5]=='uk_bn': storage['Medium']='2271'
        elif storage['ID'][:5]=='uk_in': storage['Medium']='2272'
        elif storage['ID'][:5]=='uk_ms': storage['Medium']='2273'
        elif storage['ID'][:5]=='uk_qt': storage['Medium']='2274'
        elif storage['ID'][:5]=='us_nn': storage['Medium']='2371'
        elif storage['ID'][:5]=='us_bo': storage['Medium']='2372'
        elif storage['ID'][:5]=='us_nh': storage['Medium']='2373'
        elif storage['ID'][:5]=='us_mp': storage['Medium']='2374'
        elif storage['ID'][:5]=='us_we': storage['Medium']='2375'
        elif storage['ID'][:5]=='us_fn': storage['Medium']='2376'

        ##Online

        elif storage['ID'][:5]=='cd_bo': storage['Medium']='1381'
        elif storage['ID'][:5]=='cd_so': storage['Medium']='1382'
        elif storage['ID'][:5]=='cd_to': storage['Medium']='1383'
        elif storage['ID'][:5]=='cd_zo': storage['Medium']='1384'
        elif storage['ID'][:5]=='de_bo': storage['Medium']='1581'
        elif storage['ID'][:5]=='de_no': storage['Medium']='1582'
        elif storage['ID'][:5]=='de_so': storage['Medium']='1583'
        elif storage['ID'][:5]=='de_to': storage['Medium']='1584'
        elif storage['ID'][:5]=='uk_bo': storage['Medium']='2281'
        elif storage['ID'][:5]=='uk_do': storage['Medium']='2282'
        elif storage['ID'][:5]=='uk_go': storage['Medium']='2283'
        elif storage['ID'][:5]=='uk_to': storage['Medium']='2284'

        ##Edward
        
        elif storage['ID'][:5]=='cd_ew': storage['Medium']='1361'

          
        elif 'Medium' in storage.keys():
            verb('Medium has been set already: '+str(storage['Medium']))
            if storage['Medium'][1][:2] == '11': settings['Country'] = 'au'
            elif storage['Medium'][1][:2] == '12': settings['Country'] = 'bu'
            elif storage['Medium'][1][:2] == '13': settings['Country'] = 'cd'
            elif storage['Medium'][1][:2] == '14': settings['Country'] = 'cf'
            elif storage['Medium'][1][:2] == '15': settings['Country'] = 'de'
            elif storage['Medium'][1][:2] == '16': settings['Country'] = 'dk'
            elif storage['Medium'][1][:2] == '17': settings['Country'] = 'fr'
            elif storage['Medium'][1][:2] == '18': settings['Country'] = 'it'
            elif storage['Medium'][1][:2] == '19': settings['Country'] = 'nl'
            elif storage['Medium'][1][:2] == '20': settings['Country'] = 'pl'
            elif storage['Medium'][1][:2] == '21': settings['Country'] = 'se'
            elif storage['Medium'][1][:2] == '22': settings['Country'] = 'uk'
            elif storage['Medium'][1][:2] == '23': settings['Country'] = 'us'
            elif storage['Medium'][1][:2] == '24': settings['Country'] = 'gr'
            elif storage['Medium'][1][:2] == '25': settings['Country'] = 'es'
            elif storage['Medium'][1][:2] == '26': settings['Country'] = 'pt'
            else:
                verb('ERROR: No known Medium or Country stored in Storage')
                accept = 0
        else:
            storage['Medium']='9999'
            verb('ERROR: No known Medium or Country identified in ID')
            accept = 0

        if storage['Medium'] in ['9901','9902']:
            storage['Medium_Type']='SM'
            storage['Author'] = '2'
            storage['Author_ID'] = [storage['ID'][9:14]]
            storage['Position'] = '99'
            storage['Genre'] = '7'

        if storage['Medium'][-2] == '5':
            storage['Medium_Type']='PR'
            storage['Author'] = '2'
            storage['Position'] = '99'
            storage['Genre'] = '7'
            if len(storage['ID']) == 26:
                storage['Author_ID'] = [storage['ID'][12:17]]

        if storage['Medium'][-2] == '6':
            storage['Medium_Type']='PM'
            storage['Author'] = '2'
            storage['Position'] = '99'
            storage['Genre'] = '6'

        if storage['Medium'][-2] == '7':
            storage['Medium_Type']='TV'

        if storage['Medium'] == '1361':
            storage['Medium_Type']='EW'
            storage['Author'] = '2'
            storage['Genre'] = '6'

        if storage['Medium'] in ['2401','2402']:
            storage['Medium_Type']='CD'

        if storage['Medium'] in ['1373','1374','1375','1573','1574','1577',
                                 '1773','1774','1873','1874','1875','2273',
                                 '2274','2374','2375','2376']:
            storage['Medium_Type']='Talk'



        if '_im_' in storage['ID']:
            settings['Sample']=settings['Country']+'_im'
        elif '_la_' in storage['ID']:
            settings['Sample']=settings['Country']+'_la'
        elif '_db_' in storage['ID']:
            settings['Sample']=settings['Country']+'_db'
        elif '_el_' in storage['ID'] or '_el-' in storage['ID']:
            election_year = storage['ID'][9:11]
            settings['Sample']=settings['Country']+'_el_'+election_year
        elif storage['Medium'] == '1361':
            settings['Sample']='cd_ew'
        else:
            settings['Sample']='XX'
            verb('ERROR: Sample unknown '+storage['ID'])
            accept = 0

        settings['Wordlists']={'bu_la':[],
                               'bu_im':[],
                               'bu_db':[],
                               'dk_la':['løn','arbejdsløshed','strejke','beskæftigelse','erhvervs',
                                        'ledig','fagfor','LO','FTF'],
                               'dk_im':['migra','asyl','flygtning','etnisk','udlændinge',
                                        'opholdstilladelse','burka'],
                               'dk_db':['løn','arbejdsløshed','strejke','beskæftigelse','erhvervs',
                                        'ledig','fagfor','LO','FTF','migra','asyl','flygtning','etnisk',
                                        'udlændinge','opholdstilladelse','burka'],
                               'de_el_13':['CDU','CSU','Merkel','FDP','Grüne','SPD','Linke','Seehofer',
                                           'AfD','Lucke','Steinbrück'],
                               'de_el_02':['CDU','CSU','FDP','Grüne','SPD','Wahl'],
                               'de_el_94':['CDU','CSU','FDP','Grüne','SPD','Wahl'],
                               'de_el_83':['CDU','CSU','FDP','Grüne','SPD','Wahl'],
                               'de_el_72':['CDU','CSU','FDP','Grüne','SPD','Wahl'],
                               'de_la':['Gewerkschaft','arbeitslos','Mindestl','arbeitspl','arbeitsmarkt',
                                        'streik','Hartz','Rentenalter','DGB','Arbeitneh'],
                               'de_im':['asyl','ausländ','einbürger','migra','Roma','rassis',
                                        'Flüchtling','Zuwander'],
                               'de_db':['Gewerkschaft','arbeitslos','Mindestl','arbeitspl','arbeitsmarkt',
                                        'streik','Hartz','Rentenalter','DGB','Arbeitneh',
                                        'asyl','ausländ','einbürger','migra','Roma','rassis',
                                        'Flüchtling','Zuwander'],
                               'uk_la':['trade union','employer','employement','unemploye','minimum wage',
                                        'workforce','labour market','strike','job cuts','jobseeker',
                                        'job market','striver','skiver','tobin tax','Trades Union Congress','TUC'],
                               'uk_im':['foreigne','migra','immigra','deport','racis','racial','refuge','ethnic'],
                               'uk_db':['trade union','employer','employement','unemploye','minimum wage',
                                        'workforce','labour market','strike','job cuts','jobseeker',
                                        'job market','striver','skiver','tobin tax','Trades Union Congress','TUC',
                                        'foreigne','migra','immigra','deport','racis','racial','refuge','ethnic'],
                               'uk_el_74':['Tories','Labour','Conservative','SDP','Liberal'],
                               'uk_el_83':['Tories','Labour','Conservative','SDP','Liberal'],
                               'uk_el_92':['Tories','Labour','Conservative','SDP','Liberal'],
                               'uk_el_01':['Tories','Labour','Conservative','SDP','Liberal'],
                               'uk_el_10':['Tories','Labour','Conservative','SDP','Liberal'],
                               'uk_el_15':['Tories','Labour','Conservative','SDP','Liberal'],
                               'fr_el_11':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist','sarkozy','hollande'],
                               'fr_el_12':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist','sarkozy','hollande'],
                               'fr_el_74':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_73':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_81':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_95':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_93':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_97':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_99':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_el_02':['PS','UMP','EELV','verts','MoDem','Front','Gauche','PG',
                                           'PCF','socialist','centrist','communist'],
                               'fr_la':['FSU','conféderation','chôm','salaire minimum','organisation patronale',
                                        'employés','marché du travail','grève','MEDEF'],
                               'fr_im':['asile','natrualis','migra','migre','burqa','expuls','roms','racis'],
                               'fr_db':['FSU','conféderation','chôm','salaire minimum','organisation patronale',
                                        'employés','marché du travail','grève','MEDEF',
                                        'asile','natrualis','migra','migre','burqa','expuls','roms','racis'],
                               'it_el_01':[],
                               'it_el_13':['PD','PDL','Pdl','Lega','M5S','M5s','SC','SEL','RC',
                                           'Partito','Popolo della','cinque stelle','cinque Stelle',
                                           'Scelta Civica','Sinistra Ecologia','Rivoluzione Civile',
                                           'Monti','Berlusconi','elezione','Grillo'],
                               'it_la':['disoccupa','salario minimo','Confindustria','associazione degli imprenditori',
                                        'tagli della spesa pubblica','tagli al welfare','CGIL'],
                               'it_im':['naturalizza','migr','burka','rom','razzis',
                                        'rifugat','profug','Lampedusa'],
                               'it_db':['disoccupa','salario minimo','Confindustria','associazione degli imprenditori',
                                        'tagli della spesa pubblica','tagli al welfare','CGIL',
                                        'naturalizza','migr','burka','rom','razzis',
                                        'rifugat','profug','Lampedusa'],
                               'nl_la':['vakbond','werkloos','minimumloon','werkgeversorganisatie',
                                        'werkgeversvereniging','brancheorganisatie','ondernemersvereni',
                                        'werkplaats','baanverlies','arbeidsmarkt','FNV','CNV','staking',
                                        'pensioengerechtigde leeftijd','pensioen','economische ontwi'],
                               'nl_im':['asiel','buitenland','vreemdeling','allochtoon',
                                        'migratie','immigratie','racisme','vluchteling',
                                        'voortvluchtig','integratie'],
                               'nl_db':['vakbond','werkloos','minimumloon','werkgeversorganisatie',
                                        'werkgeversvereniging','brancheorganisatie','ondernemersvereni',
                                        'werkplaats','baanverlies','arbeidsmarkt','FNV','CNV','staking',
                                        'pensioengerechtigde leeftijd','pensioen','economische ontwi',
                                        'asiel','buitenland','vreemdeling','allochtoon',
                                        'migratie','immigratie','racisme','vluchteling',
                                        'voortvluchtig','integratie'],
                               'nl_el_12':['VVD','PVV','PvdA','D66','SP','CDA','GL','ARP','KVP','CHU','Partij'],
                               'nl_el_02':['VVD','PVV','PvdA','D66','SP','CDA','GL','ARP','KVP','CHU','Partij'],
                               'nl_el_94':['VVD','PVV','PvdA','D66','SP','CDA','GL','ARP','KVP','CHU','Partij'],
                               'nl_el_82':['VVD','PVV','PvdA','D66','SP','CDA','GL','ARP','KVP','CHU','Partij'],
                               'nl_el_71':['VVD','PVV','PvdA','D66','SP','CDA','GL','ARP','KVP','CHU','Partij'],
                               'nl_el_72':['VVD','PVV','PvdA','D66','SP','CDA','GL','ARP','KVP','CHU','Partij'],
                               'au_el_13':['SPÖ','ÖVP','Grün','Neos','FPÖ','Stronach','TS',
                                           'Sozialdem','Freiheitl','Volkspart'],
                               'au_el_02':['SPÖ','ÖVP','Grün','FPÖ','Sozialdem','Freiheitl','Volkspart'],
                               'au_el_94':['SPÖ','ÖVP','Grün','FPÖ','Sozialdem','Freiheitl','Volkspart'],
                               'au_el_83':['SPÖ','ÖVP','Grün','FPÖ','Sozialdem','Freiheitl','Volkspart'],
                               'au_el_75':['SPÖ','ÖVP','Grün','FPÖ','Sozialdem','Freiheitl','Volkspart'],
                               'au_la':['Gewerkschaft','arbeitslos','mindestl','arbeitspl','arbeitsmarkt',
                                        'streik','Pensionsalter','ÖGB','GÖD'],
                               'au_im':['asyl','ausländ','einbürger','migra','immigra',
                                        'Roma','rassis','flüchtling','zuwander','Burka'],
                               'au_db':['Gewerkschaft','arbeitslos','mindestl','arbeitspl','arbeitsmarkt',
                                        'streik','Pensionsalter','ÖGB','GÖD',
                                        'asyl','ausländ','einbürger','migra','immigra',
                                        'Roma','rassis','flüchtling','zuwander','Burka'],
                               'pl_la':['zawod','zwiazek','lobby','bezrobo','robo','bez pracy','prac',
                                        'wynagrodz','wynagrodzenie minimalne','placa','placa minimalna',
                                        'OR chlebodaw','korpor','zwiaz','stowarz','zajec','zatrud',
                                        'rynek','sila','emeryt','handel','eksport','strajk','podat'],
                               'pl_im':['azyl','obcokraj','cudzoziem','imigra','roma','rasi','uchod',
                                        'emig','wyemig','przyby','migra','deport','etni',
                                        'dyskry','ras','kult'],
                               'pl_db':['zawod','zwiazek','lobby','bezrobo','robo','bez pracy','prac',
                                        'wynagrodz','wynagrodzenie minimalne','placa','placa minimalna',
                                        'OR chlebodaw','korpor','zwiaz','stowarz','zajec','zatrud',
                                        'rynek','sila','emeryt','handel','eksport','strajk','podat',
                                        'azyl','obcokraj','cudzoziem','imigra','roma','rasi','uchod',
                                        'emig','wyemig','przyby','migra','deport','etni',
                                        'dyskry','ras','kult'],
                               'se_la':['fackförening,','landsorganisationen','LO','TCO','SACO','SAC',
                                        'arbetslös','arbetssökand','minimilön','lön','arbetsgivareförening',
                                        'arbetsplats','anställ','social nedrustning','arbetsmarknad',
                                        'pensionsålder','arbetstagar','arbetsgivar'],
                               'se_im':['asyl','utlänn','migra','invandr','roma','rasist','flykting',
                                        'burka','emigr','immigr','ethnie'],
                               'se_db':['fackförening,','landsorganisationen','LO','TCO','SACO','SAC',
                                        'arbetslös','arbetssökand','minimilön','lön','arbetsgivareförening',
                                        'arbetsplats','anställ','social nedrustning','arbetsmarknad',
                                        'pensionsålder','arbetstagar','arbetsgivar',
                                        'asyl','utlänn','migra','invandr','roma','rasist','flykting',
                                        'burka','emigr','immigr','ethnie'],
                               'se_el_14':['Kristdemokrat', 'socialdemokrat', 'miljöpart',
                                           'gröna','vänsterpart','folkpart','liberaler',
                                           'sverigedemokrater','moderater','centerpart'],
                               'se_el_02':['Kristdemokrat', 'socialdemokrat', 'miljöpart',
                                           'gröna','vänsterpart','folkpart','liberaler',
                                           'sverigedemokrater','moderater','centerpart'],
                               'se_el_94':['Kristdemokrat', 'socialdemokrat', 'miljöpart',
                                           'gröna','vänsterpart','folkpart','liberaler',
                                           'sverigedemokrater','moderater','centerpart'],
                               'se_el_82':['Kristdemokrat', 'socialdemokrat', 'miljöpart',
                                           'gröna','vänsterpart','folkpart','liberaler',
                                           'sverigedemokrater','moderater','centerpart'],
                               'se_el_73':['Kristdemokrat', 'socialdemokrat', 'miljöpart',
                                           'gröna','vänsterpart','folkpart','liberaler',
                                           'sverigedemokrater','moderater','centerpart'],
                               'cd_el_75':['SP','SVP','FDP','CVP','GP','Grüne','Grünlib',
                                           'Freisinn','Volkspart','Christdemo','Sozialdemo'],
                               'cd_el_83':['SP','SVP','FDP','CVP','GP','Grüne','Grünlib',
                                           'Freisinn','Volkspart','Christdemo','Sozialdemo'],
                               'cd_el_95':['SP','SVP','FDP','CVP','GP','Grüne','Grünlib',
                                           'Freisinn','Volkspart','Christdemo','Sozialdemo'],
                               'cd_el_03':['SP','SVP','FDP','CVP','GP','Grüne','Grünlib',
                                           'Freisinn','Volkspart','Christdemo','Sozialdemo'],
                               'cd_el_11':['SP','SVP','FDP','CVP','GP','Grüne','Grünlib','BDP',
                                           'Freisinn','Volkspart','Christdemo','Sozialdemo'],
                               'cd_el_15':['SP','SVP','FDP','CVP','GP','Grüne','Grünlib','BDP',
                                           'Freisinn','Volkspart','Christdemo','Sozialdemo'],
                               'cd_la':['Gewerkschaft','arbeitslos','mindestl','arbeitgeberver',
                                        'Economiesuisse','Travailsuisse','arbeitspl','Sozialabbau',
                                        'arbeitsmarkt','Rentenalter','arbeitnehm'],
                               'cd_im':['asyl','ausländ','einbürger','immigra','Roma',
                                        'rassis','flüchtling','auswander','einwander',
                                        'zuwander','migra','personenfreiz','ausschaff',
                                        'multikult','masseneinwand','ecopop'],
                               'cd_db':['Gewerkschaft','arbeitslos','mindestl','arbeitgeberver',
                                        'Economiesuisse','Travailsuisse','arbeitspl','Sozialabbau',
                                        'arbeitsmarkt','Rentenalter','arbeitnehm',
                                        'asyl','ausländ','einbürger','immigra','Roma',
                                        'rassis','flüchtling','auswander','einwander',
                                        'zuwander','migra','personenfreiz','ausschaff',
                                        'multikult','masseneinwand','ecopop'],
                               'cd_ew':[],
                               'cf_la':['FSU','conféderation','chôm','salaire minimum','organisation patronale',
                                        'employés','marché du travail','grève','MEDEF'],
                               'cf_im':['asile','natrualis','migra','migre','burqa','expuls',
                                        'roms','racis'],
                               'us_la':['unemploy','workless','workforce','employer','minimum wage','unions'],
                               'us_im':['migration','foreigner','refugee','ethnic','discrimin',
                                        'green card','racism','immigr','naturaliz'],
                               'us_db':['unemploy','workless','workforce','employer','minimum wage','unions',
                                        'migration','foreigner','refugee','ethnic','discrimin',
                                        'green card','racism','immigr','naturaliz']
                               }
        
        settings['Actorslists']={'bu_la':['Bulgarien_2014','Bulgarien_SPer_2014','Bulgarien_SPty_2014'],
                                 'bu_im':['Bulgarien_2014','Bulgarien_SPer_2014','Bulgarien_SPty_2014'],
                                 'bu_db':['Bulgarien_2014','Bulgarien_SPer_2014','Bulgarien_SPty_2014'],
                                 'dk_la':['Daenemark_2014','Daenemark_SPer_2014','Daenemark_SPty_2014'],
                                 'dk_im':['Daenemark_2014','Daenemark_SPer_2014','Daenemark_SPty_2014'],
                                 'de_el_13':['Deutschland_2013','Deutschland_SPer_2013','Deutschland_SPty_2013'],
                                 'de_el_02':['Deutschland_2002','Deutschland_SPer_2002','Deutschland_SPty_2002'],
                                 'de_el_94':['Deutschland_1994','Deutschland_SPer_1994','Deutschland_SPty_1994'],
                                 'de_el_83':['Deutschland_1983','Deutschland_SPer_1983','Deutschland_SPty_1983'],
                                 'de_el_72':['Deutschland_1972','Deutschland_SPer_1972','Deutschland_SPty_1972'],
                                 'de_la':['Deutschland_2014','Deutschland_SPer_2014','Deutschland_SPty_2014'],
                                 'de_im':['Deutschland_2014','Deutschland_SPer_2014','Deutschland_SPty_2014'],
                                 'de_db':['Deutschland_2014','Deutschland_SPer_2014','Deutschland_SPty_2014'],
                                 'uk_la':['England_2014','England_SPer_2014','England_SPty_2014'],
                                 'uk_im':['England_2014','England_SPer_2014','England_SPty_2014'],
                                 'uk_db':['England_2014','England_SPer_2014','England_SPty_2014'],
                                 'uk_el_83':['England_1983','England_SPer_1983','England_SPty_1983'],
                                 'uk_el_74':['England_1974','England_SPer_1974','England_SPty_1974'],
                                 'uk_el_92':['England_1992','England_SPer_1992','England_SPty_1992'],
                                 'uk_el_01':['England_2001','England_SPer_2001','England_SPty_2001'],
                                 'uk_el_10':['England_2010','England_SPer_2010','England_SPty_2010'],
                                 'uk_el_15':['England_2010','England_SPer_2010','England_SPty_2010'],
                                 'fr_el_11':['Frankreich_2011','Frankreich_SPer_2011','Frankreich_SPty_2011'],
                                 'fr_el_12':['Frankreich_2011','Frankreich_SPer_2011','Frankreich_SPty_2011'],
                                 'fr_el_02':['Frankreich_2002','Frankreich_SPer_2002','Frankreich_SPty_2002'],
                                 'fr_el_99':['Frankreich_1999','Frankreich_SPer_1999','Frankreich_SPty_1999'],
                                 'fr_el_95':['Frankreich_1995','Frankreich_SPer_1995','Frankreich_SPty_1995'],
                                 'fr_el_93':['Frankreich_1995','Frankreich_SPer_1995','Frankreich_SPty_1995'],
                                 'fr_el_97':['Frankreich_1995','Frankreich_SPer_1995','Frankreich_SPty_1995'],
                                 'fr_el_81':['Frankreich_1981','Frankreich_SPer_1981','Frankreich_SPty_1981'],
                                 'fr_el_74':['Frankreich_1974','Frankreich_SPer_1974','Frankreich_SPty_1974'],
                                 'fr_el_73':['Frankreich_1974','Frankreich_SPer_1974','Frankreich_SPty_1974'],
                                 'fr_la':['Frankreich_2014','Frankreich_SPer_2014','Frankreich_SPty_2014'],
                                 'fr_im':['Frankreich_2014','Frankreich_SPer_2014','Frankreich_SPty_2014'],
                                 'fr_db':['Frankreich_2014','Frankreich_SPer_2014','Frankreich_SPty_2014'],
                                 'it_el_01':['Italien_2001','Italien_SPer_2001','Italien_SPty_2001'],
                                 'it_el_13':['Italien_2013','Italien_SPer_2013','Italien_SPty_2013'],
                                 'it_el_94':['Italien_1994','Italien_SPer_1994','Italien_SPty_1994'],
                                 'it_el_83':['Italien_1983','Italien_SPer_1983','Italien_SPty_1983'],
                                 'it_el_72':['Italien_1972','Italien_SPer_1972','Italien_SPty_1972'],
                                 'it_la':['Italien_2014','Italien_SPer_2014','Italien_SPty_2014'],
                                 'it_im':['Italien_2014','Italien_SPer_2014','Italien_SPty_2014'],
                                 'it_db':['Italien_2014','Italien_SPer_2014','Italien_SPty_2014'],
                                 'nl_la':['Niederlande_2014','Niederlande_SPer_2014','Niederlande_SPty_2014'],
                                 'nl_im':['Niederlande_2014','Niederlande_SPer_2014','Niederlande_SPty_2014'],
                                 'nl_db':['Niederlande_2014','Niederlande_SPer_2014','Niederlande_SPty_2014'],
                                 'nl_el_12':['Niederlande_2012','Niederlande_SPer_2012','Niederlande_SPty_2012'],
                                 'nl_el_02':['Niederlande_2002','Niederlande_SPer_2002','Niederlande_SPty_2002'],
                                 'nl_el_94':['Niederlande_1994','Niederlande_SPer_1994','Niederlande_SPty_1994'],
                                 'nl_el_82':['Niederlande_1982','Niederlande_SPer_1982','Niederlande_SPty_1982'],
                                 'nl_el_71':['Niederlande_1972','Niederlande_SPer_1972','Niederlande_SPty_1972'],
                                 'nl_el_72':['Niederlande_1972','Niederlande_SPer_1972','Niederlande_SPty_1972'],
                                 'au_el_13':['Oesterreich_2013','Oesterreich_SPer_2013','Oesterreich_SPty_2013'],
                                 'au_el_02':['Oesterreich_2002','Oesterreich_SPer_2002','Oesterreich_SPty_2002'],
                                 'au_el_94':['Oesterreich_1994','Oesterreich_SPer_1994','Oesterreich_SPty_1994'],
                                 'au_el_83':['Oesterreich_1983','Oesterreich_SPer_1983','Oesterreich_SPty_1983'],
                                 'au_el_75':['Oesterreich_1975','Oesterreich_SPer_1975','Oesterreich_SPty_1975'],
                                 'au_la':['Oesterreich_2014','Oesterreich_SPer_2014','Oesterreich_SPty_2014'],
                                 'au_im':['Oesterreich_2014','Oesterreich_SPer_2014','Oesterreich_SPty_2014'],
                                 'au_db':['Oesterreich_2014','Oesterreich_SPer_2014','Oesterreich_SPty_2014'],
                                 'pl_la':['Polen_2014','Polen_SPer_2014','Polen_SPty_2014'],
                                 'pl_im':['Polen_2014','Polen_SPer_2014','Polen_SPty_2014'],
                                 'pl_db':['Polen_2014','Polen_SPer_2014','Polen_SPty_2014'],
                                 'se_la':['Schweden_2014','Schweden_SPer_2014','Schweden_SPty_2014'],
                                 'se_im':['Schweden_2014','Schweden_SPer_2014','Schweden_SPty_2014'],
                                 'se_db':['Schweden_2014','Schweden_SPer_2014','Schweden_SPty_2014'],
                                 'se_el_14':['Schweden_2014','Schweden_SPer_2014','Schweden_SPty_2014'],
                                 'se_el_02':['Schweden_2002','Schweden_SPer_2002','Schweden_SPty_2002'],
                                 'se_el_94':['Schweden_1994','Schweden_SPer_1994','Schweden_SPty_1994'],
                                 'se_el_82':['Schweden_1982','Schweden_SPer_1982','Schweden_SPty_1982'],
                                 'se_el_73':['Schweden_1973','Schweden_SPer_1973','Schweden_SPty_1973'],
                                 'cd_el_75':['Schweiz_DE_1975','Schweiz_DE_SPer_1975','Schweiz_DE_SPty_1975'],
                                 'cd_el_83':['Schweiz_DE_1983','Schweiz_DE_SPer_1983','Schweiz_DE_SPty_1983'],
                                 'cd_el_95':['Schweiz_DE_1995','Schweiz_DE_SPer_1995','Schweiz_DE_SPty_1995'],
                                 'cd_el_03':['Schweiz_DE_2003','Schweiz_DE_SPer_2003','Schweiz_DE_SPty_2003'],
                                 'cd_el_11':['Schweiz_DE_2011','Schweiz_DE_SPer_2011','Schweiz_DE_SPty_2011'],
                                 'cd_el_15':['Schweiz_DE_2011','Schweiz_DE_SPer_2011','Schweiz_DE_SPty_2011'],
                                 'cd_ew':['Schweiz_DE_Edward Diss 1947-2011','Schweiz_DE_SPer_Edward Diss 1947-2011','Schweiz_DE_SPty_Edward Diss 1947-2011'],
                                 'cd_la':['Schweiz_DE_2014','Schweiz_DE_SPer_2014','Schweiz_DE_SPty_2014'],
                                 'cd_im':['Schweiz_DE_2014','Schweiz_DE_SPer_2014','Schweiz_DE_SPty_2014'],
                                 'cd_db':['Schweiz_DE_2014','Schweiz_DE_SPer_2014','Schweiz_DE_SPty_2014'],
                                 'cf_la':['Schweiz_DE_2014','Schweiz_DE_SPer_2014','Schweiz_DE_SPty_2014'],
                                 'cf_im':['Schweiz_DE_2014','Schweiz_DE_SPer_2014','Schweiz_DE_SPty_2014'],
                                 'cf_db':['Schweiz_DE_2014','Schweiz_DE_SPer_2014','Schweiz_DE_SPty_2014'],
                                 'us_la':['USA_2014','USA_SPer_2014','USA_SPty_2014'],
                                 'us_db':['USA_2014','USA_SPer_2014','USA_SPty_2014'],
                                 'us_im':['USA_2014','USA_SPer_2014','USA_SPty_2014'],
                                 'gr_el_15':['Greece_2015','Greece_SPer_2015','Greece_SPty_2015'],
                                 'es_el_16':['Spain_2015','Spain_SPer_2015','Spain_SPty_2015'],
                                 'pt_el_16':['Portugal_2015','Portugal_SPer_2015','Portugal_SPty_2015']
                                 }

        if not settings['Sample'] in settings['Actorslists'].keys():
            accept = 0
        

        if accept == 1:
            verb('--Got the medium: '+str(storage['Medium'])+' In Country: '+settings['Country'])
            verb('--Sample: '+str(settings['Sample']))
            land = settings['Country']
            try:
                settings['Hotwords']=settings['Wordlists'][settings['Sample']]
            except:
                settings['Hotwords']=[]
            nl = []
            for a in settings['Hotwords']:
                ni = a[0].upper()+a[1:]
                if not ni in settings['Hotwords']:
                    nl.append(ni)
            settings['Hotwords']=settings['Hotwords']+nl
            partylist = settings['Actorslists'][settings['Sample']][2]
            sperslist = settings['Actorslists'][settings['Sample']][1]
            fullist = settings['Actorslists'][settings['Sample']][0]
            interlist = 'International_Function'
            codebook['Spr_ID'][2] = []
            codebook['Spr_ID'][3] = []
            codebook['Def_SPer'][2] = []
            codebook['Def_SPer'][3] = []
            codebook['Def_SPty'][2] = []
            codebook['Def_SPty'][3] = []
            codebook['All_Actors'][2] = []
            codebook['All_Actors'][3] = []
            for i in range(0,len(tmp_cb[fullist][2])):
                codebook['Spr_ID'][2].append(tmp_cb[fullist][2][i]) ##Nicht mehr subjlist
                codebook['Spr_ID'][3].append(tmp_cb[fullist][3][i])
            for i in range(0,len(tmp_cb[sperslist][2])):
                codebook['Def_SPer'][2].append(tmp_cb[sperslist][2][i])
                codebook['Def_SPer'][3].append(tmp_cb[sperslist][3][i])
            for i in range(0,len(tmp_cb[partylist][2])):
                codebook['Def_SPty'][2].append(tmp_cb[partylist][2][i])
                codebook['Def_SPty'][3].append(tmp_cb[partylist][3][i])
            for i in range(0,len(tmp_cb[interlist][2])):
                codebook['Def_SupI'][2].append(tmp_cb[interlist][2][i])
                codebook['Def_SupI'][3].append(tmp_cb[interlist][3][i])
            for i in range(0,len(tmp_cb[fullist][2])):
                codebook['All_Actors'][2].append(tmp_cb[fullist][2][i])
                codebook['All_Actors'][3].append(tmp_cb[fullist][3][i])
            settings['Speakerlist']=self.extract_speakers(tmp_cb[sperslist][2])
        else:
            self.message('Invalid Text')


    def extract_speakers(self,namelist):
        parties = []
        lastnames = []
        for e in namelist:
            if e[-1]==')':
                cut = e.find(',')
                if cut > 0:
                    lastnames.append(e[:cut])
                cut = e.rfind('(')
                if cut > 0:
                    parties.append(e[cut+1:-1])

        fullist = lastnames + get_unique(parties)
        outlist = []
        for e in fullist:
            if not e[0] == ' ' and not e[-1] == ' ':
                outlist.append(e)
        return outlist

    def recode_strategies(self):
        global storage
        global settings
        log('Calling Function: Recode_Strategies')
        storage['Count_Speaker'] = 0
        storage['Count_Issues'] = 0
        storage['Count_ActEval'] = 0
        try:        
            if 'Speaker' in storage.keys():
                for s in storage['Speaker'].keys():
                    verb('-Speaker: '+str(s))
                    storage['Count_Speaker'] = storage['Count_Speaker'] + 1
                    if 'Issue' in storage['Speaker'][s].keys():
                        storage['Speaker'][s]['Count_Issues_S'] = len(storage['Speaker'][s]['Issue'].keys())
                        storage['Count_Issues'] = storage['Count_Issues']+len(storage['Speaker'][s]['Issue'].keys())
                    if 'Target' in storage['Speaker'][s].keys():
                        storage['Speaker'][s]['Count_ActEval_S'] = len(storage['Speaker'][s]['Target'].keys())
                        storage['Count_ActEval'] = storage['Count_ActEval']+len(storage['Speaker'][s]['Target'].keys())
                        for a in storage['Speaker'][s]['Target'].keys():
                            verb('-Target: '+str(a))
                            storage['Speaker'][s]['Target'][a]['STRAT_ShiftingBlame'] = 0
                            storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 0
                            storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 0
                            storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 0
                            storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 0
                            storage['Speaker'][s]['Target'][a]['STRAT_Monolith'] = 0
                            storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = 0
                            if 'Att_Impact' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Att_Impact']['aneg'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_ShiftingBlame'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Impact']['apos'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_ShiftingBlame'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Impact']['aneg'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_ShiftingBlame'] = -1
                                if storage['Speaker'][s]['Target'][a]['Att_Impact']['apos'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_ShiftingBlame'] = -1
                            if 'Att_Power' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Att_Power']['gain'] == '2':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Power']['have'] == '2':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Power']['lose'] == '-2':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Power']['gain'] == '-2':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = -1
                                if storage['Speaker'][s]['Target'][a]['Att_Power']['have'] == '-2':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = -1
                                if storage['Speaker'][s]['Target'][a]['Att_Power']['lose'] == '2':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Sovereignty'] = -1
                            if 'Att_People' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Att_People']['belo'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['clos'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['know'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['care'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['beha'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['belo'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['clos'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['know'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['care'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_People']['beha'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 1
                            if 'Att_Act' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Att_Act']['every'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Closeness'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Act']['every'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Exclusion'] = 1
                            if 'Att_Pos' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['good'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['char'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['comm'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['cred'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['lead'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['cons'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['oth'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Virtues'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['good'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['char'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['comm'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['cred'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['lead'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['cons'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Pos']['oth'] == '-1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                            if 'Att_Neg' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['malev'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['crim'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['lazy'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['stu'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['ext'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['raci'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['unde'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                                if storage['Speaker'][s]['Target'][a]['Att_Neg']['oth'] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Denouncing'] = 1
                            if 'Monolith' in storage['Speaker'][s]['Target'][a].keys():
                                if storage['Speaker'][s]['Target'][a]['Monolith'][1] == '1':
                                    storage['Speaker'][s]['Target'][a]['STRAT_Monolith'] = 1
                            verb('--Berechnet: Shifting Blame: '+str(storage['Speaker'][s]['Target'][a]['STRAT_ShiftingBlame']))
                            verb('--Berechnet: Closeness to the People: '+str(storage['Speaker'][s]['Target'][a]['STRAT_Closeness']))
                            verb('--Berechnet: Exclusuion from the People: '+str(storage['Speaker'][s]['Target'][a]['STRAT_Exclusion']))
                            verb('--Berechnet: Stressing Virtues: '+str(storage['Speaker'][s]['Target'][a]['STRAT_Virtues']))
                            verb('--Berechnet: Denouncing: '+str(storage['Speaker'][s]['Target'][a]['STRAT_Denouncing']))
                            verb('--Berechnet: Monolithic: '+str(storage['Speaker'][s]['Target'][a]['STRAT_Monolith']))
        except:
            verb('ERROR: Could not calculate strategies')

    def recode_styles(self):
        global storage
        global settings
        log('Calling Function: Recode_Styles')
        try:
            storage['STYLE_Negativ'] = 0
            storage['STYLE_Emot'] = 0
            if 'Speaker' in storage.keys():
                for s in storage['Speaker'].keys():
                    verb('-Speaker: '+str(s))
                    storage['Speaker'][s]['STYLE_Colloquial'] = 0
                    storage['Speaker'][s]['STYLE_Casual'] = 0
                    
                    if 'Language' in storage['Speaker'][s].keys():
                        if storage['Speaker'][s]['Language']['emot'] == 1:
                            verb('Found STYLE_Emot')
                            storage['STYLE_Emot']=storage['STYLE_Emot']+1
                        lang = [storage['Speaker'][s]['Language']['vulg'],
                                storage['Speaker'][s]['Language']['slang'],
                                storage['Speaker'][s]['Language']['foreign']]
                        if lang in [[1,1,0],[1,0,0],[0,1,0]]:
                            storage['Speaker'][s]['STYLE_Colloquial'] = 1
                        elif lang == [0,0,1]:
                            storage['Speaker'][s]['STYLE_Colloquial'] = -1
                        else:
                            storage['Speaker'][s]['STYLE_Colloquial'] = 9

                    if 'A_Pres' in storage['Speaker'][s].keys():
                        if storage['Speaker'][s]['A_Pres'][1] in ['1','2','4']:
                            storage['Speaker'][s]['STYLE_Casual'] = 1
                                       
                    for level in ['Issue','Target']:
                        if level in storage['Speaker'][s].keys():
                            for unit in storage['Speaker'][s][level].keys():
                                verb('-'+level+': '+str(unit))
                                
                                storage['Speaker'][s][level][unit]['STYLE_Facts'] = 0
                                storage['Speaker'][s][level][unit]['STYLE_Sense'] = 0
                                storage['Speaker'][s][level][unit]['STYLE_BlackWhite'] = 0
                                storage['Speaker'][s][level][unit]['STYLE_Sarcasm'] = 0
                                storage['Speaker'][s][level][unit]['STYLE_Drama'] = 0
                                storage['Speaker'][s][level][unit]['STYLE_EmoTone'] = 0
                                storage['Speaker'][s][level][unit]['STYLE_CommMan'] = ''
                                storage['Speaker'][s][level][unit]['STYLE_UsThem'] = ''
                                storage['Speaker'][s][level][unit]['STYLE_Privat'] = ''
                                                            
                                if 'Rhetoric' in storage['Speaker'][s][level][unit].keys():
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['emerg'] == 1:
                                        storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                        storage['Speaker'][s][level][unit]['STYLE_Drama'] = 1
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['war'] == 1:
                                        storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                        storage['Speaker'][s][level][unit]['STYLE_Drama'] = 1
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['scand'] == 1:
                                        storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                        storage['Speaker'][s][level][unit]['STYLE_Drama'] = 1
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['abs'] == 1:
                                        storage['Speaker'][s][level][unit]['STYLE_BlackWhite'] = 1
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['imm'] == 1:
                                        storage['Speaker'][s][level][unit]['STYLE_BlackWhite'] = 1
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['sarc'] == 1:
                                        storage['Speaker'][s][level][unit]['STYLE_Sarcasm'] = 1
                                    if storage['Speaker'][s][level][unit]['Rhetoric']['exagg'] == 1:
                                        storage['Speaker'][s][level][unit]['STYLE_Drama'] = 1

                                if 'Emot' in storage['Speaker'][s][level][unit].keys():
                                    negapp = 0
                                    negav = 0
                                    posi = 0
                                    if storage['Speaker'][s][level][unit]['Emot']['anger'] == 1:
                                        negapp = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['contempt'] == 1:
                                        negapp = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['fear'] == 1:
                                        negav = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['fear'] == 1:
                                        negav = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['regret'] == 1:
                                        negapp = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['sadness'] == 1:
                                        negav = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['uneasiness'] == 1:
                                        negav = 1
                                        if s == 'Journ':
                                            storage['STYLE_Negativ'] = storage['STYLE_Negativ']+1
                                    if storage['Speaker'][s][level][unit]['Emot']['affection'] == 1:
                                        posi = 1
                                    if storage['Speaker'][s][level][unit]['Emot']['contentment'] == 1:
                                        posi = 1
                                    if storage['Speaker'][s][level][unit]['Emot']['happiness'] == 1:
                                        posi = 1
                                    if storage['Speaker'][s][level][unit]['Emot']['hope'] == 1:
                                        posi = 1
                                    if storage['Speaker'][s][level][unit]['Emot']['pride'] == 1:
                                        posi = 1
                                    if storage['Speaker'][s][level][unit]['Emot']['hope'] == 1:
                                        posi = 1
                                        
                                    emotionen = [negapp,negav,posi]
                                    if emotionen == [0,0,0]:
                                        storage['Speaker'][s][level][unit]['STYLE_EmoTone'] = 0
                                    elif emotionen == [1,0,0]:
                                        storage['Speaker'][s][level][unit]['STYLE_EmoTone'] = 3
                                    elif emotionen == [0,1,0]:
                                        storage['Speaker'][s][level][unit]['STYLE_EmoTone'] = 2
                                    elif emotionen == [0,0,1]:
                                        storage['Speaker'][s][level][unit]['STYLE_EmoTone'] = 1
                                    else:
                                        storage['Speaker'][s][level][unit]['STYLE_EmoTone'] = 4
                                                                            
                                if 'Sourcing' in storage['Speaker'][s][level][unit].keys():
                                    for quelle in storage['Speaker'][s][level][unit]['Sourcing'].keys():
                                        if quelle in ['2','3','4'] and storage['Speaker'][s][level][unit]['Sourcing'][quelle] == 1:
                                            storage['Speaker'][s][level][unit]['STYLE_Facts'] = 1

                                if 'Iss_Just' in storage['Speaker'][s][level][unit].keys():
                                    if storage['Speaker'][s][level][unit]['Iss_Just']['Comm'] == 1:
                                        storage['Speaker'][s][level][unit]['STYLE_Sense'] = 1

                                if 'Def_Volk' in storage['Speaker'][s][level][unit].keys():
                                    storage['Speaker'][s][level][unit]['STYLE_CommMan'] = 0
                                    if storage['Speaker'][s][level][unit]['Def_Volk'][1] == '4':
                                        storage['Speaker'][s][level][unit]['STYLE_CommMan'] = 1

                                if 'Distance' in storage['Speaker'][s][level][unit].keys():
                                    if storage['Speaker'][s][level][unit]['Distance'][1] == '1':
                                        storage['Speaker'][s][level][unit]['STYLE_UsThem'] = 1
                                    else:
                                        storage['Speaker'][s][level][unit]['STYLE_UsThem'] = 2

                                if 'Privat' in storage['Speaker'][s][level][unit].keys():
                                    if storage['Speaker'][s][level][unit]['STYLE_Privat'] == '':
                                        storage['Speaker'][s][level][unit]['STYLE_Privat'] = 0
                                    for k in storage['Speaker'][s][level][unit]['Privat'].keys():
                                        if storage['Speaker'][s][level][unit]['Privat'][k] == 1:
                                            storage['Speaker'][s][level][unit]['STYLE_Privat'] = 1
                                if 'PrivAtt' in storage['Speaker'][s][level][unit].keys():
                                    if storage['Speaker'][s][level][unit]['STYLE_Privat'] == '':
                                        storage['Speaker'][s][level][unit]['STYLE_Privat'] = 0
                                    if storage['Speaker'][s][level][unit]['PrivAtt'][1] == '1':
                                        storage['Speaker'][s][level][unit]['STYLE_Privat'] = 1
                                if 'Namecall' in storage['Speaker'][s][level][unit].keys():
                                    if storage['Speaker'][s][level][unit]['STYLE_Privat'] == '':
                                        storage['Speaker'][s][level][unit]['STYLE_Privat'] = 0
                                    if storage['Speaker'][s][level][unit]['Namecall'][1] in ['1','2','-1']:
                                        storage['Speaker'][s][level][unit]['STYLE_Privat'] = 1
                                                                        
                                verb('----Calculated: STYLE_Facts: '+str(storage['Speaker'][s][level][unit]['STYLE_Facts']))
                                verb('----Calculated: STYLE_Sense: '+str(storage['Speaker'][s][level][unit]['STYLE_Sense']))
                                verb('----Calculated: STYLE_BlackWhite: '+str(storage['Speaker'][s][level][unit]['STYLE_BlackWhite']))
                                verb('----Calculated: STYLE_Sarcasm: '+str(storage['Speaker'][s][level][unit]['STYLE_Sarcasm']))
                                verb('----Calculated: STYLE_Drama: '+str(storage['Speaker'][s][level][unit]['STYLE_Drama']))
                                verb('----Calculated: STYLE_EmoTone: '+str(storage['Speaker'][s][level][unit]['STYLE_EmoTone']))
                                verb('----Calculated: STYLE_CommMan: '+str(storage['Speaker'][s][level][unit]['STYLE_CommMan']))
                                verb('----Calculated: STYLE_UsThem: '+str(storage['Speaker'][s][level][unit]['STYLE_UsThem']))
                                verb('----Calculated: STYLE_Privat: '+str(storage['Speaker'][s][level][unit]['STYLE_Privat']))
                                
                    verb('\n---Calculated: STYLE_Colloquial: '+str(storage['Speaker'][s]['STYLE_Colloquial']))
                    verb('---Calculated: STYLE_Casual: '+str(storage['Speaker'][s]['STYLE_Casual']))
                    
            verb('\n--Calculated: Negativity: '+str(storage['STYLE_Negativ']))
            verb('--Calculated: Emotionalization: '+str(storage['STYLE_Emot']))
            
        except Exception as fehler:
            verb('ERROR: Could not calculate Styles. The error was: '+str(fehler))


    def empty_statement(self,styp='Issue'):
        outdic = {}
        if styp == 'Issue':
            outdic = {'Fulltext': '', '#TS': time.time(),
                      'Rhetoric': {'exagg': 0, 'scand': 0, 'sarc': 0,
                                   'imm': 0, 'quest': 0, 'abs': 0, 'patri': 0,
                                   'war': 0, 'emerg': 0},
                      'Sourcing': {'99': 0, '1': 0, '3': 0, '2': 0, '5': 0,
                                   '4': 0, '7': 0, '6': 0, '9': 0, '8': 0},
                      'Iss_Elab': {'cons': 0, 'power': 0, 'cas': 0, 'resp': 0,
                                   'dev': 0, 'caus': 0, 'treat': 0, 'prob': 0},
                      'Wording':'', 'Wording_Iss':'',
                      'Spr_ID':storage[dta_pos[0]][dta_pos[1]]['Spr_ID'],
                      'Auto_Coding':1}
        elif styp == 'Target':
            outdic = {'Tgt_ID': ('Other actor or organization', 'Othr'),
                      'Def_Othr': 'Automated',
                      'Agreement': '0',
                      'Att_Power': {'limit': '9', 'gain': '9',
                                    'have': '9', 'lose': '9'},
                      'Att_Impact': {'burd': '9', 'aneg': '9', 'thre': '9',
                                     'apos': '9', 'abil': '9', 'enri': '9'},
                      'Fulltext': '', 'Wording': '',
                      'Rhetoric': {'exagg': 0, 'scand': 0, 'sarc': 0,
                                   'imm': 0, 'quest': 0, 'abs': 0,
                                   'patri': 0, 'war': 0, 'emerg': 0},
                      'Wording_Tgt': '',
                      'Att_Pos': {'oth': '9', 'cons': '9', 'lead': '9',
                                  'char': '9', 'good': '9', 'comm': '9',
                                  'cred': '9'},
                      'Att_Neg': {'oth': '9', 'crim': '9', 'lazy': '9',
                                  'right': '9', 'pop': '9', 'stu': '9',
                                  'malev': '9', 'left': '9', 'ext':'9',
                                  'raci':'9', 'unde':'9'},
                      'Sourcing': {'99': 0, '1': 0, '3': 0, '2': 0, '5': 0,
                                   '4': 0, '7': 0, '6': 0, '9': 0, '8': 0},
                      '#TS': time.time(),'Auto_Coding':1,
                      'Att_Act': {'symb': '9', 'right': '9', 'immo': '9',
                                  'crim': '9', 'prom': '9', 'other': '9',
                                  'every': '9', 'dem': '9', 'mist': '9',
                                  'plan': '9'},
                      'Spr_ID':storage[dta_pos[0]][dta_pos[1]]['Spr_ID']}
        else:
            verb('ERROR: No such type of statement')

        return outdic
        

#---------------------------------------------------------
        
    def abort(self):
        #This function is called by the abort-button. For each page on which the abort-button is enabled
        #this function has to be defined.
        #The abort-function may also be called by other buttons such as questions defined in the MCP function      
        global prog_pos
        global dta_pos
        log('Calling Function: Abort')
        if available('Out_Log'):
            settings['Logging_Info'][-1].append(time.time()-settings['Logging_Info'][-1][1])

        if prog_pos in ['otherart','art_otherart']:
            self.clean_up_all()
            prog_pos = 'cfb1'
            self.ask()
        elif prog_pos in ['art_issue','artspez1']:
            if self.message('Caution02',3)==1:
                self.clean_up_all()
                storage['Bemerkungen']='Does not belong to the sample'
                storage['Discard'] = 1
                prog_pos = 'final_remarks'
                self.ask()
        elif prog_pos == 'statements':
            if settings['Text_Aktiv']==1:
                storage['Highlight']['Spr'][dta_pos[1]]['Done']=1
            self.clean_up_all()

            ##----Automatically code a blank Actor-Evaluation for the Journalist:
##            if not dta_pos[1]=='Journ':
##                if not 'Tmp_Journ_AE' in settings.keys():
##                    settings['Tmp_Journ_AE'] = {}
##                idnr = len(settings['Tmp_Journ_AE'].keys())+1
##                aid = 'Speaker'+'{0:02}'.format(idnr)
##                settings['Tmp_Journ_AE'][aid] = self.empty_statement('Target')
##                settings['Tmp_Journ_AE'][aid]['#TN'] = storage[dta_pos[0]][dta_pos[1]]['#TN']+' (without attributions)'
##                settings['Tmp_Journ_AE'][aid]['Def_Actor'] = storage[dta_pos[0]][dta_pos[1]]['Spr_ID']
##                settings['Tmp_Journ_AE'][aid]['Tgt_ID']=('Specific person', 'SPer')
##                settings['Tmp_Journ_AE'][aid]['Spr_ID']=('Author of this text', storage['Author_ID'])
##                settings['Tmp_Journ_AE'][aid]['Att_Act']['other']='1'
##                if 'Issue' in storage[dta_pos[0]][dta_pos[1]].keys():
##                    if len(storage[dta_pos[0]][dta_pos[1]]['Issue'].keys()) == 1:
##                        i = storage[dta_pos[0]][dta_pos[1]]['Issue'].keys()[0]
##                        iss = storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID'][1]
##                        ilb = self.namegetter('Iss_Link',iss)
##                        #ilb = storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID'][0][0]
##                        verb('--Automatically assigning one issue to this speaker: '+ str(iss) + ' from: ' + str(storage[dta_pos[0]][dta_pos[1]]['Issue'][i]['Iss_ID']))
##                        settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (ilb,iss)
##                    elif len(storage[dta_pos[0]][dta_pos[1]]['Issue'].keys()) > 1:
##                        settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (self.namegetter('Iss_Link','1'),'1')
##                    else:
##                        settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (self.namegetter('Iss_Link','0'),'0')
##                else:
##                    settings['Tmp_Journ_AE'][aid]['Iss_Link'] = (self.namegetter('Iss_Link','0'),'0')
            ##----------------------------------------------------------------------

            self.level_up()
            prog_pos = 's_auswahl'
            self.ask()
            
        elif prog_pos == 'choose_addition':
            self.clean_up_all()
            prog_pos = 'art_summ'
            self.ask()

        elif prog_pos == 'last_review':
            self.clean_up_all()
            self.hide_review()
            self.clean_all_tags(['Spr','Iss','Tgt']) ###Remove the Highlight-Review
            self.f_questions.Frage2.delete('1.0',END)
            prog_pos = 's_markieren'
            self.ask()
            
        else:
            verb('ERROR: Abort function not defined for this page')


    def back(self):
        #This function is called by the back-button. For each page on which the back-button is enabled
        #this function has to be defined. The standard definition (go back one page) is default for all pages.
        #In some cases, this default will not hold, however, as parts of the data structure also has to
        #be changed. For example, the data level (data_pos) has to be changed or some entry has to be
        #deleted when going back from certain pages. In these cases a manual definition must be provided
        #in order to prevent errors.
        global prog_pos
        global dta_pos
        log('Calling Function: Back')

        if len(settings['Out_Track']) > 0:
            tf = open(settings['Out_Track'], 'a')
            tf.write('back-button\n')
            tf.close()

        storage['Backs'] = storage['Backs'] + 1
        
        if len(settings['Page_History']) > 1:
            if prog_pos in ['s_identity']: ## Jumping back from the coding of a speaker
##                if settings['Text_Aktiv']==1:
##                    del storage[dta_pos[0]][dta_pos[1]]
##                    if len(storage[dta_pos[0]].keys()) == 0:
##                        del storage[dta_pos[0]]
##                    verb('--Removed the current speaker from storage')                
                self.level_up()
                prog_pos = 's_auswahl'
            elif prog_pos == 's_pres' and dta_pos[1] == 'Journ': ## Jumping back from the coding of a speaker
                self.level_up()
                if settings['Text_Aktiv']==1:
                    prog_pos = 'last_review'
                else:
                    prog_pos = 'choose_addition'
            elif prog_pos in ['i_identity','e_target']: #Jumping back out of a statement
                l = len(storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys())
                verb('Aborted statement had: '+str(l)+' Keys')
                if l < 12:
                    del storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]
                    verb('--Removed the current statement from storage')
                    
##                if settings['Text_Aktiv']==1:
##                    del storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]
##                    if len(storage[dta_pos[0]][dta_pos[1]][dta_pos[2]].keys()) == 0:
##                        del storage[dta_pos[0]][dta_pos[1]][dta_pos[2]]
##                    verb('--Removed the current statement from storage')
                else:
                    self.message('Caution05')
                self.level_up()
                if settings['Text_Aktiv']==1:
                    prog_pos = 'statements'
                else:
                    prog_pos = 'choose_addition'
            elif prog_pos == 'agree':
                if settings['Page_History'][len(settings['Page_History'])-2] in ['statements','choose_addition']:
                    self.level_up()
                    prog_pos = settings['Page_History'][len(settings['Page_History'])-2]
            elif prog_pos == 'last_review': ## Jumping back on the review-page
                prog_pos = 's_auswahl'
            else:
                prog_pos = settings['Page_History'][len(settings['Page_History'])-2] #Go back one step

            self.clean_up_all()
            settings['Page_History'].pop(len(settings['Page_History'])-1) #remove the two most recent pages in history.
            settings['Page_History'].pop(len(settings['Page_History'])-1)
            self.hide_review()
            self.ask()
        else:
            if self.message('Caution01',3) == 1: #Warning when trying to go back to the very beginning.
                self.fuellen() #Delete everyting on this text and start anew

    def middlebutton(self):
        #This is just a function which may be called by any third button of Button-Questions. It works the
        #same way as back and abort
        global prog_pos
        global dta_pos
        log('Calling Function: Middlebutton on position '+prog_pos)

        if prog_pos == 's_auswahl':
            verb('--No more speakers in your list. Proceeding to last Review')
            self.clean_up_all()
            prog_pos = 'last_review'
            self.ask()
        elif prog_pos == 's_pres':
            self.ask()


        else:
            verb('Error: Middlebutton not defined for this page')


    def rb_tamper(self):
        #This function will be called whenever the value of a Radiobutton is changed. It may be used to
        #Change the display according to the current selection.
        #This function has to be defined for all pages on which it is needed.  
        global prog_pos
        log('Calling Function: RB-Tamper')

        if prog_pos == 'att_ppl':
            try:
                self.clean_up('dd',2)
            except:
                verb('nothing to remove')
            rbpos = self.store_var('Att_People',store=0)
            ppl = 0
            for r in rbpos.keys():
                if rbpos[r] in ['1','-1']:
                    ppl = 1
                    verb('People mentioned in: '+r)
            if ppl == 1:
                self.question_dd('Monolith',2)
            else:
                verb('No people')
                
        elif prog_pos == 'att_impact':
            try:
                self.clean_up('dd',3)
            except:
                verb('nothing to remove')
            rbpos = self.store_var('Att_Impact',store=0)
            imp = 0
            for crit in ['thre','burd','enri']:
                if crit in rbpos.keys():
                    if rbpos[crit] in ['1','-1']:
                        imp=1
                        verb('Threat, Burden or Enrichment')
            if imp == 1:
                self.question_dd('Impact_Tgt',3)
            else:
                verb('No Threat, Burden, or Enrichment')
            
        elif prog_pos == 'i_position':
            self.clean_up('dd',2)
            #codebuch['Iss_Pos'] = codebuch[settings['Input'][0].get()]
            if settings['Input'][0].get() in codebook.keys():
                self.question_dd(settings['Input'][0].get(),2)
        else:
            verb('ERROR: RB-Tamper not defined for this page.')             

            
############################################
##                                        ##
##       Question-Functions               ##
##                                        ##
############################################


    def question_dd(self, cb_var, question_pos,width=40): #Dropdown-Question: Up to three dropdown selections may be displayed per page
        global settings
        log('--Question: Dropdown. Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        #### Setting the default value according to text statistics using AEGLOS:
        if settings['AEGLOS'] == '1':
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'])
            wert = self.namegetter(cb_var,pred)
            if not wert == '':
                if not cb_var in def_val.keys():
                    def_val[cb_var] = wert
                    if settings['Verbose'] == '1':
                        verb('Automated determination of the value')
                        verb('Best prediction: '+str(pred)+' Value: '+str(wert))
                else:
                    if settings['Verbose'] == '1': verb('Another default value has been set already. No changes made')

        settings['Curr_Page'][question_pos-1] = ['dd',cb_var]
        settings['Input'][question_pos-1] = ''
        curr_tree=curr()

        verb('Looking for previously set values..')
        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = '' ###Has to have the same data type as set default values or previous codings

        if type(previous_coding) == tuple:
            previous_coding = previous_coding[0]
        elif type(previous_coding) == str:
            if len(self.namegetter(cb_var,previous_coding)) >0:
                previous_coding = self.namegetter(cb_var,previous_coding)
            elif previous_coding in codebook[cb_var][2]:
                previous_coding = str(previous_coding)
            else:
                previous_coding = ''
                verb('No valid coding found')
        else:
            previous_coding = ''
            verb('No valid coding found')

        namelist = codebook[cb_var][2]
        codelist = codebook[cb_var][3]
         
        settings['Input'][question_pos-1] = StringVar()
        if previous_coding == '':
            settings['Input'][question_pos-1].set(namelist[0])
        else:
            settings['Input'][question_pos-1].set(previous_coding)

        if question_pos == 1:
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Display question
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Display additional information
            #Display dropdown
            self.f_questions.dd1 = apply(OptionMenu, (self.f_questions, settings['Input'][question_pos-1]) + tuple(namelist))
            self.f_questions.dd1["width"] = width
            self.f_questions.dd1["takefocus"] = 1
            self.f_questions.dd1.grid(row=3, column=1, sticky=W+E)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            if settings['Insecure']=='1':
                self.f_questions.ins1 = Label(self.f_questions, text="unsich.",fg="#ee0000")
                self.f_questions.ins1.grid(row=4, column=3, sticky=E)
                self.f_questions.ins1.bind('<Button-1>', CMD(self.insecure, cb_var))               
        if question_pos == 2:
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Display question
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Display additional information
            #Display Dropdown
            self.f_questions.dd2 = apply(OptionMenu, (self.f_questions, settings['Input'][question_pos-1]) + tuple(namelist))
            self.f_questions.dd2["width"] = width
            self.f_questions.dd2["takefocus"] = 1
            self.f_questions.dd2.grid(row=7, column=1, sticky=W+E)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            if settings['Insecure']=='1':
                self.f_questions.ins2 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins2.grid(row=8, column=3, sticky=E)
                self.f_questions.ins2.bind('<Button-1>', CMD(self.insecure, cb_var))               
        if question_pos == 3:
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Display Question
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Display additional information
            #Display Dropdown
            self.f_questions.dd3 = apply(OptionMenu, (self.f_questions, settings['Input'][question_pos-1]) + tuple(namelist))
            self.f_questions.dd3["width"] = width
            self.f_questions.dd3["takefocus"] = 1
            self.f_questions.dd3.grid(row=11, column=1, sticky=W+E)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            if settings['Insecure']=='1':
                self.f_questions.ins3 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins3.grid(row=12, column=3, sticky=E)
                self.f_questions.ins3.bind('<Button-1>', CMD(self.insecure, cb_var))               

    def question_txt(self, cb_var, question_pos, width=40): #Textfield-Entry. Display a one-line text entry.
        log('--Question: TXT(line). Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = '' ###Has to have the same data type as set default values or previous codings

        if question_pos == 1:
            settings['Curr_Page'][0] = ['txt',cb_var]
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt1 = Entry(self.f_questions, width=width)
            self.f_questions.txt1.grid(row=3,column=0,columnspan=3,sticky=W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.txt1.insert(END,str(previous_coding))
                
        if question_pos == 2:
            settings['Curr_Page'][1] = ['txt',cb_var]
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt2 = Entry(self.f_questions, width=width)
            self.f_questions.txt2.grid(row=7,column=0,columnspan=3,sticky=W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.txt2.insert(END,str(previous_coding))
                
        if question_pos == 3:
            settings['Curr_Page'][2] = ['txt',cb_var]
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt3 = Entry(self.f_questions, width=width)
            self.f_questions.txt3.grid(row=11,column=0,columnspan=3,sticky=W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.txt3.insert(END,str(previous_coding))

    def getselect(self,textfeld): #Import selected text to the current entry form
        log('Calling Function: Getselect')
        try:
            select = bereinigen(self.Artikel.get(SEL_FIRST,SEL_LAST))
        except:
            verb('No Text selected')
            select = ""
        if textfeld == 1:
            self.f_questions.txt1.delete('1.0',END)
            self.f_questions.txt1.insert(END, select)
        elif textfeld == 2:
            self.f_questions.txt2.delete('1.0',END)
            self.f_questions.txt2.insert(END, select)
        elif textfeld == 3:
            self.f_questions.txt3.delete('1.0',END)
            self.f_questions.txt3.insert(END, select)


    def question_txt2(self, cb_var, question_pos, width=40, height=3, getselect=0): #Text Entry for input of multiple lines of text.
        log('--Question: TXT2(multiline). Variable: '+cb_var+'; Position: '+str(question_pos)+'; Getselect:'+str(getselect),pos=0)
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = '' ###Has to have the same data type as set default values or previous codings

        if question_pos == 1:
            settings['Curr_Page'][0] = ['txt2',cb_var]
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt1 = Text(self.f_questions, width=width, height=height, wrap=WORD, relief=RIDGE, font = (settings['Font'], "9"))
            self.f_questions.txt1.grid(row=3,column=0,columnspan=3,sticky=W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.getselect1 = Button(self.f_questions, text = "Get Selection", command=CMD(self.getselect,1))
            self.f_questions.getselect1.grid(row=3,column=3)
            if getselect == 0:
                self.f_questions.getselect1.destroy()
            self.f_questions.txt1.insert(END,str(previous_coding))
                
        if question_pos == 2:
            settings['Curr_Page'][1] = ['txt2',cb_var]
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Coder Information
            self.f_questions.txt2 = Text(self.f_questions, width=width, height=height, wrap=WORD, relief=RIDGE, font = (settings['Font'], "9"))
            self.f_questions.txt2.grid(row=7,column=0,columnspan=3,sticky=W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.getselect2 = Button(self.f_questions, text = "Get Selection", command=CMD(self.getselect,2))
            self.f_questions.getselect2.grid(row=7,column=3)
            if getselect == 0:
                self.f_questions.getselect2.destroy()
            self.f_questions.txt2.insert(END,str(previous_coding))
                
        if question_pos == 3:
            settings['Curr_Page'][2] = ['txt2',cb_var]
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt3 = Text(self.f_questions, width=width, height=height, wrap=WORD, relief=RIDGE, font = (settings['Font'], "9"))
            self.f_questions.txt3.grid(row=11,column=0,columnspan=3,sticky=W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.getselect3 = Button(self.f_questions, text = "Get Selection", command=CMD(self.getselect,3))
            self.f_questions.getselect3.grid(row=11,column=3)
            if getselect == 0:
                self.f_questions.getselect3.destroy()
            self.f_questions.txt3.insert(END,str(previous_coding))
            
    def question_cb(self, cb_var, question_pos,layout="hor",defval=0): #Checkbox-question. Up to 14 checkboxes may be defined in the codebook
        log('--Question: Checkbox. Variable: '+cb_var+'; Position: '+str(question_pos)+'; Layout: '+layout,pos=0)
        global settings
        if settings['AEGLOS'] == '1':
            verb('Automated detection')
            predliste = []
            for kat in codebook[cb_var][3]:
                vname = cb_var + '_' + kat
                wert = acabc.predict_short(vname,settings['Fulltext'])
                if vname in def_val.keys():
                    predliste.append(str(def_val[vname]))
                    verb('Previous Default-Value set: '+str(def_val[vname]))
                else:
                    predliste.append(str(wert))
                    verb('New Default-Value set: '+str(wert))
        else:
            verb('Searching Default-Values')
            predliste = []
            for kat in codebook[cb_var][3]:
                vname = cb_var + '_' + kat
                if vname in def_val.keys():
                    predliste.append(str(def_val[vname]))
                    if settings['Verbose'] == '1': verb('Old Default-Value set: '+str(def_val[vname]))
                else:
                    predliste.append('0')

        settings['Curr_Page'][question_pos-1] = ['cb',cb_var]
        settings['Input'][question_pos-1] = []
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = {} ###Has to have the same data type as set default values or previous codings


        if question_pos == 1:
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist1 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist1.grid(row=3, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist1
            if settings['Insecure']=='1':
                self.f_questions.ins1 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins1.grid(row=4, column=3, sticky=E)
                self.f_questions.ins1.bind('<Button-1>', CMD(self.insecure, cb_var))
        elif question_pos == 2:
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist2 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist2.grid(row=7, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist2
            if settings['Insecure']=='1':
                self.f_questions.ins2 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins2.grid(row=8, column=3, sticky=E)
                self.f_questions.ins2.bind('<Button-1>', CMD(self.insecure, cb_var))               
        elif question_pos == 3:
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist3 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist3.grid(row=11, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist3
            if settings['Insecure']=='1':
                self.f_questions.ins3 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins3.grid(row=12, column=3, sticky=E)
                self.f_questions.ins3.bind('<Button-1>', CMD(self.insecure, cb_var))               

        namelist = codebook[cb_var][2]
        codelist = codebook[cb_var][3]

        if layout == 'vert':
            lpos = [(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3)]
        elif layout == 'hor':
            lpos = [(1,1),(1,3),(2,1),(2,3),(3,1),(3,3),(4,1),(4,3),(5,1),(5,3),(6,1),(6,3),(7,1),(7,3)]
        elif layout == 'hor3':
            lpos = [(1,1),(1,3),(1,5),(2,1),(2,3),(2,5),(3,1),(3,3),(3,5),(4,1),(4,3),(4,5),(5,1),(5,3)]

        for k in range(len(namelist)):
            v = IntVar()
            if codelist[k] in previous_coding.keys():
                v.set(int(previous_coding[codelist[k]]))
            else:
                v.set(defval)
            settings['Input'][question_pos-1].append(v)          

        buttons = []
        labels = []      
        for k in range(len(namelist)):
            lab = Label(f,text=namelist[k])
            labels.append(lab)
            lab.grid(row=lpos[k][0],column=lpos[k][1],sticky=W)
            but = Checkbutton(f,variable=settings['Input'][question_pos-1][k])
            buttons.append(but)
            but.grid(row=lpos[k][0],column=lpos[k][1]-1,sticky=E)

             
    def question_rb(self, cb_var, question_pos, layout='vert', defval='98'): #Radiobutton-Question: Up to 7 Radiobuttons may be defined in the codebook.
        log('--Question: Radiobutton. Variable: '+cb_var+'; Position: '+str(question_pos)+'; Layout: '+layout,pos=0)
        global settings
        #### Automated content analysis:
        if settings['AEGLOS'] == '1':
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'])
            wert = self.namegetter(cb_var,pred)
            if not wert == '':
                if not cb_var in def_val.keys():
                    def_val[cb_var] = pred
                    if settings['Verbose'] == '1':
                        verb('Automated value determination')
                        verb('Best prediction: '+str(pred)+ 'Value: '+str(wert))
                else:
                    if settings['Verbose'] == '1': verb('Another default value has been set already. No changes made')

        settings['Curr_Page'][question_pos-1] = ['rb',cb_var]
        settings['Input'][question_pos-1] = ''
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = '' ###Has to have the same data type as set default values or previous codings

        if type(previous_coding) == tuple:
            previous_coding = previous_coding[1]
        elif type(previous_coding) == str:
            if len(self.codegetter(cb_var,previous_coding)) >0:
                previous_coding = self.codegetter(cb_var,previous_coding)
            elif previous_coding in codebook[cb_var][3]:
                previous_coding = str(previous_coding)
            else:
                previous_coding = ''
                verb('No valid coding found')
        else:
            previous_coding = ''
            verb('No valid coding found')


        if question_pos == 1:
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist1 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist1.grid(row=3, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist1
            if settings['Insecure']=='1':
                self.f_questions.ins1 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins1.grid(row=4, column=3, sticky=E)
                self.f_questions.ins1.bind('<Button-1>', CMD(self.insecure, cb_var))
        elif question_pos == 2:
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist2 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist2.grid(row=7, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist2
            if settings['Insecure']=='1':
                self.f_questions.ins2 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins2.grid(row=8, column=3, sticky=E)
                self.f_questions.ins2.bind('<Button-1>', CMD(self.insecure, cb_var))               
        elif question_pos == 3:
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist3 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist3.grid(row=11, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist3
            if settings['Insecure']=='1':
                self.f_questions.ins3 = Label(self.f_questions, text="unsich.", fg="#ee0000")
                self.f_questions.ins3.grid(row=12, column=3, sticky=E)
                self.f_questions.ins3.bind('<Button-1>', CMD(self.insecure, cb_var))               

        namelist = codebook[cb_var][2]
        codelist = codebook[cb_var][3]
        if defval == '98':
            defval = codelist[0]

        if layout == 'vert':
            lpos = [(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(1,3),(2,3),(3,3),(4,3),(5,3),(6,3),(7,3)]
        if layout == 'hor':
            lpos = [(1,1),(1,3),(2,1),(2,3),(3,1),(3,3),(4,1),(4,3),(5,1),(5,3),(6,1),(6,3),(7,1),(7,3)]
         
        settings['Input'][question_pos-1] = StringVar()
        if previous_coding == '':
            settings['Input'][question_pos-1].set(defval)
        else:
            settings['Input'][question_pos-1].set(previous_coding)

        buttons = []
        labels = []      
        for k in range(len(namelist)):
            lab = Label(f,text=namelist[k])
            labels.append(lab)
            lab.grid(row=lpos[k][0],column=lpos[k][1],sticky=W)
            but = Radiobutton(f,variable=settings['Input'][question_pos-1],value=codelist[k],command=self.rb_tamper)
            buttons.append(but)
            but.grid(row=lpos[k][0],column=lpos[k][1]-1,sticky=W)

        self.rb_tamper()
          

    def question_sd(self, cb_var, question_pos,points=5,defval=0): #Semantic differential question
        log('--Question: Semantic Differential. Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        global settings
        settings['Curr_Page'][question_pos-1] = ['sd',cb_var]
        settings['Input'][question_pos-1] = []
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = {} ###Has to have the same data type as set default values or previous codings

        if question_pos == 1:
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist1 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist1.grid(row=3, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist1
        elif question_pos == 2:
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist2 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist2.grid(row=7, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist2
        elif question_pos == 3:
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist3 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist3.grid(row=11, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            f = self.f_questions.rblist3

        namelist = codebook[cb_var][2]
        codelist = codebook[cb_var][3]
        for k in range(len(namelist)):
            v = StringVar()
            if codelist[k] in previous_coding.keys():
                v.set(previous_coding[codelist[k]])
            else:
                v.set(defval)
            settings['Input'][question_pos-1].append(v)          

        scale = range(points)
        buttons = []
        labels = []
        for k in range(len(namelist)):
            lab = Label(f,text=namelist[k])
            labels.append(lab)
            lab.grid(row=k+1,column=points+2,sticky=W)
            lab2 = Label(f,text=codelist[k])
            labels.append(lab2)
            lab2.grid(row=k+1,column=0,sticky=E)

        for i in range(points):
            for k in range(len(namelist)):
                rb = Radiobutton(f,variable=settings['Input'][question_pos-1][k], value=points-i)
                buttons.append(rb)
                rb.grid(row=k+1,column=i+1)
         
    def question_rating(self,cb_var,question_pos,scalelist=['disagree','','','','agree'],valuelist=['1','2','3','4','5'],defval='1'):
        ##Rating question. For each item you may rate from scalelist[0] to scalelist[-1] setting the codes from valuelist[0] to valuelist[-1]. The length of these lists has to be identical.
        log('--Question: Rating. Variable: '+cb_var+'; Position: '+str(question_pos)+'; Number of Points: '+str(len(scalelist)),pos=0)
        global settings
        settings['Curr_Page'][question_pos-1] = ['rating',cb_var]
        settings['Input'][question_pos-1] = []
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = {} ###Has to have the same data type as set default values or previous codings

        if question_pos == 1:
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist1 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist1.grid(row=3, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            if settings['Insecure']=='1':
                self.f_questions.ins1 = Label(self.f_questions, text="unsich.",fg="#ee0000")
                self.f_questions.ins1.grid(row=4, column=3, sticky=E)
                self.f_questions.ins1.bind('<Button-1>', CMD(self.insecure, cb_var))               
            f = self.f_questions.rblist1
        elif question_pos == 2:
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist2 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist2.grid(row=7, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            if settings['Insecure']=='1':
                self.f_questions.ins2 = Label(self.f_questions, text="unsich.",fg="#ee0000")
                self.f_questions.ins2.grid(row=8, column=3, sticky=E)
                self.f_questions.ins2.bind('<Button-1>', CMD(self.insecure, cb_var))               
            f = self.f_questions.rblist2
        elif question_pos == 3:
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Frage
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Codieranweisung
            self.f_questions.rblist3 = Frame(self.f_questions, borderwidth=2, bg=settings['BG_Color'])
            self.f_questions.rblist3.grid(row=11, column=0, columnspan=3, sticky=E+W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            if settings['Insecure']=='1':
                self.f_questions.ins3 = Label(self.f_questions, text="unsich.",fg="#ee0000")
                self.f_questions.ins3.grid(row=12, column=3, sticky=E)
                self.f_questions.ins3.bind('<Button-1>', CMD(self.insecure, cb_var))               
            f = self.f_questions.rblist3

        namelist = codebook[cb_var][2]
        codelist = codebook[cb_var][3]
        for k in range(len(namelist)):
            v = StringVar()
            if codelist[k] in previous_coding.keys():
                v.set(previous_coding[codelist[k]])
            else:
                v.set(defval)
            settings['Input'][question_pos-1].append(v)           
        anzahl = len(codebook[cb_var][2])
        scale = []
        labels = []
        buttons = []
        for i in range(len(scalelist)):
            sc = Label(f, text=scalelist[i])
            scale.append(sc)
            sc.grid(row=0,column=i+1)

        for k in range(len(namelist)):
            lab = Label(f,text=namelist[k])
            labels.append(lab)
            lab.grid(row=k+1,column=0,sticky=W)

        for i in range(len(scalelist)):
            for k in range(len(namelist)):
                rb = Radiobutton(f,variable=settings['Input'][question_pos-1][k], value=valuelist[i], command=self.rb_tamper)
                buttons.append(rb)
                rb.grid(row=k+1,column=i+1)

        self.rb_tamper()


    def question_bt(self, cb_var, question_pos): #Button-Question: Up to four buttons may be defined in the codebook
        log('--Question: Buttons. Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        if question_pos == 1:
            settings['Curr_Page'][0] = ['bt',cb_var]
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Coder information
            settings[cb_var] = StringVar(self)
            auswliste = codebook[cb_var][2]           
            anzahl = len(codebook[cb_var][2])
            
            if anzahl > 0:
                self.f_questions.bu1_1 = Button(self.f_questions, text=auswliste[0], width=20, command=CMD(self.submit,1))
                self.f_questions.bu1_1.grid(row=3,column=1, sticky = W)
            if anzahl > 1:
                self.f_questions.bu1_2 = Button(self.f_questions, text=auswliste[1], width=20, command=CMD(self.submit,2))
                self.f_questions.bu1_2.grid(row=3,column=2, sticky = W)
            if anzahl > 2:
                self.f_questions.bu1_3 = Button(self.f_questions, text=auswliste[2], width=20, command=CMD(self.submit,3))
                self.f_questions.bu1_3.grid(row=3,column=3, sticky = W)

            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=4, sticky=W)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))

        if question_pos == 2:
            settings['Curr_Page'][1] = ['bt',cb_var]
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Coder Information
            settings[cb_var] = StringVar(self)
            auswliste = codebook[cb_var][2]           
            anzahl = len(codebook[cb_var][2])
            
            if anzahl > 0:
                self.f_questions.bu2_1 = Button(self.f_questions, text=auswliste[0], width=20, command=CMD(self.submit,1))
                self.f_questions.bu2_1.grid(row=7,column=1, sticky = W)
            if anzahl > 1:
                self.f_questions.bu2_2 = Button(self.f_questions, text=auswliste[1], width=20, command=CMD(self.submit,2))
                self.f_questions.bu2_2.grid(row=7,column=2, sticky = W)
            if anzahl > 2:
                self.f_questions.bu2_3 = Button(self.f_questions, text=auswliste[2], width=20, command=CMD(self.submit,3))
                self.f_questions.bu2_3.grid(row=7,column=3, sticky = W)

            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=4, sticky=W)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))

        if question_pos == 3:
            settings['Curr_Page'][2] = ['bt',cb_var]
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Coder Information
            settings[cb_var] = StringVar(self)
            auswliste = codebook[cb_var][2]           
            anzahl = len(codebook[cb_var][2])
            
            if anzahl > 0:
                self.f_questions.bu3_1 = Button(self.f_questions, text=auswliste[0], width=20, command=CMD(self.submit,1))
                self.f_questions.bu3_1.grid(row=11, column=1, sticky = W)
            if anzahl > 1:
                self.f_questions.bu3_2 = Button(self.f_questions, text=auswliste[1], width=20, command=CMD(self.submit,2))
                self.f_questions.bu3_2.grid(row=11, column=2, sticky = W)
            if anzahl > 2:
                self.f_questions.bu3_3 = Button(self.f_questions, text=auswliste[2], width=20, command=CMD(self.submit,3))
                self.f_questions.bu3_3.grid(row=11, column=3, sticky = W)

            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=4, sticky=W)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))


    def question_ls(self,cb_var,liste,multi=1):
        log('--Question: Listselection. Variable: '+cb_var+'; List: '+liste,pos=0)
        global prog_pos
        predlist = []
        if settings['AEGLOS'] == '1':
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'],top=5)
            for item in pred:
                wert = self.namegetter(liste,item)
                predlist.append(wert)
            if len(predlist) > 0:
                if not cb_var in def_val.keys():
                    def_val[cb_var] = predlist
                    if settings['Verbose'] == '1':
                        verb('Automated value detection')
                        verb('Best prediction: '+str(predlist))
                else:
                    verb('Another default value has been set already. No changes made')
  
        settings['Curr_Page'][0] = ['list',cb_var,liste]
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = [] ###Has to have the same data type as set default values or previous codings

        if type(previous_coding) == tuple:
            previous_coding = previous_coding[0]
        elif type(previous_coding) == list:
            outlist = []
            for element in previous_coding:
                if element in codebook[liste][2]:
                    outlist.append(element)
                else:
                    if len(self.namegetter(liste,element)) > 0:
                        outlist.append(self.namegetter(liste,element))
            previous_coding = outlist
        elif type(previous_coding) == str:
            if len(self.namegetter(liste,previous_coding)) >0:
                previous_coding = [self.namegetter(liste,previous_coding)]
            elif previous_coding in codebook[liste][2]:
                previous_coding = [str(previous_coding)]
            else:
                previous_coding = []
                verb('No valid coding found')
        else:
            previous_coding = []
            verb('No valid coding found')

        previous_coding = get_unique(previous_coding)      
        verb('Previous coding: '+str(previous_coding))

        self.f_questions.Frage1.insert(INSERT, codebook[cb_var][0],'fett') #Question
        self.f_questions.Frage1.insert(INSERT, codebook[cb_var][1])
        if multi == 1:
            self.f_questions.Aspliste = Listbox(self.f_questions,height=10,width=80, selectmode=MULTIPLE)
        else:
            self.f_questions.Aspliste = Listbox(self.f_questions,height=10,width=80, selectmode=BROWSE)
        self.f_questions.Aspliste.grid(row=3, column=0, columnspan=5, sticky=W+E)
        self.f_questions.Aspliste.focus()
        self.f_questions.scroll_AspListe = Scrollbar(self.f_questions, orient=VERTICAL, command=self.f_questions.Aspliste.yview)
        self.f_questions.scroll_AspListe.grid(row=3, column=5, sticky=W+N+S)
        self.f_questions.Aspliste["yscrollcommand"] = self.f_questions.scroll_AspListe.set
        for element in previous_coding:
            self.f_questions.Aspliste.insert(END,element)
        if len(previous_coding) > 0:
            self.f_questions.Aspliste.insert(END,'****')
        if len(previous_coding) == 1:
            self.f_questions.Aspliste.selection_set(0)
        for element in codebook[liste][2]:
            self.f_questions.Aspliste.insert(END,element)
        self.f_questions.h_Aspliste = Label(self.f_questions, text="?")
        self.f_questions.h_Aspliste.grid(row=4, column=5, sticky=N+E)
        self.f_questions.h_Aspliste.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
        self.f_bottomline.b_check.grid()
        
    def cut_entry(self,wtup):
        log('Calling Function: Cut_Entry')
        ##Fragmentation of a string using punctuation and spaces as cut-points
        outliste = []
        seg = ''
        for i in range(0,len(wtup)):
            if wtup[i] in [' ','\t',',',';']:
                if len(seg) > 0:
                    outliste.append(seg)
                seg = ''
            else:
                seg = seg + wtup[i]
        outliste.append(seg)
        return outliste
    
    def cutback_list(self,liste,auffang=0,broadseek=0): #Reducing the list according to input
        log('Calling Function: Cutback_List')
        if type(auffang) == str:
            suchstring = auffang
        elif auffang.char == chr(8): ##Erase-Key
            suchstring = bereinigen(self.f_questions.seektext.get()[:-1])
        else:
            suchstring = bereinigen(self.f_questions.seektext.get()) + auffang.char
        self.f_questions.Aspliste.delete(0,END)
        sl = self.cut_entry(suchstring)
        for element in codebook[liste][2]:
            inside = 1
            for s in sl:
                if not bereinigen(s,1) in bereinigen(element,1):
                    inside = 0
            if inside == 1:
                self.f_questions.Aspliste.insert(END,element)

        if self.f_questions.Aspliste.size() <1 and broadseek==1:
            for element in codebook[liste][2]:
                inside = 0
                for s in sl:
                    if bereinigen(s,1) in bereinigen(element,1):
                        inside = 1
                if inside == 1:
                    self.f_questions.Aspliste.insert(END,element)

        if self.f_questions.Aspliste.size() == 1:
            self.f_questions.Aspliste.selection_set(0)
            

    def question_lseek(self,cb_var,liste,multi=0):
        log('--Question: List Seek. Variable: '+cb_var+'; List: '+liste,pos=0)
        global prog_pos
        predlist = []
        if settings['AEGLOS'] == '1':
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'],top=5)
            for item in pred:
                wert = self.namegetter(liste,item)
                predlist.append(wert)
            if len(predlist) > 0:
                if not cb_var in def_val.keys():
                    def_val[cb_var] = predlist
                    if settings['Verbose'] == '1':
                        verb('Automated value detection')
                        verb('Best prediction: '+str(predlist))
                else:
                    verb('Another default value has been set already. No changes made')
        
        settings['Curr_Page'][0] = ['listseek',cb_var,liste]
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var][0]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = [] ###Has to have the same data type as set default values or previous codings

        if type(previous_coding) == tuple:
            previous_coding = previous_coding[0]
        elif type(previous_coding) == list:
            outlist = []
            for element in previous_coding:
                if element in codebook[liste][2]:
                    outlist.append(element)
                else:
                    if len(self.namegetter(liste,element)) > 0:
                        outlist.append(self.namegetter(liste,element))
            previous_coding = outlist
        elif type(previous_coding) == str:
            if len(self.namegetter(liste,previous_coding)) >0:
                previous_coding = [self.namegetter(liste,previous_coding)]
            elif previous_coding in codebook[liste][2]:
                previous_coding = [str(previous_coding)]
            else:
                previous_coding = []
                verb('No valid coding found')
        else:
            previous_coding = []
            verb('No valid coding found')

        previous_coding = get_unique(previous_coding)      
        verb('Previous coding: '+str(previous_coding))

        self.f_questions.Frage1.insert(INSERT, codebook[cb_var][0],'fett') #Question
        self.f_questions.Frage1.insert(INSERT, codebook[cb_var][1])

        self.f_questions.seektext = Entry(self.f_questions,width=80)
        self.f_questions.seektext.grid(row=2,column=0,columnspan=5,sticky=W+E)
        self.f_questions.seektext.bind('<Key>', CMD(self.cutback_list, liste))
        
        if multi == 1:
            self.f_questions.Aspliste = Listbox(self.f_questions,height=10,width=80, selectmode=MULTIPLE)
        else:
            self.f_questions.Aspliste = Listbox(self.f_questions,height=10,width=80, selectmode=BROWSE)
        self.f_questions.Aspliste.grid(row=3, column=0, columnspan=5, sticky=W+E)
        self.f_questions.scroll_AspListe = Scrollbar(self.f_questions, orient=VERTICAL, command=self.f_questions.Aspliste.yview)
        self.f_questions.scroll_AspListe.grid(row=3, column=5, sticky=W+N+S)
        self.f_questions.Aspliste["yscrollcommand"] = self.f_questions.scroll_AspListe.set
        for element in previous_coding:
            self.f_questions.Aspliste.insert(END,element)
        if len(previous_coding) > 0:
            self.f_questions.Aspliste.insert(END,'****')
        if len(previous_coding) == 1:
            self.f_questions.Aspliste.selection_set(0)
        for element in codebook[liste][2]:
            self.f_questions.Aspliste.insert(END,element)
        self.f_questions.h_Aspliste = Label(self.f_questions, text="?")
        self.f_questions.h_Aspliste.grid(row=4, column=5, sticky=N+E)
        self.f_questions.h_Aspliste.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
        self.f_questions.seektext.focus()
        self.f_bottomline.b_check.grid()

    def list_add(self,spillover=0):
        log('Calling Function: List Add')
        listsel = self.f_questions.Aspliste.curselection()
        if len(listsel)>0:
            for selection in listsel:
                self.f_questions.Itmliste.insert(END,self.f_questions.Aspliste.get(selection))
            self.f_questions.seektext.delete(0,END)
        elif len(bereinigen(self.f_questions.seektext.get())) > 0:
            self.f_questions.Itmliste.insert(END,bereinigen(self.f_questions.seektext.get()))
            self.f_questions.seektext.delete(0,END)
        else:
            self.message('Invalid-Selection01')

    def list_rem(self,spillover=0):
        log('Calling Function: List Remove')
        listsel = self.f_questions.Itmliste.curselection()
        if len(listsel)==1:
            self.f_questions.Itmliste.delete(listsel[0])
        else:
            self.message('Invalid-Selection01')
        
    def question_ladd(self,cb_var,liste,multi=1):
        log('--Question: List Add. Variable: '+cb_var+'; List: '+liste,pos=0)
        global prog_pos
        predlist = []
        if settings['AEGLOS'] == '1':
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'],top=5)
            for item in pred:
                wert = self.namegetter(liste,item)
                predlist.append(wert)
            if len(predlist) > 0:
                if not cb_var in def_val.keys():
                    def_val[cb_var] = predlist
                    if settings['Verbose'] == '1':
                        verb('Automated value detection')
                        verb('Best prediction:'+str(predlist))
                else:
                    verb('Another default value has been set already. No changes made')
        
        settings['Curr_Page'][0] = ['listadd',cb_var,liste]
        curr_tree = curr()

        if cb_var in curr_tree.keys():
            previous_coding = curr_tree[cb_var][0]
            verb('Previous coding found for '+cb_var+': '+str(previous_coding))
        elif cb_var in def_val.keys():
            previous_coding = def_val[cb_var]
            verb('Set default values found for '+cb_var+': '+str(previous_coding))
        else:
            previous_coding = [] ###Has to have the same data type as set default values or previous codings

        if type(previous_coding) == tuple:
            previous_coding = previous_coding[0]
        elif type(previous_coding) == list:
            outlist = []
            for element in previous_coding:
                if element in codebook[liste][2]:
                    outlist.append(element)
                else:
                    if len(self.namegetter(liste,element)) > 0:
                        outlist.append(self.namegetter(liste,element))
        elif type(previous_coding) == str:
            if len(self.namegetter(liste,previous_coding)) >0:
                previous_coding = [self.namegetter(liste,previous_coding)]
            elif previous_coding in codebook[liste][2]:
                previous_coding = [str(previous_coding)]
            else:
                previous_coding = []
                verb('No valid coding found')
        else:
            previous_coding = []
            verb('No valid coding found')

        previous_coding = get_unique(previous_coding)      
        verb('Previous coding: '+str(previous_coding))

        self.f_questions.Frage1.insert(INSERT, codebook[cb_var][0],'fett') #Question
        self.f_questions.Frage1.insert(INSERT, codebook[cb_var][1])

        self.f_questions.seektext = Entry(self.f_questions,width=80)
        self.f_questions.seektext.grid(row=2,column=0,columnspan=5,sticky=W+E)
        self.f_questions.seektext.bind('<Key>', CMD(self.cutback_list, liste))
        self.f_questions.seektext.bind('<Return>', CMD(self.list_add))
        
        if multi == 1:
            self.f_questions.Aspliste = Listbox(self.f_questions,height=7,width=80, selectmode=MULTIPLE)
        else:
            self.f_questions.Aspliste = Listbox(self.f_questions,height=7,width=80, selectmode=BROWSE)
        self.f_questions.Aspliste.grid(row=3, column=0, columnspan=5, sticky=W+E)
        self.f_questions.scroll_AspListe = Scrollbar(self.f_questions, orient=VERTICAL, command=self.f_questions.Aspliste.yview)
        self.f_questions.scroll_AspListe.grid(row=3, column=5, sticky=W+N+S)
        self.f_questions.Aspliste["yscrollcommand"] = self.f_questions.scroll_AspListe.set

        self.f_questions.adb = Button(self.f_questions,text='Add Item',command=self.list_add)
        self.f_questions.adb.grid(row=4,column=1)
        self.f_questions.rb = Button(self.f_questions,text='Remove Item',command=self.list_rem)
        self.f_questions.rb.grid(row=4,column=2)

        self.f_questions.Itmliste = Listbox(self.f_questions,height=7,width=80, selectmode=BROWSE)
        self.f_questions.Itmliste.grid(row=5, column=0, columnspan=5, sticky=W+E)
        self.f_questions.scroll_ItmListe = Scrollbar(self.f_questions, orient=VERTICAL, command=self.f_questions.Itmliste.yview)
        self.f_questions.scroll_ItmListe.grid(row=5, column=5, sticky=W+N+S)
        self.f_questions.Itmliste["yscrollcommand"] = self.f_questions.scroll_ItmListe.set

        for element in previous_coding:
            self.f_questions.Itmliste.insert(END,element)
        for element in codebook[liste][2]:
            self.f_questions.Aspliste.insert(END,element)

        self.f_questions.h_Aspliste = Label(self.f_questions, text="?")
        self.f_questions.h_Aspliste.grid(row=4, column=5, sticky=N+E)
        self.f_questions.h_Aspliste.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
        self.f_questions.seektext.focus()
        self.f_bottomline.b_check.grid()

    def question_change(self,cb_var,pos=0):
        log('--Question: Change the text in text display. Variable: '+cb_var,pos=0)
        self.question_bt(cb_var,1)
        settings['Curr_Page'][0] = ['change',cb_var]


    def question_menu(self, cb_var, question_pos): #Menu-Question: Up to three menu selections may be displayed per page
        global settings
        log('--Question: Menu. Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        settings['Curr_Page'][question_pos-1] = ['menu',cb_var]
        settings['Input'][question_pos-1] = ''
        curr_tree=curr()

        namelist = codebook[cb_var][2]
        codelist = codebook[cb_var][3]
        
        settings['Input'][question_pos-1] = StringVar()
        settings['Input'][question_pos-1].set(namelist[0])

        if question_pos == 1:
            self.f_questions.Frage1.insert(END, codebook[cb_var][1],'fett') #Display additional information
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.mb1 = Menubutton(self.f_questions, text=codebook[cb_var][0][:-1],relief=RAISED)
            self.f_questions.mb1.grid(row=3,column=1,sticky=W+E)
            self.f_questions.menu1 = Menu(self.f_questions.mb1,tearoff=0)
            self.f_questions.mb1["menu"] = self.f_questions.menu1
            m = self.f_questions.menu1
               
        if question_pos == 2:
            self.f_questions.Frage2.insert(END, codebook[cb_var][1],'fett') #Display additional information
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.mb2 = Menubutton(self.f_questions, text=codebook[cb_var][0][:-1],relief=RAISED)
            self.f_questions.mb2.grid(row=7,column=1,sticky=W+E)
            self.f_questions.menu2 = Menu(self.f_questions.mb2,tearoff=0)
            self.f_questions.mb2["menu"] = self.f_questions.menu2
            m = self.f_questions.menu2

        if question_pos == 3:
            self.f_questions.Frage3.insert(END, codebook[cb_var][1],'fett') #Display additional information
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.mb3 = Menubutton(self.f_questions, text=codebook[cb_var][0][:-1],relief=RAISED)
            self.f_questions.mb3.grid(row=11,column=1,sticky=W+E)
            self.f_questions.menu3 = Menu(self.f_questions.mb3,tearoff=0)
            self.f_questions.mb3["menu"] = self.f_questions.menu3
            m = self.f_questions.menu3

        curcas = Menu(m,tearoff=0)
        curlab = ''
        for i in range(len(codelist)-1):
            if codelist[i][0] == '-':
                curcas.add_command(label=namelist[i],command=CMD(self.submit,codelist[i][1:]))
            elif codelist[i][0] == '#':
                if len(curlab) > 1:
                    m.add_cascade(label=curlab,menu=curcas)
                    curlab = ''
                m.add_separator()
            else:
                if len(curlab) > 1:
                    m.add_cascade(label=curlab,menu=curcas)
                if codelist[i+1][0] == '-':
                    curcas = Menu(m,tearoff=0)
                    curlab = namelist[i]
                else:
                    m.add_command(label=namelist[i],command=CMD(self.submit,codelist[i]))
                    curlab = ''

        if codelist[-1][0] == '-':
            curcas.add_command(label=namelist[-1],command=CMD(self.submit,codelist[-1][1:]))
            m.add_cascade(label=curlab,menu=curcas)
        else:
            if len(curlab) > 1:
                m.add_cascade(label=curlab,menu=curcas)
            m.add_command(label=namelist[-1],command=CMD(self.submit,codelist[-1]))




    def question_mark_units(self,cb_var,tags):
        log('--Question: Mark Units. Variable: '+cb_var+'; Level: '+str(tags),pos=0)
        self.question_bt(cb_var,1)
        settings['Curr_Page'][0] = ['unit_mark',cb_var,tags]
        if type(tags) == str:
            tags = [tags]
        self.f_questions.bu1_1["command"]=self.submit
        for t in tags:
            if t in storage['Highlight'].keys():
                for bez in storage['Highlight'][t].keys():
                    if storage['Highlight'][t][bez]['Done'] == 0:
                        self.Artikel.tag_add(storage['Highlight'][t][bez]['Typ'],
                                             storage['Highlight'][t][bez]['Start'],
                                             storage['Highlight'][t][bez]['End'])
       
    def units_action(self,tags,action='none'):
        log('Calling Function: Units Action')
        global prog_pos
        global dta_pos
        if action == 'add':
            self.clean_up_all()
            settings['Curr_Page'][0]=['unit_mark','Add_Items',tags]
##            for tag in tags: ##Prevent tags of already stored highlights to be stored again
##                for e in storage['Highlight'][tag].keys():
##                    self.Artikel.tag_remove(storage['Highlight'][tag][e]['Typ'],
##                                            storage['Highlight'][tag][e]['Start'],
##                                            storage['Highlight'][tag][e]['End'])       
            self.store_var_all()
            self.ask()
        elif action == 'rem':
            selection = self.f_questions.Aspliste.curselection()[0]
            label = self.f_questions.Aspliste.get(selection)
            verb('List Selection: '+str(label))
            for tag in tags:
                for fk in storage['Highlight'][tag].keys():
                    if label == storage['Highlight'][tag][fk]['Label']:
                        del storage['Highlight'][tag][fk]
            self.clean_up_all()
            self.ask()
        elif action == 'mark':
            selection = self.f_questions.Aspliste.curselection()[0]
            label = self.f_questions.Aspliste.get(selection)
            verb('List Selection: '+str(label))
            for tag in tags:
                self.clean_all_tags(tag)
                for fk in storage['Highlight'][tag].keys():
                    if label == storage['Highlight'][tag][fk]['Label']:
                        self.Artikel.tag_add(storage['Highlight'][tag][fk]['Typ'],
                                             storage['Highlight'][tag][fk]['Start'],
                                             storage['Highlight'][tag][fk]['End'])
        else:
            verb('Warning: No function tied to this button')


    def tagorder(self, tags):
        log('Calling Function: Tagorder'+str(tags),pos=0)
        taglist = []
        for tag in tags:
            for e in storage['Highlight'][tag].keys():
                taglist.append((tag,e))
        verb(str(taglist))

        poslist = []
        for t in taglist:
            if 'Start' in storage['Highlight'][t[0]][t[1]].keys():
                poslist.append(str(storage['Highlight'][t[0]][t[1]]['Start']))
            else:
                poslist.append('0')
        verb(str(poslist))

        outlist = []
        for tag in sorted(zip(poslist,taglist)):
            outlist.append(tag[1])

        return outlist
        

    def question_sel_units(self,var,tags):
        log('--Question: Select Units. Variable: '+var+'; For tags: '+str(tags),pos=0)
        global prog_pos
        global dta_pos
        if type(tags) == str:
            tags = [tags]
        settings['Curr_Page'][0] = ['unit_auswahl',var,tags]
        for tag in tags:
            verb('Available Units for tag '+tag+': '+str(sorted(storage['Highlight'][tag].keys())))

        self.f_questions.Frage1.insert(INSERT, codebook[var][0],'fett') #Asking for a list
        self.f_questions.Frage1.insert(INSERT, codebook[var][1]) 
        self.f_questions.Aspliste = Listbox(self.f_questions,height=5,width=80, selectmode=BROWSE)
        self.f_questions.Aspliste.grid(row=3, column=0, columnspan=5, sticky=W+E)
        self.f_questions.Aspliste.focus()
        self.f_questions.scroll_AspListe = Scrollbar(self.f_questions, orient=VERTICAL, command=self.f_questions.Aspliste.yview)
        self.f_questions.scroll_AspListe.grid(row=3, column=5, sticky=W+N+S)
        self.f_questions.Aspliste["yscrollcommand"] = self.f_questions.scroll_AspListe.set
        anz = 0
        for tag in self.tagorder(tags):
            if storage['Highlight'][tag[0]][tag[1]]['Done'] == 0:
                anz = anz + 1
                self.f_questions.Aspliste.insert(END,storage['Highlight'][tag[0]][tag[1]]['Label'])
        self.f_questions.h_Aspliste = Label(self.f_questions, text="?")
        self.f_questions.h_Aspliste.grid(row=4, column=5, sticky=N+E)
        self.f_questions.h_Aspliste.bind('<Button-1>', CMD(self.hilfe_zu, codebook[var][4]))
        self.f_bottomline.b_check.grid()
        
        self.f_questions.Aspliste.selection_set('0')

        self.f_questions.fk_hinzu = Button(self.f_questions, text = codebook[var][2][0], width=20,command=CMD(self.units_action,tags,'add'))
        self.f_questions.fk_hinzu.grid(row=4,column=1,sticky=W+E)
        self.f_questions.fk_weg = Button(self.f_questions, text = codebook[var][2][1], width=20,command=CMD(self.units_action,tags,'rem'))
        self.f_questions.fk_weg.grid(row=4,column=2,sticky=W+E)
        self.f_questions.fk_markieren = Button(self.f_questions, text = codebook[var][2][2], width=20,command=CMD(self.units_action,tags,'mark'))
        self.f_questions.fk_markieren.grid(row=4,column=3,sticky=W+E)

        return anz


    def question_spr(self, cb_var, question_pos): #Specific question type asking for three attributes of an actor (a, b and c).
        log('--Question: Sprecher. Variable: '+cb_var+'; Position: '+question_pos,pos=0)
        global prog_pos

        if question_pos == 1:
            zeile = 1
            settings['Curr_Page'][0] = ['spr',cb_var]
        if question_pos == 2:
            zeile = 5
            settings['Curr_Page'][1] = ['spr',cb_var]
        if question_pos == 3:
            zeile = 9
            settings['Curr_Page'][2] = ['spr',cb_var]

        self.f_questions.sprecher = Frame(self.f_questions, relief=RIDGE, borderwidth=2, bg=settings['BG_Color'])
        self.f_questions.sprecher.grid(row=zeile, rowspan=2, column=0, columnspan=4, sticky=E+W)
        self.f_questions.sprecher.Frage = Text(self.f_questions.sprecher, width=80, height=6, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'])
        self.f_questions.sprecher.Frage.grid(row=0, column=0, columnspan=6, sticky=N+S+E+W)
        self.f_questions.sprecher.Frage.tag_config('fett', font = (settings['Font'], "10", "bold"))
        self.f_questions.sprecher.Frage.insert(INSERT,codebook[cb_var][0], 'fett') #Question
        self.f_questions.sprecher.Frage.insert(END, codebook[cb_var][1]) #Coder Information
        self.f_questions.help_spr = Label(self.f_questions, text="?")
        self.f_questions.help_spr.grid(row=zeile, column=4, sticky=W)
        self.f_questions.help_spr.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))

        settings['Akt_a'] = StringVar()
        settings['Akt_b'] = StringVar()
        settings['Akt_c'] = StringVar()
        auswliste_a = codebook['Akt_a'][2]
        auswliste_b = codebook['Akt_b'][2]
        auswliste_c = codebook['Akt_c'][2]
        settings['Akt_a'].set(auswliste_a[0]) #defaultwert
        settings['Akt_b'].set(auswliste_b[0]) #defaultwert
        settings['Akt_c'].set(auswliste_c[0]) #defaultwert
        self.f_questions.sprecher.l_Quelle_a = Label(self.f_questions.sprecher, text=codebook[cb_var][2][0])
        self.f_questions.sprecher.l_Quelle_a.grid(row=1, column=0, sticky=W+S)
        self.f_questions.sprecher.l_Quelle_b = Label(self.f_questions.sprecher, text=codebook[cb_var][2][1])
        self.f_questions.sprecher.l_Quelle_b.grid(row=1, column=2, sticky=W+S)
        self.f_questions.sprecher.l_Quelle_c = Label(self.f_questions.sprecher, text=codebook[cb_var][2][2])
        self.f_questions.sprecher.l_Quelle_c.grid(row=1, column=4, sticky=W+S)
        self.f_questions.sprecher.Quelle_a = apply(OptionMenu, (self.f_questions.sprecher, settings['Akt_a']) + tuple(auswliste_a))
        self.f_questions.sprecher.Quelle_a.grid(row=3, column=0, columnspan=2, sticky=W+E)
        self.f_questions.sprecher.Quelle_b = apply(OptionMenu, (self.f_questions.sprecher, settings['Akt_b']) + tuple(auswliste_b))
        self.f_questions.sprecher.Quelle_b.grid(row=3, column=2, columnspan=2, sticky=W+E)
        self.f_questions.sprecher.Quelle_c = apply(OptionMenu, (self.f_questions.sprecher, settings['Akt_c']) + tuple(auswliste_c))
        self.f_questions.sprecher.Quelle_c.grid(row=3, column=4, columnspan=2, sticky=W+E)
        self.f_questions.sprecher.Quelle_a["width"] = 20
        self.f_questions.sprecher.Quelle_b["width"] = 20
        self.f_questions.sprecher.Quelle_c["width"] = 20

        self.f_questions.sprecher.Other_a = Entry(self.f_questions.sprecher, textvariable=settings['Akt_a'], width=20)
        self.f_questions.sprecher.Other_a.grid(row=2, column=0, sticky=W)
        self.f_questions.sprecher.Other_b = Entry(self.f_questions.sprecher, textvariable=settings['Akt_b'], width=20)
        self.f_questions.sprecher.Other_b.grid(row=2, column=2, sticky=W)
        self.f_questions.sprecher.Other_c = Entry(self.f_questions.sprecher, textvariable=settings['Akt_c'], width=20)
        self.f_questions.sprecher.Other_c.grid(row=2, column=4, sticky=W)
        


############################################
##                                        ##
##       Speicherroutinen                 ##
##                                        ##
############################################

    def export_data(self, dta_pos_all, varlist, filename,debug=0):
        try:
            a = open(filename,'r')
            a.close()
        except:
            verb('No storage file yet. Creating new file')
            a = open(filename,'w')
            a.write('Coder\tID\t')
            for d in dta_pos_all:
                a.write('Level\tUnit_ID\t')
            for v in varlist:
                if v in settings['Multi_Items']:
                    for code in codebook[v][3]:
                        a.write(v+'_'+code+'\t')
                else:
                    a.write(v+'\t')
            if len(dta_pos_all) == 0:
                a.write('T_Brutto\tT_Break\tT_Netto\tT_H\tSessiontext\tSession_ID')
            a.write('\n')
            a.close()
            
        log('Calling Function: Export_Data of all elements in: '+ str(dta_pos_all))
        if len(dta_pos_all) == 3:
            verb('Fourth Level of Analysis')
            if dta_pos_all[0] in storage.keys():
                for i in sorted(storage[dta_pos_all[0]].keys()):
                    if dta_pos_all[1] in storage[dta_pos_all[0]][i].keys():
                        for k in sorted(storage[dta_pos_all[0]][i][dta_pos_all[1]].keys()):
                            if dta_pos_all[2] in storage[dta_pos_all[0]][i][dta_pos_all[1]][k].keys():
                                for l in sorted(storage[dta_pos_all[0]][i][dta_pos_all[1]][k][dta_pos_all[2]].keys()):
                                    direc = storage[dta_pos_all[0]][i][dta_pos_all[1]][k][dta_pos_all[2]][l]
                                    exp_file = open(filename, 'a')
                                    exp_file.write(settings['Coder'])
                                    exp_file.write('\t')
                                    exp_file.write(storage['ID'])
                                    exp_file.write('\t')
                                    exp_file.write(dta_pos_all[0])
                                    exp_file.write('\t')
                                    exp_file.write(i)
                                    exp_file.write('\t')
                                    exp_file.write(dta_pos_all[1])
                                    exp_file.write('\t')
                                    exp_file.write(k)
                                    exp_file.write('\t')                            
                                    exp_file.write(dta_pos_all[2])
                                    exp_file.write('\t')
                                    exp_file.write(l)
                                    exp_file.write('\t')                            
                                    for var in varlist:
                                        self.var_export(exp_file, direc,var,debug)
                                    exp_file.write('\n')
                                    exp_file.close()

        elif len(dta_pos_all) == 2:
            verb('Third Level of Analysis')
            if dta_pos_all[0] in storage.keys():
                for i in sorted(storage[dta_pos_all[0]].keys()):
                    if dta_pos_all[1] in storage[dta_pos_all[0]][i].keys():
                        for k in sorted(storage[dta_pos_all[0]][i][dta_pos_all[1]].keys()):
                            direc = storage[dta_pos_all[0]][i][dta_pos_all[1]][k]
                            exp_file = open(filename, 'a')
                            exp_file.write(settings['Coder'])
                            exp_file.write('\t')
                            exp_file.write(storage['ID'])
                            exp_file.write('\t')
                            exp_file.write(dta_pos_all[0])
                            exp_file.write('\t')
                            exp_file.write(i)
                            exp_file.write('\t')
                            exp_file.write(dta_pos_all[1])
                            exp_file.write('\t')
                            exp_file.write(k)
                            exp_file.write('\t')                            
                            for var in varlist:
                                self.var_export(exp_file, direc,var,debug)
                            exp_file.write('\n')
                            exp_file.close()
                            
        elif len(dta_pos_all) == 1:
            verb('Second Level of Analysis')
            if dta_pos_all[0] in storage.keys():
                for i in sorted(storage[dta_pos_all[0]].keys()):
                    direc = storage[dta_pos_all[0]][i]
                    exp_file = open(filename, 'a')
                    exp_file.write(settings['Coder'])
                    exp_file.write('\t')
                    exp_file.write(storage['ID'])
                    exp_file.write('\t')
                    exp_file.write(dta_pos_all[0])
                    exp_file.write('\t')
                    exp_file.write(i)
                    exp_file.write('\t')
                    for var in varlist:
                        self.var_export(exp_file, direc,var,debug)
                    exp_file.write('\n')
                    exp_file.close()
            else:
                verb('Level of Analysis not found: '+str(dta_pos_all[0]))
                    
        elif len(dta_pos_all) == 0:
            verb('First Level of Analysis (root-Level)')
            direc = storage
            exp_file = open(filename, 'a')
            exp_file.write(settings['Coder'])
            exp_file.write('\t')
            exp_file.write(storage['ID'])
            exp_file.write('\t')
            for var in varlist:
                self.var_export(exp_file, direc,var,debug)
            dauer = time.time()-storage['#TS'][1]
            dauer_net = dauer - settings['Break_Time']
            dauer_h = dauer_net/3600
            exp_file.write(str(dauer))
            exp_file.write('\t')              
            exp_file.write(str(settings['Break_Time']))
            exp_file.write('\t')              
            exp_file.write(str(dauer_net))
            exp_file.write('\t')              
            exp_file.write(str(dauer_h))
            exp_file.write('\t')              
            exp_file.write(str(settings['Session_Text']))
            exp_file.write('\t')              
            exp_file.write(str(settings['Session_Name']))
            exp_file.write('\n')
            exp_file.close()


    def var_export(self, exp_file, dictionary, variabel,debug=0):
        global codebook
        global settings
        verb('--Var Export: '+variabel)
        if variabel in dictionary.keys():
            if type(dictionary[variabel]) == tuple:
                if debug == 1: exp_file.write(variabel+"=")
                if not dictionary[variabel][1] == '':
                    exp_file.write(str(dictionary[variabel][1]))
                else:
                    exp_file.write(bereinigen(dictionary[variabel][0]))
                exp_file.write('\t')
            elif type(dictionary[variabel]) == str or type(dictionary[variabel]) == unicode:
                if debug == 1: exp_file.write(variabel+"=")
                exp_file.write(bereinigen(dictionary[variabel]).replace('"','<quot>'))
                exp_file.write('\t')
            elif type(dictionary[variabel]) == dict:
                for item in codebook[variabel][3]:
                    if item in dictionary[variabel].keys():
                        if debug == 1: exp_file.write(variabel+'_'+item+"=")
                        if type(dictionary[variabel][item]) == str:
                            exp_file.write(str(dictionary[variabel][item]))
                            exp_file.write('\t')
                        elif type(dictionary[variabel][item]) == int:
                            exp_file.write(str(dictionary[variabel][item]))
                            exp_file.write('\t')
                        elif type(dictionary[variabel][item]) == tuple:
                            if not dictionary[variabel][item][1] == '':
                                exp_file.write(str(dictionary[variabel][item][1]))
                            else:
                                exp_file.write(str(dictionary[variabel][item][0]))
                            exp_file.write('\t')
                    else:
                        exp_file.write('\t')
            elif type(dictionary[variabel]) == int:
                if debug == 1: exp_file.write(variabel+"=")
                exp_file.write(str(dictionary[variabel]))
                exp_file.write('\t')
            elif type(dictionary[variabel]) == float:
                if debug == 1: exp_file.write(variabel+"=")
                exp_file.write(str(dictionary[variabel]))
                exp_file.write('\t')
            else:
                if debug == 1: exp_file.write(variabel+"=")
                verb('Unknown Type: '+str(type(dictionary[variabel])))
                exp_file.write('\t')
        else:
            if variabel in settings['Multi_Items']:
                laenge = len(codebook[variabel][3])
                if debug == 1: exp_file.write(variabel+"=")
                for i in range(1,laenge):
                    exp_file.write('\t')
            else:
                if debug == 1: exp_file.write(variabel+"=")               
            exp_file.write('\t')   

    def export_tab_alle(self, filename):
        log('Calling Function: Export Tab Alle')
        global tmp_ort
        ## This Function is currently not used. It would make use of the export_tab-Function for all subtrees within storage
     
    def export_tab(self, filename, element):
        log('Calling Function: Export Tab')
        #element is a Tuple, which contains two elements:
        #   Element to be exported
        #   Another tuple of the form: (ID, ID, ID...) for each level it passes.
        tabelle = element[0]
        specify = element[1]
        if settings['Verbose'] == '1':
            verb(str(tabelle))
            verb(str(specify))        


############################################
##                                        ##
##       Hilfsfunktionen                  ##
##                                        ##
############################################

    def set_window(self):
        log('Setting the Window')
        #Set the window in which the query form is set up. There are five elements:
        #   1) Review-Frame: May be used to display a list of previously coded elements on this level.
        #   2) Location-Frame: Contains a text-area which may be used to display additional information on the current position.
        #   3) Explanation-Frame: Spare frame beneath the location frame (usually not used)
        #   4) Question-Frame: Frame which contains empty spaces for three questions. Questions may be called by self.question..()-functions.
        #   5) Button-Frame: Is used to display four buttons: Check, Abort, Back and Break. Each has a defined target and may be
        #                    displayed and removed by calling the self.buttons()-Function
        
        if settings['Layout'] == 'Lefty':
            c1 = 1
            butt_order = [0,1,2,3]
            verb('Left-Handed Design')
        else:
            c1 = 5
            butt_order = [3,2,1,0]
            verb('Right-Handed Design')
            
        #Remove everything to prevent redundancy
        try:
            self.f_review.destroy()
            self.f_location.destroy()
            self.f_explanation.destroy()
            self.f_questions.destroy()
            self.f_bottomline.destroy()
            self.menubar.destroy()
            verb("Window reset")         
        except:
            verb("First Window")

        #Build:   
        self.f_review = Frame(self, borderwidth=2, bg=settings['BG_Color'], height=20, relief=FLAT)
        self.f_review.grid(row=1, column=c1, sticky=N+E+S+W)
        self.f_location = Frame(self, borderwidth=2, bg=settings['BG_Color'])
        self.f_location.grid(row=2, column=c1, sticky=N+E+S+W)
        self.f_explanation = Frame(self, borderwidth=2, bg=settings['BG_Color'])
        self.f_explanation.grid(row=3, column=c1, sticky=N+E+S+W)
        self.f_questions = Frame(self, borderwidth=2, bg=settings['BG_Color'])
        self.f_questions.grid(row=4, column=c1, sticky=N+E+S+W)
        self.f_bottomline = Frame(self, borderwidth=2, bg=settings['BG_Color'])
        self.f_bottomline.grid(row=6, column=c1, sticky=E+S+W)

        self.f_location.angabe = Text(self.f_location, width=80, height=2, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_location.angabe.grid(row=0, column=0, columnspan=4, sticky=N+S+E+W)
        self.f_location.angabe.tag_config('highlight', font = (settings['Font'], "9", "italic"))
        self.f_location.angabe.tag_config('fett', font = (settings['Font'], "9", "bold"))

        self.f_questions.Frage1 = Text(self.f_questions, width=80, height=4, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_questions.Frage1.grid(row=1, column=0, columnspan=4, sticky=N+S+E+W)
        self.f_questions.Frage1.tag_config('fett', font = (settings['Font'], "10", "bold"))
        self.f_questions.Frage2 = Text(self.f_questions, width=80, height=4, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_questions.Frage2.grid(row=5, column=0, columnspan=4, sticky=N+S+E+W)
        self.f_questions.Frage2.tag_config('fett', font = (settings['Font'], "10", "bold"))
        self.f_questions.Frage3 = Text(self.f_questions, width=80, height=4, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_questions.Frage3.grid(row=9, column=0, columnspan=4, sticky=N+S+E+W)
        self.f_questions.Frage3.tag_config('fett', font = (settings['Font'], "10", "bold"))

        self.f_questions.spacer1 = Text(self.f_questions, width=80, height=1, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_questions.spacer1.grid(row=4, column=0, columnspan=4, sticky=S+E+W)
        self.f_questions.spacer2 = Text(self.f_questions, width=80, height=1, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_questions.spacer2.grid(row=8, column=0, columnspan=4, sticky=S+E+W)
        self.f_questions.spacer3 = Text(self.f_questions, width=80, height=1, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg=settings['BG_Color'], takefocus = 0)
        self.f_questions.spacer3.grid(row=12, column=0, columnspan=4, sticky=S+E+W)

        for i in range(0,5):
            self.f_bottomline.columnconfigure(i, minsize=40)

        self.f_bottomline.b_check = Button(self.f_bottomline, text = "Check", width=18, command=self.submit)
        self.f_bottomline.b_check.grid(row=0, column=butt_order[0], sticky=N+S+E+W)
        self.f_bottomline.b_abort = Button(self.f_bottomline, text = "-", width=18, command=self.abort)
        self.f_bottomline.b_abort.grid(row=0, column=butt_order[1], sticky=N+S+E+W)
        self.f_bottomline.b_back = Button(self.f_bottomline, text = "Back", width=18, command=self.back, takefocus = 0)
        self.f_bottomline.b_back.grid(row=0, column=butt_order[2], sticky=N+S+W)

        self.f_bottomline.b_break = Button(self.f_bottomline, text = "Break", width=18, command=self.pause, takefocus = 0)
        self.f_bottomline.b_break.grid(row=0, column=butt_order[3], sticky=N+S+W)

        self.menubar = Frame(self,borderwidth=2, bg=settings['BG_Color'], relief=RAISED)
        self.menubar.grid(row=0,column=c1,columnspan=2,sticky=W+E)

        self.menubar.deb = Menubutton(self.menubar, text="Help",relief=RAISED)
        self.menubar.deb.grid(row=0,column=9,sticky=N+W)
        self.menubar.deb.menu = Menu(self.menubar.deb, tearoff=0)
        self.menubar.deb["menu"] = self.menubar.deb.menu

        self.menubar.fmen = Menubutton(self.menubar, text="File",relief=RAISED)
        self.menubar.fmen.grid(row=0,column=0,sticky=N+W)
        self.menubar.fmen.menu = Menu(self.menubar.fmen, tearoff=0)
        self.menubar.fmen["menu"] = self.menubar.fmen.menu

        self.menubar.set = Menubutton(self.menubar, text="Settings",relief=RAISED)
        self.menubar.set.grid(row=0,column=2,sticky=N+W)
        self.menubar.set.menu = Menu(self.menubar.set, tearoff=0)
        self.menubar.set["menu"] = self.menubar.set.menu

        self.menubar.tools = Menubutton(self.menubar, text="Tools",relief=RAISED)
        self.menubar.tools.grid(row=0,column=1,sticky=N+W)
        self.menubar.tools.menu = Menu(self.menubar.tools, tearoff=0)
        self.menubar.tools["menu"] = self.menubar.tools.menu


        self.menubar.deb.menu.add_command(label="Where am I?",command=self.show_parameters)
        self.menubar.deb.menu.add_command(label="How did I get here?",command=self.show_path)
        self.menubar.deb.menu.add_command(label="What just happened?",command=self.show_verb)       
        self.menubar.deb.menu.add_command(label="What did I code?",command=self.show_storage)
        self.menubar.deb.menu.add_command(label="How are you set up?",command=self.show_settings)
        self.menubar.deb.menu.add_command(label="IT CRASHED! Take me back to somewhere safe",command=self.reset_coding)
        
        self.menubar.fmen.menu.add_command(label="Store the current coding",command=self.store_coding)
        if available('Out_Tmp'):
            self.menubar.fmen.menu.add_command(label="Load the last temporarily stored coding",command=CMD(self.load_coding,settings['Out_Tmp']))
        self.menubar.fmen.menu.add_command(label="Load specific coding...",command=self.load_coding)
        self.menubar.fmen.menu.add_command(label="Leave a comment",command=self.comment)
        
        self.menubar.tools.menu.add_command(label="Visone",command=visonout)
        self.menubar.tools.menu.add_command(label="Coding Stats",command=self.calculate_stats)
        self.menubar.tools.menu.add_command(label="Create SPSS Syntax",command=self.spss_syntax)

        self.layout = StringVar()
        self.layout.set(settings['Layout'])

        lay = Menu(self.menubar.set.menu,tearoff=0)
        lay.add_radiobutton(label='Left-Handed',variable=self.layout,value='Lefty',command=self.reload_window)
        lay.add_radiobutton(label='Right-Handed',variable=self.layout,value='Righty',command=self.reload_window)
        self.menubar.set.menu.add_cascade(label="Layout",menu=lay)
        
        self.encod = StringVar()
        self.encod.set(settings['Text_Encoding'])

        te = Menu(self.menubar.set.menu,tearoff=0)
        te.add_radiobutton(label='UTF-8',variable=self.encod,value='utf-8',command=self.reload_window)
        te.add_radiobutton(label='Latin-1',variable=self.encod,value='latin-1',command=self.reload_window)
        self.menubar.set.menu.add_cascade(label="Text Encoding (Text Display)",menu=te)

        self.fs = StringVar()
        self.fs.set(settings['Fontsize'])

        fsi = Menu(self.menubar.set.menu,tearoff=0)
        fsi.add_radiobutton(label='9',variable=self.fs,value='9',command=self.reload_window)
        fsi.add_radiobutton(label='10',variable=self.fs,value='10',command=self.reload_window)
        fsi.add_radiobutton(label='11',variable=self.fs,value='11',command=self.reload_window)
        fsi.add_radiobutton(label='12',variable=self.fs,value='12',command=self.reload_window)
        fsi.add_radiobutton(label='14',variable=self.fs,value='14',command=self.reload_window)
        fsi.add_radiobutton(label='18',variable=self.fs,value='18',command=self.reload_window)
        self.menubar.set.menu.add_cascade(label="Font Size (Text Display)",menu=fsi)


        self.font = StringVar()
        self.font.set(settings['Font'])

        fon = Menu(self.menubar.set.menu,tearoff=0)
        fon.add_radiobutton(label='Arial',variable=self.font,value='Arial',command=self.reload_window)
        fon.add_radiobutton(label='Times',variable=self.font,value='Times',command=self.reload_window)
        fon.add_radiobutton(label='Helvetica',variable=self.font,value='Helvetica',command=self.reload_window)
        self.menubar.set.menu.add_cascade(label="Font",menu=fon)       
               
                        
        self.ask()

    def reload_window(self,spill=0):
        global cini
        if self.message('Caution03',3)==1:
            settings['Text_Encoding']=self.encod.get()
            settings['Layout']=self.layout.get()
            settings['Font']=self.font.get()
            settings['Fontsize']=self.fs.get()

            sets = ['Text_Encoding','Layout','Font','Fontsize']

            if 'Coder-Settings' in cini.keys():
                for i in range(len(cini['Coder-Settings'][3])):
                    for s in sets:
                        if cini['Coder-Settings'][3][i]==s:
                            cini['Coder-Settings'][2][i]=settings[s]
                for s in sets:
                    if not s in cini['Coder-Settings'][3]:
                        cini['Coder-Settings'][3].append(s)
                        cini['Coder-Settings'][2].append(settings[s])
                
            self.set_window()
            if len(settings['Fulltext'])>1:
                self.anzeigen(settings['Fulltext'])


    def comment(self,spill=0):
        self.commbox = Toplevel(self)
        self.commbox.rowconfigure(1, weight=1)
        self.commbox.columnconfigure(1, weight=1)
        self.commbox.title("Leave a comment")
        self.commbox.ysc = Scrollbar(self.commbox, orient=VERTICAL)
        self.commbox.ysc.grid(row=1,column=2,sticky=W+N+S)
        self.commbox.info = Text(self.commbox,width=60,height=10,bg="#ffffff",
                                 wrap=WORD, yscrollcommand=self.commbox.ysc.set,
                                 font=("Arial",9),takefocus=0, relief=RIDGE)
        self.commbox.info.grid(row=1,column=1,sticky=N+E+S+W)
        self.commbox.ysc["command"]=self.commbox.info.yview
        self.commbox.info.focus()
        self.commbox.info.bind('<Control-Return>',self.check_comment)
        
        self.commbox.lab = Label(self.commbox,text="Enter your comments here:")
        self.commbox.lab.grid(row=0,column=1,sticky=W)

        self.commbox.check = Button(self.commbox,text="Save comments and close",command=self.check_comment)
        self.commbox.check.grid(row=2,column=1)

    def check_comment(self,spill=0):
        global prog_pos
        global data_pos
        global storage
        text = self.commbox.info.get('1.0',END)
        text = 'Kommentar: '+prog_pos + '; '+str(dta_pos)+':\n'+bereinigen(text)+'\n-----------\n' 
        if not 'Bemerkungen' in storage.keys():
            storage['Bemerkungen'] = ''
        storage['Bemerkungen']=storage['Bemerkungen']+text

        self.commbox.destroy()

    def calculate_stats(self):
        try:
            dta = get_data('_Text.txt')
            outtext = ''
        except:
            outtext = 'ERROR: No stored codings found. History could not be calculated'

        if outtext == '':
            curr_time = time.time()
            day_time = time.time()-3600*24
            week_time = time.time()-3600*24*7

            anz_total = 0
            anz_week = 0
            anz_day = 0

            dur_total = 0
            dur_week = 0
            dur_day = 0

            for i in range(len(dta['ID'])):
                dur = 0
                ts = 0
                try:
                    dur = float(dta['T_Netto'][i])
                    ts = float(dta['#TS'][i])
                except:
                    verb('ERROR: Could not calculate timestamps for text Number '+str(i))

                anz_total = anz_total + 1
                dur_total = dur_total + dur

                if ts > day_time:
                    anz_day = anz_day + 1
                    dur_day = dur_day + dur
                if ts > week_time:
                    anz_week = anz_week + 1
                    dur_week = dur_week + dur

            dic_total = {'H':math.trunc(dur_total/3600),'M':math.trunc((dur_total % 3600)/60),'S':math.trunc(dur_total % 60)}
            dic_week = {'H':math.trunc(dur_week/3600),'M':math.trunc((dur_week % 3600)/60),'S':math.trunc(dur_week % 60)}
            dic_day = {'H':math.trunc(dur_day/3600),'M':math.trunc((dur_day % 3600)/60),'S':math.trunc(dur_day % 60)}

           
            d_total = '{0:02}'.format(dic_total['H'])+':'+'{0:02}'.format(dic_total['M'])+':'+'{0:02}'.format(dic_total['S'])
            d_week = '{0:02}'.format(dic_week['H'])+':'+'{0:02}'.format(dic_week['M'])+':'+'{0:02}'.format(dic_week['S'])
            d_day = '{0:02}'.format(dic_day['H'])+':'+'{0:02}'.format(dic_day['M'])+':'+'{0:02}'.format(dic_day['S'])

            if anz_total > 0:
                m_total = time.strftime("%H:%M:%S",time.gmtime(dur_total/anz_total))
            else:
                m_total = '-'
            if anz_week > 0:
                m_week = time.strftime("%H:%M:%S",time.gmtime(dur_week/anz_week))
            else:
                m_week = '-'
            if anz_day > 0:
                m_day = time.strftime("%H:%M:%S",time.gmtime(dur_day/anz_day))
            else:
                m_day = '-'

                        
            outtext = 'Coder Statistics:\n-----------------\n\n'
            outtext = outtext + '{0:20}'.format('Period')+'{0:20}'.format('Number of Texts')+'{0:20}'.format('Duration')+'{0:20}'.format('Time per Text')
            outtext = outtext + '\n--------------------------------------------------------------------------------\n'
            outtext = outtext + '{0:20}'.format('All Time')+'{0:>15}'.format(str(anz_total))+'{0:>13}'.format(d_total)+'{0:>20}'.format(m_total)+'\n'
            outtext = outtext + '{0:20}'.format('This Week')+'{0:>15}'.format(str(anz_week))+'{0:>13}'.format(d_week)+'{0:>20}'.format(m_week)+'\n'
            outtext = outtext + '{0:20}'.format('Today (last 24h)')+'{0:>15}'.format(str(anz_day))+'{0:>13}'.format(d_day)+'{0:>20}'.format(m_day)+'\n'

        sess_time = time.time()-settings['Session_Start']
        s_time = time.strftime("%H:%M:%S",time.gmtime(sess_time))
        outtext = outtext + '\n\nDuration of the current coding session (without breaks): '+s_time

        if available('Todo'):
            try:
                tmp = open(settings['Todo'],'r')
                tod = tmp.readlines()
                tmp.close()
                remain = len(tod)
                outtext = outtext + '\n\nRemaining Texts on your list: '+str(remain)
            except:
                outtext = outtext + '\n\nNo Todo-List found. Not able to gather remaining texts.'
            
        
        self.display_text(outtext,font=('Courier',10,'bold'),bg="#eeffff")


    def spss_syntax(self,fname = ''):
        log('Calling Function: SPSS Syntax')
        if fname == '':
            fname = tkFileDialog.asksaveasfilename(**{'defaultextension':'.sps',
                                                      'filetypes':[('SPSS Syntax file','.sps'),('All Files','.*')]})

        if not fname == '':
            multi_items = settings['Multi_Items']
            liste = codebook.keys()
            syntax_file = open(fname,'w')
            for element in sorted(liste):
                if element in codebook.keys():
                    if element in multi_items:
                        for i in range(len(codebook[element][3])):
                            ausp = codebook[element][3][i]
                            option = codebook[element][2][i]
                            option = option.replace("'"," ")
                            option = option.replace("\n"," / ")
                            vname = element + '_' + ausp
                            syntax_file.write('\nVARIABLE LABELS ')
                            syntax_file.write(vname)
                            syntax_file.write(" '")
                            syntax_file.write(codebook[element][0][:-1]+' - '+option)
                            syntax_file.write("'.\n")
                            syntax_file.write('VARIABLE LEVEL '+vname+'(NOMINAL).\n')
                            syntax_file.write('VALUE LABELS '+vname+' 0 "not selected" 1 "selected".\n\n')                   
                    else:       
                        syntax_file.write('\nVARIABLE LABELS ')
                        syntax_file.write(element)
                        syntax_file.write(" '")
                        syntax_file.write(codebook[element][0][:-1])
                        syntax_file.write("'.\n")
                        if len(codebook[element][2]) > 0:
                            syntax_file.write('MISSING VALUES ')
                            syntax_file.write(element)
                            syntax_file.write(' (98).\n')
                            syntax_file.write('VARIABLE LEVEL '+element+'(NOMINAL).\n')
                            syntax_file.write('VALUE LABELS ')
                            syntax_file.write(element)
                            for i in range(0,len(codebook[element][2])):
                                syntax_file.write(" '")
                                syntax_file.write(codebook[element][3][i])
                                syntax_file.write("' '")
                                option = codebook[element][2][i]
                                option = option.replace("'"," ")
                                option = option.replace("\n"," / ")                             
                                syntax_file.write(option)
                                syntax_file.write("'")
                                if i < len(codebook[element][2])-1:
                                    syntax_file.write("\n")
                                else:
                                    syntax_file.write(".\n\n\n")
                else:
                    syntax_file.write('*CAUTION. MISSING VARIABLE IN SYNTAX: ')
                    syntax_file.write(element)
                    syntax_file.write(".\n\n")
                   
                syntax_file.write('\n')
            syntax_file.write('\n\n')
            syntax_file.close()
            self.message("SPSS Done",2)
            
                    


    def store_coding(self,fname = ''):
        log('Calling Function: Store text')
        if fname == '':
            fname = tkFileDialog.asksaveasfilename(**{'defaultextension':'.cod',
                                                      'filetypes':[('Angrist Coding','.cod'),('All Files','.*')]})

        if not fname == '':
            if settings['Break'] > 0: ##Update Break time if coder stores from break
                zeit = time.time() - settings['Break']
                settings['Break_Time'] = settings['Break_Time'] + zeit
            dauer = time.time()-storage['#TS'][1]
            dauer_net = dauer - settings['Break_Time']
            storage['#T_Brutto'] = dauer
            storage['#T_Netto'] = dauer_net
            storage['#T_Break'] = settings['Break_Time']
            
            storage['#TS2']=(time.ctime(), time.time())
            out = open(fname,'w')
            out.write(str(storage))
            out.close()
            verb('Stored: '+bereinigen(fname))
        else:
            verb('ERROR: Could not store file. No filename.')

    def load_coding(self,fname = ''):
        global prog_pos
        global dta_pos
        global storage
        global settings
        log('Calling Function: Load text')

        if fname == '':
            fname = tkFileDialog.askopenfilename(**{'defaultextension':'.cod',
                                                    'filetypes':[('Angrist Coding','.cod'),('All Files','.*')]})

        if fname == '':
            if available('Out_Tmp'):
                fname = settings['Out_Tmp']

        if not fname == '':
            inp = open(fname,'r')
            s = inp.readline()
            inp.close()
            storage = eval(s)                
            verb(baum_schreiben(storage))
            settings['Break_Time'] = 0

            if '#T_Netto' in storage.keys():
                duration = storage['#T_Netto']
                storage['#TS'] = (storage['#TS'][0],time.time()-duration)
                verb('Previous net time found. Corrected current coding for '+str(duration)+' seconds previous coding')
            elif '#TS2' in storage.keys():
                duration = storage['#TS2'][1] - storage['#TS'][1]
                storage['#TS'] = (storage['#TS'][0],time.time()-duration)
                verb('Previous timestamps found. Corrected current timestamp to account for '+str(duration)+' seconds previous coding')
            else:
                storage['#TS'] = (time.ctime(), time.time())
                verb('No previous Timestamps found. File corrupt. Lost information on previous coding time')

            entered_id = storage['ID']
                    
            if len(entered_id) > 1:
                fname = settings['Text_Folder'] + entered_id +'.txt'
                verb('-Loading File: '+fname)
                settings['Fulltext'] = artikelholen(storage['ID'])
                storage['Fulltext'] = bereinigen(settings['Fulltext'])
                settings['PDF-Page'] = os.getcwd()+'\\'+settings['Text_Folder']+storage['ID'][:-4]+'.jpg'
            else:
                self.message("Runtime-Error03")

            verb('--Loaded coding successfully')

            if settings['Fulltext'] == '':
                verb('---No Text found')
                if self.message('Runtime-Error06',3):
                    self.clean_up_all()
                    self.ausblenden()
                    self.load_countryspec()
                    prog_pos = settings['First_Page']  #Go to the page set as first page of the analysis
                    dta_pos = ['-','-','-','-']
                    self.ask()
            else:
                verb('---Text found')
                self.ausblenden()
                self.anzeigen(settings['Fulltext'])
                self.clean_up_all()
                self.load_countryspec()
                prog_pos = settings['First_Page']
                dta_pos = ['-','-','-','-']
                verb('Set Program Position: '+prog_pos)
                self.ask()
      

    def debug_on(self,event=0):
        self.deb.grid()

    def display_text(self, content = "No text to display",title="Debugging-Information",bg="#ffffcc",font=('Arial',9)):
        self.infobox = Toplevel(self)
        self.infobox.rowconfigure(1, weight=1)
        self.infobox.columnconfigure(1, weight=1)
        self.infobox.title(title)
        self.infobox.ysc = Scrollbar(self.infobox, orient=VERTICAL)
        self.infobox.ysc.grid(row=1,column=2,sticky=W+N+S)
        self.infobox.info = Text(self.infobox,width=100,height=30,bg=bg,wrap=WORD, yscrollcommand=self.infobox.ysc.set,font=font,takefocus=0)
        self.infobox.info.grid(row=1,column=1,sticky=N+E+S+W)
        self.infobox.ysc["command"]=self.infobox.info.yview

        self.infobox.info.tag_config('errormsg',background="#ffcccc", font = ("Arial",9, "bold"))
        self.infobox.info.tag_config('functcall',foreground="#0000cc", font = ("Arial",9, "bold"))
        
        self.infobox.info.insert(END,content)
        self.infobox.info.see(END)

        start = '1.1'
        while not start == '':
            a = self.infobox.info.search('ERROR',start,END)
            if not a == '':
                start_z = str(a) + ' linestart'
                end_z = str(a) + ' lineend'
                self.infobox.info.tag_add('errormsg',start_z,end_z)
                start = end_z
            else:
                start = a
        start = '1.1'
        while not start == '':
            a = self.infobox.info.search('Function',start,END)
            if not a == '':
                start_z = str(a) + ' linestart'
                end_z = str(a) + ' lineend'
                self.infobox.info.tag_add('functcall',start_z,end_z)
                start = end_z
            else:
                start = a
                
    def show_path(self,event=0):
        global settings
        out = str(settings['Path_Log'])
        out = out + ('\n\nVisited pages:'+str(settings['Page_History']))
        self.display_text(out)

    def show_verb(self,event=0):
        global settings
        out = str(settings['Verb_Log'])
        self.display_text(out)

    def show_storage(self,event=0):
        global storage
        out = str(baum_schreiben(storage,trunc=80))
        self.display_text(out,font=('Arial',settings['Fontsize']))

    def show_settings(self,event=0):
        tmp_dic = {}
        for c in settings.keys():
            if not c in ['Verb_Log','Path_Log']:
                tmp_dic[c] = settings[c]
        out = str(baum_schreiben(tmp_dic))
        self.display_text(out)

    def show_parameters(self):
        global dta_pos
        global prog_pos
        global settings
        out='Current location within program and data:\n----------------------------\n'
        out = out + 'Dta_Pos: '+str(dta_pos)
        out = out + '\nProg_Pos: '+prog_pos
        out = out + '\nPage: '+str(settings['Curr_Page'])
        out = out + '\n\n\nCurrent Subtree:\n----------------------------\n'
        out = out + str(baum_schreiben(curr()))
        self.display_text(out)

    def reset_coding(self):
        global dta_pos
        global prog_pos
        #dta_pos=['-','-','-','-']
        #prog_pos = settings['First_Page']
        ##Send Log-File
        fname = '..\\'+settings['Coder'] + str(int(time.time())) + '.txt'
        store_name = '_tmp_'+settings['Coder'] + str(int(time.time())) + '.txt'
        out = open(fname,'w')
        out.write('Automatisch generiertes Logfile.\n')
        out.write(time.ctime()+'\n----------------------------\n')
        out.write(str(settings['Verb_Log']))
        out.close()
        self.store_coding(store_name)
        self.load_coding(store_name)
        

    def locate(self,l1,l2,l3):
        log('Calling Function: Locate with '+l1+' and '+l2)
        self.f_location.angabe.delete('1.0', END)
        lev = 0
        if dta_pos[0] == '-':
            lev = 0
        elif dta_pos[2] == '-':
            lev = 1
        elif dta_pos[4] == '-':
            lev = 2
        if lev > 0:
            self.f_location.angabe.insert(INSERT, self.namegetter('Location',l1)+'\n','fett')
            self.f_location.angabe.insert(INSERT, self.namegetter('Location',l2)+' ')
            self.f_location.angabe.insert(INSERT, storage[dta_pos[0]][dta_pos[1]]['#TN'])
        if lev > 1:
            self.f_location.angabe.insert(INSERT, ' '+self.namegetter('Location',l3)+' ')
            self.f_location.angabe.insert(INSERT, storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['#TN'])
        if lev == 0:
            self.f_location.angabe.insert(INSERT, 'Text ID: '+str(storage['ID']))
       
    def show_review(self,level,rm=1,height=6):
        #Show the list of previously coded elements on a level below the current one
        global prog_pos
        log('Calling Function: Show_Review')
        try:
            self.f_review.A_Liste.destroy()
            self.f_review.scroll_A_Liste.destroy()
            self.f_review.b_remove.grid_remove()            
        except:
            verb('No List to remove')
        
        self.f_review.A_Liste = Listbox(self.f_review, selectmode = BROWSE, height=height, width=80)
        self.f_review.A_Liste.grid(row=0,rowspan=3, column=0, sticky=W+E)
        self.f_review.scroll_A_Liste = Scrollbar(self.f_review, orient=VERTICAL, command=self.f_review.A_Liste.yview)
        self.f_review.scroll_A_Liste.grid(row=0,rowspan=3, column=1, sticky=W+N+S)
        self.f_review.A_Liste["yscrollcommand"] = self.f_review.scroll_A_Liste.set
        self.f_review.b_remove = Button(self.f_review, text = "Remove", width=6, command=CMD(self.remove_item,level,height), takefocus = 0)
        self.f_review.b_remove.grid(row=0,column=2,sticky=N+E)
        self.f_review.b_edit = Button(self.f_review, text = "Edit", width=6, command=CMD(self.edit_item,level), takefocus = 0)
        self.f_review.b_edit.grid(row=1,column=2,sticky=N+E)

        curr_tree = curr()

        if type(level) == str:
            level = [level]

        for l in level:
            if l in curr_tree.keys():
                for item in sorted(curr_tree[l].keys()):
                    lab = '<'+item+'>: '+curr_tree[l][item]['#TN']
                    self.f_review.A_Liste.insert(END,lab)
        if rm == 0:
            self.f_review.b_remove.grid_remove()
        else:
            self.f_review.b_remove.grid()

    def hide_review(self): #Hide the review-list
        global prog_pos
        log('Calling Function: Hide Review')
        try:
            self.f_review.A_Liste.destroy()
            self.f_review.scroll_A_Liste.destroy()
            self.f_review.b_remove.grid_remove()
            self.f_review.b_edit.grid_remove()
        except:
            verb('No List to remove')
        self.f_review["height"]=20

    def remove_item(self,level,height):
        #Remove an item from the review-List. Depending on level and requirements this function might need adaption.
        global prog_pos
        log('Calling Function: Remove_Item')
        listsel = self.f_review.A_Liste.curselection()
        if len(listsel) == 0:
            self.message("Invalid-Selection01")
        else:
            select = self.f_review.A_Liste.get(listsel[0])
            verb(str(select))
            c1 = 1
            c2 = select.find('>')
            code = select[c1:c2]
            verb('Code to remove: '+code)

            if type(level) == str:
                level = [level]

            for l in level:
                if dta_pos[0] == '-':
                    if l in storage.keys():
                        if code in storage[l].keys():
                            del storage[l][code]
                            verb('Removing Element: '+code+ 'on Level: '+l)
                            if len(storage[l].keys()) == 0:
                                del storage[l]
                elif dta_pos[2] == '-':
                    if l in storage[dta_pos[0]][dta_pos[1]].keys():
                        if code in storage[dta_pos[0]][dta_pos[1]][l].keys():
                            del storage[dta_pos[0]][dta_pos[1]][l][code]
                            verb('Removing Element: '+code+ 'on Level: '+l)
                            if len(storage[dta_pos[0]][dta_pos[1]][l].keys()) == 0:
                                del storage[dta_pos[0]][dta_pos[1]][l]
                elif dta_pos[4] == '-':
                    if l in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                        if code in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][l].keys():
                            del storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][l][code]
                            verb('Removing Element: '+code+ 'on Level: '+l)
                            if len(storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][l].keys()) == 0:
                                del storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][l]
           
            self.hide_review()
            self.show_review(level,1,height)
            storage['Remove_item'] = storage['Remove_item'] + 1


    def edit_item(self,level):
        #Remove an item from the review-List. Depending on level and requirements this function might need adaption.
        global prog_pos
        global dta_pos
        log('Calling Function: Edit_Item')
        listsel = self.f_review.A_Liste.curselection()
        if len(listsel) == 0:
            self.message("Invalid-Selection01")
        else:
            select = self.f_review.A_Liste.get(listsel[0])
            verb(str(select))
            c1 = 1
            c2 = select.find('>')
            code = select[c1:c2]
            verb('Code to Edit: '+code)

            if type(level) == str:
                level = [level]

            for l in level:
                if dta_pos[0] == '-':
                    if l in storage.keys():
                        if code in storage[l].keys():
                            verb('Editing Element: '+code+ 'on Level: '+l)
                            dta_pos = [l,code,'-','-']
                elif dta_pos[2] == '-':
                    if l in storage[dta_pos[0]][dta_pos[1]].keys():
                        if code in storage[dta_pos[0]][dta_pos[1]][l].keys():
                            verb('Editing Element: '+code+ 'on Level: '+l)
                            dta_pos = [dta_pos[0],dta_pos[1],l,code,'-','-']
                elif dta_pos[4] == '-':
                    if l in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                        if code in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][l].keys():
                            verb('Editing Element: '+code+ 'on Level: '+l)
                            dta_pos = [dta_pos[0],dta_pos[1],[dta_pos[2]],[dta_pos[3]],l,code,'-','-']

        if dta_pos[0]=='Speaker' and dta_pos[2]=='-':
            prog_pos = 's_identity'
            if 'HL_Start' in storage[dta_pos[0]][dta_pos[1]]:
                self.Artikel.tag_add('Spr',storage[dta_pos[0]][dta_pos[1]]['HL_Start'],
                                     storage[dta_pos[0]][dta_pos[1]]['HL_End'])
        elif dta_pos[0]=='Speaker' and dta_pos[2]=='Issue':
            prog_pos = 'i_identity'
            if 'HL_Start' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]:
                self.Artikel.tag_add('Iss',storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['HL_Start'],
                                     storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['HL_End'])
        elif dta_pos[0]=='Speaker' and dta_pos[2]=='Target':
            prog_pos = 'agree'
            if 'HL_Start' in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]:
                self.Artikel.tag_add('Tgt',storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['HL_Start'],
                                     storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]['HL_End'])

        self.clean_up_all()            
        self.ask()

    def level_up(self):
        log('Calling Function: Level Up')
        global dta_pos 
        laenge = len(dta_pos)
        minstrich = 0
        for i in range(0,laenge):
            if dta_pos[i] == '-' and minstrich == 0:
                minstrich = i
        if minstrich == 0:
            minstrich = laenge        
        for i in range(minstrich-2,laenge):
            dta_pos[i] = '-'

    def level_down(self,variable,level): ##Change the level of analysis by one. If successful, the function returns 1
        log('Calling Function: Level Down')
        global dta_pos
        accept = 1
        ld_type = 'other'
        idvar = self.store_var(variable,store=0)
        tstamp = time.time()
        if type(idvar) == tuple:
            ident = str(idvar[1])
            if ident == '[]' or ident == '':
                accept = 0
            tname = str(idvar[0])
        elif type(idvar) == dict:
            if idvar == {}:
                accept = 0
                verb('ERROR: No selection')
            else:
                ident = idvar['ID']
                tname = idvar['Label']
                if level == 'Statement':
                    if idvar['Typ']=='Iss':
                        level = 'Issue'
                    elif idvar['Typ']=='Tgt':
                        level = 'Target'
                    else:
                        verb('ERROR: No valid statement')
                ld_type = 'highlight'
        elif type(idvar) == str or type(idvar) == unicode:
            ident = bereinigen(idvar)
            tname = bereinigen(idvar)
            if ident == '':
                accept = 0

        if accept == 1:
            if '-' in dta_pos:
                minstrich = len(dta_pos)
                for i in range(0,len(dta_pos)):
                    if dta_pos[i] == '-' and minstrich == len(dta_pos):
                        minstrich = i
            else:
                minstrich = len(dta_pos)
                dta_pos.append('-')
                dta_pos.append('-')

            if minstrich == 0:
                if ld_type == 'highlight':
                    verb('--Taking label from highlight')
                    if not level in storage.keys():
                        storage[level]={}
                    storage[level][ident]={}            
                else:
                    idlab = ident
                    idnr = 1
                    ident = idlab + "{0:02}".format(idnr)
                    if level in storage.keys():
                        while ident in storage[level].keys():
                            idnr = idnr + 1
                            ident = idlab + "{0:02}".format(idnr)
                    else:
                        storage[level] = {}
                        storage[level][ident] = {}
                storage[level][ident]['#TN'] = tname
                storage[level][ident]['#TS'] = tstamp
            elif minstrich == 2:
                if ld_type == 'highlight':
                    verb('--Taking label from highlight')
                    if not level in storage[dta_pos[0]][dta_pos[1]].keys():
                        storage[dta_pos[0]][dta_pos[1]][level] = {}
                    storage[dta_pos[0]][dta_pos[1]][level][ident] = {}

                else:                
                    if level in storage[dta_pos[0]][dta_pos[1]].keys():
                        while ident in storage[dta_pos[0]][dta_pos[1]][level].keys():
                            ident = ident + 'x'
                        storage[dta_pos[0]][dta_pos[1]][level][ident] = {}
                    else:
                        storage[dta_pos[0]][dta_pos[1]][level] = {}
                        storage[dta_pos[0]][dta_pos[1]][level][ident] = {}
                if len(dta_pos) < 5:
                    dta_pos = dta_pos + ['-','-']
                storage[dta_pos[0]][dta_pos[1]][level][ident]['#TN'] = tname
                storage[dta_pos[0]][dta_pos[1]][level][ident]['#TS'] = tstamp
            elif minstrich == 4:
                if level in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                    while ident in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][level].keys():
                        ident = ident + 'x'
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][level][ident] = {}
                else:
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][level] = {}
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][level][ident] = {}
                if len(dta_pos) < 7:
                    dta_pos = dta_pos + ['-','-']
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][level][ident]['#TN'] = tname
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][level][ident]['#TS'] = tstamp
            elif minstrich == 6:
                if level in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]].keys():
                    while ident in storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][dta_pos[4]][dta_pos[5]][level].keys():
                        ident = ident + 'x'
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][dta_pos[4]][dta_pos[5]][level][ident] = {}
                else:
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][dta_pos[4]][dta_pos[5]][level] = {}
                    storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][dta_pos[4]][dta_pos[5]][level][ident] = {}
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][dta_pos[4]][dta_pos[5]][level][ident]['#TN'] = tname
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][dta_pos[4]][dta_pos[5]][level][ident]['#TS'] = tstamp

            dta_pos[minstrich] = level
            dta_pos[minstrich+1] = ident          
        return accept
        

    def buttons(self, check=1, abort=0, back=1, pause=1):
        global codebook
        log('--Setting Buttons: Check='+str(check)+'; Abort='+str(abort)+'; Back='+str(back)+'; Break='+str(pause),pos=0)
        if 'Buttons' in codebook.keys():
            if len(codebook['Buttons'][2])>3:
                self.f_bottomline.b_check["text"] = codebook['Buttons'][2][0]
                self.f_bottomline.b_abort["text"] = codebook['Buttons'][2][1]
                self.f_bottomline.b_back["text"] = codebook['Buttons'][2][2]
                self.f_bottomline.b_break["text"] = codebook['Buttons'][2][3]
            else:
                verb('ERROR: The variable "Buttons" in the codebook should contain at least four options')
        self.f_bottomline.b_abort["bg"] = settings['BG_Color']
        if check == 1:
            #self.f_bottomline.b_check.grid()
            self.f_bottomline.b_check['state']=NORMAL
        else:
            #self.f_bottomline.b_check.grid_remove()
            self.f_bottomline.b_check['state']=DISABLED
        if abort == 1:
            #self.f_bottomline.b_abort.grid()
            self.f_bottomline.b_abort['state']=NORMAL
            self.f_bottomline.b_abort['bd']=2
        else:
            #self.f_bottomline.b_abort.grid_remove()
            self.f_bottomline.b_abort['state']=DISABLED
            self.f_bottomline.b_abort['bd']=0
        if back == 1:
            #self.f_bottomline.b_back.grid()
            self.f_bottomline.b_back['state']=NORMAL
        else:
            #self.f_bottomline.b_back.grid_remove()
            self.f_bottomline.b_back['state']=DISABLED
        if pause == 1:
            #self.f_bottomline.b_break.grid()
            self.f_bottomline.b_break['state']=NORMAL
        else:
            #self.f_bottomline.b_break.grid_remove()
            self.f_bottomline.b_break['state']=DISABLED
            

    def store_var_all(self,setdef=0): ##Storing all variables on this page
        log('--Store_Var_All:',pos=0)
        global prog_pos
        global dta_pos
        for i in range(len(settings['Curr_Page'])):
            anzeige = settings['Curr_Page'][i]
            if len(anzeige[1]) > 1:
                if anzeige[0] == 'list':
                    self.store_var(anzeige[2],i,setdef)
                else:
                    self.store_var(anzeige[1],i,setdef)

                
    def store_var(self,variabel='',pos=-1,setdef=0,store=1): ##Storing values from all question-types.
        log('----Storing Variable: '+variabel,pos=0)
        wert = 'invalid'
        if pos == -1:
            for i in range(len(settings['Curr_Page'])):
                if settings['Curr_Page'][i][1] == variabel:
                    pos = i
                elif len(settings['Curr_Page'][i]) == 3:
                    if settings['Curr_Page'][i][2] == variabel:
                        pos = i
        elif variabel == '':            
            variabel = settings['Curr_Page'][pos][1]
            
        if pos == -1 or variabel == '':
            verb('ERROR: could not find the specified item to store. Position: '+str(pos)+'; Variable: '+variabel)
        else:
            element = settings['Curr_Page'][pos]
            if element[0] == 'dd':
                wert = (settings['Input'][pos].get(),self.codegetter(variabel,settings['Input'][pos].get()))
                verb('    Stored Variable:'+variabel+': '+str(wert),1)                       

            elif element[0] == 'txt':
                if pos == 0:
                    wert = bereinigen(self.f_questions.txt1.get())
                elif pos == 1:
                    wert = bereinigen(self.f_questions.txt2.get())
                elif pos == 2:
                    wert = bereinigen(self.f_questions.txt3.get())                   
                verb('    Stored Variable:'+variabel+': '+str(wert),1)

            elif element[0] == 'txt2':
                if pos == 0:
                    wert = bereinigen(self.f_questions.txt1.get('1.0',END))
                elif pos == 1:
                    wert = bereinigen(self.f_questions.txt2.get('1.0',END))
                elif pos == 2:
                    wert = bereinigen(self.f_questions.txt3.get('1.0',END))
                verb('    Stored Variable:'+variabel+': '+str(wert),1)

            elif element[0] == 'rb':
                wert = (self.namegetter(variabel,settings['Input'][pos].get()),settings['Input'][pos].get())
                verb('    Stored Variable:'+variabel+': '+str(wert),1)
                
                                    
            elif element[0] == 'spr':
                wert = {}
                wert[codebook[variabel][3][0]] = (bereinigen(settings['Akt_a'].get()),self.codegetter('Akt_a',settings['Akt_a'].get()))
                wert[codebook[variabel][3][1]] = (bereinigen(settings['Akt_b'].get()),self.codegetter('Akt_b',settings['Akt_b'].get()))
                wert[codebook[variabel][3][2]] = (bereinigen(settings['Akt_c'].get()),self.codegetter('Akt_c',settings['Akt_c'].get()))
                verb('    Stored Variable:'+variabel+': '+str(wert),1)

            elif element[0] in ['rating','sd','cb']:
                wert = {}
                for i in range(len(codebook[variabel][3])):
                    code = codebook[variabel][3][i]
                    wert[code] = settings['Input'][pos][i].get()
                verb('    Stored Variable:'+variabel+': '+str(wert),1)                  
            
            elif element[0] in ['list','listseek']:
                listvar = settings['Curr_Page'][0][2]
                variabel = settings['Curr_Page'][0][1]
                listsel = self.f_questions.Aspliste.curselection()
                Namen = []
                Codes = []
                for selection in listsel:
                    Namen.append(self.f_questions.Aspliste.get(selection))
                    Codes.append(self.codegetter(listvar, self.f_questions.Aspliste.get(selection)))
                wert = (Namen,Codes)
                verb('    Stored Variable:'+variabel+': '+str(wert),1)

            elif element[0] in ['listadd']:
                listvar = settings['Curr_Page'][0][2]
                variabel = settings['Curr_Page'][0][1]
                listsel = range(0,self.f_questions.Itmliste.size()) ###Get all!
                Namen = []
                Codes = []
                for i in listsel:
                    selection = str(i)
                    Namen.append(self.f_questions.Itmliste.get(selection))
                    c = self.codegetter(listvar, self.f_questions.Itmliste.get(selection))
                    if c == '':
                        c = self.f_questions.Itmliste.get(selection)
                    Codes.append(c)
                wert = (Namen,Codes)
                verb('    Stored Variable:'+variabel+': '+str(wert),1)

            elif element[0] == 'change':
                verb('Storing changed text')
                verb('Output File: '+settings['Filename'])
                arttext = self.Artikel.get("1.0",END)
                settings['Fulltext'] = arttext
                update_text(arttext)

                
            elif element[0] == 'unit_auswahl':
                if len(self.f_questions.Aspliste.curselection())>0:
                    selection = self.f_questions.Aspliste.curselection()[0]
                    label = self.f_questions.Aspliste.get(selection)
                    verb('List Selection:'+str(label))
                    tags = element[2]
                    for t in tags:
                        if t in storage['Highlight'].keys():
                            for e in storage['Highlight'][t].keys():
                                if 'Label' in storage['Highlight'][t][e].keys():
                                    if storage['Highlight'][t][e]['Label'] == label:
                                        verb(baum_schreiben(storage['Highlight'][t][e]))
                                        wert = storage['Highlight'][t][e]
                                        self.Artikel.tag_add(wert['Typ'],wert['Start'],wert['End'])
                else:
                    wert = {}
                verb('    Stored Variable:'+variabel+': '+str(wert),1)

            elif element[0] == 'unit_mark':
                tags = element[2]
                verb('Storing Text highlights')
                verb('--Storing selection for tags: '+str(tags))

                for t in tags:
                    if t in storage['Highlight'].keys():
                        if not variabel == 'Add_Items':
                            verb('--Removing previously highlighted but uncoded items for: '+t)
                            for e in storage['Highlight'][t].keys():
                                if 'Done' in storage['Highlight'][t][e].keys():
                                    if storage['Highlight'][t][e]['Done']==0:
                                        del storage['Highlight'][t][e]
                                        verb('----Removed: '+e)
                                else:
                                    storage['Highlight'][t][e]['Done']=1
                    else:
                        storage['Highlight'][t] = {}
                    
                rem = []
                try:
                    for tag in tags:
                        verb('Looking for highlights: '+tag)
                        i = 0
                        while i in range(0,len(self.Artikel.tag_ranges(tag))):
                            i0 = i/2+1
                            ident = tag + "{0:02}".format(i0)
                            while ident in storage['Highlight'][tag].keys():
                                i0 = i0 + 1
                                ident = tag + "{0:02}".format(i0)                        
                            storage['Highlight'][tag][ident] = {}
                            start_tag = self.Artikel.tag_ranges(tag)[i]
                            end_tag = self.Artikel.tag_ranges(tag)[i+1]
                            start_z = str(start_tag) + ' linestart'
                            end_z = str(end_tag) + ' lineend'
                            verb('Found: '+str(tag)+ '; ' + str(i)+ '; ' +
                                 str(i/2)+ '; From: ' + str(start_tag)+
                                 '; To: ' + str(end_tag))
                            verb('Naming it: '+ident)
                            sel_txt = bereinigen(self.Artikel.get(start_tag,end_tag))
                            verb('String: '+sel_txt)
                            labeltext = tag + ': ' + sel_txt[:40]
                            if len(sel_txt) > 40: labeltext = labeltext + '...'
                            select = bereinigen(self.Artikel.get(start_z,end_z))
                            verb('In Paragraph: '+select)
                            storage['Highlight'][tag][ident]['Start'] = str(start_tag)
                            storage['Highlight'][tag][ident]['End'] = str(end_tag)
                            storage['Highlight'][tag][ident]['Fulltext'] = select
                            storage['Highlight'][tag][ident]['Wording'] = sel_txt
                            storage['Highlight'][tag][ident]['Done'] = 0
                            storage['Highlight'][tag][ident]['Label'] = labeltext
                            storage['Highlight'][tag][ident]['Typ']=tag
                            storage['Highlight'][tag][ident]['ID']=ident
                            
                            rem.append((tag,start_tag,end_tag))
                            i = i + 2
                except:
                    verb('Not able to store highlighted text')

                for e in rem:
                    verb('Cleaning up tags')
                    self.Artikel.tag_remove(e[0],e[1],e[2])              

                verb(baum_schreiben(storage['Highlight']))
                verb(str(len(storage['Highlight'][t].keys()))+' Units highlighted')
                store = 0 #There is no meaningful value for the question variable


        if store == 1:
            if not dta_pos[3] == '-':
                storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]][variabel] = wert
            elif not dta_pos[1] == '-':
                storage[dta_pos[0]][dta_pos[1]][variabel] = wert
            else:
                storage[variabel] = wert
            verb('    Stored in storage',1)
        if setdef == 1:
            if type(wert) == list:
                def_val[variabel] = get_unique(wert)
                verb('    -Setting Default: '+str(def_val[variabel]),1)
            else:
                def_val[variabel] = wert
                verb('    -Setting Default: '+str(def_val[variabel]),1)
            verb('    Set as Default',1)
        return wert

    def check_entries(self):
        log('--Checking submitted entries',pos=0)
        #Check all entries for validity.
        all_correct = 1 ##Begin with an assumption of innocence
        for i in range(0,len(settings['Curr_Page'])):
            typ = settings['Curr_Page'][i][0]
            if typ == 'rb':
                if settings['Input'][i].get()=='98':
                    verb('Please choose an option vor variable: "' + settings['Curr_Page'][i][1] + '"')
                    self.message('Invalid-Selection02',add=settings['Curr_Page'][i][1])
                    all_correct=0
            if typ == 'dd':
                if self.codegetter(settings['Curr_Page'][i][1],settings['Input'][i].get()) == '98':
                    verb('Please choose an option vor variable: "' + settings['Curr_Page'][i][1] + '"')
                    self.message('Invalid-Selection02',add=settings['Curr_Page'][i][1])
                    all_correct=0
            if typ == 'txt':
                if i == 0:
                    try:
                      verb(bereinigen(self.f_questions.txt1.get()))
                    except:
                        all_correct = 0
                        self.message('Invalid-Selection03')
                if i == 1:
                    try:
                      verb(bereinigen(self.f_questions.txt2.get()))
                    except:
                        all_correct = 0
                        self.message('Invalid-Selection03')
                if i == 2:
                    try:
                      verb(bereinigen(self.f_questions.txt3.get()))
                    except:
                        all_correct = 0
                        self.message('Invalid-Selection03')
            if typ == 'txt2':
                if i == 0:
                    try:
                      verb(bereinigen(self.f_questions.txt1.get('1.0',END)))
                    except:
                        all_correct = 0
                        self.message('Invalid-Selection03')
                if i == 1:
                    try:
                      verb(bereinigen(self.f_questions.txt2.get('1.0',END)))
                    except:
                        all_correct = 0
                        self.message('Invalid-Selection03')
                if i == 2:
                    try:
                      verb(bereinigen(self.f_questions.txt3.get('1.0',END)))
                    except:
                        all_correct = 0
                        self.message('Invalid-Selection03')

            if typ == 'spr':
                wert = {}
                a = self.codegetter('Akt_a',settings['Akt_a'].get())
                b = self.codegetter('Akt_b',settings['Akt_b'].get())
                c = self.codegetter('Akt_c',settings['Akt_c'].get())
                if a == 'akt000':
                    if c == 'orga000':
                        if b == 'fkt000':
                            all_correct = 0
                            self.message('Invalid-Selection02')
        return all_correct

    def clean_up_all(self): ##Clean up the whole page (only question-frame).
        log('--Clean Up All:',pos=0)
        for i in range(0,len(settings['Curr_Page'])):
            typ = settings['Curr_Page'][i][0]
            pos = i + 1
            self.clean_up(typ,pos)

    def clean_up(self,typ='all',pos=0): ##Clean up a specific element on the page (only question_frame)
        log('----Clean Up: Element: '+typ+' Position: '+str(pos))
        try:
            if typ == 'dd':
                if pos == 1:
                    self.f_questions.dd1.destroy()
                    self.f_questions.help1.destroy()
                    self.f_questions.Frage1.delete("1.0",END)
                    if settings['Insecure']=='1':
                        self.f_questions.ins1.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
                if pos == 2:
                    self.f_questions.dd2.destroy()
                    self.f_questions.help2.destroy()
                    self.f_questions.Frage2.delete("1.0",END)
                    if settings['Insecure']=='1':
                        self.f_questions.ins2.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
                if pos == 3:
                    self.f_questions.dd3.destroy()
                    self.f_questions.help3.destroy()
                    self.f_questions.Frage3.delete("1.0",END)
                    if settings['Insecure']=='1':
                        self.f_questions.ins3.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
            elif typ == 'txt' or typ == 'txt2':
                if pos == 1:
                    self.f_questions.txt1.destroy()
                    self.f_questions.help1.destroy()
                    self.f_questions.Frage1.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.getselect1.destroy()
                    except:
                        verb('No Button')
                if pos == 2:
                    self.f_questions.txt2.destroy()
                    self.f_questions.help2.destroy()
                    self.f_questions.Frage2.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.getselect2.destroy()
                    except:
                        verb('No Button')
                if pos == 3:
                    self.f_questions.txt3.destroy()
                    self.f_questions.help3.destroy()
                    self.f_questions.Frage3.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.getselect3.destroy()
                    except:
                        verb('No Button')
            elif typ == 'list':
                self.f_questions.Aspliste.destroy() 
                self.f_questions.scroll_AspListe.destroy()
                self.f_questions.h_Aspliste.destroy()
                self.f_questions.Frage1.delete("1.0",END)    
                for i in settings['Curr_Page']:
                    if i[0] == 'list':
                        i[0] = ''
                        i[1] = ''
            elif typ == 'listseek':
                self.f_questions.Aspliste.destroy() 
                self.f_questions.scroll_AspListe.destroy()
                self.f_questions.h_Aspliste.destroy()
                self.f_questions.seektext.destroy()
                self.f_questions.Frage1.delete("1.0",END)    
                for i in settings['Curr_Page']:
                    if i[0] == 'listseek':
                        i[0] = ''
                        i[1] = ''
            elif typ == 'listadd':
                self.f_questions.Aspliste.destroy()
                self.f_questions.scroll_AspListe.destroy()
                self.f_questions.h_Aspliste.destroy()
                self.f_questions.seektext.destroy()
                self.f_questions.adb.destroy()
                self.f_questions.rb.destroy()
                self.f_questions.Itmliste.destroy()
                self.f_questions.scroll_ItmListe.destroy()
                self.f_questions.Frage1.delete("1.0",END)    
                for i in settings['Curr_Page']:
                    if i[0] == 'listadd':
                        i[0] = ''
                        i[1] = ''
            elif typ == 'unit_auswahl':
                self.f_questions.Aspliste.destroy()
                self.f_questions.scroll_AspListe.destroy()
                self.f_questions.h_Aspliste.destroy()
                self.f_questions.Frage1.delete("1.0",END)
                self.f_questions.fk_hinzu.destroy()
                self.f_questions.fk_weg.destroy()
                self.f_questions.fk_markieren.destroy()
                for i in settings['Curr_Page']:
                    if i[0] == 'list':
                        i[0] = ''
                        i[1] = ''
            elif typ == 'unit_mark':
                self.f_questions.help1.destroy()
                self.f_questions.Frage1.delete("1.0",END)
                settings['Curr_Page'][0] = ['','']
                self.f_questions.bu1_1.destroy()                       
            elif typ == 'change':
                self.f_questions.help1.destroy()
                self.f_questions.Frage1.delete("1.0",END)
                settings['Curr_Page'][0] = ['','']
                self.f_questions.bu1_1.destroy()

            elif typ in ['rb','sd','rating','cb']:
                if pos == 1:
                    self.f_questions.rblist1.destroy()
                    self.f_questions.help1.destroy()
                    self.f_questions.Frage1.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.ins1.destroy()
                    except:
                        verb('No Insec Button')
                if pos == 2:
                    self.f_questions.rblist2.destroy()
                    self.f_questions.help2.destroy()
                    self.f_questions.Frage2.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.ins2.destroy()
                    except:
                        verb('No Insec Button')
                if pos == 3:
                    self.f_questions.rblist3.destroy()
                    self.f_questions.help3.destroy()
                    self.f_questions.Frage3.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.ins3.destroy()
                    except:
                        verb('No Insec Button')
            elif typ == 'bt':
                if pos == 1:
                    self.f_questions.help1.destroy()
                    self.f_questions.Frage1.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.bu1_1.destroy()
                        self.f_questions.bu1_2.destroy()
                        self.f_questions.bu1_3.destroy()
                        self.f_questions.bu1_4.destroy()
                    except:
                        verb('Less than 4 Buttons')
                if pos == 2:
                    self.f_questions.help2.destroy()
                    self.f_questions.Frage2.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.bu2_1.destroy()
                        self.f_questions.bu2_2.destroy()
                        self.f_questions.bu2_3.destroy()
                        self.f_questions.bu2_4.destroy()
                    except:
                        verb('Less than 4 Buttons')
                if pos == 3:
                    self.f_questions.help3.destroy()
                    self.f_questions.Frage3.delete("1.0",END)
                    settings['Curr_Page'][pos-1] = ['','']
                    try:
                        self.f_questions.bu3_1.destroy()
                        self.f_questions.bu3_2.destroy()
                        self.f_questions.bu3_3.destroy()
                        self.f_questions.bu3_4.destroy()
                    except:
                        verb('Less than 4 Buttons')
            elif typ == 'spr':
                self.f_questions.help_spr.destroy()
                self.f_questions.sprecher.destroy()
                for i in settings['Curr_Page']:
                    if i[0] == 'spr':
                        i[0] = ''
                        i[1] = ''
            elif typ == 'val':
                self.f_questions.value.destroy()
                self.f_questions.help_val.destroy()
                for i in settings['Curr_Page']:
                    if i[0] == 'val':
                        i[0] = ''
                        i[1] = ''
            elif typ == 'menu':
                if pos == 1:
                    self.f_questions.mb1.destroy()
                    self.f_questions.help1.destroy()
                    self.f_questions.Frage1.delete("1.0",END)
                    if settings['Insecure']=='1':
                        self.f_questions.ins1.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
                if pos == 2:
                    self.f_questions.mb2.destroy()
                    self.f_questions.help2.destroy()
                    self.f_questions.Frage2.delete("1.0",END)
                    if settings['Insecure']=='1':
                        self.f_questions.ins2.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
                if pos == 3:
                    self.f_questions.mb3.destroy()
                    self.f_questions.help3.destroy()
                    self.f_questions.Frage3.delete("1.0",END)
                    if settings['Insecure']=='1':
                        self.f_questions.ins3.destroy()
                    settings['Curr_Page'][pos-1] = ['','']

            else:
                if settings['Verbose'] == '1':
                    verb('ERROR: Unknown Element. Cannot clean up')
        except:
            verb('ERROR: Element not found')


    def codegetter(self,variabel,item): #Get the code of a value when only the label is known
        log('Calling Function: Codegetter for Variable: '+variabel+' and Value: '+str(item),pos=0)
        varindex = ''
        for i in range(0,len(codebook[variabel][2])):
            try:
                if bereinigen(codebook[variabel][2][i]) == bereinigen(item):
                    varindex = codebook[variabel][3][i]
            except:
                varindex = 'special character!'

        if varindex == '':
            if settings['Verbose'] == '1':
                verb('--Error: Code not found for:'+str(item))
        else:
            verb('--Code identified: '+str(varindex))           
        return varindex

    def namegetter(self,variabel,item): #Get the label of a value when only the code is known
        log('Calling Function: Namegetter for Variable: '+variabel+' and Value: '+str(item),pos=0)
        varindex = ''
        for i in range(0,len(codebook[variabel][2])):
            try:
                if codebook[variabel][3][i] == item:
                    varindex = codebook[variabel][2][i]
            except:
                varindex = 'special character!'

        if varindex == '':
            verb('--ERROR: Name not found for:'+str(item)+' (Values:'+str(codebook[variabel][2])+')')
        else:
            verb('--Name identified: '+str(varindex))
        return varindex



############################################
##                                        ##
##       Grundfunktionen                  ##
##                                        ##
############################################


    def anzeigen(self,text): ##Display the text
        log('Calling Function: Anzeigen')
        global def_val
        global settings

        try:
            if available('Text_Encoding'):        
                text = text.decode(settings['Text_Encoding'],'ignore')
                text = text.encode('latin-1','ignore')
        except:
            verb('ERROR: Problem occurred during decoding the text')
            text = bereinigen(text,lb=1,uml=1)

        if storage['ID'][:5] == 'au_kr':
            text = text.replace(chr(132),'"')
            text = text.replace(chr(147),'"')
                
        verb('Displaying text. Length: '+str(len(text))+
             '; First 100 Characters: \n'+text)
        self.ausblenden() ##First try to remove the text to prevent redundancy

        cols = [3,4]       
        
        self.yscroller = Scrollbar(self, orient=VERTICAL)
        self.yscroller.grid(row=1, rowspan=6, column=cols[1], sticky=W+N+S)
        self.Artikel = Text(self, width=80, height=30, bg='#ffffff', wrap=WORD,
                            yscrollcommand=self.yscroller.set, relief=GROOVE,
                            font = (settings['Font'], settings['Fontsize']), takefocus = 0)
        self.Artikel.grid(row=1, rowspan=6, column=cols[0], sticky=N+E+S+W)      
        self.yscroller["command"] = self.Artikel.yview
        self.Artikel.insert(INSERT, text)
        settings['Text_Aktiv'] = 1

        self.etui = Frame(self, borderwidth=2, bg=settings['BG_Color'])
        self.etui.grid(row=0, column=cols[0], columnspan=2,sticky=S+W+E)
        self.Artikel.tag_config('worddetect',underline=1, font = (settings['Font'], settings['Fontsize'], "bold"))
        
        for i in range(0,len(settings['Highlight_Buttons'])):
            self.Artikel.tag_config(settings['Highlight_Buttons'][i][1], background=settings['Highlight_Buttons'][i][2])
            self.etui.leuchtstift = Button(self.etui, text = settings['Highlight_Buttons'][i][0], width=5, command=CMD(self.mark,settings['Highlight_Buttons'][i][1]), background=settings['Highlight_Buttons'][i][2], takefocus = 0)
            self.etui.leuchtstift.grid(row=0, column=i+4, sticky=W)
        self.Artikel.tag_config('prominent', foreground='#ff0000')

        if 'Hotwords' in settings.keys():
            self.etui.wd = Button(self.etui, text = "Keywords", width=8, command=CMD(self.mark,'worddetect'), background='#ffffff', takefocus = 0)
            self.etui.wd.grid(row=0, column=0, sticky=W)
            if 'Auto_Highlight' in settings.keys():
                if settings['Auto_Highlight'] in [1,'1']:
                    self.mark('worddetect')
        self.etui.tippex = Button(self.etui, text = "", width=4, command=CMD(self.mark,'blank'), background='#ffffff', takefocus = 0)
        self.etui.tippex.grid(row=0, column=1, sticky=W)
        self.etui.tippex = Button(self.etui, text = "Mark", width=4, command=CMD(self.mark,'markprominent'), background='#ffffff', takefocus = 0, fg='#ff0000')
        self.etui.tippex.grid(row=0, column=2, sticky=W)

        self.etui.columnconfigure(2,minsize=50)
           


    def clean_all_tags(self,sel_tag=[]):
        global settings
        log('Calling Function: Clean All Tags')
        tags = []
        if len(sel_tag) == 0:
            for b in settings['Highlight_Buttons']:
                tags.append(b[1])
        else:
            for b in settings['Highlight_Buttons']:
                if b[1] in sel_tag:
                    tags.append(b[1])
        verb('--Only removing tags: '+str(tags))

        for tag_id in tags:
            try:
                self.Artikel.tag_remove(tag_id,1.0,END)
            except:
                verb('--Tag removal impossible for: '+tag_id)

    def mark(self,tag_id,ls=[]): ##Highlighting the selected text
        log('--Marking as: '+tag_id,pos=0)
        if tag_id == 'blank':
            for tag_desc in settings['Highlight_Buttons']:
                tag_id = tag_desc[1]
                try:
                    self.Artikel.tag_remove(tag_id,SEL_FIRST,SEL_LAST)
                except:
                    if not settings['Verbose'] == '0':
                        verb('----No selection. Highlighting impossible')
        elif tag_id == 'markprominent':
            self.Artikel.tag_add('prominent',SEL_FIRST,SEL_LAST)
        elif tag_id == 'worddetect':
            try:
                verb(str(self.Artikel.tag_ranges('worddetect')[1]))
                self.Artikel.tag_remove('worddetect',1.0,END)
                verb('tags wieder entfernt')
                self.etui.wd['relief']=RAISED
            except:
                try:
                    verb('---Country:'+settings['Country'])                   
                    verb('Suchen nach Worten aus '+str(settings['Hotwords']))
                    for wort in settings['Hotwords']:
                        verb(wort)
                        start = '1.1'
                        while not start == '':
                            a = self.Artikel.search(wort,start,END)
                            verb(str(a)+':')
                            if not a == '':
                                anfang = self.Artikel.search(' ',a,backwards=TRUE)
                                ende = self.Artikel.search(' ',a,forwards=TRUE)
                                start = ende
                                if math.floor(float(anfang)) < math.floor(float(a)):
                                    anfang = str(int(math.floor(float(a))))+".0"
                                self.Artikel.tag_add('worddetect',anfang,ende)
                                if math.floor(float(ende)) > math.floor(float(a)):
                                    ende = str(1+int(math.floor(float(a))))+".0"
                                self.Artikel.tag_add('worddetect',anfang,ende)
                            else:
                                start = ''
                                anfang = ''
                                ende = ''
                            verb('>'+str(a)+str(anfang)+str(ende))
                        self.etui.wd['relief']=SUNKEN
                except:
                    verb('ERROR: Could not highlight Hotwords')
        else:
            try:
                self.Artikel.tag_add(tag_id,SEL_FIRST,SEL_LAST)
            except:
                verb('No selection. Highlighting impossible')

    def ausblenden(self): #Remove text from window
        log('--(Ausblenden)',pos=0)
        try:
            self.yscroller.destroy()
            self.Artikel.destroy()
            self.etui.destroy()
            settings['Text_Aktiv'] = 0
        except:
            verb('--Unable to remove text')


    def intronase(self): ##Cut loops from the page history. Necessary for the correct application of the back-function
        log('--Intronase')
        current = settings['Page_History'][len(settings['Page_History'])-1]
        i = len(settings['Page_History'])-1
        while i > 0:
            i = i -1
            if settings['Page_History'][i] == current:
                verb('----Double in: '+str(settings['Page_History']))
                while len(settings['Page_History']) > i:
                    settings['Page_History'].pop(i)
                settings['Page_History'].append(current)
        verb('----New History: '+str(settings['Page_History']))
 
    def hilfe_zu(self,htext,event=0): ##Display the help-text for a variable in a new window
        log('Calling Function: Hilfe zu')
        storage['Helptexts'] = storage['Helptexts'] + 1
        htext_out = ""
        for zeichen in htext:
            if zeichen == '#':
                htext_out = htext_out + '\n'
            else:
                htext_out = htext_out + zeichen             
        #tkMessageBox.showinfo("Hilfe", htext_out)
        self.display_text(htext_out,title="Help Text",bg="#ffffff")

    def message(self,m_id,m_type=1,var='Err_Msg',add=''):
        log('Calling Function: Message with message: '+m_id+' in Codebook-Variable: '+var)
        title = m_id
        text = self.namegetter(var,m_id)+add
        r = 0
        if m_type == 1:
            tkMessageBox.showwarning(title,text)
        elif m_type == 2:
            tkMessageBox.showinfo(title,text)
        elif m_type == 3:
            r = tkMessageBox.askokcancel(title,text)
        return r

    def insecure(self,variabel,event=0): ##Report an insecurity
        log('Calling Function: Insecure')
        exp_file = open('..\insec.txt','a')
        zeile = settings['Coder'] + '\t' + storage['ID'] + '\t' + variabel + '\t' + str(dta_pos) + '\t' + str(time.ctime()) + '\t' + bereinigen(settings['Fulltext']) + '\n'
        exp_file.write(zeile)
        exp_file.close()           
        self.message("Info01")
        
    def pause(self): ##Making a break (disable the question-frame and wat for the button to be pressed again)
        log('Calling Function: Pause')
        storage['Breaks'] = storage['Breaks'] + 1
        if settings['Layout'] == 'Lefty':
            c1 = 1
        else:
            c1 = 5

        if settings['Break'] == 0:
            settings['Break'] = time.time()
            sess_time = time.time()-settings['Session_Start']
            s_time = time.strftime("%H:%M:%S",time.gmtime(sess_time))
            outtext = 'Enjoy your break.\n\nHit "End Break" to continue\n\n\nDuration of the current\ncoding session (without breaks): '+s_time
            self.f_bottomline.b_break["text"] = 'End Break'
            #self.pausentext = Text(self, width=80, height=3, wrap=WORD, relief=FLAT, font = (settings['Font'], "9"), bg='#ffaaaa')
            self.pausentext=Canvas(self,bg='#33aaff')
            self.pausentext.create_text(200,100,text=outtext,font=('Arial','14'),fill="#aaeeff")
            self.pausentext.grid(row=4, column=c1, sticky=N+E+S+W)
            settings['Logging_Info'].append(['BREAK',time.time()])
        else:
            zeit = time.time() - settings['Break']
            settings['Break'] = 0
            settings['Break_Time'] = settings['Break_Time'] + zeit
            settings['Session_Start'] = settings['Session_Start'] + zeit
            self.f_bottomline.b_break["text"] = 'Break'
            self.pausentext.destroy()
            settings['Logging_Info'].append(['END BREAK',time.time()])


    def cini_schreiben(self):
        log('Calling Function: CINI schreiben')
        c_file = open('a_settings.ini','w')
        c_file.write('##Coder Information:\n##This ini-File is formatted as the codebook:\n##3 Lines (Question, Information, Help) before any values may be defined.\n\n\n')
        for variable in ['Coder-Settings','Default-Values']:
            c_file.write('[')
            c_file.write(variable)
            c_file.write(']\nFrage: ')
            c_file.write(cini[variable][0])
            c_file.write('Anweisung: ')
            c_file.write(cini[variable][1])
            c_file.write('Hilfe: ')
            c_file.write(cini[variable][4])
            if variable == 'Default-Values':
                verb('Default Values: '+str(def_val))
                if available('Retain_Values'):
                    for dvar in sorted(def_val.keys()):
                        if dvar in settings['Retain_Values']:
                            c_file.write(dvar)
                            c_file.write(':')
                            c_file.write(str(def_val[dvar]))
                            c_file.write('\n')                    
            else:                
                for i in range(0,len(cini[variable][2])):
                    c_file.write(cini[variable][3][i])
                    c_file.write(':')
                    c_file.write(cini[variable][2][i])
                    c_file.write('\n')
            c_file.write('\n\n')
        c_file.write('\n\n\n')
        c_file.close()


    def load_cset(self,csettings):
        outcodes = []
        for c in csettings[2]:
            if len(c) > 0:
                if c[0] in ['[','{','(']:
                    try:
                        code=eval(c)
                    except:
                        code = c
                elif c[0] in ['0','1','2','3','4','5','6','7','8','9','-']:
                    try:
                        code = float(c)
                        if code == int(code):
                            code = int(code)
                    except:
                        code = c
                else:
                    code = c
            else:
                code = 0
            outcodes.append(code)
        csettings[2] = outcodes
        return csettings
        

############################################
##                                        ##
##       I/O Functions                    ##
##                                        ##
############################################

def artikelholen(ID): ##Get a text from the folder specified
    log('        Artikelholen',pos=0)
    at = ""
    if ID[-4] == '.':
        art_filen = settings['Text_Folder'] + ID
    else:
        art_filen = settings['Text_Folder'] + ID + '.txt'
    if ID[-4:] in ['.PDF','.pdf','.Pdf']:
        art_filen = ''
        storage['Medium_Type'] = 'PDF'
    verb('Loading: ' + str(art_filen))

    settings['Filename']=art_filen
    
    try:
        art_file = open(art_filen, 'r')
        F_list = art_file.readlines()
        if settings['Verbose'] == '1':
            verb(str(F_list))
        art_file.close()
        textmine(F_list)
        F_listneu = []
        for zeile in F_list: ### Replace unusual characters for a correct display of the text
            #zeileneu = bereinigen(zeile,lb=1,uml=1)
            F_listneu.append(zeile)                    
        for zeile in F_listneu:
            at = at + zeile
        verb(art_filen)
        at = at + '\n\n-End of Document \n '
    except IOError:
        at = ""
        verb('ERROR: The file could not be loeded: '+art_filen)
    except:
        verb("ERROR: EXCEPTIONAL ERROR WHEN LOADING FILE: "+art_filen)
    return at


def update_text(fulltext):
    log('        Update Text',pos=0)
    outfile = settings['Filename']
    outtext = settings['Fulltext']

    verb('Storing text to: '+outfile)

    #print [outtext]

    outtext = outtext.encode('latin-1')
    #print [outtext]

    art_file = open(outfile, 'w')
    art_file.write(outtext)
    art_file.close()


def textmine(linelist): ##A list of all lines within the text are submitted to this function. May be used to change default values.
    global def_val
    global settings
    log('        Textmining',pos=0)
    verb(str(storage['ID'][:3]))


    settings['Country']=storage['ID'][:2]
    verb('--Got the country: '+settings['Country'])
    
    
    storage['Length'] = 0
    for l in linelist:
        for c in l:
            if c == ' ': storage['Length'] = storage['Length']+1
        storage['Length'] = storage['Length']+1
    storage['Length'] = str(storage['Length'])
    verb('--Counted Words: '+storage['Length'])
   

    for zeile in linelist[:20]:
        ### Länge rausfinden
        if 'Woerter' in bereinigen(zeile):
            laenge = ''
            for c in zeile:
                if c in ['1','2','3','4','5','6','7','8','9','0']:
                    laenge = laenge + c
            storage['Length'] = laenge
        if 'words' in zeile:
            laenge = ''
            for c in zeile:
                if c in ['1','2','3','4','5','6','7','8','9','0']:
                    laenge = laenge + c
            storage['Length'] = laenge
        if 'LENGTH:' in zeile:
            laenge = ''
            for c in zeile:
                if c in ['1','2','3','4','5','6','7','8','9','0']:
                    laenge = laenge + c
            storage['Length'] = laenge
        if 'LÄNGE:' in zeile:
            laenge = ''
            for c in zeile:
                if c in ['1','2','3','4','5','6','7','8','9','0']:
                    laenge = laenge + c
            storage['Length'] = laenge
        if bereinigen(zeile[:6]) in ['LENGTH','LAeNGE']:
            laenge = ''
            for c in zeile:
                if c in ['1','2','3','4','5','6','7','8','9','0']:
                    laenge = laenge + c
            storage['Length'] = laenge
    verb('--Got length: '+storage['Length'])
 
            


def get_codebook(filename): ##Load the codebook from a given file. Returns a codebook-Dictionary for use within the tool.
    log('Calling Function: Get Codebook from: '+filename)
    #Codebook-Enries have the form:
    #
    #[Name of the variable]
    #Question
    #Coder Information
    #Helptext
    #Code1:Item1
    #Code2:Item2
    #...
        
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

            #verb(varname+str(optionen))
            verb(varname+'; ')

            cb[varname] = []
            cb[varname].append(varfrage) #codebook['variabel'][0] is the question as string (including final linebreak)
            cb[varname].append(varanw)   #codebook['variabel'][1] is the coder information
            cb[varname].append(optionen) #codebook['variabel'][2] is a list containing all labels
            cb[varname].append(codes)    #codebook['variabel'][3] is a list containing all codes (parallel to [2]
            cb[varname].append(varhilfe)    #codebook['variabel'][4] is the helptext
        i = i + 1
    
    verb('\nCodebook loaded successfully')
    return cb

def create_addlist(varname,mtype='TV'):
    global codebook
    global storage

    codebook[varname]={}
    codebook[varname][0] = codebook['Choose_Addition'][0]
    codebook[varname][1] = codebook['Choose_Addition'][1]
    codebook[varname][2] = list(codebook['Choose_Addition'][2])
    codebook[varname][3] = list(codebook['Choose_Addition'][3])
    codebook[varname][4] = codebook['Choose_Addition'][4]

    tmp_store = storage
##    tmp_store = {}
##    tmp_store['Speaker']={'Journ':{}, 'Spr01':{}}
##    tmp_store['Speaker']['Journ'] = {'#TN':'Autor des Textes', 'Target':{'Tgt01':{'#TN':'Halt ein Target'}}}
##    tmp_store['Speaker']['Spr01'] = {'#TN':'Christoph Blocher (SVP)', 'Issue':{'Iss01':{'#TN':'Immigration'}}}

    codebook[varname][2].append('Add new Issue...')
    codebook[varname][3].append('Add_Issue')   
    for spr in tmp_store['Speaker'].keys():
        if not (spr == 'Journ' and mtype=='Talk'):
            codebook[varname][2].append('...to Speaker: '+tmp_store['Speaker'][spr]['#TN'])
            codebook[varname][3].append(('-',spr,'Add_Iss'))
    codebook[varname][2].append('Add new Target Evaluation...')
    codebook[varname][3].append('Add_Issue')   
    for spr in tmp_store['Speaker'].keys():
        if not (spr == 'Journ' and mtype=='Talk'):
            codebook[varname][2].append('...to Speaker: '+tmp_store['Speaker'][spr]['#TN'])
            codebook[varname][3].append(('-',spr,'Add_Tgt'))
    codebook[varname][2].append('#')
    codebook[varname][3].append('#')   

    codebook[varname][2].append('Edit existing Speaker')
    codebook[varname][3].append('Edit_Spr') 
    for spr in tmp_store['Speaker'].keys():
        if not (spr == 'Journ' and mtype=='Talk'):
            codebook[varname][2].append('Edit '+tmp_store['Speaker'][spr]['#TN'])
            codebook[varname][3].append(('-',spr,'Edit_Spr'))

    for spr in tmp_store['Speaker'].keys():
        if not (spr == 'Journ' and mtype=='Talk'):
            codebook[varname][2].append('Edit Statement by: '+tmp_store['Speaker'][spr]['#TN'])
            codebook[varname][3].append('Edit_Statement')
            if 'Issue' in tmp_store['Speaker'][spr].keys():
                for i in tmp_store['Speaker'][spr]['Issue']:    
                    codebook[varname][2].append('Edit Issue: '+tmp_store['Speaker'][spr]['Issue'][i]['#TN'])
                    codebook[varname][3].append(('-',spr,'Edit_Iss',i))
            if 'Target' in tmp_store['Speaker'][spr].keys():
                for i in tmp_store['Speaker'][spr]['Target']:    
                    codebook[varname][2].append('Edit Target: '+tmp_store['Speaker'][spr]['Target'][i]['#TN'])
                    codebook[varname][3].append(('-',spr,'Edit_Tgt',i))

    codebook[varname][2].append('#')
    codebook[varname][3].append('#')   

    codebook[varname][2].append('Remove existing Speaker')
    codebook[varname][3].append('Rem_Spr') 
    for spr in tmp_store['Speaker'].keys():
        if not spr == 'Journ':
            codebook[varname][2].append('Remove '+tmp_store['Speaker'][spr]['#TN'])
            codebook[varname][3].append(('-',spr,'Rem_Spr'))

    for spr in tmp_store['Speaker'].keys():
        if not (spr == 'Journ' and mtype=='Talk'):
            codebook[varname][2].append('Remove Statement by: '+tmp_store['Speaker'][spr]['#TN'])
            codebook[varname][3].append('Rem_Statement')
            if 'Issue' in tmp_store['Speaker'][spr].keys():
                for i in tmp_store['Speaker'][spr]['Issue']:    
                    codebook[varname][2].append('Remove Issue: '+tmp_store['Speaker'][spr]['Issue'][i]['#TN'])
                    codebook[varname][3].append(('-',spr,'Rem_Iss',i))
            if 'Target' in tmp_store['Speaker'][spr].keys():
                for i in tmp_store['Speaker'][spr]['Target']:    
                    codebook[varname][2].append('Remove Target: '+tmp_store['Speaker'][spr]['Target'][i]['#TN'])
                    codebook[varname][3].append(('-',spr,'Rem_Tgt',i))



def florinize(data,varlist):
    log('Calling Function: Florinize')
    align_dic = {}
    varlist = varlist + ['Unit_Speaker','Unit_Issue','Unit_Target']
    if 'Speaker' in data.keys():
        for s in data['Speaker'].keys():
            data['Speaker'][s]['Unit_Speaker'] = s
            verb('--Speaker: '+str(s))
            i_list = []
            a_list = []
            if 'Issue' in sorted(data['Speaker'][s].keys()):
                for i in data['Speaker'][s]['Issue'].keys():
                    verb('----Issue: '+str(i))
                    data['Speaker'][s]['Issue'][i]['Unit_Issue'] = i
                    if 'Iss_ID' in data['Speaker'][s]['Issue'][i].keys():
                        i_id = data['Speaker'][s]['Issue'][i]['Iss_ID'][1]
                    else:
                        i_id = ('None','0')
                        verb('ERROR: Incomplete coding of an Issue (No Iss_ID): '+str(i))
                    i_list.append((i,i_id))
            if 'Target' in sorted(data['Speaker'][s].keys()):
                for a in data['Speaker'][s]['Target'].keys():
                    verb('----Target: '+str(a))
                    data['Speaker'][s]['Target'][a]['Unit_Target'] = a
                    if 'Tgt_ID' in data['Speaker'][s]['Target'][a].keys():
                        tgt = data['Speaker'][s]['Target'][a]['Tgt_ID'][1]
                    else:
                        tgt = ('None','0')
                        verb('ERROR: Incomplete coding of a Target Evaluation (No Tgt_ID): '+str(a))
                    if 'Iss_Link' in data['Speaker'][s]['Target'][a]:
                        il = data['Speaker'][s]['Target'][a]['Iss_Link'][1]
                    else:
                        il = ('None','0')
                        verb('ERROR: Incomplete coding of a Target Evaluation (No Iss_Link): '+str(a))
                    a_list.append((a,tgt,il))
            outlist = []
            done_dic= {}
            verb('Speaker: '+str(s)+ ':\n--Issues: '+str(i_list)+'\n--Actors: '+str(a_list))
            for i in i_list:
                done_dic[i[0]] = 0
            for a in a_list:
                if not a[2] in ['0','9']:
                    iss = 0
                    for i in i_list:
                        if a[2]==i[1]:
                            iss = i[0]
                            done_dic[i[0]] = 1
                            verb('Linking:'+a[0]+' to '+i[0])
                            verb('Preparing: '+str(iss)+'/'+a[0])
                            outlist.append((iss,a[0]))
                    if iss == 0:
                        verb('Preparing: 0/'+a[0])
                        outlist.append((0,a[0]))                        
                else:
                    verb('Preparing: 0/'+a[0])
                    outlist.append((0,a[0]))
            for i in done_dic.keys():
                if done_dic[i] <1:
                    verb('Preparing: '+i+'/No actor')
                    outlist.append((i,0))
            if outlist==[]:
                outlist = [(0,0)]
            align_dic[s] = outlist

            verb('Writing: '+str(outlist))

        s_order = []
        s_unorder = align_dic.keys()
        if 'Journ' in s_unorder:
            s_order.append('Journ')
            s_unorder.remove('Journ')
        s_order = s_order + sorted(s_unorder)

        new_data = {}
        iss_number_int = 0

        for s in s_order:
            for iss in align_dic[s]:
                iss_number_int = iss_number_int + 1
                iss_number = '{0:02}'.format(iss_number_int)
                new_data[iss_number] = {}
                ##Artikellevel
                for v in data.keys():
                    if v in varlist:
                        new_data[iss_number][v] = data[v]
                ##Sprecherlevel
                for v in data['Speaker'][s].keys():
                    if v in varlist:
                        new_data[iss_number][v] = data['Speaker'][s][v]
                if not iss[0] == 0:
                    for v in data['Speaker'][s]['Issue'][iss[0]].keys():
                        if v in varlist:
                            new_data[iss_number][v] = data['Speaker'][s]['Issue'][iss[0]][v]
                if not iss[1] == 0:
                    for v in data['Speaker'][s]['Target'][iss[1]].keys():
                        if v in varlist:
                            if v in new_data[iss_number].keys(): #Issue has already set this variable
                                verb('--ATTENTION: Found two different values for '+v+
                                     '\n----From Issue: '+str(new_data[iss_number][v])+
                                     '----From Target: '+str(data['Speaker'][s]['Target'][iss[1]][v]))
                                if type(data['Speaker'][s]['Target'][iss[1]][v]) == dict:
                                    try:
                                        for k in data['Speaker'][s]['Target'][iss[1]][v].keys():
                                            values = [data['Speaker'][s]['Target'][iss[1]][v][k],new_data[iss_number][v][k]]
                                            new_data[iss_number][v][k] = sorted(values)[1]
                                            verb('----Picked: '+str(new_data[iss_number][v][k])+' for key: '+str(k))
                                    except Exception as fehler:
                                        verb('ERROR: Could not unite the values. Picking Target Value!.'+str(fehler))
                                        new_data[iss_number][v] = data['Speaker'][s]['Target'][iss[1]][v]
                                else:
                                    v1 = data['Speaker'][s]['Target'][iss[1]][v]
                                    v2 = new_data[iss_number][v]
                                    if type(v1) == tuple:
                                        v1 = v1[1]
                                    if type(v2) == tuple:
                                        v2 = v2[1]
                                    values = [v1,v2]
                                    new_data[iss_number][v] = sorted(values)[1]
                                    verb('----Picked: '+str(new_data[iss_number][v]))
                            else:
                                new_data[iss_number][v] = data['Speaker'][s]['Target'][iss[1]][v]
    else:
        new_data={'01':{'ID':data['ID']}}
    return new_data


def visonout(filename="vtest.graphml"):
    global storage
    log('Calling Function: Visonout')
    vin = open('..\\vclean.txt','r')
    vinlines = vin.readlines()
    vin.close()
    vinend = '  </graph>\n  <data key="d13">\n    <y:Resources/>\n  </data>\n</graphml>'

    nodes = {}
    nnr = 0

    if 'Speaker' in storage.keys():
        for s in storage['Speaker'].keys():
            nid = bereinigen(storage['Speaker'][s]['#TN'])
            nodes[nid] = {}
            nodes[nid]['ID'] = 'n'+str(nnr)
            snode = 'n'+str(nnr)
            nodes[nid]['Col'] = 'FFFF66'
            nodes[nid]['Typ'] = 'Speaker'
            nnr = nnr + 1
            if 'Issue' in storage['Speaker'][s].keys():
                for i in storage['Speaker'][s]['Issue'].keys():
                    nid = bereinigen(storage['Speaker'][s]['Issue'][i]['#TN'])
                    if nid in nodes.keys():
                        nodes[nid]['Speakers'].append(snode)
                    else:
                        nodes[nid]={}
                        nodes[nid]['ID']='n'+str(nnr)
                        nodes[nid]['Speakers']=[snode]
                        nodes[nid]['Col'] = '66FF66'
                        nodes[nid]['Typ'] = 'Issue'
                        nnr = nnr + 1
            if 'Target' in storage['Speaker'][s].keys():
                for a in storage['Speaker'][s]['Target'].keys():
                    nid = bereinigen(storage['Speaker'][s]['Target'][a]['#TN'])
                    if nid in nodes.keys():
                        nodes[nid]['Speakers'].append(snode)
                    else:
                        nodes[nid]={}
                        nodes[nid]['ID']='n'+str(nnr)
                        nodes[nid]['Speakers']=[snode]
                        nodes[nid]['Col'] = '99AAFF'
                        nodes[nid]['Typ'] = 'Target'
                        nnr = nnr + 1

    vinsert = []
    verb(baum_schreiben(nodes))

    pos = 0
    for n in nodes:
        pos = pos + 1
        xpos = pos%3 * 50
        ypos = pos/3 * 50
        insert1 = ['    <node id="'+nodes[n]['ID']+'">',
                   '      <data key="d0">',
                   '        <visone:shapeNode>',
                   '          <y:ShapeNode>',
                   '            <y:Geometry height="30.0" width="80.0" x="'+str(xpos)+'" y="'+str(ypos)+'"/>',
                   '            <y:Fill color="#'+nodes[n]['Col']+'" transparent="false"/>',
                   '            <y:BorderStyle color="#FFFFFF00" type="line" width="1.0"/>',
                   '            <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog plain" fontSize="20" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" modelName="internal" modelPosition="c" textColor="#000000" visible="true" width="37.0" x="21.5" y="5.6494140625">Levrat</y:NodeLabel>',
                   '            <y:Shape type="roundrectangle"/>',
                   '          </y:ShapeNode>',
                   '        </visone:shapeNode>',
                   '      </data>',
                   '      <data key="d1">'+nodes[n]['ID'][1:]+'</data>',
                   '      <data key="d2">'+nodes[n]['ID']+'</data>',
                   '      <data key="d3">'+n+'</data>',
                   '      <data key="d4">'+nodes[n]['Typ']+'</data>',
                   '    </node>']
        vinsert = vinsert + insert1

    enr = 0
    for n in nodes:
        if 'Speakers' in nodes[n].keys():
            for s in nodes[n]['Speakers']:
                eid = 'e' + str(enr)
                enr = enr + 1               
                insert1 = ['    <edge id="'+eid+'" source="'+s+'" target="'+nodes[n]['ID']+'">',
                           '      <data key="d5">',
                           '        <visone:polyLineEdge>',
                           '          <y:PolyLineEdge>',
                           '            <y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0"/>',
                           '            <y:LineStyle color="#808080" type="line" width="3.0"/>',
                           '            <y:Arrows source="none" target="StandardArrow"/>',
                           '            <y:EdgeLabel alignment="center" distance="2.0" fontFamily="Dialog plain" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="4.0" modelName="six_pos" modelPosition="tail" preferredPlacement="anywhere" ratio="0.5" textColor="#000000" visible="true" width="4.0" x="52.165283203125" y="43.46430303586408"/>',
                           '            <y:BendStyle smoothed="false"/>',
                           '          </y:PolyLineEdge>',
                           '          <visone:edgeRealizerData>',
                           '            <visone:line style="continuous" width="3.0"/>',
                           '          </visone:edgeRealizerData>',
                           '        </visone:polyLineEdge>',
                           '      </data>',
                           '      <data key="d6">3</data>',
                           '      <data key="d7">true</data>',
                           '      <data key="d8">'+eid[1:]+'</data>',
                           '      <data key="d9">'+eid+'</data>',
                           '    </edge>']
                vinsert = vinsert + insert1
    
    verb(str(vinsert))

    vout = open(filename,'w')
    for l in vinlines:
        vout.write(l)
    for v in vinsert:
        vout.write(v+'\n')
    vout.write(vinend+'\n')
    vout.close()


def log(name,pos=1):
    ## Making Log-Entries for called functions and events.
    global settings
    global prog_pos
    global dta_pos
    if settings['Verbose'] == '2':
        if pos == 1:
            settings['Verb_Log']=settings['Verb_Log']+name+'. Prog_Pos='+prog_pos+'; DTA-Pos='+ str(dta_pos) + '\n'
        else:
            settings['Verb_Log']=settings['Verb_Log']+name+'\n'
    if pos == 1:
        settings['Path_Log']=settings['Path_Log']+name+'. Prog_Pos='+prog_pos+'; DTA-Pos='+ str(dta_pos) + '\n'
    else:
        settings['Path_Log']=settings['Path_Log']+name+'\n'

def verb(name,stage=2,nl=1):
    ## Making Verbose-Entries. 
    global settings
    if int(settings['Verbose']) >= int(stage):
        settings['Verb_Log']=settings['Verb_Log']+name
        if nl==1:
            settings['Verb_Log']=settings['Verb_Log']+'\n'

def curr():
    log('Calling Function: Curr')
    global dta_pos
    global storage
    if dta_pos[0] == '-':
        curr_tree = storage
    elif dta_pos[2] == '-':
        curr_tree = storage[dta_pos[0]][dta_pos[1]]
    elif dta_pos[4] == '-':
        curr_tree = storage[dta_pos[0]][dta_pos[1]][dta_pos[2]][dta_pos[3]]
    else:
        verb('ERROR: No current tree at this data position!')
        curr_tree = {}
    verb('--Keys in current subtree: '+str(curr_tree.keys()))
    return curr_tree

def critical_abort():
    Anzeige.destroy()

def available(key):
    ##Checks whether a setting is available in the settings-directory.
    ##Available means: The key is present and if the value is a string this string is non-empty
    global settings
    log('Checking availability of setting: '+key)
    if key in settings.keys():
        if type(settings[key]) == str:
            if len(settings[key]) > 0:
                avail = True
            else:
                avail = False
        else:
            avail = True
    else:
        avail = False

    if avail:
        verb('--Setting found: '+str(settings[key]))
    else:
        verb('--Not available')
    return avail

def get_todo(fname):
    log('Calling Function: Get TODO')
    try:
        todo_file = open(fname,'r')
        art_name = todo_file.readline()
        art_name = art_name[:len(art_name)-1]
        verb('Next Item To do: '+ art_name)
        todo_file.close()
    except:
        verb('Unable to get next Item to do in: '+fname)
        art_name = ''
    return art_name

def check_todo():
    global settings
    global storage
    log('Calling Function: Check Todo')
    verb('Finalizing todo-list...')

    if available('Out_Tmp'):
        tf = open(settings['Out_Tmp'],'w')
        tf.write('')
        tf.close()

    try:
        todo_file = open(settings['Todo'],'r')
        todo_list = todo_file.readlines()
        todo_file.close()
        just_done = storage['ID'] + '\n'
        if just_done in todo_list:
            todo_list.remove(just_done)
        todo_file = open(settings['Todo'],'w')
        for element in todo_list:
            todo_file.write(element)
        todo_file.close()
        verb('New Todo-List: '+str(todo_list))
        if todo_list == []:
            verb('End of Todo-List')
    except:
        verb('No ToDo-List')


def baum_schreiben(tdic, einr = 0, inherit = '{\n', spc = '    ', trunc=0):
    for k in sorted(tdic.keys()):
        if type(tdic[k]) == dict:
            inherit = inherit + einr*spc + str(k) + ': ' + baum_schreiben(tdic[k],einr+1,trunc=trunc)
        else:
            value = tdic[k]
            if type(value)==str:
                value = "'"+value+"'"
            elif type(value) in [int,float]:
                value = str(value)
            elif type(value) == list:
                value = str(value)
            else:
                value = str(value)
            if len(value) > trunc and trunc > 0:
                tail = int(trunc/2)
                value = value[:tail] + '...'+value[-tail:] + ' ('+str(len(value))+' characters)'
                
            inherit = inherit + einr*spc + str(k) + ': '+ value + '\n'

    inherit = inherit + einr*spc + '}\n'
    return inherit

def baum_export(filename): ###Nicely export the storage
    settings['Coding_Time'] = time.time() - storage['#TS'][1]
    exp_file = open(filename, 'a')
    exp_file.write('\n------------------------------\n')
    exp_file.write('Codierung von Codierer:\n')
    exp_file.write(settings['Coder'])
    exp_file.write('\nZu Artikel:\n')
    exp_file.write(storage['ID'])
    exp_file.write('\nDauer:\n')
    exp_file.write(str(settings['Coding_Time']))        
    exp_file.write('\n------------------------------\n')                       
    for a in sorted(storage.keys()):
        exp_file.write('\n')
        exp_file.write(str(a))
        exp_file.write(': ')
        try:
            for b in sorted(storage[a].keys()):
                exp_file.write('\n')
                exp_file.write('\t')
                exp_file.write(str(b))
                exp_file.write(': ')
                try:
                    for c in sorted(storage[a][b].keys()):
                        exp_file.write('\n')
                        exp_file.write('\t\t')
                        exp_file.write(str(c))
                        exp_file.write(': ')
                        try:
                            for d in sorted(storage[a][b][c].keys()):
                                exp_file.write('\n')
                                exp_file.write('\t\t\t')
                                exp_file.write(str(d))
                                exp_file.write(': ')
                                try:
                                    for e in sorted(storage[a][b][c][d].keys()):
                                        exp_file.write('\n')
                                        exp_file.write('\t\t\t\t')
                                        exp_file.write(str(e))
                                        exp_file.write(': ')
                                        try:
                                            for f in sorted(storage[a][b][c][d][e].keys()):
                                                exp_file.write('\n')
                                                exp_file.write('\t\t\t\t\t')
                                                exp_file.write(str(f))
                                                exp_file.write(': ')
                                                try:
                                                    for g in sorted(storage[a][b][c][d][e][f].keys()):
                                                        exp_file.write('\n')
                                                        exp_file.write('\t\t\t\t\t\t')
                                                        exp_file.write(str(g))
                                                        exp_file.write(': ')
                                                        exp_file.write(str(storage[a][b][c][d][e][f][g]))
                                                except:
                                                    exp_file.write(str(storage[a][b][c][d][e][f]))
                                        except:
                                            exp_file.write(str(storage[a][b][c][d][e]))
                                except:
                                    exp_file.write(str(storage[a][b][c][d]))
                        except:
                            exp_file.write(str(storage[a][b][c]))
                except:
                    exp_file.write(str(storage[a][b]))
        except:
            exp_file.write(str(storage[a]))

    exp_file.write('\n\n\ENDE')                
    exp_file.close()
    
def get_varnames(filename):
    inp_file = open(filename, 'r')
    varline = inp_file.readline()
    inp_file.close()
    vlist = []
    i = 0
    varname = ''
    while not varline[i] == '\n':
        c = varline[i]
        i = i + 1
        if c == '\t':
            vlist.append(varname)
            varname = ''
        else:
            varname = varname + c
    vlist.append(varname)
    return vlist

def get_data(filename, varlist = []):
    if varlist == []:
        varlist = get_varnames(filename)
    inp_file = open(filename, 'r')
    varline = inp_file.readline()
    dtaline = inp_file.readline()
    data_dic = {}
    for var in varlist:
        data_dic[var] = []

    while not dtaline == '':
        var = 0
        i = 0
        value = ''
        while not dtaline[i] == '\n':
            if dtaline[i] == '\t':
                if var == len(varlist)-1:
                    break
                data_dic[varlist[var]].append(value)
                value = ''
                var = var + 1
            else:
                value = value + dtaline[i]
            i = i + 1
        try:
            data_dic[varlist[var]].append(value)
        except:
            verb('.')
        dtaline = inp_file.readline()

    inp_file.close()
    return data_dic

def get_unique(liste):
    unlist = []
    for element in liste:
        if not element in unlist:
            unlist.append(element)
    return sorted(unlist)

def getcaps(zeile):
    log('Calling Function: Getcaps')
    #This function removes all words from a string which do not begin with a capital letter.
    outstring=''
    seg=''
    for i in range(0,len(zeile)):
        if zeile[i] in [' ','\t',',',';','.',':','"',"'"]:
            if len(seg) > 1:
                if ord(seg[0]) in range(65,91):
                    outstring=outstring+seg+' '
            seg = ''
        else:
            seg = seg + zeile[i]
    if len(seg) > 1:
        if ord(seg[0]) in range(65,91):
            outstring=outstring+seg
    verb('Only words with capital letters: '+outstring)
    return outstring


def bereinigen(uml_string, lc=0,lb=0,uml=0,encod='latin-1'):
    #This function removes any special character from a string.
    replace = {}
    replace[126] = {1:'~',0:'tilde'}
    replace[128] = {1:'E',0:'euro'}
    replace[132] = {1:'"',0:'"'}
    replace[133] = {1:'...',0:'...'}
    replace[138] = {1:'S',0:'S'}
    replace[139] = {1:'<',0:'"'}
    replace[140] = {1:'Oe',0:'Oe'}
    replace[142] = {1:'Z',0:'Z'}
    replace[145] = {1:'"',0:'"'}
    replace[146] = {1:'"',0:'"'}
    replace[147] = {1:'"',0:'"'}
    replace[148] = {1:'"',0:'"'}
    replace[149] = {1:'-',0:'-'}
    replace[150] = {1:'-',0:'-'}
    replace[151] = {1:'-',0:'-'}
    replace[152] = {1:'-',0:'-'}
    replace[153] = {1:'(tm)',0:'(tm)'}
    replace[154] = {1:'s',0:'s'}
    replace[155] = {1:'>',0:'"'}
    replace[156] = {1:'oe',0:'oe'}
    replace[158] = {1:'z',0:'z'}
    replace[159] = {1:'Y',0:'Y'}
    replace[160] = {1:'.',0:' '}
    replace[162] = {1:'.',0:''}
    replace[163] = {1:'£',0:'lbs.'}
    replace[165] = {1:'Y',0:'yen'}
    replace[167] = {1:'§',0:'par'}
    replace[169] = {1:'(c)',0:'(c)'}
    replace[171] = {1:'"',0:'"'}
    replace[173] = {1:'-',0:'-'}
    replace[175] = {1:'-',0:'-'}
    replace[176] = {1:'°',0:''}
    replace[177] = {1:'+/-',0:'+/-'}
    replace[186] = {1:'°',0:''}
    replace[187] = {1:'"',0:'"'}
    replace[188] = {1:'1/4',0:'1/4'}
    replace[189] = {1:'1/2',0:'1/2'}
    replace[190] = {1:'3/4',0:'3/4'}
    replace[191] = {1:'?',0:'?'}
    replace[192] = {1:'A',0:'A'}
    replace[193] = {1:'A',0:'A'}
    replace[194] = {1:'Â',0:'A'}
    replace[195] = {1:'Ã',0:'A'}
    replace[196] = {1:'Ä',0:'Ae'}
    replace[197] = {1:'A',0:'A'}
    replace[198] = {1:'Ae',0:'Ae'}
    replace[199] = {1:'Ç',0:'C'}
    replace[200] = {1:'È',0:'E'}
    replace[201] = {1:'É',0:'E'}
    replace[202] = {1:'Ê',0:'E'}
    replace[203] = {1:'Ë',0:'E'}
    replace[204] = {1:'I',0:'I'}
    replace[205] = {1:'I',0:'I'}
    replace[206] = {1:'I',0:'I'}
    replace[207] = {1:'Ï',0:'I'}
    replace[208] = {1:'D',0:'D'}
    replace[209] = {1:'Ñ',0:'N'}
    replace[210] = {1:'Ò',0:'O'}
    replace[211] = {1:'Ó',0:'O'}
    replace[212] = {1:'Ô',0:'O'}
    replace[213] = {1:'O',0:'O'}
    replace[214] = {1:'Ö',0:'Oe'}
    replace[216] = {1:'Oe',0:'Oe'}
    replace[217] = {1:'Ù',0:'U'}
    replace[218] = {1:'Ú',0:'U'}
    replace[219] = {1:'Û',0:'U'}
    replace[220] = {1:'Ü',0:'Ue'}
    replace[221] = {1:'Y',0:'Y'}
    replace[222] = {1:'th',0:'th'}
    replace[223] = {1:'ß',0:'ss'}
    replace[224] = {1:'à',0:'a'}
    replace[225] = {1:'á',0:'a'}
    replace[226] = {1:'â',0:'a'}
    replace[227] = {1:'a',0:'a'}
    replace[228] = {1:'ä',0:'ae'}
    replace[229] = {1:'a',0:'a'}
    replace[230] = {1:'æ',0:'ae'}
    replace[231] = {1:'ç',0:'c'}
    replace[232] = {1:'è',0:'e'}
    replace[233] = {1:'é',0:'e'}
    replace[234] = {1:'ê',0:'e'}
    replace[235] = {1:'ë',0:'e'}
    replace[236] = {1:'i',0:'i'}
    replace[237] = {1:'i',0:'i'}
    replace[238] = {1:'î',0:'i'}
    replace[239] = {1:'ï',0:'i'}
    replace[240] = {1:'dh',0:'dh'}
    replace[241] = {1:'ñ',0:'n'}
    replace[242] = {1:'o',0:'o'}
    replace[243] = {1:'ó',0:'o'}
    replace[244] = {1:'ô',0:'o'}
    replace[245] = {1:'õ',0:'o'}
    replace[246] = {1:'ö',0:'oe'}
    replace[247] = {1:'%',0:'%'}
    replace[248] = {1:'oe',0:'oe'}
    replace[249] = {1:'ù',0:'u'}
    replace[250] = {1:'ú',0:'u'}
    replace[251] = {1:'û',0:'u'}
    replace[252] = {1:'ü',0:'ue'}
    replace[253] = {1:'y',0:'y'}
    replace[254] = {1:'th',0:'th'}
    replace[904] = {1:u'Έ',0:'E'}
    replace[913] = {1:u'Α',0:'A'}
    replace[914] = {1:u'Β',0:'B'}
    replace[915] = {1:u'Γ',0:'G'}
    replace[916] = {1:u'Δ',0:'D'}
    replace[917] = {1:u'Ε',0:'E'}
    replace[918] = {1:u'Ζ',0:'Z'}
    replace[919] = {1:u'Η',0:'H'}
    replace[920] = {1:u'Θ',0:'Th'}
    replace[921] = {1:u'Ι',0:'I'}
    replace[922] = {1:u'Κ',0:'K'}
    replace[923] = {1:u'Λ',0:'L'}
    replace[924] = {1:u'Μ',0:'M'}
    replace[925] = {1:u'Ν',0:'N'}
    replace[926] = {1:u'Ξ',0:'X'}
    replace[927] = {1:u'Ο',0:'O'}
    replace[928] = {1:u'Π',0:'p'}
    replace[929] = {1:u'Ρ',0:'R'}
    replace[931] = {1:u'Σ',0:'S'}
    replace[932] = {1:u'Τ',0:'T'}
    replace[933] = {1:u'Υ',0:'Y'}
    replace[934] = {1:u'Φ',0:'F'}
    replace[935] = {1:u'Χ',0:'Ch'}
    replace[936] = {1:u'Ψ',0:'Ps'}
    replace[937] = {1:u'Ω',0:'W'}
    replace[940] = {1:u'ά',0:'a'}
    replace[941] = {1:u'έ',0:'e'}
    replace[942] = {1:u'ή',0:'h'}
    replace[943] = {1:u'ί',0:'i'}
    replace[945] = {1:u'α',0:'a'}
    replace[946] = {1:u'β',0:'b'}
    replace[947] = {1:u'γ',0:'g'}
    replace[948] = {1:u'δ',0:'d'}
    replace[949] = {1:u'ε',0:'e'}
    replace[950] = {1:u'ζ',0:'z'}
    replace[951] = {1:u'η',0:'h'}
    replace[952] = {1:u'θ',0:'th'}
    replace[953] = {1:u'ι',0:'i'}
    replace[954] = {1:u'κ',0:'k'}
    replace[955] = {1:u'λ',0:'l'}
    replace[956] = {1:u'μ',0:'m'}
    replace[957] = {1:u'ν',0:'n'}
    replace[958] = {1:u'ξ',0:'x'}
    replace[959] = {1:u'ο',0:'o'}
    replace[960] = {1:u'π',0:'p'}
    replace[961] = {1:u'ρ',0:'r'}
    replace[962] = {1:u'ς',0:'s'}
    replace[963] = {1:u'σ',0:'s'}
    replace[964] = {1:u'τ',0:'t'}
    replace[965] = {1:u'υ',0:'y'}
    replace[966] = {1:u'φ',0:'f'}
    replace[967] = {1:u'χ',0:'ch'}
    replace[968] = {1:u'ψ',0:'ps'}
    replace[969] = {1:u'ω',0:'w'}
    replace[970] = {1:u'ϊ',0:'i'}
    replace[972] = {1:u'ό',0:'o'}
    replace[973] = {1:u'ύ',0:'u'}
    replace[974] = {1:u'ώ',0:'w'}
    replace[977] = {1:u'ϑ',0:'th'}
    replace[978] = {1:u'ϒ',0:'y'}
    replace[982] = {1:u'ϖ',0:'p'}
    replace[1040] = {1:u'А',0:'A'}
    replace[1072] = {1:u'а',0:'a'}
    replace[1041] = {1:u'Б',0:'B'}
    replace[1073] = {1:u'б',0:'b'}
    replace[1042] = {1:u'В',0:'V'}
    replace[1074] = {1:u'в',0:'v'}
    replace[1043] = {1:u'Г',0:'G'}
    replace[1075] = {1:u'г',0:'g'}
    replace[1044] = {1:u'Д',0:'D'}
    replace[1076] = {1:u'д',0:'d'}
    replace[1045] = {1:u'Е',0:'E'}
    replace[1077] = {1:u'е',0:'e'}
    replace[1046] = {1:u'Ж',0:'Zh'}
    replace[1078] = {1:u'ж',0:'zh'}
    replace[1047] = {1:u'З',0:'Z'}
    replace[1079] = {1:u'з',0:'z'}
    replace[1048] = {1:u'И',0:'I'}
    replace[1080] = {1:u'и',0:'i'}
    replace[1049] = {1:u'Й',0:'Y'}
    replace[1081] = {1:u'й',0:'y'}
    replace[1050] = {1:u'К',0:'K'}
    replace[1082] = {1:u'к',0:'k'}
    replace[1051] = {1:u'Л',0:'L'}
    replace[1083] = {1:u'л',0:'l'}
    replace[1052] = {1:u'М',0:'M'}
    replace[1084] = {1:u'м',0:'m'}
    replace[1053] = {1:u'Н',0:'N'}
    replace[1085] = {1:u'н',0:'n'}
    replace[1054] = {1:u'О',0:'O'}
    replace[1086] = {1:u'о',0:'o'}
    replace[1055] = {1:u'П',0:'P'}
    replace[1087] = {1:u'п',0:'p'}
    replace[1056] = {1:u'Р',0:'R'}
    replace[1088] = {1:u'р',0:'r'}
    replace[1057] = {1:u'С',0:'S'}
    replace[1089] = {1:u'с',0:'s'}
    replace[1058] = {1:u'Т',0:'T'}
    replace[1090] = {1:u'т',0:'t'}
    replace[1059] = {1:u'У',0:'U'}
    replace[1091] = {1:u'у',0:'u'}
    replace[1060] = {1:u'Ф',0:'F'}
    replace[1092] = {1:u'ф',0:'f'}
    replace[1061] = {1:u'Х',0:'H'}
    replace[1093] = {1:u'х',0:'h'}
    replace[1062] = {1:u'Ц',0:'Ts'}
    replace[1094] = {1:u'ц',0:'Ts'}
    replace[1063] = {1:u'Ч',0:'Ch'}
    replace[1095] = {1:u'ч',0:'ch'}
    replace[1064] = {1:u'Ш',0:'Sh'}
    replace[1096] = {1:u'ш',0:'sh'}
    replace[1065] = {1:u'Щ',0:'Sht'}
    replace[1097] = {1:u'щ',0:'sht'}
    replace[1066] = {1:u'Ъ',0:'A'}
    replace[1098] = {1:u'ъ',0:'a'}
    replace[1068] = {1:u'Ь',0:"Y"}
    replace[1100] = {1:u'ь',0:"y"}
    replace[1070] = {1:u'Ю',0:'Yu'}
    replace[1102] = {1:u'ю',0:'yu'}
    replace[1071] = {1:u'Я',0:'Ya'}
    replace[1103] = {1:u'я',0:'ya'}  
    replace[260] = {1:u'Ą',0:'A'}
    replace[261] = {1:u'ą',0:'a'}
    replace[262] = {1:u'Ć',0:'C'}
    replace[263] = {1:u'ć',0:'c'}
    replace[280] = {1:u'Ę',0:'E'}
    replace[281] = {1:u'ę',0:'e'}
    replace[321] = {1:u'Ł',0:'L'}
    replace[322] = {1:u'ł',0:'l'}
    replace[323] = {1:u'Ń',0:'N'}
    replace[324] = {1:u'ń',0:'n'}
    replace[346] = {1:u'Ś',0:'S'}
    replace[347] = {1:u'ś',0:'s'}
    replace[377] = {1:u'Ź',0:'Z'}
    replace[378] = {1:u'ź',0:'z'}
    replace[379] = {1:u'Ż',0:'Z'}
    replace[380] = {1:u'ż',0:'z'}
    replace[8211] = {1:u'–',0:'-'}
    replace[8220] = {1:u'"',0:'"'}
    replace[8221] = {1:u'"',0:'"'}

    if encod == 'utf-8':
        uml_string = uml_string.decode('utf-8')
    
    ausgabe = ''
    for i in uml_string:
        if i in ['\n','\r']:
            if lb==0:
                ausgabe = ausgabe + ' / '
            else:
                ausgabe = ausgabe + '\n'
        elif i == '\t':
            if uml == 1:
                ausgabe = ausgabe + '\t'
            else:
                ausgabe = ausgabe + '<TAB>'
        elif ord(i) < 125:
            ausgabe = ausgabe + i
        else:  ##Replacement of common special characters.
            if ord(i) in replace.keys():
                ausgabe = ausgabe + replace[ord(i)][uml]
            else:
                ausgabe = ausgabe + '<ORD:' + str(ord(i)) +'>'
                #print('Unknown Character: '+ str(ord(i))+' in: '+ausgabe,0)
        if lc == 1:
            ausgabe = ausgabe.lower()
    return str(ausgabe)


def display_page(e=0):
    global settings
    cmd = '..\\IrfanView\\i_view32.exe "'+settings['PDF-Page']+'"'
##    t = open(settings['PDF-Page'],'r')
##    t.close()
##        
##    print cmd
    #os.system(cmd)
    os.system('rundll32 "%ProgramFiles%\Windows Photo Viewer\PhotoViewer.dll", ImageView_Fullscreen '+settings['PDF-Page'])


def write_data(data,varlist,filename):
    exp_file = open(filename,'w')
    lastvar = varlist[len(varlist)-1]
    for var in varlist:
        exp_file.write(var)
        if not var == lastvar:
            exp_file.write('\t')
    exp_file.write('\n')
    for i in range(0,len(data[varlist[0]])):
        for var in varlist:
            exp_file.write(str(data[var][i]))
            if not var == lastvar:
                exp_file.write('\t')
        exp_file.write('\n')
    exp_file.close()


###
### Initial definition of essential settings (Settings which are called within routines and have to be defined somewhere)
###
###

global settings
settings= {}
settings['Coder'] = 'default' ##May be overwritten by setting some other value in a_settings.ini
settings['Font'] = 'Arial' ##Font in all displayed text (Questions and Text)
settings['Fontsize']="12" ##Font Size within the text display. No effect on question size.
settings['BG_Color']="SystemMenu"
settings['Layout'] = 'Lefty' ##Layout of Angrist. 'Lefty' sets the left-handed design in which the check button is bottom-left. 'Righty' sets right-handed layout with Check on bottom-right.
settings['Curr_Page'] = [['el1','var1'],['el2','var2'],['el3','var3']] ##Temporary storage of current page order. Essential for displaying and storing values.
settings['Page_History'] = [] ##Will contain the whole list of visited pages during program execution
settings['Input'] = ['','',''] ##Temporary Storage of input values. Essential for moste question types.
settings['Path_Log'] = '\nLog of called functions:\n-----------------\n' ##String containing a detailed log-File if debugging is set 1
settings['Verb_Log'] = '\nVerbose progress:\n-----------------\n' ##String containing all comments of the verbose program
settings['Text_Aktiv'] = 0 ##Integer indicating whether the Text display is active (1) or inactive (0).
settings['Fulltext']='' ##String containing the whole text which is coded at the moment.
settings['Text_Encoding']='latin-1'

settings['Verbose'] = '2' ##Verbosity of the program. 0 does not make any notes to the console, 1 is used for coding, 2 is used for debugging.
settings['Debugging'] = '0' ##If set to '1', invalid entries are possible and verbose is set to 1.
settings['Assurance'] = '0' ##May be used to prompt questions at critical points.
settings['AEGLOS'] = '0' ##If set to '1', the aeglos-Module will be attached and used. Only useful after training of this module.
settings['Insecure']='0' ##If set to '1', the coder may report insecurity for certain variables.

settings['Multi_Items']=[] ##Contains variables which give rise to a number of dummies. Variable names are the keys, the number of dummies are the values.
settings['Break'] = 0 ##Currently at break.
settings['Break_Time'] = 0 ##Total break time in this text
settings['Session_Start'] = time.time() ##Start of the coding of this session
settings['Session_Text'] = 0 ##Number of texts in this session (Will be set + 1 at the beginning)
settings['Session_Name'] = 'S_'+str(int(time.time())) ##Name of this session
settings['Country']='ch' ##Current country
settings['Hotwords']=[] ##List of hotwords.
settings['Auto_Highlight'] = 1 ##Mark the hotwords upon loading the text.

settings['Language'] = 'en' ##Language of the codebook (may be used if different codebooks are at disposal. No effect otherwise.
settings['Todo'] = 'to_do.txt' ##Text-File which contains the list of text-files to be coded (with or without extension)
settings['Package_Todo'] = '' ##Text-File containing a list of folders containing articles and a todo-file.
settings['Codebook'] = 'a_codebuch.ini'
settings['Settings'] = 'a_settings.ini'
settings['Retain_Values']=['Author_ID']

settings['Text_Folder'] = 'Probecodierung\\' ##Folder which contains the text-files to be coded.
settings['Out_Track'] = '' ##File to write the tracking-report (no report if set to '')
settings['Out_Tree']='trees.txt' ##File to write the tree files in indented layout (no output if set to '')
settings['Out_JSON']='json_dump.txt' ##File to write the JSON-Outputs (no output if set to '')
settings['Out_Tmp']='tmp_sav.cod' ##File to write the temporary savings (no savings if set to '')
settings['Out_Log']='_log.txt'

root = Tk()
fenster = Anzeige(root)
root.mainloop()
