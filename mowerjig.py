from build123d import *
from ocp_vscode import show_clear,show, show_all

def construct() -> Part:
    length = 80
    height = 50
    thickness = 5
    bar_width = 20
    guide_len = 70
    slot_width = 5.5
    screw_diameter = 5
    left_slider_length = 20
    rail_len = 20
    rail_width = 10
    rail_height = 5

    with BuildPart() as rb:
        # Slider Bar Front Side
        with BuildSketch(Plane.XZ):
            Rectangle(length, bar_width)

        extrude(amount=thickness)
        front_face = rb.faces().sort_by(Axis.Y)[0]
        # cut out the slot
        with BuildSketch(front_face):
            slot_lengh = length - 20
            SlotCenterToCenter(slot_lengh, slot_width)
        extrude(amount=-thickness, mode=Mode.SUBTRACT)

        # extend slider to lowest z
        with BuildSketch(front_face):
            with Locations((0, -((bar_width+thickness) / 2))):
                Rectangle(length, thickness)
        extrude(amount=-thickness)

        # guide wall to the right
        zero_z = -bar_width / 2
        lowest_z = zero_z - thickness
        with BuildSketch(Plane.YZ.offset(length/2)):
            with Locations((-thickness, lowest_z)):
                Rectangle(guide_len, height, align=(Align.MIN, Align.MIN))
        extrude(amount=-thickness)

        # mount for vise at bottom:
        with BuildSketch(front_face):
            with Locations((length / 2 - bar_width, lowest_z)):
                Rectangle(bar_width, thickness, align=(Align.MIN, Align.MIN))
            mirror(about=Plane.YZ)
        extrude(amount=-bar_width)
        ff = rb.faces(Select.LAST).filter_by(Plane.XY).sort_by(Axis.Z)[1:3]
        with Locations(ff):
            CounterSinkHole(screw_diameter / 2 - 0.5, counter_sink_radius=screw_diameter)

        # guide for the knife

        with BuildSketch(Plane.XZ.offset(-(guide_len - rail_len - thickness))):
            with Locations((guide_len / 2, bar_width / 2)):
                Rectangle(rail_width, rail_height, align=(Align.MAX, Align.MAX))
        extrude(amount=-rail_len)

    # construct the left side as a new part
    with BuildPart() as lb:
        # left guide
        tolerance = 0.2
        with BuildSketch(Plane.YZ.offset(-length/2)):
            with Locations((-thickness * 2, zero_z + tolerance)):
                Rectangle(guide_len + thickness, height, align=(Align.MIN, Align.MIN))
            with Locations((-thickness, -bar_width / 2 - tolerance)):
                Rectangle(thickness + 2 * tolerance, bar_width + 2 * tolerance, align=(Align.MIN, Align.MIN), mode=Mode.SUBTRACT)
        extrude(amount=-thickness)

        # slider
        with BuildSketch(Plane.XZ.offset(thickness)):
            with Locations((-length/2, -bar_width / 2 + tolerance)):
                Rectangle(left_slider_length, height, align=(Align.MIN, Align.MIN))
            with Locations((-length / 2 + slot_width, 0)):
                Circle(slot_width / 2, mode=Mode.SUBTRACT)
        extrude(amount=thickness)

        # fillet
        fe = lb.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1].sort_by(Axis.X)[-1]
        fillet(fe, radius=left_slider_length)

        # cut-out for rail
        with BuildSketch(Plane.XZ.offset(-(guide_len - rail_len - thickness))):
            with Locations((-length / 2, bar_width / 2 - tolerance)):
                Rectangle(thickness, rail_height + 2 * tolerance, align=(Align.MAX, Align.MAX))
        extrude(amount=-(rail_len+tolerance), mode=Mode.SUBTRACT)

    show_all()
    return rb.part


def export (part: Part, name: str):
    exporter = Mesher()

    exporter.add_shape(part, )
    exporter.add_meta_data(
        name_space="custom",
        name="name",
        value=name,
        metadata_type="str",
        must_preserve=False,
    )
    exporter.add_code_to_metadata()
    exporter.write(name)

if __name__ == '__main__':
    show_clear()
    part = construct()
    # export(part, "jig.stl")