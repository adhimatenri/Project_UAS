# city.py
import numpy as np
from OpenGL.GL import *
import random

class City:
    def __init__(self):
        self.buildings = []
        self.stars = []
        self.generate_buildings()
        self.generate_stars()
    
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
                
                # Random "lights on" effect
                # We use hash or determinism based on coordinates so it doesn't flicker
                import hashlib
                win_hash = int(hashlib.md5(f"{building['x']}{building['z']}{i}{j}".encode()).hexdigest(), 16)
                if win_hash % 3 == 0: # 1 in 3 windows is lit
                    glMaterialfv(GL_FRONT, GL_EMISSION, [0.5, 0.5, 0.3, 1.0])
                    glColor3f(1.0, 1.0, 0.5) # Yellowish light
                else:
                    glColor3f(0.2, 0.2, 0.3) # Dark window
                
                self.draw_cube(1, 1, 1)
                # Reset emission
                glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
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
        # Draw sky first (background)
        self.draw_sky()
        
        for building in self.buildings:
            self.draw_building(building)
        
        # Lampu jalan
        self.draw_street_lights()
        
    def generate_stars(self):
        """Generate random stars"""
        for _ in range(200):
            # Stars around the sky dome
            theta = random.uniform(0, 2 * np.pi)
            phi = random.uniform(0, np.pi / 2.5) # Don't go too low to horizon
            r = 400.0 # Far away
            
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.cos(phi)
            z = r * np.sin(phi) * np.sin(theta)
            
            self.stars.append((x, y, z))

    def draw_sky(self):
        """Draw stars and moon"""
        # Stars
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for star in self.stars:
            glVertex3f(star[0], star[1], star[2])
        glEnd()
        
        # Moon
        glPushMatrix()
        # Position moon roughly where the light source is
        glTranslatef(50.0, 50.0, 50.0) 
        glColor3f(1.0, 1.0, 0.9) # Pale yellow
        
        # Moon glow
        glEnable(GL_LIGHTING) # Enable lighting for moon to be visible properly or just use emission
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.8, 0.8, 0.7, 1.0])
        
        self.draw_sphere(5.0)
        
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()
        
        glEnable(GL_LIGHTING)

    def draw_street_lights(self):
        glColor3f(0.3, 0.3, 0.3)
        
        # Extended range to match road length (approx -100 to 100)
        for z in range(-100, 101, 25): 
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
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glScalef(0.1, 8.0, 0.1)
        self.draw_cube(1, 1, 1)
        glPopMatrix()
        
        # Kepala lampu
        glPushMatrix()
        glTranslatef(0, 4.0, 0)
        
        # Efek menyala kuning (Emissive)
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 0.0, 1.0])
        glColor3f(1.0, 1.0, 0.0)
        
        self.draw_sphere(0.5)
        
        # Reset emission
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()