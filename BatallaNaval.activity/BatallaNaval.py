#!/usr/bin/env python
# -*- coding: cp1252 -*-

import pygtk
pygtk.require('2.0')
import gtk
import logging
import random

try:
    from sugar.activity.activity import Activity, ActivityToolbox
except:
    pass

log = logging.getLogger('BatallaNaval')
log.setLevel(logging.DEBUG)

lista_barcos = {
    "Portaaviones": 5,
    "Acorazado": 4,
    "Crucero": 3,
    "Submarino": 3,
    "Destructor": 2}

class PanelPrincipal(gtk.HBox):
    
    def __init__(self):
        gtk.HBox.__init__(self, True)
        
        self.tablero1 = Tablero(None)               # tablero propio  
        self.tablero2 = Tablero(self.jugada_hecha)  # tablero enemigo

        log.debug("Barcos Propios")
        barcos_propios = crear_barcos()
        for barco in barcos_propios:
            self.tablero1.agregar_barco(barco, True)
            log.debug("barco:%s, %s (%s, %s)" % (barco.name, barco.orientacion, barco.pos[0], barco.pos[1]))

        log.debug("Barcos Enemigos")
        self.barcos_enemigos = crear_barcos()
        for barco in self.barcos_enemigos:
            self.tablero2.agregar_barco(barco, False)
            log.debug("barco:%s, %s (%s, %s)" % (barco.name, barco.orientacion, barco.pos[0], barco.pos[1]))

        self.add(self.tablero1)
        self.add(self.tablero2)
        
        self.show_all()
        
        self.jugadas_enemigas = []   # Lleva un registro de las jugadas hechas por la computadora
    
    # Carga barcos remotos
    def cargar_barcos(self, barcos):
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
    
    # Cuando el enemigo juega sobre mi tablero, hago la judada y le respondo si fue tocado
    def jugada_red(self, x, y):
        return self.tablero1.jugada(self.tablero1.filas[x-1][y-1])
    
    # Cuando yo mismo hice una jugada sobre el tablero enemigo, si hay colaboración actualizo según la respuesta
    def jugada_hecha(self, x, y):
        # Si hay colaboración, indico al oponente la jugada que hice
        if self.colaboracion:
            self.colaboracion.Play(x, y)
            return
        
        # Sinó, la computadora hace una jugada al azar sobre el tablero propio
        if len(self.jugadas_enemigas) == 100:
            return
        
        ok = False
        while not ok:
            x, y = random.randint(1, 10), random.randint(1, 10)
            if not (x, y) in self.jugadas_enemigas:
                ok = True
        
        self.jugadas_enemigas.append((x, y))
        self.tablero1.filas[x-1][y-1].clicked()
        
def crear_barcos():
    barcos = [Barco(b[0], b[1], None) for b in lista_barcos.items()]
    
    celdas_ocupadas = []
    
    for barco in barcos:
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
            ok = True
            for celda in barco.get_celdas():
                if celda in celdas_ocupadas:
                    ok = False
            if ok:
                celdas_ocupadas.extend(barco.get_celdas())
    return barcos

class Celda(gtk.Button):
    
    def __init__(self, pos, clicked_cb):
        gtk.Button.__init__(self)
        self.pos = pos
        
        self.connect("clicked", clicked_cb)
    
    def ocultar(self):
        self.set_no_show_all(True)
        self.hide()
    
    def tocado(self):
        color = gtk.gdk.Color(65535,65535/2,0)
        self.modify_bg(gtk.STATE_NORMAL, color)
        self.modify_bg(gtk.STATE_PRELIGHT, color)
        self.show()     # Por si está oculta atrás de un barco
        
    def agua(self):
        color = gtk.gdk.Color(0,0,65535/2)
        self.modify_bg(gtk.STATE_NORMAL, color)
        self.modify_bg(gtk.STATE_PRELIGHT, color)
        self.show()     # Por si está oculta atrás de un barco
        
