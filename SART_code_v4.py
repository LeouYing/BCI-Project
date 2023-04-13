""" Sustained Attention to Response Task (SART)

Author: Cary Stothart (cary.stothart@gmail.com)
Date: 05/11/2015
Version: 2.0
Tested on StandalonePsychoPy-1.82.01-win32

################################# DESCRIPTION #################################

This module contains the standard SART task as detailed by Robertson et al. 
(1997). 

This module is modified by CruX 2023 Team 6 to adapt to our own distraction experiment.
We will overwrite some parts of the code without explicit markings.

This code is for NUMERICAL STIMULATION
    CB CONDITION 1 USES THIS IN STAGE 1
    CB CONDITION 2 USES THIS IN STAGE 3

The modifications made are noted here as well on github:
    Collected participant's phone usage in hours [part_info_gui()]
    Added counterbalancing condition: 
        1: stage 1 uses numStim and stage 3 uses alphaStim
        2: stage 1 uses alphaStim and stage 3 uses numStim
    Reduced the number of blocks to 6 [sart()]
    Changed the number of repetitions of all 9 digits within each block to be 7 [sart()]
    Reduced the circle and X stimuli down just to the + stimulus with smaller font [sart_trial()]
    Got rid of font size as a variable [sart_block()]
    Randomize 3 blocks excluding block 1 to be distraction blocks [sart()]
        of which randomize 3 trials to play distraction sound concurrently [sart_block()]
    Added two T/F columns to indicate whether the current block or trial is distraction or not [sart_block(), sart_trial()]
    
The following task attributes can be easily modified (see the sart()
function documentation below for details):
    
1) Number of blocks (default is 1)
2) Number of font size by number repetitions per trial (default is 1)
3) Target number (default is 3)
4) The presentation order of the numbers. Specifically, the
   numbers can be presented randomly or in a fixed fashion. (default is random)
5) Whether or not practice trials should be presented at the beginning of the 
   task.
   
How to use:

1. Install PsychoPy if you haven't already.
2. Load this file and run it using PsychoPy. Participants will be run on the 
   classic SART task (Robertson et al, 1997) unless one of the sart()
   function parameters is changed.

Reference:

Robertson, H., Manly, T., Andrade, J.,  Baddeley, B. T., & Yiend, J. (1997). 
'Oops!': Performance correlates of everyday attentional failures in traumatic 
brain injured and normal subjects. Neuropsychologia, 35(6), 747-758.

################################## FUNCTIONS ##################################

Self-Contained Functions (Argument=Default Value):

sart(monitor="testMonitor", blocks=1, reps=5, omitNum=3, practice=True, 
     path="", fixed=False)
     
monitor......The monitor to be used for the task.
blocks.......The number of blocks to be presented --> 6 blocks
reps.........The number of repetitions to be presented per block.  Each
             repetition equals 9 trials (1 font size X 9 numbers). --> 7 repetitions
omitNum......The number participants should withhold pressing a key on. --> 3
practice.....If the task should display 18 practice trials that contain 
             feedback on accuracy. --> no
path.........The directory in which the output file will be placed. Defaults
             to the directory in which the task is placed.
fixed........Whether or not the numbers should be presented in a fixed
             instead of random order (e.g., 1, 2, 3, 4, 5, 6, 7, 8 ,9,
             1, 2, 3, 4, 5, 6, 7, 8, 9...).     
             
################################### CITATION ##################################

How to cite this software in APA:

Stothart, C. (2015). Python SART (Version 2) [software]. Retrieved from 
https://github.com/cstothart/python-cog-tasks.  

For a DOI and other citation information, please see 
http://figshare.com/authors/Cary_Stothart/394277
     
################################## COPYRIGHT ##################################

The MIT License (MIT)

Copyright (c) 2015 Cary Robert Stothart

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.     

"""

import time
import copy
import random
import sys

from psychopy import visual, core, data, event, gui
from psychopy.sound import Sound

