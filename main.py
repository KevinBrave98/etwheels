import cv2 as cv
import module as m
import time

# Variables
COUNTER = 0
CLOSED_EYES_FRAME = 1

# creating camera object

camera = cv.VideoCapture(0)
camera2 = cv.VideoCapture(1) #need second camera(back)

onStatus = False #wheelchair status
tryActivateStatus = False #try to activate wheelchair status
tryDeactivateStatus = False #try to deactivate wheelchair status
last_blink_time = 0
blink_time_value = 0.8
leftStatus = False;
rightStatus = False;
countdown = 0

while True:
    # getting frame from camera
    ret, frame = camera.read()
    ret2, frame2 = camera2.read()
    # ret2, frame2 = camera2.read()
    if ret == False or ret2 == False:
        break
    # converting frame into Gray image.
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    height, width = grayFrame.shape
    circleCenter = (int(width/2), 50)
    # calling the face detector function
    image, face = m.faceDetector(frame, grayFrame)
    if face is not None:

        # calling landmarks detector function.
        image, PointList = m.faceLandmarkDetector(frame, grayFrame, face, False)

        RightEyePoint = PointList[36:42]
        LeftEyePoint = PointList[42:48]
        leftRatio, topMid, bottomMid = m.blinkDetector(LeftEyePoint)
        rightRatio, rTop, rBottom = m.blinkDetector(RightEyePoint)

        blinkRatio = (leftRatio + rightRatio)/2
        cv.circle(image, circleCenter, (int(blinkRatio*4.3)), m.CHOCOLATE, -1)
        cv.circle(image, circleCenter, (int(blinkRatio*3.2)), m.CYAN, 2)
        cv.circle(image, circleCenter, (int(blinkRatio*2)), m.GREEN, 3)

        if blinkRatio < 5:
            countdown = time.time()
        else:
            if(time.time() - countdown > 3) :
                onStatus = False 
                tryActivateStatus = False
                tryDeactivateStatus = False
                leftStatus = False
                rightStatus = False

        if blinkRatio > 5:
            COUNTER += 1
        else:
            if COUNTER > CLOSED_EYES_FRAME:
                if onStatus == False and rightStatus == True:
                    onStatus = True 
                    tryActivateStatus = False
                    leftStatus = False
                    rightStatus = False
                    COUNTER = 0
                    last_blink_time = 0
                elif onStatus == True and rightStatus == True:
                    onStatus = False 
                    tryDeactivateStatus = False
                    leftStatus = False
                    rightStatus = False
                    COUNTER = 0
                    last_blink_time = 0
                else:
                    COUNTER = 0
                    if onStatus == False:
                        if time.time() - last_blink_time < blink_time_value and time.time() - last_blink_time > 0.4:
                            if tryActivateStatus == True:
                                tryActivateStatus = False
                                leftStatus = False
                                rightStatus = False
                            else:
                                tryActivateStatus = True;
                                last_blink_time = 0;
                                # last_blink_time = time.time()
                        else:
                            last_blink_time = time.time()
                    else:
                        if time.time() - last_blink_time < blink_time_value and time.time() - last_blink_time > 0.4:
                            if tryDeactivateStatus == True:
                                tryDeactivateStatus = False
                                leftStatus = False
                                rightStatus = False
                            else:
                                tryDeactivateStatus = True;
                                last_blink_time = 0;
                                # last_blink_time = time.time()
                        else:
                            last_blink_time = time.time()

        if tryActivateStatus == True:
            cv.putText(image, f'Start Wheelchair?', (230, 70), m.fonts, 1, m.BLUE, 2)

        if tryDeactivateStatus == True:
            cv.putText(image, f'Stop Wheelchair?', (230, 70), m.fonts, 1, m.BLUE, 2)

        if onStatus == False:   
            cv.putText(image, f'Wheelchair Stopped', (230, 40), m.fonts, 1, m.ORANGE, 2)

        if onStatus == True:
            cv.putText(image, f'Wheelchair is Moving', (230, 40), m.fonts, 1, m.ORANGE, 2)

        mask, pos = m.EyeTracking(image, grayFrame, RightEyePoint)
        maskleft, leftPos = m.EyeTracking(image, grayFrame, LeftEyePoint)
        
        if pos == "Left" or leftPos == "Left":
            cv.putText(image, f'Looking Left', (230, 120), m.fonts, 1, m.GOLDEN, 2)
        elif pos == "Right" or leftPos == "Right":
            cv.putText(image, f'Looking Right', (230, 120), m.fonts, 1, m.GOLDEN, 2)
        else:
            cv.putText(image, f'Looking Straight', (230, 120), m.fonts, 1, m.GOLDEN, 2)

        if onStatus == True:
            if (pos == "Left" or leftPos == "Left") and tryDeactivateStatus == False:
                cv.putText(image, f'Turning Left', (230, 460), m.fonts, 1, m.GOLDEN, 2)
            elif (pos == "Right" or leftPos == "Right") and tryDeactivateStatus == False:
                cv.putText(image, f'Turning Right', (230, 460), m.fonts, 1, m.GOLDEN, 2)
            else:
                cv.putText(image, f'Moving Forward', (230, 460), m.fonts, 1, m.GOLDEN, 2)

        if tryActivateStatus == True:
            if pos == "Left" or leftPos == "Left":
                leftStatus = True;
            if leftStatus == True:
                if pos == "Right" or leftPos =="Right":
                    rightStatus = True;
            if rightStatus == True:
                if pos == "Left" or leftPos =="Left":
                    rightStatus = False;
        
        if tryDeactivateStatus == True:
            if pos == "Left" or leftPos == "Left":
                leftStatus = True;
            if leftStatus == True:
                if pos == "Right" or leftPos =="Right":
                    rightStatus = True;
            if rightStatus == True:
                if pos == "Left" or leftPos =="Left":
                    rightStatus = False;
        # showing the frame on the screen
        cv.putText(frame2, f'REAR VIEW', (230, 50), m.fonts, 1, m.RED, 2)
        cv.imshow('Frame', image)
        cv.imshow('Frame 2', frame2)
    else:
        cv.putText(image, f'FACE NOT DETECTED', (230, 50), m.fonts, 1, m.RED, 2)
        cv.putText(image, f'WHEELCHAIR STOPPED', (230, 100), m.fonts, 1, m.RED, 2)
        cv.putText(frame2, f'REAR VIEW', (230, 50), m.fonts, 1, m.RED, 2)
        cv.imshow('Frame', image)
        cv.imshow('Frame 2', frame2)
        tryActivateStatus = False
        tryDeactivateStatus = False
        leftStatus = False
        rightStatus = False
        onStatus = False

    key = cv.waitKey(1)

    # if q is pressed on keyboard: quit
    if key == ord('q'):
        break
# closing the camera
camera.release()
# Recoder.release()
# closing  all the windows
cv.destroyAllWindows()
