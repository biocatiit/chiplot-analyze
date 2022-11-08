#!/usr/bin/python
"""This program inputs chiplot files from a GUI and then under instruction
from the user, determines reflection points and splits the chiplot accordingly."""

# basic library imports
import os, sys, getopt

# imports for GUI
from tkinter import *
import tkinter.filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# import the splitter routines
from chiplot_analyze.dlog import *
from chiplot_analyze.splitter.splitter import Splitter
from chiplot_analyze.background_sub.bgsub import BackgroundSub
from chiplot_analyze.peak_analyzer.centroid import Centroid
from chiplot_analyze.chiplot import Chiplot

print('Python Version', sys.version)

class mainClass:
	def __init__(self, width, height, centerErrorRange, zoomMin, basemove):
		"""initialization routine for splitter main class, simply sets
		default class variables"""
		# create GUI
		self.root = Tk()
		self.root.title('Chiplot Splitter')

		# Header buttons for global options
		Button(self.root, text = "Split New Chiplot", command = self.splitNew).grid(row = 0, column = 0, sticky = W)
		self.leftBgButton = Button(self.root, text = "Left BGsub Chiplot", command = self.subLeft, state = DISABLED)
		self.leftBgButton.grid(row = 1, column = 1, columnspan = 1, sticky = W)
		self.rightBgButton = Button(self.root, text = "Right BGsub Chiplot", command = self.subRight, state = DISABLED)
		self.rightBgButton.grid(row = 1, column = 2, columnspan = 1, sticky = W)
		Button(self.root, text = "BGSub New Chiplot", command = self.subNew).grid(row = 0, column = 1, columnspan = 1, sticky = W)
		Button(self.root, text = "Centroid New Chiplot", command = self.centNew).grid(row = 0, column = 2, columnspan = 1, sticky = W)
		self.currCentButton = Button(self.root, text = "Centroid Current Chiplot", command = self.centCurr, state = DISABLED)
		self.currCentButton.grid(row=1, column = 3, columnspan = 1, sticky = W)
		Button(self.root, text = "Exit", command = self.exit).grid(row = 0, column = 3, columnspan = 2, sticky = W)


		# create and pack in figure
		self.fig = Figure(figsize = (width, height), dpi=100)
		self.plotCanvas = FigureCanvasTkAgg(self.fig, self.root)
		self.plotCanvas.get_tk_widget().grid(row = 2, columnspan = 5)
		self.plotCanvas.draw()

		# create a prompt label with related varible
		self.prompt = StringVar()
		self.prompt.set('Select function to perform from options at the top of the window')
		Label(self.root, textvariable = self.prompt).grid(row = 3, columnspan = 5)


		# set class variables
		self.directory = '~'
		self.filename = ''
		self.routine = None
		self.chiplot = None
		self.centerErrorRange = centerErrorRange
		self.reflectionPairs = 2
		self.validCenter = 0
		self.smooth = 'spline'
		self.zoommin = zoomMin
		self.basemove = basemove
		self.logfile = None
		self.leftChiplot = None
		self.rightChiplot = None
		self.bakChiplot = None


		# launch application to run mode
		self.root.mainloop()

	def openChiplot(self):
		"""loads chiplot from file into the GUI"""

		#Testing
		# ask user for file
		if(self.filename == ''):
			self.side=''
			self.filename = tkinter.filedialog.askopenfilename(initialdir = '~', title = 'Chiplot Splitter: Please select a chiplot')
		else:
			self.filename = tkinter.filedialog.askopenfilename(initialfile = self.filename, title = 'Chiplot Splitter: Please select a chiplot')
		if(self.filename == ''):
			dlog('Error: No file selected', 'l')
			return -1

		(self.directory, displayName)=os.path.split(self.filename)
		displayTitle = 'Chiplot Splitter: '+displayName
		self.root.title(displayTitle)
		if(self.chiplot != None):
			del self.chiplot

		# create new chiplot and load data
		self.chiplot = Chiplot(list(), list())
		if(self.chiplot.loadFile(self.filename) < 0):
			dlog('Error: Unsucessful load of chiplot to variables')
			return -2
		dlog('Closing File\n', 'l')
		dlog('Opening File: '+self.filename, 'l')
		if(self.chiplot.points < 2):
			dlog('Error: Unsucessful load of chiplot to variables')
			return -2
		return 0

	def setTitle(self):
		(self.directory, displayName)=os.path.split(self.chiplot.filename)
		displayTitle = 'Chiplot Splitter: '+displayName
		self.root.title(displayTitle)

	def splitNew(self):
		"""initiates the splitting of a new Chiplot"""
		dlog('in split new', 'd')
		self.grabData()
		if(self.openChiplot() < 0):
			dlog('Error: Could not open chiplot for spliting','l')
			return
		self.reapRoutine()
		self.setTitle()
		self.routine = Splitter(self.chiplot, self.root, self.plotCanvas, self.fig, self.prompt, self.leftBgButton, self.rightBgButton, self.centerErrorRange, self.reflectionPairs, self.validCenter)
		self.routine.displayPlot()
		# at this point Splitter will take over


	def subNew(self):
		"""initiates the background subtraction of a new Chiplot"""
		dlog('in sub new', 'd')
		self.grabData()
		if(self.openChiplot() < 0):
			dlog('Error: Could not open chiplot for background subtraction','l')
			return
		self.reapRoutine()
		self.leftBgButton.config(state = DISABLED)
		self.rightBgButton.config(state = DISABLED)
		self.sub()
		#self.reapRoutine()

	def subLeft(self):
		"""Initiates the background subtraction of the left current chiplot"""

		dlog('in sub curr', 'd')
		self.grabData()
		if(self.leftChiplot == None):
			dlog('Error: Could not open left chiplot for background subtraction','l')
			return
		self.reapRoutine()
		self.chiplot = self.leftChiplot
		self.sub()

	def subRight(self):
		"""Initiates the background subtraction of the right current chiplot"""

		dlog('in sub curr', 'd')
		self.grabData()
		if(self.rightChiplot == None):
			dlog('Error: Could not open right chiplot for background subtraction','l')
			return
		self.reapRoutine()
		self.chiplot = self.rightChiplot
		self.sub()

	def sub(self):
		"""Initiates the actual subtraction"""
		dlog('subtraction is happening', 'd')
		self.setTitle()
		self.routine = BackgroundSub(self.chiplot, self.root, self.plotCanvas, self.fig, self.prompt, self.currCentButton, self.smooth)
		self.routine.displayPlot()
		# at this point BackgroundSub will take over

	def centCurr(self):
		"""Initiates the analysis of the point on the current chiplot"""
		dlog('in centroid curr', 'd')
		self.grabData()
		if(self.bakChiplot == None):
			dlog('Error: chiplot was not set prior','l')
			return
		self.reapRoutine()
		self.chiplot = self.bakChiplot
		self.cent()


	def centNew(self):
		"""initiates the background subtraction of a new Chiplot"""
		dlog('in centroid new', 'd')
		self.grabData()
		if(self.openChiplot() < 0):
			dlog('Error: Could not open chiplot for background subtraction','l')
			return
		self.reapRoutine()
		self.leftBgButton.config(state = DISABLED)
		self.rightBgButton.config(state = DISABLED)
		self.cent()

	def cent(self):
		self.setTitle()
		self.routine = Centroid(self.chiplot, self.root, self.plotCanvas, self.fig, self.prompt, self.zoommin, self.basemove, self.logfile)
		self.routine.displayPlot()
		# at this point Centroid will take over

	def exit(self):
		"""cleans up objects and closes files before exiting"""
		try:
			if self.routine.__class__.__name__ == 'Centroid':
				self.logfile = self.routine.logfile
		except AttributeError:
			sys.exit()
		if self.logfile != None:
			self.logfile.write('\nclosing chiplot analyze\n\n')
			self.logfile.close()
		sys.exit()

	def grabData(self):
		if self.routine == None:
			return

		if self.routine.__class__.__name__ == 'Splitter':
			self.leftChiplot = self.routine.leftChi
			self.rightChiplot = self.routine.rightChi

		if self.routine.__class__.__name__ == 'BackgroundSub':
			self.bakChiplot = self.routine.workingChiplot

	def reapRoutine(self):
		"""cleans up the routine and gathers useful information from it before destroying it"""
		if self.routine == None:
			return
		dlog('routine is a '+self.routine.__class__.__name__)
		# gather information from splitter
		if self.routine.__class__.__name__ == 'Splitter':
			self.reflectionPairs = int(self.routine.reflections.get())
			self.validCenter = int(self.routine.validcenter.get())
		# gather information from BackgroundSub
		if self.routine.__class__.__name__ == 'BackgroundSub':
			self.smooth = self.routine.smoothFunction.get()
		# gather information from centroid
		if self.routine.__class__.__name__ == 'Centroid':
			self.logfile = self.routine.logfile

		self.routine.clean()
		del self.routine


