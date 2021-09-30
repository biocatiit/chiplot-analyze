# basic imports
from chiplot_analyze.dlog import dlog
from chiplot_analyze.chiplot import Chiplot
import tkinter.filedialog, os

def convexHull(chiplot):
	"""method that computes the convex hull of the given chiplot within
	 the bounds and returns two list objects the first, xdata and
	the second ydata for the convex hull points"""
	dlog('in convexHull')
	xhull = list()
	yhull = list()
	
	# the first point is always the start of the convex hull
	xhull.append(chiplot.xdata[0])
	yhull.append(chiplot.ydata[0])
	lasthullindex = 0
	
	points = len(chiplot.ydata)
	
	# Here is the actual algorithm!
	while(lasthullindex < points - 1):
		slope = (chiplot.ydata[lasthullindex+1]-chiplot.ydata[lasthullindex])/(chiplot.xdata[lasthullindex+1]-chiplot.xdata[lasthullindex])
		dlog('slope: '+str(slope))
		currenthullindex = lasthullindex+1
		currenthully = chiplot.ydata[lasthullindex]
		dlog('last hull point: '+str(chiplot.xdata[lasthullindex])+','+str(chiplot.ydata[lasthullindex]))
		
		for i in range(currenthullindex + 1, points):
			extrapolation = currenthully + slope*(chiplot.xdata[i]-chiplot.xdata[lasthullindex])
			if chiplot.ydata[i] < extrapolation:
				dlog('computing slope with new point: '+str(chiplot.xdata[i])+','+str(chiplot.ydata[i]))
				slope = ((chiplot.ydata[i]-chiplot.ydata[lasthullindex])/(chiplot.xdata[i]-chiplot.xdata[lasthullindex]))
				dlog('slope: '+str(slope))
				currenthullindex = i
		
		# Store the hull points to be used for a spline fit
		xhull.append(chiplot.xdata[currenthullindex])
		yhull.append(chiplot.ydata[currenthullindex])
		lasthullindex = currenthullindex
	
	return xhull, yhull

def outputHull(xhull, yhull, filename):
	"""outputs the two lists in a csv format"""
	dlog('in output hull of convex hull')
	hullfilename = tkinter.filedialog.asksaveasfilename(initialdir = os.path.dirname(filename), initialfile = os.path.basename(filename)+'.hull', title = 'Convex Hull Points')
	if hullfilename == '':
		return 0
	wfile = open( hullfilename, "w")
	if wfile == None:
		dlog('Invalid file to write to: '+hullfilename, 'l')
		return -1
	wfile.write('Convex Hull of '+filename+'\n')
	wfile.write('Points: '+str(len(yhull))+'\n')
	wfile.write('X,Y\n')
	for i in range(0,len(yhull)):
		wfile.write(('%.7e' % xhull[i])+','+('%.7e' % yhull[i])+'\n')
	wfile.close()
	dlog('Wrote chiplot to file: '+hullfilename, 'l')
	del wfile
	return 0
	
