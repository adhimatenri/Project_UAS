# city.py
import numpy as np
from OpenGL.GL import *
import random

class City:
    def __init__(self):
        self.buildings = []
        self.generate_buildings()
    
    def generate_buildings(self):
        for i in range(-50, 51, 20):
            for j in range(-50, 51, 20):
                if abs(i) < 10 and abs(j) < 100:
                    continue
                
                height = random.uniform(5, 30)
                width = random.uniform(3, 8)
                depth = random.uniform(3, 8)
                
                color = [
                    random.uniform(0.3, 0.8),
                    random.uniform(0.3, 0.8),
                    random.uniform(0.3, 0.8),
                    1.0
                ]
                
                self.buildings.append({
                    'x': i + random.uniform(-5, 5),
                    'z': j + random.uniform(-5, 5),
                    'width': width,
                    'height': height,
                    'depth': depth,
                    'color': color
                })
    
    def draw_cube(self, width, height, depth):
        """Draw cube manually"""
        w = width / 2
        h = height / 2
        d = depth / 2
        
        glBegin(GL_QUADS)
        
        # Front
        glNormal3f(0, 0, 1)
        glVertex3f(-w, -h, d); glVertex3f(w, -h, d)
        glVertex3f(w, h, d); glVertex3f(-w, h, d)
        
        # Back
        glNormal3f(0, 0, -1)
        glVertex3f(-w, -h, -d); glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d); glVertex3f(w, -h, -d)
        
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d); glVertex3f(-w, h, d)
        glVertex3f(w, h, d); glVertex3f(w, h, -d)
        
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d); glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d); glVertex3f(-w, -h, d)
        
        # Right
        glNormal3f(1, 0, 0)
        glVertex3f(w, -h, -d); glVertex3f(w, h, -d)
        glVertex3f(w, h, d); glVertex3f(w, -h, d)
        
        # Left
        glNormal3f(-1, 0, 0)
        glVertex3f(-w, -h, -d); glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d); glVertex3f(-w, h, -d)
        
        glEnd()
    
    def draw_building(self, building):
        glPushMatrix()
        glTranslatef(building['x'], building['height']/2, building['z'])
        glColor4fv(building['color'])
        
        self.draw_cube(building['width'], building['height'], building['depth'])
        
        # Jendela-jendela (sederhana)
        self.draw_windows(building)
        
        glPopMatrix()
    
    def draw_windows(self, building):
        glColor3f(0.8, 0.9, 1.0)
        
        window_count = 3
        for i in range(window_count):
            for j in range(2):
                glPushMatrix()
                x_pos = (j - 0.5) * (building['width'] * 0.6)
                y_pos = (i - 1) * (building['height'] * 0.25)
                glTranslatef(x_pos, y_pos, building['depth']/2 + 0.1)
                glScalef(0.2, 0.2, 0.1)
                self.draw_cube(1, 1, 1)
                glPopMatrix()
    
    def draw_sphere(self, radius):
        """Simple sphere drawing"""
        slices = 16
        stacks = 16
        
        for i in range(stacks):
            lat0 = np.pi * (-0.5 + (i) / stacks)
            z0 = np.sin(lat0) * radius
            zr0 = np.cos(lat0) * radius
            
            lat1 = np.pi * (-0.5 + (i + 1) / stacks)
            z1 = np.sin(lat1) * radius
            zr1 = np.cos(lat1) * radius
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * np.pi * (j) / slices
                x = np.cos(lng)
                y = np.sin(lng)
                
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()
    
    def render(self):
        for building in self.buildings:
            self.draw_building(building)
        
        # Lampu jalan
        self.draw_street_lights()
    
    def draw_street_lights(self):
        glColor3f(0.3, 0.3, 0.3)
        
        for z in range(-50, 51, 20):
            # Lampu kiri
            glPushMatrix()
            glTranslatef(-8, 0, z)
            self.draw_single_street_light()
            glPopMatrix()
            
            # Lampu kanan
            glPushMatrix()
            glTranslatef(8, 0, z)
            self.draw_single_street_light()
            glPopMatrix()
    
    def draw_single_street_light(self):
        # Tiang
        glPushMatrix()
        glScalef(0.1, 8.0, 0.1)
        self.draw_cube(1, 1, 1)
        glPopMatrix()
        
        # Kepala lampu
        glPushMatrix()
        glTranslatef(0, 8, 0)
        glColor3f(1.0, 1.0, 0.8)
        self.draw_sphere(0.5)
        glPopMatrix()