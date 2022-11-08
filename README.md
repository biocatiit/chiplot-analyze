# Chiplot-analyze
Chiplot-analyze is a utility program designed to take as input 1D traces of the integrated intensity along rectangular boxed shaped regions aligned along either the equator, the meridian, or along a layer line using the program  FIT2D (http://www.esrf.eu/computing/scientific/FIT2D/) and saved as “chiplot” files.  Chiplot files are an ASCIII format and are easily readable in various ways. What chiplot-analyze does is take one of these traces and splits into two halves containing symmetrical diffraction patterns from the left or right (if trace is from the equator or a layer line) or top and bottom (if trace is along the meridian). You can then subtract a continuous background for the trace  using a convex hull algorithm and save the background subtracted trace in a new file.  The background subtracted trace can then be input into various peak fitting programs for further analysis. In the Irving lab this is usually the Fityk program (http://fityk.nieto.pl/) which allows defining custom peak functions. The final thing chiplot-analyze can do is to calculate  the centroid and integrated of  user defined diffraction peaks and save the results to a file. The functionality of chiplot-analyze has been incorporated into the MuscleX package (https://github.com/biocatiit/musclex/wiki) which is a recommended replacement for chiplot-analyze.  It is provided as a legacy application for someone wishing to replicate earlier published work.

### For Linux
Install *pip* first if you have not. Also, [TkInter][1] is needed.
```
sudo apt-get install python-pip python-tk
```
Install *chiplot-analyze*.
```
sudo pip install chiplot-analyze
```

### For Windows
Install *chiplot-analyze*.
```
pip install chiplot-analyze
```

## Running
Simply run
```
chiplot-analyze
```
See [Readme.rst][2] for details.
Find sample input data [here][3].

[1]: https://wiki.python.org/moin/TkInter
[2]: https://github.com/biocatiit/chiplot-analyze/blob/master/README.rst
[3]: https://github.com/biocatiit/chiplot-analyze/tree/master/chiplot_analyze/sample