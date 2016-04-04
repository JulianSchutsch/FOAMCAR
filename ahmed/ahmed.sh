#!/bin/sh

rm ahmed.g
mged -c ahmed.g "source ahmed.script"
g-stl -a 0.01 -o ahmed_mm.stl ahmed.g ahmed.c
surfaceConvert ahmed_mm.stl ahmed_m.stl -clean -scale 0.001
