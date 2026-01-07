# car.py
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class Car:
    def __init__(self):
        self.x = 0.0
        self.y = 0.3
        self.z = 0.0
        self.speed = 1.5  # ⭐ LAMBAT SAJA
        self.max_speed = 30.0
        self.acceleration = 0.3
        self.brake_power = 0.8
        self.steering_angle = 0.0
        self.max_steering = 40.0
        self.direction = 0.0
        self.wheel_rotation = 0.0
        self.wheel_angle = 0.0
        self.auto_mode = True  # Mode otomatis jalan lurus
        
        # Warna sederhana
        self.body_color = [0.2, 0.5, 0.8, 1.0]      # Biru
        self.wheel_color = [0.1, 0.1, 0.1, 1.0]     # Hitam untuk ban
        self.rim_color = [0.7, 0.7, 0.7, 1.0]       # Silver untuk velg
        self.window_color = [0.5, 0.7, 0.9, 0.5]    # Kaca biru transparan
        self.headlight_color = [1.0, 0.9, 0.6, 1.0] # Kuning untuk lampu
        self.taillight_color = [0.9, 0.1, 0.1, 1.0] # Merah untuk lampu belakang
    
    def toggle_auto_mode(self):
        """Toggle mode otomatis"""
        self.auto_mode = not self.auto_mode
        print(f"Auto mode: {'ON' if self.auto_mode else 'OFF'}")
    
    def move_forward(self):
        if not self.auto_mode:  # Hanya jika manual mode
            self.speed = min(self.speed + self.acceleration, self.max_speed)
    
    def move_backward(self):
        if not self.auto_mode:
            self.speed = max(self.speed - self.acceleration, -self.max_speed/3)
    
    def turn_left(self):
        self.steering_angle = min(self.steering_angle + 2.0, self.max_steering)
        self.wheel_angle = self.steering_angle
    
    def turn_right(self):
        self.steering_angle = max(self.steering_angle - 2.0, -self.max_steering)
        self.wheel_angle = self.steering_angle
    
    def brake(self):
        if self.speed > 0:
            self.speed = max(self.speed - self.brake_power, 0)
        elif self.speed < 0:
            self.speed = min(self.speed + self.brake_power, 0)
    
    def reset_position(self):
        self.x = 0.0
        self.z = 0.0
        self.speed = 1.5
        self.direction = 0.0
        self.steering_angle = 0.0
    
    def update(self):
        # ⭐ AUTO MODE: Jalan lurus pelan-pelan
        if self.auto_mode:
            if self.speed < 8.0:  # ⭐ KECEPATAN SANGAT LAMBAT
                self.speed = min(self.speed + 0.05, 8.0)
        
        # Update posisi
        if abs(self.speed) > 0.05:
            dir_rad = np.radians(self.direction)
            self.x += self.speed * np.sin(dir_rad) * 0.1
            self.z += self.speed * np.cos(dir_rad) * 0.1
            
            # Update arah berdasarkan steering
            if abs(self.steering_angle) > 1.0:
                turn_factor = self.speed * 0.015  # ⭐ BELOK PELAN
                self.direction += self.steering_angle * turn_factor
                self.direction %= 360
        
        # Steering slowly returns to center
        if abs(self.steering_angle) > 0.5:
            self.steering_angle *= 0.9
        else:
            self.steering_angle = 0.0
        
        # Natural deceleration
        if abs(self.speed) > 0.1:
            self.speed *= 0.98
        elif not self.auto_mode:
            self.speed = 0.0
    
    def update_wheel_rotation(self, delta_time):
        # Animasi putaran roda yang realistis
        wheel_radius = 0.35  # Radius roda
        wheel_circumference = 2.0 * np.pi * wheel_radius
        distance_per_second = self.speed * 0.2778  # km/h to m/s
        rotation_per_second = distance_per_second / wheel_circumference
        self.wheel_rotation += rotation_per_second * 360 * delta_time
    
    # ==================== FUNGSI BANTUAN ====================
    
    def draw_rect(self, width, height, depth):
        """Draw persegi panjang sederhana"""
        w = width / 2.0
        h = height / 2.0
        d = depth / 2.0
        
        glBegin(GL_QUADS)
        # Front
        glVertex3f(-w, -h, d); glVertex3f(w, -h, d)
        glVertex3f(w, h, d); glVertex3f(-w, h, d)
        # Back
        glVertex3f(-w, -h, -d); glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d); glVertex3f(w, -h, -d)
        # Top
        glVertex3f(-w, h, -d); glVertex3f(-w, h, d)
        glVertex3f(w, h, d); glVertex3f(w, h, -d)
        # Bottom
        glVertex3f(-w, -h, -d); glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d); glVertex3f(-w, -h, d)
        # Right
        glVertex3f(w, -h, -d); glVertex3f(w, h, -d)
        glVertex3f(w, h, d); glVertex3f(w, -h, d)
        # Left
        glVertex3f(-w, -h, -d); glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d); glVertex3f(-w, h, -d)
        glEnd()
    
    def draw_wheel(self, x_offset, z_offset, is_front=True):
        """Draw roda yang proper dengan ban dan velg"""
        glPushMatrix()
        glTranslatef(x_offset, 0.3, z_offset)
        
        # Roda depan bisa berbelok
        if is_front:
            glRotatef(self.wheel_angle, 0, 1, 0)
        
        # Putaran roda (mengelilingi sumbu X)
        glRotatef(self.wheel_rotation, 1, 0, 0)
        
        # ===== BAN =====
        glColor4fv(self.wheel_color)  # Hitam
        self.draw_cylinder(0.35, 0.22, 24)  # Radius 0.35, tebal 0.22
        
        # ===== VELG =====
        glPushMatrix()
        glColor4fv(self.rim_color)  # Silver
        
        # Velg sebagai disk
        self.draw_disk(0.25, 0.05, 16)
        
        # Center hub (tutup tengah)
        glColor3f(0.4, 0.4, 0.4)
        self.draw_disk(0.08, 0.06, 8)
        
        glPopMatrix()
        glPopMatrix()
    
    def draw_cylinder(self, radius, height, segments=16):
        """Draw cylinder untuk ban"""
        # Sisi samping
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            glNormal3f(np.cos(angle), np.sin(angle), 0)
            glVertex3f(x, y, height/2)
            glVertex3f(x, y, -height/2)
        glEnd()
        
        # Tutup atas
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, height/2)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            glVertex3f(radius * np.cos(angle), radius * np.sin(angle), height/2)
        glEnd()
        
        # Tutup bawah
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -height/2)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            glVertex3f(radius * np.cos(angle), radius * np.sin(angle), -height/2)
        glEnd()
    
    def draw_disk(self, radius, thickness, segments=16):
        """Draw disk pipih untuk velg"""
        # Atas
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, thickness/2)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            glVertex3f(radius * np.cos(angle), radius * np.sin(angle), thickness/2)
        glEnd()
        
        # Bawah
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -thickness/2)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            glVertex3f(radius * np.cos(angle), radius * np.sin(angle), -thickness/2)
        glEnd()
        
        # Sisi samping
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            glVertex3f(x, y, thickness/2)
            glVertex3f(x, y, -thickness/2)
        glEnd()
    
    # ==================== RENDER MOBIL ====================
    
    def render(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.direction, 0, 1, 0)
        
        # ===== BODY UTAMA =====
        glColor4fv(self.body_color)
        
        # Body bawah (chassis)
        glPushMatrix()
        glTranslatef(0, 0.25, 0)
        glScalef(1.6, 0.3, 3.2)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Body atas
        glPushMatrix()
        glTranslatef(0, 0.7, 0)
        glScalef(1.4, 0.45, 2.4)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Atap
        glPushMatrix()
        glTranslatef(0, 1.05, 0)
        glScalef(1.2, 0.1, 1.8)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # ===== PINTU 4 =====
        # Garis pintu depan
        glColor3f(0.15, 0.15, 0.15)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # Garis vertikal antara pintu depan dan belakang
        glVertex3f(0.7, 0.5, 0.3)
        glVertex3f(0.7, 0.9, 0.3)
        glVertex3f(-0.7, 0.5, 0.3)
        glVertex3f(-0.7, 0.9, 0.3)
        # Handle pintu
        glVertex3f(0.72, 0.65, 0.5)
        glVertex3f(0.72, 0.65, 0.6)
        glVertex3f(-0.72, 0.65, 0.5)
        glVertex3f(-0.72, 0.65, 0.6)
        glEnd()
        glLineWidth(1.0)
        
        # ===== KACA =====
        glColor4fv(self.window_color)
        
        # Kaca depan
        glPushMatrix()
        glTranslatef(0, 0.95, 0.8)
        glScalef(1.2, 0.25, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Kaca belakang
        glPushMatrix()
        glTranslatef(0, 0.95, -0.8)
        glScalef(1.2, 0.25, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Kaca samping kiri
        glPushMatrix()
        glTranslatef(0.7, 0.95, 0)
        glScalef(0.05, 0.25, 1.0)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Kaca samping kanan
        glPushMatrix()
        glTranslatef(-0.7, 0.95, 0)
        glScalef(0.05, 0.25, 1.0)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # ===== DETAIL =====
        
        # Grill depan
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 0.5, 1.45)
        glScalef(0.7, 0.15, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Bemper depan
        glPushMatrix()
        glTranslatef(0, 0.3, 1.5)
        glScalef(1.4, 0.1, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Bemper belakang
        glPushMatrix()
        glTranslatef(0, 0.3, -1.5)
        glScalef(1.4, 0.1, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # ===== LAMPU =====
        
        # Lampu depan kiri
        glColor4fv(self.headlight_color)
        glPushMatrix()
        glTranslatef(0.45, 0.5, 1.48)
        glScalef(0.12, 0.12, 0.1)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Lampu depan kanan
        glPushMatrix()
        glTranslatef(-0.45, 0.5, 1.48)
        glScalef(0.12, 0.12, 0.1)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Lampu belakang kiri
        glColor4fv(self.taillight_color)
        glPushMatrix()
        glTranslatef(0.4, 0.5, -1.48)
        glScalef(0.1, 0.18, 0.1)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Lampu belakang kanan
        glPushMatrix()
        glTranslatef(-0.4, 0.5, -1.48)
        glScalef(0.1, 0.18, 0.1)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # ===== RODA 4 =====
        
        # Roda depan kiri
        self.draw_wheel(0.75, 0.9, is_front=True)
        
        # Roda depan kanan
        self.draw_wheel(-0.75, 0.9, is_front=True)
        
        # Roda belakang kiri
        self.draw_wheel(0.75, -0.9, is_front=False)
        
        # Roda belakang kanan
        self.draw_wheel(-0.75, -0.9, is_front=False)
        
        # ===== SPION =====
        
        # Spion kiri
        glColor4fv(self.body_color)
        glPushMatrix()
        glTranslatef(0.85, 0.95, 0.4)
        glScalef(0.06, 0.1, 0.12)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Spion kanan
        glPushMatrix()
        glTranslatef(-0.85, 0.95, 0.4)
        glScalef(0.06, 0.1, 0.12)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # Kaca spion
        glColor3f(0.8, 0.85, 0.9)
        glPushMatrix()
        glTranslatef(0.88, 0.95, 0.4)
        glScalef(0.02, 0.08, 0.08)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.88, 0.95, 0.4)
        glScalef(0.02, 0.08, 0.08)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        # ===== PLAT NOMOR =====
        
        # Plat belakang
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(0, 0.4, -1.52)
        glScalef(0.25, 0.09, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0, 0.4, -1.51)
        glScalef(0.23, 0.07, 0.05)
        self.draw_rect(1, 1, 1)
        glPopMatrix()
        
        glPopMatrix()  # End of car transformation