import cv2
import gc
from numpy import ndarray
from imutils import grab_contours
from easyocr import Reader
from tkinter import *
import re
from email.message import EmailMessage
import ssl
import smtplib
import pywhatkit
from datetime import datetime


def googlesheet(plate_number, client, t):
    try:
        sheet = client.open("Parking slots").worksheet("Sheet1")
    except Exception as e:
        print("The connection was not estabilished.")
        return 
    cells=sheet.col_values(col=1)
    s_no=len(cells)
    insertrow=[plate_number,s_no,t]
    sheet.insert_row(insertrow,s_no+1)
    return [plate_number,s_no,t]

def sendgmail(s,client):
    plate_number = str(s[0])
    slot = str(s[1])
    #The sheet holding the faculty information
    sheet2=  client.open("Parking slots").worksheet("Sheet2") #has details of the owner of vehicle
    #fetching the required email address
    RecieverDetails = sheet2.row_values(sheet2.find(plate_number).row)
    #preparing the mail contents
    sender = "uparkopen@gmail.com" #email id of sender
    password = "seufgscbiedmpxya" #password for the sender's account
    reciever = str(RecieverDetails[-2]) #email id of the receiver
    subject = "This is your parking slot" #subject of the email
    body = f"You have to park your vehical at slot number {slot}" #body of the email

    #collecting all the elments of the email message
    e = EmailMessage() #making the message
    e['From'] = sender #setting the from as the sender's email id
    e['To'] = reciever #setting the to as the reciever's email id
    e['Subject'] = subject #setting the subject in the email
    e.set_content(body) #combining the contents

    #creating the context
    con = ssl.create_default_context()

    #sending the email using the smtplib module
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=con) as smtp:
        smtp.login(sender,password) #the account from which it is to be send
        smtp.sendmail(sender,reciever,e.as_string()) #the from,to and content of the email to be sent ''')

def sendwhatsapp(s, client):
    plate_number = str(s[0])
    slot_number = str(s[1])
    sheet2=  client.open("Parking slots").worksheet("Sheet2") #has details of the owner of vehicle
    RecieverDetails = sheet2.row_values(sheet2.find(plate_number).row)
    contact_number = "+"+str(RecieverDetails[-1])
    pywhatkit.sendwhatmsg_instantly(contact_number, "Dear faculty, You have entered college premise with vehicle number: " + " "
    + plate_number + " " + "have been assigned the parking slot number" + " " + slot_number)

def isValid(number):
    pattern = '^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$'
    result = re.match(pattern, number)
    if result:
        return True
    else:
        return False

def time():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return str(current_time)

def plate_read(a):
    img = a
    img2 = a
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plateCascade = cv2.CascadeClassifier('lp.xml')
    faces = plateCascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors = 5, minSize=(25,25))
    plat = []
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,0),5)
        plat = img[y: y+h, x:x+w]
    if (type(plat) is ndarray):
        gray = cv2.cvtColor(plat, cv2.COLOR_BGR2GRAY)
        blured_image = cv2.GaussianBlur(gray,(11,11),0)
        edge_image_blur = cv2.Canny(blured_image,30,100)
        edge_image_normal = cv2.Canny(gray,30,100)
        #Finding points of contours
        key_points=cv2.findContours(edge_image_blur,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        #defining contours from keypoints
        contours = grab_contours(key_points)
        #drawing contours
        reader = Reader(['en'])
        all_reads = reader.readtext(plat)
        license_plate = ("".join(map(lambda read: read[-2], all_reads))).upper()
        del(faces)
        gc.collect()
        cv2.destroyAllWindows()
        return str(license_plate)
    del(faces)
    gc.collect()
    cv2.destroyAllWindows()
    return
    

def ReadFromVideo(p):
    l = []
    #cap = cv2.VideoCapture(p)
    flag = True
    while flag:
        cap = cv2.VideoCapture(p)
        ret, frame = cap.read()
        if (type(frame) is ndarray):

            # Extract Region of interest
            #roi = frame[350: 730,510: 810]
            roi = frame[350: 600,350:1000]
            pl = (plate_read(roi))
            #cv2.imshow("roi", roi)
            #cv2.imshow("Frame", frame)

            key = cv2.waitKey(30)
            if key == 27:
                break
            
        else:
            flag = False
        #show_frames()
    cap.release()
    cv2.destroyAllWindows()


"""try: 
    #estabilishing the connectivity between the google sheet
        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("reading/gs_credentials.json",scope)
        client = gspread.authorize(creds)
except Exception as e:
        print("The connection was not estabilished.")
ReadFromVideo('VN20221021_095309.mp4')
#ReadFromVideo(0)"""