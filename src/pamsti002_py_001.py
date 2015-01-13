#! /usr/bin/python
#-*-coding: utf-8 -*-

#ref. file: pyqttoc001.py

from PyQt4.QtGui import *
import mywindow001, sys, os

def main(args):
    os.system('clear')
    a=QApplication(args)
    # Création d'un widget qui servira de fenêtre
    mainapp=mywindow001.myguiapp()
    mainapp.show()
    r=a.exec_()
    return r

if __name__=="__main__":
    main(sys.argv)