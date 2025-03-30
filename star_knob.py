from build123d import *
from ocp_vscode import show_clear,show, show_all, Camera
from math import asin, atan, degrees, radians, sin, acos, radians, pi, sqrt

# Note: This is not yet working correctly. There is a small gap
# between c0 and c1 circles resulting in ugly edges.

with BuildPart() as part:
    knob_radius = 20
    knob_perimeter = knob_radius * pi * 2
    offset_grip = 5
    grip_radius = 10
    # offset_grip2 = 3.0
    # grip_radius2 = 4.2
    grip_height = 8
    alfa = 36 # 360 / 10
    # https://de.wikipedia.org/wiki/Kreissegment
    # chord_height = grip_radius - 0.5 * sqrt(4 * grip_radius * grip_radius - chord_len * chord_len)
    # chord_len = 2 * sqrt(2 * grip_radius * chord_height - (chord_height * chord_height))
    # new begin
    # use the law of cosines to calculate angles of circles so that we have
    # a tangent constraint between the inner circle and the outer cutouts.
    dist_m1_m2 = knob_radius + grip_radius - offset_grip
    angle_large = acos((knob_radius * knob_radius + dist_m1_m2 * dist_m1_m2 - grip_radius * grip_radius)
                       / (2 * knob_radius * dist_m1_m2))
    angle_large = acos((knob_radius * knob_radius + dist_m1_m2 * dist_m1_m2 - grip_radius * grip_radius)
                       / (2 * knob_radius * dist_m1_m2))
    angle_small = acos((grip_radius * grip_radius + dist_m1_m2 * dist_m1_m2 - knob_radius * knob_radius)
                       / (2 * grip_radius * dist_m1_m2))
    # end new
    # print(f'Perimeter: {knob_perimeter} = 10 * {knob_perimeter / 10}')
    # print(f'Chord Length: {chord_len}, Chord Height: {chord_height}')
    # calculate angle of this chord in knob
    # angle_large = atan(chord_len / (2 * knob_radius)) * 2
    # angle_large = atan(chord_len / (2 * (knob_radius - chord_height))) * 2
    perimeter_sum = knob_perimeter * (5 * angle_large / (2 * pi))
    perimeter_remain = knob_perimeter - perimeter_sum
    print(f'perimeter_remain: {perimeter_remain}, perimeter_sum: {perimeter_sum}, total: {knob_perimeter}')
    # angle_small = perimeter_remain / knob_perimeter * 2 * pi / 5
    # chord_len_small = 2 * knob_radius * sin(angle_small / 2)
    # grip_radius2 = chord_len_small / 2

    angle_large = degrees(angle_large)
    angle_small = degrees(angle_small)
    # l0 = Line((0,0), (knob_radius - chord_height, 0))
    lt1 = PolarLine((0,0), knob_radius, - angle_large)
    lt2 = PolarLine((0,0), knob_radius, angle_large)
    print(f'large angle: {angle_large}')
    print(f'small angle: {angle_small}')
    # print(f'chord_len_small: {chord_len_small}')
    with BuildSketch(Plane.XY):
        c0 = Circle(knob_radius)
        with PolarLocations(knob_radius + offset_grip, count=5):
            c1 = Circle(radius=grip_radius, mode=Mode.SUBTRACT)
        # start_angle=angle_large / 2
        # increment_angle = angle_large + angle_small
        # for i in range(5):
        #     angle1 = i * increment_angle + start_angle
        #     angle2 = i * increment_angle + start_angle + angle_small
        #     print(f'angle1: {angle1}')
        #     print(f'angle2: {angle2}')
        #     l1 = PolarLine((0,0), knob_radius, angle1)
        #     l2 = PolarLine((0,0), knob_radius, angle2)
        #     start1 = l1 @ 1
        #     start2 = l2 @ 1
        #     with BuildLine(Plane.XY):
        #         TangentArc([start1, start2], tangent=start1)
        #         RadiusArc(start2, start1, knob_radius)
        #     aface = make_face()
    extrude(amount=grip_height)

    # filleting the top edge:
    top_edges = part.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1]
    # # print(top_edges)
    with BuildSketch(Plane.XZ):
        fr = 3 # fillet radius
        # segment_height = grip_radius - sqrt(4 * grip_radius * grip_radius - chord_len * chord_len) / 2
        with Locations((knob_radius - offset_grip - fr, grip_height - fr)):
            Rectangle(fr*2, fr*2, align=(Align.MIN, Align.MIN))
            Circle(radius=fr, mode=Mode.SUBTRACT)
    sweep(path=top_edges, mode=Mode.SUBTRACT)
    # extrude(amount=40, mode=Mode.SUBTRACT)
show_all(reset_camera=Camera.KEEP)
