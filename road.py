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

    def draw_textured_road_surface(self, width, length):
        """Draw surface with texture coordinates"""
        # Repetition factor for texture
        rep_x = width / 5.0
        rep_z = length / 5.0
        
        w = width / 2.0
        l = length / 2.0
        
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(-w, 0, -l)
        glTexCoord2f(0, rep_z); glVertex3f(-w, 0, l)
        glTexCoord2f(rep_x, rep_z); glVertex3f(w, 0, l)
        glTexCoord2f(rep_x, 0); glVertex3f(w, 0, -l)
        glEnd()

    def render(self):
        # Generate texture if it doesn't exist
        if not hasattr(self, 'road_texture'):
            self.road_texture = self.generate_asphalt_texture()
        
        # Jalan utama dengan texture
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.road_texture)
        
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)  # Putih agar warna texture keluar
        glTranslatef(0, 0.01, 0)
        # Kita gambar plane terpisah untuk permukaan jalan yang bertekstur
        self.draw_textured_road_surface(self.road_width, self.road_length)
        glPopMatrix()
        
        glDisable(GL_TEXTURE_2D)
        
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