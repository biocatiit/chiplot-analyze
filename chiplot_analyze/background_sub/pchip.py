# general imports
from chiplot_analyze.dlog import dlog
from chiplot_analyze.chiplot import Chiplot
from pylab import fabs

def pchipChiplot(x, y, chiplot):
	"""Interpolates the set of given points with a spline function and returns
	the evaluation of this function at xpoints"""
	dlog('in pchip')
	# copy lists
	x = x[:]
	y = y[:]
	
	# Generate the Pchip from the convex hull
	pchipy = pchip(x, y, chiplot.xdata)
	dlog(str(len(chiplot.xdata))+','+str(len(pchipy)), 'd')
	

	return chiplot.xdata, pchipy

def sign(d):
	if d > 0:
		return 1
	if d == 0:
		return 0
	if d < 0:
		return -1
	dlog('Error in determining sign')
	return None

def pchip(x, y, u):
 	# calculate the first derivative at each section
	# there will be len(x)-1
	h = list()
	h0 = x[0]
	for h1 in x[1:]:
		h.append(h1-h0)
		h0 = h1
	
	delta = list()
	for i in range(len(h)):
		delta.append((y[i+1]-y[i])/h[i])
	
	d = list()
	d.append(pchipend(h[0], h[1], delta[0], delta[1]))
	for i in range(1,len(x)-1):
		d.append(pchipslopes(h[i-1], h[i], delta[i-1], delta[i]))
	
	d.append(pchipend(h[-1], h[-2], delta[-1], delta[-2]))

	# evaluate function
	pchipy = list()
	dlog('evaluating pchip')
	segmentlx = x[0]
	segmently = y[0]
	dlog(str(len(d))+','+str(len(delta))+','+str(len(h)))
	for i in range(len(delta)):
		dlog(str(i))
		segmentrx = x[i+1]
		segmentry = y[i+1]
		leftindex = u.index(segmentlx)
		rightindex = u.index(segmentrx)
		dlog(str(d[i])+','+str(delta[i])+','+str(d[i+1]))
		c = (3*delta[i] - 2*d[i] - d[i+1])/h[i]
		b = (d[i] - 2*delta[i] + d[i+1])/(h[i]**2)
		dfloat = d[i]
		for j in u[leftindex:rightindex]:
			j = j - u[leftindex]
			dlog('j: '+str(j))
			pchipy.append(segmently + j*(dfloat + j*(c + j*b)))
		segmentlx = segmentrx
		segmently = segmentry
	
	# append the last point
	pchipy.append(y[-1])
		
	return pchipy

def pchipslopes(hm, h, deltam, delta):
	# PCHIPSLOPES  Slopes for shape-preserving Hermite cubic
	# pchipslopes(h,delta) computes d(k) = P(x(k)).
	# 
	# Slopes at interior points
	# delta = diff(y)./diff(x).
	# d(k) = 0 if delta(k-1) and delta(k) have opposites
  #			signs or either is zero.
	# d(k) = weighted harmonic mean of delta(k-1) and
  #			delta(k) if they have the same sign.
	
	if sign(deltam)*sign(delta) > 0:
		w1 = 2*h + hm
		w2 = h + 2*hm
		return (w1+w2)/(w1/deltam + w2/delta)
	else:
		return 0.0

def pchipend(h1,h2,del1,del2):
	# Noncentered, shape-preserving, three-point formula.
	d = ((2*h1+h2)*del1 - h1*del2)/(h1+h2)
	if sign(d) != sign(del1):
		d = 0
	elif( sign(del1) != sign(del2)) and (abs(d) > abs(3*del1)):
		d = 3*del1
	return d
