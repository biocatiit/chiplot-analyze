# general imports
from chiplot_analyze.dlog import dlog
from chiplot_analyze.chiplot import Chiplot
from pylab import fabs

def splineChiplot(x, y, chiplot):
	"""Interpolates the set of given points with a spline function and returns
	the evaluation of this function at xpoints"""
	dlog('in spline')
	spliney = list()
	# copy lists
	x = x[:]
	y = y[:]
	
	#Generate cubic spline from the hull points
	#But first, check the slopes of the last couple hull points to make sure noise doesn't screw things up
	slope=list()
	#find the slope between every hull point
	for i in range(0, len(x)-1):
		slope.append((y[i+1]-y[i])/(x[i+1]-x[i]))
		
	output="\n\n\nslope= "+str(slope)+"\n\n\n"
	dlog(output, 'd')
	#Find the location where the slope levels out
	#This ASSUMES the the plot is nearly flat until it reaches the central peak.
	i=len(slope)-1
	while(fabs(slope[i])>1.5*fabs(slope[i-2]) and fabs(slope[i])>0.005):
		i=i-1
		
	#i now contains the index of the first hull point that should be changed
	for j in range(i, len(x)):
		"""linearly extrapolate the last few hull points so they
			make a better spline"""
		y[j]=slope[i]*(x[j]-x[i])+y[i]
	
	dlog(str(y), 'd')
	
	# setup variables
	yref = 0.0 # return variable, spline code from fortran, needed to be passed by reference
	secondderiv = list() # the rest are the same, pass by reference
	firstderiv1 = 1E30
	firstderivN = 1E30
	cubicspline = spline(x, y, len(x), firstderiv1, firstderivN, secondderiv)
	dlog(str(cubicspline), 'd')
	
	# Create find the location of the spline at each data point     
	for xpoint in chiplot.xdata:
		interpolationpoint = splint(x, y, cubicspline, len(x), xpoint, yref)
		if interpolationpoint != 1E9:
			spliney.append(interpolationpoint)
		else:
			spliney.append(spliney[-1])
			dlog('error in interpolating data')
	dlog('len of x, y'+str(len(chiplot.xdata))+","+str(len(spliney)))
	return chiplot.xdata, spliney

def spline(x, y, N, firstderiv1, firstderivN, secondderiv):
	"""Given lists x and y of length N containing a tabulated function, and given values
		firstderiv1 and firstderiv2 for the first derivative of the interpolating function at
		points 1 and N, this routine returns a list secondderiv of length N which contains
		the second derrivatives of the interpolating function at the tabulated points x"""
	
	NMAX=100000		#Just a large number
	U=list()
	for i in range(0, N):
		secondderiv.append(0)
		U.append(0)
	if (firstderiv1>.99E30):
		secondderiv[0]=0
		U[0]=(0.0)
	else:
		secondderiv[0]=(-.5)
		U[0]=((3/(x[1]-x[0]))*((y[1]-y[0])/(x[1]-x[0])-firstderiv1))
	
	#Decomposition loop of the tridiagonal algorithm
	for i in range(1, N-1):
		sig=(x[i]-x[i-1])/(x[i+1]-x[i-1])
		p=sig*secondderiv[i-1]+2
		secondderiv[i]=((sig-1)/p)
		Ua = y[i+1] - y[i]
		Ub = x[i+1] - x[i]
		Uc = y[i] - y[i-1]
		Ud = x[i] - x[i-1]
		Ue = x[i+1] - x[i-1]
		U[i] = (6*(Ua/Ub - Uc/Ud)/Ue - sig*U[i-1])/p
	
	if (firstderivN>.99E30):
		QN=0.0
		UN=0.0
	else:
		QN=.5
		UN=(3/(x[N-1]-x[N-2]))*(firstderivN-(y[N-1]-y[N-2])/(x[N-1]-x[N-2]))
	
	secondderiv[N-1]=((UN-QN*U[N-2])*(QN*secondderiv[N-2]+1))
	for i in range(N-2, 0, -1):
		secondderiv[i]=secondderiv[i]*secondderiv[i+1]+U[i]
		
	return secondderiv
	
	
	
def splint(xa, ya, y2a, N, x, y):
	"""This function returns the cubic spline interpolated value for y at point x, given the 
		lists of points xa, ya and the output of spline y2a"""
		
	#use bisection to find the area around x	
	klo=1
	khi=N
	while (khi-klo>1):
		k=(khi+klo)//2
	#	print k
		if (xa[k]>x):
			khi=k
		else:
			klo=k
		
			
	if (khi>=len(xa)):
		return 1E9
	
	#klo and khi now bracket the input value of x
	h=xa[khi]-xa[klo]
	if (h==0):
		print("Bad input.  The xa's must be distinct")
	
	#now the cubic spline polynomial is evaluated
	A=(xa[khi]-x)/h
	B=(x-xa[klo])/h
	C=(pow(A, 3)-A)*pow(h, 2)/6.0
	D=(pow(B, 3)-B)*pow(h, 2)/6.0
	Y=A*ya[klo]+B*ya[khi]+C*y2a[klo]+D*y2a[khi]
	
	return Y
