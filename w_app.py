#Add the required library
import Adafruit_DHT             #DHT11 sensor library.
import time                     #Time library, will use to setup the waiting time between the sensor readings.
from rpi_lcd import LCD         #LCD library to display the information.
from datetime import date       #Date library to get date information.
import paho.mqtt.client as mqtt #MQTT protocl Library needed to maintain the connection with Thingboard IoT Platform.
import json                     #json library, will use it to send the information to IoT platform via MQTT protocol.

DHT_sensor = Adafruit_DHT.DHT11                 #Initiate the sensor class.
lcd = LCD()                                     #Initiate the LCD class.
client = mqtt.Client()                          #Initiate the MQTT class.
sensor_data = {'temperature': 0, 'humidity': 0} #Initiate the dictionary variable, we will use it with json function to send the data to Thingboard via MQTT.
DHT_PIN = 17                                    #Rasperberry GPIO pin, where the DHT11 sensor is connected.
THINGSBOARD_HOST = 'thingsboard.cloud'          #Thingboard host address, we will use this in the MQTT connection.
ACCESS_TOKEN = 'AccessTocken Here'           #Secure access token to the dashboard, will pass this information in the MQTT connection.
wait_time = 5                                   #Default waiting time between sensor readings.

def mqtt_con():                     #The MQTT communication protocol function. This function will establish the connection with MQTT broker in Thingboard.
    client.username_pw_set(ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start()
def get_data():                     #This function will return the temperature and Humidity information from the sensor along with the current date.
    humidity, temperature  = Adafruit_DHT.read(DHT_sensor, DHT_PIN)
    today = date.today()
    return humidity, temperature, today
def lcd_disp(temp, hum, today):	    #The purpose of this function is to display the weather information and the current date on the LCD screen.
    lcd.text(f"{today}", 1)
    lcd.text("T "f"{temp} H "f"{hum}", 2)
def log_data(temperature, humidity): #This function will log the information collected from get_data function into ThingBoard dashboard over MQTT protocol using json.
    sensor_data['temperature'] = temperature
    sensor_data['humidity'] = humidity
    client.publish('esp/telemetry',\
                    json.dumps(sensor_data), 1) #The information will be published on esp/telemetry topic.
def waiting(): #This function allows the user to set the waiting time between sensor reading in seconds. The defualt time is 5 second.
    while 1:
        try:
            wait_time = int(input("Please enter the waiting time between the readings in seconds, " \
                                  "default time is 5 seconds: ") or "5") #If no value entered. deafult value '5' will be used.
            return wait_time
        except:
            print("That's not a valid number, please try again")          #If non-integer value entered, the system will ask the user to renter the value.
def run():                                                                #The main function to run the application.
    mqtt_con()
    print('Welcome to the Weather Application\nThe application is running now')
    wait_time = waiting() 
    try:
        while True:
            humidity,temperature, today = get_data()     
            if humidity is not None and temperature is not None:
                lcd_disp(temperature,humidity,today)
                log_data(temperature,humidity)
                print(f'tem= {temperature} Hum= {humidity}')
                time.sleep(int(wait_time))
            else:
                time.sleep(3)                     #If the sensor couldn't generate the weather information, It will wait for 3 seconds and try again.
    except KeyboardInterrupt:
        lcd.clear()
        client.loop_stop()
        client.disconnect()        
run()
