# -*- coding: latin-1 -*-


###############################################################################################
##                                                                                           ##
##                              ANGRIST 1.2.1 - Coder Interface                              ##
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
try:
    from PIL import ImageTk, Image
except:
    i = 1
import tkMessageBox
import tkFileDialog
import time
import math
import unicodedata
try:
    import aeglos
except:
    i = 1


class CMD: #Auxilliary function for callbacks using parameters. Syntax: CMD(function, argument1, argument2, ...)
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
        self.rowconfigure(6, weight=1) #Only expandable row in the grid is row 6 (above bottomline frame)
        self.columnconfigure(3, weight=1) #Only expandable column in the grid is column 15 (text field)
        self.bind_all("<F1>",self.debug_on)
        self.bind_all("<F2>",self.show_path)
        self.bind_all("<F3>",self.show_verb)
        self.bind_all("<F4>",self.show_storage)
        self.bind_all("<F5>",self.comment)

        root.title("ANGRIST 1.2 - Coder Interface")
        self.fuellen()
        
    def fuellen(self):
        global codebook #codebook, entsprechend der Datei 'codebook.ini'
        global storage #variabletupel, das angibt, welche Variable wie belegt ist
        global dta_pos #Aktuelle Position im Codierbaum. Ein Tupel der Form: (Artikel, Development, Element)
        dta_pos = 'NO DATA YET'
        global prog_pos #Aktuelle Position im codebook. Ein String, der angibt, bei welcher Variable das Programm steht.
        prog_pos = 'NO POSITION YET'
        global def_val #Default-Werte für einzelne Variablen in einem Directory
        def_val = {}
        global settings #Dictionary for flexible settings and entries.

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
        self.spacer = Text(self,width=1,height=45, bg=settings['BG_Color'], relief=FLAT,takefocus = 0)
        self.spacer.grid(row=0,column=0,rowspan=8)

        ##
        ## Below this point all global variables and settings are defined
        ##
        #All settings values set below are overwritten as soon as a
        #file for coder settings is found to specify other settings.

        settings['Highlight_Buttons'] = [['Actor','Act','#ffff66']]
        settings['Multi_Items'] = ['Framing']
        settings['First_Page'] = 'article properties'
        settings['Hotwords']=['Boehner','Cruz','Gray','Holmes','Norton','Issa',
                              'Needham','Obama','Reid']

        if 'Actor' in settings.keys():
            del settings['Actor'] ##Reset upon loading new text

        ##
        ## Below external sources are included to load additional settings
        ##

        global cini
        if available('Settings'):
            try:
                cini = get_codebook(settings['Settings'])
            except:
                verb('ERROR: No settings file found in '+settings['Settings']+'. No coder settings loaded.')
                settings['Settings'] = ''
                cini = {}
        else:
            cini = {}


        if 'Coder-Settings' in cini.keys():
            cset = self.load_cset(cini['Coder-Settings'])
            for i in range(0,len(cset[3])):
                cod = cset[3][i]
                val = cset[2][i]
                settings[cod] = val
            for i in range(0,len(cini['Default-Values'][3])):
                def_val[cini['Default-Values'][3][i]] = cini['Default-Values'][2][i]
            verb('Defaul_Values:'+str(def_val))

          
        codebook = {}
        if available('Codebook'):
            codebook = get_codebook(settings['Codebook'])
        else:
            codebook = get_codebook('a_codebook.ini')
            
        for v in sorted(codebook.keys()):
            verb(v+'; ',nl=0)
        verb('\n'+str(len(codebook.keys()))+' Variables in Codebook.')


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
        storage['#TS'] = (time.ctime(), time.time()) #Timestamp of beginning of coding. Tuple of the shape (String describing time, timestamp in seconds)
        storage['Breaks'] = 0
        storage['Helptexts'] = 0
        storage['Backs'] = 0
        storage['Remove_item'] = 0
        storage['ID'] = art_id
        storage['Highlight'] = {}

        if not art_id == '':
            settings['Fulltext'] = artikelholen(storage['ID'])
            if settings['Text_Format']=='text':
                storage['Fulltext'] = bereinigen(settings['Fulltext'])
            elif settings['Text_Format']=='pic':
                storage['Fulltext'] = 'Picture loaded. No text'
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
            prog_pos = 'ENTER_Art_ID'
        elif settings['Fulltext'] == '':
            verb('ERROR: Article: "' + storage['ID'] + '" in Folder: "' +
                 settings['Text_Folder'] +'" does not exist.')
            codebook['ID'] = codebook['ID2']
            prog_pos = 'ENTER_Art_ID'
        else:
            self.anzeigen(settings['Fulltext'])
            prog_pos = settings['First_Page']

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
        #The MCP function is the core of this interface. In this function all pages of the questionnaire are defined.
        #A variety of self.question...-functions may be used in the questionnaire
        #   self.question_dd(variable, Position): Dropdown selection
        #   self.question_cb(variable, Position): Checkbox (Multiple item selection possible)
        #   self.question_txt(variable, Position): Text input (one line)
        #   self.question_txt2(variable, Position[, width][, height]): Text input (multiple lines)
        #   self.question_rb(variable, Position): Radiobutton selection (Single item selection)
        #   self.question_rat(variable, Position): Multiple Items with 1-5 Scale
        #   self.question_rat2(variable, Position): Multiple Items with 1-2 Scale
        #   self.question_rat7(variable, Position): Multiple Items with 1-7 Scale
        #   self.question_ls(variable, listenvariable): List selection
        #   self.question_lseek(variable,listvariable): Searchable list selection
        #   self.question_ladd(variable,listvariable): Creating a sub-list of a large list
        #   self.question_bt(variable, Position): Up to four buttons to press (each one has to be defined in this function)
        
        if available('Out_Log'):
            settings['Logging_Info'].append([prog_pos,time.time()])
        
        settings['Page_History'].append(prog_pos)
        self.intronase()
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
        self.buttons()

        if prog_pos == 'article properties': #First page if no ID was found in any to-do list
