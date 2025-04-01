from build123d import *
from ocp_vscode import show_clear,show, show_all, Camera
from math import asin, acos, atan, degrees, sin, cos, tan, radians, radians, pi, sqrt
from typing import Iterable

knob_radius = 20
offset_grip = 7
grip_radius = 10
grip_height = 9

# for size M8:
m8_shaft_radius = 8.3 / 2
m8_hex_radius = 13 / 2
m8_thickness = 5.6

knob_perimeter = knob_radius * pi * 2
alfa = 36 # 360 / 10
dist_m1_m2 = knob_radius + offset_grip
# angle_large is the angle from center m0 of the grip circle intersecting
# the main cirle c0
angle_large = acos((knob_radius * knob_radius + dist_m1_m2 * dist_m1_m2 - grip_radius * grip_radius)
                    / (2 * knob_radius * dist_m1_m2))
perimeter_sum = knob_perimeter * (10 * angle_large / (2 * pi))
perimeter_remain = knob_perimeter - perimeter_sum
print(f'perimeter_remain: {perimeter_remain}, perimeter_sum: {perimeter_sum}, total: {knob_perimeter}')

# angle_small is the angle from center m0 between two grip circle (the section without cutout)
angle_small = perimeter_remain / knob_perimeter * 2 * pi / 5
angle_sum = angle_large + angle_small
# calculate the intersection points of lt1 and lt2 with c0
p1 = (cos(angle_large) * knob_radius, sin(angle_large) * knob_radius)
p2 = (cos(angle_sum) * knob_radius, sin(angle_sum) * knob_radius)
# centerpoint of second circle:
angle_c2 = 2 * angle_large + angle_small
m0 = (0,0)  # center of main circle
m1 = (dist_m1_m2, 0)  # center of first cut-out circle on x-axis
m2 = (cos(angle_c2) * dist_m1_m2, sin(angle_c2) * dist_m1_m2) # angle of 2nd cutout circle

angle_large = degrees(angle_large)
angle_small = degrees(angle_small)
angle_sum = degrees(angle_sum)
print(f'large angle: {angle_large}')
print(f'small angle: {angle_small}')

pentagon_cutout_thickness = m8_thickness + 2
pentagon_taper = 5

def construct_knob() -> Part:
    # lt1 = Line(m0, p1)
    # lt2 = Line(m0, p2)
    hl1 = PolarLine(m1, 50, angle= degrees(acos((p1[0] - m1[0]) / grip_radius)))
    hl2 = PolarLine(m2, 50, angle= - degrees(acos((p2[0] - m2[0]) / grip_radius)))
    # tan2 = PolarLine(p2, 50, angle= 90 - degrees(acos((p2[0] - m2[0]) / grip_radius)))
    # tan1 = PolarLine(p1, length=50, angle=90 - degrees(acos((m1[0] - p1[0]) / grip_radius)))
    # calculate the center of the smaller circle that has tangent to m1 and m2
    m3 = hl1.intersect(hl2)
    # get the angle of p to m0:
    angle_m3 = degrees(atan(m3.Y / m3.X))
    dist_m0_m3 = m3.distance_to(m0)
    m3_radius = m3.distance_to(p1)
    print(f'Distance: {dist_m0_m3}, angle: {angle_m3}')
    ll = PolarLine(m0, dist_m0_m3, angle_m3)

    with BuildPart() as part:
        with BuildSketch(Plane.XY):
            c0 = Circle(knob_radius)
            with PolarLocations(dist_m0_m3, start_angle=angle_m3, count = 5):
                c3 = Circle(m3_radius)
            with PolarLocations(knob_radius + offset_grip, count=5):
                c1 = Circle(radius=grip_radius, mode=Mode.SUBTRACT)

        extrude(amount=grip_height)

        # rounding the top
        with BuildSketch(Plane.YZ):
            top_point = (0, grip_height)
            with BuildLine(Plane.YZ):
                ra = JernArc(top_point, (-1,0), radius=7 * (knob_radius + offset_grip), arc_size=10)
                outer = ra @ 1
                Line(outer, (outer.Y, grip_height))
                Line((outer.Y, grip_height), top_point)
            cc = make_face()
        revolve(cc, axis=Axis.Z, revolution_arc=360, mode=Mode.SUBTRACT)

        # filleting the top edge:
        top_edges = part.edges().filter_by(Axis.Z, reverse=True).filter_by(Plane.XY, reverse=True)
        fillet(top_edges, 2)

        # create a cutout at the bottom
        with BuildSketch(Plane.XY):
            pentagon = RegularPolygon(knob_radius / 2, 5, rotation=angle_small)
        extrude(amount=pentagon_cutout_thickness, mode=Mode.SUBTRACT, taper=pentagon_taper)

    show_all(reset_camera=Camera.KEEP)
    return part.part

def construct_inlay() -> Part:
    # create inner part
    with BuildPart() as part2:
        with BuildSketch(Plane.XY):
            RegularPolygon(knob_radius / 2, 5, rotation=angle_small)
        extrude(amount=pentagon_cutout_thickness, taper=pentagon_taper)
        top_face = part2.faces().filter_by(Plane.XY).sort_by(Axis.Z)[-1]
        with BuildSketch(top_face):
            RegularPolygon(m8_hex_radius, 6)
        extrude(amount=-m8_thickness, taper=pentagon_taper, mode=Mode.SUBTRACT)
        with BuildSketch(top_face):
            Circle(radius=m8_shaft_radius)
        extrude(amount=-pentagon_cutout_thickness, mode=Mode.SUBTRACT)
    show_all(reset_camera=Camera.KEEP)
    return part2.part

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
    part1 = construct_knob()
    part2 = construct_inlay()
    show(part1, part2)
    export([part1, part2], "knob.3mf")