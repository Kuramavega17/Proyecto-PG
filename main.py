import pygame
from pygame.locals import *
import sys
import subprocess
#from music_manager import music_manager
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from camera import Camera
from mov import handle_events, handle_mouse
from OBJ import OBJ
import tkinter as tk
from tkinter import messagebox

def mostrar_ventana_perder():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    messagebox.showinfo("Juego Terminado", "¡Has Perdido el juego!")
    root.destroy()  # Destruye la ventana principal de Tkinter
def mostrar_ventana_ganar():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    messagebox.showinfo("Juego Terminado", "¡Has GANADO el juego!")
    root.destroy()  # Destruye la ventana principal de Tkinter
    pygame.quit()
    sys.exit()
#Funcion para cargar texturas
def load_texture(path):
    texture_surface = pygame.image.load(path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    glEnable(GL_TEXTURE_2D)
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture

#Funcion para mostrar x,y y z

def draw_axes(length):
    glBegin(GL_LINES)
    
    # Eje X - Rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(length, 0.0, 0.0)

    # Eje Y - Verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, length, 0.0)

    # Eje Z - Azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, length)

    glEnd()

#Funcion para pared
def pared(x, y, z, lA, lB, lC):
    return [
        #x  y  z
        ((x+lA), y, z), ((x+lA), (y+lC), z), (x, (y+lC), (z+lB)), (x, y, (z+lB)),
    ]

#Funcion para piso
def piso(xA, xB, yA, yB, val):
    subxA, subxB = 0 , 0
    if (xA == 0):
        subxA = 2
        subxB = 4
    else:
        subxA = 0
        subxB = 2
    if val == 0:
        return [
            #x  y  z
            (xB, 0, yA), (xA, 0, yA), (xA, 0, yB), (xB, 0, yB),
        ], (subxA), (subxB), (yA), (yB)
    else:
        return [
            #x  y  z
            (xB, 0, yA), (xA, 0, yA), (xA, 0, yB), (xB, 0, yB),
        ], (subxA), (subxB), (yA + 2), (yB + 2)

#Funcion para renderizar texturas por coordenadas
def renPiso(pisoSuper, tex_coords):    
    glBegin(GL_QUADS)
    for i in range(0, len(pisoSuper), 4):
        for j in range(4):
            glTexCoord2f(tex_coords[j][0], tex_coords[j][1])
            glVertex3fv(pisoSuper[i + j])
    glEnd()

def labBin(archivo):
    with open(archivo, 'r') as file:
        lineas = file.readlines()
        a = [[0 for _ in range(43)] for _ in range(9)]
        for i in range(0, 9, 1):
            if i < len(lineas):
                b = ''.join(lineas[i][j] for j in range(1, 129, 3))  # Saltear columnas de por medio

                for j in range(min(43, len(b))):
                    a[i][j] = b[j]
    return a


def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 600), DOUBLEBUF | OPENGL) #Dimension Ventana
    pygame.display.set_caption("Stronghold for Minecraft") #Label
    glEnable(GL_DEPTH_TEST) #Profundidad
    glDepthFunc(GL_LESS) #Profundidad

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (800 / 600), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    glClearColor(0.9, 0.9, 0.5, 1.0)  # Color de fondo más oscuro
    luz_posicion = [1.0, 0.0, 19.0]  # Posición de la luz
    # Color de la luz ambiental (color rojo)
    luz_ambiental = [0.5, 0.0, 0.0, 1.0]

    # Color de la luz difusa (color oscuro)
    luz_difusa = [10.01, 10.01, 10.01, 0.05]

    # Color de la luz especular (color normal)
    luz_especular = [0.0, 1.0, 0.0, 1.0]
    # Configurar la luz
    glLightfv(GL_LIGHT0, GL_POSITION, luz_posicion)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiental)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)

    # Habilitar la iluminación
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    camera = Camera((3.5,1.5,0.5))
    camera.rot = [260.0, 0.0]
    
    cam = [0, 0]
    posCam = [0.25,0.25]
    
    anchoAA = [8,6,4,2,0]
    largoAA = [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39]
    anchoAB = [7,5,3,1]
    largoBB = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40]
    
    #load textures
    atardecer= load_texture('Textura/atardecer.jpg')
    superficie = load_texture('Textura/suelo.jpg')
    wall = load_texture('Textura/Pared0.jpg')
    lava = load_texture('Textura/lava.jpg')
    end = load_texture('Textura/end.png')
    paredEnd = load_texture('Textura/sueloEnd.jpg')
    pisoEnd = load_texture('Textura/sueloE.jpg')
    pezPlata= load_texture('Textura/Pez plata.jpg')
    frontEnd= load_texture('Textura/frontEnd.jpg')
    agua= load_texture('Textura/agua.jpg')
    
    golem = OBJ('Textura/iron_golem.obj', 'Textura/iron_golem.png')
    golem2 = OBJ('Textura/iron_golem.obj', 'Textura/iron_golem.png')
    cofre = OBJ('Textura/Chest.obj', 'Textura/Chest.png')
    ghast = OBJ('Textura/Kraseu.obj', 'Textura/Krasea.png')
    golem.position = (1, 0, 9)
    golem.scale=(0.05, 0.05, 0.05)
    golem2.position = (4, 0, 9)
    golem2.scale=(0.05, 0.05, 0.05)
    cofre.position = (2, 0, 9)
    cofre.scale=(1, 1., 1)
    ghast.position = (3, 1, 13)
    ghast.scale=(2.0, 4.0, 2.0)
    
    pygame.mixer.music.load('Textura/cueva.mp3')
    pygame.mixer.music.play()
    
 
    
    xA, xB, yA, yB = 0, 2, 0, 2
    
    pisoAA, xA, xB, yA, yB = piso(xA, xB, yA, yB, 0)
    pisoBA, xA, xB, yA, yB = piso(xA, xB, yA, yB, 1)
    pisoAB, xA, xB, yA, yB = piso(xA, xB, yA, yB, 0)
    pisoBB, xA, xB, yA, yB = piso(xA, xB, yA, yB, 1)
    pisoAC, xA, xB, yA, yB = piso(xA, xB, yA, yB, 0)
    pisoBC, xA, xB, yA, yB = piso(xA, xB, yA, yB, 1)
    pisoAD, xA, xB, yA, yB = piso(xA, xB, yA, yB, 0)
    pisoBD, xA, xB, yA, yB = piso(xA, xB, yA, yB, 1)
    pisoAE, xA, xB, yA, yB = piso(xA, xB, yA, yB, 0)
    pisoBE, xA, xB, yA, yB = piso(xA, xB, yA, yB, 1)
    
    
    #techo 1ra estructura
    pisoDA = [
        #x  y  z
        (0, 4, 0), (0, 4, 10), (4, 4, 10), (4, 4, 0),
    ]
    #piso 2da estructura
    pisoDB = [
        #x  y  z
        (0, 0, 12), (4, 0, 12), (4, 0, 20), (0, 0, 20),
    ]
    #techo 2da estructura
    pisoDB0 = [
        #x  y  z
        (0, 4, 12), (4, 4, 12), (4, 4, 20), (0, 4, 20),
    ]
    #lava
    pisoDC = [
        #x  y  z
        (1, 1, 1),(1, 1, 2),  (2, 1, 2),(2, 1, 1), 
    ]
    #agua1
    pisoDD =[
        (2, 1, 13),(4, 1, 13),(4, 1, 14),(2, 1, 14), 
    ]
    #agua2
    pisoDE =[
        (0, 1, 16),(2, 1, 16),(2, 1, 17),(0, 1, 17), 
    ]
    #altar
    pisoDF =[
        (1, 1, 18),(2, 1, 18),(2, 1, 19),(1, 1, 19), 
    ]
    
    #Extremos
    wallA=pared(0,0,0,4,0,4)
    wallB=pared(4,0,0,0,10,4)
    wallC=pared(0,0,0,0,10,4)
    wallD=pared(0,0,10,4,0,4)
    #Primer obstaculo
    wallE=pared(1,0,1,3,0,4)
    wallF=pared(1,0,1,0,3,4)
    wallG=pared(1,0,4,2,0,4)
    #Obstaculo dentro de obstaculo
    wallH=pared(2,0,3,2,0,4)
    wallI=pared(1,0,2,2,0,4)
    #Obstaculo, la secuela
    wallJ=pared(0,0,5,3,0,4)
    wallK=pared(1,0,6,3,0,4)
    #Ultimate Obstaculo
    wallM=pared(0,0,7,2,0,4)
    wallN=pared(3,0,7,1,0,4)
    #Altar
    wallO=pared(1,0,18,1,0,1)
    wallP=pared(1,0,18,0,1,1)
    wallQ=pared(1,0,19,1,0,1)
    wallR=pared(2,0,18,0,1,1)
    
    #cofre
    #wallC1=pared(1,0,9,2,0,1)
    #wallC2=pared(1,0,10,2,0,1)
    #wallC3=pared(1,0,9,0,1,1)
    #wallC4=pared(3,0,9,0,1,1)
    
    #Lava
    wallS=pared(2,0,1,0,1,1)
    wallS1=pared(1,0,1,0,1,1)
    wallS2=pared(1,0,1,1,0,1)
    wallS3=pared(1,0,2,1,0,1)
    
    #Otro piso
    wallX=pared(0,0,12,0,8,4)
    wallY=pared(4,0,12,0,8,4)
    wallZ=pared(0,0,20,4,0,4)
    wallZ0=pared(0,0,12,4,0,4)
    #Obstaculos
    wallZ1=pared(4,0,13,-2,0,1)
    wallZ10=pared(4,0,14,-2,0,1)
    wallZ11=pared(4,0,13,0,1,1)
    wallZ12=pared(2,0,13,0,1,1)
    
    
    wallZ4=pared(0,0,16,2,0,1)
    wallZ40=pared(0,0,16,0,1,1)
    wallZ41=pared(2,0,16,0,1,1)
    wallZ42=pared(0,0,17,2,0,1)

    w = wallA+wallB+wallC+wallD+wallE+wallF+wallG+wallH+wallI+wallJ+wallK+wallM+wallN
    l=wallS+wallS1+wallS2+wallS3
    e=wallO+wallP+wallQ+wallR
    s2=wallX+wallY+wallZ+wallZ0
    pz=wallZ1+wallZ4+wallZ10+wallZ11+wallZ12+wallZ40+wallZ41+wallZ42
    #pisoBA = [
    #    #x  y  z
    #    (4, 0, 0), (2, 0, 0), (2, 0, 2), (4, 0, 2),
    #]
    #pisoAB = [
    #    #x  y  z
    #    (2, 0, 2), (0, 0, 2), (0, 0, 4), (2, 0, 4),
    #]
    #pisoBB = [
    #    #x  y  z
    #    (4, 0, 2), (2, 0, 2), (2, 0, 4), (4, 0, 4),
    #]
    #pisoAC = [
    #    #x  y  z
    #    (2, 0, 4), (0, 0, 4), (0, 0, 6), (2, 0, 6),
    #]
    #pisoBC = [
    #    #x  y  z
    #    (4, 0, 4), (2, 0, 4), (2, 0, 6), (4, 0, 6),
    #]
    #pisoC = [
    #    #x  y  z
    #    (5, 0, 6), (0, 0, 6), (0, 0, 9), (5, 0, 9),
    #]
    #
    tex_coords = (
        (1, 1), (1, 0), (0, 0), (0, 1),
    )
    
    clock = pygame.time.Clock()
    running = True

    pygame.mouse.set_pos(screen.get_width() // 2, screen.get_height() // 2)  # Centrar el cursor al inicio
    pygame.mouse.set_visible(False)  # Ocultar el cursor
    
    Model = 'model.txt'
    atravesar = labBin(Model)
    
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0
                    #close_window_and_run_script("Python/menu.py")
            handle_mouse(camera, event)

        handle_events(camera)
        pygame.mouse.set_pos(screen.get_width() // 2, screen.get_height() // 2)

        # Obtener la posición del cursor
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        camera.rotate(mouse_dx * 0.2, mouse_dy * 0.2)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        camera.update()
        # Dibujar ejes
        #draw_axes(15.0)
        
        glBindTexture(GL_TEXTURE_2D,superficie)
        
        renPiso(pisoAA, tex_coords)
        renPiso(pisoBA, tex_coords)
        renPiso(pisoAB, tex_coords)
        renPiso(pisoBB, tex_coords)
        renPiso(pisoAC, tex_coords)
        renPiso(pisoBC, tex_coords)
        renPiso(pisoAD, tex_coords)
        renPiso(pisoBD, tex_coords)
        renPiso(pisoAE, tex_coords)
        renPiso(pisoBE, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,frontEnd)
        renPiso(pisoDF, tex_coords)
        
        
        glBindTexture(GL_TEXTURE_2D,agua)
        renPiso(pisoDD, tex_coords)
        renPiso(pisoDE, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,lava)
        renPiso(pisoDC, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,atardecer)
        renPiso(pisoDA, tex_coords)  
        
        glBindTexture(GL_TEXTURE_2D,pisoEnd)
        renPiso(pisoDB, tex_coords)
        renPiso(pisoDB0, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,wall)
        renPiso(w, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,lava)
        renPiso(l, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,end)
        renPiso(e, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,paredEnd)
        renPiso(s2, tex_coords)
        
        glBindTexture(GL_TEXTURE_2D,pezPlata)
        renPiso(pz, tex_coords)
        
        golem.render()
        golem2.render()
        cofre.render()
        ghast.render()
        if (camera.pos[0] > 2 and camera.pos[0] < 4) and (camera.pos[2] > 13 and camera.pos[2] < 14):
            mostrar_ventana_perder()
            camera.pos[0] = 3.5
            camera.pos[2] = 0.5
        if (camera.pos[0] > 0 and camera.pos[0] < 2) and (camera.pos[2] > 16 and camera.pos[2] < 17):
            mostrar_ventana_perder()
            camera.pos[0] = 3.5
            camera.pos[2] = 0.5

        if (camera.pos[0] > 1 and camera.pos[0] < 3) and (camera.pos[2] > 9 and camera.pos[2] < 10):
            camera.pos[0] = 0.5
            camera.pos[2] = 13.0
            print("TPA")
        if (camera.pos[0] > 1 and camera.pos[0] < 2) and (camera.pos[2] > 18 and camera.pos[2] < 19):
            print("Gano")
            mostrar_ventana_ganar()
        if (camera.pos[0] > 1 and camera.pos[0] < 2) and (camera.pos[2] > 1 and camera.pos[2] < 2):
            mostrar_ventana_perder()
            camera.pos[0] = 3.5
            camera.pos[2] = 0.5
        
        if (round(camera.pos[0]) - camera.pos[0]) > 0: #Esta en la parte arriba del bloque
            if (round(camera.pos[2]) - camera.pos[2]) > 0: #Esta del lado izquierdo del bloque
                if (round(camera.pos[2])-1) != cam[1]:
                    if ((round(camera.pos[2]) - 1) - cam[1]) < 0:
                        print("Cambio hacia la izquierda arriba")
                        #print(f"{(anchoAB[round(camera.pos[0]) - 1])} - {(largoBB[round(camera.pos[2])])}")
                        print((atravesar[(anchoAB[round(camera.pos[0]) - 1])][(largoBB[round(camera.pos[2])])]))
                        if ((atravesar[(anchoAB[round(camera.pos[0]) - 1])][(largoBB[round(camera.pos[2])])]) == "0"):
                            print("pasa")
                            cam[1] = round(camera.pos[2]) - 1
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
                if (round(camera.pos[0]) - 1) != cam[0]:
                    if ((round(camera.pos[0]) - 1) - cam[0]) < 0:
                        print("Cambio hacia abajo (CAD)")
                        #print(atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2]) - 1])])
                        if((atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2]) - 1])]) == "0"):
                            print("pasa")
                            cam[0] = round(camera.pos[0]) - 1
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
            else: #Esta del lado derecho
                if (round(camera.pos[2])) != cam[1]:
                    if ((round(camera.pos[2])) - cam[1]) > 0:
                        print("Cambio hacia la derecha arriba")
                        #print(f"{(anchoAB[round(camera.pos[0]) - 1])} - {(largoBB[round(camera.pos[2])])}")
                        print((atravesar[(anchoAB[round(camera.pos[0]) - 1])][(largoBB[round(camera.pos[2])])]))
                        if ((atravesar[(anchoAB[round(camera.pos[0]) - 1])][(largoBB[round(camera.pos[2])])]) == "0"):
                            print("pasa")
                            cam[1] = round(camera.pos[2])
                            #print(f"{cam[1]} - {round(camera.pos[2]) - 1}")
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
                if (round(camera.pos[0]) - 1) != cam[0]:
                    if ((round(camera.pos[0]) - 1) - cam[0]) < 0:
                        print("Cambio hacia abajo (CAI)")
                        #print(atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2])])])
                        if((atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2])])]) == "0"):
                            print("pasa")
                            print(f"A: {cam[0]} - {cam[1]}")
                            cam[0] = round(camera.pos[0]) - 1
                            #cam[1] = round(camera.pos[2]) - 1
                            print(f"B: {cam[0]} - {cam[1]}")
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
        else: #Esta en la parte abajo del bloque
            #print(round(camera.pos[2]) - camera.pos[2])
            if (round(camera.pos[2]) - camera.pos[2]) > 0: #Esta del lado derecho del bloque
                if (round(camera.pos[2])-1) != cam[1]:
                    if ((round(camera.pos[2])-1) - cam[1]) < 0:
                        print("Cambio hacia la izquierda abajo")
                        #print(f"{(anchoAB[round(camera.pos[0]) - 1])} - {(largoBB[round(camera.pos[2])])}")
                        print((atravesar[(anchoAB[round(camera.pos[0])])][(largoBB[round(camera.pos[2])])]))
                        if ((atravesar[(anchoAB[round(camera.pos[0])])][(largoBB[round(camera.pos[2])])]) == "0"):
                            print("pasa")
                            cam[1] = round(camera.pos[2]) - 1
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
                if (round(camera.pos[0])) != cam[0]:
                    if ((round(camera.pos[0])) - cam[0]) > 0:
                        print("Cambio hacia arriba (CAD)")
                        #print(atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2])-1])])
                        if (atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2])-1])] == "0"):
                            print("pasa")
                            #print(f"A: {cam[0]} - {cam[1]}")
                            cam[0] = round(camera.pos[0])
                            #cam[1] = round(camera.pos[2])
                            #print(f"B: {cam[0]} - {cam[1]}")
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
            else:
                if (round(camera.pos[2])) != cam[1]:
                    if ((round(camera.pos[2])) - cam[1]) > 0:
                        print("Cambio hacia la derecha abajo")
                        #print(f"{(anchoAB[round(camera.pos[0]) - 1])} - {(largoBB[round(camera.pos[2])])}")
                        print((atravesar[(anchoAB[round(camera.pos[0])])][(largoBB[round(camera.pos[2])])]))
                        if ((atravesar[(anchoAB[round(camera.pos[0])])][(largoBB[round(camera.pos[2])])]) == "0"):
                            print("pasa")
                            cam[1] = round(camera.pos[2])
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]
                if (round(camera.pos[0])) != cam[0]:
                    if ((round(camera.pos[0])) - cam[0]) > 0:
                        print("Cambio hacia arriba (CAI)")
                        #print(atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2])])])
                        if (atravesar[(anchoAA[(round(camera.pos[0]))])][(largoAA[round(camera.pos[2])])] == "0"):
                            print("pasa")
                            #print(f"A: {cam[0]} - {cam[1]}")
                            cam[0] = round(camera.pos[0])
                            #cam[1] = round(camera.pos[2])
                            #print(f"B: {cam[0]} - {cam[1]}")
                        else:
                            print("no pasa")
                            camera.pos[0] = posCam[0]
                            camera.pos[2] = posCam[1]

        #print(cam)

        posCam[0] = camera.pos[0]
        posCam[1] = camera.pos[2]
        
        pygame.display.flip()
        clock.tick(60)
    pygame.mouse.set_visible(True)  # Mostrar el cursor al salir
    pygame.quit()

if __name__ == "__main__":
    main()