#            self.question_change('Make_Changes',1)
            self.question_dd('Author',1)
            self.question_dd('Genre',2)
            self.question_cb('T2',3)


        elif prog_pos == 'actor highlight':
            self.buttons(0,0,1,1)
            self.question_mark_units('Mark_Text',['Act'])

        elif prog_pos == 'actor list':
            self.buttons(1,0,1,1)
            self.clean_all_tags(['Act']) ##Remove all highlights for speaker. Leave Statement highlights.
            self.show_review('Actor',1)
            self.question_sel_units('Choose_Actor','Act')
            if self.f_questions.Aspliste.size() == 1:
                self.f_questions.Aspliste.selection_set(0)
            elif self.f_questions.Aspliste.size() == 0:
                self.submit('no more actors')
              

        elif prog_pos == 'actor selection':
            self.show_review('Actor',1)
            self.question_dd('Act_ID',1)

        elif prog_pos == 'actor properties':
            if settings['Text_Aktiv']==1:
                print codebook['Act_ID'][3]
                if codebook['Act_ID'][3][0] == 'x':
                    codebook['Act_ID'][3] = codebook['Act_ID'][3][1:]
                    codebook['Act_ID'][2] = codebook['Act_ID'][2][1:]
                self.question_dd('Act_ID',1)
            self.question_dd('Presentation',2)
            self.question_dd('Voice',3)


        elif prog_pos == 'framing':
            self.question_rating('Framing',1,['present','absent'],['1','0'],defval='0')

           
        elif prog_pos == 'otherart':
            self.buttons(0,0,0,1)
            self.ausblenden()

            storage['Codierstart_Lab'] = storage['#TS'][0]

            ##------Export all Data to various Output-Files

            if available('Out_Tree'):
                baum_export(settings['Out_Tree'])

            self.export_data([],['#TS','Codierstart_Lab','Author','Genre',
                                 'Length','Framing'],'_Text.txt')
            
            self.export_data(['Actor'],['#TS','Act_ID','Presentation',
                                        'Voice'],'_Actor.txt')
            
                
            check_todo()
            if available('Settings'):
                verb('Writing Coder information')
                self.cini_schreiben()        

            self.question_bt('Otherart',1)
            self.f_questions.bu1_1.focus()

        elif prog_pos == 'ENTER_Art_ID':
            self.ausblenden()
            self.question_txt('ID',1)

            
        elif prog_pos == 'ende':
            self.buttons(0,0,0,0)
            self.f_questions.Frage2.insert(INSERT,self.namegetter('Location','End'), 'fett')

        else:
            verb('ERROR: Unknown program position for MCP: ' + prog_pos)
                


