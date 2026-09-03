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
PAPEL = srgb(238, 233, 224)
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
    bpy.ops.object.shade_smooth_by_angle() if hasattr(
        bpy.ops.object, "shade_smooth_by_angle") else None
    return o


def moneda(nombre, pos, radio, alto, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radio,
                                        depth=alto, location=pos)
    o = bpy.context.object
    o.name = nombre
    o.data.materials.append(mat)
    bpy.ops.object.modifier_add(type="BEVEL")
    o.modifiers["Bevel"].width = min(0.02, alto * 0.18)
    o.modifiers["Bevel"].segments = 3
    return o


def pila(prefijo, x, n, mat, radio=1.15, alto=0.17, sep=0.015):
    """Una torre de monedas. Cada una gira un poco: apiladas a mano."""
    for i in range(n):
        z = 0.16 + alto / 2 + i * (alto + sep)
        o = moneda(f"{prefijo}_{i}", (x, 0.0, z), radio, alto, mat)
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
    # que apunte al origen
    dx, dy, dz = -pos[0], -pos[1], -pos[2]
    o.rotation_euler = (math.acos(dz / math.sqrt(dx*dx + dy*dy + dz*dz)),
                        0.0, math.atan2(dy, dx) + math.pi / 2)
    return o


def montar():
    limpiar()

    m_papel = material("papel", PAPEL, rugosidad=0.62)
    m_frio = material("depositos", FRIO, rugosidad=0.35, metal=0.25)
    m_rojo = material("prestamos", ROJO, rugosidad=0.38, metal=0.15)
    m_margen = material("margen", AMBAR, rugosidad=0.2, emision=9.0)
    m_suelo = material("suelo", NOCHE, rugosidad=0.85)

    # el suelo, para que la hoja no flote en negro
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.001))
    bpy.context.object.data.materials.append(m_suelo)

    # LA HOJA DE CALCULO: una losa de papel
    hoja = caja("hoja", (0, 0, 0.08), (5.6, 3.6, 0.08), m_papel)
    bpy.ops.object.modifier_add(type="BEVEL")
    hoja.modifiers["Bevel"].width = 0.03
    hoja.modifiers["Bevel"].segments = 3

    # las dos columnas
    pila("deposito", -2.45, 9, m_frio)
    pila("prestamo", 2.45, 7, m_rojo)

    # EL MARGEN: finisimo, y es lo unico que emite luz propia
    caja("margen", (0, 0, 0.95), (0.045, 3.05, 0.78), m_margen)

    # un par de laminas mas bajas, para que la hoja no quede vacia en medio
    for i, y in enumerate((-2.1, 2.1)):
        caja(f"renglon_{i}", (0, y, 0.19), (4.4, 0.045, 0.02), m_frio)

    luz("clave", (6.5, -7.0, 9.0), 2600, 7.0, (1.0, 0.95, 0.88))
    luz("relleno", (-8.0, -4.0, 4.5), 700, 9.0, (0.72, 0.80, 1.0))
    luz("contra", (-3.0, 8.0, 5.0), 1400, 6.0, (1.0, 0.72, 0.45))

    # camara ortografica: el isometrico de verdad, sin fuga de perspectiva
    bpy.ops.object.camera_add(location=(11.0, -11.0, 9.2))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 13.5
    cam.rotation_euler = (math.radians(58.0), 0.0, math.radians(45.0))
    bpy.context.scene.camera = cam

    mundo = bpy.context.scene.world
    if mundo is None:
        mundo = bpy.data.worlds.new("mundo")
        bpy.context.scene.world = mundo
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs[0].default_value = NOCHE
    mundo.node_tree.nodes["Background"].inputs[1].default_value = 1.0


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
    e.render.filepath = SALIDA
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"escrito {SALIDA}.png")


if __name__ == "__main__":
    montar()
    renderizar()
