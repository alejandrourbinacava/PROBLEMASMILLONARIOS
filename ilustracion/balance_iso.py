#!/usr/bin/env python3
"""
La hoja de calculo del banco, en isometrico. Se ejecuta dentro de Blender:

    blender -b -P ilustracion/balance_iso.py

No abre ventana y no toca la GPU: Cycles en CPU, que es lo unico que hay en
un runner de Actions. Es una ILUSTRACION FIJA, no un plano de video. Un
fotograma cuesta minutos; diez mil no caben en ningun sitio. El movimiento
se lo pone Remotion despues, con camara y parallax sobre el PNG.

La escena dice la frase del guion: a un lado lo depositado, al otro lo
prestado, y en medio un margen muy fino -la lamina ambar que brilla-.
"""
import math
import os
import sys

import bpy

W, H = 1920, 1080
MUESTRAS = 160
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "salida", "c_blender")


def srgb(r, g, b, a=1.0):
    """De 0-255 sRGB a lineal, que es lo que come Blender."""
    def c(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(r), c(g), c(b), a)


AMBAR = srgb(255, 176, 60)
ROJO = srgb(232, 86, 64)
PAPEL = srgb(198, 192, 180)
FRIO = srgb(122, 146, 178)
NOCHE = srgb(9, 13, 24)


def limpiar():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for bloque in (bpy.data.meshes, bpy.data.materials, bpy.data.lights):
        for d in list(bloque):
            if d.users == 0:
                bloque.remove(d)


