
"""

@author: Leonardo Bonetti, David Quiroga

leonardo.bonetti@psych.ox.ac.uk
leonardo.bonetti@clin.au.dk

"""


#################### INFORMATION THAT MUST BE UPDATED BEFORE RUNNING THE SCRIPT ####################

#logdir = ('D:\\Leonardo task\\Leonardo task\\Scripts_LeonardoChunyan_Shangai\\Block1_EncodingRecognition') #directory where you have the folder named 'StimuliBlock1' which contains the stimuli
import os
 #directory where you have the folder named 'StimuliBlock1' which contains the stimuli
logdir = os.path.dirname(os.path.abspath("__file__")).replace('\\','/')
os.chdir(logdir)
#frate = 60 #60 #refresh rate of the monitor (i.e.  number of times per second that the screen is redrawn); Typically is 60 Hz in standard monitors and 120 Hz in better monitors. Please check and update according to your setting.
response_buttons = [1, 2] #I assume participants will use buttons 1 and 2 in your response pad. If not, please change them here
random_enc_l = 1 #1 for randomising the order of the melodies in the learnig phase (e.g. m2-m1-m3-m3-m2-m1-m2-m1-m3); 0 for no randomisation (i.e. m1-m1-m1.. m2-m2-m2.. m3-m3-m3)
#PLEASE, USE random_enc_l = 1; 0 would make the learning easier and could be used only if we see that the patients are very bad at doing the task

#In addition:
  #1) Be sure that the folder 'StimuliBlock1' which contains the stimuli is in the 'logdir' that you chose.

#################### #################### ####################

#################### Load libraries and set directories ####################

#please donwlowad the libraries that you do not have

from random import shuffle
from psychopy import prefs
#prefs.hardware['audioLib'] = ['sounddevice']
prefs.hardware['audioLib'] = ['PTB']
try:
    prefs.hardware['audioDevice'] = ['sysdefault']
    print('using sysdefault audio device')
except NotImplementedError:
    print('could not setup sysdefault audio device')
# prefs.hardware['audioLib'] = ['pygame']
from psychopy import visual, core, sound, event, gui, monitors, logging
import itertools as it
from datetime import datetime
import numpy as np
import csv
import sys

### TRIGGER ###
#from psychopy import parallel
from triggers import setParallelData
setParallelData(0)

#silentDur = .5
#silent = sound.Sound('C', secs=silentDur, volume=0.7, stereo = False)
break_length1 = 120# 120
break_length2 = 120#120
#################### Actual code ####################

# quit key (to terminate the experiment)
def quitpd():
    win.close()
    logging.flush()
    logfile.close()
    core.quit()

