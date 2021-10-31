# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 11:48:04 2020

@author: Admin
"""

import mysql.connector
from tkinter import *
import wx
import mysql
from frame_main import mainframe,MyDialog_type_name
import sys
import cv2
import os
import pickle
import mysql.connector as sql
import numpy as np
import datetime
from playsound import playsound

win = Tk()
win.geometry("500x325")
win.title("Login Page")
try :
    db = sql.connect(host = "localhost", user = "root", passwd = "", database = "opencv")
    print("connect to server assuces")
    cur = db.cursor()
except sql.errors.DatabaseError:
    print("can not connect to server")
    exit()
def login() :
    try:
        user = user1.get()
        passwd = passwd1.get()
        print(user)
        cur.execute("select * from teacher where Acc_Teacher = '%s' and Pass_Teacher = %s" % (user, passwd))
        rud = cur.fetchall()
        if rud:
            print("Welcome")
          
        else:
            print("Account Eror")
        cur.close()
        db.close()
    except mysql.connector.errors.ProgrammingError:
        print("hello sai")
        pass      
userlvl = Label(win, text = "Username :")
passwdlvl = Label(win, text = "Password  :")
user1 = Entry(win, textvariable = StringVar())
passwd1 = Entry(win, textvariable = IntVar().set(""))
enter = Button(win, text = "Enter", command = lambda: login(), bd = 0)
enter.configure(bg = "pink")
user1.place(x = 200, y = 120)
passwd1.place(x = 200, y = 170)
userlvl.place(x = 130, y = 120)
passwdlvl.place(x = 130, y = 170)
enter.place(x = 238, y = 225)
win.mainloop()