import wx
from frame_main import mainframe,MyDialog_type_name
import json
import sys
import cv2
import os
from tkinter import *
import mysql
import pickle
import mysql.connector as sql
import numpy as np
import datetime
defaut_config = '{"camera":{"name":"noname","id":0}}'
#read config file
try:
    file_config = open("config.ini")
except:
    print("-create file config defaut")
    file_config = open("config.ini","w")
    file_config.write(defaut_config)
#take parameter config
try:
    config = json.loads(file_config.read())
except:
    config = json.loads(defaut_config)
################################################################################
########################### DATA BASE ##########################################
################################################################################
try :
    db = sql.connect(host = "localhost", user = "root", passwd = "", database = "diemdanh")
    print("connect to server assuces")
    cur = db.cursor()
except sql.errors.DatabaseError:
    print("can not connect to server")
    exit()
################################################################################

#################################################################################
########################initilize camera#########################################
#################################################################################
cap = cv2.VideoCapture(config["camera"]["id"])
if cap.isOpened():
    cap.open(config["camera"]["id"])
else:
    print("camera is used by other program")
    sys.exit(1)
############################SETTING LABEL########################################
#################################################################################
font = cv2.FONT_HERSHEY_SIMPLEX
#read pickle file
labels = {}
print("Starting app...")
print("type: q keyboard to exit")
#################################################################################
###########################cascade classifier####################################
#################################################################################
face_cascade = cv2.CascadeClassifier('classifier/haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainner/trainner_face.yml")
class frame(mainframe):
    """docstring for ClassName"""
    def __init__(self, parent):
        mainframe.__init__(self,parent)
    def outclose( self, event ):
        cap.release()
        cv2.destroyAllWindows()
        self.Destroy()
    def mainframeOnClose( self, event ):
        cap.release()
        cv2.destroyAllWindows()
        dialog.Destroy()
        self.Destroy()
    def m_menuItem_exitOnMenuSelection( self, event ):
        cap.release()
        cv2.destroyAllWindows()
        dialog.Destroy()
        self.Destroy()

    def m_menuItem_aboutOnMenuSelection( self, event ):
        wx.MessageBox("this is face recognizer program v1")

    def m_button_runOnButtonClick( self, event ):
        recognizer.read("trainner/trainner_face.yml")
        with open("labels.pickle","rb") as f:
            og_labels = pickle.load(f)
            labels = {v:k for k,v in og_labels.items()}
            print("hahah"+str(labels))
        while(True):
            # Capture frame-by-frame
            try:
                ret, frame = cap.read()
            except:
                break
            # Our operations on the frame come here
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #--------------------------------------------
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                #take gray of face
                roi_gray = gray[y:y+h, x:x+w]
                #check confident of gray in data train
                id_,conf = recognizer.predict(roi_gray)
                print(conf)
                percent = " {0}%".format(round(100-conf))
                if conf>=15 and conf <=50:
                    bel = labels[id_]
                    color = (0,255,0)
                    print ("hello "+bel)
                    try:
                        # Thêm các hàng trong chi tiết điểm danh
                        cur.execute("select MAX(id) AS maximum from chitietdd where masv = '%s'" % (bel))
                        rud4 = cur.fetchall()
                        id_temp =0
                        for l in rud4:
                            id_temp = l[0]
                        cur.execute("UPDATE chitietdd SET trangthai='Có mặt' WHERE id = %s" % (id_temp))
                        db.commit()
                        print(cur.rowcount, "record(s) affected")
                        #sql_insert = "INSERT INTO dsds (name,time_in,time_out) VALUES (%s , %s, %s)"
                        #val_insert = (bel,"haha","None")
                        #cur.execute(sql_insert,val_insert)
                        #db.commit()
                        #print(cur.rowcount, "record inserted.")
                    except:
                        print ("error insert")
                        pass
                else:
                    bel = "Unknow"
                    color = (0,0,255)
                #draw rectangle in face
                frame = cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
                #--------------------------------------------------------------
                cv2.putText(frame,bel,(x+10,y-10), font, 1,color,2,cv2.LINE_AA)
                cv2.putText(frame,percent,(x+10,y+h-10), font, 1,color,2,cv2.LINE_AA)
                # Display the resulting frame
            cv2.imshow('FACE DETECTION PROGRAM',frame)
            # Exit program
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    def m_button_train_datasetOnButtonClick( self, event ):
        y_labels = []
        x_train = []
        #get dir of folder program
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(BASE_DIR,"images")
        current_id = 0
        label_ids ={}
        for root,dirs,files in os.walk(image_dir):
            for file in files:
               if file.endswith("png") or file.endswith("jpg"):
                    path = os.path.join(root,file)
                    label = os.path.basename(root).replace(" ","-").lower()
                    if label in label_ids:
                        pass
                    else:
                        label_ids[label] = current_id
                        current_id += 1
                    id_ = label_ids[label]
                    try:
                        image_array = cv2.imread(path,0)
                    except:
                        continue
                    faces = face_cascade.detectMultiScale(image_array, 1.3, 5)
                    #if face is detect, append to x_train array, y_labels array
                    for(x,y,w,h) in faces:
                        roi = image_array[y:y+h,x:x+w]
                        x_train.append(roi)
                        y_labels.append(id_)
                    cv2.imshow("TRAINING",image_array)
        with open("labels.pickle","wb") as f:
            pickle.dump(label_ids,f)
        recognizer.train(x_train,np.array(y_labels))
        recognizer.save("trainner/trainner_face.yml")
        cv2.destroyAllWindows()
        wx.MessageBox("FINISH TRAINING DATA")
        #print "finish"
    def m_button_create_datasetOnButtonClick( self, event ):
        dialog.Show()

class dialog_type_name(MyDialog_type_name):
    
    def __int__(self,parent):
        MyDialog_type_name.__int__(self,parent)
    def m_sdbSizerOnCancelButtonClick( self, event ):
        event.Skip()

    def m_sdbSizerOnOKButtonClick( self, event ):
        name = self.m_textCtrl.GetLineText(0)
        id_sv = self.m_textCtrl1.GetLineText(0)
        malop = self.m_textCtrl2.GetLineText(0)
        i=0
        j=0
        offset = 50
        if name == "":
            wx.MessageBox("type name please !")
        elif id_sv == "":
            wx.MessageBox("type masv please !")
        elif malop =="":
            wx.MessageBox("type class please !")
        else:
            print("ten :"+name+" id:"+id_sv+" lop:"+malop)
            dialog.Show(False)
            path = "images/"+str(id_sv)
            if os.path.exists(path):
               print("folder is exists")
            else:
               print("folder is created")
               os.mkdir(path)
            for root,dirs,files in os.walk(path):
               for file in files:
                   j += 1
            while True:
                ret,img = cap.read()
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray,1.2,5)
                for (x,y,w,h) in faces:
                   i +=1
                   #lưu ảnh
                   cv2.imwrite(path+"/"+id_sv+"_"+str(i+j)+".jpg",gray[y-offset:y+h+offset,x-offset:x+w+offset])
                   # vẽ 1 hình vuông
                   cv2.rectangle(img,(x,y),(x+w,y+h),(225,0,0),1)
                   cv2.putText(img,"sample"+str(i),(x,y), font, 1,(0,0,255),2,cv2.LINE_AA)
                   cv2.imshow("create dataset face",img)
                cv2.waitKey(100)
                if i>=50:
                   cv2.destroyAllWindows()
                   wx.MessageBox("create dataset finish")
                   sql_insertsv = "INSERT INTO sinhvien (masv,tensv,malop) VALUES (%s , %s, %s)"
                   val_insertsv = (id_sv,name, malop)
                   cur.execute(sql_insertsv,val_insertsv)
                   db.commit()
                   break
