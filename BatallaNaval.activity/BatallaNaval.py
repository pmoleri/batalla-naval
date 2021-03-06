#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#
# Copyright 2009 ceibalJAM!
# This file is part of Batalla Naval.
#
# Batalla Naval is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Batalla Naval is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Batalla Naval.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# ceibalJAM! http://ceibaljam.org

import pygtk
pygtk.require('2.0')
import gtk
import logging
import random

# Permite definir un Log que filtra mensajes a la salida est�ndar dependiendo de nivel elegido.
log = logging.getLogger('BatallaNaval')
log.setLevel(logging.DEBUG)

# Diccionario que contiene el nombre y largo de cada barco
lista_barcos = {
    "Portaaviones": 5,
    "Acorazado": 4,
    "Crucero": 3,
    "Submarino": 3,
    "Destructor": 2}

class PanelPrincipal(gtk.HBox):
    ''' Panel Principal es un Widget que contiene ambos tableros y se encarga
        de crear los barcos en posiciones al azar para cada tablero '''
    
    def __init__(self):
        gtk.HBox.__init__(self, True)
        
        self.tablero1 = Tablero(None)               # tablero propio  
        self.tablero2 = Tablero(self.jugada_hecha)  # tablero enemigo

        log.debug("Barcos Propios")
        barcos_propios = crear_barcos()
        for barco in barcos_propios:
            self.tablero1.agregar_barco(barco, True)
            log.debug("barco:%s, %s (%s, %s)" % (barco.nombre, barco.orientacion, barco.pos[0], barco.pos[1]))

        log.debug("Barcos Enemigos")
        self.barcos_enemigos = crear_barcos()
        for barco in self.barcos_enemigos:
            self.tablero2.agregar_barco(barco, False)
            log.debug("barco:%s, %s (%s, %s)" % (barco.nombre, barco.orientacion, barco.pos[0], barco.pos[1]))

        self.add(self.tablero1)
        self.add(self.tablero2)
        
        self.jugadas_enemigas = []   # Lleva un registro de las jugadas hechas por la computadora
        
        self.show_all()
    
    # Carga barcos remotos
    def cargar_barcos(self, barcos):
        ''' Esta funci�n es llamada cuando me conecto en red con otro usuario, recibo
            una tupla con los datos de los barcos enemigos. '''
        log.debug("Cargando barcos enemigos")
        self.tablero2.barcos = []
        for dato in barcos:
            log.debug("Dato: %s" % str(dato))
            nombre = dato[0]
            orientacion = dato[1]
            largo = dato[2]
            pos = dato[3:5]
            
            barco = Barco(nombre, largo, pos, orientacion)
            self.tablero2.agregar_barco(barco, False)
            log.debug("barco:%s, %s (%s, %s)" % (barco.name, barco.orientacion, barco.pos[0], barco.pos[1]))
    
    def jugada_red(self, x, y):
        ''' Callback de colaboraci�n para la se�al Play.
            Cuando el enemigo juega sobre mi tablero, reflejo la judada y le respondo si fue tocado '''
        return self.tablero1.jugada(self.tablero1.filas[x-1][y-1])
    
    def jugada_hecha(self, x, y):
        ''' Cuando yo mismo hice una jugada sobre el tablero enemigo
            si la actividad est� compartida indico al oponente la jugada que hice,
            en caso contrario me simulo una jugada random del enemigo. '''

        # Si estoy compartiendo con alguien, indico al oponente la jugada que hice
        if self.colaboracion and self.colaboracion.entered:
            log.debug("Se�alo jugada a los participantes")
            self.colaboracion.Play(x, y)
            return
        
        # Sin�, la computadora hace una jugada al azar sobre el tablero propio
        if len(self.jugadas_enemigas) == 100:
            log.error("Alcanz� las 100 jugadas.")
            return
        
        ok = False
        while not ok:
            x, y = random.randint(1, 10), random.randint(1, 10)
            if not (x, y) in self.jugadas_enemigas:
                ok = True
        
        self.jugadas_enemigas.append((x, y))
        self.tablero1.jugada(self.tablero1.filas[x-1][y-1])

