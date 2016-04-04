#
# Copyright: Julian Schutsch 2014
#
# Argument parser

import argparse
import math

class Arguments:
    pass

class FailedParse(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason

def parseArguments():
    parser = argparse.ArgumentParser(description='Calculate force and torque using OpenFOAM.')

    parser.add_argument('--windAngles', type=float, nargs="*", help='Wind angles in multiples of math.pi')
    parser.add_argument('--vehicleSpeeds', type=float, nargs="*", help='Vehicle Speeds')
    parser.add_argument('--windSpeeds', type=float, nargs="*", help='Wind speeds')



    args = parser.parse_args()

    settings = Arguments()
    if not args.windAngles:
       settings.windAngles = [0, 0.1*math.pi, 0.2*math.pi, 0.3*math.pi, 0.4*math.pi, 0.5*math.pi, 0.6*math.pi, 0.7*math.pi, 0.8*math.pi, 0.9*math.pi, math.pi]
    else:
       settings.windAngles = [f*math.pi for f in args.windAngles]
    if not args.vehicleSpeeds:
       settings.vehicleSpeeds = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    else:
       settings.vehicleSpeeds = args.vehicleSpeeds
    if not args.windSpeeds:
       settings.windSpeeds = [0, 10, 20, 30, 40]
    else:
       settings.windSpeeds = args.windSpeeds

    return settings
