import os
import sys
import time
import random
import threading
import serial
import pandas

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout

import calculations as calc
from constants import get_data, PERCENTAGE_WORN


DESGASTE = uic.loadUiType("GUI/front_end.ui")


class MainWindow(DESGASTE[0], DESGASTE[1]):
    '''
    Clase para instanciar GUI
    '''

    def __init__(self, numero_puerto=1, example=True):
        super().__init__()
        self.setupUi(self)
        self.example = example
        if not example:
            self.puerto = serial.Serial(
                f'/dev/cu.usbmodem14{numero_puerto}1', 9600)
        self.timer_on = False
        self.plot_inf_band = None  # sensor de banda
        self.plot_inf_lado = None  # sensor lateral
        self.__set()

    def __set(self):
        '''
        setea informacion inicial y conexion de botones y lee base de datos
        '''

        self.boton_tiempo_rodamiento.clicked.connect(self.obtener_datos)

        self.marcas = {marca: [] for marca in [f for f in os.listdir('database/')
                                               if not f.startswith('.')]}

        del self.marcas['data_generator.py']
        for modelo in self.marcas.keys():
            self.marcas[modelo] = {f: self.obtener_data_modelo(modelo, f)
                                   for f in os.listdir(f'database/{modelo}')
                                   if not f.startswith('.')}

        self.marca_selector.currentIndexChanged.connect(
            self.marca_selection_change)
        self.modelo_selector.currentIndexChanged.connect(
            self.modelo_selection_change)

        self.marca_selector.addItems(self.marcas.keys())

    @property
    def info_actual(self):
        '''
        obtiene la informacion del neumatico actual
        '''

        marca = self.marca_selector.currentText()
        modelo = self.modelo_selector.currentText()
        dimension = self.dimensiones_selector.currentText()
        return self.marcas[marca][modelo][dimension]

    @staticmethod
    def obtener_data_modelo(marca, modelo):
        '''
        genera el diccionario con la informacion de los neumaticos ubicados
        en la base de datos
        se llama solo 1 vez
        '''

        data = {}
        data_mod = pandas.read_csv(
            f'database/{marca}/{modelo}', delimiter=', ', engine='python')
        for size in range(len(data_mod['Size'])):
            data[data_mod['Size'][size]] = {
                x: data_mod[x][size] for x in data_mod.keys()}
        return data

    def marca_selection_change(self):
        '''
        Selecciona la marca en la GUI
        '''

        self.modelo_selector.clear()
        self.modelo_selector.addItems(
            self.marcas[self.marca_selector.currentText()])

        lim = round(calc.tire_depth(self.info_actual[
            'Tread_Depth']) * PERCENTAGE_WORN, 4)

        self.desgaste_lim_lcd.display(lim)

    def modelo_selection_change(self):
        '''
        Selecciona el modelo de nuematico en la GUI
        '''

        try:
            marca = self.marca_selector.currentText()
            modelo = self.modelo_selector.currentText()

            self.dimensiones_selector.clear()
            self.dimensiones_selector.addItems(self.marcas[marca][modelo])

            lim = round(calc.tire_depth(self.info_actual[
                'Tread_Depth']) * PERCENTAGE_WORN, 4)

            self.desgaste_lim_lcd.display(lim)

        except KeyError:
            pass

    def obtener_datos(self):
        '''
        instancia el thread y setea los parametros iniciales de esa medicion
        '''

        if not self.timer_on:
            self.dist_inst_banda = float(self.distancia_inst_banda.value())
            self.dist_inst_lado = float(self.distancia_inst_lado.value())

            self.info_sensor = threading.Thread(name='ARDUINO listner',
                                                target=self.get_arduino_data)

            self.timer_on = True
            self.info_sensor.start()
            self.boton_tiempo_rodamiento.setText('Detener rodamiento')

        else:
            self.timer_on = False
            self.boton_tiempo_rodamiento.setText('Iniciar rodamiento')

    def get_arduino_data(self):
        '''
        thread para obtener la informacion desde el sensor
        '''

        if not self.example:
            # setea la medicion de tiempo
            tiempo_inicial = time.time()  # 30 segundos
            data_cont_front = []
            data_cont_lado = []

            # se ejecuta durante el tiempo estipulado
            while self.timer_on:
                var = map(float,
                          self.puerto.readline().decode("utf-8").split(";"))
                var = list(var)

                tiempo_demora = time.time() - tiempo_inicial

                data_cont_front.append((var[0], tiempo_demora))
                data_cont_lado.append((var[1], tiempo_demora))

                self.desgaste_inst_banda.display(var[0])
                self.desgaste_inst_lado.display(var[1])
                self.tiempo_rodamiento_lcd.display(tiempo_demora)

            # se obtiene el tiempo que se demoro el rodamiento

            delta_tiempo = tiempo_inicial - time.time()

            # se muestra 0 para indicar que se termino
            self.desgaste_inst_banda.display(0)
            self.desgaste_inst_lado.display(0)
            self.tiempo_rodamiento_lcd.display(0)

            # hace el calculo de los puntos riesgosos
            self.plot_inf_band = calc.riesgos_banda(data_cont_front,
                                                    self.info_actual[
                                                        'Tread_Depth'],
                                                    self.dist_inst_banda,
                                                    self.info_actual[
                                                        'Diameter'][:-1],
                                                    delta_tiempo)

            self.plot_inf_lado = calc.riesgos_lado(data_cont_lado,
                                                   self.dist_inst_lado,
                                                   self.info_actual['Width'],
                                                   delta_tiempo)

            # plotea la informacion obtenida del sensor
        else:
            # plotea la informacion obtenida en mediciones previas
            self.plot_inf_band = random.choice(get_data())
            self.plot_inf_lado = random.choice(get_data())

        # activa el boton para visualizar la informacion
        self.boton_mostrar_graf.clicked.connect(self.show_data)

    def show_data(self):
        '''
        muestra grafico de los datos obtenidos previamente
        '''

        self.grafico_banda = Graph('Banda', data=self.plot_inf_band,
                                   parent=self)
        self.grafico_lado = Graph('Lado', data=self.plot_inf_lado, parent=self)

        self.grafico_banda.show()
        self.grafico_lado.show()
        # se desactiva el boton para evitar inconvenientes de datos parciales
        self.boton_mostrar_graf.disconnect()

        data_neum = [self.marca_selector.currentText(),
                     self.modelo_selector.currentText(),
                     self.dimensiones_selector.currentText()]

        info_string = [f'{data_neum[0].title()}: ',
                       f'{data_neum[1].replace("_", " ")[:-4].title()}: ',
                       f'{data_neum[2]}\n']
        modelo_intermedio = ''.join(info_string)

        mensaje = calc.message_creator(modelo=modelo_intermedio,
                                       data_lado=self.plot_inf_lado,
                                       data_banda=self.plot_inf_band)

        calc.sendemail(from_addr='MAIL',
                       to_addr_list=['MAIL'],
                       cc_addr_list=[''],
                       subject='Desgaste de neumaticos',
                       message=f'{mensaje}')


class Graph(QDialog):
    '''
    Ventana para mostrar informacion recolectada con el sensor
    '''

    def __init__(self, tipo, data=None, parent=None, lims=(None, None)):
        super(Graph, self).__init__(parent)

        self.setWindowTitle(f'{tipo}')
        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)

        # setea layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot(data, lims)

    def plot(self, data, lims):
        '''plotea la data a mostrar en la GUI'''

        # en vez de of ax.hold(False)
        self.figure.clear()

        # crea an ejes
        axes = self.figure.add_subplot(111, polar=True)

        if lims != (None, None):
            axes.set_ylim(lims[0], lims[1])

        # borra grafico antiguo

        # plotea data
        for info in data:
            axes.plot(info[0], info[1], 'o')

        # actualiza
        self.canvas.draw()


if __name__ == '__main__':
    def hook(type, value, traceback):
        '''
        para evitar problemas con errores de input
        '''

        print(type)
        print(traceback)

    sys.__excepthook__ = hook
    APP = QApplication([])
    VENTANA = MainWindow(numero_puerto=1, example=True)
    VENTANA.show()
    APP.exec_()
