#! /usr/bin/python
#-*-coding: utf-8 -*-

import os,MySQLdb
import PyQt4.QtGui as gui
from PyQt4.QtGui import QWidget, QLabel, QPushButton, QListWidget, QLineEdit, QRadioButton, QButtonGroup, QTimeEdit, QCheckBox
from PyQt4.QtCore import QSocketNotifier, SIGNAL, QTime

myfifor = "/tmp/ctopyfifo"
myfifow = "/tmp/pytocfifo"

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
    
    keyBoardAlpha = {}
    keyBoardNum = {}
    
    def __init__(self):
        global projlist
        global clickonkeyb
    
        QWidget.__init__(self)
        
        screen = gui.QDesktopWidget().screenGeometry()
        hpos = (screen.width() - widwith) / 2
        vpos = (screen.height() - widheight) / 2

        self.w1label1=QLabel(self.trUtf8("pamsti002 sys running.."), self)
        self.w1label1.move(10,10)

        self.w1label2=QLabel(self.trUtf8("status:"), self)
        self.w1label2.move(10,30)

        self.w1label3=QLabel(self.trUtf8(".."), self)
        self.w1label3.setFixedSize(280,18)
        self.w1label3.move(60,30)

        self.w1button2=QPushButton(self.trUtf8("Quit"), self)
        self.w1button2.move(10,205)
        
        self.setFixedSize(widwith,widheight)
        self.move(hpos,vpos)

        self.connect(self.w1button2, SIGNAL("clicked()"), self.closeAll)
        
        self.fdr = os.open(myfifor, os.O_RDONLY | os.O_NONBLOCK)
        
        self.notifier_r = QSocketNotifier(self.fdr, QSocketNotifier.Read)
        self.connect(self.notifier_r, SIGNAL('activated(int)'), self.readAllData)

        self.w2=QWidget()
        self.w2.setFixedSize(widwith,widheight)
        self.w2.move(hpos,vpos)

        self.w2.label1=QLabel(self.trUtf8("init wait.."), self.w2)
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
        
        self.w2.rb1 = QRadioButton(self.trUtf8("matin"),self.w2)
        self.w2.rb1.move(210,120)

        self.w2.rb2 = QRadioButton(self.trUtf8("après-midi"),self.w2)
        self.w2.rb2.move(210,140)

        matin_aprem = QButtonGroup()
        matin_aprem.addButton(self.w2.rb1)
        matin_aprem.addButton(self.w2.rb2)

        self.w2.hourEdit = QTimeEdit(self.w2)  
        self.w2.hourEdit.resize(45,40)
        self.w2.hourEdit.move(212,180)
        self.w2.hourEdit.setDisplayFormat("HH")    
        self.w2.hourEdit.setTime(QTime.currentTime())   
        
        self.w2.minuteEdit = QTimeEdit(self.w2)  
        self.w2.minuteEdit.resize(45,40)
        self.w2.minuteEdit.move(266,180)
        self.w2.minuteEdit.setDisplayFormat("mm")    
        self.w2.minuteEdit.setTime(QTime.currentTime())

        self.w2.timeDots=QLabel(self.trUtf8(":"), self.w2)
        self.w2.timeDots.setFixedWidth(10)
        self.w2.timeDots.move(260,192)
        
        self.w2.infoLabel=QLabel(self.trUtf8("info:"), self.w2)
        self.w2.infoLabel.setFixedWidth(30)
        self.w2.infoLabel.move(10,220)

        self.w2.info=QLabel(self.trUtf8("..."), self.w2)
        self.w2.info.setFixedWidth(260)
        self.w2.info.move(50,220)

        self.initKeybLayout()
        
        self.w3=QWidget()
        self.w3.setFixedSize(widwith,widheight)
        self.w3.move(hpos,vpos)
        
        self.w3.button1=QPushButton(self.trUtf8("Fermer"), self.w3)
        self.w3.button1.move(10,205)
        
        self.w3.button2=QPushButton(self.trUtf8("Enregistrement"), self.w3)
        self.w3.button2.move(120,205)
        
        self.connect(self.w3.button1, SIGNAL("clicked()"), self.closeCatering)
        
        self.w3.label1=QLabel(self.trUtf8("Enregistrement"), self.w3)
        self.w3.label1.move(10,50)
        
        self.w3.label2=QLabel(self.trUtf8("Sélection"), self.w3)
        self.w3.label2.move(10,70)
        
        self.w3.label3=QLabel(self.trUtf8("Midi"), self.w3)
        self.w3.label3.move(120,90)
        
        self.w3.cb1E=QCheckBox('', self.w3)
        self.w3.cb1E.setEnabled(False)
        self.w3.cb1E.move(120,50)
        
        self.w3.cb1S=QCheckBox('', self.w3)
        self.w3.cb1S.move(120,70)
        
        self.w3.label4=QLabel(self.trUtf8("Soir"), self.w3)
        self.w3.label4.move(155,90)
        
        self.w3.cb2E=QCheckBox('', self.w3)
        self.w3.cb2E.setEnabled(False)        
        self.w3.cb2E.move(155,50)
        
        self.w3.cb2S=QCheckBox('', self.w3)
        self.w3.cb2S.move(155,70)        
        
        self.w3.label5=QLabel(self.trUtf8("Nuit"), self.w3)
        self.w3.label5.move(190,90)
        
        self.w3.cb3E=QCheckBox('', self.w3)
        self.w3.cb3E.setEnabled(False)        
        self.w3.cb3E.move(190,50)
        
        self.w3.cb3S=QCheckBox('', self.w3)
        self.w3.cb3S.move(190,70)        
        
        self.w3.label6=QLabel(self.trUtf8("Aller"), self.w3)
        self.w3.label6.move(225,90)
        
        self.w3.cb4E=QCheckBox('', self.w3)
        self.w3.cb4E.setEnabled(False)        
        self.w3.cb4E.move(225,50)
        
        self.w3.cb4S=QCheckBox('', self.w3)
        self.w3.cb4S.move(225,70)        
        
        self.w3.label7=QLabel(self.trUtf8("Retour"), self.w3)
        self.w3.label7.move(260,90)
        
        self.w3.cb5E=QCheckBox('', self.w3)
        self.w3.cb5E.setEnabled(False)        
        self.w3.cb5E.move(260,50)
        
        self.w3.cb5S=QCheckBox('', self.w3)
        self.w3.cb5S.move(260,70)        
        
    def closeCatering(self):
        self.w3.close()

    def readAllData(self):
        global readdata
        bufferSize = 1024
        while True:
            data = os.read(self.fdr, bufferSize)
            if not data:
                break
            readdata = self.trUtf8(data)
            if readdata == 'Hi':
                self.w1label3.setText(self.trUtf8("received init signal.."))
                fdw = os.open(myfifow, os.O_WRONLY)
                os.write(fdw, "Ok\0")
                os.close(fdw)
            elif readdata == 'Bye':
                self.w1label3.setText(self.trUtf8("received quit signal.."))
                fdw = os.open(myfifow, os.O_WRONLY)
                os.write(fdw, "Ok\0")
                os.close(fdw)
            else:
                self.w1label3.setText(self.trUtf8("received " + readdata))
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

        try:
            fdw = os.open(myfifow, os.O_WRONLY)
            os.write(fdw, "Quit\0")
            os.close(fdw)
        except:
            print "Pipe already closed.."

        # Close all cursors
        cur1.close()
        cur2.close()
        cur3.close()
        cur4.close()
        # Close databases
        db.close()

        os.close(self.fdr)
        gui.qApp.quit()

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

    def initButtonSpace(self):        
        self.w2.buttonSpace=QPushButton(self.trUtf8("-"), self.w2)
        self.w2.buttonSpace.setFixedSize(40,20)
        self.w2.buttonSpace.move(90,200)
        self.connect(self.w2.buttonSpace, SIGNAL("clicked()"), self.buttonSpace)

    def buttonSpace(self):
        self.w2.qle1.setText(self.w2.qle1.text()+' ')

    def initButtonBackSpace(self):        
        self.w2.buttonBackSpace=QPushButton(self.trUtf8("<"), self.w2)
        self.w2.buttonBackSpace.setFixedSize(40,20)
        self.w2.buttonBackSpace.move(90,120)
        self.connect(self.w2.buttonBackSpace, SIGNAL("clicked()"), self.buttonBackSpace)

    def buttonBackSpace(self):
        self.w2.qle1.setText(self.w2.qle1.text()[:-1])

    def initButtonZero(self):        
        self.w2.buttonZero=QPushButton(self.trUtf8("0"), self.w2)
        self.w2.buttonZero.setFixedSize(40,20)
        self.w2.buttonZero.move(140,180)
        self.connect(self.w2.buttonZero, SIGNAL("clicked()"), self.buttonZero)

    def buttonZero(self):
        self.w2.qle1.setText(self.w2.qle1.text()+'0')

    def initButtonCatering(self):        
        self.w2.buttonCatering=QPushButton(self.trUtf8("Repas"), self.w2)
        self.w2.buttonCatering.setFixedSize(60,20)
        self.w2.buttonCatering.move(140,200)
        self.connect(self.w2.buttonCatering, SIGNAL("clicked()"), self.buttonCatering)

    def buttonCatering(self):
        self.w3.show()
        self.w3.raise_()
        self.w3.activateWindow()

    def initKeybLayout(self):
        self.initButtonSpace()
        self.initButtonBackSpace()
        self.initButtonZero()
        self.initButtonCatering()

        keyDataAlpha = [["a", 10, 120],
                ["b", 30, 120],
                ["c", 50, 120],
                ["d", 70, 120],
                ["e", 10, 140],
                ["f", 30, 140],
                ["g", 50, 140],
                ["h", 70, 140],
                ["i", 90, 140],
                ["j", 110, 140],
                ["k", 10, 160],
                ["l", 30, 160],
                ["m", 50, 160],
                ["n", 70, 160],
                ["o", 90, 160],
                ["p", 110, 160],
                ["q", 10, 180],
                ["r", 30, 180],
                ["s", 50, 180],
                ["t", 70, 180],
                ["u", 90, 180],
                ["v", 110, 180],
                ["w", 10, 200],
                ["x", 30, 200],
                ["y", 50, 200],
                ["z", 70, 200]]

        for index, k in enumerate(keyDataAlpha):
            self.keyBoardAlpha[index]=keybButton(k[0], k[1], k[2], self.w2)

        keyDataNum = [["7", 140, 120],
                ["8", 160, 120],
                ["9", 180, 120],
                ["4", 140, 140],
                ["5", 160, 140],
                ["6", 180, 140],
                ["1", 140, 160],
                ["2", 160, 160],
                ["3", 180, 160],
                [".", 180, 180]]
        
        for index, k in enumerate(keyDataNum):
            self.keyBoardNum[index]=keybButton(k[0], k[1], k[2], self.w2)

class keybButton:

    def __init__(self, letter, x, y, parent):
        self.letter=letter
        self.parent=parent
        self.keyButton=QPushButton(parent.trUtf8(self.letter), parent)
        self.keyButton.setFixedSize(20,20)
        self.keyButton.move(x,y)
        parent.connect(self.keyButton, SIGNAL("clicked()"), self.buttonAction)

    def buttonAction(self):
        self.parent.qle1.setText(self.parent.qle1.text()+self.letter)