def sart(monitor="testMonitor", blocks=6, reps=7, omitNum=3, practice=True, 
         path="", fixed=False): 
    """ SART Task.
    
    monitor......The monitor to be used for the task.
    blocks.......The number of blocks to be presented.
    reps.........The number of repetitions to be presented per block.  Each
                 repetition equals 9 trials (1 font size X 9 numbers).
    omitNum......The number participants should withold pressing a key on.
    practice.....If the task should display 18 practice trials that contain 
                 feedback on accuracy.
    path.........The directory in which the output file will be placed. Defaults
                 to the directory in which the task is placed.
    fixed........Whether or not the numbers should be presented in a fixed
                 instead of random order (e.g., 1, 2, 3, 4, 5, 6, 7, 8 ,9,
                 1, 2, 3, 4, 5, 6, 7, 8, 9...).
    """
    partInfo = part_info_gui() # show info page
    mainResultList = []
    fileName = "SART_" + str(partInfo[0]) + ".tsv"
    outFile = open(path + fileName, "w") # output file path
    win = visual.Window(fullscr=False, color="black", units='cm',
                        monitor=monitor) 
    distBlocks = random.sample(range(2,7), 3) ## Randomize distraction blocks (cannot be block 1)
    print(distBlocks)
    sart_init_inst(win, omitNum) # show instruction message
    if practice == True: # true in our experiment
        sart_prac_inst(win, omitNum)
        mainResultList.extend(sart_block(win, fb=True, omitNum=omitNum, 
                              reps=1, bNum=0, fixed=fixed, dist=False, distBlocks=distBlocks)) ## dist = false
    sart_act_task_inst(win) # shows instruction message to start the task
    for block in range(1, blocks + 1):
        ## Randomize distraction blocks
        # if (block == 2) or (block == 4) or (block == 6):
        if (block == distBlocks[0]) or (block == distBlocks[1]) or (block == distBlocks[2]):
            dist = True 
        else:
            dist = False
        mainResultList.extend(sart_block(win, fb=False, omitNum=omitNum,
                              reps=reps, bNum=block, fixed=fixed, dist=dist, distBlocks=distBlocks)) # pass in dist
        if (blocks > 1) and (block != blocks):
            sart_break_inst(win) # shows take-a-break message
    evalInfo = self_eval_gui() ## Self evaluation form at the end
    outFile.write("part_num\tpart_gender\tpart_age\t" +
                  "part_hours\texp_initials\tCB_condition\tawareness" +
                  "\tattention\tblock_num\tdist_block\ttrial_num\tdist_trial\t" +
                  "number\tomit_num\tresp_acc\tresp_rt_s\ttrial_start_time_s" +
                  "\ttrial_end_time_s\tmean_trial_time_s\ttiming_function\n") ## Added indicator columns whether the block and trial is distraction or not
    """
    participant number, gender, age, hours on phone, experimenter initials, 
    condition block number (1/2), participant awareness (1-6), 
    participant attention (1-6), distraction block (T/F), trial number (1-63), 
    distraction trial (T/F), omit number (3), response accuracy, 
    response time (s), trial start time (s), trial end time (s), 
    mean trial time (s), timing function
    """
    
    for line in mainResultList:
        for item in partInfo:
            outFile.write(str(item) + "\t")
        for number in evalInfo:
            outFile.write(str(number) + "\t") ## Add self eval info
        for col in line:
            outFile.write(str(col) + "\t")
        outFile.write("time.perf_counter()\n")
    outFile.close()
    
def part_info_gui():
    info = gui.Dlg(title='SART')
    info.addText('Participant Info')
    info.addField('Part. Number: ')
    info.addField('Part. Gender: ', 
                  choices=["Please Select", "Male", "Female", "Other"])
    info.addField('Part. Age:  ')
    """
    info.addField('Part. Year in School: ', 
                  choices=["Please Select", "Freshman", "Sophmore", "Junior", 
                           "Senior", "1st Year Graduate Student", 
                           "2nd Year Graduate Student", 
                           "3rd Year Graduate Student", 
                           "4th Year Graduate Student",
                           "5th Year Graduate Student", 
                           "6th Year Graduate Student"])
    """
    info.addField('How many hours do you spend on your phone daily?', 
                  choices=["Please select", "0-2", "2-4", "4-6", ">6"]) ## changed corrected vision to phone usage
    info.addText('Experimenter Info')
    info.addField('Initials:  ')
    info.addField('CB condition:  ') ## Counterbalancing condition
    info.show()
    if info.OK:
        infoData = info.data
    else:
        sys.exit()
    return infoData
    
