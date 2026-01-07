# road.py
from OpenGL.GL import *
from OpenGL.GLU import *

class Road:
    def __init__(self):
        self.road_length = 200
        self.road_width = 15
    
    def draw_cube(self, size):
        """Draw cube manually tanpa GLUT"""
        s = size / 2.0
        glBegin(GL_QUADS)
        # Front
        glNormal3f(0, 0, 1)
        glVertex3f(-s, -s, s); glVertex3f(s, -s, s); glVertex3f(s, s, s); glVertex3f(-s, s, s)
        # Back
        glNormal3f(0, 0, -1)
        glVertex3f(-s, -s, -s); glVertex3f(-s, s, -s); glVertex3f(s, s, -s); glVertex3f(s, -s, -s)
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(-s, s, -s); glVertex3f(-s, s, s); glVertex3f(s, s, s); glVertex3f(s, s, -s)
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(-s, -s, -s); glVertex3f(s, -s, -s); glVertex3f(s, -s, s); glVertex3f(-s, -s, s)
        # Right
        glNormal3f(1, 0, 0)
        glVertex3f(s, -s, -s); glVertex3f(s, s, -s); glVertex3f(s, s, s); glVertex3f(s, -s, s)
        # Left
        glNormal3f(-1, 0, 0)
        glVertex3f(-s, -s, -s); glVertex3f(-s, -s, s); glVertex3f(-s, s, s); glVertex3f(-s, s, -s)
        glEnd()
    
    def render(self):
        # Jalan utama
        glPushMatrix()
        glColor3f(0.3, 0.3, 0.3)  # Warna aspal
        glTranslatef(0, 0.01, 0)  # Sedikit di atas ground
        glScalef(self.road_width, 0.1, self.road_length)
        self.draw_cube(1.0)
        glPopMatrix()
        
        # Marka jalan tengah
        self.draw_road_markings()
        
        # Trotoar
        self.draw_sidewalk()
    
    def draw_road_markings(self):
        glColor3f(1.0, 1.0, 0.0)  # Kuning
        
        mark_length = 3.0
        mark_gap = 5.0
        mark_width = 0.3
        
        for z in range(-self.road_length//2, self.road_length//2, int(mark_length + mark_gap)):
            glPushMatrix()
            glTranslatef(0, 0.02, z)
            glScalef(mark_width, 0.05, mark_length)
            self.draw_cube(1.0)
            glPopMatrix()
    
    def draw_sidewalk(self):
        glColor3f(0.6, 0.6, 0.6)  # Warna trotoar
        
        # Trotoar kiri
        glPushMatrix()
        glTranslatef(-self.road_width/2 - 1.5, 0.05, 0)
        glScalef(3.0, 0.15, self.road_length)
        self.draw_cube(1.0)
        glPopMatrix()
        
        # Trotoar kanan
        glPushMatrix()
        glTranslatef(self.road_width/2 + 1.5, 0.05, 0)
        glScalef(3.0, 0.15, self.road_length)
        self.draw_cube(1.0)
        glPopMatrix()