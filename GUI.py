import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
import socket
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition, SlideTransition
import threading
import time

class MyLabel(Label):
    def on_size(self,*args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,1,1,1)
            Rectangle(pos = self.pos, size = self.size)

class MyLabel2(Label):
    def on_size(self,*args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1,0,0,1)
            Rectangle(pos = self.pos, size = self.size)

class MyGrid2(GridLayout):
    def __init__(self, **kwargs):

        super(MyGrid2, self).__init__(**kwargs)
        self.cols = 1
        self.Title = MyLabel2(text = """Can't connect to Blinds

Trying to reconnect""")
        self.Title.font_size = 70
        self.add_widget(self.Title)


class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        self._lock = threading.Lock()


        self.Failed = 0

        self.currentScreen = 0
        super(MyGrid, self).__init__(**kwargs)
        #self.spacing = [10,10]
        #self.padding = [10,10,10,10]
        self.cols = 1
        self.Title = MyLabel(text="Auto Blind")
        self.Title.color = [0,0,1,1]
        self.Title.font_size= 70
        self.add_widget(self.Title)



        self.submitToggle = Button(text="Down", font_size=40)

        self.submitToggle.background_color = [1,0,0,1]
        self.submitToggle.bind(on_press=self.pressed)
        self.add_widget(self.submitToggle)
        #self.submitToggle.background_normal = ''
        #self.submitToggle.border = [10,10,10,10]

        self.submitAwayFromHome = Button(text="AwayFromHomeOn", font_size=40)
        self.submitAwayFromHome.bind(on_press=self.AwayFromHome)
        self.submitAwayFromHome.background_color = [0,1,0,1]
        self.add_widget(self.submitAwayFromHome)
        #self.submitAwayFromHome.background_normal = ''



        self.PickTime = Button(text="PickTimeOn", font_size=40)
        self.PickTime.bind(on_press=self.PickTimeOn)
        self.PickTime.background_color = [0,1,0,1]
        self.add_widget(self.PickTime)
        #self.PickTime.background_normal = ''

        self.inside = GridLayout()
        self.inside.cols = 2

        self.dropdown = DropDown()

        for i in range(24):
            for j in range(0,60,15):
                btn = Button(text = str(i)+":"+str(j),size_hint_y = None,height=200)
                btn.bind(on_release = lambda btn:self.dropdown.select(btn.text))
                self.dropdown.add_widget(btn)
                #btn.background_normal = ''
                btn.background_color = [0,1,1,1]
        #self.dropdown.container.spacing = 10
        self.mainbutton = Button(text="""Pick Time To Go Up""")
        self.mainbutton.bind(on_release = self.dropdown.open)
        self.dropdown.bind(on_select = self.mainButtonOneTrigger)
        self.inside.add_widget(self.mainbutton)
        self.mainbutton.background_color = [0,1,1,1]
        #self.mainbutton.background_normal = ''


        self.dropdown2 = DropDown()
        for i in range(24):
            for j in range(0,60,15):
                btn = Button(text = str(i)+":"+str(j),size_hint_y = None,height=200)
                btn.bind(on_release = lambda btn:self.dropdown2.select(btn.text))
                btn.background_color = [1,0,1,1]
                self.dropdown2.add_widget(btn)
                #btn.background_normal = ''
        self.mainbutton2 = Button(text="Pick Time to Go Down")
        self.mainbutton2.bind(on_release = self.dropdown2.open)
        self.dropdown2.bind(on_select = self.mainButtonTwoTrigger)
        self.inside.add_widget(self.mainbutton2)
        self.mainbutton2.background_color = [1,0,1,1]
        #self.mainbutton2.background_normal = ''

        self.submitTemperature = Button(text="Turn on Auto Temp Control",height=600)
        self.submitTemperature.bind(on_press=self.TempToggle)
        self.inside.add_widget(self.submitTemperature)
        self.submitTemperature.background_color = [0,1,0,1]
        #self.submitSunrise.background_normal = ''

        self.dropdown3 = DropDown()
        for i in range(10,50,2):
            btn = Button(text = str(i),size_hint_y = None,height=200)
            btn.bind(on_release = lambda btn:self.dropdown3.select(btn.text))
            btn.background_color = [1,1,0,1]
            self.dropdown3.add_widget(btn)
            #btn.background_normal = ''
        self.mainbutton3 = Button(text="Pick Temp")
        self.mainbutton3.bind(on_release = self.dropdown3.open)
        self.dropdown3.bind(on_select = self.mainButtonThreeTrigger)
        self.inside.add_widget(self.mainbutton3)
        self.mainbutton3.background_color = [1,1,0,1]

        #self.inside.spacing = [10,10]

        self.add_widget(self.inside)

        self.Calibrate = Button(text="Press To Start Calibration", font_size=40)
        self.Calibrate.bind(on_press=self.CalibrateNow)
        self.Calibrate.background_color = [0,1,0,1]
        self.add_widget(self.Calibrate)



        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.IP = s.getsockname()[0]
        s.close()

        self.sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock2.bind((self.IP,5005))
        #self.sock2.settimeout(5)


        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        self.state = False

        s.close()

        self.state = False

        self.sendMsg(self.IP)

        self.lastTime = time.time()
        x = threading.Thread(target=self.update, args=(1,))
        x.start()
        Clock.schedule_interval(self.checking,0.5)



    def Give(self,screens,screenobj):
        self.screens = screens
        self.screenObj = screenobj

    def isScreenReady(self,asking = True, state = False):
        if asking:
            return self.state
        if not asking:
            self.state = state


    def CalibrateNow(self,instance):
        self.sendMsg("Calibrate")


    def mainButtonThreeTrigger(self,instance,x):
        '''setattr(self.mainbutton3, "text","""Pick Temp above which should go Down
Current Choice: """ + x)'''
        self.sendMsg("Temp " + x)


    def mainButtonOneTrigger(self,instance,x):
        '''setattr(self.mainbutton, "text","""Pick Time To Go Up
Time Selected: """ + x)'''
        self.sendMsg("UpTime " + x)


    def mainButtonTwoTrigger(self,instance,x):
        '''setattr(self.mainbutton2, "text","""Pick Time To Go Down
Time Selected: """ + x)'''
        self.sendMsg("DownTime " + x)



    def PickTimeOn(self,instance):
        self.sendMsg("PickTime")


    def TempToggle(self,instance):
        self.sendMsg("Sunrise")


    def AwayFromHome(self,instance):
        self.sendMsg("AwayFromHome")


    def sendMsg(self,msg):
        with self._lock:
            UDP_IP = "192.168.0.38"
            UDP_PORT = 5005

            self.sock.sendto(msg.encode(), (UDP_IP,UDP_PORT))



    def pressed(self, instance):
        self.sendMsg("toggle")

    def get(self,getting = True):
        with self._lock:
            if getting:
                return self.lastTime
            else:
                self.lastTime = time.time()

    def checking(self,instance):
        a = self.get()
        if time.time()-a > 5:
            if self.isScreenReady() and self.currentScreen == 0:
                self.currentScreen = 1
                self.screenObj.switch_to(self.screens[1])
                #self.screenObj.current = "ErrorScreen"
        else:
            if self.isScreenReady() and self.currentScreen == 1:
                self.currentScreen = 0
                self.screenObj.switch_to(self.screens[0])





    def update(self, instance=None):
        while True:
            self.sendMsg(self.IP)
            self.sock2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.sock2.bind((self.IP,5005))
            self.sock2.settimeout(0.5)

            try:
                data, addr = self.sock2.recvfrom(1024)
            except socket.timeout:
                #print("cannot locate pi")
                self.sock2.close()
                continue
            self.get(False)
            #print("Got through")
            self.sock2.close()

            self.Failed = 0
            d = data.decode()
            d = d.split()
            if d[0] == "1":
                self.submitToggle.text="Down"
                self.submitToggle.background_color = [1,0,0,1]
            if d[0] == "0":
                self.submitToggle.text= "Up"
                self.submitToggle.background_color = [0,1,0,1]
            if d[1] == "1":
                self.submitAwayFromHome.text = "AwayFromHomeOff"
                self.submitAwayFromHome.background_color = [1,0,0,1]
            if d[1] == "0":
                self.submitAwayFromHome.text = "AwayFromHomeOn"
                self.submitAwayFromHome.background_color = [0,1,0,1]
            if d[2] == "1":
                self.submitTemperature.text = "Turn off Auto Temp Control"
                self.submitTemperature.background_color = [1,0,0,1]
            if d[2] == "0":
                self.submitTemperature.text = "Turn on Auto Temp Control"
                self.submitTemperature.background_color = [0,1,0,1]
            if d[3] == "1":
                self.PickTime.text = "Pick Time Off"
                self.PickTime.background_color = [1,0,0,1]
            if d[3] == "0":
                self.PickTime.text = "Pick Time On"
                self.PickTime.background_color = [0,1,0,1]
            if d[4] != "None":
                setattr(self.mainbutton, "text","""Pick Time To Go Up
        Time Selected: """ + d[4])
            if d[5] != "None":
                setattr(self.mainbutton2, "text","""Pick Time To Go Down
        Time Selected: """ + d[5])

            if d[6] != "None":
                setattr(self.mainbutton3, "text","""Pick Temp
        Current Choice: """ + d[6])
            if d[7] == "0":
                self.Calibrate.text = "Press To Start Calibration"
                self.Calibrate.background_color = [0,1,0,1]
            if d[7] == "1":

                self.Calibrate.text = "Stop when blind at the bottom"
                self.Calibrate.background_color = [1,0,0,1]


class MainScreen(Screen):
    pass

class ErrorScreen(Screen):
    pass









class MyApp(App):

    def build(self):
        sm = ScreenManager(transition=SlideTransition(
                                     duration=0.5))
        mainscreen = MainScreen(name="MainScreen")
        sm.add_widget(mainscreen)
        errorscreen = ErrorScreen(name="ErrorScreen")
        sm.add_widget(errorscreen)

        screenz = [mainscreen,errorscreen]
        a = MyGrid()
        a.Give(screenz,sm)
        a.isScreenReady(False,True)
        errorscreen.add_widget(MyGrid2())
        mainscreen.add_widget(a)


        return sm


if __name__ == "__main__":
    MyApp().run()
