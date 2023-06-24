from tkinter import *
import time
import serial
import threading
import continuous_threading
import random
import os


ser1 = serial.Serial('COM8',19200) #white cable
ser2 = serial.Serial('COM9',19200) #black cable
val1 = 0

index1 = 0
data1 = 0
index2 = 0
data2 = 0

counter = 0
calib_value = 0
lower = 0
upper = 0
newvalue = 0
def readserial():
    
    global counter
    global calib_value
    global lower
    global upper
    global newvalue

    index1 = ser1.readline().decode('utf-8')
    data1 = float(index1.rstrip())
    #print ("Ground", data1)
    index2 = ser2.readline().decode('utf-8')
    data2 = float(index2.rstrip())
    #print ("Controller", data2)
    

    if (counter == 0):
        counter = counter + 1
    elif (counter == 1):
        counter = counter + 1
        calib_value = data1 - data2
        #print("Calib value", calib_value)

    lower = calib_value - 15
    upper = calib_value + 15
    oldvalue = data1-data2
        
    if ((data1-data2) > calib_value):
        #print("Up")
        # map data difference to value between 0 and 200      
        newvalue = ((oldvalue - calib_value) * 350)/(upper - calib_value)
        #main.after(FRAMERATE, birdUp)
        birdUp()
        #print("New value", newvalue)

    elif ((data1-data2) <= calib_value):
        #print("Down")
        #map data diff to value between 0 and 200        
        newvalue = 350 - ((oldvalue - lower) * 350)/(calib_value - lower)
        #main.after(FRAMERATE, birdDown)
        birdDown()
        #print("New value", newvalue)

    #print("Nothing true: ", data1, "  ", data2)


t1 = continuous_threading.PeriodicThread(0.05, readserial)
t1.start()


FRAMERATE = 30
SCORE = -1

def center(toplevel):
	toplevel.update_idletasks()
	w = toplevel.winfo_screenwidth()
	h = toplevel.winfo_screenheight()
	size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
	x = w/2 - size[0]/2
	y = h/2 - size[1]/2 - 35
	toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))
	
main = Tk()
main.resizable(width = False, height = False)
main.title("Flappy Bird")
main.geometry('550x700')

center(main)

BIRD_Y = 350
PIPE_X = 550
PIPE_HOLE = 0
NOW_PAUSE = False

BEST_SCORE = 0

if os.path.isfile("data.dat"):
	scoreFile = open('data.dat')
	BEST_SCORE = int(scoreFile.read())
	scoreFile.close()
else:
	scoreFile = open('data.dat', 'w')
	scoreFile.write(str(BEST_SCORE))
	scoreFile.close()

w = Canvas(main, width = 550, height = 700, background = "#4EC0CA", bd=0, highlightthickness=0)
w.pack()

birdImg = PhotoImage(file="images/bird.gif")
bird = w.create_image(100, BIRD_Y, image=birdImg)

up_count = 0
endRectangle = endBest = endScore = None

pipeUp = w.create_rectangle(PIPE_X, 0, PIPE_X + 100, PIPE_HOLE, fill="#74BF2E", outline="#74BF2E")
pipeDown = w.create_rectangle(PIPE_X, PIPE_HOLE + 200, PIPE_X + 100, 700, fill="#74BF2E", outline="#74BF2E")
score_w = w.create_text(15, 45, text="0", font='Impact 60', fill='#ffffff', anchor=W)


def generatePipeHole():
	global PIPE_HOLE
	global SCORE
	global FRAMERATE
	SCORE += 1
	w.itemconfig(score_w, text=str(SCORE))
	PIPE_HOLE = random.randint(50, 500)
	if SCORE + 1 % 7 == 0 and SCORE != 0: 
		FRAMERATE-=1
	#print("Score: " + str(SCORE))

generatePipeHole()

def birdUp():
    global BIRD_Y
    global up_count
    global NOW_PAUSE
    global newvalue
    
    BIRD_Y = 350 - int(newvalue)
    #print(BIRD_Y)
    if BIRD_Y <= 0: BIRD_Y = 0
    w.coords(bird, 100, BIRD_Y)
    #if NOW_PAUSE == False: main.after(FRAMERATE,birdUp)
    #if NOW_PAUSE == False: 
        #main.after(FRAMERATE, birdUp)
		
		
		
		#if up_count < 5:
		#	up_count += 1
		#	main.after(FRAMERATE, birdUp)
			
		#else: up_count = 0
    #else:
        #restartGame()


def birdDown():
    global BIRD_Y
    global NOW_PAUSE
    global newvalue
    
    BIRD_Y = 350 + int(newvalue)
    #print(BIRD_Y)
    if BIRD_Y >= 700: BIRD_Y = 700
    w.coords(bird, 100, BIRD_Y)
    #if NOW_PAUSE == False: main.after(FRAMERATE,birdDown)



def pipesMotion():
	global PIPE_X
	global PIPE_HOLE
	global NOW_PAUSE

	PIPE_X -= 5
	w.coords(pipeUp, PIPE_X, 0, PIPE_X + 100, PIPE_HOLE)
	w.coords(pipeDown, PIPE_X, PIPE_HOLE + 200, PIPE_X + 100, 700)
	
	if PIPE_X < -100: 
		PIPE_X = 550
		generatePipeHole()
	
	if NOW_PAUSE == False: main.after(FRAMERATE, pipesMotion)

def engGameScreen():
    global endRectangle
    global endScore
    global endBest

    endRectangle = w.create_rectangle(0, 0, 550, 700, fill='#4EC0CA')
    endScore = w.create_text(15, 200, text="Your score: " + str(SCORE), font='Impact 50', fill='#ffffff', anchor=W)
    endBest = w.create_text(15, 280, text="Best score: " + str(BEST_SCORE), font='Impact 50', fill='#ffffff', anchor=W)

def detectCollision():
	global NOW_PAUSE
	global BEST_SCORE

	if (PIPE_X < 150 and PIPE_X + 100 >= 55) and (BIRD_Y < PIPE_HOLE + 45 or BIRD_Y > PIPE_HOLE + 175):
		#print("Collision")
		NOW_PAUSE = True
		if SCORE > BEST_SCORE:
			BEST_SCORE = SCORE
			scoreFile = open('data.dat', 'w')
			scoreFile.write(str(BEST_SCORE))
			scoreFile.close()
		#print("Pause")
		engGameScreen()
	if NOW_PAUSE == False: main.after(FRAMERATE, detectCollision)

def restartGame(event = None):
    global PIPE_X
    global BIRD_Y
    global SCORE
    global NOW_PAUSE
    global FRAMERATE
    
    BIRD_Y = 350
    PIPE_X = 550
    SCORE = -1
    FRAMERATE = 30
    NOW_PAUSE = False
    
    global counter
    
    counter = 0
        
    w.delete(endScore)
    w.delete(endRectangle)
    w.delete(endBest)
    generatePipeHole()
    #main.after(FRAMERATE, birdDown)
    main.after(FRAMERATE, pipesMotion)
    main.after(FRAMERATE, detectCollision)

# main.after(FRAMERATE, birdUp)	
#main.after(FRAMERATE, birdDown)
main.after(FRAMERATE, pipesMotion)
main.after(FRAMERATE, detectCollision)
main.bind("<space>", restartGame)

#line = ser.readline().rstrip() 
main.mainloop()
