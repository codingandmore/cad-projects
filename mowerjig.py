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
        # Slider Bar Front Side
        with BuildSketch(Plane.XZ):
            Rectangle(length, bar_width)

        extrude(amount=thickness)
        front_face = rb.faces().sort_by(Axis.Y)[0]
        # cut out the slot
        with BuildSketch(front_face):
            slot_lengh = length - 30
            with Locations((-5, 0)):
                SlotCenterToCenter(slot_lengh, 5)
        extrude(amount=-thickness, mode=Mode.SUBTRACT)

        # extend slider to lowest z
        with BuildSketch(front_face):
            with Locations((0, -((bar_width+thickness) / 2))):            
                Rectangle(length, thickness)
        extrude(amount=-thickness)
        
        # guide wall to the right
        lowest_z = -bar_width / 2 - thickness
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