from build123d import *
from ocp_vscode import show_clear,show, show_all

length = 200
width = length
thickness = 5
hole_diameter = 4
height_adjustment_diameter = 6
router_cutout_diameter = 35

three_hole_radius = 58.5
two_hole_radius = 67
height_adjustment_radius = 65.5
rounded_corner_radius = 4
counter_sink_radius = 5

corner_hole_offset = 10

with BuildPart() as part:
    with BuildSketch() as sketch:
        RectangleRounded(length, width, radius=rounded_corner_radius)
        # central router cutout
        Circle(router_cutout_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

    # mounting holes at the corners:
    with Locations(part.faces().sort_by(Axis.Z)[-1]):
        hw = width / 2
        hl = length / 2
        locs = [(-hw + corner_hole_offset, -hl + corner_hole_offset),
                (-hw + corner_hole_offset, hl - corner_hole_offset),
                (hw - corner_hole_offset, -hl + corner_hole_offset),
                (hw - corner_hole_offset, hl - corner_hole_offset)]
        with Locations(locs):
            CounterSinkHole(hole_diameter / 2, counter_sink_radius)

        # height adjustment screw
        with Locations(Rot(Z=-28)): # perform a rotation coplanar with Plane.XY
            with Locations((height_adjustment_radius, 0)):
                Hole(height_adjustment_diameter / 2)
        # three hole arms:
        with PolarLocations(0, 3, start_angle=34.5):
            with Locations((three_hole_radius, 0)):
                CounterSinkHole(hole_diameter / 2, counter_sink_radius)
        # two hole arms:
        with PolarLocations(0, 2, start_angle=26):
            with Locations((two_hole_radius, 0)):
                CounterSinkHole(hole_diameter / 2, counter_sink_radius)

show_all()
