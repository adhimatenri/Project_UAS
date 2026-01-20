# road.py - Enhanced Grid-Based Road System
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np

class Road:
    def __init__(self):
        # Optimized 3x3 grid system for better performance
        self.road_width = 15
        self.world_size = 160  # Reduced from 200 for tighter city
        
        # Simplified road network coordinates (3x3 grid)
        self.horizontal_roads = [-30, 0, 30]  # Z-coordinates (3 roads)
        self.vertical_roads = [-30, 0, 30]    # X-coordinates (3 roads)
        
        # City block definitions (4 larger blocks: 50x50 units each)
        self.city_blocks = []
        block_size = 50
        block_positions = [(-15, -15), (15, -15), (-15, 15), (15, 15)]  # Plus pattern centers
        
        for center_x, center_z in block_positions:
            self.city_blocks.append({
                'center_x': center_x,
                'center_z': center_z, 
                'size': block_size
            })
        
        # Performance optimization
        self.road_display_list = None
        self.marking_display_list = None
        
        print(f"🛣️  Optimized road system initialized:")
        print(f"   Grid: 3x3 roads creating 4 large city blocks")
        print(f"   Intersections: 9 (reduced from 25)")
        print(f"   World bounds: ±{self.world_size//2} units")
        print(f"   Performance: 64% fewer intersection calculations")
    
    def get_city_blocks(self):
        """Return city block information for building placement"""
        return self.city_blocks
    
    def is_road_area(self, x, z, buffer=2.0):
        """Check if coordinates are in road area (with buffer for safety)"""
        road_half_width = (self.road_width / 2.0) + buffer
        
        # Check if in any horizontal road
        for road_z in self.horizontal_roads:
            if abs(z - road_z) <= road_half_width:
                return True
        
        # Check if in any vertical road  
        for road_x in self.vertical_roads:
            if abs(x - road_x) <= road_half_width:
                return True
                
        return False
    
    def is_intersection(self, x, z, buffer=5.0):
        """Check if coordinates are at an intersection"""
        near_vertical = any(abs(x - road_x) <= buffer for road_x in self.vertical_roads)
        near_horizontal = any(abs(z - road_z) <= buffer for road_z in self.horizontal_roads)
        return near_vertical and near_horizontal
    
    def get_spawn_position(self):
        """Get a good spawn position in middle of a road segment for 3x3 grid"""
        # Spawn in center road (index 1), between intersections
        spawn_x = self.vertical_roads[1]  # Center vertical road (0)
        spawn_z = (self.horizontal_roads[0] + self.horizontal_roads[1]) / 2  # Between first two roads (-15)
        return spawn_x, 0.3, spawn_z

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
    
    def generate_asphalt_texture(self):
        """Generate procedural noise texture for asphalt"""
        width, height = 128, 128
        texture_data = bytearray()
        
        # Simple noise generation
        import random
        for i in range(width * height):
            # Abu-abu gelap dengan noise
            base = 60
            noise = random.randint(-15, 15)
            c = max(0, min(255, base + noise))
            texture_data.append(c) # R
            texture_data.append(c) # G
            texture_data.append(c) # B
        
        # Create GL Texture
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, 
                     GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        
        return tex_id

    def draw_grid_roads(self):
        """Draw the complete 4x4 road grid with optimized rendering"""
        if not hasattr(self, 'road_texture'):
            self.road_texture = self.generate_asphalt_texture()
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.road_texture)
        glColor3f(1.0, 1.0, 1.0)  # White to show texture properly
        
        # Draw horizontal roads
        for road_z in self.horizontal_roads:
            self.draw_single_road(
                center_x=0, center_z=road_z,
                width=self.world_size, length=self.road_width,
                horizontal=True
            )
        
        # Draw vertical roads  
        for road_x in self.vertical_roads:
            self.draw_single_road(
                center_x=road_x, center_z=0,
                width=self.road_width, length=self.world_size,
                horizontal=False
            )
            
        glDisable(GL_TEXTURE_2D)
    
    def draw_single_road(self, center_x, center_z, width, length, horizontal=True):
        """Draw a single road segment with proper texture mapping"""
        w = width / 2.0
        l = length / 2.0
        
        # Texture repetition based on road dimensions
        if horizontal:
            tex_u = width / 10.0  # Repeat every 10 units
            tex_v = length / 10.0
        else:
            tex_u = width / 10.0
            tex_v = length / 10.0
        
        glPushMatrix()
        glTranslatef(center_x, 0.01, center_z)  # Slight elevation to prevent z-fighting
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0);      glVertex3f(-w, 0, -l)
        glTexCoord2f(tex_u, 0);  glVertex3f(w, 0, -l) 
        glTexCoord2f(tex_u, tex_v); glVertex3f(w, 0, l)
        glTexCoord2f(0, tex_v);     glVertex3f(-w, 0, l)
        glEnd()
        
        glPopMatrix()

    def draw_realistic_lane_markings(self):
        """Draw realistic road markings: yellow center lines, white edges, crosswalks"""
        glDisable(GL_TEXTURE_2D)  # No texture for markings
        glLineWidth(3.0)  # Thicker lines for visibility
        
        # Yellow dashed center lines on all roads
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        self.draw_dashed_center_lines()
        
        # White solid edge lines
        glColor3f(1.0, 1.0, 1.0)  # White
        self.draw_solid_edge_lines()
        
        # Crosswalk markings at intersections
        self.draw_crosswalk_markings()
        
        glLineWidth(1.0)  # Reset line width
    
    def draw_dashed_center_lines(self):
        """Draw yellow dashed center lines on all roads"""
        dash_length = 3.0
        gap_length = 2.0
        total_length = dash_length + gap_length
        
        glBegin(GL_LINES)
        
        # Horizontal road center lines
        for road_z in self.horizontal_roads:
            y = 0.02  # Slightly above road surface
            for x in range(-int(self.world_size//2), int(self.world_size//2), int(total_length)):
                # Only draw if not at intersection
                if not any(abs(x - road_x) <= self.road_width/2 for road_x in self.vertical_roads):
                    glVertex3f(x, y, road_z)
                    glVertex3f(x + dash_length, y, road_z)
        
        # Vertical road center lines
        for road_x in self.vertical_roads:
            y = 0.02
            for z in range(-int(self.world_size//2), int(self.world_size//2), int(total_length)):
                # Only draw if not at intersection
                if not any(abs(z - road_z) <= self.road_width/2 for road_z in self.horizontal_roads):
                    glVertex3f(road_x, y, z)
                    glVertex3f(road_x, y, z + dash_length)
        
        glEnd()
    
    def draw_solid_edge_lines(self):
        """Draw white solid edge lines for all roads"""
        edge_offset = self.road_width / 2.0 - 0.5  # Slightly inside road edge
        y = 0.02
        
        glBegin(GL_LINES)
        
        # Horizontal roads - top and bottom edges
        for road_z in self.horizontal_roads:
            # Top edge
            glVertex3f(-self.world_size//2, y, road_z + edge_offset)
            glVertex3f(self.world_size//2, y, road_z + edge_offset)
            # Bottom edge  
            glVertex3f(-self.world_size//2, y, road_z - edge_offset)
            glVertex3f(self.world_size//2, y, road_z - edge_offset)
        
        # Vertical roads - left and right edges
        for road_x in self.vertical_roads:
            # Right edge
            glVertex3f(road_x + edge_offset, y, -self.world_size//2)
            glVertex3f(road_x + edge_offset, y, self.world_size//2)
            # Left edge
            glVertex3f(road_x - edge_offset, y, -self.world_size//2)
            glVertex3f(road_x - edge_offset, y, self.world_size//2)
        
        glEnd()
    
    def draw_crosswalk_markings(self):
        """Draw zebra crossing markings at intersections"""
        stripe_width = 1.0
        stripe_gap = 0.5
        crosswalk_width = self.road_width - 2.0  # Leave some margin
        y = 0.03  # Above other markings
        
        glColor3f(1.0, 1.0, 1.0)  # White crosswalks
        
        # Draw crosswalks at each intersection
        for road_x in self.vertical_roads:
            for road_z in self.horizontal_roads:
                # Horizontal crosswalk (across vertical road)
                self.draw_single_crosswalk(
                    road_x, road_z, 
                    width=self.road_width, length=crosswalk_width,
                    horizontal=True
                )
                
                # Vertical crosswalk (across horizontal road)  
                self.draw_single_crosswalk(
                    road_x, road_z,
                    width=crosswalk_width, length=self.road_width, 
                    horizontal=False
                )
    
    def draw_single_crosswalk(self, center_x, center_z, width, length, horizontal):
        """Draw a single crosswalk with zebra stripes"""
        stripe_width = 1.0
        stripe_gap = 0.5
        y = 0.03
        
        if horizontal:
            # Stripes run along width (x-direction)
            num_stripes = int(width // (stripe_width + stripe_gap))
            start_x = center_x - (num_stripes * (stripe_width + stripe_gap)) / 2
            
            glBegin(GL_QUADS)
            for i in range(num_stripes):
                x = start_x + i * (stripe_width + stripe_gap)
                glVertex3f(x, y, center_z - length/2)
                glVertex3f(x + stripe_width, y, center_z - length/2)
                glVertex3f(x + stripe_width, y, center_z + length/2)
                glVertex3f(x, y, center_z + length/2)
            glEnd()
        else:
            # Stripes run along length (z-direction)
            num_stripes = int(length // (stripe_width + stripe_gap))
            start_z = center_z - (num_stripes * (stripe_width + stripe_gap)) / 2
            
            glBegin(GL_QUADS)
            for i in range(num_stripes):
                z = start_z + i * (stripe_width + stripe_gap)
                glVertex3f(center_x - width/2, y, z)
                glVertex3f(center_x + width/2, y, z)
                glVertex3f(center_x + width/2, y, z + stripe_width)
                glVertex3f(center_x - width/2, y, z + stripe_width)
            glEnd()

    def render(self):
        """Render the complete road system with markings"""
        # Draw the grid of roads with textures
        self.draw_grid_roads()
        
        # Draw realistic lane markings over the roads
        self.draw_realistic_lane_markings()
        
    def cleanup(self):
        """Clean up OpenGL resources"""
        if hasattr(self, 'road_texture'):
            glDeleteTextures([self.road_texture])
        if hasattr(self, 'road_display_list') and self.road_display_list:
            glDeleteLists(self.road_display_list, 1)
        if hasattr(self, 'marking_display_list') and self.marking_display_list:
            glDeleteLists(self.marking_display_list, 1)
        
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