def sart_init_inst(win, omitNum):
    inst = visual.TextStim(win, text=("In this task, a series of numbers will" +
                                      " be presented to you.  For every" +
                                      " number that appears except for the" +
                                      " number " + str(omitNum) + ", you are" +
                                      " to press the space bar as quickly as" +
                                      " you can.  That is, if you see any" +
                                      " number but the number " +
                                      str(omitNum) + ", press the space" +
                                      " bar.  If you see the number " +
                                      str(omitNum) + ", do not press the" +
                                      " space bar or any other key.\n\n" +
                                      "Please give equal importance to both" +
                                      " accuracy and speed while doing this" + 
                                      " task.\n\nPress the b key when you" +
                                      " are ready to start."), 
                           color="white", height=0.7, pos=(0, 0))
    event.clearEvents()
    while 'b' not in event.getKeys():
        inst.draw()
        win.flip()
        
def sart_prac_inst(win, omitNum):
    inst = visual.TextStim(win, text=("We will now do some practice trials " +
                                      "to familiarize you with the task.\n" +
                                      "\nRemember, press the space bar when" +
                                      " you see any number except for the " +
                                      " number " + str(omitNum) + ".\n\n" +
                                      "Press the b key to start the " +
                                      "practice."), 
                           color="white", height=0.7, pos=(0, 0))
    event.clearEvents()
    while 'b' not in event.getKeys():
        inst.draw()
        win.flip()
        
def sart_act_task_inst(win):
    inst = visual.TextStim(win, text=("We will start the actual task.\n" +
                                      "\nRemember, give equal importance to" +
                                      " both accuracy and speed while doing" +
                                      " this task.\n\nPress the b key to " +
                                      "start the actual task."), 
                           color="white", height=0.7, pos=(0, 0))
    event.clearEvents()
    while 'b' not in event.getKeys():
        inst.draw()
        win.flip()
        
def sart_break_inst(win):
        inst = visual.TextStim(win, text=("You will now have a 20 second " +
                                          "break.  Please remain in your " +
                                          "seat during the break."),
                               color="white", height=0.7, pos=(0, 0))
        nbInst = visual.TextStim(win, text=("You will now do a new block of" +
                                            " trials.\n\nPress the b key " +
                                            "bar to begin."),
                                 color="white", height=0.7, pos=(0, 0))
        startTime = time.perf_counter()
        while 1:
            eTime = time.perf_counter() - startTime
            inst.draw()
            win.flip()
            if eTime > 20:
                break
        event.clearEvents()
        while 'b' not in event.getKeys():
            nbInst.draw()
            win.flip()

## play distraction sound
def playSound():
    Dist = Sound('distraction.wav')
    Dist.play()

def sart_block(win, fb, omitNum, reps, bNum, fixed, dist, distBlocks):
    mouse = event.Mouse(visible=0)
    fix = visual.TextStim(win, text="+", height=1.5, color="white", pos=(0, 0)) ## sub circle and x stim for + stim
    numStim = visual.TextStim(win, font="Arial", color="white", pos=(0, 0))
    correctStim = visual.TextStim(win, text="CORRECT", color="green", 
                                  font="Arial", pos=(0, 0))
    incorrectStim = visual.TextStim(win, text="INCORRECT", color="red",
                                    font="Arial", pos=(0, 0))                                 
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    if fb == True:
        fontSizes=[1.20]
    else:
        fontSizes=[1.20] # what was this originally? doesn't matter but we can just get rid of this and just define fontSizes=1.20
    
    list= data.createFactorialTrialList({"number" : numbers,
                                         "fontSize" : fontSizes,}) # can get rid of fontSize
                                         
    # start - Don't need this -----
    seqList = []
    for i in range(len(fontSizes)):
        for number in numbers:
            random.shuffle(list)
            for trial in list:
                if trial["number"] == number and trial not in seqList:
                    seqList.append(trial)
                    break
    # end
    
    if fixed == True:
        trials = data.TrialHandler(seqList, nReps=reps, method='sequential')
    else:
        trials = data.TrialHandler(list, nReps=reps, method='random')    # always use this

    clock = core.Clock()
    tNum = 0
    resultList = []
    startTime = time.perf_counter()
    
    distTrials = random.sample(range(1, 63), 3)    ## Randomize trials with distractions
    print(distTrials)
    
    for trial in trials:
        tNum += 1
        
        ## play distraction sound if the block is a distraction block and trials are distraction trials
        """
        if (dist == True) and ((tNum == 2) or (tNum == 20) or (tNum == 30)):
            playSound()
            resultList.append(sart_trial(win, fb, omitNum, fix,
                              numStim, correctStim, incorrectStim, clock, 
                              trials.thisTrial['fontSize'], 
                              trials.thisTrial['number'], tNum, bNum, mouse, True, distBlocks))
        else:
            resultList.append(sart_trial(win, fb, omitNum, fix,
                              numStim, correctStim, incorrectStim, clock, 
                              trials.thisTrial['fontSize'], 
                              trials.thisTrial['number'], tNum, bNum, mouse, False, distBlocks))
        """
        ## Randomize
        if (dist == True) and ((tNum == distTrials[0]) or (tNum == distTrials[1]) or (tNum == distTrials[2])):
            playSound()
            resultList.append(sart_trial(win, fb, omitNum, fix,
                              numStim, correctStim, incorrectStim, clock, 
                              trials.thisTrial['fontSize'], 
                              trials.thisTrial['number'], tNum, bNum, mouse, True, distBlocks))
        else:
            resultList.append(sart_trial(win, fb, omitNum, fix,
                              numStim, correctStim, incorrectStim, clock, 
                              trials.thisTrial['fontSize'], 
                              trials.thisTrial['number'], tNum, bNum, mouse, False, distBlocks))
        
    endTime = time.perf_counter()
    totalTime = endTime - startTime # reaction time
    
    for row in resultList:
        row.append(totalTime/tNum) # average time per trial in a block, how is 2.05 and 1.15 derived in the original paper? what's the purpose?
    print ("\n\n#### Block " + str(bNum) + " ####\nDes. Time Per P Trial: " +
           str(2.05*1000) + " ms\nDes. Time Per Non-P Trial: " +
           str(1.15*1000) + " ms\nActual Time Per Trial: " +
           str((totalTime/tNum)*1000) + " ms\n\n")
    return resultList

