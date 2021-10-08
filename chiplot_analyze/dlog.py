# imports to enable Topleve()
from tkinter import *

def setDebug(debugLevel = 0):
	global _debug
	_debug = debugLevel

def dlog(string, debug='d'):
	if (debug == 'l'):
		print(string)
	elif(_debug > 0):
		print('debug: '+string)

def errorMessage(command, ignoreCommand, title, messageString, errorString):
	window = Toplevel()
	window.title(title)
	Label(window, text = messageString).grid(row = 0, columnspan = 2)
	Label(window, text = errorString, fg = '#f00').grid(row = 1, columnspan = 2)
	Button(window, text = "Redo", command = command).grid(row = 2, column = 0, sticky = W)
	Button(window, text = "Ignore", command = ignoreCommand).grid(row = 2, column = 1, sticky = E)
	window.lift()
	return window