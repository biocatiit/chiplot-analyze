# basic imports
from tkinter import *
import os, tkinter.filedialog
from chiplot_analyze.dlog import dlog, errorMessage
from chiplot_analyze.chiplot import Chiplot

class Splitter:
	def __init__(self, chiplot, window, canvas, fig, prompt, leftButton, rightButton, errorRange = 10.0, reflections = 2, center = 0):
		"""initialization routine for splitter, sets class variables and prompts
		user on what he or she should do"""
		dlog('in splitter initialization')
		dlog('Running Splitter Routine', 'l')
		# drawing variables
		self.chiplot = chiplot
		self.fig = fig
		self.prompt = prompt
		self.canvas = canvas
		self.add = None
		self.connect = None
		self.dialogWindow = None
		# control variables
		self.reflections = StringVar()
		self.reflections.set(str(reflections))
		self.validcenter = IntVar()
		self.validcenter.set(center)
		# calculation variables
		self.clicks = list()
		self.peaks = list()
		self.center = None
		self.errorRange = errorRange
		self.leftChi = None
		self.rightChi = None
		self.leftButton = leftButton
		self.rightButton = rightButton
		self.lxdata = list()
		self.rxdata = list()
		
		# create the application specific controls
		self.controls = list()
		clearButton = Button(window, text = "Reset (clear)", command = self.clear)
		self.controls.append(clearButton)
		clearButton.grid(row = 4, column = 0, sticky = W)
		splitButton = Button(window, text = "Split", command = self.split)
		self.controls.append(splitButton)
		splitButton.grid(row = 4, column = 1, sticky = W)
		reflectionLabel = Label(window, text = "Enter the number of reflection pairs used to split the chiplot:")
		self.controls.append(reflectionLabel)
		reflectionLabel.grid(row = 4, column = 2, sticky = E)
		reflectionsEntry = Entry(window, textvariable = self.reflections)
		self.controls.append(reflectionsEntry)
		reflectionsEntry.grid(row = 4, column = 3, sticky = W)
		centerCheck = Checkbutton(window, variable = self.validcenter, text = 'valid center peak')
		self.controls.append(centerCheck)
		centerCheck.grid(row = 4, column = 4, padx = 5, sticky = E)
		# hold onto special buttons
		self.splitbutton = splitButton
		
	
	def clean(self):
		dlog('reclaiming splitter object')
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
		dlog('in display plot of Splitter')
		if(self.add == None):
			self.add=self.fig.add_subplot(111)
			
		self.add.plot(self.chiplot.xdata, self.chiplot.ydata)
		self.canvas.draw()
		if(self.connect == None):
			self.connect = self.canvas.mpl_connect('button_press_event', self.mouseDown)
		self.prompt.set('Set the number of peaks, then define peaks by clicking to the right and left of them\nThe chiplot will automagically split when enough peaks have been selected, or you can select split from the commands below')
	
	def clear(self):
		dlog('in Splitter.clear')
		if(self.clicks != None):
			del self.clicks
		self.clicks = list()
		self.add.cla()
		if(self.peaks != None):
			del self.peaks
		self.peaks = list()
		self.center = None
		self.leftChi = None
		self.rightChi = None
		self.splitbutton.config(state = NORMAL)
		if self.dialogWindow != None:
			self.dialogWindow.destroy()
			self.dialogWindow = None
		self.displayPlot()
	
	def split(self):
		"""method that splits the chiplot"""
		dlog('in split method of Splitter')
		# gather peaks
		self.calcPeaks()
		
		# find center
		centers = list()
		peakIndexTop = len(self.peaks)-1
		for i in range(0,(len(self.peaks)+1)//2):
			centers.append((self.peaks[i] + self.peaks[peakIndexTop - i])/2.0)
		# calculate the range of the peak centers to determine
		if len(centers) == 0:
			return
		
		self.splitbutton.config(state = DISABLED)
		# if they generally agree
		lowercent = centers[0]
		uppercent = centers[0]
		self.center = centers[0]
		# average of the centers and determine range
		for cent in centers[1:]:
			self.center = self.center + cent
			if cent > uppercent:
				uppercent = cent
			if cent < lowercent:
				lowercent = cent
		self.center = self.center/float(len(centers))
		dlog(str(centers))
		dlog('Center range: '+str(uppercent-lowercent))
		dlog('Center of chiplot: '+str(self.center), 'l')
		errorString = ''
		if(uppercent - lowercent > self.errorRange):
			# Error splitting chiplot, values are to separate
			dlog('Error: chiplot center from given peak data are not uniform enough', 'l')
			errorString = '**Caution, the splitting routine found the selected reflections do not converge to a centralized point**'
		
		# clear old peaks and then display the new peaks found
		if(self.add == None):
			dlog('Error: Splitter has no subplot to draw to')
			return
		self.add.cla()
		self.displayPlot()
		self.canvas.mpl_disconnect(self.connect)
		self.connect = None
		for i in range(0, len(self.peaks)):
			x = self.peaks[i]
			y = self.chiplot.ydata[self.chiplot.xdata.index(x)]
			self.add.scatter([x], [y])
		# display calculated center
		self.add.plot([self.center, self.center], [self.chiplot.ymin, self.chiplot.ymax]) 
		self.prompt.set('The chiplot has been split, follow dialog box for output information\nCenter: '+str(self.center))
		self.canvas.draw()
		self.splitChiplot(errorString)
	
	def mouseDown(self, event):
		"""method used to capture mouse events from plot"""
		# capture click data and draw dot for user feedback
		if event.xdata == None:
			return
		self.clicks.append(event.xdata)
		log = 'click '+str(event.xdata)+":"+str(event.ydata)
		dlog(log, 'l')
		if(self.add == None):
			dlog('Error: Splitter has no subplot to draw to')
			return
		self.add.scatter([event.xdata], [event.ydata])
		self.canvas.draw()
		neededClicks = int(self.reflections.get())*2*2 + int(self.validcenter.get())*2
		if(len(self.clicks) == neededClicks ):
			self.split()
		
	
	def calcPeaks(self):
		# sort the clicks, and then find the average of the reflections
		self.clicks.sort()
		dlog(('calculating peaks, reflections and center: '+self.reflections.get()+' '+str(self.validcenter.get())))
		numPeaks = int(self.reflections.get())*2 + int(self.validcenter.get())
		if(len(self.clicks) < numPeaks*2):
			numPeaks = int(len(self.clicks)/2)
		dlog('num of peaks calculated: '+str(numPeaks))
		for i in range(0,numPeaks):
			lower = self.clicks[i*2]
			upper = self.clicks[i*2+1]
			self.peaks.append(self.findPeak(lower, upper))
		
	
	def findPeak(self, lower, upper):
		dlog('finding peak between: '+str(lower)+' and '+str(upper))
		for i in range(0, len(self.chiplot.xdata)):
			if((self.chiplot.xdata[i] < lower) and (self.chiplot.xdata[i+1] > lower)):
				lower = self.chiplot.xdata[i]
			if((self.chiplot.xdata[i] < upper) and (self.chiplot.xdata[i+1] > upper)):
				upper = self.chiplot.xdata[i]
		lowerIndex = self.chiplot.xdata.index(lower)
		upperIndex = self.chiplot.xdata.index(upper)
		peakdata = self.chiplot.ydata[lowerIndex+1:upperIndex]
		ymax = self.chiplot.ydata[lowerIndex]
		count = 0
		peak = 0
		for peaky in peakdata:
			count = count + 1
			if peaky > ymax:
				peak = count
				ymax = peaky
		dlog('Found peak at: '+str(peak + lowerIndex), 'l')
		dlog('Peak : '+str(self.chiplot.xdata[peak+lowerIndex]), 'l')
		return self.chiplot.xdata[peak + lowerIndex]
	
	def enableButtons(self):
		#enables global buttons
		self.leftButton.config(state = NORMAL)
		self.rightButton.config(state = NORMAL)
		
	def splitChiplot(self, error):
		# actually split the chiplot and write the halves to a file
		splitCenter = int(self.center)+1
		#rewrite lx data as to start from beginning going to center
		self.lxdata = list()
		dlog('self.center: '+str(self.center))
		i=0
		while(self.chiplot.xdata[i]<self.center): #Problem here - might work now
			holder = (self.center-self.chiplot.xdata[i])
			self.lxdata.append(holder)
			i=i+1
		lydata = self.chiplot.ydata[:i]
		self.lxdata.reverse()
		lydata.reverse()
		#changing rx data
		yIndex = i
		while(i<len(self.chiplot.xdata)):
			self.rxdata.append(self.chiplot.xdata[i]-self.center)
			i=i+1
		dlog('leng of rxdata, rydata: '+str(i)+' '+str(yIndex))
		self.leftChi = Chiplot(self.lxdata,lydata,self.chiplot.filename+"l", self.chiplot.projection)
		self.rightChi = Chiplot(self.rxdata,self.chiplot.ydata[yIndex:],self.chiplot.filename+"r", self.chiplot.projection)
		directory, filename = os.path.split(self.chiplot.filename)
		window = Toplevel()
		window.title("Output split chiplots")
		Label(window, text = 'Chiplot split, verify the split by the green line, if it needs to be redone, select Redo below\nOtherwise output files to custom or standard filenames:\nLeft standard: '+filename+'l.xy'+'\nRight standard: '+filename+'r.xy').grid(row = 0, columnspan = 3)
		Label(window, text = error, fg = '#f00').grid(row = 1, columnspan = 3)
		Button(window, text = "Redo", command = self.clear).grid(row = 2, column = 0, sticky = W)
		Button(window, text = "Standard", command = self.standardFiles).grid(row = 2, column = 1, sticky = E)
		Button(window, text = "Custom", command = self.customFiles).grid(row = 2, column = 2, sticky = W)
		# Label(window, text = '\n').grid(row = 3, column = 3)
		window.lift()
		self.enableButtons()
		self.dialogWindow = window

	def resetXSplit(self):
		#changes the x values for the two split graphs
		dlog('reset x in splitter','d')
		
		
	def standardFiles(self):
		self.dialogWindow.destroy()
		self.dialogWindow = None
		if self.leftChi.writeFile(True,'l.xy') < 0:
			dlog('Unable to output left side of chiplot: '+self.chiplot.filename, 'l')
			self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing split chiplots',
				'Chiplot split but unable to output files correctly',
				'Unable to output left side of chiplot: '+self.chiplot.filename)
			return
		if self.rightChi.writeFile(True,'r.xy') < 0:
			dlog('Unable to output right side of chiplot: '+self.chiplot.filename, 'l')
			self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing split chiplots',
				'Chiplot split but unable to output files correctly',
				'Unable to output right side of chiplot: '+self.chiplot.filename)
		dlog('Split chiplot into: '+self.chiplot.filename+'l.xy and '+self.chiplot.filename+'r.xy', 'l')
		
	
	def customFiles(self):
		filenamel = tkinter.filedialog.asksaveasfilename(initialdir = os.path.dirname(self.chiplot.filename), initialfile = os.path.basename(self.chiplot.filename)+'l.xy',title = 'Left Chiplot Split')
		if filenamel == '':
			return
		# destroy message box
		self.dialogWindow.destroy()
		self.dialogWindow = None
		if self.leftChi.writeFile(True, '', filenamel) < 0:
			dlog('Unable to output left side of chiplot: '+self.chiplot.filename, 'l')
			self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing split chiplots',
				'Chiplot split but unable to output files correctly',
				'Unable to output left side of chiplot: '+self.chiplot.filename)
			return
		filenamer = tkinter.filedialog.asksaveasfilename(initialdir = os.path.dirname(self.chiplot.filename), initialfile = os.path.basename(self.chiplot.filename)+'r.xy',title = 'Right Chiplot Split')
		if filenamer != '':
			if self.rightChi.writeFile(True, '', filenamer) == 0:
				dlog('Split chiplot into: '+filenamer+' and '+filenamel, 'l')
				return
		dlog('Unable to output right side of chiplot: '+self.chiplot.filename, 'l')
		self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing split chiplots',
			'Chiplot split but unable to output files correctly',
			'Unable to output right side of chiplot: '+self.chiplot.filename)
	

	def ignoreError(self):
		self.dialogWindow.destroy()
		self.dialogWindow = None
	

