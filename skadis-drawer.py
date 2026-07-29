# %%
import copy
from build123d import *
from ocp_vscode import show_clear,show, show_all, Camera
from math import asin, acos, atan, ceil, degrees, sin, cos, tan, radians, radians, pi, sqrt
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

def create_board(x_units: int, y_units: int, border_x: int=0, border_y: int=0) -> Part:
    with BuildPart() as partBuilder:
        with BuildSketch(Plane.XY):
            with Locations((-border_x, -border_y, 0)):
                Rectangle(x_units * slot_spacing + 2 * border_x, y_units * slot_spacing + 2 * border_y, align=(Align.MIN, Align.MIN))
            half_x = int(x_units / 2)
            half_y = int(y_units / 2)
            with GridLocations(x_spacing=double_slot_spacing, y_spacing=double_slot_spacing,
                               x_count=half_x, y_count=half_y, align=(Align.MIN, Align.MIN)):
                SlotOverall(skadis_slot_len, skadis_slot_w, align=(Align.MIN, Align.MIN), mode=Mode.SUBTRACT)
            with Locations((20, 20)):
                with GridLocations(x_spacing=double_slot_spacing, y_spacing=double_slot_spacing,
                                   x_count=half_x, y_count=half_y, align=(Align.MIN, Align.MIN)):
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

    return partBuilder.part

def create_snap_hook(with_support: bool=True) -> Part:
    hook = create_snap_hook_internal(False)
    RigidJoint(label="hookjt", to_part=hook, joint_location=Location((0, -(wall_thickness-2)/2, wall_height / 2)))
    return hook

def create_snap_groove():
    snap_hook = create_snap_hook_internal(False, True)
    face = snap_hook.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
    joint_loc = Location(face.center_location.position, 180)
    RigidJoint(label="groovejt", to_part=snap_hook, joint_location=joint_loc)
    return snap_hook

def create_wall(x_units: int, y_units: int, len_units: int, orientation: Orientation, left_groove: bool):
    # depending on if we are on an even or odd row the first slot is offseted
    feet_offset = 0
    if x_units & 1 != y_units & 1:
        feet_offset = slot_spacing
    remaining_wall_len = len_units * slot_spacing - feet_offset
    no_feet = ceil(remaining_wall_len / (slot_spacing * 2))
    # print(f'{no_feet=}, {len_units=}, {feet_offset=}, {remaining_wall_len=}')

    # main part:
    loc = (x_units * slot_spacing, y_units * slot_spacing)
    with BuildPart() as builder:
        with BuildSketch(Plane.XY):
            with Locations(loc):
                if orientation is Orientation.vertical:
                    Rectangle(skadis_slot_w, len_units * slot_spacing, align=(Align.MIN, Align.MIN))
                else:
                    Rectangle(len_units * slot_spacing, skadis_slot_w, align=(Align.MIN, Align.MIN))
        extrude(amount=wall_height)

        joint_loc_feet = faces().filter_by(Plane.XY).sort_by(Axis.Z)[0].center_location
        joint_loc_feet.orientation = (0, 0, 0)
        if orientation is Orientation.vertical:
            joint_loc_end = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1].center_location
            joint_loc_start = faces().filter_by(Plane.XZ).sort_by(Axis.Y)[0].center_location
            saved_loc = copy.copy(joint_loc_start)
            joint_loc_feet.position -= (skadis_slot_w / 2, (len_units * slot_spacing / 2) - skadis_slot_w / 2 - feet_offset, 0)
            if left_groove:
                joint_loc_start.position += (-skadis_slot_w / 2, skadis_slot_w / 2, 0)
                joint_loc_start.orientation = (0, 0, 180)
            else:
                joint_loc_start.orientation = (0, 0, 270)
            joint_loc_end.orientation = (0, 0, 90)
            saved_loc.position += (-skadis_slot_w / 2, skadis_slot_w / 2 + slot_spacing, 0)
            saved_loc.orientation = (0, 0, 180)
        else:
            joint_loc_end = faces().filter_by(Plane.YZ).sort_by(Axis.X)[-1].center_location
            joint_loc_start = faces().filter_by(Plane.YZ).sort_by(Axis.X)[0].center_location
            saved_loc = copy.copy(joint_loc_start)
            joint_loc_feet.position -= (len_units * slot_spacing / 2 - feet_offset, 0, 0)
            joint_loc_end.orientation = (0, 0, 0)
            saved_loc.position += (skadis_slot_w / 2 + slot_spacing, skadis_slot_w / 2, 0)
            saved_loc.orientation = (0, 0, 90)
            if left_groove:
                joint_loc_start.position += (skadis_slot_w / 2, skadis_slot_w / 2, 0)
                joint_loc_start.orientation = (0, 0, 90)
            else:
                joint_loc_start.orientation = (0, 0, 180)

        RigidJoint(label="wallstartjt", joint_location=joint_loc_start)
    wall = builder.part

    # create groove at start
    snap_groove = create_snap_groove()
    wall.joints["wallstartjt"].connect_to(snap_groove.joints["groovejt"])

    with BuildPart() as builder:
        add(wall)
        add(snap_groove, mode=Mode.SUBTRACT)
        RigidJoint(label="wallendjt", joint_location=joint_loc_end)
        RigidJoint(label="wallfootjt", joint_location=joint_loc_feet)
        RigidJoint(label="wallmidjt", joint_location=saved_loc)
        # add all other grooves along the wall
        if left_groove:
            count = len_units
            snap_groove2 = snap_groove
        else:
            # create and connect a second groove rotated 90° to first one
            snap_groove2 = create_snap_groove()
            builder.joints["wallmidjt"].connect_to(snap_groove2.joints["groovejt"])
            count = len_units - 1

        if orientation is Orientation.vertical:
            xc = 1
            yc = count
        else:
            xc = count
            yc = 1

        with GridLocations(x_spacing=slot_spacing, y_spacing=slot_spacing,
                x_count=xc, y_count=yc, align=(Align.MIN, Align.MIN)):
            add(snap_groove2, mode=Mode.SUBTRACT)
    wall = builder.part

     # create hook at end
    snap_hook = create_snap_hook()
    wall.joints["wallendjt"].connect_to(snap_hook.joints["hookjt"])

    # create feet:
    foot = create_hook(cut_to_thickness=True if orientation is Orientation.vertical else False)
    wall.joints["wallfootjt"].connect_to(foot.joints["foot-jt"])
    wall_elems = [wall, snap_hook, foot]

    for p in range (1,  no_feet):
        pos = p * slot_spacing * 2
        if orientation is Orientation.vertical:
            l = Location((0, pos, 0))
        else:
            l = Location((pos, 0, 0))
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
    # hook = create_hook(False)
    # hook.label = "hook"
    # snap_hook = create_snap_hook(False)
    # snap_hook.label = "SnapHook"
    # snap_groove = create_snap_groove()
    # snap_groove.label = "SnapHookGroove"
    board = create_board(12, 8, border_x=10, border_y=10)
    board.label = "Board"
    name = "wall-v"
    wallv = create_wall(1, 2, 5, Orientation.vertical, True)
    wallv.label = name
    wallh = create_wall(3, 4, 4, Orientation.horizontal, False)
    name = "wall-h"
    wallh.label = name
    # sb.label = "sb"
    # eb.label = "eb"
    show_objects = (
        # hook,
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
