from build123d import *
from ocp_vscode import show_clear,show, show_all
from math import asin, atan, degrees, radians, sin, cos, radians, pi, sqrt

# Note: This is not yet working correctly. There is a small gap
# between c0 and c1 circles resulting in ugly edges.

with BuildPart() as part:
    knob_radius = 20
    knob_perimeter = knob_radius * pi * 2
    offset_grip = 4
    grip_radius = 10
    offset_grip2 = 3.0
    grip_radius2 = 4.2
    grip_height = 8
    alfa = 36 # 360 / 10
    # https://de.wikipedia.org/wiki/Kreissegment
    # chord_len = 2 * knob_radius * sin(radians(alfa) / 2)
    chord_height = grip_radius - offset_grip
    chord_len = 2 * sqrt(2 * grip_radius * chord_height - (chord_height * chord_height))
    # print(f'Perimeter: {knob_perimeter} = 10 * {knob_perimeter / 10}')
    print(f'Chord Length: {chord_len}')
    # calculate angle of this chord in knob
    angle_large = atan(chord_len / (2 * knob_radius)) * 2
    print(f'large angle: {degrees(angle_large)}')
    perimeter_sum = knob_perimeter * (5 * angle_large / (2 * pi))
    perimeter_remain = knob_perimeter - perimeter_sum
    print(f'perimeter_remain: {perimeter_remain}, perimeter_sum: {perimeter_sum}, total: {knob_perimeter}')
    angle_small = perimeter_remain / knob_perimeter * 2 * pi / 5
    print(f'small angle: {degrees(angle_small)}')
    chord_len_small = 2 * knob_radius * sin(angle_small / 2)
    print(f'chord_len_small: {chord_len_small}')
    grip_radius2 = chord_len_small / 2
    with BuildSketch(Plane.XY):
        # use the following helper lines for checking correct dimensions:
        # l1 = PolarLine((0,0), knob_radius + 5, degrees(angle_large) / 2)
        # l0 = Line((knob_radius,0), (knob_radius,chord_len / 2 ))
        # l2 = PolarLine((0,0), knob_radius + 5, - degrees(angle_large) / 2)
        c0 = Circle(knob_radius)
        with PolarLocations(knob_radius, count=5, start_angle=36):
            c2 = Circle(radius=grip_radius2, mode=Mode.ADD)
        with PolarLocations(knob_radius + offset_grip, count=5):
            c1 = Circle(radius=grip_radius, mode=Mode.SUBTRACT)
    extrude(amount=grip_height)

    # filleting the top edge:
    top_edges = part.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1][:2]
    print(top_edges)
    with BuildSketch(Plane.XZ):
        fr = 3 # fillet radius
        segment_height = grip_radius - sqrt(4 * grip_radius * grip_radius - chord_len * chord_len) / 2
        with Locations((knob_radius - segment_height - fr, grip_height - fr)):
            Rectangle(fr*2, fr*2, align=(Align.MIN, Align.MIN))
            Circle(radius=fr, mode=Mode.SUBTRACT)
    #sweep(path=top_edges, mode=Mode.SUBTRACT)
    # extrude(amount=40, mode=Mode.SUBTRACT)
show_all()
