import time
# import datalogger
import math
import board
import adafruit_hcsr04
from adafruit_circuitplayground import cp

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.A2, echo_pin=board.A1)
pixels = cp.pixels
pixels.brightness = 0.3
pixels.show()
pixels.fill((0, 0, 0))

# ------------------------------------------------------------------------------- #
# Other functions
# ------------------------------------------------------------------------------- #
def alarm():
    while not cp.button_b:
        cp.play_tone(262, 1)
        pixels.fill((255, 0, 0))
        time.sleep(0.1)
        pixels.fill((0, 0, 255))
        time.sleep(0.1)
    pixels.fill((0, 0, 0))

def sentry_check():
    # print("sentry check")
    x, y, z = cp.acceleration
    time.sleep(0.05)
    acc_x = abs(x/9.8)
    acc_y = abs(y/9.8)
    acc_z = abs(z/9.8)
    # print("acceleration = " + str(acc_x) + "," + str(acc_y) + "," + str(acc_z))
    temperature = cp.temperature
    # print("temperature = " + str(temperature) + " C")

    sentry = False

    # check if the trash can is shaked
    if cp.shake(shake_threshold=20):
        # this condition is due to critter
        print("Critter detected")
        print("acceleration = " + str(acc_x) + "," + str(acc_y) + "," + str(acc_z))
        sentry = True

    # check if the trash can is falling down
    # elif (acc_x > 0.5 and acc_x < 1) or (acc_y > 0.5 and acc_y < 1) and (acc_z > 0.7 and acc_z < 1.5):
        # this means the trash can is probably falling down
    #    print("The trash can is falling down...")
    #    print("acceleration = " + str(acc_x) + "," + str(acc_y) + "," + str(acc_z))
    #    sentry = True

    # check if ultrasonic sensor is still connected
    test = getTrashLevel()
    # check 3 more times
    counter = 0
    while counter < 3 and math.isnan(test):
        test = getTrashLevel()
        time.sleep(0.1)
        counter += 1
    if math.isnan(test):
        print("Ultrasonic sensor is not working anymore!!!!")
        sentry = True

    # check if the trash can is on fire
    if temperature > 48:  # checks if temp is 48+(celcius(degrees) of fire)
        print('the can is on fire')
        print("temperature = " + str(temperature) + " C")
        sentry = True

    #if cp.loud_sound(sound_threshold=250):
    #    print('animal attack')
    #    sentry = True

    if sentry:
        alarm()

def getTrashLevel():
    try:
        # print((sonar.distance,))
        return sonar.distance
    except RuntimeError:
        print("Retrying!")
        return float('nan')
    time.sleep(0.1)

def displayLights(level):
    pixels.fill((0,0,0))
    if level < red:
        pixels[0] = (255, 0, 0)
        pixels[1] = (255, 0, 0)
        pixels[2] = (255, 0, 0)
        pixels[3] = (255, 0, 0)
        pixels[4] = (255, 0, 0)
    elif level > red and level < yellow:
        pixels[0] = (255, 255, 0)
        pixels[1] = (255, 255, 0)
        pixels[2] = (255, 255, 0)
    else:
        pixels[0] = (0, 255, 0)

    # pixels.fill((0,0,0))
    return True



def lightsOFF():
    print("lights OFF")
    pixels.fill((0,0,0))
    return False

# --------------------------------------------------------------------------- #
#       MAIN FOREVER LOOP
# ---------------------------------------------------------------------------#
timerVal = 0.5
tm = time.monotonic()
sentryTime = time.monotonic()

fullheight = 100
red = 20.0
yellow = 40.0

LED = False
light_time = time.monotonic()
while True:
    monotonic = time.monotonic()
    # print("tm = " + str(tm) + "  monotonic = " + str(monotonic))
    if cp.switch:   # this means the CPX is in testing mode or movement, installation etc.
                    # during this time no need to check sentry mode
                    # also during this time run the loop more freqently so people can test
        timerVal = 2
        if (monotonic - tm) >= timerVal:
            tm = time.monotonic()
            trashLevel = getTrashLevel()
            if not math.isnan(trashLevel):
                print("checking trash level: testing = " + str(trashLevel))
                LED = displayLights(trashLevel)
                light_time = time.monotonic()


    else:           # this means CPX is in actual service mode
                    # sentry mode is now enabled and timer value is increased to 30 sec
        timerVal = 30
        if (monotonic - sentryTime) >= 0.5:
            # print("sentry check")
            sentry_check()
            sentryTime = time.monotonic()

        if (monotonic - tm) > timerVal:
            tm = time.monotonic()
            trashLevel = getTrashLevel()
            if not math.isnan(trashLevel):
                print("checking trash level: service = " + str(trashLevel))
                LED = displayLights(trashLevel)
                light_time = time.monotonic()

    if cp.button_a:
        fullheight = getTrashLevel()
        red = fullheight * 0.2
        yellow = fullheight * 0.4
        cp.play_tone(292, 1)

    if LED and (monotonic - light_time) > 0.5 :
        # print("light time: " + str(monotonic - light_time) + " And LED = " + str(LED))
        LED = lightsOFF()
        light_time = time.monotonic()

    time.sleep(0.05)


