#
# Copyright: Julian Schutsch 2014
#
# Delaunay interpolation for OpenFOAM coefficients.

import scipy
import numpy
import math
from . import database

class InterpolatedCoefficients:
    def __init__(self, filename):
        self.database = database.CoefficientDatabase(filename)
        self.map = {(vehicleSpeed, windSpeed, windAngle):(numpy.array(F), numpy.array(M)) for vehicleSpeed, windSpeed, windAngle, F, M in self.database.iterate()}
        points = [numpy.array(x) for x in self.map]
        self.delaunay = scipy.spatial.Delaunay(points, qhull_options="QJ")

    def interpolate(self, vehicleSpeed, windSpeed, windAngle):
        windFloor = 2*math.pi*math.floor(windAngle/(2*math.pi))
        windAngle = windAngle-windFloor
        if windAngle>=math.pi:
            windAngle = 2*math.pi-windAngle
        assert(windAngle>=0 and windAngle<=math.pi)
        point = numpy.array([vehicleSpeed, windSpeed, windAngle])
        simplexIndex = self.delaunay.find_simplex(point)
        simplex =self.delaunay.simplices[simplexIndex]
        p = [self.delaunay.points[i] for i in simplex]
        F = [self.map[x[0], x[1], x[2]][0] for x in p]
        M = [self.map[x[0], x[1], x[2]][1] for x in p]

        diffVec = point-p[0]
        matrix = numpy.transpose(numpy.array([p[1]-p[0],p[2]-p[0],p[3]-p[0]]))
        coefficients = numpy.linalg.solve(matrix, diffVec)
        FResult = F[0]+coefficients[0]*(F[1]-F[0])+coefficients[1]*(F[2]-F[0])+coefficients[2]*(F[3]-F[0])
        MResult = M[0]+coefficients[0]*(M[1]-M[0])+coefficients[1]*(M[2]-M[0])+coefficients[2]*(M[3]-M[0])
        return FResult, MResult