###################################################################################
################################ MAIN #############################################
###################################################################################
win = Tk()
win.geometry("500x400")
win.title("Login Page")
try :
    db = sql.connect(host = "localhost", user = "root", passwd = "", database = "diemdanh")
    print("connect to server assuces")
    cur = db.cursor()
except sql.errors.DatabaseError:
    print("can not connect to server")
    exit()
def login() :
    try:
        #lấy dữ liệu về tài khoản
        user = user1.get()
        #lấy dữ liệu mật khẩu
        passwd = passwd1.get()
        #lấy dữ liệu mã môn học
        mamon = ma_mon1.get()
        date_object = datetime.date.today()
        print(user)
        
        cur.execute("select * from giaovien where magv = '%s' and matkhaugv = %s" % (user, passwd))
        rud = cur.fetchall()
        if rud:
            print("apply success")
            cur.execute("select * from monhoc where magv = '%s' and id = %s" % (user, mamon))
            rud1 = cur.fetchall()
            if rud1:
                print("apply success mamon")
                print("ngày"+str(date_object))
                cur.execute("select * from diemdanh where mamon = '%s' and ngaydd = '%s'" % (mamon, str(date_object)))
                rud2 = cur.fetchall()
                if rud2:
                    print("Đã có điểm danh ngày hôm nay")
                    pass
                else:
                    sql_insertdd = "INSERT INTO diemdanh (mamon,ngaydd) VALUES (%s , %s)"
                    val_insertdd = (mamon,date_object)
                    cur.execute(sql_insertdd,val_insertdd)
                    db.commit()
                    print(cur.rowcount, "Them hang diem danh moi.")
                    pass
                # Tìm id điểm danh mới nhất
                cur.execute("SELECT MAX(id) AS maximum FROM diemdanh where mamon = '%s'" % (mamon))
                result = cur.fetchall()
                id_dd =0
                for i in result:
                    id_dd = i[0]
                print("hàng mới nhất " + str(id_dd))
                # Lấy giá trị mã lớp
                cur.execute("select malop from monhoc where id = %s" % (mamon))
                malop=""
                rud3 = cur.fetchall()
                for j in rud3:
                    malop=j[0]
                print("Mã lớp " + str(malop))
                # Thêm các hàng trong chi tiết điểm danh
                cur.execute("select MAX(masv) AS maximum from sinhvien where malop = '%s'" % (malop))
                rud4 = cur.fetchall()
                id_svtemp =0
                for h in rud4:
                    id_svtemp = h[0]
                cur.execute("SELECT * from chitietdd where masv = '%s' and madd = '%s'" % (id_svtemp,id_dd))
                rud5 = cur.fetchall()
                if rud5:
                    print("có danh sách r")
                    pass
                else:
                    cur.execute("select masv from sinhvien where malop = '%s'" % (malop))
                    rud6 = cur.fetchall()
                    for k in rud6:
                        sql_insertctdd = "INSERT INTO chitietdd (masv,trangthai,madd) VALUES (%s , %s, %s)"
                        val_insertctdd = (k[0],"Vắng",id_dd)
                        cur.execute(sql_insertctdd,val_insertctdd)
                        db.commit()
                    print("Welcome")
                #-------------------------------
                frames = frame(None)
                #-------------------------------
                frames.Show()
                #------------------------------
                win.destroy()
                app.MainLoop()
            else:
                print("Eror object or account")
        else:
            print("Eror pass or account")
            exit()
        cur.close()
        db.close()
    except mysql.connector.errors.ProgrammingError:
        print("hello sai")
        pass      
    
    
userlvl = Label(win, text = "Username :")
passwdlvl = Label(win, text = "Password  :")
ma_mon_lvl = Label(win, text = "ID_Subject")

user1 = Entry(win, textvariable = StringVar())
passwd1 = Entry(win, textvariable = IntVar().set(""))
ma_mon1 = Entry(win, textvariable = StringVar())


enter = Button(win, text = "Enter", command = lambda: login(), bd = 0)
enter.configure(bg = "pink")
user1.place(x = 200, y = 120)
passwd1.place(x = 200, y = 170)
ma_mon1.place(x = 200, y = 220)

userlvl.place(x = 130, y = 120)
passwdlvl.place(x = 130, y = 170)
ma_mon_lvl.place(x = 130, y = 220)

enter.place(x = 238, y = 275)
app = wx.App()
dialog = dialog_type_name(None)
win.mainloop()