############################################
##                                        ##
##       SUBMIT - FUNCTION                ##
##                                        ##
############################################
        
    def submit(self,button=0):
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
        #If necessary, the submit-Function will take one argument (button) which may be used in the handling of entries.
        #The button-parameter will also catch the event when binding a widget-event to the submit function.

        accept_entry = 0 #Only if the entry is valid, acceptance is set to 1
        accept_entry = self.check_entries() #Checking for any invalid entries. Returning 1 if everything is OK

        if accept_entry == 1:

            if prog_pos == 'article properties':
                self.store_var_all()
                self.clean_up_all()
                if settings['Text_Aktiv']==1:
                    prog_pos = 'actor highlight'
                else:
                    prog_pos = 'actor selection'
                self.ask()

            elif prog_pos == 'actor highlight':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'actor list'
                self.ask()

            elif prog_pos == 'actor list':
                if button == 'no more actors':
                    self.clean_up_all()
                    prog_pos = 'framing'
                    self.ask()
                else:              
                    self.clean_all_tags(['Act']) #Remove any existing highlights
                    if self.level_down('Choose_Actor','Actor')==1:
                        properties = self.store_var('Choose_Actor',store=0)
                        self.clean_up_all()
                        storage[dta_pos[0]][dta_pos[1]]['Fulltext'] = properties['Fulltext']
                        storage[dta_pos[0]][dta_pos[1]]['Wording'] = properties['Wording']
                        storage[dta_pos[0]][dta_pos[1]]['HL_Start'] = properties['Start']
                        storage[dta_pos[0]][dta_pos[1]]['HL_End'] = properties['End']
                        prog_pos = 'actor properties'
                        self.ask()
                    else:
                        self.message('Invalid-Selection01')
                        verb('ERROR: Unable to go down one level')
                
     
            elif prog_pos == 'actor selection':
                act = self.store_var('Act_ID',store=0)[1]
                if act == 'x':
                    self.clean_up_all()
                    prog_pos = 'framing'
                    self.ask()
                else:
                    if self.level_down('Act_ID','Actor'):
                        self.store_var_all()
                        self.clean_up_all()
                        prog_pos = 'actor properties'
                        self.ask()

            elif prog_pos == 'actor properties':
                self.store_var_all()
                self.clean_up_all()
                if settings['Text_Aktiv']==1:
                    prog_pos = 'actor list'
                    storage['Highlight']['Act'][dta_pos[1]]['Done']=1
                    self.level_up()
                else:
                    self.level_up()
                    prog_pos = 'actor selection'
                self.ask()

            elif prog_pos == 'framing':
                self.store_var_all()
                self.clean_up_all()
                prog_pos = 'otherart'
                self.ask()

            elif prog_pos == 'otherart':
                if button == '1':
                    self.fuellen()
                elif button == '2':
                    self.clean_up_all()
                    prog_pos = 'ende'
                    self.ask()

            elif prog_pos == 'ENTER_Art_ID':
                entered_id = self.store_var('ID')
                
                if len(entered_id) > 1:
                    fname = settings['Text_Folder'] + entered_id +'.txt'
                    verb('-Loading File: '+fname)
                    settings['Fulltext'] = artikelholen(storage['ID'])
                    storage['Fulltext'] = bereinigen(settings['Fulltext'])
                else:
                    self.message("Runtime-Error03")                

                if settings['Fulltext'] == '':
                    if self.message('Runtime-Error06',3):
                        self.clean_up_all()
                        prog_pos = settings['First_Page']  #Go to the page set as first page of the analysis
                        self.ask()
                else:
                    self.anzeigen(settings['Fulltext'])
                    self.clean_up_all()
                    prog_pos = settings['First_Page']
                    self.ask()                         
            else:
                verb("ERROR: The program position '"+prog_pos+"' is not defined for SUBMIT")
        else:
            verb('Invalid Entries')


############################################
##                                        ##
##       Individual Functions             ##
##       for each project                 ##
##                                        ##
############################################

        
    def abort(self):
        #This function is called by the abort-button. For each page on which the abort-button is enabled
        #this function has to be defined.
        #The abort-function may also be called by other buttons such as questions defined in the MCP function      
        global prog_pos
        global dta_pos
        log('Calling Function: Abort')

        if prog_pos == 'page':
            self.clean_up_all()
            prog_pos = 'next page'
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
            if prog_pos == ['actor presentation']: ## Jumping back from the coding of a speaker
                del storage[dta_pos[0]][dta_pos[1]]
                self.level_up()
                prog_pos = 'actor selection'
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


    def rb_tamper(self):
        #This function will be called whenever the value of a Radiobutton is changed. It may be used to
        #Change the display according to the current selection.
        #This function has to be defined for all pages on which it is needed.  
        global prog_pos
        log('Calling Function: RB-Tamper')

        if prog_pos == 'example':
            verb('Doing nothing')
        else:
            verb('Error: RB-Tamper not defined for this page.')             

            
