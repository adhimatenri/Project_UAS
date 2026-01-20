# car.py - VERSI DENGAN FISIKA LEBIH BAIK
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

class Car:
    def __init__(self):
        # Default spawn position (will be updated by road system)
        self.x = 15.0  # Middle vertical road
        self.y = 0.3
        self.z = -30.0  # Between first two horizontal roads
        self.speed = 0.0  # Start stationary
        self.max_speed = 50.0
        self.acceleration = 2.5  # Enhanced for intersection navigation
        self.brake_power = 4.0  # Stronger braking
        self.steering_angle = 0.0
        self.max_steering = 55.0  # Increased for sharper turns
        self.direction = 0.0  # Car direction (degrees)
        self.wheel_rotation = 0.0
        self.wheel_angle = 0.0  # Front wheel angle
        self.auto_mode = False  # Manual mode
        
        # City boundaries (optimized for 3x3 grid)
        self.world_bounds = 75.0  # Reduced from 95 to 75 units
        self.road_system = None  # Reference to road system
        
        # Warna
        self.body_color = [0.2, 0.5, 0.8, 1.0]
        self.wheel_color = [0.1, 0.1, 0.1, 1.0]
        self.rim_color = [0.7, 0.7, 0.7, 1.0]
        self.window_color = [0.5, 0.7, 0.9, 0.5]
        self.headlight_color = [1.0, 0.9, 0.6, 1.0]
        self.taillight_color = [0.9, 0.1, 0.1, 1.0]
    
    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        print(f"Auto mode: {'ON' if self.auto_mode else 'OFF'}")
    
    def move_forward(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)
    
    def move_backward(self):
        self.speed = max(self.speed - self.acceleration, -self.max_speed/2)
    
    def turn_left(self):
        # Enhanced steering responsiveness for intersections
        turn_rate = 4.0 if abs(self.speed) > 10 else 6.0  # Faster turning at low speeds
        self.steering_angle = min(self.steering_angle + turn_rate, self.max_steering)
        self.wheel_angle = self.steering_angle
    
    def turn_right(self):
        # Enhanced steering responsiveness for intersections  
        turn_rate = 4.0 if abs(self.speed) > 10 else 6.0  # Faster turning at low speeds
        self.steering_angle = max(self.steering_angle - turn_rate, -self.max_steering)
        self.wheel_angle = self.steering_angle
    
    def brake(self):
        if self.speed > 0:
            self.speed = max(self.speed - self.brake_power, 0)
        elif self.speed < 0:
            self.speed = min(self.speed + self.brake_power, 0)
    
    def reset_position(self):
        # Reset to proper spawn position in road grid
        if self.road_system:
            spawn_x, spawn_y, spawn_z = self.road_system.get_spawn_position()
            self.x = spawn_x
            self.y = spawn_y 
            self.z = spawn_z
        else:
            # Fallback to grid-compatible position
            self.x = 15.0  # Middle vertical road
            self.y = 0.3
            self.z = -30.0  # Between roads
        
        self.speed = 0.0
        self.direction = 0.0
        self.steering_angle = 0.0
        self.wheel_angle = 0.0
        print(f"🚗 Car reset to position: ({self.x:.1f}, {self.z:.1f}) in 3x3 grid")
    
    def set_road_system(self, road_system):
        """Set reference to road system for boundaries and spawn position"""
        self.road_system = road_system
        # Update spawn position
        if road_system:
            spawn_x, spawn_y, spawn_z = road_system.get_spawn_position()
            self.x = spawn_x
            self.y = spawn_y
            self.z = spawn_z
            print(f"🚗 Car spawn position set to: ({self.x:.1f}, {self.z:.1f})")
    
    def check_city_boundaries(self, new_x, new_z):
        """Check if position is within city boundaries"""
        return (abs(new_x) <= self.world_bounds and abs(new_z) <= self.world_bounds)
    
    def is_on_road(self, x, z):
        """Check if position is on a road (for better navigation feedback)"""
        if not self.road_system:
            return True  # Assume on road if no road system
        return self.road_system.is_road_area(x, z, buffer=0.5)
    
    def check_collision(self, new_x, new_z, buildings):
        """Simple collision detection - returns True if collision"""
        car_radius = 1.0  # Ukuran setengah body mobil
        
        for b in buildings:
            # Building bounds
            min_x = b['x'] - b['width']/2 - car_radius
            max_x = b['x'] + b['width']/2 + car_radius
            min_z = b['z'] - b['depth']/2 - car_radius
            max_z = b['z'] + b['depth']/2 + car_radius
            
            if min_x < new_x < max_x and min_z < new_z < max_z:
                return True
        return False
        """Simple collision detection - returns True if collision"""
        car_radius = 1.0  # Ukuran setengah body mobil
        
        for b in buildings:
            # Building bounds
            min_x = b['x'] - b['width']/2 - car_radius
            max_x = b['x'] + b['width']/2 + car_radius
            min_z = b['z'] - b['depth']/2 - car_radius
            max_z = b['z'] + b['depth']/2 + car_radius
            
            if min_x < new_x < max_x and min_z < new_z < max_z:
                return True
        return False
        
    def update(self, buildings=None):
        # OPTIMIZED PHYSICS FOR 3x3 GRID NAVIGATION
        if abs(self.speed) > 0.01:
            # Calculate movement
            dir_rad = np.radians(self.direction)
            move_factor = 0.08
            
            dx = self.speed * np.sin(dir_rad) * move_factor
            dz = self.speed * np.cos(dir_rad) * move_factor
            
            new_x = self.x + dx
            new_z = self.z + dz
            
            # Check city boundaries first (tighter bounds for 3x3 grid)
            if not self.check_city_boundaries(new_x, new_z):
                # Hit city boundary - stop and bounce back
                self.speed = -self.speed * 0.15  # Gentler bounce
                return
            
            # Optimized building collision (fewer buildings to check)
            collision = False
            if buildings:
                if self.check_collision(new_x, new_z, buildings):
                    collision = True
                    self.speed = -self.speed * 0.25  # Smoother collision response
            
            if not collision:
                self.x = new_x
                self.z = new_z
            
            # OPTIMIZED TURNING PHYSICS
            if abs(self.steering_angle) > 0.5:
                # Tuned for 3x3 grid intersections
                base_turn_speed = 1.0  # Slightly reduced for better control
                speed_factor = min(abs(self.speed) / 20.0, 1.0)
                turn_speed = base_turn_speed * (0.4 + 0.6 * speed_factor)
                
                if self.speed > 0:  # Forward
                    self.direction += self.steering_angle * turn_speed
                else:  # Reverse
                    self.direction -= self.steering_angle * turn_speed
                
                self.direction %= 360
        
        # Faster steering return for better responsiveness
        self.steering_angle *= 0.85
        if abs(self.steering_angle) < 0.8:
            self.steering_angle = 0.0
            self.wheel_angle = 0.0
        
        # Natural deceleration
        if abs(self.speed) > 0.05:
            self.speed *= 0.988
    
    def update_wheel_rotation(self, delta_time):
        """Animasi putaran roda"""
        if delta_time > 0 and abs(self.speed) > 0.1:
            # Formula sederhana: 10 km/h = 1 rotasi per detik
            rotation_speed = self.speed * 36.0 * delta_time
            
            if self.speed > 0:
                self.wheel_rotation += rotation_speed
            elif self.speed < 0:
                self.wheel_rotation -= rotation_speed
            
            self.wheel_rotation %= 360.0
    
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
        """Draw roda"""
        glPushMatrix()
        glTranslatef(x_offset, 0.3, z_offset)
        
        # Roda depan bisa berbelok
        if is_front:
            glRotatef(self.wheel_angle, 0, 1, 0)
      
        # Mobil menghadap ke arah Z+, roda perlu menghadap ke samping (sumbu X)
        glRotatef(90, 0, 1, 0)  # Putar 90 derajat

        # Rotasi roda mengelilingi sumbu Z (yang sekarang menjadi sumbu depan roda)
        glRotatef(self.wheel_rotation, 0, 0, 1)

        # ===== BAN =====
        glColor4fv(self.wheel_color)
        self.draw_cylinder_for_wheel(0.35, 0.22, 24)
        
        # ===== VELG =====
        glPushMatrix()
        glColor4fv(self.rim_color)
        
        # Velg depan
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, 0.12)
        for i in range(25):
            angle = 2.0 * np.pi * i / 24
            x = 0.25 * np.cos(angle)
            y = 0.25 * np.sin(angle)
            glVertex3f(x, y, 0.12)
        glEnd()
        
        # Velg belakang
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -0.12)
        for i in range(25):
            angle = 2.0 * np.pi * i / 24
            x = 0.25 * np.cos(angle)
            y = 0.25 * np.sin(angle)
            glVertex3f(x, y, -0.12)
        glEnd()
        
        # Pusat velg
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, 0.125)
        for i in range(17):
            angle = 2.0 * np.pi * i / 16
            x = 0.08 * np.cos(angle)
            y = 0.08 * np.sin(angle)
            glVertex3f(x, y, 0.125)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -0.125)
        for i in range(17):
            angle = 2.0 * np.pi * i / 16
            x = 0.08 * np.cos(angle)
            y = 0.08 * np.sin(angle)
            glVertex3f(x, y, -0.125)
        glEnd()
        
        glPopMatrix()
        glPopMatrix()
    
    def draw_cylinder_for_wheel(self, radius, height, segments=16):
        """Draw cylinder khusus untuk roda"""
        half_height = height / 2.0
        
        # Sisi samping
        glBegin(GL_QUAD_STRIP)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            glNormal3f(np.cos(angle), np.sin(angle), 0)
            glVertex3f(x, y, half_height)
            glVertex3f(x, y, -half_height)
        glEnd()
        
        # Tutup depan (luar)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, 1)
        glVertex3f(0, 0, half_height)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            glVertex3f(x, y, half_height)
        glEnd()
        
        # Tutup belakang (dalam)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0, -1)
        glVertex3f(0, 0, -half_height)
        for i in range(segments + 1):
            angle = 2.0 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            glVertex3f(x, y, -half_height)
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
        # Headlight glow
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.8, 0.8, 0.6, 1.0])
        self.draw_rect(1, 1, 1)
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()
        
        # Lampu depan kanan
        glPushMatrix()
        glTranslatef(-0.45, 0.5, 1.48)
        glScalef(0.12, 0.12, 0.1)
        # Headlight glow
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.8, 0.8, 0.6, 1.0])
        self.draw_rect(1, 1, 1)
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()
        
        # Lampu belakang kiri
        glColor4fv(self.taillight_color)
        glPushMatrix()
        glTranslatef(0.4, 0.5, -1.48)
        glScalef(0.1, 0.18, 0.1)
        # Taillight glow
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.8, 0.0, 0.0, 1.0])
        self.draw_rect(1, 1, 1)
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()
        
        # Lampu belakang kanan
        glPushMatrix()
        glTranslatef(-0.4, 0.5, -1.48)
        glScalef(0.1, 0.18, 0.1)
        # Taillight glow
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.8, 0.0, 0.0, 1.0])
        self.draw_rect(1, 1, 1)
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
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