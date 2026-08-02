from typing import Iterable
from ocp_vscode import show_clear,show, show_all, Camera
from build123d import *

from skadis_organizer import SkadisOrganizer

# %%
def export (parts: Iterable[Part], name: str):
    exporter = Mesher()

    for part in parts:
        if isinstance(part, Compound):
            print(f'melting compound {part.label}')
            with BuildPart() as builder:
                for p in part.compounds():
                    add(p)
            x = builder.part
            x.orientation += (0, 90, 0)
            exporter.add_shape(x, mesh_type=MeshType.MODEL)
        else:
            exporter.add_shape(part, mesh_type=MeshType.MODEL)

    exporter.add_meta_data(
        name_space="custom",
        name="name",
        value=name,
        metadata_type="str",
        must_preserve=False,
    )
    exporter.write(name)


if __name__ == '__main__':
    org = SkadisOrganizer(wall_height=30, first_row_indented=True, with_support=True)
    board = org.create_board(27, 17, border_x=10, border_y=10, name="Board")
    walla = org.create_wall(2, 5, 9, SkadisOrganizer.Orientation.VERTICAL, True, "A")
    wallb = org.create_wall(4, 5, 6, SkadisOrganizer.Orientation.VERTICAL, True, "B")
    wallc = org.create_wall(6, 5, 4, SkadisOrganizer.Orientation.VERTICAL, True, "C")
    walld = org.create_wall(13, 5, 6, SkadisOrganizer.Orientation.VERTICAL, True, "D")
    walle = org.create_wall(16, 2, 12, SkadisOrganizer.Orientation.VERTICAL, True, "E")
    wallf = org.create_wall(18, 2, 12, SkadisOrganizer.Orientation.VERTICAL, False, "F")
    wallg = org.create_wall(2, 14, 12, SkadisOrganizer.Orientation.HORIZONTAL, True, "G")
    adapterh1 = org.create_adapter(SkadisOrganizer.AdapterType.LEFT_HOOK, 2, 5, 2, "H1A")
    adapterh2 = org.create_adapter(SkadisOrganizer.AdapterType.LEFT_HOOK, 4, 5, 2, "H2A")
    adapterh3 = org.create_adapter(SkadisOrganizer.AdapterType.LEFT_HOOK, 6, 5, 2, "H3A")
    wallh = org.create_wall(8, 5, 5, SkadisOrganizer.Orientation.HORIZONTAL, False, "H")
    walli = org.create_wall(2, 2, 14, SkadisOrganizer.Orientation.HORIZONTAL, False, "I")
    wallj = org.create_wall(14, 14, 11, SkadisOrganizer.Orientation.HORIZONTAL, False, "J")
    wallk = org.create_wall(6, 9, 7, SkadisOrganizer.Orientation.HORIZONTAL, True, "K")
    walll = org.create_wall(4, 11, 8, SkadisOrganizer.Orientation.HORIZONTAL, True, "L")
    adapterl1 = org.create_adapter(SkadisOrganizer.AdapterType.RIGHT_GROOVE, 12, 11, 1, "L1A")
    show_clear()
    # show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    show_all(reset_camera=Camera.KEEP)
    fname = "Drawer-1.3mf"
    print(f"Exporting to {fname}")
    # export([walla, wallb], fname)
    export([walla, wallb, wallc, walld, walle, wallf, wallg, wallh, adapterh1,
                   adapterh2, adapterh3, walli, wallj, wallk, walll, adapterl1], fname)


# %%