############################################
##                                        ##
##       Question-Functions               ##
##                                        ##
############################################


    def question_dd(self, cb_var, question_pos,width=40): #Dropdown-Question: Up to three dropdown selections may be displayed per page
        global settings
        log('--Question: Dropdown. Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        #### Setting the default value according to text statistics using AEGLOS:
        if settings['AEGLOS']:
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'])
            wert = self.namegetter(cb_var,pred)
            if not wert == '':
                if not cb_var in def_val.keys():
                    def_val[cb_var] = wert
                    verb('Automated determination of the value')
                    verb('Best prediction: '+str(pred)+' Value: '+str(wert))
                else:
                    verb('Another default value has been set already. No changes made')

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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
        if settings['AEGLOS']:
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
                    verb('Old Default-Value set: '+str(def_val[vname]))
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
        if settings['AEGLOS']:
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'])
            wert = self.namegetter(cb_var,pred)
            if not wert == '':
                if not cb_var in def_val.keys():
                    def_val[cb_var] = pred                    
                    verb('Automated value determination')
                    verb('Best prediction: '+str(pred)+ 'Value: '+str(wert))
                else:
                    verb('Another default value has been set already. No changes made')

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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
            if settings['Insecure']:
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
                self.f_questions.bu1_1 = Button(self.f_questions, text=auswliste[0], width=20, command=CMD(self.submit,codebook[cb_var][3][0]))
                self.f_questions.bu1_1.grid(row=3,column=1, sticky = W)
            if anzahl > 1:
                self.f_questions.bu1_2 = Button(self.f_questions, text=auswliste[1], width=20, command=CMD(self.submit,codebook[cb_var][3][1]))
                self.f_questions.bu1_2.grid(row=3,column=2, sticky = W)
            if anzahl > 2:
                self.f_questions.bu1_3 = Button(self.f_questions, text=auswliste[2], width=20, command=CMD(self.submit,codebook[cb_var][3][2]))
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
        if settings['AEGLOS']:
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'],top=5)
            for item in pred:
                wert = self.namegetter(liste,item)
                predlist.append(wert)
            if len(predlist) > 0:
                if not cb_var in def_val.keys():
                    def_val[cb_var] = predlist
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
        if settings['AEGLOS']:
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'],top=5)
            for item in pred:
                wert = self.namegetter(liste,item)
                predlist.append(wert)
            if len(predlist) > 0:
                if not cb_var in def_val.keys():
                    def_val[cb_var] = predlist
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
        if settings['AEGLOS']:
            wert = -1
            pred = acabc.predict_short(cb_var,settings['Fulltext'],top=5)
            for item in pred:
                wert = self.namegetter(liste,item)
                predlist.append(wert)
            if len(predlist) > 0:
                if not cb_var in def_val.keys():
                    def_val[cb_var] = predlist
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



    def question_file(self, cb_var, question_pos, mode='load'):
        log('--Question: Filename. Variable: '+cb_var+'; Position: '+str(question_pos),pos=0)
        width=50
        
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
            settings['Curr_Page'][0] = ['file',cb_var]
            self.f_questions.Frage1.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage1.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt1 = Entry(self.f_questions, width=width)
            self.f_questions.txt1.grid(row=3,column=0,columnspan=2,sticky=E+W)
            self.f_questions.getselect1 = Button(self.f_questions,text='Browse...',command=CMD(self.opendialog,mode,question_pos))
            self.f_questions.getselect1.grid(row=3,column=2,sticky=W)
            self.f_questions.help1 = Label(self.f_questions, text="?")
            self.f_questions.help1.grid(row=3, column=3, sticky=E)
            self.f_questions.help1.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.txt1.insert(END,str(previous_coding))
                
        if question_pos == 2:
            settings['Curr_Page'][1] = ['file',cb_var]
            self.f_questions.Frage2.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage2.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt2 = Entry(self.f_questions, width=width)
            self.f_questions.txt2.grid(row=7,column=0,columnspan=2,sticky=E+W)
            self.f_questions.getselect2 = Button(self.f_questions,text='Browse...',command=CMD(self.opendialog,mode,question_pos))
            self.f_questions.getselect2.grid(row=7,column=2,sticky=W)
            self.f_questions.help2 = Label(self.f_questions, text="?")
            self.f_questions.help2.grid(row=7, column=3, sticky=E)
            self.f_questions.help2.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.txt2.insert(END,str(previous_coding))
                
        if question_pos == 3:
            settings['Curr_Page'][2] = ['file',cb_var]
            self.f_questions.Frage3.insert(INSERT,codebook[cb_var][0], 'fett') #Question
            self.f_questions.Frage3.insert(END, codebook[cb_var][1]) #Coder information
            self.f_questions.txt3 = Entry(self.f_questions, width=width)
            self.f_questions.txt3.grid(row=11,column=0,columnspan=2,sticky=E+W)
            self.f_questions.getselect3 = Button(self.f_questions,text='Browse...',command=CMD(self.opendialog,mode,question_pos))
            self.f_questions.getselect3.grid(row=11,column=2,sticky=W)
            self.f_questions.help3 = Label(self.f_questions, text="?")
            self.f_questions.help3.grid(row=11, column=3, sticky=E)
            self.f_questions.help3.bind('<Button-1>', CMD(self.hilfe_zu, codebook[cb_var][4]))
            self.f_questions.txt3.insert(END,str(previous_coding))




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
            a.write('Coder\tText_ID\t')
            for d in dta_pos_all:
                a.write(d+'_Level\t'+d+'_ID\t')
            for v in varlist[:-1]:
                if v in settings['Multi_Items']:
                    for code in codebook[v][3]:
                        a.write(v+'_'+code+'\t')
                else:
                    a.write(v+'\t')
            v = varlist[-1]
            if v in settings['Multi_Items']:
                for code in codebook[v][3]:
                    a.write(v+'_'+code)
            else:
                a.write(v)
            
            if len(dta_pos_all) == 0:
                a.write('\tT_Brutto\tT_Break\tT_Netto\tT_H\tSessiontext\tSession_ID')
            a.write('\n')
            a.close()
            
        log('Calling Function: Export_Data of all elements in: '+ str(dta_pos_all))
        if len(dta_pos_all) == 3:
            verb('Fourth Level of Analysis')
            if dta_pos_all[0] in storage.keys():
                for i in storage[dta_pos_all[0]].keys():
                    if dta_pos_all[1] in storage[dta_pos_all[0]][i].keys():
                        for k in storage[dta_pos_all[0]][i][dta_pos_all[1]].keys():
                            if dta_pos_all[2] in storage[dta_pos_all[0]][i][dta_pos_all[1]][k].keys():
                                for l in storage[dta_pos_all[0]][i][dta_pos_all[1]][k][dta_pos_all[2]].keys():
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
                for i in storage[dta_pos_all[0]].keys():
                    if dta_pos_all[1] in storage[dta_pos_all[0]][i].keys():
                        for k in storage[dta_pos_all[0]][i][dta_pos_all[1]].keys():
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
                for i in storage[dta_pos_all[0]].keys():
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
                if type(dictionary[variabel][1]) == list:
                    if len(dictionary[variabel][1]) == 1:
                        dictionary[variabel] = (dictionary[variabel][0][0],dictionary[variabel][1][0])
                    elif len(dictionary[variabel][1]) == 0:
                        dictionary[variabel] = ('','')
                if not dictionary[variabel][1] == '':
                    exp_file.write(str(dictionary[variabel][1]))
                else:
                    exp_file.write(bereinigen(dictionary[variabel][0]))
                exp_file.write('\t')
            elif type(dictionary[variabel]) == str or type(dictionary[variabel]) == unicode:
                if debug == 1: exp_file.write(variabel+"=")
                exp_file.write(bereinigen(dictionary[variabel]))
                exp_file.write('\t')
            elif type(dictionary[variabel]) == dict:
                for item in codebook[variabel][3]:
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

##        self.f_bottomline.b_check.grid_remove()
##        self.f_bottomline.b_abort.grid_remove()
##        self.f_bottomline.b_back.grid_remove()

        self.menubar = Frame(self,borderwidth=2, bg=settings['BG_Color'], relief=RAISED)
        self.menubar.grid(row=0,column=c1,columnspan=2,sticky=W+E)

        self.menubar.deb = Menubutton(self.menubar, text="Help",relief=RAISED)
        self.menubar.deb.grid(row=0,column=9,sticky=N+E)
        self.menubar.deb.menu = Menu(self.menubar.deb, tearoff=0)
        self.menubar.deb["menu"] = self.menubar.deb.menu

        self.menubar.fmen = Menubutton(self.menubar, text="File",relief=RAISED)
        self.menubar.fmen.grid(row=0,column=0,sticky=N+W)
        self.menubar.fmen.menu = Menu(self.menubar.fmen, tearoff=0)
        self.menubar.fmen["menu"] = self.menubar.fmen.menu

        self.menubar.set = Menubutton(self.menubar, text="Settings",relief=RAISED)
        self.menubar.set.grid(row=0,column=1,sticky=N+W)
        self.menubar.set.menu = Menu(self.menubar.set, tearoff=0)
        self.menubar.set["menu"] = self.menubar.set.menu

##        self.menubar.tools = Menubutton(self.menubar, text="Tools",relief=RAISED)
##        self.menubar.tools.grid(row=0,column=1,sticky=N+W)
##        self.menubar.tools.menu = Menu(self.menubar.tools, tearoff=0)
##        self.menubar.tools["menu"] = self.menubar.tools.menu


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
        self.menubar.fmen.menu.add_command(label="Create SPSS labelling syntax",command=self.spss_syntax)


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
            dta = get_data('_Text.txt')[0]
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

            d_total = time.strftime("%H:%M:%S",time.gmtime(dur_total))
            d_week = time.strftime("%H:%M:%S",time.gmtime(dur_week))
            d_day = time.strftime("%H:%M:%S",time.gmtime(dur_day))

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
            outtext = outtext + '{:20}'.format('Period')+'{:20}'.format('Number of Texts')+'{:20}'.format('Duration')+'{:20}'.format('Time per Text')
            outtext = outtext + '\n--------------------------------------------------------------------------------\n'
            outtext = outtext + '{:20}'.format('All Time')+'{:20}'.format(str(anz_total))+'{:20}'.format(d_total)+'{:20}'.format(m_total)+'\n'
            outtext = outtext + '{:20}'.format('This Week')+'{:20}'.format(str(anz_week))+'{:20}'.format(d_week)+'{:20}'.format(m_week)+'\n'
            outtext = outtext + '{:20}'.format('Today (last 24h)')+'{:20}'.format(str(anz_day))+'{:20}'.format(d_day)+'{:20}'.format(m_day)+'\n'

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
            storage['#TS2']=(time.ctime(), time.time())
            out = open(fname,'w')
            out.write(str(storage))
            out.close()
        verb('Stored: '+bereinigen(fname))

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
            verb(baum_schreiben(storage,trunc=40))
            
            if '#TS2' in storage.keys():
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
        out = str(baum_schreiben(storage,trunc=50))
        self.display_text(out)

    def show_settings(self,event=0):
        tmp_dic = {}
        for c in settings.keys():
            if not c in ['Verb_Log','Path_Log']:
                tmp_dic[c] = settings[c]
        out = str(baum_schreiben(tmp_dic,trunc=50))
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
        out = out + str(baum_schreiben(curr(),trunc=50))
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
       
    def show_review(self,level,rm=1,edit=0,height=3):
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
        if edit == 0:
            self.f_review.b_edit.grid_remove()
            
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
            prog_pos = 'statements'
        elif dta_pos[0]=='Speaker' and dta_pos[2]=='Issue':
            prog_pos = 'i_style'
        elif dta_pos[0]=='Speaker' and dta_pos[2]=='ActEval':
            prog_pos = 'e_spec'

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
                        storage[level][ident] = {}
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
        global settings
        global storage
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
                if arttext == settings['Fulltext']:
                    print 'ok'

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

                verb(baum_schreiben(storage['Highlight'],trunc=40))
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
                    if settings['Insecure']:
                        self.f_questions.ins1.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
                if pos == 2:
                    self.f_questions.dd2.destroy()
                    self.f_questions.help2.destroy()
                    self.f_questions.Frage2.delete("1.0",END)
                    if settings['Insecure']:
                        self.f_questions.ins2.destroy()
                    settings['Curr_Page'][pos-1] = ['','']
                if pos == 3:
                    self.f_questions.dd3.destroy()
                    self.f_questions.help3.destroy()
                    self.f_questions.Frage3.delete("1.0",END)
                    if settings['Insecure']:
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
            else:
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


        if settings['Text_Format']=='text':
            try:
                if available('Text_Encoding'):        
                    text = text.decode(settings['Text_Encoding'],'ignore')
                    text = text.encode('latin-1','ignore')
            except:
                verb('ERROR: Problem occurred during decoding the text')
                text = bereinigen(text,lb=1,uml=1)
                    
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
        elif settings['Text_Format']=='pic':
            cols = [3,4]
            self.yscroller = Scrollbar(self, orient=VERTICAL)
            self.yscroller.grid(row=1, rowspan=6, column=cols[1], sticky=W+N+S)
            self.xscroller = Scrollbar(self, orient=HORIZONTAL)
            self.xscroller.grid(row=7, column=cols[0], sticky=E+W)
            self.Artikel = Canvas(self, bg='#ffffff',yscrollcommand=self.yscroller.set,
                                  xscrollcommand=self.xscroller.set,takefocus = 0)
            self.Artikel.grid(row=1, rowspan=6, column=cols[0], sticky=N+E+S+W)
            self.yscroller["command"] = self.Artikel.yview
            self.xscroller["command"] = self.Artikel.xview
            self.Artikel.pic = Label(self.Artikel, image=text)
            self.Artikel.pic.grid(row=1,column=1)


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
        else:
            zeit = time.time() - settings['Break']
            settings['Break'] = 0
            settings['Break_Time'] = settings['Break_Time'] + zeit
            settings['Session_Start'] = settings['Session_Start'] + zeit
            self.f_bottomline.b_break["text"] = 'Break'
            self.pausentext.destroy()


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
                            c_file.write(def_val[dvar])
                            c_file.write('\n')                    
            else:                
                for i in range(0,len(cini[variable][2])):
                    c_file.write(str(cini[variable][3][i]))
                    c_file.write(':')
                    c_file.write(str(cini[variable][2][i]))
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
    log('Calling Function: Artikelholen for text ID: "'+str(ID)+'"',pos=0)
    at = ""
    if ID[-4] == '.':
        art_filen = settings['Text_Folder'] + ID
    else:
        art_filen = settings['Text_Folder'] + ID + '.txt'

    if ID[-4:].lower() in ['.jpg','.bmp','.png']:
        settings['Text_Format'] = 'pic'

    settings['Filename']=art_filen

    if settings['Text_Format'] == 'pic':
        at = ImageTk.PhotoImage(Image.open(art_filen))
    else:
        verb('Loading: ' + str(art_filen))
        try:
            art_file = open(art_filen, 'r')
            F_list = art_file.readlines()
            verb(' - Length of file: '+str(len(F_list))+' lines.')
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

    ##Hier kann aus den Zeilen des Artikels Information gewonnen werden. Falls erwünscht.


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

            verb(varname+str(optionen))

            cb[varname] = []
            cb[varname].append(varfrage) #codebook['variable'][0] is the question as string (including final linebreak)
            cb[varname].append(varanw)   #codebook['variable'][1] is the coder information
            cb[varname].append(optionen) #codebook['variable'][2] is a list containing all labels
            cb[varname].append(codes)    #codebook['variable'][3] is a list containing all codes (parallel to [2]
            cb[varname].append(varhilfe)    #codebook['variable'][4] is the helptext
        i = i + 1
    
    verb('Codebook loaded successfully')
    return cb


def log(name,pos=1):
    ## Making Log-Entries for called functions and events.
    global settings
    global prog_pos
    global dta_pos
    if settings['Verbose'] >0:
        if pos == 1:
            settings['Verb_Log']=settings['Verb_Log']+name+'. Prog_Pos='+prog_pos+'; DTA-Pos='+ str(dta_pos) + '\n'
        else:
            settings['Verb_Log']=settings['Verb_Log']+name+'\n'
    if pos == 1:
        settings['Path_Log']=settings['Path_Log']+name+'. Prog_Pos='+prog_pos+'; DTA-Pos='+ str(dta_pos) + '\n'
    else:
        settings['Path_Log']=settings['Path_Log']+name+'\n'

def verb(name,stage=1,nl=1):
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
    verb(baum_schreiben(curr_tree,trunc=30))
    return curr_tree

def critical_abort():
    Anzeige.destroy()

def available(key):
    ##Checks whether a setting is available in the settings-directory.
    ##Available means: The key is present and if the value is a string this string is non-empty
    global settupel
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
    if art_name == '':
        verb('no todo')
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
    log('Exporting Storage dictionary')
    global settings
    global storage
    settings['Coding_Time'] = time.time() - storage['#TS'][1]
    if available('Out_Tree'):
        verb('Writing indented tree')
        exp_file = open(settings['Out_Tree'], 'a')
        exp_file.write('\n------------------------------\n')
        exp_file.write('Codierung von Codierer:\n')
        exp_file.write(settings['Coder'])
        exp_file.write('\nZu Artikel:\n')
        exp_file.write(storage['ID'])
        exp_file.write('\nDauer:\n')
        exp_file.write(str(settings['Coding_Time']))        
        exp_file.write('\n------------------------------\n')

        tr = baum_schreiben(storage, spc='\t', trunc=0)

        exp_file.write('\n'+tr)
        exp_file.write('\n\n\ENDE')                
        exp_file.close()
    else:
        verb('No location for Out_Tree specified. No tree exported')

    if available('Out_JSON'):
        verb('Output of JSON format')
        json = str(storage)
        js_out = open(settings['Out_JSON'],'a')
        js_out.write(json)
        js_out.write('\n')
        js_out.close()
    else:
        verb('No location for Out_Json specified. Json not exported')


    
def get_varnames(filename,header=1,sep='\t'):
    log('Calling Function: Get Varnames. Separator: '+sep+'; Header: '+str(header))
    try:
        inp_file = open(filename, 'r')
        varline = inp_file.readline()[:-1]
        inp_file.close()
        vlist = []
    except:
        vlist = 0
    if not vlist == 0:
        varnames = varline.split(sep)
        for varname in varnames:
            if len(varname) == 0: varname = '_'
            if varname[0] in ['"',"'"]: varname = varname[1:]
            if varname[-1] in ['"',"'"]: varname = varname[:-1]
            if len(varname) == 0: varname = '_'
            nr = 1
            vlab = varname
            while varname in vlist:
                varname = vlab + "{0:02}".format(nr)
                nr = nr + 1
            vlist.append(varname)       
        if header == '0':
            nv = []
            for i in range(len(vlist)): nv.append('VAR'+"{0:02}".format(i))
            vlist = nv        
    return vlist

def get_data(filename, header=1, sep='\t', varlist = [],verbose=0):
    errmsg = ''
    try:
        inp_file = open(filename, 'r')
        dtalines = inp_file.readlines()
        inp_file.close()
        
        data_dic = {}
    except:
        data_dic = 0
        errmsg = 'The file "'+filename+'" is not valid or does not exist'

    if data_dic == 0:
        summary = 'Unable to load data.'
    else:
        if varlist == []: varlist = get_varnames(filename,header,sep) #Get variable names
        first_line = 0
        if header in [1,'1']: first_line = 1 #Remove header
        for var in varlist: data_dic[var] = [] #Set up data dic

        for i in range(first_line,len(dtalines)):
            dtaline = dtalines[i]
            if len(dtaline) < 2:
                errmsg = errmsg + 'ERROR: line '+str(i)+' is empty. Ignoring Line\n'
            else:
                if dtaline[-1] == '\n':
                    dtaline = dtaline[:-1]
                dta = dtaline.split(sep)
                if len(dta) == len(varlist):
                    for k in range(len(dta)):
                        value = dta[k]
                        if value == ' ': value = ''
                        if len(value) > 1:
                            if value[0] in ['"',"'"] and value[-1] in ['"',"'"]: value = value[1:-1]
                        data_dic[varlist[k]].append(value)
                elif len(dta) > len(varlist):
                    errmsg = errmsg + 'ERROR: line '+str(i)+' has more values than variables (N='+str(len(dta))+'). Ignoring line'
                else:
                    errmsg = errmsg + 'ERROR: line '+str(i)+' has less values than variables (N='+str(len(dta))+'). Ignoring line'

        ncases = len(data_dic[varlist[0]])
        nvars = len(varlist)
        nerr = len(errmsg.split('\n'))-1
        summary = 'Data loaded.\n'+str(ncases)+' Cases\n'+str(nvars)+' Variables\n'+str(nerr)+' Invalid lines'

        if len(errmsg)>2: verb('Errors while loading file: "'+filename+'"\n'+errmsg,verbose)
        verb('\n'+summary,verbose)
        
    return [data_dic, varlist, summary, errmsg]

def write_data(data,init_varlist,filename,header=1,sep='\t',verbose=0):
    errmsg = ''
    varlist = []
    varlen = []
    for v in init_varlist: #Check for completeness before starting
        if v in data.keys():
            if not v in varlist:
                varlist.append(v)
            else:
                errmsg = errmsg + 'ERROR: Variable "'+v+'" twice in output. Skipping variable\n'
            varlen.append(len(data[v]))
        else:
            errmsg = errmsg + 'ERROR: Variable "'+v+'" not in data. Skipping variable\n'

    if not min(varlen) == max(varlen):
        errmsg = errmsg + 'ERROR: Not all variables have the equal amount of cases:\n'
        errmsg = errmsg + ' - Using the first variable as standard: '+str(varlen[0])+' cases.\n'
        remvar = []
        for v in varlist:
            if not len(data[v]) == varlen[0]:
                errmsg = errmsg + ' - Variable "'+v+'" deviant ('+str(len(data[v]))+' cases). Skipping variable\n'
                remvar.append(v)
        for v in remvar:
            varlist.remove(v)

    try:
        exp_file = open(filename,'w')
    except:
        varlist = []
        errmsg = errmsg + 'ERROR: File '+filename+' could not be created. Invalid filename.\n'

    if len(varlist) > 0:     
        if header == 1:
            for k in range(len(varlist)):
                exp_file.write(varlist[k])
                if k < len(varlist)-1:
                    exp_file.write(sep)
                else:
                    exp_file.write('\n')

        for i in range(len(data[varlist[0]])):
            for k in range(len(varlist)):
                outval = data[varlist[k]][i]
                if type(outval) == float:
                    if outval == int(outval):
                        outval = int(outval)
                exp_file.write(str(outval))
                if k < len(varlist)-1:
                    exp_file.write(sep)
                else:
                    exp_file.write('\n')

        exp_file.close()
        outtext = 'File "'+filename+'" successfully created.\n'
        outtext = outtext + str(len(data[varlist[0]])) + ' Cases\n'+str(len(varlist))+' Variables\n'
    else:
        outtext = 'File "'+filename+'" could not be created.\n'

    if len(errmsg)>2: verb('Errors while writing data to: "'+filename+'"\n'+errmsg,verbose)
    verb('\n'+outtext,verbose)
    
    return [outtext,errmsg]


def get_directory(extensions):
    extlist = []
    for extension in extensions:
        if not '.' in extension:
            if len(extension) in [2,3,4]:
                extension = '*.' + extension
                extlist.append(extension)
            else:
                verb('ERROR: invalid extension for directory-command: '+extension)
        else:
            extlist.append(extension)

    outlist = []

    if len(extlist) >0:
        for e in extlist:
            os.system('dir '+e+' /b >direc.tmp')
            time.sleep(0.3)
            direc = open('direc.tmp','r')
            fnames = direc.readlines()
            direc.close()
            time.sleep(0.3)
            os.system('del direc.tmp')
            for f in fnames:
                outlist.append(f[:-1])
                verb('File found and added: '+f)
    else:
        verb('ERROR: No valid extensions found')

    return outlist


def get_unique(liste):
    td = {}
    for l in liste: td[str(l)] = 0
    return sorted(td.keys())


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


def bereinigen(uml_string, lc=0,lb=0,uml=0):
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
    replace[163] = {1:'lbs.',0:'lbs.'}
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
settings['Text_Format'] = 'text'
settings['Fulltext']='' ##String containing the whole text which is coded at the moment.
settings['Text_Encoding']='latin-1'

settings['Verbose'] = 2 ##Verbosity of the program. 0 does not make any notes to the console, 1 is used for coding, 2 is used for debugging.
settings['Debugging'] = 0 ##If set to '1', invalid entries are possible and verbose is set to 1.
settings['AEGLOS'] = 0 ##If set to '1', the aeglos-Module will be attached and used. Only useful after training of this module.
settings['Insecure']=0 ##If set to '1', the coder may report insecurity for certain variables.

settings['Multi_Items']=[] ##Contains variables which give rise to a number of dummies. Variable names are the keys, the number of dummies are the values.
settings['Break'] = 0 ##Currently at break.
settings['Break_Time'] = 0 ##Total break time in this text
settings['Session_Start'] = time.time() ##Start of the coding of this session
settings['Session_Text'] = 0 ##Number of texts in this session (Will be set + 1 at the beginning)
settings['Session_Name'] = 'S_'+str(int(time.time())) ##Name of this session
settings['Hotwords']=[] ##List of hotwords.
settings['Auto_Highlight'] = 1 ##Mark the hotwords upon loading the text.

settings['Todo'] = 'to_do.txt' ##Text-File which contains the list of text-files to be coded (with or without extension)
settings['Package_Todo'] = '' ##Text-File containing a list of folders containing articles and a todo-file.
settings['Codebook'] = 'a_codebook.ini'
settings['Settings'] = 'a_settings.ini'

settings['Text_Folder'] = 'Text\\' ##Folder which contains the text-files to be coded.
settings['Out_Track'] = '' ##File to write the tracking-report (no report if set to '')
settings['Out_Tree']='' ##File to write the tree files in indented layout (no output if set to '')
settings['Out_JSON']='' ##File to write the JSON-Outputs (no output if set to '')
settings['Out_Tmp']='' ##File to write the temporary savings (no savings if set to '')
settings['Out_Log']=''

root = Tk()
fenster = Anzeige(root)
root.mainloop()