# actual code to run...
def usage():
	print('''Chiplot Analyze: a Tkinter GUI program used to analyze
	chiplots made from fit2D's projection routine
	required python packages = Tkinter, matplotlib,
		and all their dependencies
	simply run the program from the commanline and
	preset values should work, to customize preset
	values use the following command line arguments:
		-h or --help -> this screen
		-c or --centerErrorRange -> set the maximum
			error range allowed when calculating the
			center peak while splitting chiplots
		-z or --zoomMin -> sets the smallest zoom
			scale while zooming chiplots (in pixels)
		-b or --baseMove -> sets the movement of the
			baseline when pressing the up and down
			keys in the peak analyzation routine
		-s or --size -> sets the default size of the
			graph, useful when displaying on smaller or
			larger screens''')

global _debug
_debug = 0
setDebug(_debug)
centerErrorRange = 10.0
zoomMin = 50
basemove = 0.01
width = 8
height = 4
# process arguments
try:
	opts, args = getopt.getopt(sys.argv[1:], "hc:dz:b:s:", ["help", "centerErrorRange="])
except getopt.GetoptError:
	usage()
	sys.exit(2)
for opt, arg in opts:
	if opt in ("-h", "--help"):
		usage()
		sys.exit()
	elif opt == '-d':
		_debug = 1
		setDebug(_debug)
	elif opt in ("-c", "--centerErrorRange"):
		centerErrorRange = float(arg)
	elif opt in ("-z", "--zoomMin"):
		zoomMin = float(arg)
	elif opt in ("-b", "--baseMove"):
		basemove = float(arg)
	elif opt in ("-s", "--size"):
		sizes = arg.split(',', 2)
		width = int(sizes[0])/100
		height = int(sizes[1])/100


# then run the main class
main = mainClass(width, height, centerErrorRange, zoomMin, basemove)
