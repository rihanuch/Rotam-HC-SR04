import numpy as np
from random import weibullvariate, uniform

# constantes para utilizar en diferentes calculos de desgaste

PERCENTAGE_WORN = 0.2
EMAIL = 'MAIL'
PASSWORD = 'PASSWORD'

def generate_degradation_data(cant_data: int):
    '''
    Generates tire degradation data with a weibull distribution
    '''
    for number in range(cant_data):
        if number == 0:
            open('examples/data_examples.csv', 'w', encoding='utf-8').close()

        data = []
        rads = np.arange(0, (2 * np.pi), 0.01)
        final = '\n'
        for radian in rads:
            num = round(weibullvariate(uniform(60, 61), uniform(1, 1.01)), 4)
            if 56 < num < 60:
                data.append((round(radian, 4), num))

        if number == cant_data - 1:
            final = ''
        with open('examples/data_examples.csv', 'a', encoding='utf-8') as file:
            file.writelines(f'{data}{final}')


def get_data(generate=False, cant=0):
    '''
    returns a data with all the generated examples
    '''
    if generate:
        if cant == 0:
            generate_degradation_data(50)
        else:
            generate_degradation_data(cant)

    with open('examples/data_examples.csv', 'r') as filehandle:
        places = [eval(current_place.rstrip())
                  for current_place in filehandle.readlines()]

    return places
