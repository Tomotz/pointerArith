This directory contains Python programs for performing program analysis.

Author: Shachar Itzhaky and Mooly Sagiv

Requirements:
1. Python 2.7 Interpreter freely available from http://www.python.org/
2. Graphwiz visualizing software freely available from http://www.graphviz.org/
3. Portable Network Graphics freely from http://www.libpng.org/pub/png/ (you can use other graphic interfaces, e.g. ps)

Programs
chaotic.py	The main Chaotic iteration algorithm
--------------------------------------------------------
cp_prog1.py	Constant Propagation Example 1 (the example from class with 2 fixedpoints)
cp_prog2.py	Constant Propagation Example 2
cp_one.py	Lattice definition for Constant Propagation with One Variable
-----------
aexp.py Formal Available Expression Lattice
ae_prog1.py Formal Available Expressions Example 1
ae_prog1.py Formal Available Expressions Example 2
-----------
pointsto.py PointsTo Lattice with Generic Transfer Functions
pt_prog1.py A Simple Example Program for PointsTo Analysis
pt_prog2.py The exammple from the ppt slides
