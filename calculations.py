from constants import PERCENTAGE_WORN, EMAIL, PASSWORD
import smtplib


def sendemail(from_addr, to_addr_list, cc_addr_list, subject, message,
              smtpserver='smtp.gmail.com:587'):
    header = f'From: {EMAIL}\n'
    header += f'To: {", ".join(to_addr_list)}\n'
    header += f'Cc: {", ".join(cc_addr_list)}\n'
    header += f'Subject: {subject}\n'
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.ehlo()
    server.starttls()
    server.login(EMAIL, PASSWORD)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()


def inch_to_cm(inch: float):
    return inch * 2.54


def tire_depth(size: str):
    return inch_to_cm(float(eval(size[:-1])))


def tire_diameter(size: str):
    return inch_to_cm(float(size[:-1]))


def tire_height(diameter: str, rim: str):
    return (tire_diameter(rim), tire_diameter(diameter) - tire_diameter(rim))


def riesgos_banda(measured_distances: list, depth: str, inst_dist: float,
                  diameter: str, tiempo: float):
    list_danger = []  # lista de tuplas del tipo (tiempo, distancia peligro)
    depth = tire_depth(depth)
    diameter = tire_diameter(diameter[:-1])
    for dist in measured_distances:
        if (dist[0] - inst_dist) < (depth * PERCENTAGE_WORN):
            list_danger.append((round(dist[1] / tiempo * 2 * 3.14159, 4),
                                round(diameter - (dist[0] - inst_dist), 4)))

    return list_danger


def riesgos_lado(measured_distances: list, width: str, inst_dist: float,
                 tiempo: float):
    list_danger = []  # lista de tuplas del tipo (tiempo, distancia peligro)
    width = tire_diameter(width)
    for dist in measured_distances:
        # dist es del tipo (medida, tiempo)
        if round(inst_dist, 2) < round(dist[0], 2):
            list_danger.append((round(dist[1] / tiempo * 2 * 3.14159, 4),
                                round(width - (dist[0] - inst_dist), 4)))

    return list_danger


def message_creator(modelo=None, data_lado=None, data_banda=None):
    mensaje = modelo
    mensaje += '\nInformacion lateral\nAngulo, Distancia\n'
    for count, data in enumerate(data_lado):
        mensaje += f'{data[0]}, {data[1]}\n'

    mensaje += '\nInformacion banda\nAngulo, Distancia\n'
    for count, data in enumerate(data_banda):
        mensaje += f'{data[0]}, {data[1]}\n'

    mensaje += '\n\nGracias por preferirnos'

    return mensaje
