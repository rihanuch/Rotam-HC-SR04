import os

MARCA = 'MARCA'
MODELO = 'MODELO'


# modelo de informacion de  https://tiresize.com/

DATA = '''
'''


def parse(text, carpeta, direccion):
    '''
    parsea los datos y los escribe en el archivo para cada modelo de nuematcio
    '''
    head = "Size, Diameter, Width, Rim_Range, Measured_Rim, Tread_Depth, Load_Range, Max_Load(lbs), Max_psi, Weight(lbs), Revs/Mile"

    direccion = direccion.replace(' ', '_')
    text = text.split('\n')

    real = [text[x].strip('\n') + ', ' +(', ').join(
        filter(
            lambda x: x != '' and x != 'psi' and x != 'lbs',
            text[x+1].replace(' ', ',').split(',')[3:]))
            for x in range(0, len(text), 2)]

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    with open(f'{carpeta}/{direccion}.csv', 'w', encoding="utf-8") as file:

        file.write(head+'\n')
        for tire in real:
            file.write(tire+'\n')

parse(DATA, MARCA, MODELO)
