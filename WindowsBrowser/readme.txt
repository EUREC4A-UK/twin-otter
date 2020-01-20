This is an exe for windows to browse netcdfs. It can plot the data (any variable against any other variable), export plots as images and export data as csv.

I wrote it to browse FAAM data. I have tested it on a 1 Hz Twin Otter file and it worked.
It will probably crash if all variables in a file are not the same length
It can't properly deal with variables with more than 1 dimension - it flattens them to 1D then they will probaly end up different lengths and cause a crash.
It probably crashes if you try to load a second file - open a new instance instead
It probably crashes if using NetCDF4 (non classic).
It crashes if the two files included in the installation are not in the same directory.

It is far from perfect. I lost the source many years ago so I can't modify it. If you are using Linux (or even on Windows), you may find there are much better tools. This is just here in case it is useful.

To install simply save the 2 files (CPToolBox.exe and plxtnd5.fnt) in any directory - they must be together.

To run double click CPToolBox.exe

To load a file use File -> Open NetCDF

To plot variables go to Plot -> New Plot
On the traces tab things are pretty obvious, use the add, remove and edit buttons as you would expect
On the Axes tab, set the axis limits or hit the span all button
***NOTE*** the span all button does not filter fill values so may go a bit crazy

To edit a created plot use Plot -> Plot properties, you get the same options as when you create a plot

To save a plot as an image got to Plot -> Export Plot

To export data as csv for eay import to excel or something, go to File -> Export as csv
