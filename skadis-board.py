from build123d import *
from ocp_vscode import show_clear,show, show_all, Camera
from typing import Iterable
from enum import Enum

skadis_slot_len = 15
skadis_slot_w = 5
clearance = 0.3
slot_spacing = 20
double_slot_spacing = 2 * slot_spacing
board_thickness = 5

def create_board(x_units: int, y_units: int) -> Part:
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XY):
            Rectangle(x_units * slot_spacing, y_units * slot_spacing, align=(Align.MIN, Align.MIN))
            # with Locations((0, 0)):
            half_x = int(x_units / 2)
            half_y = int(y_units / 2)
            with GridLocations(x_spacing=double_slot_spacing, y_spacing=double_slot_spacing,
                               x_count=half_x, y_count=half_x, align=(Align.MIN, Align.MIN)):
                SlotOverall(skadis_slot_len, skadis_slot_w, align=(Align.MIN, Align.MIN), mode=Mode.SUBTRACT)
            with Locations((20, 20)):
                with GridLocations(x_spacing=double_slot_spacing, y_spacing=double_slot_spacing,
                                   x_count=half_x, y_count=half_x, align=(Align.MIN, Align.MIN)):
                    SlotOverall(skadis_slot_len, skadis_slot_w, align=(Align.MIN, Align.MIN), mode=Mode.SUBTRACT)

        extrude(amount=-board_thickness)
    return partBuilder.part


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
    name = "board"
    board = create_board(12, 8)
    board.label = name
    show_objects = (
        board,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")