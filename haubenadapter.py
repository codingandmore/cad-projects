from typing import Iterable
from build123d import *
from ocp_vscode import show_clear,show, show_all
from math import atan, degrees


def construct() -> Part:
    dm_absaug_s = 34.5
    dm_absaug_l = 36
    dm_haube_s = 36
    dm_haube_l = 38
    wall_thicknes = 2.5
    half_len = 30
    conn_len = 5
    # taper_absaug = degrees(atan((dm_absaug_l - dm_absaug_s) / half_len))
    # taper_haube =degrees(atan((dm_haube_l - dm_haube_s) / half_len))

    # print(f'Taper Absaug: {taper_absaug}')
    # print(f'Taper Haube: {taper_haube}')

    with BuildPart() as part:
        with BuildSketch(Plane.XY):
            with BuildLine(Plane.XY):
                p1 = (conn_len, dm_absaug_s / 2)
                p2 = (conn_len + half_len, dm_absaug_l / 2)
                l1 = Line(p1, p2)
                offset(amount=wall_thicknes, side=Side.LEFT)
            make_face()
            with BuildLine(Plane.XY):
                p1 = (conn_len, dm_absaug_s / 2)
                p2 = (-half_len, dm_haube_l / 2)
                l2 = Line(p1, p2)
                offset(amount=wall_thicknes, side=Side.RIGHT)
            make_face()
            # with BuildLine(Plane.XY):
            #     p1 = (0, dm_haube_s / 2)
            #     p2 = (conn_len*2, dm_absaug_s / 2)
            #     Line(p1, p2)
            #     offset(amount=wall_thicknes, side=Side.LEFT)
            # make_face()
        #revolve(axis=Axis.X)
    show_all()
    return part.part

def export (part: Part, name: str):
    exporter = Mesher()

    # exporter.add_code_to_metadata()
    exporter.add_shape(part)
    exporter.write(f'{name}.3mf')

if __name__ == '__main__':
    show_clear()
    part = construct()
    print(part)
    export(part, "haubenadapter")
