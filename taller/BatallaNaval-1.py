#!/usr/bin/env python
# -*- coding: cp1252 -*-

import pygtk
pygtk.require('2.0')
import gtk
import logging
import random

# Permite definir un Log que filtra mensajes a la salida estándar dependiendo de nivel elegido.
log = logging.getLogger('BatallaNaval')
log.setLevel(logging.DEBUG)

# Diccionario que contiene el nombre y largo de cada barco
lista_barcos = {
    "Portaaviones": 5,
    "Acorazado": 4,
    "Crucero": 3,
    "Submarino": 3,
    "Destructor": 2}

class PanelPrincipal():
    ''' Panel Principal es un Widget que contiene ambos tableros y se encarga
        de crear los barcos en posiciones al azar para cada tablero '''
    
    def __init__(self):
        self.tablero = Tablero()

        log.debug("Carga barcos")
        barcos = crear_barcos()
        for barco in barcos:
            self.tablero.agregar_barco(barco)
            log.debug("barco:%s, %s (%s, %s)" % (barco.nombre, barco.orientacion, barco.pos[0], barco.pos[1]))
    
    def mostrar_informacion(self):
        for fila in self.tablero.filas:
            print "-".join([str(celda.pos) for celda in fila])
            
        print ""
        
        print "barcos:"
        for barco in self.tablero.barcos:
            str_celdas = "-".join([str(celda) for celda in barco.get_celdas()])
            print "%s : %s" % (barco.nombre, str_celdas)

class Barco():
    ''' Esta clase representa un barco, tiene nombre, largo, orientación y posición.
        Como es un widget puede ser mostrado en la pantalla y tiene un texto con el nombre del barco '''
        
    horizontal = 'H'
    vertical = 'V'
    
    def __init__(self, nombre, largo, pos, orientacion = horizontal):
        self.nombre = nombre
        self.largo = largo
        self.pos = pos
        self.orientacion = orientacion
    
    def set_orientacion(self, orientacion):
        ''' Graba la orientación '''
        
    def get_inicio(self):
        return self.pos
    
    def get_fin(self):
        if self.orientacion == Barco.horizontal:
            return self.pos[0], self.pos[1] + self.largo - 1
        else:
            return self.pos[0] + self.largo - 1, self.pos[1]

    def get_filas(self):
        return range(self.get_inicio()[0], self.get_fin()[0]+1)
    
    def get_cols(self):
        return range(self.get_inicio()[1], self.get_fin()[1]+1)
    
    def get_celdas(self):
        return [(f, c) for f in self.get_filas() for c in self.get_cols()]

def crear_barcos():
    ''' Parte de la lista_barcos para crear un conjunto de barcos en posiciones al azar. '''
    
    # Convierte la lista de definición en una lista de objetos Barco sin posición definida
    barcos = [Barco(nombre, largo, None) for nombre, largo in lista_barcos.items()]
    
    celdas_ocupadas = []    # Llevo una lista de las celdas ya ocupadas por los barcos
    
    for barco in barcos:
        # Para cada barco me mantengo en un loop hasta que encuentre coordenadas al azar que no
        # intersecten con ningún barco ya ubicado.
        ok = False
        while not ok:
            # Determino al azar si es horizontal o vertical
            if random.randint(0, 1):
                # Calculo coordenadas random - horizontal
                barco.set_orientacion(Barco.horizontal)
                posx = random.randint(1, 10)
                posy = random.randint(1, 10-barco.largo+1)
            else:
                # Calculo coordenadas random - vertical
                barco.set_orientacion(Barco.vertical)
                posx = random.randint(1, 10-barco.largo+1)
                posy = random.randint(1, 10)
            barco.pos = (posx, posy)
            
            # Verifico si la posición elegida no intersecciona con las celdas ya ocupadas por otros barcos
            # Convierto las listas en sets y aplico intersección
            interseccion = set(barco.get_celdas()) & set(celdas_ocupadas)
            if not interseccion:
                ok = True
                celdas_ocupadas.extend(barco.get_celdas())
    return barcos

class Celda():
    ''' Esta clase representa una celda del tablero. '''
        
    def __init__(self, pos):
        self.pos = pos

class Tablero():
    ''' Define un tablero con celdas y una función para agregar barcos '''
    
    def __init__(self):
        
        self.filas = []
        # Creo todas las celdas, las guardo en la colección de filas y las adjunto al tablero
        for i in range(1, 11):
            fila = []
            for j in range(1, 11):
                celda = Celda((i, j))
                fila.append(celda)
            self.filas.append(fila)
        
        # Los barcos que hay en el tablero
        self.barcos = []
    
    def agregar_barco(self, barco):
        ''' Agrega un barco al tablero, si mostrar=True sustituye las celdas que ocupa por el barco. '''
        self.barcos.append(barco)
    
    def ocultar_celda(self, i, j):
        self.filas[i-1][j-1].ocultar()
    
def init():
    panel_principal = PanelPrincipal()
    panel_principal.mostrar_informacion()

# Este código se ejecuta sólo cuando se ejecuta directo ese módulo (no cuando se importa desde sugar)
if __name__ == "__main__":
    log.addHandler(logging.StreamHandler())
    init()
