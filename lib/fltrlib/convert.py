import math
import numpy


def power2decibels(matrix):
    return 10. * numpy.log10(matrix.clip(min=0.0000000001))


def decibels2power(matrix):
    return numpy.exp(matrix / (10. * math.log(10)))