class Barco(gtk.Frame):
    ''' Esta clase representa un barco, tiene nombre, largo, orientaci�n y posici�n.
        Como es un widget puede ser mostrado en la pantalla y tiene un texto con el nombre del barco '''
        
    horizontal = 'H'
    vertical = 'V'
    
    def __init__(self, nombre, largo, pos, orientacion = horizontal):
        gtk.Frame.__init__(self)
        self.nombre = nombre
        self.largo = largo
        self.pos = pos
        
        # Agrega una etiqueta con el nombre del barco
        self.label = gtk.Label(nombre)
        self.add(self.label)
        
        self.set_orientacion(orientacion)   # Graba la orientaci�n y ajusta la etiqueta a dicha orientaci�n.
    
    def set_orientacion(self, orientacion):
        ''' Graba la orientaci�n y ajusta la etiqueta a dicha orientaci�n. '''
        self.orientacion = orientacion
        if self.orientacion == Barco.horizontal:
            self.label.set_angle(0)
        else:
            self.label.set_angle(90)
        
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
    
    # Convierte la lista de definici�n en una lista de objetos Barco sin posici�n definida
    barcos = [Barco(nombre, largo, None) for nombre, largo in lista_barcos.items()]
    
    celdas_ocupadas = []    # Llevo una lista de las celdas ya ocupadas por los barcos
    
    for barco in barcos:
        # Para cada barco me mantengo en un loop hasta que encuentre coordenadas al azar que no
        # intersecten con ning�n barco ya ubicado.
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
            
            # Verifico si la posici�n elegida no intersecciona con las celdas ya ocupadas por otros barcos
            # Convierto las listas en sets y aplico intersecci�n
            interseccion = set(barco.get_celdas()) & set(celdas_ocupadas)
            if not interseccion:
                ok = True
                celdas_ocupadas.extend(barco.get_celdas())
    return barcos

class Celda(gtk.Button):
    ''' Esta clase representa una celda del tablero, como es subclase de button se le puede
        conectar la se�al "clicked".
        Tambi�n presenta funciones para ocultar y colorearse dependiendo de si toc� un barco o di� agua. '''
        
    def __init__(self, pos):
        gtk.Button.__init__(self)
        self.pos = pos
    
    def ocultar(self):
        ''' Oculta permanentemente la celda, de modo que show_all no la muestre '''
        self.set_no_show_all(True)
        self.hide()
    
    def colorear(self, color):
        self.modify_bg(gtk.STATE_NORMAL, color)
        self.modify_bg(gtk.STATE_PRELIGHT, color)
        self.show()     # Por si est� oculta atr�s de un barco

    def tocado(self):
        self.colorear( gtk.gdk.Color(65535,65535/2,0) )
        
    def agua(self):
        self.colorear( gtk.gdk.Color(0,0,65535/2) )


