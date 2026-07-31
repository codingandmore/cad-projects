from typing import Iterable
from ocp_vscode import show_clear,show, show_all, Camera
from build123d import *

from skadis_organizer import SkadisOrganizer

# %%
def export (parts: Iterable[Part], name: str):
    exporter = Mesher()

    for part in parts:
        exporter.add_shape(part)

    exporter.add_meta_data(
        name_space="custom",
        name="name",
        value=name,
        metadata_type="str",
        must_preserve=False,
    )
    exporter.write(name)


if __name__ == '__main__':
    show_clear()
    org = SkadisOrganizer(wall_height=30)
    board = org.create_board(27, 17, border_x=10, border_y=10, start_indented=True)
    board.label = "Board"

    walla = org.create_wall(2, 5, 9, SkadisOrganizer.Orientation.VERTICAL)
    walla.label = "A"

    wallb = org.create_wall(4, 5, 6, SkadisOrganizer.Orientation.VERTICAL)
    wallb.label = "B"

    wallc = org.create_wall(6, 5, 4, SkadisOrganizer.Orientation.VERTICAL)
    wallc.label = "C"
    walld = org.create_wall(13, 5, 6, SkadisOrganizer.Orientation.VERTICAL)
    walld.label = "D"
    walle = org.create_wall(16, 2, 12, SkadisOrganizer.Orientation.VERTICAL)
    walle.label = "E"
    wallf = org.create_wall(18, 2, 12, SkadisOrganizer.Orientation.VERTICAL)
    wallf.label = "F"

    wallg = org.create_wall(2, 14, 14, SkadisOrganizer.Orientation.HORIZONTAL)
    wallg.label = "G"
    wallh = org.create_wall(2, 5, 11, SkadisOrganizer.Orientation.HORIZONTAL)
    wallh.label = "H"
    walli = org.create_wall(2, 2, 14, SkadisOrganizer.Orientation.HORIZONTAL)
    walli.label = "I"
    wallj = org.create_wall(16, 14, 9, SkadisOrganizer.Orientation.HORIZONTAL)
    wallj.label = "J"
    wallk = org.create_wall(6, 9, 7, SkadisOrganizer.Orientation.HORIZONTAL)
    wallk.label = "k"
    walll = org.create_wall(4, 11, 9, SkadisOrganizer.Orientation.HORIZONTAL)
    walll.label = "L"
    # show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    show_all(reset_camera=Camera.KEEP)
    # export([part1, part2], "drawer-1.3mf")


# %%