def sart_trial(win, fb, omitNum, fix, numStim, correctStim, 
               incorrectStim, clock, fontSize, number, tNum, bNum, mouse, dist, distBlocks):
    startTime = time.perf_counter() 
    mouse.setVisible(0)
    respRt = "NA"
    numStim.setHeight(fontSize)
    numStim.setText(number)
    numStim.draw() # show number
    event.clearEvents()
    clock.reset() 
    stimStartTime = time.perf_counter() # start time of the stimulus
    win.flip()
    fix.draw() ## only show + fixation point
    waitTime = .25 - (time.perf_counter() - stimStartTime) 
    core.wait(waitTime, hogCPUperiod=waitTime)
    maskStartTime = time.perf_counter()
    win.flip()
    waitTime = .90 - (time.perf_counter() - maskStartTime)
    core.wait(waitTime, hogCPUperiod=waitTime)
    win.flip()
    allKeys = event.getKeys(timeStamped=clock)
    # Get response
    if len(allKeys) != 0:
        respRt = allKeys[0][1]
    if len(allKeys) == 0:
        if omitNum == number:
            respAcc = 1
        else:
            respAcc = 0
    else:
        if omitNum == number:
            respAcc = 0
        elif omitNum == 'q':
            sys.exit()
        else:
            respAcc = 1 
    if fb == True:
        if respAcc == 0: 
            incorrectStim.draw()
        else:
            correctStim.draw()
        stimStartTime = time.perf_counter()
        win.flip()
        waitTime = .90 - (time.perf_counter() - stimStartTime) 
        core.wait(waitTime, hogCPUperiod=waitTime)
        win.flip()
    endTime = time.perf_counter()
    totalTime = endTime - startTime
    
    ## Indicate whether the block and the trial is distraction
    if (bNum == distBlocks[0]) or (bNum == distBlocks[1]) or (bNum == distBlocks[2]):
        distB = True
    else:
        distB = False
    return [str(bNum), str(distB), str(tNum), str(dist), str(number), str(omitNum), str(respAcc),
            str(respRt), str(startTime), str(endTime)]

## Self-evaluation GUI
def self_eval_gui():
    info = gui.Dlg(title='Self evaluation')
    info.addText('Please rate yourself on these questions by clicking on a number below: ')
    info.addField('How aware were you of where your attention was during this block of trials? 1 <- not aware, very aware -> 6',
                    choices=["Please Select", "1", "2", "3", "4", "5", "6"])
    info.addField('Where was your attention focused during this block of trials? 1 <- off-task, on-task -> 6', 
                  choices=["Please Select", "1", "2", "3", "4", "5", "6"])
    info.show()
    if info.OK:
        infoData = info.data
    else:
        sys.exit()
    return infoData

def main():
    sart()

if __name__ == "__main__":
    main()
    