# create folders if not already present
def create_directory(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' already exists.")

event.globalKeys.add(key='escape',func=quitpd)

#settings for delivering triggers
# port = parallel.ParallelPort(address=0x0378)
# port.setData(0)

#GUI for subject ID
ID = gui.Dlg(title = 'subj ID')
ID.addField('ID: ')
ID.addField('Pre-task rest (sec): ', str(break_length1))
ID.addField('Mid-task rest (sec): ', str(break_length2))

subID = ID.show()

break_length1 = int(subID[1])
break_length2 = int(subID[2])

#filename = logdir + '\\csv_files\\Subj_' + subID[0] + '_Block_1_EncodingRecognition.csv' #name for the csv file
cdate = datetime.now()
ctime = '{}-{}-{}_{}-{}-{}'.format(cdate.year,cdate.month,cdate.day,cdate.hour,cdate.minute,cdate.second)

filename = f'{logdir}/logs/{ctime}_Subj_{subID[0]}_Block_1_EncodingRecognition.csv' #name for the csv file
if os.path.exists(filename): #checking that the file does not exist already, to prevent risks of overwriting previous files
    print('THE FILE NAMED ' + filename + ' ALREADY EXIST!! Check the ID of your current subject')
else:
    #create log_files directory if they do not exist
    directory_path = logdir + '/logs'
    create_directory(directory_path)
    # #create csv_files directory if they do not exist
    # directory_path = logdir + '/csv_files'
    # create_directory(directory_path)

    logfile = open(filename,'w') #create csv file for the subject
    logfile.write("subj;trial;response;RT;Trig;accuracy\n") #prepare columns in the csv file

    #create log file
    filename = f'{logdir}/logs/{ctime}_Subj_{subID[0]}_Block_1_EncodingRecognition.log'
    lastLog = logging.LogFile(filename, level=logging.INFO, filemode='a')

    #getting audio files and storing them for later presentation (learning phase)
    os.chdir(logdir + '/StimuliBlock1_Encoding_48k')
    pathwave = logdir + '/StimuliBlock1_Encoding_48k'
    wavefilesd = []
    wavenamesd = []
    for file in sorted(os.listdir(pathwave)): #over files in directory
        if file.endswith(".wav"): #if the file is an audio file
            wavenamesd.append(file) #file name is appended
            wavefilesd.append(sound.Sound(file))#,volume = 0.7)) #file audio is appended

    wavezip_enc = list(zip(wavenamesd,wavefilesd)) #zipping together file names and file audios

    if random_enc_l == 1: #randomising order of trials for the learning phase, only if requested by user
        shuffle(wavezip_enc)


    #getting audio files and storing them for later presentation (recognition phase)
    os.chdir(logdir + '/StimuliBlock1_Recognition_48k')
    pathwave = logdir + '/StimuliBlock1_Recognition_48k'
    wavefilesd = []
    wavenamesd = []
    for file in sorted(os.listdir(pathwave)): #over files in directory
        if file.endswith(".wav"): #if the file is an audio file
            wavenamesd.append(file) #file name is appended
            wavefilesd.append(sound.Sound(file))#,volume = 0.7)) #file audio is appended

    wavezip = list(zip(wavenamesd,wavefilesd)) #zipping together file names and file audios
    shuffle(wavezip) #randomising order of trials for the recognition phase

    #initializing RT variable to get RTs (probably no longer necessary, but I decided to keep it)
    RT = core.Clock()

    #preparing window for the screen, first instruction and fixation cross
    win = visual.Window(fullscr = True, color = 'black') #preparing window
    frate = np.round(win.getActualFrameRate())
    prd = 1000/frate #conversion screen refresh rate # FIXXXXX

    # INITIAL PROMPT
    initPrompt = visual.TextStim(win,text = 'In this task, you will memorize some melodies and '
                                             'will play a game where you will have to recall them '
                                             'as accurately as possible\n\n'
                                             'In addition, at the beggining and in the middle '
                                             'of the task, you will be asked to rest and relax '
                                             'for a couple of minutes\n\n press a key to begin',
                                             color = 'gray') #preparing message
    initPrompt.draw()
    win.flip()
    event.waitKeys()

    # INITIAL RESTING STATE
    fix_c = visual.TextStim(win,text = '+', color = 'gray',height = 0.2) #fixation cross
    restext = visual.TextStim(win,text = 'Before the task please have a 2-minute break\n\nYou can relax', color = 'gray') #preparing message
    # pausemex = visual.TextStim(win,text = '现在你有两分钟的休息时间', color = 'gray') #preparing message
    restext.draw() #presenting message
    win.flip()
    core.wait(4) #4-second break for allowing participant to read the instruction

    ### TRIGGER ###
    ParalData = 4#80 #trigger value resting
    win.callOnFlip(setParallelData, int(ParalData))
    for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
        fix_c.draw()
        win.flip()

    setParallelData(0) #close trigger
    for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
        fix_c.draw()
        win.flip()

    ### TRIGGER ###

    #previous loop which prevented to quit the experiment
    #for frs in range(int(np.round(119900/prd))): #time frames corresponding to 50 ms
     #   fix_c.draw()
      #  win.flip()

    #current loop which allows to quit the experiment if th experimenter wishes to do so
    RT.reset()
    resp = None
    while resp == None: #while there is no response
        key = event.getKeys(keyList = ['escape']) #looking for response
        fix_c.draw()
        win.flip()
        if 'escape' in key: #additional precaution to get out in case experimenter presses 'escape' on keyboard
            logging.flush()
            core.quit()
        if RT.getTime() > break_length1: #120
            resp = 0 #in this case response is coded as '0'

    #learning phase instruction (in English)
    instr = visual.TextStim(win,text = 'Learning phase\n\n'
                                       'Now you will listen to a series of melodies repeated several times \n\n'
                                       'Please memorize them as much as possible \n\n'
                                       'Later, you will play a game where you need to recognise these melodies to accumulate points \n\n'
                                       'Press any key to continue',color = 'gray')
    #learning phase instruction (in Chinese)
    # instr = visual.TextStim(win,text = '学习阶段 \n\n 现在你将听到三段音乐，每段重复十遍 \n\n 请尽力记住这三段音乐 \n\n 如已准备好，请按任意键继续',color = 'gray')

    #actual experiment (learning phase)
    #presenting instruction
    instr.draw()
    win.flip()
    event.waitKeys()

    #LEARNING PHASE
    for wavve in range(len(wavezip_enc)): #over repetitions of the melodies to be encoded
    #for wavve in range(1,10): #this is just for testing purposes since it loops over only a few trials
        jes = 'Repetition number ' + str((wavve + 1)) + ' / 30' #text for the repetition number
        # jes = '重复的次数 ' + str((wavve + 1)) + ' / 30' #text for the repetition number
        playlear = visual.TextStim(win,text = jes, color = 'gray') #preparing information for the message
        playlear.draw() #showing message
        win.flip()
        core.wait(1) #duration of 1 second
        fix_c.draw() #fixation cross
        win.flip()
        core.wait(0.5) #waiting half second

        if 'm1' in wavezip_enc[wavve][0]: #old melody 1
            trigval = 1 #70 trigvalue
        elif 'm2' in wavezip_enc[wavve][0]: #old melody 2
            trigval = 2 #80 trigvalue
        elif 'm3' in wavezip_enc[wavve][0]: #old melody 3
            trigval = 3 #90 trigvalue

        ### TRIGGER ###
        nextFlip = win.getFutureFlipTime(clock='ptb') #getting next flip time
        ParalData = trigval #assigning trigger value
        win.callOnFlip(setParallelData, int(ParalData))

        ### TRIGGER ###
        wavezip_enc[wavve][1].play(when = nextFlip) #playing sound, exactly at next flip
        #event.clearEvents(eventType='keyboard')
        RT.reset()
        resp = None

        ### TRIGGER ###
        for frs in range(int(np.round(50/prd))): # 6time frames corresponding to 50 ms
            fix_c.draw()
            win.flip()
        setParallelData(0) #closing trigger
        for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
            fix_c.draw()
            win.flip()

        ### TRIGGER ###
        #writing trial ID
        lrow = '{};{};{};{};{};{} \n' #new row in the csv file
        lrow = lrow.format(subID[0],wavezip_enc[wavve][0], '', '',str(trigval),'1') #storing trial ID
        logfile.write(lrow) #writing on csv

        key = event.getKeys(keyList = ['escape']) #looking for escape if needed
        if 'escape' in key: #just in case experimenter presses 'escape' on keyboard because they want to quit the experiment
            logging.flush()
            core.quit()

        #previous loop which prevented to quit the experiment
        #for frs in range(int(np.round(11900/prd))): #time frames corresponding to 50 ms
         #   fix_c.draw()
          #  win.flip()

        #current loop which allows to quit the experiment if th experimenter wishes to do so
        while resp == None: #while there is no response
            key = event.getKeys(keyList = ['escape']) #looking for response
            fix_c.draw()
            win.flip()
            if 'escape' in key: #just in case experimenter presses 'escape' on keyboard because they want to quit the experiment
                logging.flush()
                core.quit()
            if RT.getTime() > 5.9: #11.9: #1.9 melody + 4s ITI
                resp = 0 #in this case response is coded as '0'

    #SHORT BREAK
    pausemex = visual.TextStim(win,text = 'Now you have a 2-minute break \n\n You can relax', color = 'gray') #preparing message
    # pausemex = visual.TextStim(win,text = '现在你有两分钟的休息时间', color = 'gray') #preparing message
    pausemex.draw() #presenting message
    win.flip()
    core.wait(4) #4-second break for allowing participant to read the instruction

    ### TRIGGER ###
    ParalData = 4#80 #trigger value resting
    win.callOnFlip(setParallelData, int(ParalData))
    for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
        fix_c.draw()
        win.flip()

    setParallelData(0) #close trigger
    for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
        fix_c.draw()
        win.flip()

    ### TRIGGER ###

    #previous loop which prevented to quit the experiment
    #for frs in range(int(np.round(119900/prd))): #time frames corresponding to 50 ms
     #   fix_c.draw()
      #  win.flip()

    #current loop which allows to quit the experiment if th experimenter wishes to do so
    RT.reset()
    resp = None
    while resp == None: #while there is no response
        key = event.getKeys(keyList = ['escape']) #looking for response
        fix_c.draw()
        win.flip()
        if 'escape' in key: #additional precaution to get out in case experimenter presses 'escape' on keyboard
            logging.flush()
            core.quit()
        if RT.getTime() > break_length2: #120
            resp = 0 #in this case response is coded as '0'


    #RECOGNITION PHASE
    playrec = visual.TextStim(win,text = 'Recognition phase \n\n Now you will listen to 126 melodies. \n\n'
                                         'For each of them, please press ' + str(response_buttons[0]) + ' if the melody is "old"'
                                         '(the melody appeared in the "learning" part) or press ' + str(response_buttons[1]) +
                                         ' if it is "new" (the melody did not appear in the "learning part"). \n\n'
                                         'For each correct answer you will get 10 points\n'
                                         'and for each incorrect answer you will lose 10 points.\n\n'
                                         'Your goal is to get as many points as you can\n\n'
                                         'Good luck!\n\n'
                                         'Press any key to continue', color = 'gray',wrapWidth=2)
    # playrec = visual.TextStim(win,text = '重现阶段 \n\n 现在你将听到126段音乐 \n\n 听到的每一段音乐，请按 ' + str(response_buttons[0]) + ' 如果这段音乐是上一阶段听到的三段里的一段 或者 按 ' + str(response_buttons[1]) + ' 如果这段音乐是你第一次听到 \n\n 请按任意键继续', color = 'gray')
    playrec.draw() #present instruction for recognition
    win.flip()
    event.waitKeys()

    score = 0
    #presentation of stimuli
    #for wavve in range(1,6): #this is just for testing purposes since it loops over only a few trials
    for wavve in range(len(wavezip)): #over melodies for recognition phase
        #displaying the progressive trial number for participants' comfort
        jes = 'trial number ' + str((wavve + 1)) + ' / ' + str(len(wavezip)) #text for the trial number
        # jes = '数量 ' + str((wavve + 1)) + ' / ' + str(len(wavezip)) #text for the trial number
        instrrectr = visual.TextStim(win,text = jes,color = 'gray')
        instrrectr.draw() #presenting trial number
        win.flip()
        core.wait(1) #duration of 1 second
        fix_c.draw() #fixation cross
        win.flip()
        core.wait(0.5) #waiting half second

        #preparing trigger value
        if 'old' in wavezip[wavve][0]: #old melody
            trigval = 5#100 #trigvalue
        elif 'new' in wavezip[wavve][0]: #new melody
            if 'k1' in wavezip[wavve][0]: #in musical key (weaker variation)
                if 't3' in wavezip[wavve][0]: #varied from tone 4
                    trigval = 6#110 #trigvalue
                elif 't4' in wavezip[wavve][0]: #varied from tone 5
                    trigval = 7#120
            elif 'k2' in wavezip[wavve][0]: #out of musical key (stronger variation)
                if 't3' in wavezip[wavve][0]: #varied from tone 4
                    trigval = 8#130
                elif 't4' in wavezip[wavve][0]: #varied from tone 5
                    trigval = 9#140

        ### TRIGGER ###
        nextFlip = win.getFutureFlipTime(clock='ptb') #getting next flip time
        win.callOnFlip(setParallelData, int(trigval))
        ### TRIGGER ###

        #***#win.callOnFlip(print, int(trigger))            #PRINTING TRIGGER (IF YOU WANT TO TEST IT IN YOUR LOCAL COMPUTER)
        wavezip[wavve][1].play(when = nextFlip) #playing sound, exactly at next flip
        event.clearEvents(eventType='keyboard') #making sure that no key are pre-recorded in memory
        RT.reset()
        resp = None

        ### TRIGGER ###
        for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
            fix_c.draw()
            win.flip()

        setParallelData(0)
        for frs in range(int(np.round(50/prd))): #time frames corresponding to 50 ms
            fix_c.draw()
            win.flip()

        ### TRIGGER ###

        while resp == None: #while there is no response
            key = event.getKeys(keyList = [str(response_buttons[0]),str(response_buttons[1]),'escape']) #looking for response (either one of the two keys used for recording participant's response or the escape key in case you need to quit the experiment)
            if len(key) > 0: #if response is given
                rt = RT.getTime() #getting RT
                resp = key[0][0] #getting the actual response (e.g. '1' or '2')
            elif RT.getTime() > 6: #otherwise waiting 6 seconds - maximum waiting time if participant does not reply
                resp = 0 #in this case response is coded as '0'
                rt = RT.getTime() #getting fixed (maximum) RT
        logging.flush()
        acc = ''
        if ((resp == '1') & (trigval==5)) or ((resp == '2') & (trigval>5)):
            acc = '1'
            score += 10
            feedback = visual.TextStim(win, text='Correct! (+10 points)\n\n'
                                                 f'Current score: {score}\n\n'
                                                 '(press a key to to continue)',
                                       color='green')
        else:
            acc = '0'
            score -= 10
            feedback = visual.TextStim(win, text='Incorrect (-10 points)\n\n'
                                        f'Current score: {score}\n\n'
                                        '(press a key to to continue)',
                                       color='red')
        #writing RT, trial ID, subject's response
        lrow = '{};{};{};{};{};{} \n' #new row in the csv file
        lrow = lrow.format(subID[0],wavezip[wavve][0], resp, round(rt*1000),str(trigval),acc) #storing behavioural information
        logfile.write(lrow) #writing on csv

        core.wait(.5)
        feedback.draw()
        win.flip()
        event.waitKeys()
        core.wait(.5) #short waiting time before the next trial # before = 1.5

        if 'escape' in key: #just in case experimenter presses 'escape' on keyboard because they want to quit the experiment
            logging.flush()
            core.quit()

    #final message
    playlear = visual.TextStim(win,text = f'Your final score is {score}\n\n'
                                           'Great work!\n\n', color = 'gray')
    # playlear = visual.TextStim(win,text = '测试结束，请叫医生', color = 'gray')
    playlear.draw()
    win.flip()
    core.wait(4)

    familiarity = visual.TextStim(win,text = 'The melodies you memorized belong to a musical piece\n'
                                           'How familiar are you with it?\n\n'
                                           '1 = I have never heard it before\n'
                                           '2 = I ocassionally heard it\n'
                                           '3 = I sometimes listen to it\n'
                                           '4 = I usually listen to it\n'
                                           '5 = I played it\n'
                                           '6 = I played it in front of an audience\n\n'
                                           'Use the keyboard numbers to provide an answer',
                                           color = 'gray')
    familiarity.draw()
    win.flip()
    fam = event.waitKeys(keyList = ['1','2','3','4','5','6'])

    logging.flush()

    lrow = '{};{};{};{};{};{} \n'.format(subID[0],'familiarity', fam, 'NA','NA','NA') #new row in the csv file
    logfile.write(lrow) #writing on csv
    logfile.close() #closing csv file

    end_text = visual.TextStim(win, text = 'This is the end of the current task.\n\n'
                                           'Thank you for participating!',
                                           color = 'gray')
    end_text.draw()
    win.flip()
    core.wait(2)
    event.waitKeys(keyList=['space'])

####################
