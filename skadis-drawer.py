# %%
import copy
from build123d import *
from ocp_vscode import show_clear,show, show_all, Camera
from math import asin, acos, atan, degrees, sin, cos, tan, radians, radians, pi, sqrt
from typing import Iterable
from enum import Enum

skadis_slot_len = 15
skadis_slot_w = 5
clearance = 0.3
wall_height = 30
wall_thickness = skadis_slot_w # do not change!
slot_spacing = 20
double_slot_spacing = 2 * slot_spacing
hook_offset_row = slot_spacing - skadis_slot_w + clearance / 2 # initial offset for hook to align with next wall
peg_h = skadis_slot_len - clearance
peg_w = skadis_slot_w - clearance
board_thickness = 5

clearance_depth = 0.1
peg_d = skadis_slot_w - clearance_depth
skadis_slot_d = 5

class Orientation(Enum):
    horizontal = 1
    vertical = 2

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

def create_hook(cut_to_thickness: bool=False)-> Part:
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XY):
             SlotOverall(peg_h / 2, peg_w, -0, (Align.MIN, Align.CENTER))
        extrude(amount=-peg_d)
        with BuildSketch(Plane.XY.offset(-peg_d)):
            SlotOverall(peg_h, peg_w, 0, (Align.CENTER, Align.CENTER))
        extrude(amount=-peg_d)
        if cut_to_thickness:
            with BuildSketch(Plane.XY):
                with Locations((skadis_slot_w, 0)):
                    Rectangle(peg_w, peg_w, align=(Align.MIN, Align.CENTER))
            extrude(amount=-peg_d*2, mode=Mode.SUBTRACT)
        joint_loc = Location((0,0,0))
        RigidJoint(label="foot-jt", joint_location=joint_loc)
    return partBuilder.part

def create_hook_90():
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XY):
             SlotOverall(peg_h / 2, peg_w, 0, (Align.MIN, Align.CENTER))
        extrude(amount=-peg_d)
        with BuildSketch(Plane.XY.offset(-peg_d)):
            SlotOverall(peg_h, peg_w, 0, (Align.CENTER, Align.CENTER))
        extrude(amount=-peg_d)
        with BuildSketch(Plane.XY):
            with Locations((0, skadis_slot_len - skadis_slot_w)):
                Rectangle(peg_w, peg_w, align=(Align.CENTER, Align.MAX))
        extrude(amount=-peg_d*2, mode=Mode.SUBTRACT)
        joint_loc = Location((0,0,0))
        RigidJoint(label="foot-jt", joint_location=joint_loc)
    return partBuilder.part

def create_snap_hook_internal(with_support: bool=True, for_subtract: bool=False):
    mid_point_y = wall_height / 2

    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XZ):
            if (for_subtract):
                with Locations((0, mid_point_y)):
                    Rectangle(wall_thickness, 4, align=(Align.MIN, Align.MIN))
            else:
                with Locations((0, mid_point_y)):
                    Rectangle(0.2, 2, align=(Align.MIN, Align.MIN))
                with Locations((0, mid_point_y + 2)):
                    Rectangle(wall_thickness, 2, align=(Align.MIN, Align.MIN))
            triangle_len = 1.1
            triangle_mid = wall_thickness / 2
            triangle_top = (triangle_mid, mid_point_y + 4 + triangle_len)
            triangle_bottom_left = (triangle_mid - triangle_len, mid_point_y + 4)
            triangle_bottom_right = (triangle_mid + triangle_len, mid_point_y + 4)
            with BuildLine():
                Line(triangle_top, triangle_bottom_right)
                Line(triangle_top, triangle_bottom_left)
                Line(triangle_bottom_left, triangle_bottom_right)
            make_face()
        half_hook = extrude(amount=wall_thickness - 2)
        if (for_subtract):
            offset(amount=0.3)
        else:
            half_hook.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-1]
            half_hook = fillet(half_hook.edges().filter_by(Axis.Y).sort_by(Axis.Z)[-1], 1.0)
            half_hook = fillet(half_hook.faces().filter_by(Axis.X).sort_by(Axis.X)[-1].edges(), 0.5)
            # add support bar
            if (with_support):
                with BuildSketch(Plane.XZ):
                    with Locations((4, mid_point_y)):
                        Rectangle(1, 4, align=(Align.MIN, Align.MIN))
                extrude(amount=-1)

    half_hook = partBuilder.part
    mirror_plane = Plane.XY.offset(mid_point_y)
    with BuildPart() as partBuilder:
        add(half_hook)
        mirror(half_hook, mirror_plane)
        RigidJoint(label="hookjt", joint_location=Location((0, -(wall_thickness-2)/2, mid_point_y)))

    return partBuilder.part

def create_snap_hook(with_support: bool=True):
    return  create_snap_hook_internal(False)

def create_snap_groove():
    mid_point_y = wall_height / 2
    snap_hook = create_snap_hook_internal(False, True)
    RigidJoint(label="groovejt", to_part=snap_hook, joint_location=Location((0, -(wall_thickness-2)/2, mid_point_y)))
    return snap_hook

