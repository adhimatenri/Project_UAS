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
        # Adjusted to strictly avoid road overlap using coordinate checks
        for i in range(-60, 61, 15):
            for j in range(-60, 61, 20):
                
                width = random.uniform(3, 8)
                height = random.uniform(5, 30)
                depth = random.uniform(3, 8)
                
                # Generate exact position first
                noise_x = random.uniform(-5, 5)
                noise_z = random.uniform(-5, 5)
                
                cand_x = i + noise_x
                cand_z = j + noise_z
                
                # ROAD SAFE ZONE CHECK
                # Road width=15, Sidewalk extends to ~10.5. 
                # Exact sidewalk edge is 10.5.
                
                min_x = cand_x - width/2
                max_x = cand_x + width/2
                
                if max_x > -10.5 and min_x < 10.5:
                    continue
                
                color = [
                    random.uniform(0.3, 0.8),
                    random.uniform(0.3, 0.8),
                    random.uniform(0.3, 0.8),
                    1.0
                ]
                
                self.buildings.append({
                    'x': cand_x,
                    'z': cand_z,
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
        # Window settings
        win_size = 0.6  # Enlarged from ~0.2
        win_depth = 0.1
        
        # Iterate over 2 sides only: 0=Front, 2=Back (Searah dengan jalan/Z-axis)
        for side in [0, 2]:
            glPushMatrix()
            
            # Rotate to the correct side
            glRotatef(side * 90, 0, 1, 0)
            
            # Determine face dimensions based on side
            # 0 & 2 (Front/Back) use width for horizontal spacing, depth for distance
            if side % 2 == 0:
                face_width = building['width']
                face_dist = building['depth'] / 2.0
            else:
                # Should not happen in this loop but kept for logic
                face_width = building['depth']
                face_dist = building['width'] / 2.0
                
            # Logic for window placement on this face
            # Calculate how many windows fit horizontally and vertically
            
            # Simple grid: 2 columns, N rows depending on height
            cols = 2
            rows = max(2, int(building['height'] / 2.5))
            
            for i in range(rows):
                for j in range(cols):
                    glPushMatrix()
                    
                    # Position on face
                    # Spread columns across face_width
                    # (j - 0.5) centers 2 columns. For more cols physics is different.
                    x_pos = (j - 0.5) * (face_width * 0.5) 
                    
                    # Spread rows along height
                    # Start from bottomish? 
                    y_pos = (i - rows/2 + 0.5) * (building['height'] / rows) * 0.8
                    
                    # Translate to face surface
                    glTranslatef(x_pos, y_pos, face_dist + 0.05)
                    
                    # Scale window (Enlarged)
                    glScalef(win_size, win_size, win_depth)
                    
                    # Random "lights on" effect
                    # Hash includes side to vary pattern per side
                    import hashlib
                    win_hash = int(hashlib.md5(f"{building['x']}{building['z']}{side}{i}{j}".encode()).hexdigest(), 16)
                    
                    if win_hash % 3 == 0:
                        glMaterialfv(GL_FRONT, GL_EMISSION, [0.6, 0.6, 0.4, 1.0])
                        glColor3f(1.0, 1.0, 0.6) # Brighter yellow
                    else:
                        glColor3f(0.1, 0.1, 0.2) # Dark window
                        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
                    
                    self.draw_cube(1, 1, 1)
                    
                    # Reset emission
                    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
                    glPopMatrix()
            
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
        # MANUAL POLE DRAWING WITH GRADIENT (Tiang dengan efek cahaya)
        # Replaces simple cube scaling to allow vertex coloring
        
        w = 0.05 # Half width (matches 0.1 scale)
        h_top = 4.0
        h_bot = -4.0
        
        # Colors
        c_dark = [0.2, 0.2, 0.2]      # Bottom (Dark)
        c_lit = [1.0, 1.0, 0.5]       # Top (Illuminated by lamp)
        
        glBegin(GL_QUADS)
        # Front
        glNormal3f(0, 0, 1)
        glColor3fv(c_dark); glVertex3f(-w, h_bot, w); glVertex3f(w, h_bot, w)
        glColor3fv(c_lit);  glVertex3f(w, h_top, w); glVertex3f(-w, h_top, w)
        
        # Back
        glNormal3f(0, 0, -1)
        glColor3fv(c_dark); glVertex3f(w, h_bot, -w); glVertex3f(-w, h_bot, -w)
        glColor3fv(c_lit);  glVertex3f(-w, h_top, -w); glVertex3f(w, h_top, -w)
        
        # Right
        glNormal3f(1, 0, 0)
        glColor3fv(c_dark); glVertex3f(w, h_bot, -w); glVertex3f(w, h_bot, w)
        glColor3fv(c_lit);  glVertex3f(w, h_top, w); glVertex3f(w, h_top, -w)
        
        # Left
        glNormal3f(-1, 0, 0)
        glColor3fv(c_dark); glVertex3f(-w, h_bot, w); glVertex3f(-w, h_bot, -w)
        glColor3fv(c_lit);  glVertex3f(-w, h_top, -w); glVertex3f(-w, h_top, w)
        glEnd()
        
        # Kepala lampu
        glPushMatrix()
        glTranslatef(0, 4.0, 0)
        
        # 1. Bulb (Intense Center)
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 0.0, 1.0])
        glColor3f(1.0, 1.0, 0.0)
        self.draw_sphere(0.5)
        
        # 2. Glow Halo (Transparent Outer Sphere)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE) # Additive blending creates "glow"
        glDepthMask(GL_FALSE) # Don't write key to depth buffer
        
        glColor4f(1.0, 0.8, 0.0, 0.2) # Yellowish transparent
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.5, 0.4, 0.0, 1.0])
        self.draw_sphere(1.5) # Larger radius
        
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # Reset default
        
        # Reset emission
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()