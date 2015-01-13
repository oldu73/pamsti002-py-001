#! /usr/bin/python
#-*-coding: utf-8 -*-
import os,sys,MySQLdb
import PyQt4.QtGui as gui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QSocketNotifier, SIGNAL

myfifor = "ctopyfifo"
myfifow = "pytocfifo"

try:
    os.mkfifo(myfifor)
    os.mkfifo(myfifow)   

except OSError:
    pass

db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="pamsti001")
cur1 = db.cursor()
cur2 = db.cursor()
cur3 = db.cursor()
cur4 = db.cursor()

projlist = None
readdata = None

widwith = 320
widheight = 240

class myguiapp(QWidget):
    def __init__(self):
    global projlist
    global clickonkeyb
    
        QWidget.__init__(self)
        
        screen = gui.QDesktopWidget().screenGeometry()
    hpos = (screen.width() - widwith) / 2
    vpos = (screen.height() - widheight) / 2

        self.w1label1=QLabel(self.trUtf8("pamsti001 sys running..."), self)
        self.w1label1.move(10,10)

        self.w1button2=QPushButton(self.trUtf8("Quit"), self)
        self.w1button2.move(10,205)
        
        self.setFixedSize(widwith,widheight)
        self.move(hpos,vpos)

    self.connect(self.w1button2, SIGNAL("clicked()"), self.closeAll)
    
    self.fdr = os.open(myfifor, os.O_RDONLY)
    
    self.notifier_r = QSocketNotifier(self.fdr, QSocketNotifier.Read)
    self.connect(self.notifier_r, SIGNAL('activated(int)'), self.readAllData)
    
    self.w2=QWidget()
    self.w2.setFixedSize(widwith,widheight)
    self.w2.move(hpos,vpos)
    self.w2.label1=QLabel(self.trUtf8("init wait..."), self.w2)
    self.w2.label1.setFixedWidth(150)
    self.w2.label1.move(170,15)
      
    self.w2.button1=QPushButton(self.trUtf8("OK"), self.w2)
    self.w2.button1.setFixedSize(40,25)
    self.w2.button1.move(120,10)
    
    self.w2.projlist1 = QListWidget(self.w2)
    self.w2.projlist1.setFixedSize(300,75)
    self.w2.projlist1.move(10,40)
    
    cur2.execute("SELECT projnumb,clientname,clientprojid,clientlocation FROM projdesc001")
    projlist = cur2.fetchall()
  
    for item1 in projlist:
      tmpstr1 = ""
      for item2 in item1:
        tmpstr1 += item2.decode('latin-1').encode("utf-8") + " / "
      self.w2.projlist1.addItem(self.trUtf8(tmpstr1))

    self.connect(self.w2.button1, SIGNAL("clicked()"), self.writeAllData)
    
    self.w2.qle1 = QLineEdit(self.w2)
    self.w2.qle1.setFixedSize(100,25)
    self.w2.qle1.move(10,10)

    self.w2.qle1.textChanged[str].connect(self.onChanged)
    
    self.w2.buttonA=QPushButton(self.trUtf8("a"), self.w2)
    self.w2.buttonA.setFixedSize(20,20)
    self.w2.buttonA.move(10,120)
    self.connect(self.w2.buttonA, SIGNAL("clicked()"), self.buttonA)

    self.w2.buttonSpace=QPushButton(self.trUtf8("sp"), self.w2)
    self.w2.buttonSpace.setFixedSize(25,20)
    self.w2.buttonSpace.move(200,200)
    self.connect(self.w2.buttonSpace, SIGNAL("clicked()"), self.buttonSpace)

    def readAllData(self):
    global readdata
    bufferSize = 1024
    while True:
      data = os.read(self.fdr, bufferSize)
      if not data:
        break
      readdata = self.trUtf8(data)
      cur1.execute("SELECT firstname, lastname FROM person001 WHERE rfid = %s",readdata)
      person = cur1.fetchone()
      # person is a tuple
      self.w2.label1.setText(self.trUtf8(str(person[0]).decode('latin-1').encode("utf-8") + " " + str(person[1]).decode('latin-1').encode("utf-8")))
      self.w2.show()
      self.w2.raise_()
      self.w2.activateWindow()

    def writeAllData(self):
    global projlist,readdata
    fdw = os.open(myfifow, os.O_WRONLY)
    os.write(fdw, "Ok\0")
    os.close(fdw)

    try:
      # Execute the SQL command
      cur3.execute("INSERT INTO timeisup001(rfid,projnumb) VALUES('%s','%s')"%(readdata,self.trUtf8(projlist[self.w2.projlist1.currentRow()][0])))
      # Commit your changes in the database
      db.commit()
    except:
      # Rollback in case there is any error
      db.rollback()

    self.w2.close()
          
    def closeAll(self):
      
    fdw = os.open(myfifow, os.O_WRONLY)
    os.write(fdw, "Quit\0")
    os.close(fdw)
      
    # Close all cursors
    cur1.close()
    cur2.close()
    cur3.close()
    cur4.close()
    # Close databases
    db.close()

    os.close(self.fdr)
    qApp.quit()

    def onChanged(self, text):
    global projlist
    
    tmpstr0 = '%'+text+'%'
    cur4.execute("""SELECT projnumb,clientname,clientprojid,clientlocation FROM projdesc001 WHERE 
    projnumb LIKE '%s' OR clientname LIKE '%s' OR clientprojid LIKE '%s' OR clientlocation LIKE '%s'""" % (tmpstr0,tmpstr0,tmpstr0,tmpstr0))

    self.w2.projlist1.clear()

    projlist = cur4.fetchall()

    for item1 in projlist:
      tmpstr1 = ""
      for item2 in item1:
        tmpstr1 += item2.decode('latin-1').encode("utf-8") + " / "
      self.w2.projlist1.addItem(self.trUtf8(tmpstr1))

    def buttonA(self):
    self.w2.qle1.setText(self.w2.qle1.text()+'a')

    def buttonSpace(self):
    self.w2.qle1.setText(self.w2.qle1.text()+' ')