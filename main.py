import pycom
import machine
from machine import Timer
import time
import _thread

counter = 0

# 10 000 imp/kWh -> 166,667 imp/kWh per min -> 2.778 imp/kWh per sec

# Timer for sending data to pybytes, should be periodicly sent depending on the interval of the power indicator
class Data_Interupt:

    def __init__(self):
        self.seconds = 0
        self.led = 1
        self.__alarm = Timer.Alarm(self._seconds_handler, 60, periodic=True)
        self.__alarm2 = Timer.Alarm(self._led_handler, 0.5, periodic=True)

    def _seconds_handler(self, alarm):
        global counter
        kWh = self._calculate_power()
        self.seconds += 10
        print("kWh: " + str(kWh))
        print("%02d seconds have passed" % self.seconds)
        pybytes.send_signal(0, kWh)
        counter = 0
    
    def _led_handler(self, alarm):
        dac = machine.DAC('P22')        # create a DAC object
        self.led *= -1 
        dac.write(self.led)
       # print("led")

    def _calculate_power(self):
        global counter
        total_imp = counter * 60
        total_imp = total_imp / 10000
        return total_imp

send_data = Data_Interupt()


# function for updating a counter each time the power indicator lights up, should be reset each interval
def track_light():
    adc = machine.ADC()             # create an ADC object
    apin = adc.channel(pin='P16') 
    global counter
    light = False


    while True:
        val = apin()    
        val= val/400
        val= val/10

        if val >= 0.5 and light == False:
            print("Light")
            counter += 1
            print(str(val))
            print(str(light))
            print("")
            light = True

        elif val < 0.5 and light == True:
            print("Dark")
            print(str(val))
            print(str(light))
            print("")
            light = False


# currently only used to light the LED depending on the photon sensors values.
def run_loop():
    dac = machine.DAC('P22')        # create a DAC object
    adc = machine.ADC()             # create an ADC object
    apin = adc.channel(pin='P16') 
    global counter

    while True:
        time.sleep(1)
        val = apin()
        val= val/400
        val= val/10
        dac.write(val)
        print(str(counter))


    # pybytes.send_signal(1, val)
    # time.sleep(10)



_thread.start_new_thread(track_light, ())
#_thread.start_new_thread(run_loop, ())