class Tablero(gtk.Frame):
    ''' Define un tablero, el tablero est� definido con una tabla exterior que permite poner
        los t�tulos de las filas y las columnas (que a su vez son tablas) y una tabla interior
        que tiene todas las celdas del tablero (tabla_celdas). '''
    
    def __init__(self, llamada_jugada_hecha):
        gtk.Frame.__init__(self)

        # N�meros
        tabla_numeros = gtk.Table(1, 10, True)
        for i in range(1, 11):
            label = gtk.Label(str(i))
            tabla_numeros.attach(label, i-1, i, 0, 1)
        
        # Letras
        tabla_letras = gtk.Table(10, 1, True)
        for i in range(1, 11):
            char = chr( ord('A') + i - 1 )
            label = gtk.Label(char)
            tabla_letras.attach(label, 0, 1, i-1, i)
        
        # Se hace una tabla para ubicar las letras, los n�meros y la tabla de celdas
        self.tabla = gtk.Table(2, 2, False)
        self.add(self.tabla)
        
        # Opciones para las tablas de letras y n�meros.
        opciones = gtk.SHRINK|gtk.FILL
        
        label = gtk.Label("      ") # Para dar m�s espacio a la columna de letras
        self.tabla.attach(label, 0, 1, 0, 1, xoptions=opciones, yoptions=opciones)
        self.tabla.attach(tabla_numeros, 1, 2, 0, 1, xoptions=opciones, yoptions=opciones)
        self.tabla.attach(tabla_letras, 0, 1, 1, 2, xoptions=opciones, yoptions=opciones)
        
        # El tablero es otra tabla
        self.tabla_celdas = gtk.Table(10, 10, True)
        self.tabla.attach(self.tabla_celdas, 1, 2, 1, 2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND)
        
        self.filas = []
        # Creo todas las celdas, las guardo en la colecci�n de filas y las adjunto al tablero
        for i in range(1, 11):
            fila = []
            for j in range(1, 11):
                celda = Celda((i, j))
                celda.connect("clicked", self.celda_clickeada)
                fila.append(celda)
                self.tabla_celdas.attach(celda, j-1, j, i-1, i)
            self.filas.append(fila)
        
        # Los barcos que hay en el tablero
        self.barcos = []
        
        # Callback para cuando el jugador hace una jugada en el tablero
        self.llamada_jugada_hecha = llamada_jugada_hecha
    
    def agregar_barco(self, barco, mostrar):
        ''' Agrega un barco al tablero, si mostrar=True sustituye las celdas que ocupa por el barco. '''
        self.barcos.append(barco)
        if mostrar:
            # Oculta las celdas que ocupa el barco
            for i, j in barco.get_celdas():
                self.ocultar_celda(i, j)
            
            # Obtiene los extremos del barco y lo adjunta a la tabla
            arr, izq = barco.get_inicio()
            aba, der = barco.get_fin()
            self.tabla_celdas.attach(barco, izq-1, der, arr-1, aba)
    
    def ocultar_celda(self, i, j):
        self.filas[i-1][j-1].ocultar()

    def celda_clickeada(self, celda):
        ''' Cuando hay definido un callback de jugadas hechas, significa que en este tablero puedo jugar.
            Realizo la jugada y notifico al callback '''
        if self.llamada_jugada_hecha:
            # Este es el callback para cuando clickean una celda
            self.jugada(celda)
            self.llamada_jugada_hecha(celda.pos[0], celda.pos[1])
    
    def jugada(self, celda):
        ''' verifica si la jugada da en alg�n barco o en el agua y manda la se�al correcta a la celda '''
        tocado = False
        for barco in self.barcos:
            if celda.pos in barco.get_celdas():
                tocado = True
                celda.tocado()
        if not tocado:
            celda.agua()
            
        log.debug("Pos:%s Tocado:%s", str(celda.pos), tocado)
        return tocado
    
def init(standalone, ventana_principal):
    ''' Esta funci�n es el punto de entrada com�n para sugar y modo standalone
        standalone es un boolean que indica si es Standalone o se ejecuta desde Sugar '''
    panel_principal = PanelPrincipal()
    
    if not standalone:
        ventana_principal.set_canvas(panel_principal)
        
        # Colaboraci�n
        panel_principal.colaboracion = ventana_principal.colaboracion
        panel_principal.colaboracion.set_up(
                None,   # Nuevo compa�ero
                None,   # Sali� Compa�ero
                panel_principal.cargar_barcos,  # World
                panel_principal.jugada_red,     # Play
                panel_principal.tablero1.barcos)# Mis barcos
    else:
        ventana_principal.add(panel_principal)
        panel_principal.colaboracion = None
    
    ventana_principal.set_title("Batalla Naval - ceibalJAM")
    ventana_principal.connect("destroy", lambda wid: gtk.main_quit())
    ventana_principal.connect("delete_event", lambda a1, a2: gtk.main_quit())

    ventana_principal.show()

# Este c�digo se ejecuta s�lo cuando se ejecuta directo ese m�dulo (no cuando se importa desde sugar)
if __name__ == "__main__":
    log.addHandler(logging.StreamHandler())
    ventana_principal = gtk.Window(gtk.WINDOW_TOPLEVEL)
    init(True, ventana_principal)
    gtk.main()