class Tablero(gtk.Frame):
    
    def __init__(self, llamada_jugada_hecha):
        gtk.Frame.__init__(self)

        # Números
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
        
        # Se hace una tabla para ubicar las letras, los números y el tablero
        self.tabla = gtk.Table(2, 2, False)
        self.add(self.tabla)
        
        opciones = gtk.SHRINK|gtk.FILL
        
        label = gtk.Label("      ")
        self.tabla.attach(label, 0, 1, 0, 1, xoptions=opciones, yoptions=opciones)
        
        self.tabla.attach(tabla_numeros, 1, 2, 0, 1, xoptions=opciones, yoptions=opciones)
        self.tabla.attach(tabla_letras, 0, 1, 1, 2, xoptions=opciones, yoptions=opciones)
        
        self.filas = []
        
        # El tablero es otra tabla
        self.tabla_celdas = gtk.Table(10, 10, True)
        self.tabla.attach(self.tabla_celdas, 1, 2, 1, 2, xoptions=gtk.FILL|gtk.EXPAND, yoptions=gtk.FILL|gtk.EXPAND)

        for i in range(1, 11):
            row = []
            for j in range(1, 11):
                left = j - 1
                top = i - 1
                celda = Celda((i, j), self.celda_clickeada)
                row.append(celda)
                self.tabla_celdas.attach(celda, left, j, top, i)
                #print label.get_text()
            self.filas.append(row)
        
        self.barcos = []     # Los barcos que hay en el tablero
        
        self.llamada_jugada_hecha = llamada_jugada_hecha
    
    def agregar_barco(self, barco, show):
        self.barcos.append(barco)
        if show:
            for i in barco.get_filas():
                for j in barco.get_cols():
                    self.ocultar_celda(i, j)
            izq = barco.get_inicio()[1]-1
            der = barco.get_fin()[1]
            arr = barco.get_inicio()[0]-1
            aba = barco.get_fin()[0]
            self.tabla_celdas.attach(barco, izq, der, arr, aba)
        
    def ocultar_celda(self, i, j):
        self.filas[i-1][j-1].ocultar()

    def celda_clickeada(self, celda):
        # Cuando hay definido un callback de jugadas hechas, significa que es el tablero en el que puedo jugar
        if self.llamada_jugada_hecha:
            # Este es el callback para cuando clickean una celda
            self.jugada(celda)
            self.llamada_jugada_hecha(celda.pos[0], celda.pos[1])
    
    def jugada(self, celda):
        tocado = False
        for barco in self.barcos:
            if celda.pos in barco.get_celdas():
                tocado = True
                celda.tocado()
        if not tocado:
            celda.agua()
        
        return tocado
    
class Barco(gtk.Frame):
    
    horizontal = 'H'
    vertical = 'V'
    
    def __init__(self, nombre, largo, pos, orientacion = horizontal):
        #gtk.Label.__init__(self, nombre)
        gtk.Frame.__init__(self)
        self.nombre = nombre
        self.largo = largo
        self.pos = pos
        self.label = gtk.Label(nombre)
        self.add(self.label)
        self.set_orientacion(orientacion)
    
    def set_orientacion(self, orientacion):
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
    
# Esta función es el punto de entrada común para sugar y modo standalone
# standalone es un boolean que indica si es Standalone o se ejecuta desde Sugar
def init(standalone, ventana_principal):
    
    panel_principal = PanelPrincipal()
    
    if not standalone:
        toolbox = ActivityToolbox(ventana_principal)
        ventana_principal.set_toolbox(toolbox)
        toolbox.show()
        ventana_principal.set_canvas(panel_principal)
        
        # Colaboración
        panel_principal.colaboracion = ventana_principal.colaboracion
        panel_principal.colaboracion.set_up(
                None,   # Nuevo compañero
                None,   # Salió Compañero
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

# Este es el procedimiento principal en modo standalone
def main():
    ventana_principal = gtk.Window(gtk.WINDOW_TOPLEVEL)
    init(True, ventana_principal)
    gtk.main()
    return 0

# Este código se ejecuta sólo cuando se ejecuta directo ese módulo (no cuando se importa desde sugar)
if __name__ == "__main__":
   main()
