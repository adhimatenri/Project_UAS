# city.py - Enhanced Building System for Grid-Based City
import numpy as np
from OpenGL.GL import *
import random

class City:
    def __init__(self):
        self.buildings = []
        self.stars = []
        self.road_system = None  # Will be set by main.py
        
        # Building theme definitions optimized for dense coverage
        self.building_themes = {
            'residential': {
                'colors': [(0.8, 0.7, 0.6, 1.0), (0.7, 0.8, 0.7, 1.0), (0.9, 0.8, 0.7, 1.0)],
                'height_range': (8, 16),
                'size_range': (4, 6)
            },
            'commercial': {
                'colors': [(0.6, 0.6, 0.8, 1.0), (0.5, 0.7, 0.9, 1.0), (0.7, 0.7, 0.8, 1.0)],
                'height_range': (12, 22),
                'size_range': (5, 7)
            },
            'office': {
                'colors': [(0.4, 0.4, 0.5, 1.0), (0.5, 0.5, 0.6, 1.0), (0.3, 0.4, 0.6, 1.0)],
                'height_range': (15, 28),
                'size_range': (6, 8)
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
        """Generate perfect coverage buildings with exact segment dimensions"""
        if not self.road_system:
            print("⚠️  Cannot generate buildings - no road system reference")
            return
            
        self.buildings = []
        successful_count = 0
        attempted_count = 0
        
        # Step 1: Generate optimized perimeter walls
        perimeter_buildings = self.generate_optimized_perimeter_walls()
        successful_count += len(perimeter_buildings)
        attempted_count += len(perimeter_buildings)
        
        # Step 2: Generate perfect-fit buildings for each block segment
        for i, block in enumerate(self.road_system.city_blocks):
            theme = self.get_block_theme(block['center_x'], block['center_z'])
            block_buildings, block_attempts = self.generate_perfect_block_coverage(block, theme)
            successful_count += len(block_buildings)
            attempted_count += block_attempts
        
        print(f"   Building distribution: {attempted_count} attempted, {successful_count} successful")
        print(f"   🏢 Comprehensive coverage: {len(self.buildings)} total buildings")
    
    def generate_perfect_block_coverage(self, block, theme):
        """Generate perfect-fit buildings that exactly fill block segments with zero gaps"""
        block_buildings = []
        attempts = 0
        
        # Calculate exact buildable segments for this block
        segments = self.calculate_exact_segments(block)
        
        for segment in segments:
            attempts += 1
            
            # Create perfect-fit building for segment
            building = self.create_perfect_fit_building(segment, theme)
            
            # Verify building fits perfectly (minimal road overlap check)
            if not self.overlaps_road_area(building['x'], building['z'], building['width'], building['depth']):
                self.buildings.append(building)
                block_buildings.append(building)
        
        return block_buildings, attempts
    
    def calculate_exact_segments(self, block):
        """Calculate buildable segments with generous road clearance (never on roads)"""
        segments = []
        
        # Block info
        center_x = block['center_x']
        center_z = block['center_z']
        block_radius = block['size'] / 2.0
        block_left = center_x - block_radius
        block_right = center_x + block_radius
        block_top = center_z - block_radius
        block_bottom = center_z + block_radius
        
        # Road/clearance settings
        road_positions = [-30, 0, 30]
        road_half_width = 7.5
        sidewalk_buffer = 2.5   # Extra breathing room beyond painted road
        road_clearance = road_half_width + sidewalk_buffer  # 10 units from road center
        min_segment_size = 8.0
        inner_padding = 0.5     # Prevent floating point bleed into roads
        
        def compute_safe_ranges(range_start, range_end):
            """Return axis ranges fully outside any road exclusion zone"""
            safe_ranges = []
            current_start = range_start
            for road in road_positions:
                exclusion_start = road - road_clearance
                exclusion_end = road + road_clearance
                if exclusion_end <= range_start:
                    continue
                if exclusion_start >= range_end:
                    break
                if exclusion_start > current_start:
                    safe_ranges.append((current_start, min(exclusion_start, range_end)))
                current_start = max(current_start, min(exclusion_end, range_end))
                if current_start >= range_end:
                    break
            if current_start < range_end:
                safe_ranges.append((current_start, range_end))
            
            # Apply padding and size filter
            cleaned_ranges = []
            for start, end in safe_ranges:
                if end - start < min_segment_size:
                    continue
                padded_start = start + inner_padding
                padded_end = end - inner_padding
                if padded_end - padded_start >= min_segment_size:
                    cleaned_ranges.append((padded_start, padded_end))
            return cleaned_ranges
        
        safe_x_ranges = compute_safe_ranges(block_left, block_right)
        safe_z_ranges = compute_safe_ranges(block_top, block_bottom)
        
        for x_start, x_end in safe_x_ranges:
            width = x_end - x_start
            for z_start, z_end in safe_z_ranges:
                depth = z_end - z_start
                if width >= min_segment_size and depth >= min_segment_size:
                    segments.append({
                        'center_x': (x_start + x_end) / 2.0,
                        'center_z': (z_start + z_end) / 2.0,
                        'width': width,
                        'depth': depth
                    })
        
        return segments
    
    def quick_road_check(self, x, z):
        """Quick check if position is obviously on a road (center check only)"""
        if not self.road_system:
            return False
        return self.road_system.is_road_area(x, z, buffer=1.0)
    
    def create_perfect_fit_building(self, segment, theme):
        """Create building with exact segment dimensions for perfect coverage"""
        theme_data = self.building_themes[theme]
        
        # Use exact segment dimensions (no variation for perfect fit)
        width = segment['width']  # Exact fit
        depth = segment['depth']  # Exact fit
        height = random.uniform(*theme_data['height_range'])
        color = random.choice(theme_data['colors'])
        
        return {
            'x': segment['center_x'],
            'z': segment['center_z'],
            'width': width,
            'height': height,
            'depth': depth,
            'color': color,
            'theme': theme
        }
    
    def wall_overlaps_road(self, center_x, center_z, width, depth):
        """Wall-specific collision detection - only checks actual roads, not world boundaries"""
        if not self.road_system:
            return False
        
        # Only check core road positions [-30, 0, 30] with realistic margins
        road_positions = [-30, 0, 30]
        road_half_width = 7.5  # 15-unit road width / 2
        safety_margin = 2.0
        
        # Check building center and corners against actual road areas only
        half_w = width / 2.0
        half_d = depth / 2.0
        
        test_points = [
            (center_x, center_z),  # Center
            (center_x - half_w, center_z - half_d),  # Corners
            (center_x + half_w, center_z - half_d),
            (center_x - half_w, center_z + half_d),
            (center_x + half_w, center_z + half_d)
        ]
        
        for test_x, test_z in test_points:
            # Check against horizontal roads
            for road_z in road_positions:
                if abs(test_z - road_z) <= road_half_width + safety_margin:
                    return True
            
            # Check against vertical roads  
            for road_x in road_positions:
                if abs(test_x - road_x) <= road_half_width + safety_margin:
                    return True
        
        return False
    
    def wall_overlaps_road(self, center_x, center_z, width, depth):
        """Wall-specific collision detection - only checks actual roads, not world boundaries"""
        if not self.road_system:
            return False
        
        # Only check core road positions [-30, 0, 30] with realistic margins
        road_positions = [-30, 0, 30]
        road_half_width = 7.5  # 15-unit road width / 2
        safety_margin = 2.0
        
        # Check building center and corners against actual road areas only
        half_w = width / 2.0
        half_d = depth / 2.0
        
        test_points = [
            (center_x, center_z),  # Center
            (center_x - half_w, center_z - half_d),  # Corners
            (center_x + half_w, center_z - half_d),
            (center_x - half_w, center_z + half_d),
            (center_x + half_w, center_z + half_d)
        ]
        
        for test_x, test_z in test_points:
            # Check against horizontal roads
            for road_z in road_positions:
                if abs(test_z - road_z) <= road_half_width + safety_margin:
                    return True
            
            # Check against vertical roads  
            for road_x in road_positions:
                if abs(test_x - road_x) <= road_half_width + safety_margin:
                    return True
        
        return False

    def overlaps_road_area(self, center_x, center_z, width, depth):
        """Strict road overlap detection - matches calculate_exact_segments clearance"""
        if not self.road_system:
            return False
        
        road_positions = [-30, 0, 30]
        road_half_width = 7.5
        sidewalk_buffer = 2.5
        road_clearance = road_half_width + sidewalk_buffer
        
        half_w = width / 2.0
        half_d = depth / 2.0
        
        left = center_x - half_w
        right = center_x + half_w
        top = center_z - half_d
        bottom = center_z + half_d
        
        # Check vertical roads
        for road_x in road_positions:
            exclusion_left = road_x - road_clearance
            exclusion_right = road_x + road_clearance
            if not (right <= exclusion_left or left >= exclusion_right):
                return True
        
        # Check horizontal roads
        for road_z in road_positions:
            exclusion_top = road_z - road_clearance
            exclusion_bottom = road_z + road_clearance
            if not (bottom <= exclusion_top or top >= exclusion_bottom):
                return True
        
        return False
    
    def generate_optimized_perimeter_walls(self):
        """Generate comprehensive perimeter building system with complete coverage"""
        perimeter_buildings = []
        
        print("🏗️  Generating comprehensive perimeter system...")
        
        # Phase 1: Generate corner buildings (4 large corner zones)
        corner_buildings = self.generate_corner_buildings()
        perimeter_buildings.extend(corner_buildings)
        print(f"   Phase 1: {len(corner_buildings)} corner buildings generated")
        
        # Phase 2: Generate complete perimeter walls (100% edge coverage)
        wall_buildings = self.generate_complete_perimeter_walls()
        perimeter_buildings.extend(wall_buildings)
        print(f"   Phase 2: {len(wall_buildings)} wall segments generated")
        
        # Phase 3: Generate inner perimeter rings (systematic area coverage)
        ring_buildings = self.generate_inner_perimeter_rings()
        perimeter_buildings.extend(ring_buildings)
        print(f"   Phase 3: {len(ring_buildings)} ring buildings generated")
        
        # Add all perimeter buildings to main building list
        for building in perimeter_buildings:
            self.buildings.append(building)
        
        print(f"   Total perimeter buildings: {len(perimeter_buildings)}")
        return perimeter_buildings
        """Determine building theme for 4-block system with distinct districts"""
        # Create themed districts for the 4 blocks
        if center_x < 0 and center_z < 0:
            return 'office'      # Top-left: Downtown office district
        elif center_x > 0 and center_z < 0:
            return 'commercial'  # Top-right: Commercial district 
        elif center_x < 0 and center_z > 0:
            return 'residential' # Bottom-left: Residential district
        else:
            return 'residential' # Bottom-right: More residential
    

    

    
    def generate_corner_buildings(self):
        """Generate 16 corner buildings (4 per corner) for complete corner coverage"""
        corner_buildings = []
        corner_height = 18
        corner_color = (0.3, 0.3, 0.4, 1.0)
        
        # Each corner zone gets 4 buildings to fill completely
        # Corner zones: ±45 to ±80 in both x and z
        corner_specs = [
            # Northeast corner (x: 45-80, z: 45-80)
            {'x': 55, 'z': 55, 'w': 20, 'd': 20},
            {'x': 55, 'z': 72, 'w': 20, 'd': 16},
            {'x': 72, 'z': 55, 'w': 16, 'd': 20},
            {'x': 72, 'z': 72, 'w': 16, 'd': 16},
            # Northwest corner (x: -80 to -45, z: 45-80)
            {'x': -55, 'z': 55, 'w': 20, 'd': 20},
            {'x': -55, 'z': 72, 'w': 20, 'd': 16},
            {'x': -72, 'z': 55, 'w': 16, 'd': 20},
            {'x': -72, 'z': 72, 'w': 16, 'd': 16},
            # Southeast corner (x: 45-80, z: -80 to -45)
            {'x': 55, 'z': -55, 'w': 20, 'd': 20},
            {'x': 55, 'z': -72, 'w': 20, 'd': 16},
            {'x': 72, 'z': -55, 'w': 16, 'd': 20},
            {'x': 72, 'z': -72, 'w': 16, 'd': 16},
            # Southwest corner (x: -80 to -45, z: -80 to -45)
            {'x': -55, 'z': -55, 'w': 20, 'd': 20},
            {'x': -55, 'z': -72, 'w': 20, 'd': 16},
            {'x': -72, 'z': -55, 'w': 16, 'd': 20},
            {'x': -72, 'z': -72, 'w': 16, 'd': 16},
        ]
        
        for spec in corner_specs:
            corner_buildings.append({
                'x': spec['x'], 'z': spec['z'],
                'width': spec['w'], 'height': corner_height, 'depth': spec['d'],
                'color': corner_color, 'theme': 'corner'
            })
        
        return corner_buildings
    
    def generate_complete_perimeter_walls(self):
        """Generate continuous perimeter walls - 6 per edge, zero gaps"""
        wall_buildings = []
        wall_height = 15
        wall_color = (0.4, 0.4, 0.4, 1.0)
        
        # Continuous wall segments covering -45 to +45 range on each edge
        # Corners (±45 to ±80) handled by corner_buildings
        
        # North edge walls (z=72, x from -45 to 45)
        for x_pos in [-36, -18, 0, 18, 36]:
            wall_buildings.append({
                'x': x_pos, 'z': 72, 'width': 20, 'height': wall_height,
                'depth': 16, 'color': wall_color, 'theme': 'wall'
            })
        
        # South edge walls (z=-72, x from -45 to 45)
        for x_pos in [-36, -18, 0, 18, 36]:
            wall_buildings.append({
                'x': x_pos, 'z': -72, 'width': 20, 'height': wall_height,
                'depth': 16, 'color': wall_color, 'theme': 'wall'
            })
        
        # East edge walls (x=72, z from -45 to 45)
        for z_pos in [-36, -18, 0, 18, 36]:
            wall_buildings.append({
                'x': 72, 'z': z_pos, 'width': 16, 'height': wall_height,
                'depth': 20, 'color': wall_color, 'theme': 'wall'
            })
        
        # West edge walls (x=-72, z from -45 to 45)
        for z_pos in [-36, -18, 0, 18, 36]:
            wall_buildings.append({
                'x': -72, 'z': z_pos, 'width': 16, 'height': wall_height,
                'depth': 20, 'color': wall_color, 'theme': 'wall'
            })
        
        return wall_buildings
    
    def generate_inner_perimeter_rings(self):
        """Generate dense inner ring buildings between city blocks and outer walls"""
        ring_buildings = []
        ring_color = (0.5, 0.4, 0.3, 1.0)
        
        # North inner row (z=50) - fills gap between city and north wall
        for x in [-40, -20, 0, 20, 40]:
            ring_buildings.append({
                'x': x, 'z': 50, 'width': 18, 'height': 14, 'depth': 14,
                'color': ring_color, 'theme': 'ring1'
            })
        
        # South inner row (z=-50)
        for x in [-40, -20, 0, 20, 40]:
            ring_buildings.append({
                'x': x, 'z': -50, 'width': 18, 'height': 14, 'depth': 14,
                'color': ring_color, 'theme': 'ring1'
            })
        
        # East inner column (x=50) - avoid overlapping with z=±50 rows
        for z in [-25, 0, 25]:
            ring_buildings.append({
                'x': 50, 'z': z, 'width': 14, 'height': 14, 'depth': 18,
                'color': ring_color, 'theme': 'ring1'
            })
        
        # West inner column (x=-50)
        for z in [-25, 0, 25]:
            ring_buildings.append({
                'x': -50, 'z': z, 'width': 14, 'height': 14, 'depth': 18,
                'color': ring_color, 'theme': 'ring1'
            })
        
        return ring_buildings
        """Determine building theme for 4-block system with distinct districts"""
        # Create themed districts for the 4 blocks
        if center_x < 0 and center_z < 0:
            return 'office'      # Top-left: Downtown office district
        elif center_x > 0 and center_z < 0:
            return 'commercial'  # Top-right: Commercial district 
        elif center_x < 0 and center_z > 0:
            return 'residential' # Bottom-left: Residential district
        else:
            return 'residential' # Bottom-right: More residential

    def get_block_theme(self, center_x, center_z):
        """Determine building theme for 4-block system with distinct districts"""
        # Create themed districts for the 4 blocks
        if center_x < 0 and center_z < 0:
            return 'office'      # Top-left: Downtown office district
        elif center_x > 0 and center_z < 0:
            return 'commercial'  # Top-right: Commercial district 
        elif center_x < 0 and center_z > 0:
            return 'residential' # Bottom-left: Residential district
        else:
            return 'residential' # Bottom-right: More residential

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