def material(nombre, color, rugosidad=0.5, metal=0.0, emision=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rugosidad
    p.inputs["Metallic"].default_value = metal
    if emision:
        # El nombre del socket cambio entre versiones de Blender.
        for clave in ("Emission Color", "Emission"):
            if clave in p.inputs:
                p.inputs[clave].default_value = color
                break
        if "Emission Strength" in p.inputs:
            p.inputs["Emission Strength"].default_value = emision
    return m


def caja(nombre, pos, escala, mat):
    bpy.ops.mesh.primitive_cube_add(size=2, location=pos)
    o = bpy.context.object
    o.name = nombre
    o.scale = escala
    o.data.materials.append(mat)
    return o


def moneda(nombre, pos, radio, alto, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=radio,
                                        depth=alto, location=pos)
    o = bpy.context.object
    o.name = nombre
    o.data.materials.append(mat)
    bpy.ops.object.modifier_add(type="BEVEL")
    o.modifiers["Bevel"].width = min(0.02, alto * 0.18)
    o.modifiers["Bevel"].segments = 3
    return o


def pila(prefijo, x, y, n, mat, radio=1.15, alto=0.17, sep=0.015):
    """Una torre de monedas. Cada una gira un poco: apiladas a mano."""
    for i in range(n):
        z = 0.16 + alto / 2 + i * (alto + sep)
        o = moneda(f"{prefijo}_{i}", (x, y, z), radio, alto, mat)
        o.rotation_euler[2] = math.radians(i * 11.0)
        o.location[0] += math.sin(i * 1.7) * 0.035
        o.location[1] += math.cos(i * 2.1) * 0.035


def luz(nombre, pos, energia, tam, color=(1, 1, 1)):
    d = bpy.data.lights.new(nombre, type="AREA")
    d.energy = energia
    d.size = tam
    d.color = color
    o = bpy.data.objects.new(nombre, d)
    bpy.context.collection.objects.link(o)
    o.location = pos

    # Apuntar al origen. Una luz de area emite por su -Z local, asi que hay
    # que resolver que rotacion lleva (0,0,-1) hasta la direccion d. Sale
    #     rx = acos(-dz/L)      rz = atan2(-dx, dy)
    # y NO acos(dz/L) con atan2(dy,dx), que es lo que habia: eso las dejaba
    # apuntando justo al lado contrario. Con el emisor fuerte no se noto
    # -iluminaba el solo-, y al bajarlo la escena se quedo negra.
    dx, dy, dz = -pos[0], -pos[1], -pos[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    o.rotation_euler = (math.acos(-dz / L), 0.0, math.atan2(-dx, dy))
    return o


def montar():
    limpiar()

    m_papel = material("papel", PAPEL, rugosidad=0.62)
    m_frio = material("depositos", FRIO, rugosidad=0.35, metal=0.25)
    m_rojo = material("prestamos", ROJO, rugosidad=0.38, metal=0.15)
    m_margen = material("margen", AMBAR, rugosidad=0.2, emision=3.2)
    m_suelo = material("suelo", NOCHE, rugosidad=0.85)

    # el suelo, para que la hoja no flote en negro
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.001))
    bpy.context.object.data.materials.append(m_suelo)

    # LA HOJA DE CALCULO: una losa de papel
    hoja = caja("hoja", (0, 0, 0.08), (3.9, 3.9, 0.08), m_papel)
    bpy.ops.object.modifier_add(type="BEVEL")
    hoja.modifiers["Bevel"].width = 0.03
    hoja.modifiers["Bevel"].segments = 3

    # Las dos columnas van en la diagonal CONTRARIA a la de la camara. En la
    # misma se tapan la una a la otra: en isometrico esa es la profundidad.
    D = 1.95
    pila("deposito", -D, D, 9, m_frio)
    pila("prestamo", D, -D, 6, m_rojo)

    # EL MARGEN. La frase dice "muy fino", asi que fino de verdad: una lamina
    # baja entre las dos pilas. Antes era un muro de 0,78 de alto emitiendo a
    # 9 y se comia la escena entera -de ahi que todo saliera naranja-.
    caja("margen", (0, 0, 0.44), (0.78, 0.05, 0.28), m_margen)

    # dos renglones impresos, en la diagonal de la camara para que se lean
    for i, s in enumerate((-1, 1)):
        caja(f"renglon_{i}", (s * 1.45, s * 1.45, 0.17), (2.5, 0.03, 0.014),
             m_frio)

    luz("clave", (6.5, -7.0, 9.0), 1500, 7.0, (1.0, 0.95, 0.88))
    luz("relleno", (-8.0, -4.0, 4.5), 420, 9.0, (0.72, 0.80, 1.0))
    luz("contra", (-3.0, 8.0, 5.0), 750, 6.0, (1.0, 0.72, 0.45))

    # camara ortografica: el isometrico de verdad, sin fuga de perspectiva
    bpy.ops.object.camera_add(location=(11.0, -11.0, 9.2))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 13.6
    # La camara mira al origen, pero el peso de la escena esta por encima:
    # la pila de depositos sube casi dos unidades. Sin este desplazamiento
    # se corta por arriba y sobra hoja vacia por abajo.
    cam.data.shift_y = 0.115
    cam.rotation_euler = (math.radians(58.0), 0.0, math.radians(45.0))
    bpy.context.scene.camera = cam

    mundo = bpy.context.scene.world
    if mundo is None:
        mundo = bpy.data.worlds.new("mundo")
        bpy.context.scene.world = mundo
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs[0].default_value = NOCHE
    mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.30


def renderizar():
    e = bpy.context.scene
    e.render.engine = "CYCLES"
    e.cycles.device = "CPU"
    e.cycles.samples = MUESTRAS
    e.cycles.use_denoising = True
    e.render.resolution_x = W
    e.render.resolution_y = H
    e.render.resolution_percentage = 100
    e.render.image_settings.file_format = "PNG"
    e.view_settings.view_transform = "AgX"
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)

    # Una horquilla, no una apuesta. Calcular la exposicion de cabeza es
    # adivinar; tres renders de una escena tan simple cuestan lo mismo que
    # equivocarse una vez, y de la horquilla se elige mirando.
    for ev, sufijo in ((-1.2, "_oscuro"), (0.0, ""), (1.2, "_claro")):
        e.view_settings.exposure = ev
        e.render.filepath = SALIDA + sufijo
        bpy.ops.render.render(write_still=True)
        print(f"escrito {SALIDA}{sufijo}.png  (EV {ev:+.1f})")


if __name__ == "__main__":
    montar()
    renderizar()
