import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import pygame
import os

class City:
    def __init__(self):
        self.buildings = []
        self.stars = []
        self.road_system = None  # Will be set by main.py
        self.road_system = None  # Will be set by main.py
        self.city_display_list = None  # GPU-compiled geometry for performance
        self.street_lights_display_list = None  # GPU-compiled street lights
        
        # Load textures (Deferred to setup_gl_resources)
        self.texture_id = None
        
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
        self.generate_stars()
        print("🏙️  City system initialized - awaiting road system for building placement")
        
    def setup_gl_resources(self):
        """Initialize OpenGL resources after context creation"""
        self.texture_id = self.load_texture("assets/building_texture.png")
        print("   ✅ City GL resources loaded")

    def load_texture(self, filename):
        """Load texture from file"""
        try:
            if not os.path.exists(filename):
                print(f"⚠️ Texture not found: {filename}")
                return None
                
            texture_surface = pygame.image.load(filename)
            texture_data = pygame.image.tostring(texture_surface, "RGB", 1)
            width = texture_surface.get_width()
            height = texture_surface.get_height()
            
            tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            
            gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, width, height, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
            return tex_id
        except Exception as e:
            print(f"Error loading texture {filename}: {e}")
            return None
    
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
        stats = getattr(self, 'perimeter_edge_stats', None)
        if stats:
            print(
                "   Perimeter coverage -> "
                f"N:{stats.get('north',0)} S:{stats.get('south',0)} "
                f"E:{stats.get('east',0)} W:{stats.get('west',0)} "
                f"Corners:{stats.get('corner',0)} Seam:{stats.get('seam',0)}"
            )
        
        # Step 2: Generate perfect-fit buildings for each block segment
        for i, block in enumerate(self.road_system.city_blocks):
            theme = self.get_block_theme(block['center_x'], block['center_z'])
            block_buildings, block_attempts = self.generate_perfect_block_coverage(block, theme)
            successful_count += len(block_buildings)
            attempted_count += block_attempts
        
        print(f"   Building distribution: {attempted_count} attempted, {successful_count} successful")
        print(f"   🏢 Perfect coverage: {len(self.buildings)} buildings with zero gaps")
    
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
        """Calculate 4 precise segments per block avoiding roads at [-30, 0, 30]"""
        segments = []
        
        # Block boundaries
        block_radius = block['size'] / 2.0  # 25 units
        center_x = block['center_x']
        center_z = block['center_z']
        
        # Road positions: [-30, 0, 30] with 15-unit width (±7.5 from center)
        road_half_width = 7.5
        
        # Calculate segments that avoid roads
        # For block at (-15, -15): roads at x=[-30, 0, 30] and z=[-30, 0, 30]
        # Available x ranges: block_center ± 25, avoiding roads
        # Available z ranges: block_center ± 25, avoiding roads
        
        # Determine which roads intersect this block
        block_left = center_x - block_radius    # -40
        block_right = center_x + block_radius   # +10
        block_top = center_z - block_radius     # -40  
        block_bottom = center_z + block_radius  # +10
        
        # Find road intersections within this block
        intersecting_x_roads = []
        for road_x in [-30, 0, 30]:
            if block_left <= road_x <= block_right:
                intersecting_x_roads.append(road_x)
        
        intersecting_z_roads = []
        for road_z in [-30, 0, 30]:
            if block_top <= road_z <= block_bottom:
                intersecting_z_roads.append(road_z)
        
        # Create segments by dividing block around intersecting roads with proper clearance
        road_clearance = road_half_width + 0.2  # Reduced clearance for better coverage
        
        x_boundaries = [block_left] + [r - road_clearance for r in intersecting_x_roads] + [r + road_clearance for r in intersecting_x_roads] + [block_right]
        z_boundaries = [block_top] + [r - road_clearance for r in intersecting_z_roads] + [r + road_clearance for r in intersecting_z_roads] + [block_bottom]
        
        # Sort and remove duplicates
        x_boundaries = sorted(list(set(x_boundaries)))
        z_boundaries = sorted(list(set(z_boundaries)))
        
        # Create segments from boundary combinations with optimized selection
        valid_segments = []
        for i in range(len(x_boundaries) - 1):
            for j in range(len(z_boundaries) - 1):
                x_start = x_boundaries[i]
                x_end = x_boundaries[i + 1]
                z_start = z_boundaries[j]
                z_end = z_boundaries[j + 1]
                
                width = x_end - x_start
                depth = z_end - z_start
                
                # Accept segments with smaller minimum size for maximum coverage
                if width >= 4.0 and depth >= 4.0:
                    seg_center_x = (x_start + x_end) / 2.0
                    seg_center_z = (z_start + z_end) / 2.0
                    
                    # Quick pre-filter: skip segments obviously on roads
                    if not self.quick_road_check(seg_center_x, seg_center_z):
                        valid_segments.append({
                            'center_x': seg_center_x,
                            'center_z': seg_center_z,
                            'width': width,
                            'depth': depth
                        })
        
        # Sort segments by size (largest first for better coverage)
        valid_segments.sort(key=lambda s: s['width'] * s['depth'], reverse=True)
        
        print(f"   Block ({center_x}, {center_z}): Generated {len(valid_segments)} valid segments")
        return valid_segments
    
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
    
    def overlaps_road_area(self, center_x, center_z, width, depth):
        """Precise road overlap detection for perfect-fit buildings"""
        if not self.road_system:
            return False
        
        # Minimal buffer for mathematical precision only
        buffer = 0.1
        
        # Check if building center is in road
        if self.road_system.is_road_area(center_x, center_z, buffer=buffer):
            return True
        
        # Check building corners with minimal buffer
        half_w = width / 2.0
        half_d = depth / 2.0
        
        corners = [
            (center_x - half_w, center_z - half_d),  # Top-left
            (center_x + half_w, center_z - half_d),  # Top-right
            (center_x - half_w, center_z + half_d),  # Bottom-left
            (center_x + half_w, center_z + half_d)   # Bottom-right
        ]
        
        for x, z in corners:
            if self.road_system.is_road_area(x, z, buffer=buffer):
                return True
        
        return False
    
    def generate_optimized_perimeter_walls(self):
        """Tile the entire outer belt (|coord| ∈ [45, 80]) with road-safe buildings"""
        if not self.road_system:
            self.perimeter_edge_stats = {}
            return []
        
        perimeter_buildings = []
        stats = {'north': 0, 'south': 0, 'east': 0, 'west': 0, 'corner': 0, 'seam': 0}
        self.perimeter_edge_stats = stats
        inner_limit = 45.0
        outer_limit = 80.0
        seam_depth = 4.0
        min_segment = 3.0
        edge_tile_width = 18.0
        edge_tile_depth = 12.0
        corner_tile = 16.0
        edge_height_range = (12.0, 18.0)
        corner_height_range = (18.0, 24.0)
        edge_palette = [
            (0.33, 0.33, 0.37, 1.0),
            (0.28, 0.30, 0.34, 1.0),
            (0.36, 0.34, 0.30, 1.0)
        ]
        corner_palette = [
            (0.22, 0.24, 0.30, 1.0),
            (0.26, 0.28, 0.32, 1.0),
            (0.24, 0.22, 0.28, 1.0)
        ]
        road_half = (getattr(self.road_system, 'road_width', 15.0) / 2.0) + 0.5
        vertical_roads = getattr(self.road_system, 'vertical_roads', [-30, 0, 30])
        horizontal_roads = getattr(self.road_system, 'horizontal_roads', [-30, 0, 30])

        def span_ranges(start, end, preferred_size):
            ranges = []
            cursor = start
            while cursor < end - 1e-3:
                seg_end = min(cursor + preferred_size, end)
                ranges.append((cursor, seg_end))
                cursor = seg_end
            return ranges

        def carve_road_gaps(ranges, road_values):
            carved = []
            for seg_start, seg_end in ranges:
                segments = [(seg_start, seg_end)]
                for road in road_values:
                    cut_start = road - road_half
                    cut_end = road + road_half
                    next_segments = []
                    for sub_start, sub_end in segments:
                        if sub_end <= cut_start or sub_start >= cut_end:
                            next_segments.append((sub_start, sub_end))
                            continue
                        if sub_start < cut_start:
                            next_segments.append((sub_start, cut_start))
                        if cut_end < sub_end:
                            next_segments.append((cut_end, sub_end))
                    segments = [s for s in next_segments if s[1] - s[0] >= min_segment]
                carved.extend(segments)
            return carved

        def ranges_to_spans(ranges):
            return [((start + end) / 2.0, end - start) for start, end in ranges if end - start >= min_segment]

        def add_perimeter_building(center_x, center_z, width, depth, height_range, palette, zone):
            if abs(center_x) > outer_limit + 0.1 or abs(center_z) > outer_limit + 0.1:
                return
            if self.overlaps_road_area(center_x, center_z, width, depth):
                return
            building = {
                'x': center_x,
                'z': center_z,
                'width': width,
                'depth': depth,
                'height': random.uniform(*height_range),
                'color': random.choice(palette),
                'theme': 'perimeter'
            }
            self.buildings.append(building)
            perimeter_buildings.append(building)
            if zone in stats:
                stats[zone] += 1

        # North/South belts
        x_long_ranges = carve_road_gaps(span_ranges(-outer_limit, outer_limit, edge_tile_width), vertical_roads)
        x_spans = ranges_to_spans(x_long_ranges)
        z_band_spans = ranges_to_spans(span_ranges(inner_limit, outer_limit, edge_tile_depth))
        for z_center, depth in z_band_spans:
            for x_center, width in x_spans:
                add_perimeter_building(x_center, z_center, width, depth, edge_height_range, edge_palette, 'north')
                add_perimeter_building(x_center, -z_center, width, depth, edge_height_range, edge_palette, 'south')

        # East/West belts
        z_long_ranges = carve_road_gaps(span_ranges(-outer_limit, outer_limit, edge_tile_width), horizontal_roads)
        z_spans = ranges_to_spans(z_long_ranges)
        x_band_spans = ranges_to_spans(span_ranges(inner_limit, outer_limit, edge_tile_depth))
        for x_center, width in x_band_spans:
            for z_center, depth in z_spans:
                add_perimeter_building(x_center, z_center, width, depth, edge_height_range, edge_palette, 'east')
                add_perimeter_building(-x_center, z_center, width, depth, edge_height_range, edge_palette, 'west')

        # Corner grids for skyline depth
        corner_spans = ranges_to_spans(span_ranges(inner_limit, outer_limit, corner_tile))
        for x_center, width in corner_spans:
            for z_center, depth in corner_spans:
                add_perimeter_building(x_center, z_center, width, depth, corner_height_range, corner_palette, 'corner')
                add_perimeter_building(-x_center, z_center, width, depth, corner_height_range, corner_palette, 'corner')
                add_perimeter_building(x_center, -z_center, width, depth, corner_height_range, corner_palette, 'corner')
                add_perimeter_building(-x_center, -z_center, width, depth, corner_height_range, corner_palette, 'corner')

        # Outer seam flush with ±80 to hide any remaining voids
        seam_spans = ranges_to_spans(span_ranges(outer_limit - seam_depth, outer_limit, seam_depth))
        for z_center, depth in seam_spans:
            for x_center, width in x_spans:
                add_perimeter_building(x_center, z_center, width, depth, edge_height_range, edge_palette, 'seam')
                add_perimeter_building(x_center, -z_center, width, depth, edge_height_range, edge_palette, 'seam')
        for x_center, width in seam_spans:
            for z_center, depth in z_spans:
                add_perimeter_building(x_center, z_center, width, depth, edge_height_range, edge_palette, 'seam')
                add_perimeter_building(-x_center, z_center, width, depth, edge_height_range, edge_palette, 'seam')

        return perimeter_buildings
    

    

    
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

        glEnd()

    def draw_textured_cube(self, width, height, depth):
        """Draw cube with texture coordinates"""
        w = width / 2
        h = height / 2
        d = depth / 2
        
        # Calculate repetitions based on size (approx 5 units per repeat)
        rep_x = width / 5.0
        rep_y = height / 5.0
        rep_z = depth / 5.0
        
        # OPTIMIZATION: Assume texture already bound by caller
        # Removed: glEnable(GL_TEXTURE_2D) and glBindTexture() - now done once outside loop
            
        # Modulate texture with color
        glColor4f(1.0, 1.0, 1.0, 1.0) 
        
        glBegin(GL_QUADS)
        
        # Front
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0); glVertex3f(-w, -h, d)
        glTexCoord2f(rep_x, 0); glVertex3f(w, -h, d)
        glTexCoord2f(rep_x, rep_y); glVertex3f(w, h, d)
        glTexCoord2f(0, rep_y); glVertex3f(-w, h, d)
        
        # Back
        glNormal3f(0, 0, -1)
        glTexCoord2f(0, 0); glVertex3f(w, -h, -d)
        glTexCoord2f(rep_x, 0); glVertex3f(-w, -h, -d)
        glTexCoord2f(rep_x, rep_y); glVertex3f(-w, h, -d)
        glTexCoord2f(0, rep_y); glVertex3f(w, h, -d)
        
        # Right
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(w, -h, d)
        glTexCoord2f(rep_z, 0); glVertex3f(w, -h, -d)
        glTexCoord2f(rep_z, rep_y); glVertex3f(w, h, -d)
        glTexCoord2f(0, rep_y); glVertex3f(w, h, d)
        
        # Left
        glNormal3f(-1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(-w, -h, -d)
        glTexCoord2f(rep_z, 0); glVertex3f(-w, -h, d)
        glTexCoord2f(rep_z, rep_y); glVertex3f(-w, h, d)
        glTexCoord2f(0, rep_y); glVertex3f(-w, h, -d)
        
        glEnd()
        
        # Draw Top/Bottom without texture (just dark gray)
        glDisable(GL_TEXTURE_2D)  # Temporarily disable for non-textured surfaces
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_QUADS)
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(-w, h, -d); glVertex3f(-w, h, d)
        glVertex3f(w, h, d); glVertex3f(w, h, -d)
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(-w, -h, -d); glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d); glVertex3f(-w, -h, d)
        glEnd()
        
        # Re-enable texture for next building
        glEnable(GL_TEXTURE_2D)
    
    def draw_building(self, building):
        glPushMatrix()
        glTranslatef(building['x'], building['height']/2, building['z'])
        
        # Use tint color for texture
        glColor4fv(building['color'])
        
        # Use textured cube for building body
        self.draw_textured_cube(building['width'], building['height'], building['depth'])
        
        # Jendela-jendela (sederhana) - Optional now that we have textures, but keeping for extra detail
        # self.draw_windows(building) # Disabling windows to let texture shine and save perf
        
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

    def compile_static_geometry(self):
        """Compile all static building geometry into a GPU display list for performance"""
        if self.city_display_list is not None:
            glDeleteLists(self.city_display_list, 1)
        
        self.city_display_list = glGenLists(1)
        glNewList(self.city_display_list, GL_COMPILE)
        
        # OPTIMIZATION: Set texture state ONCE before recording all buildings
        # This eliminates ~1000+ redundant state changes per frame
        glEnable(GL_TEXTURE_2D)
        if self.texture_id:
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # Record all building drawing commands (texture already bound)
        for building in self.buildings:
            self.draw_building(building)
        
        # Clean up texture state
        glDisable(GL_TEXTURE_2D)
        
        glEndList()
        print(f"   ⚡ GPU display list compiled: {len(self.buildings)} buildings optimized")
        print(f"   🎨 Texture state optimized: 1 bind vs {len(self.buildings)} previous redundant binds")
        
        # Also compile street lights to GPU for performance
        self.compile_street_lights()
    
    def compile_street_lights(self):
        """Compile street lights into a GPU display list for performance"""
        if self.street_lights_display_list is not None:
            glDeleteLists(self.street_lights_display_list, 1)
        
        self.street_lights_display_list = glGenLists(1)
        glNewList(self.street_lights_display_list, GL_COMPILE)
        self.draw_street_lights()
        glEndList()
        print(f"   💡 Street lights compiled to GPU display list")
    
    def render(self):
        """Render all city elements using GPU-accelerated display list"""
        # Draw stars and sky first (background)
        self.draw_sky()
        
        # Draw all buildings using compiled display list (massive performance boost)
        if self.city_display_list is not None:
            glCallList(self.city_display_list)
        else:
            # Fallback to immediate mode if display list not compiled
            for building in self.buildings:
                self.draw_building(building)
        
        # Draw street lights using compiled display list
        if self.street_lights_display_list is not None:
            glCallList(self.street_lights_display_list)
        else:
            # Fallback to immediate mode
            self.draw_street_lights()
    
    def get_buildings_for_collision(self):
        """Return building list for collision detection (compatibility method)"""
        return self.buildings
    
    def cleanup(self):
        """Clean up GPU resources (display lists)"""
        if self.city_display_list is not None:
            glDeleteLists(self.city_display_list, 1)
            self.city_display_list = None
            print("🧹 City display list cleaned up")
        
        if self.street_lights_display_list is not None:
            glDeleteLists(self.street_lights_display_list, 1)
            self.street_lights_display_list = None
            print("💡 Street lights display list cleaned up")

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
        
        # Render Glow Aura (halo)
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE) # Don't write to depth buffer for transparent glow
        
        glColor4f(1.0, 1.0, 0.5, 0.3) # Semi-transparent yellow
        
        # First halo
        self.draw_sphere(1.5)
        
        # Large faint halo
        glColor4f(1.0, 1.0, 0.5, 0.1)
        self.draw_sphere(3.0)
        
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        
        glPopMatrix()
        
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