from build123d import *
from ocp_vscode import show_clear,show, show_all

def construct():
    length = 150
    dm_absaug = 35
    screw_hole_diameter = 4

    with BuildPart() as part:
        with BuildSketch(Plane.YZ):
            t = Triangle(c=50, a=50, B=90, align=Align.MIN)
            hyp = t.edge_b
            
        extrude(amount=length / 2)

        # Drill hole for vacuum hose
        f = part.faces().sort_by(SortBy.AREA)[-1]     
        edge_x0 = part.edges().sort_by(Axis.Y).sort_by(Axis.Z)[0]
        with BuildSketch(f):
            with Locations((0, -length/4)):
                Circle(dm_absaug / 2)        
        extrude(amount=-f.distance(edge_x0), mode=Mode.SUBTRACT)
        
        # make a cutout for the screw holes
        with BuildSketch(Plane.XY.offset(10)):
            x_off = (length - dm_absaug) / 4 + dm_absaug / 2
            with Locations((x_off, 25, 0)):
                Rectangle(20, 30)
        extrude(amount=t.a - 10, mode=Mode.SUBTRACT)  
        
        # Drill the horizontal hole
        hole_face = part.faces().filter_by(Plane.XY).sort_by(Axis.Z)[-1]
        with Locations(hole_face):     
            CounterSinkHole(screw_hole_diameter, screw_hole_diameter * 2) 
            Hole(screw_hole_diameter)

        # Drill the vertical hole
        hole_face = part.faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1]
        with Locations(hole_face):      
            CounterSinkHole(screw_hole_diameter, screw_hole_diameter * 2) 

        c = part.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Y)[-1]
        fillet(c, radius=4)

        # mirror the part to get full length
        mirror(about = Plane.YZ)
    show_all()

if __name__ == '__main__':
    show_clear()
    construct()
    
