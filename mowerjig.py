from build123d import *
from ocp_vscode import show_clear,show, show_all

def construct() -> Part:
    length = 80
    height = 50
    thickness = 5
    bar_width_sm = 15
    bar_width = 20
    guide_len = 70

    with BuildPart() as rb:
        with BuildSketch(Plane.XZ):
            Rectangle(length, bar_width)

        extrude(amount=thickness)
        front_face = rb.faces().sort_by(Axis.Y)[0]
        with BuildSketch(front_face):
            slot_lengh = length - 30
            with Locations((-5, 0)):
                SlotCenterToCenter(slot_lengh, 5)
        extrude(amount=-thickness, mode=Mode.SUBTRACT)
        # with BuildSketch(front_face):
        #     with Locations((length / 2 - bar_width_sm, bar_width / 2)):
        #         Rectangle(bar_width_sm, height - bar_width, align=(Align.MIN, Align.MIN))
        # extrude(amount=-thickness)
        
        with BuildSketch(Plane.YZ.offset(length/2)):
            with Locations((-thickness, -bar_width / 2)):
                Rectangle(guide_len, height, align=(Align.MIN, Align.MIN))
        extrude(amount=-thickness)

        # mount for vise:
        with BuildSketch(front_face):
            with Locations((length / 2 - bar_width, - bar_width / 2)):
                Rectangle(bar_width, thickness, align=(Align.MIN, Align.MIN))
        extrude(amount=-bar_width) 
        ff = rb.faces(Select.LAST).filter_by(Plane.XY).sort_by(Axis.Z)[1]
        with Locations(ff):
            CounterSinkHole(3, counter_sink_radius=6)
        

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