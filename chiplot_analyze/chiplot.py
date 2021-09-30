# basic imports
import re
from .dlog import dlog

class Chiplot:
	def __init__(self, xdata = list(), ydata = list(), filename = None, projection = ''):
		"""initialization routine for Chiplot, sets class variables"""
		dlog('in chiplot initialization')
		self.xdata = xdata
		self.ydata = ydata
		self.xmax = None
		self.ymax = None
		self.xmin = None
		self.ymin = None
		self.increment = 0
		self.filename = filename
		self.smv = ''
		self.points = 0
		self.projection = projection
		
		# process data if given
		lastx = -1
		increment = 0
		dlog('len of x'+str(len(xdata)))
		dlog('len of y'+str(len(ydata)))
		
		for i in range(0,len(ydata)):
			if(self.xmax == None):
				self.xmax = xdata[i]
				self.xmin = xdata[i]
				self.ymax = ydata[i]
				self.ymin = ydata[i]
			# determine ranges for axes
			if( xdata[i] > self.xmax):
				self.xmax = xdata[i]
			elif( xdata[i] < self.xmin):
				self.xmin = xdata[i]
			if( ydata[i] > self.ymax):
				self.ymax = ydata[i]
			elif( ydata[i] < self.ymin):
				self.ymin = ydata[i]
			
			# make sure that the chiplot increments steadily upward or downward
			if(xdata[i] < lastx and increment > 0):
				dlog('Error: Chiplot does not increment its data points normally', 'l')
			elif(xdata[i] > lastx and increment < 0):
				dlog('Error: Chiplot does not increment its data points normally', 'l')
			elif(lastx != -1 and increment == 0):
				increment = xdata[i] - lastx
				dlog('incrementing by: '+str(increment), 'd')
			
			lastx = xdata[i]
			# add point to storage
			self.points = self.points + 1
	
	def loadFile(self, filename):
		debug = 'loading '+filename+' from Chiplot.loadFile'
		dlog(debug, 'd')
		chifile = open(filename, "r")
		if chifile == None:
			dlog("Invalid file", 'l')
			return -1
		
		self.filename = filename
		
		chire = re.compile("([0-9\-+.eE:]+),*\s+([0-9\-+.eE:]+)")
		
		lastx = -1
		increment = 0
		
		self.projection = chifile.readline()
		
		# read in file and parse the plot data
		for line in chifile.readlines():
			tupleMatch = chire.search(line)
			#fixing weird colon error
			#xBeg = tupleMatch.group(1).split(':')[0]
			#xEnd = tupleMatch.group(1).split(':')[1]			
			#if xBeg[len(xBeg)-1]=="."
				
			#xFull = xBeg+"0"+xEnd
			
			if(tupleMatch == None):
				continue
			try:
				xfloat = float(tupleMatch.group(1))  #change this
				yfloat = float(tupleMatch.group(2))
			except ValueError:
				dlog('unable to process chiplot, unknown value type for tuples')
				return -2
			if(self.xmax == None):
				self.xmax = xfloat
				self.xmin = xfloat
				self.ymax = yfloat
				self.ymin = yfloat
			
			# determine ranges for axes
			if( xfloat > self.xmax):
				self.xmax = xfloat
			elif( xfloat < self.xmin):
				self.xmin = xfloat
			if( yfloat > self.ymax):
				self.ymax = yfloat
			elif( yfloat < self.ymin):
				self.ymin = yfloat
			
			# make sure that the chiplot increments steadily upward or downward
			if(xfloat < lastx and increment > 0):
				dlog('Error: Chiplot does not increment its data points normally', 'l')
			elif(xfloat > lastx and increment < 0):
				dlog('Error: Chiplot does not increment its data points normally', 'l')
			elif(lastx != -1 and increment == 0):
				increment = xfloat - lastx
				dlog('incrementing by: '+str(increment), 'd')
			
			lastx = xfloat
			# add point to storage
			self.xdata.append(xfloat)
			self.ydata.append(yfloat)
			self.points = self.points + 1
			
		self.increment = increment
		#if the x values are decrementing, reverse the list
		if self.increment < 0:
			self.xdata.reverse()			
		log = 'loaded '+str(self.points)+' points from file into chiplot data'
		dlog(log, 'l')
		chifile.close()
		del chifile
		return 0
	
	def writeFile(self, resetX = False, extension = '', filename = None):
		dlog('entering writeFile of Chiplot')
		dlog('xdata[0]'+str(self.xdata[0]))
		if(filename == None):
			filename = self.filename
		if(filename == None):
			dlog('Error: could not write to a null file', 'l')
			return -1
		writeFile = filename + extension
		wfile = open( writeFile, "w")
		if wfile == None:
			dlog('Invalid file to write to: '+writeFile, 'l')
			return -1
		wfile.write(self.projection)
		wfile.write('Pixels\n')
		wfile.write('Intensity\n')
		wfile.write('\t'+str(self.points)+'\n')
		xval = self.xdata
		#loop that resets x
		#if resetX == True:
			#xval = range(0,len(self.ydata))
		#change this ^^
		for i in range(0,len(self.ydata)):
			wfile.write(' '+('%.7e' % xval[i])+'  '+('%.7e' % self.ydata[i])+'\n')
		wfile.close()
		dlog('Wrote chiplot to file: '+writeFile, 'l')
		del wfile
		return 0
		
	def average(self):
		dlog('averaging the ydata of the chiplot')
		ytotal = 0
		for ypoint in self.ydata:
			ytotal += ypoint
		return ytotal/float(len(self.ydata))
