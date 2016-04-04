#
# Copyright: Julian Schutsch 2014
#
# Calculate and store ahmed body forces and momentum for a range of conditions

import os
import sys
sys.path.append(os.path.join(".."))

import math
import argumentparser
print(sys.path)
import foamcoefficients.database as database

settings = argumentparser.parseArguments()

rootPath =  os.path.join(os.getcwd(),"..", "foamCase")

db = database.CoefficientDatabase(os.path.join("..", "foam.db"))
for vehicleSpeed in settings.vehicleSpeeds:
    for windAngle in settings.windAngles:
        for windSpeed in settings.windSpeeds:
            db.calculateAndStore(vehicleSpeed, windSpeed, windAngle, rootPath)

for vs, ws, wa, F, M in db.iterate():
    print(vs, ws, wa, F, M)
