# basic imports
from tkinter import *
import os, tkinter.filedialog, re
from chiplot_analyze.dlog import dlog
from chiplot_analyze.chiplot import Chiplot

class Centroid:
	def __init__(self, chiplot, window, canvas, fig, prompt, zoommin = 50, basemove = 50, logfile = None):
		"""initialization routine for centroid analyzation, sets class
		variables and prompts user on what he or she should do"""
		dlog('in background subtract initialization')
		dlog('Running Centroid Routine', 'l')
		# drawing variables
		self.chiplot = chiplot
		self.workingChiplot = chiplot
		self.fig = fig
		self.prompt = prompt
		self.canvas = canvas
		self.add = None
		self.connect = None
		self.dialogWindow = None
		self.zoommin = zoommin
		self.basemove = basemove
		self.logfile = logfile
		# control variables
		self.originalprompt = 'Select a command from the controls below'
		self.zoomdrag = None
		self.zoomstop = None
		self.setFunc = StringVar()
		self.setFunc.set('edges')
		self.keybaseline = None
		# calculation variables
		self.zoomstart = None
		self.zoomend = None
		self.leftedge = None
		self.rightedge = None
		self.baseline = None
		self.baselinevar = StringVar()
		self.baselinevar.set(str(-1))
		self.baselinevar.trace('w', self.setBaseline)
		self.area = None
		self.cent = None
		self.bool = 0
		
		# create the application specific controls
		self.controls = list()
		clearButton = Button(window, text = "Reset (clear)", command = self.clear)
		self.controls.append(clearButton)
		clearButton.grid(row = 4, column = 0, sticky = W)
		
		zoomButton = Button(window, text = "Zoom", command = self.zoom)
		self.controls.append(zoomButton)
		zoomButton.grid(row = 4, column = 1, sticky = W)
		
		analyzeButton = Button(window, text = "Analyze Peak", command = self.analyze)
		self.controls.append(analyzeButton)
		analyzeButton.grid(row = 4, column = 2, sticky = W)
		
		baselineEntry = Entry(window, textvariable = self.baselinevar, justify = RIGHT)
		self.controls.append(baselineEntry)
		baselineEntry.grid(row = 4, column = 3, sticky = W)
		
		baselinePrompt = Label(window, text = 'baseline')
		self.controls.append(baselinePrompt)
		baselinePrompt.grid(row = 4, column = 4, sticky = W)
		
		linePrompt = Label(window, text = 'Choose the line to adjust:')
		self.controls.append(linePrompt)
		linePrompt.grid(row = 5, column = 0, sticky = W)
		
		baseLineRadio = Radiobutton(window, variable = self.setFunc, value = 'baseline', text = 'baseline')
		self.controls.append(baseLineRadio)
		baseLineRadio.grid(row = 5, column = 2, sticky = W)
		
		edgesRadio = Radiobutton(window, variable = self.setFunc, value = 'edges', text = 'edges')
		self.controls.append(edgesRadio)
		edgesRadio.grid(row = 5, column = 1, sticky = W)
		# save some for setting active state
		self.zoomButton = zoomButton
		self.analyzeButton = analyzeButton
		self.clearButton = clearButton
		self.baselineEntry = baselineEntry
		self.baseLineRadio = baseLineRadio
		self.edgesRadio = edgesRadio
		self.linePrompt = linePrompt
		
		self.linePrompt.config(state = DISABLED)
		self.baseLineRadio.config(state = DISABLED)
		self.edgesRadio.config(state = DISABLED)

		
		# set logfile
		logre = re.compile("(.*)\.csv$")
		logfilename = ''
		while(self.logfile == None):
			dlog('setting logfile')
			#while(logre.search(str(logfilename))==None):
			logfilename = tkinter.filedialog.asksaveasfilename(initialdir = os.path.dirname(self.chiplot.filename), title = 'Peak Analyzation Logfile') ##
			dlog("logfile: "+str(logfilename)) ##
			if logfilename == '':
				dlog("logfilename equaled ''")
				continue 
			self.logfile = open( logfilename, "a")
			if self.logfile == None:
				dlog('Invalid file to write to: '+logfilename, 'l')
				continue
			self.logfile.write('filename,centroid of peak,area of peak\n')
		
		# initial prompt
		self.prompt.set(self.originalprompt)
		
	def clean(self):
		dlog('reclaiming centroid object')
		for control in self.controls:
			control.destroy()
			del control
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
		if self.dialogWindow != None:
			self.dialogWindow.destroy()
			del self.dialogWindow
		self.fig.clf()
	
	
	def displayPlot(self):
		"""creates a sub plot to display the chiplot and then links up the events"""
		dlog('in display plot of Background Subtract')
		if(self.add == None):
			self.add=self.fig.add_subplot(111)
		self.add.plot(self.workingChiplot.xdata, self.workingChiplot.ydata)
		if self.leftedge != None:
			self.add.plot([self.leftedge,self.leftedge], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'r')
		if self.rightedge != None:
			self.add.plot([self.rightedge,self.rightedge], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'r')
		if self.baseline != None:
			self.add.plot([self.workingChiplot.xmin,self.workingChiplot.xmax], [self.baseline, self.baseline], color = 'g')
		self.canvas.draw()
	
	def clear(self):
		dlog('in centroid.clear')
		self.add.cla()
		if self.dialogWindow != None:
			self.dialogWindow.destroy()
			self.dialogWindow = None
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
			self.connect = None
		if(self.zoomdrag != None):
			self.canvas.mpl_disconnect(self.zoomdrag)
			self.zoomdrag = None
		if(self.zoomstop != None):
			self.canvas.mpl_disconnect(self.zoomstop)
			self.zoomstop = None
		if(self.keybaseline != None):
			self.canvas.mpl_disconnect(self.keybaseline)
			self.keybaseline = None
		# reset class specific variables
		self.zoomstart = None
		self.zoomend = None
		self.workingChiplot = self.chiplot
		self.leftedge = None
		self.rightedge = None
		self.baseline = None
		self.area = None
		self.cent = None
		
		self.analyzeButton.config(text = "Analyze Peak", command = self.analyze, state = NORMAL)
		self.zoomButton.config(state = NORMAL)
		self.displayPlot()
		
	def analyze(self):
		dlog('in analyze')
		if(self.connect != None):
			dlog('UNABLE TO SET ANALYZE!\n')
			return
		self.baseLineRadio.config(state = NORMAL)
		self.edgesRadio.config(state = NORMAL)
		self.linePrompt.config(state = NORMAL)
		self.connect = self.canvas.mpl_connect('button_press_event', self.mouseSetEdges)
		self.keybaseline = self.canvas.mpl_connect('key_press_event', self.moveBaseline)
		self.analyzeButton.config(text = 'Run Analyze', command = self.runAnalyze, state = DISABLED)
		self.zoomButton.config(state = DISABLED)
		self.baseline = self.workingChiplot.average()
		self.baselinevar.set(str(self.baseline))
		self.prompt.set('select the right and left bounds of the peak and then use the up and down arrow keys to adjust the baseline of the peak\n when done, run the analyzation from the command below')
		self.add.cla()
		self.displayPlot()
	
		
	def mouseSetEdges(self, event):
		"""method used to capture mouse events from plot"""
		# capture click data and draw dot for user feedback
		if event.xdata == None:
			return
		dlog(str(event.xdata))
		
		if(self.add == None):
			dlog('Error: Centroid has no subplot to draw to')
			return
		
		if self.setFunc.get() == 'edges':
			if self.leftedge == None:
				self.leftedge = event.xdata
			elif self.rightedge == None:
				if self.leftedge < event.xdata:
					self.rightedge = event.xdata
				else:
					self.rightedge = self.leftedge
					self.leftedge = event.xdata
				self.analyzeButton.config(state = NORMAL)
			else:
				middle = (self.leftedge+self.rightedge)/2
				if event.xdata < middle:
					self.leftedge = event.xdata
				elif event.xdata > middle:
					self.rightedge = event.xdata
					
		if self.setFunc.get() == 'baseline':
			self.baseline = event.ydata
			self.baselinevar.set(str(self.baseline))
			
		self.add.cla()
		self.displayPlot()
		
	def moveBaseline(self, event):
		dlog('moving baseline')
		key = event.key
		self.basemove = max(self.workingChiplot.ydata)/100
		if (key == 'up'):
			self.baseline += self.basemove
		if (key=='down'):
			self.baseline -= self.basemove
		self.baselinevar.set(str(self.baseline))
		self.add.cla()
		dlog('focus change')
		self.displayPlot()
		
	def setBaseline(self, arg1 = None, arg2 = None, arg3 = None, arg4 = None, arg5 = None):
		dlog('in setbaseline')
		if self.baseline != None and self.baselinevar.get() != '':
			self.baseline = float(self.baselinevar.get())
			self.add.cla()
			self.displayPlot()
		
	def runAnalyze(self):
		dlog('in peak analyzation algorithm')
		# gather the peak points and pass them to the calculating functions
		x = list()
		y = list()
		low = self.rightedge
		high = self.leftedge
		for xpoint in self.workingChiplot.xdata:
			if xpoint < low and xpoint > self.leftedge:
				low = xpoint
			if xpoint > high and xpoint < self.rightedge:
				high = xpoint
		
		dlog('high: '+str(high)+' low: '+str(low))
		lowindex = self.workingChiplot.xdata.index(low)
		highindex = self.workingChiplot.xdata.index(high) + 1
		dlog('highindex: '+str(highindex)+' lowindex: '+str(lowindex))
		dlog('Analyzing Peak with bounds: '+str(low)+' lower x bound, '+str(high)+' upper x bound, and '+str(self.baseline)+' as a baseline')
		
		# run the actual algorithm here
		self.center(self.workingChiplot.xdata[lowindex:highindex], self.workingChiplot.ydata[lowindex:highindex])
		self.calcArea(self.workingChiplot.xdata[lowindex:highindex], self.workingChiplot.ydata[lowindex:highindex])
		
		self.logfile.write(self.chiplot.filename+','+str(self.cent)+','+str(self.area)+'\n')
		
		# draw the pretty green line
		self.add.cla()
		self.add.plot(self.workingChiplot.xdata, self.workingChiplot.ydata)
		self.add.plot([self.cent,self.cent], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'g')
		self.canvas.draw()
		# display info in the prompt
		if(self.cent == None):
			self.prompt.set('error, no points selected or the denominator of the peak is zero')
		
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
			self.connect = None
		if(self.keybaseline != None):
			self.canvas.mpl_disconnect(self.keybaseline)
			self.keybaseline = None
		self.analyzeButton.config(text = "Analyze Peak", command = self.analyze, state = NORMAL)
		self.clearButton.config(text = "Reset (Analyze New Peak)")
		self.prompt.set('Output to csv file successful, The Center of the peak is: '+str(self.cent)+'\nThe area of the peak is: '+str(self.area)+'\nselect a new function from up top or reset the current chiplot to run another peak analyzation')
		
	def center(self, x, y):
		dlog('in center')
		# calculate values to determine the centroid
		numerator = 0
		denominator = 0
		for xpoint, ypoint in zip(x, y):
			numerator += xpoint*ypoint
			denominator += ypoint
		
		if(denominator == 0):
			dlog('error, no points selected or the denominator of the peak is zero')
			return
		self.cent = numerator/denominator
		
		dlog('Center of selected point is '+str(self.cent), 'l')
		
	def calcArea(self, x, y):
		dlog('in area')
		"""Using Trapezoid rule for now to get a rough approximation of the size of the peak"""
		self.area = 0
		for i in range(1, len(y)):
			h = float(x[i] - x[i-1])
			self.area += (y[i]-self.baseline + y[i-1]-self.baseline)*h/2
		
		dlog("Area of peak centered at "+str(self.cent)+" is "+str(self.area)+" units squared", 'l')
		
	def zoom(self):
		dlog('In zoom')
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
		self.connect = self.canvas.mpl_connect('button_press_event', self.zoomdown)
		self.zoomButton.config(state = DISABLED)
		self.analyzeButton.config(state = DISABLED)
		self.prompt.set('Click the left and right boundaries of the area you would like to zoom in to')
	
	def zoomdown(self, event):
		"""method used to capture mouse events from plot"""
		# capture click data and draw dot for user feedback
		if event.xdata == None:
			return
		if(self.add == None):
			dlog('Error: Centroid has no subplot to draw to')
			return
		# set the start coords for the zooming regions
		if(self.zoomstart == None):
			self.zoomstart = event.xdata
			self.add.plot([self.zoomstart, self.zoomstart], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'r')

		else:
			self.zoomend = event.xdata
			self.add.plot([self.zoomend, self.zoomend], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'r')
			self.finishZoom(event)
		

		self.canvas.draw()
		
	def finishZoom(self, event):
			
		if(self.zoomend < self.zoomstart and self.zoomend != None):
			left = self.zoomend
			right = self.zoomstart
			
		else:
			left = self.zoomstart
			right = self.zoomend
			
		for i in range(0, len(self.chiplot.xdata)):
			if((self.chiplot.xdata[i] < left) and (self.chiplot.xdata[i+1] > left)):
				left = self.chiplot.xdata[i]
			if((self.chiplot.xdata[i] < right) and (self.chiplot.xdata[i+1] > right)):
				right = self.chiplot.xdata[i]
		dlog('left: '+str(left)+' self.zoomstart: '+str(self.zoomstart))
		left = self.chiplot.xdata.index(left)
		right = self.chiplot.xdata.index(right)
		self.workingChiplot = Chiplot(self.chiplot.xdata[left:right], self.chiplot.ydata[left:right])
		self.prompt.set(self.originalprompt)
		self.add.cla()
		self.zoomButton.config(state = NORMAL)
		self.analyzeButton.config(state = NORMAL)
		self.zoomClean(event)
		self.displayPlot()
	
	def zoomClean(self, event):
		if self.connect != None:
			self.canvas.mpl_disconnect(self.connect)
			self.connect = None
		self.zoomend = None
		self.zoomstart = None
		
	def zoommove(self, event):
		"""NOT USED method used to capture mouse events from plot"""
		# capture click data and draw dot for user feedback
		if event.xdata == None:
			return
		if(self.add == None):
			dlog('Error: Centroid has no subplot to draw to')
			return
		# set the start coords for the zooming regions
		self.zoomend = event.xdata
		self.add.cla()
		self.displayPlot()
		self.add.plot([self.zoomstart, self.zoomstart], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'r')
		self.add.plot([self.zoomend, self.zoomend], [self.workingChiplot.ymin, self.workingChiplot.ymax], color = 'r')
		self.canvas.draw()
		
	def zoomup(self, event):
		"""NOT USED method used to capture mouse events from plot"""
		# capture click data and draw dot for user feedback
		if event.xdata != None:
			self.zoomend = event.xdata
		if abs(self.zoomend - self.zoomstart) < self.zoommin:
			return
		if(self.add == None):
			dlog('Error: Centroid has no subplot to draw to')
			return
		# zoom in on the graph
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
			self.connect = None
		self.canvas.mpl_disconnect(self.zoomdrag)
		self.zoomdrag = None
		self.canvas.mpl_disconnect(self.zoomstop)
		self.zoomstop = None
		# create a new chiplot to find the convex hull of
		if(self.zoomstart < self.zoomend):
			left = int(self.zoomstart)
			right = int(self.zoomend)
		else:
			left = int(self.zoomend)
			right = int(self.zoomstart)
		self.workingChiplot = Chiplot(self.chiplot.xdata[left:right], self.chiplot.ydata[left:right])
		self.prompt.set(self.originalprompt)
		self.add.cla()
		self.zoomButton.config(state = NORMAL)
		self.analyzeButton.config(state = NORMAL)
		self.displayPlot()
