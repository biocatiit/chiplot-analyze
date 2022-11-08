# basic imports
from tkinter import *
import os, tkinter.filedialog
from chiplot_analyze.dlog import dlog
from chiplot_analyze.chiplot import Chiplot
from .convhull import convexHull, outputHull
from .spline import splineChiplot
from .pchip import pchipChiplot

class BackgroundSub:
	def __init__(self, chiplot, window, canvas, fig, prompt, centButton, smooth = 'spline'):
		"""initialization routine for background subtract, sets class
		variables and prompts user on what he or she should do"""
		dlog('in background subtract initialization')
		dlog('Running Background Subtraction Routine')
		# drawing variables
		self.chiplot = chiplot
		self.workingChiplot = None
		self.fig = fig
		self.prompt = prompt
		self.canvas = canvas
		self.add = None
		self.connect = None
		self.dialogWindow = None
		# control variables
		self.smoothFunction = StringVar()
		self.smoothFunction.set(str(smooth))
		# calculation variables
		self.leftedge = None
		self.rightedge = None
		self.xhull = None
		self.yhull = None
		self.xsmooth = None
		self.ysmooth = None
		self.peaks = list()
		self.centButton = centButton 
		self.zoomed = 0
		# create the application specific controls
		self.controls = list()
		clearButton = Button(window, text = "Reset (clear)", command = self.clear)
		self.controls.append(clearButton)
		clearButton.grid(row = 4, column = 0, sticky = W)
		
		peakButton = Button(window, text = "Eliminate Peaks", command = self.peakElim, state = DISABLED)
		self.controls.append(peakButton)
		peakButton.grid(row = 4, column = 1, sticky = W)
		
		hullButton = Button(window, text = "ConvexHull", command = self.hull, state = DISABLED)
		self.controls.append(hullButton)
		hullButton.grid(row = 4, column = 2, sticky = W)
		
		smoothButton = Button(window, text = "Smooth", command = self.smooth, state = DISABLED)
		self.controls.append(smoothButton)
		smoothButton.grid(row = 4, column = 3, sticky = W)
		
		subtractButton = Button(window, text = "Subtract", command = self.subtract, state = DISABLED)
		self.controls.append(subtractButton)
		subtractButton.grid(row = 4, column = 4, sticky = W)
		
		smoothPrompt = Label(window, text = 'Choose the smoothing type:')
		self.controls.append(smoothPrompt)
		smoothPrompt.grid(row = 5, column = 0, sticky = W)
		
		splineRadio = Radiobutton(window, variable = self.smoothFunction, value = 'spline', text = 'spline')
		self.controls.append(splineRadio)
		splineRadio.grid(row = 5, column = 1, sticky = W)
		
		testRadio = Radiobutton(window, variable = self.smoothFunction, value = 'pchip', text = 'pchip')
		self.controls.append(testRadio)
		testRadio.grid(row = 5, column = 2, sticky = W)
		# save some for setting active state
		self.smoothButton = smoothButton
		self.subtractButton = subtractButton
		self.hullButton = hullButton
		self.peakButton = peakButton

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
		dlog('in display plot of Background Subtract')
		if(self.add == None):
			self.add=self.fig.add_subplot(111)
			#will need change.
		self.add.plot(self.chiplot.xdata, self.chiplot.ydata)
		self.canvas.draw()
		if(self.connect == None):
			self.connect = self.canvas.mpl_connect('button_press_event', self.mouseSetEdges)
		self.prompt.set('Select the left and right edges of the chiplot to use in the convex hull program\nThen eliminate negative peaks using the command below or run the convex hull algorithm')
	
	def clear(self):
		dlog('in BackgroundSub.clear')
		self.add.cla()
		if self.dialogWindow != None:
			self.dialogWindow.destroy()
			self.dialogWindow = None
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
			self.connect = None
		self.workingChiplot = None
		self.leftedge = None
		self.rightedge = None
		self.xhull = None
		self.yhull = None
		self.xsmooth = None
		self.ysmooth = None
		self.peaks = list()
		self.zoomed = 0
		self.smoothButton.config(state = DISABLED)
		self.subtractButton.config(state = DISABLED)
		self.hullButton.config(text = 'ConvexHull', command = self.hull, state = DISABLED)
		self.peakButton.config(state = DISABLED)
		self.displayPlot()
	
	def mouseSetEdges(self, event):
		"""method used to capture mouse events from plot"""
		# capture click data and draw dot for user feedback
		if event.xdata == None:
			return
		dlog(str(event.xdata))
		if(self.add == None):
			dlog('Error: BGSub has no subplot to draw to')
			return
		if self.leftedge == None:
			self.leftedge = event.xdata
		elif self.rightedge == None:
			if self.leftedge < event.xdata:
				self.rightedge = event.xdata
			else:
				self.rightedge = self.leftedge
				self.leftedge = event.xdata
			self.hullButton.config(state = NORMAL)
			self.peakButton.config(state = NORMAL)
		else:
			middle = (self.leftedge+self.rightedge)/2
			if event.xdata < middle:
				self.leftedge = event.xdata
			elif event.xdata > middle:
				self.rightedge = event.xdata
		if self.leftedge < 1:
			self.leftedge = 1
		self.add.cla()
		self.add.plot(self.chiplot.xdata, self.chiplot.ydata)
		self.add.plot([self.leftedge,self.leftedge], [self.chiplot.ymin, self.chiplot.ymax], color = 'r')
		if self.rightedge != None:
			self.add.plot([self.rightedge,self.rightedge], [self.chiplot.ymin, self.chiplot.ymax], color = 'r')
		self.canvas.draw()
	
	def hull(self):
		"""computes the convex hull of the chiplot"""
		dlog('in hull of Background Subtract')
		dlog('Computing Convex Hull of Chiplot', 'l')
		if(self.rightedge == None):
			dlog('Unable to process convex hull, a left and right boundary are needed')
			return
		self.smoothButton.config(state = NORMAL)
		self.subtractButton.config(state = NORMAL)
		self.hullButton.config(text = 'Output Hull', state = NORMAL, command = self.outputHull)
		self.peakButton.config(state = DISABLED)
		if(self.connect != None):
			self.canvas.mpl_disconnect(self.connect)
		self.connect = self.canvas.mpl_connect('button_press_event', self.zoom)

		# create a new chiplot to find the convex hull of
		lower = self.leftedge
		upper = self.rightedge
		for i in range(0, len(self.chiplot.xdata)):
			if((self.chiplot.xdata[i] < lower) and (self.chiplot.xdata[i+1] > lower)):
				lower = self.chiplot.xdata[i]
			if((self.chiplot.xdata[i] < upper) and (self.chiplot.xdata[i+1] > upper)):
				upper = self.chiplot.xdata[i]
		left = self.chiplot.xdata.index(lower)
		right = self.chiplot.xdata.index(upper)
		dlog('Utilizing chiplot points between '+str(self.chiplot.xdata[left])+' and '+str(self.chiplot.xdata[right]), 'l')
		hullxplot = self.chiplot.xdata[left:right]
		hullyplot = self.chiplot.ydata[left:right]
		# blot out the large peaks
		for i in range(0,len(self.peaks)//2-1):
			lower = self.peaks[i*2]
			upper = self.peaks[i*2+1]
			for i in range(0, len(self.chiplot.xdata)):
				if((self.chiplot.xdata[i] < lower) and (self.chiplot.xdata[i+1] > lower)):
					lower = self.chiplot.xdata[i]
				if((self.chiplot.xdata[i] < upper) and (self.chiplot.xdata[i+1] > upper)):
					upper = self.chiplot.xdata[i]
			lower = self.chiplot.xdata.index(lower)
			upper = self.chiplot.xdata.index(upper)
			dlog('blotting out '+str(lower)+' to '+str(upper))
			lowerpeak = lower - left
			upperpeak = upper - left
			dlog('Removing points between '+str(hullyplot[lowerpeak])+' and '+str(hullyplot[upperpeak])+' because of large negative peak', 'l')
			sety = hullyplot[lowerpeak]
			hullyplot[lowerpeak:upperpeak] = [sety]*(upperpeak-lowerpeak)
		hullChiplot = Chiplot(hullxplot, hullyplot)
		
		self.workingChiplot = Chiplot(self.chiplot.xdata[left:right], self.chiplot.ydata[left:right])
		
		self.xhull, self.yhull = convexHull(hullChiplot)
		self.add.cla()
		self.add.plot(self.workingChiplot.xdata, self.workingChiplot.ydata)
		self.add.plot(self.xhull, self.yhull, color = 'r')
		self.canvas.draw()
		
	def zoom(self, event):
		if self.zoomed == 0:
			self.zoomIn(event)
			self.zoomed = 1
		else:
			self.zoomOut()
			self.zoomed = 0
		
	def zoomIn(self, event):	
		if event.xdata == None:
			return
		dlog(str(event.xdata))
		dlog("zooming in")
		if(self.add == None):
			dlog('Error: BGSub has no subplot to draw to')
			return
		
		lower = event.xdata
		for i in range(0, len(self.workingChiplot.xdata)):
			if((self.workingChiplot.xdata[i] < lower) and (self.workingChiplot.xdata[i+1] > lower)):
				lower = self.workingChiplot.xdata[i]
		clickIndex = self.workingChiplot.xdata.index(lower)
		
		leftIndex = clickIndex - 50
		rightIndex = clickIndex + 50
		if leftIndex < 0 or rightIndex >= len(self.workingChiplot.xdata):
			self.zoomed = 0
			return
		
		self.add.cla()
		self.add.plot(self.workingChiplot.xdata[leftIndex:rightIndex], self.workingChiplot.ydata[leftIndex:rightIndex])
		if(self.xsmooth != None):
			self.add.plot(self.xsmooth[leftIndex:rightIndex], self.ysmooth[leftIndex:rightIndex], color = 'g')
		self.canvas.draw()
	
		#get an upper and lower index by add/subtracting from the click point
		#want to clear the graph, (reference other code) 
		#after graph clear, use display/plot (.plot) and slice the working chiplot with upper/lower bound
		# if smooth isnt null, slice and display that.
		
	def zoomOut(self):
		dlog('zooming out')
		self.add.cla()
		self.add.plot(self.workingChiplot.xdata, self.workingChiplot.ydata)
		if(self.xsmooth != None):
			self.add.plot(self.xsmooth, self.ysmooth, color = 'g')
		if(self.xhull != None):
			self.add.plot(self.xhull, self.yhull, color = 'r')
		self.canvas.draw()	
		
	def peakElim(self, event = None):
		"""eliminates the peaks from the chiplot"""
		dlog('in peak eliminator of Background Subtract')
		if event == None:
			if(self.connect != None):
				self.canvas.mpl_disconnect(self.connect)
			self.connect = self.canvas.mpl_connect('button_press_event', self.peakElim)
			self.prompt.set('click to the left then right (order is important) of large negative peaks that would damage the convex hull\nWhen the large negative peaks have been removed run the convex hull algorithm')
			return
		if event.xdata == None:
			return
		dlog(str(event.xdata))
		self.peaks.append(event.xdata)
		if len(self.peaks) % 2 == 1:
			self.hullButton.config(state = DISABLED)
		else:
			self.hullButton.config(state = NORMAL)
		self.add.plot([event.xdata,event.xdata], [self.chiplot.ymin, self.chiplot.ymax], color = 'k')
		self.canvas.draw()
	
	
	def smooth(self):
		"""smooths the convex hull of the chiplot to a certain type of function"""
		dlog('in smooth of Background Subtract')
		dlog('using a '+self.smoothFunction.get()+' smoothing function')
		
		# call smoothing function
		if(self.smoothFunction.get() == 'spline'):
			self.xsmooth, self.ysmooth = splineChiplot(self.xhull, self.yhull, self.workingChiplot)
			dlog('Smoothing Convex Hull using a spline curve', 'l')
		if(self.smoothFunction.get() == 'pchip'):
			self.xsmooth, self.ysmooth = pchipChiplot(self.xhull, self.yhull, self.workingChiplot)
			dlog('Smoothing Convex Hull using a pchip curve', 'l')
		
		self.add.cla()
		self.add.plot(self.workingChiplot.xdata, self.workingChiplot.ydata)
		self.add.plot(self.xhull, self.yhull, color = 'r')
		self.add.plot(self.xsmooth, self.ysmooth, color = 'g')
		self.canvas.draw()
	
	def subtract(self):
		"""subtracts the computed background and outputs the file"""
		dlog('in subtract of Background Subtract')
		suby = list()
		self.smoothButton.config(state = DISABLED)
		self.subtractButton.config(state = DISABLED)
		
		if self.ysmooth != None:
			dlog('length of y data: '+str(len(self.workingChiplot.ydata)))
			# subtract a smoothed convex hull from chiplot
			dlog('subtracting smooth convex hull')
			for i in range (len(self.workingChiplot.ydata)):
				suby.append(self.workingChiplot.ydata[i] - self.ysmooth[i])
				
		else:
			# subtract the convex hull from the chiplot
			dlog('subtracting the convex hull')
			segmentlx = self.xhull[0]
			segmently = self.yhull[0]
			count = 0
			for i in range(1, len(self.yhull)):
				segmentrx = self.xhull[i]
				segmentry = self.yhull[i]
				leftindex = self.workingChiplot.xdata.index(segmentlx)
				dlog('leftindex: '+str(leftindex))
				rightindex = self.workingChiplot.xdata.index(segmentrx)
				dlog('rightindex: '+str(rightindex))
				slope = (float(segmently) - float(segmentry))/(float(leftindex) - float(rightindex))
				for i in range(leftindex,rightindex):
					suby.append(self.workingChiplot.ydata[i] - (segmently + slope*(i-leftindex)))
					# suby.append(segmently + slope*(i-leftindex))
				segmentlx = segmentrx
				segmently = segmentry
				 
		lower = self.leftedge
		for i in range(0, len(self.chiplot.xdata)):
			if((self.chiplot.xdata[i] < lower) and (self.chiplot.xdata[i+1] > lower)):
				lower = self.chiplot.xdata[i]
		self.leftedge = self.chiplot.xdata.index(lower)
				
		suby = [0]*int(self.leftedge) + suby
		del self.workingChiplot
		dlog('subtracted data lenght: '+str(len(suby)))
		self.workingChiplot = Chiplot(self.chiplot.xdata[:len(suby)],suby,self.chiplot.filename, self.chiplot.projection)
		self.add.cla()
		self.add.plot(self.workingChiplot.xdata, self.workingChiplot.ydata)
		self.canvas.draw()
		directory, filename = os.path.split(self.chiplot.filename)
		window=Toplevel()
		window.title("Output background subtracted chiplots")
		Label(window, text = 'Background Subtraction, verify the subtraction is what you want, if it needs to be redone, select Redo below\nOtherwise output files to custom or standard filenames:\nstandard file name: '+filename+'.bak').grid(row = 0, columnspan = 3)
		Button(window, text = "Redo", command = self.clear).grid(row = 2, column = 0, sticky = W)
		Button(window, text = "Standard", command = self.standardFiles).grid(row = 2, column = 1, sticky = E)
		Button(window, text = "Custom", command = self.customFiles).grid(row = 2, column = 2, sticky = W)
		# Label(window, text = '\n').grid(row = 3, column = 3)
		window.lift()
		self.centButton.config(state = NORMAL)
		self.dialogWindow = window
		
	def outputHull(self):
		"""outputs the hull datapoints"""
		dlog('in output hull of Background Subtract')
		if outputHull(self.xhull, self.yhull, self.chiplot.filename) < 0:
			dlog('Unable to output convex hull of chiplot: '+self.chiplot.filename, 'l')
			self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing convex hull of chiplot',
				"Convex hull successfully taken out but unable to output file correctly",
				'Unable to output convex hull of chiplot: '+self.chiplot.filename)
		else:
			dlog('Outputing Convex hull to '+self.chiplot.filename+'.hull')
		
	def standardFiles(self):
		self.dialogWindow.destroy()
		self.dialogWindow = None
		if self.workingChiplot.writeFile(False,'.bak') < 0:
			dlog('Unable to output background subtraction of chiplot: '+self.chiplot.filename, 'l')
			self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing background subtracted chiplots',
				"Chiplot's background successfully taken out but unable to output file correctly",
				'Unable to output subtracted chiplot: '+self.chiplot.filename)
		else:
			dlog('Outputing background subtraction to '+self.chiplot.filename+'.bak')
	
	def customFiles(self):
		filename = tkinter.filedialog.asksaveasfilename(initialdir = os.path.dirname(self.chiplot.filename), initialfile = os.path.basename(self.chiplot.filename)+'.bak', title = 'Background Subtracted Chiplot')
		if filename == '':
			return
		self.dialogWindow.destroy()
		self.dialogWindow = None
		if self.workingChiplot.writeFile(False, '', filename) < 0:
			dlog('Unable to output background subtraction of chiplot: '+self.chiplot.filename, 'l')
			self.dialogWindow = errorMessage(self.clear, self.ignoreError, 'Error outputing background subtracted chiplots',
				"Chiplot's background successfully taken out but unable to output file correctly",
				'Unable to output subtracted chiplot: '+self.chiplot.filename)
		else:
			dlog('Outputing background subtraction to '+filename)

	def ignoreError(self):
		self.dialogWindow.destroy()
		self.dialogWindow = None

