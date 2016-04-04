#
# Copyright: Julian Schutsch 2014
#
# Database wrapper for OpenFOAM Coefficients

import sqlite3
import numpy
import math

# Settings used for generating new values for the database
class Settings:
    def __init__(self, vehicleSpeed, windSpeed, windangle, rootPath):
        self.vehicleVelocity = numpy.array([vehicleSpeed, 0, 0])
        self.windangle = windangle
        self.rootPath = rootPath

        c = math.cos(windangle)
        s = math.sin(windangle)
        rotationMatrix = numpy.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        self.windVelocity = rotationMatrix.dot(numpy.array([windSpeed, 0, 0]))
        self.flowVelocity = self.vehicleVelocity+self.windVelocity
        xDir = numpy.array([1,0,0])
        print(self.flowVelocity, self.flowVelocity.dot(xDir))
        length = math.sqrt(self.flowVelocity[0]*self.flowVelocity[0]+self.flowVelocity[1]*self.flowVelocity[1]+self.flowVelocity[2]*self.flowVelocity[2])
        if length==0:
            self.angle = 0
        else:
            normVelocity = (1/length)*self.flowVelocity
            self.angle = math.acos(normVelocity.dot(xDir))

class CoefficientDatabase:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        try:
            self.execute('''CREATE TABLE coefficients(vehicleSpeed real, windSpeed real, windAngle real, fx real, fy real, fz real, mx real, my real, mz real)''')
        except:
            pass

    def execute(self, str):
        self.cursor.execute(str)
        self.conn.commit()

    def store(self, vehicleSpeed, windSpeed, windAngle, f, m):
        F, M = self.get(vehicleSpeed, windSpeed, windAngle)
        if F!=None:
            return False
        str = "INSERT INTO coefficients VALUES (%f, %f, %f, %f, %f, %f, %f, %f, %f)"%(vehicleSpeed, windSpeed, windAngle, f[0], f[1], f[2], m[0], m[1], m[2])
        self.execute(str)
        return True

    def get(self, vehicleSpeed, windSpeed, windAngle):
        maxDiff = "0.00001"
        str = "SELECT * FROM coefficients WHERE ABS(vehicleSpeed-%f)<"%vehicleSpeed+maxDiff+" AND ABS(windSpeed-%f)<"%windSpeed+maxDiff+" AND ABS(windAngle-%f)<"%windAngle+maxDiff
        print(str)
        self.cursor.execute(str)
        result = self.cursor.fetchall()
        if len(result)==0:
            return None, None
        if len(result)>1:
            raise Exception("Two entries? Should not be the case!")
        row = result[0]
        return [float(row[3]), float(row[4]), float(row[5])], [float(row[6]), float(row[7]), float(row[8])]

    def iterate(self):
        self.cursor.execute("SELECT * FROM coefficients")
        for row in self.cursor.fetchall():
            yield float(row[0]), float(row[1]), float(row[2]), [float(row[3]), float(row[4]), float(row[5])], [float(row[6]), float(row[7]), float(row[8])]

    def calculateAndStore(self, vehicleSpeed, windSpeed, windAngle, rootPath):
        import foamgenerator
        F, M = self.get(vehicleSpeed, windSpeed, windAngle)
        if F!=None:
            return
        settings = Settings(vehicleSpeed, windSpeed, windAngle, rootPath)

        F, M = foamgenerator.calculatePressureCoefficients(settings)
        self.store(vehicleSpeed, windSpeed, windAngle, F, M)
        return

    def minmax(self, func=lambda x,y,z:True):
        fmin = [0,0,0]
        fmax = [0,0,0]
        mmin = [0,0,0]
        mmax = [0,0,0]
        for vs, ws, wa, f, m in self.iterate():
            if func(vs, ws, wa):
                for i in range(3):
                    if f[i]<fmin[i]:
                        fmin[i]=f[i]
                    if f[i]>fmax[i]:
                        fmax[i]=f[i]
                    if m[i]<mmin[i]:
                        mmin[i]=m[i]
                    if m[i]>mmax[i]:
                        mmax[i]=m[i]
        return fmin, fmax, mmin, mmax