def create_wall(x_units: int, y_units: int, len_units: int, orientation: Orientation):
    # main part:
    loc = (x_units * slot_spacing, y_units * slot_spacing)
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                if orientation is Orientation.vertical:
                    Rectangle(skadis_slot_w, len_units * slot_spacing, align=(Align.CENTER, Align.MIN))
                else:
                    Rectangle(len_units * slot_spacing, skadis_slot_w, align=(Align.MIN, Align.CENTER))
        extrude(amount=wall_height)

        joint_loc_feet = faces().filter_by(Plane.XY).sort_by(Axis.Z)[0].center_location
        if orientation is Orientation.vertical:
            joint_loc_start = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1].center_location
            joint_loc_end = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[0].center_location
            joint_loc_feet.position -= (0, (len_units * slot_spacing / 2), 0)
            joint_loc_end.orientation = (0, 0, 270)
            joint_loc_start.orientation = (0, 0, 90)
        else:
            joint_loc_start = faces().filter_by(Plane.YZ).sort_by(Axis.X)[-1].center_location
            joint_loc_end = faces().filter_by(Plane.YZ).sort_by(Axis.X)[0].center_location
            joint_loc_feet.position -= ((len_units * slot_spacing / 2), - skadis_slot_w / 2, 0)
            joint_loc_start.orientation = (0, 0, 0)
            joint_loc_end.orientation = (0, 0, 180)

        joint_loc_feet.orientation = (0, 0, 0)
        RigidJoint(label="wallstartjt", joint_location=joint_loc_end)
        RigidJoint(label="wallendjt", joint_location=joint_loc_start)
        RigidJoint(label="wallfootjt", joint_location=joint_loc_feet)
    wall = builder.part

    # start extension:
    # create groove at start
    snap_groove = create_snap_groove()
    wall.joints["wallstartjt"].connect_to(snap_groove.joints["groovejt"])

    # create bar
    if orientation is Orientation.vertical:
        loc = (loc[0], loc[1] - wall_thickness)
    else:
        loc = (loc[0] - wall_thickness / 2, loc[1] - wall_thickness / 2)

    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                Rectangle(wall_thickness, wall_thickness, align=(Align.CENTER, Align.MIN))
        extrude(amount=wall_height)
        add(snap_groove, mode=Mode.SUBTRACT)
    start_block = builder.part

    # end extension:
    # loc = (loc[0], loc[1] + len_units * slot_spacing)
    # with BuildPart() as builder:
    #     with BuildSketch(Plane.XY):
    #         with Locations(loc):
    #             Rectangle(wall_thickness, wall_thickness, align=(Align.CENTER, Align.MIN))
    #     extrude(amount=wall_height)


    # create hook at end
    snap_hook = create_snap_hook()
    wall.joints["wallendjt"].connect_to(snap_hook.joints["hookjt"])

    # create feet:
    foot = create_hook(cut_to_thickness=True if orientation is Orientation.vertical else False)

    wall.joints["wallfootjt"].connect_to(foot.joints["foot-jt"])
    # with GridLocations(x_spacing=1, y_spacing=slot_spacing, x_count=1, y_count=len_units):
    #     foot = copy.copy(foot)
    # locs = GridLocations(x_spacing=1, y_spacing=slot_spacing * 2, x_count=1, y_count=int(len_units / 2))# .local_locations
    wall_elems = [wall, start_block, snap_hook, foot]
    print(foot.position)
    for p in range (1,  int(len_units / 2) + 1):
        if orientation is Orientation.vertical:
            l = Location((0, p * slot_spacing * 2, 0))
        else:
            l = Location((p * slot_spacing * 2, 0, 0))
        f = foot.moved(l)
        wall_elems += f

    wall_assembly = Compound(label=name, children=wall_elems)
    return wall_assembly

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

# %%
if __name__ == '__main__':
    show_clear()
    # hook = create_hook(True)
    # hook.label = "hook"
    # hook90 = create_hook_90()
    # hook90.label = "hook90"
    # snap_hook = create_snap_hook(False)
    # snap_hook.label = "SnapHook"
    # snap_groove = create_snap_groove()
    # snap_groove.label = "SnapHookGroove"
    board = create_board(12, 8)
    board.label = "Board"
    name = "wall-v"
    wallv = create_wall(2, 3, 5, Orientation.vertical)
    wallv.label = name
    wallh = create_wall(2, 1, 4, Orientation.horizontal)
    name = "wall-h"
    wallh.label = name
    # sb.label = "sb"
    # eb.label = "eb"
    show_objects = (
        # hook,
        # hook90,
        # snap_hook,
        # snap_groove,
        board,
        wallv,
        wallh,
        # sb,
        # eb,
    )
    show(show_objects, reset_camera=Camera.KEEP, render_joints=True)
    # show_all()
    # export([part1, part2], "drawer-1.3mf")


# %%
