import serial, time, decimal, numpy
import matplotlib.pyplot as plt

ARDUINO = serial.Serial('/dev/cu.usbmodem1411', 9600)

# Y_MEANS = []
# ERROR = []

# CANT_DATA = 5
# CANT_DATA_CYCLE = 4

# for cycle in range(CANT_DATA):
#     DATA = []
#     for _ in range(10):
#         info = numpy.mean([float(ARDUINO.readline().decode("utf-8"))
#                            for _ in range(CANT_DATA_CYCLE)])
#         DATA.append(info)
#     mean = round(numpy.mean(DATA), 5)
#     stdv = round(numpy.std(DATA), 5)


#     Y_MEANS.append(mean)
#     ERROR.append(stdv)

#     print(f"""
#     	Ciclo numero:   {cycle + 1}
#     	Distancia:      {mean} cm 
#     	Desviacion std: {stdv} cm""")

# X_RANGE = [x for x in range(1, CANT_DATA + 1)]

# plt.errorbar(X_RANGE, Y_MEANS, yerr=ERROR, fmt="o")
# plt.show()

while True:
    l = ARDUINO.readline().decode("utf-8").split(";")
    l = [float(l[0]),float(l[1])]
    print(l)