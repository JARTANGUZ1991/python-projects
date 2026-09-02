"""
=============================================================
  ПОСТСОВЕТСКАЯ 9-ЭТАЖКА  —  Blender Python Script
=============================================================
  Как запустить:
  1. Открой Blender
  2. Перейди во вкладку  Scripting
  3. Нажми  Open  и выбери этот файл
     (или вставь содержимое в текстовый редактор Blender)
  4. Нажми  ► Run Script
  5. Модель появится в 3D Viewport
=============================================================
"""

import bpy
import math

# ─────────────────────────────────────────────────────────────
#  ОЧИСТКА СЦЕНЫ
# ─────────────────────────────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh)


# ─────────────────────────────────────────────────────────────
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────────────────────
def make_mat(name, color, roughness=0.85, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value  = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value   = roughness
    bsdf.inputs["Metallic"].default_value    = metallic
    return mat


def add_box(name, w, d, h, cx, cy, bz, mat):
    """
    Создаёт параллелепипед.
    cx, cy — центр по X/Y; bz — нижняя грань по Z.
    """
    hw, hd = w / 2, d / 2
    verts = [
        (cx-hw, cy-hd, bz),     (cx+hw, cy-hd, bz),
        (cx+hw, cy+hd, bz),     (cx-hw, cy+hd, bz),
        (cx-hw, cy-hd, bz+h),   (cx+hw, cy-hd, bz+h),
        (cx+hw, cy+hd, bz+h),   (cx-hw, cy+hd, bz+h),
    ]
    faces = [
        (0,1,2,3),  # дно
        (4,7,6,5),  # крыша
        (0,1,5,4),  # перед
        (1,2,6,5),  # право
        (2,3,7,6),  # зад
        (3,0,4,7),  # лево
    ]
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj  = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    if mat:
        obj.data.materials.append(mat)
    return obj


# ─────────────────────────────────────────────────────────────
#  МАТЕРИАЛЫ
# ─────────────────────────────────────────────────────────────
M_CONCRETE  = make_mat("M_Concrete",  (0.76, 0.73, 0.68))
M_PANEL     = make_mat("M_Panel",     (0.82, 0.79, 0.74))
M_SEAM      = make_mat("M_Seam",      (0.55, 0.53, 0.50))
M_WINDOW    = make_mat("M_Window",    (0.40, 0.58, 0.78), roughness=0.05, metallic=0.1)
M_FRAME     = make_mat("M_Frame",     (0.90, 0.90, 0.88), roughness=0.6)
M_BALCONY   = make_mat("M_Balcony",   (0.68, 0.65, 0.61))
M_BAL_RAIL  = make_mat("M_BalRail",   (0.80, 0.80, 0.78), roughness=0.4, metallic=0.6)
M_ROOF      = make_mat("M_Roof",      (0.48, 0.46, 0.43))
M_DOOR      = make_mat("M_Door",      (0.22, 0.28, 0.22))
M_STAIR     = make_mat("M_Stairwell", (0.72, 0.70, 0.66))
M_GROUND    = make_mat("M_Ground",    (0.23, 0.20, 0.16))
M_ASPHALT   = make_mat("M_Asphalt",   (0.28, 0.27, 0.26))
M_VENT      = make_mat("M_Vent",      (0.60, 0.58, 0.55))


# ─────────────────────────────────────────────────────────────
#  ПАРАМЕТРЫ ЗДАНИЯ
# ─────────────────────────────────────────────────────────────
FLOORS       = 9
FL0_H        = 3.0      # высота 1-го этажа (выше остальных)
FLN_H        = 2.8      # высота типового этажа
BLD_W        = 60.0     # ширина по X
BLD_D        = 12.0     # глубина по Y
BASE_Z       = 0.0

TOTAL_H = FL0_H + (FLOORS - 1) * FLN_H   # ~27.2 м

# Вспомогательная функция: Z нижней грани этажа
def floor_z(fl):
    if fl == 0:
        return BASE_Z
    return BASE_Z + FL0_H + (fl - 1) * FLN_H

def floor_h(fl):
    return FL0_H if fl == 0 else FLN_H


# ─────────────────────────────────────────────────────────────
#  1. ОСНОВНОЙ КОРПУС
# ─────────────────────────────────────────────────────────────
add_box("MainBody", BLD_W, BLD_D, TOTAL_H, 0, 0, BASE_Z, M_CONCRETE)


# ─────────────────────────────────────────────────────────────
#  2. ГОРИЗОНТАЛЬНЫЕ МЕЖПАНЕЛЬНЫЕ ШВЫ
# ─────────────────────────────────────────────────────────────
for fl in range(1, FLOORS):
    z = floor_z(fl)
    add_box(f"HSeam_{fl}", BLD_W + 0.06, BLD_D + 0.06, 0.07,
            0, 0, z - 0.035, M_SEAM)


# ─────────────────────────────────────────────────────────────
#  3. ВЕРТИКАЛЬНЫЕ ШВЫ (секции)
# ─────────────────────────────────────────────────────────────
# Здание делится на 3 секции по ~20 м
for vx in [-20.0, 0.0, 20.0]:
    add_box(f"VSeam_{vx:.0f}", 0.07, BLD_D + 0.06, TOTAL_H,
            vx, 0, BASE_Z, M_SEAM)


# ─────────────────────────────────────────────────────────────
#  4. ОКНА И РАМЫ
# ─────────────────────────────────────────────────────────────
WIN_W    = 1.40
WIN_H    = 1.30
WIN_DEEP = 0.14    # глубина проёма (окно утоплено)

# Центры секций и смещения окон внутри секции
SECTION_CX = [-20.0, 0.0, 20.0]
WIN_OFF    = [-7.5, -2.5, 2.5, 7.5]   # 4 окна на секцию (12 по фасаду)

WIN_XS = [sc + wo for sc in SECTION_CX for wo in WIN_OFF]

FRONT_Y = -(BLD_D / 2 + WIN_DEEP / 2)
BACK_Y  =  (BLD_D / 2 + WIN_DEEP / 2)
FR_T    = 0.07    # толщина рамы

for fl in range(FLOORS):
    fz = floor_z(fl)
    fh = floor_h(fl)
    wz = fz + fh * 0.55 - WIN_H / 2   # вертикальная позиция окна

    for i, wx in enumerate(WIN_XS):
        for fy in (FRONT_Y, BACK_Y):
            tag = f"fl{fl}_w{i}_{'F' if fy < 0 else 'B'}"

            # Стекло
            add_box(f"Glass_{tag}", WIN_W, WIN_DEEP, WIN_H,
                    wx, fy, wz, M_WINDOW)

            # Рамы
            fd = WIN_DEEP + 0.05
            # верхняя
            add_box(f"FrameTop_{tag}", WIN_W + FR_T*2, fd, FR_T,
                    wx, fy, wz + WIN_H, M_FRAME)
            # нижняя (подоконник чуть шире)
            add_box(f"FrameBot_{tag}", WIN_W + FR_T*2 + 0.06, fd + 0.04, FR_T,
                    wx, fy, wz - FR_T, M_FRAME)
            # левая стойка
            add_box(f"FrameL_{tag}", FR_T, fd, WIN_H + FR_T * 2,
                    wx - WIN_W/2 - FR_T/2, fy, wz - FR_T, M_FRAME)
            # правая стойка
            add_box(f"FrameR_{tag}", FR_T, fd, WIN_H + FR_T * 2,
                    wx + WIN_W/2 + FR_T/2, fy, wz - FR_T, M_FRAME)
            # средний импост (Т-образная рама)
            add_box(f"FrameMid_{tag}", FR_T, fd, WIN_H,
                    wx, fy, wz, M_FRAME)

    # Окна лестничных клеток (между секциями, узкие вертикальные)
    for sx in [-10.0, 10.0]:
        for fy in (FRONT_Y, BACK_Y):
            stag = f"stair_fl{fl}_{'F' if fy < 0 else 'B'}_x{sx:.0f}"
            add_box(f"StairGlass_{stag}", 0.75, WIN_DEEP, WIN_H + 0.5,
                    sx, fy, wz - 0.15, M_WINDOW)
            add_box(f"StairFrame_{stag}", 0.75 + FR_T*2, WIN_DEEP+0.05, WIN_H + 0.5 + FR_T*2,
                    sx, fy, wz - 0.15 - FR_T, M_FRAME)


# ─────────────────────────────────────────────────────────────
#  5. БАЛКОНЫ (2–9 этажи, крайние окна каждой секции)
# ─────────────────────────────────────────────────────────────
BAL_OFFSETS = [-7.5, 7.5]   # крайние окна секции
FRONT_FACE  = -(BLD_D / 2)

for fl in range(1, FLOORS):
    fz = floor_z(fl)

    for sc in SECTION_CX:
        for bo in BAL_OFFSETS:
            bx = sc + bo
            by_center = FRONT_FACE - 0.75   # центр балконной плиты

            # Балконная плита
            add_box(f"BalSlab_fl{fl}_x{bx:.0f}", 2.2, 1.5, 0.14,
                    bx, by_center, fz - 0.14, M_BALCONY)

            # Ограждение — передняя стенка
            add_box(f"BalFront_fl{fl}_x{bx:.0f}", 2.2, 0.08, 1.0,
                    bx, FRONT_FACE - 1.46, fz, M_BAL_RAIL)
            # Боковые стенки
            add_box(f"BalSideL_fl{fl}_x{bx:.0f}", 0.08, 1.5, 1.0,
                    bx - 1.1, by_center, fz, M_BAL_RAIL)
            add_box(f"BalSideR_fl{fl}_x{bx:.0f}", 0.08, 1.5, 1.0,
                    bx + 1.1, by_center, fz, M_BAL_RAIL)

            # Тонкие вертикальные стойки ограждения
            for si in range(5):
                sx = bx - 1.0 + si * 0.5
                add_box(f"BalPost_fl{fl}_x{bx:.0f}_s{si}", 0.04, 0.04, 1.0,
                        sx, FRONT_FACE - 1.46, fz, M_BAL_RAIL)


# ─────────────────────────────────────────────────────────────
#  6. ЛЕСТНИЧНЫЕ КЛЕТКИ (выступают на торцах секций)
# ─────────────────────────────────────────────────────────────
for si, sx in enumerate([-10.0, 10.0]):
    # Выступающий объём лестничной клетки
    add_box(f"Stairwell_{si}", 3.2, 1.6, TOTAL_H,
            sx, -(BLD_D / 2 + 0.8), BASE_Z, M_STAIR)


# ─────────────────────────────────────────────────────────────
#  7. ПОДЪЕЗДЫ — КОЗЫРЬКИ И СТУПЕНИ
# ─────────────────────────────────────────────────────────────
for si, sx in enumerate([-10.0, 10.0]):
    porch_y = -(BLD_D / 2 + 2.2)

    # Козырёк
    add_box(f"Canopy_{si}", 4.0, 2.2, 0.18,
            sx, porch_y - 0.4, BASE_Z + FL0_H - 0.45, M_ROOF)
    # Опоры козырька
    for ox in [-1.5, 1.5]:
        add_box(f"CanopyPole_{si}_{'L' if ox<0 else 'R'}", 0.12, 0.12, FL0_H - 0.45,
                sx + ox, porch_y - 1.0, BASE_Z, M_CONCRETE)

    # Ступени (3 шт.)
    for step in range(3):
        sw = 3.2 - step * 0.25
        sd = 0.36
        add_box(f"Step_{si}_{step}", sw, sd, 0.17,
                sx, -(BLD_D/2 + 1.6 + 1.55) + sd * (2 - step),
                BASE_Z + 0.17 * step, M_CONCRETE)

    # Дверной проём (тёмная вставка)
    add_box(f"Door_{si}", 1.05, 0.15, 2.3,
            sx, -(BLD_D / 2 + 0.08), BASE_Z, M_DOOR)
    # Дверная рама
    add_box(f"DoorFrame_{si}", 1.20, 0.18, 2.45,
            sx, -(BLD_D / 2 + 0.06), BASE_Z, M_FRAME)


# ─────────────────────────────────────────────────────────────
#  8. КРЫША
# ─────────────────────────────────────────────────────────────
roof_z = BASE_Z + TOTAL_H

# Парапет
add_box("Parapet", BLD_W + 0.5, BLD_D + 0.5, 0.65,
        0, 0, roof_z, M_ROOF)

# Кровельная плита
add_box("RoofSlab", BLD_W + 0.25, BLD_D + 0.25, 0.22,
        0, 0, roof_z + 0.65, M_CONCRETE)

# Вентиляционные шахты
for vx, vy in [(-24, -3), (-4, 2), (16, -3), (16, 3)]:
    add_box(f"VentShaft_{vx}_{vy}", 1.3, 1.3, 2.8,
            vx, vy, roof_z + 0.87, M_VENT)
    add_box(f"VentCap_{vx}_{vy}", 1.7, 1.7, 0.15,
            vx, vy, roof_z + 0.87 + 2.8, M_ROOF)

# Лифтовая шахта (по центру, немного выше)
add_box("LiftShaft", 3.5, 3.5, 4.5, 0, 0, roof_z + 0.87, M_STAIR)
add_box("LiftCap",   3.8, 3.8, 0.2, 0, 0, roof_z + 0.87 + 4.5, M_ROOF)


# ─────────────────────────────────────────────────────────────
#  9. ЦОКОЛЬ
# ─────────────────────────────────────────────────────────────
add_box("Plinth", BLD_W + 0.2, BLD_D + 0.2, 0.6,
        0, 0, BASE_Z - 0.6, M_SEAM)


# ─────────────────────────────────────────────────────────────
# 10. ЗЕМЛЯ И АСФАЛЬТ
# ─────────────────────────────────────────────────────────────
add_box("Ground", 150, 100, 0.4, 0, 8, BASE_Z - 1.0, M_GROUND)
add_box("Pavement", BLD_W + 20, 10, 0.06,
        0, -(BLD_D / 2 + 5), BASE_Z, M_ASPHALT)


# ─────────────────────────────────────────────────────────────
# 11. КАМЕРА
# ─────────────────────────────────────────────────────────────
cam_data = bpy.data.cameras.new("Camera")
cam_obj  = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location        = (60, -72, 32)
cam_obj.rotation_euler  = (math.radians(68), 0, math.radians(47))
cam_data.lens           = 35
bpy.context.scene.camera = cam_obj


# ─────────────────────────────────────────────────────────────
# 12. ОСВЕЩЕНИЕ
# ─────────────────────────────────────────────────────────────
# Солнце
sun_data = bpy.data.lights.new("Sun", "SUN")
sun_obj  = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(58), math.radians(12), math.radians(35))
sun_data.energy        = 4.5
sun_data.angle         = math.radians(2)

# Небо
world = bpy.context.scene.world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs["Color"].default_value    = (0.52, 0.64, 0.82, 1)
bg_node.inputs["Strength"].default_value = 0.7


# ─────────────────────────────────────────────────────────────
# 13. РЕНДЕР
# ─────────────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine            = 'CYCLES'
scene.cycles.samples           = 128
scene.cycles.use_denoising     = True
scene.render.resolution_x      = 1920
scene.render.resolution_y      = 1080
scene.render.film_transparent  = False

# Центрировать вид на здание
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        with bpy.context.temp_override(area=area):
            bpy.ops.view3d.view_all()
        break

print(f"✅ Готово! Создано объектов: {len(bpy.context.scene.objects)}")
print(f"   Этажей: {FLOORS} | Высота: {TOTAL_H:.1f} м | Ширина: {BLD_W:.0f} м")
