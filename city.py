# city.py - Enhanced Building System for Grid-Based City
import numpy as np
from OpenGL.GL import *
import random

class City:
    def __init__(self):
        self.buildings = []
        self.stars = []
        self.road_system = None  # Will be set by main.py
        
        # Building theme definitions
        self.building_themes = {
            'residential': {
                'colors': [(0.8, 0.7, 0.6, 1.0), (0.7, 0.8, 0.7, 1.0), (0.9, 0.8, 0.7, 1.0)],
                'height_range': (8, 18),
                'size_range': (4, 7)
            },
            'commercial': {
                'colors': [(0.6, 0.6, 0.8, 1.0), (0.5, 0.7, 0.9, 1.0), (0.7, 0.7, 0.8, 1.0)],
                'height_range': (12, 25),
                'size_range': (5, 9)
            },
            'office': {
                'colors': [(0.4, 0.4, 0.5, 1.0), (0.5, 0.5, 0.6, 1.0), (0.3, 0.4, 0.6, 1.0)],
                'height_range': (15, 35),
                'size_range': (6, 12)
            }
        }
        
        self.generate_stars()
        print("🏙️  City system initialized - awaiting road system for building placement")
    
    def set_road_system(self, road_system):
        """Set reference to road system and generate buildings"""
        self.road_system = road_system
        self.generate_buildings_in_blocks()
        print(f"🏢  Generated {len(self.buildings)} buildings in {len(self.road_system.city_blocks)} city blocks")
    
    def generate_buildings_in_blocks(self):
        """Generate buildings only within designated city blocks"""
        if not self.road_system:
            print("⚠️  Cannot generate buildings - no road system reference")
            return
            
        self.buildings = []
        successful_count = 0
        attempted_count = 0
        
        for i, block in enumerate(self.road_system.city_blocks):
            # Determine theme based on block position (create districts)
            theme = self.get_block_theme(block['center_x'], block['center_z'])
            
            # Generate 2-4 buildings per block
            buildings_per_block = random.randint(2, 4)
            block_buildings = 0
            
            for attempt in range(buildings_per_block * 2):  # More attempts per block
                attempted_count += 1
                building = self.generate_single_building_in_block(block, theme)
                
                if building:
                    if not self.building_overlaps_road(building):
                        self.buildings.append(building)
                        successful_count += 1
                        block_buildings += 1
                        if block_buildings >= buildings_per_block:
                            break  # Got enough buildings for this block
                    else:
                        # Debug: print why building was rejected
                        if i == 0 and attempt < 2:  # Only debug first block, first attempts
                            print(f"🔍 Debug: Building at ({building['x']:.1f}, {building['z']:.1f}) rejected (road overlap)")
        
        print(f"   Building distribution: {attempted_count} attempted, {successful_count} successful")
        if successful_count == 0:
            print("⚠️  No buildings generated - checking road overlap algorithm...")
    
    def get_block_theme(self, center_x, center_z):
        """Determine building theme based on city block location"""
        # Create themed districts
        if abs(center_x) <= 15 and abs(center_z) <= 15:
            return 'office'  # Downtown core
        elif abs(center_x) <= 30 or abs(center_z) <= 30:  
            return 'commercial'  # Commercial ring
        else:
            return 'residential'  # Outer residential areas
    
    def generate_single_building_in_block(self, block, theme):
        """Generate a single building within a city block"""
        theme_data = self.building_themes[theme]
        
        # Building dimensions based on theme  
        width = random.uniform(*theme_data['size_range'])
        depth = random.uniform(*theme_data['size_range'])
        height = random.uniform(*theme_data['height_range'])
        
        # Position within block (leave 3-unit margin from block edges)
        margin = 4.0  # Increased margin to ensure clearance
        max_offset = (block['size'] / 2.0) - margin - (max(width, depth) / 2.0)
        
        if max_offset <= 0:
            return None  # Building too large for block
        
        offset_x = random.uniform(-max_offset, max_offset)
        offset_z = random.uniform(-max_offset, max_offset)
        
        building_x = block['center_x'] + offset_x
        building_z = block['center_z'] + offset_z
        
        # Select color from theme
        color = random.choice(theme_data['colors'])
        
        # Debug first few buildings
        if len(self.buildings) < 3:
            print(f"🏗️ Building attempt: Block center=({block['center_x']}, {block['center_z']}), Building=({building_x:.1f}, {building_z:.1f})")
        
        return {
            'x': building_x,
            'z': building_z,
            'width': width,
            'height': height,
            'depth': depth,
            'color': color,
            'theme': theme
        }
    
    def building_overlaps_road(self, building):
        """Enhanced check to ensure building doesn't overlap with roads"""
        if not self.road_system:
            return False
            
        # Reduced safety buffer for testing
        buffer = 0.5
        
        # Check building center first (simplest test)
        center_x, center_z = building['x'], building['z']
        if self.road_system.is_road_area(center_x, center_z, buffer=1.0):
            return True
        
        # Check building corners with smaller buffer
        half_w = building['width'] / 2.0
        half_d = building['depth'] / 2.0
        
        test_points = [
            (center_x - half_w, center_z - half_d),  # Corner 1
            (center_x + half_w, center_z - half_d),  # Corner 2
            (center_x - half_w, center_z + half_d),  # Corner 3
            (center_x + half_w, center_z + half_d),  # Corner 4
        ]
        
        for x, z in test_points:
            if self.road_system.is_road_area(x, z, buffer=buffer):
                return True
                
        return False
    
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
        win_size = 0.6  
        win_depth = 0.1
        
        # Iterate over 2 sides only: 0=Front, 2=Back
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
                face_width = building['depth']
                face_dist = building['width'] / 2.0
            
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
                lng = 2 * np.pi * j / slices
                x = np.cos(lng)
                y = np.sin(lng)
                
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()

    def render(self):
        """Render all city elements"""
        # Draw stars and sky first (background)
        self.draw_sky()
        
        # Draw all buildings
        for building in self.buildings:
            self.draw_building(building)
        
        # Draw street lights
        if self.road_system:
            self.draw_street_lights()
    
    def get_buildings_for_collision(self):
        """Return building list for collision detection (compatibility method)"""
        return self.buildings

    def generate_stars(self):
        """Generate random stars"""
        for _ in range(1000):
            # Stars around the sky dome
            theta = random.uniform(0, 2 * np.pi)
            # Lowered logic: allow stars closer to horizon (pi/2)
            phi = random.uniform(0, np.pi / 2.05) 
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
        # Position moon centered on road (X=0), higher and further away
        glTranslatef(0.0, 60.0, 150.0) 
        glColor3f(1.0, 1.0, 0.8) # Brighter Pale yellow
        
        # Moon glow
        glEnable(GL_LIGHTING) 
        # Stronger emission for "moon effect"
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.9, 0.9, 0.7, 1.0])
        
        # Slightly larger moon
        self.draw_sphere(8.0)
        
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()
        
        glEnable(GL_LIGHTING)

    def draw_street_lights(self):
        """Draw street lights along roads (updated for grid system)"""
        if not self.road_system:
            return
            
        glColor3f(0.3, 0.3, 0.3)
        
        # Street lights along horizontal roads
        for road_z in self.road_system.horizontal_roads:
            for x in range(-80, 81, 25):
                # Skip intersection areas
                if not any(abs(x - road_x) <= 10 for road_x in self.road_system.vertical_roads):
                    # Left side lights
                    glPushMatrix()
                    glTranslatef(x, 0, road_z - 8)
                    self.draw_single_street_light()
                    glPopMatrix()
                    
                    # Right side lights
                    glPushMatrix()
                    glTranslatef(x, 0, road_z + 8)
                    self.draw_single_street_light()
                    glPopMatrix()
        
        # Street lights along vertical roads
        for road_x in self.road_system.vertical_roads:
            for z in range(-80, 81, 25):
                # Skip intersection areas
                if not any(abs(z - road_z) <= 10 for road_z in self.road_system.horizontal_roads):
                    # Left side lights
                    glPushMatrix()
                    glTranslatef(road_x - 8, 0, z)
                    self.draw_single_street_light()
                    glPopMatrix()
                    
                    # Right side lights
                    glPushMatrix()
                    glTranslatef(road_x + 8, 0, z)
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
        self.draw_street_lights()
        
    def generate_stars(self):
        """Generate random stars"""
        for _ in range(1000):
            # Stars around the sky dome
            theta = random.uniform(0, 2 * np.pi)
            # Lowered logic: allow stars closer to horizon (pi/2)
            phi = random.uniform(0, np.pi / 2.05) 
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
        # Position moon centered on road (X=0), higher and further away
        glTranslatef(0.0, 60.0, 150.0) 
        glColor3f(1.0, 1.0, 0.8) # Brighter Pale yellow
        
        # Moon glow
        glEnable(GL_LIGHTING) 
        # Stronger emission for "moon effect"
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.9, 0.9, 0.7, 1.0])
        
        # Slightly larger moon
        self.draw_sphere(8.0)
        
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