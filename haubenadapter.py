from typing import Iterable
from build123d import *
from ocp_vscode import show_clear,show, show_all
from math import atan, degrees, sin, cos, radians


def construct() -> Part:
    dm_absaug_s = 34    # measured value: 34.7mm
    dm_absaug_l = 36    # measured value: 36.25mm
                        # length: 30mm
    r_absaug_s = dm_absaug_s / 2
    r_absaug_l = dm_absaug_l /2
    dm_haube_s = 36     # outer diameter: 36.8mm
    dm_haube_l = 38
    r_haube_l = dm_haube_l / 2
    r_haube_s = dm_haube_s / 2
    wall_thicknes = 2.5
    len_haube = 30
    len_absaug = 30
    conn_len = 5
    arc_r = 50
    angle = 30

    taper_absaug = degrees(atan((r_absaug_l - r_absaug_s) / len_absaug))
    taper_haube = degrees(atan((r_haube_l - r_haube_s) / len_haube))
    print(f'Taper Absaug: {taper_absaug}')
    print(f'Taper Haube: {taper_haube}')

    with BuildPart() as part:
        # Haube:
        with BuildSketch(Plane.XY):
            with BuildLine(Plane.XY):
                start_point = (r_haube_l, - len_haube)
                start_point_outer = (r_haube_l + wall_thicknes, -len_haube)

                b_line = PolarLine(start_point, length=-len_haube, angle=-90 + taper_haube)
                b_line_outer = PolarLine(start_point_outer, length=-len_haube, angle=-90 + taper_haube)
                Line(b_line_outer @ 0, b_line @ 0)
                Line(b_line_outer @ 1, b_line @ 1)
            tube0 = make_face()
        revolve(tube0, axis=Axis.Y)

        # with BuildSketch(Plane.XZ):
        #     Circle(dm_haube_l / 2 + wall_thicknes)
        #     Circle(dm_haube_l / 2, mode=Mode.SUBTRACT)
        # extrude(amount=len_haube)

        # # Arc:
        p0 = (0, 0)
        l_arc = JernArc(p0, tangent=(0,1), radius=arc_r, arc_size=30)
        end_face = part.faces().sort_by(Axis.Y)[-1]
        # next two lines are to circumvent a bug. sweep runs in an endless
        # loop if omitted.
        extrude(end_face, amount=0.01)
        end_face = part.faces().sort_by(Axis.Y)[-1]
        sweep(end_face, path=l_arc)

        with BuildSketch(Plane.XY):
            with BuildLine(Plane.XY):
                end_pos = l_arc @ 1
                c_line = PolarLine(end_pos, length=len_absaug, angle=90 + angle)
                h_line = PolarLine(end_pos, length=r_absaug_s + wall_thicknes, angle=angle)
                b_line_tapered = PolarLine(h_line@1, length=len_absaug, angle=90 + angle - taper_absaug)
                offset(b_line_tapered, amount=wall_thicknes, side=Side.LEFT)
            tube = make_face()

        # vacuum part:
        rot_axis = Axis((c_line @ 0), (c_line % 1))
        revolve(tube, axis=rot_axis)

    show_all()
    # show(c_line, rot_axis, tube, part)
    return part.part

def export (part: Part, name: str):
    exporter = Mesher()

    # exporter.add_code_to_metadata()
    exporter.add_shape(part)
    exporter.write(f'{name}.3mf')

if __name__ == '__main__':
    show_clear()
    part = construct()
    # print(part)
    export(part, "haubenadapter-30")
