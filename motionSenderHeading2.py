import serial
import serial.tools.list_ports
import struct
import sys
import time
from time import localtime, strftime
import argparse
import tqdm
import os
import swFileGen as sGen
import swFileGenRev as sGenRev
import numpy as np
import PsiMarginal
import random
import pygame
import winsound         # for sound  
from msvcrt import getch
from msvcrt import kbhit
import atexit
import math
import matplotlib.pyplot as plt


# EXPERIMENT DETAILS #
ID = 1 #                        subject ID number, int
freqs =  [1] #            Hz, can be selected on each trial according to a list of randomOrder, see below
directions = ['LEFT','RIGHT'] #  indices of keypresses [0,1]
RESPONSES = 'responseFileHeading'+str(ID)+'.csv' # filename
AXES = ['roll','pitch','yaw','X','Y','Z']  
MAXVELOCITY = [0]*6

###########################
# SUPER VARIABLES
ntrials = 100        #  number of trials in the experiment (or block, if running blocked)
Frequency = 1      # where Frequency is 0.5 Hz or 1.0 Hz
MAXVELOCITY[2] = 2  # maximum yaw vel in deg/s
axis = 3 #                       roll[0] pitch[1] yaw[2] x[3] y[4] z[5]
#rlist = [0,1,2,3,4,5,6,7,8] * int(ntrials/9)















#random.shuffle(rlist)
###########################
#maxANG = 10 # commented out for testing purposes (use smaller angles)
maxANG = 1
numANGs = 6
nHANGLES = (numANGs * 2) -1 # len(HANGLELIST)

HANGLELIST = list(set(np.concatenate([-1+np.logspace(0, math.log10(maxANG+1), numANGs), (-1+np.logspace(0, math.log10(maxANG+1), numANGs))*-1])))

# NOT USED
sneakiness = 7 #                 seconds to spend sneaking home
#####

# JOYSTICK CODE #
pygame.init()
j = pygame.joystick.Joystick(0)
j.init()
print('Initialized Joystick : %s' % j.get_name())

def get():
    out = [0] * 6
    it = 0 #iterator
    pygame.event.pump()

    #Read input from buttons
    response=[]
    while response==[]:
        if kbhit()==True:
            key = ord(getch())
            if key == 27: #ESC
                sys.exit(0)
            else:
                break
        #os.system('cls') 
        #print('Waiting for joystick input...')
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.JOYBUTTONUP:
                #print('BUTTONPRESS')
                winsound.Beep(220,250)
                if event.button == 0:  # left mouse button?
                    #print('LEFT')
                    response=0
                    break
                elif event.button == 2:  # left mouse button?
                    #print('RIGHT')
                    response=1

    return response

    
def getresponse():
    response=get()
    print('USER SELECTED: ' + directions[response])
    return response

os.chdir('C:/Users/mbarnett/Documents/MOOG/software-cs/motionFiles/Heading')

with open(RESPONSES,"a") as f:
        f.write('Study commenced at: ' + strftime("%Y-%m-%d %H:%M:%S", localtime())+'\n')

with open(RESPONSES,"a") as f:
        f.write('ID,'+
                'trial,'+
                'maxvelocity,'+
                'response,'+
                'Frequency\n')

# Used for the main loop    
def main(comName, fileName, frequency):
    #read the file
    bytesToSend = []
    print('Reading file', end='')
    with open(fileName, 'rb') as f:
        while True:
            blen = f.read(4)
            if blen == b'': break
            length = struct.unpack('I', blen)[0]
            data = f.read(length)
            packet = blen + data
            bytesToSend.append(bytearray(packet))
    print(' - Done')
    
    print('Sending packets', flush=True)

    # Actually move the platform:
    with serial.Serial(
        port=comName,
        baudrate=921600,#115200,
        xonxoff=False
        ) as ser:
        timeToPass = time.clock()
        for packet in tqdm.tqdm(bytesToSend):
            while time.clock() < timeToPass:
                pass
            ser.write(packet)

            timeToPass += (1/frequency)

    print('Done')

    return

# Used for the initialization : NO SOUNDS  


def park():
    os.system('cls') 
    print('EXIT: PARKING SYSTEM...')
    main('COM6', 'X_packets.b', 1000) # fully disengage after trial is run
    time.sleep(5)
    
atexit.register(park)

main('COM6', 'X_packets.b', 1000) # disengage
print("Disengaging if necessary...")
time.sleep(7)

main('COM6', 'Z_packets.b', 1000)
print("Engaging: please wait...")
time.sleep(13)

location = 0
slowness = 0.5


# wait for experimenter to hit ENTER to begin
input("Ready to run experiment.")

# main trial loop
for trial in range(0,ntrials-1):
         
    print("Frequency = "+str(Frequency))
    print('Trial %d of %d' % (trial, ntrials))

    MAXVELOCITY = [0]*len(AXES)
   # MAXVELOCITY[axis] = HANGLE # set new stimuli to present
    MAXVELOCITY[4] = 0.1 # maximum 0.25
    MAXVELOCITY[3] = 0.1 # maximum 0.25
    print(MAXVELOCITY[axis])
    print('^MAX VELOCITY (DISPLACEMENT x 2)^')   
    
    sGen.generate(MAXVELOCITY[0],MAXVELOCITY[1],MAXVELOCITY[2],MAXVELOCITY[3],MAXVELOCITY[4],MAXVELOCITY[5],ID,'C',Frequency) # generate smooth displacement and reversal, roll pitch yaw
    sGenRev.generate(-MAXVELOCITY[0],-MAXVELOCITY[1],-MAXVELOCITY[2],-MAXVELOCITY[3],-MAXVELOCITY[4],-MAXVELOCITY[5],ID,'C',1) # generate smooth reversal


    time.sleep(2) # PRE-TRIAL PAUSE
    
    
    ############### IMPORTANT: run trial
    winsound.Beep(440,250)
    time.sleep(0.25)
    main('COM6', 'C_packets.b', 1000)
    ####################################
    items = [0,1]

    print('Waiting for joystick press...')
    winsound.Beep(880,250)
    time.sleep(0.25)
    
    #response=getresponse() # Wait for joystick press
    #
    input("Inputting response (enter)")
    response=1
    #print(response)

    with open(RESPONSES,"a") as f:
        f.write(str(ID)+','+
                str(trial+1)+','+
                str(MAXVELOCITY[2])+','+
                str(response)+','+
                str(Frequency)+
                '\n')
   
    print("\nSneaking home...\n")
    main('COM6', 'CREV_packets.b', 1000 * (1/sneakiness) / Frequency)

    time.sleep(1)

input("\n\nExperiment terminated. Ready to disengage? Press Enter: ")
main('COM6', 'X_packets.b', 1000) # fully disengage after trial is run
print("Disengaging...")
time.sleep(1)
