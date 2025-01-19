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
            
        extrude(amount=length)
        f = part.faces().sort_by(SortBy.AREA)[-1]     
        edge_x0 = part.edges().sort_by(Axis.Y).sort_by(Axis.Z)[0]
        with BuildSketch(f):
            Circle(dm_absaug / 2)
        
        extrude(amount=-f.distance(edge_x0), mode=Mode.SUBTRACT)
        
        with BuildSketch(Plane.XY.offset(10)):
            with Locations((30, 25, 0)):
                Rectangle(20, 30)
        
        extrude(amount=t.a - 10, mode=Mode.SUBTRACT)  
        # hole_face =np.faces().sort_by(Axis.Z)[-1]          
        # with Locations(hole_face):      
        #     Hole(4)
        
        hole_face = part.faces().filter_by(Plane.XY).sort_by(Axis.Z)[-1]

        with Locations(hole_face):      
            Hole(screw_hole_diameter)

        hole_face = part.faces().filter_by(Plane.XZ).sort_by(Axis.Y)[-1]
        with Locations(hole_face):      
            Hole(screw_hole_diameter)

    show_all()

if __name__ == '__main__':
    show_clear()
    construct()
    
