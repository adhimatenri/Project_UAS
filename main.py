import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
from car import Car
from city import City
from road import Road
from camera import Camera
from PIL import Image

class CitySimulation:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.car = Car()
        self.city = City()
        self.road = Road()
        self.camera = Camera()
        self.textures = {}
        self.light_position = [50.0, 50.0, 50.0, 1.0]
        self.light_color = [1.0, 1.0, 1.0, 1.0]
        self.last_print_time = 0
        self.frame_count = 0
        self.running = True
        
        # Initialize PyGame (tanpa GLFW!)
        pygame.init()
        pygame.display.set_mode(
            (width, height), 
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("3D City Simulation")
        
        # Initialize font untuk info (opsional)
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)
        
        self.init_opengl()
        self.load_textures()
        
        print("\n" + "="*80)
        print("3D CITY SIMULATION - CONTROLS")
        print("="*80)
        print("W/S - Accelerate/Brake")
        print("A/D - Steer Left/Right")
        print("SPACE - Emergency Brake")
        print("1/2/3 - Camera Views (Follow/Top/Free)")
        print("R - Reset Position")
        print("Arrow Keys - Move Camera (Free mode only)")
        print("ESC - Exit")
        print("="*80)
        
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_TEXTURE_2D)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glClearColor(0.53, 0.81, 0.98, 1.0)
    
    def handle_events(self):
        """Handle keyboard events dengan PyGame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_o:
                    self.car.auto_mode = not self.car.auto_mode
                    print(f"Auto mode: {'ON' if self.car.auto_mode else 'OFF'}")
                
                # Kontrol mobil
                elif event.key == pygame.K_w:
                    self.car.move_forward()
                elif event.key == pygame.K_s:
                    self.car.move_backward()
                elif event.key == pygame.K_a:
                    self.car.turn_left()
                elif event.key == pygame.K_d:
                    self.car.turn_right()
                elif event.key == pygame.K_SPACE:
                    self.car.brake()
                elif event.key == pygame.K_r:
                    self.car.reset_position()
                
                # Kontrol kamera
                elif event.key == pygame.K_1:
                    self.camera.set_mode('follow')
                    print("Camera: Follow mode")
                elif event.key == pygame.K_2:
                    self.camera.set_mode('top')
                    print("Camera: Top view mode")
                elif event.key == pygame.K_3:
                    self.camera.set_mode('free')
                    print("Camera: Free mode")
        
        # Handle key holds (untuk arrow keys)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.camera.move_forward()
        if keys[pygame.K_DOWN]:
            self.camera.move_backward()
        if keys[pygame.K_LEFT]:
            self.camera.turn_left()
        if keys[pygame.K_RIGHT]:
            self.camera.turn_right()
    
    def load_textures(self):
        # ... (sama seperti sebelumnya, tanpa perubahan)
        pass
    
    def setup_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width/self.height, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
    
    def setup_lighting(self):
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.light_color)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        self.setup_projection()
        self.setup_lighting()
        
        # Update kamera
        self.camera.update(self.car)
        
        # Terapkan transformasi kamera
        gluLookAt(
            self.camera.x, self.camera.y, self.camera.z,
            self.camera.target_x, self.camera.target_y, self.camera.target_z,
            0, 1, 0
        )
        
        # Gambar scene
        self.draw_grid()
        self.road.render()
        self.city.render()
        
        # Update dan gambar mobil
        self.car.update()
        self.car.render()
        
        # UI informasi
        self.draw_ui()
    
    def draw_grid(self, size=100, step=10):
        glBegin(GL_LINES)
        glColor3f(0.5, 0.5, 0.5)
        for i in range(-size, size+1, step):
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
        glEnd()
    
    def draw_ui(self):
        """Draw UI dengan PyGame font (lebih mudah!)"""
        # Switch ke orthographic
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, -1,0, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Render text dengan PyGame
        info_lines = [
            f"Position: X={self.car.x:.1f}, Z={self.car.z:.1f}",
            f"Speed: {abs(self.car.speed):.1f} km/h",
            f"Camera: {self.camera.mode}",
            "WASD: Drive | 1/2/3: Camera | R: Reset | ESC: Exit"
        ]
        
        for i, line in enumerate(info_lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            
            w, h = text_surface.get_size()
            
            # Buat texture
            tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, 
                        GL_RGBA, GL_UNSIGNED_BYTE, text_data)
            
            # Gambar texture
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(10, 30 + i*25)
            glTexCoord2f(1, 1); glVertex2f(10 + w, 30 + i*25)
            glTexCoord2f(1, 0); glVertex2f(10 + w, 30 + i*25 + h)
            glTexCoord2f(0, 1); glVertex2f(10, 30 + i*25 + h)
            glEnd()
            
            glDisable(GL_BLEND)
            glDisable(GL_TEXTURE_2D)
            glDeleteTextures([tex_id])
        
        # Speed bar (graphics)
        speed_percent = min(abs(self.car.speed) / self.car.max_speed, 1.0)
        bar_width = 200
        bar_height = 20
        
        # Background bar
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(self.width - bar_width - 20, 30)
        glVertex2f(self.width - 20, 30)
        glVertex2f(self.width - 20, 30 + bar_height)
        glVertex2f(self.width - bar_width - 20, 30 + bar_height)
        glEnd()
        
        # Fill bar (green to red)
        r = min(1.0, speed_percent * 2)
        g = min(1.0, 2.0 - speed_percent * 2)
        glColor3f(r, g, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(self.width - bar_width - 20, 30)
        glVertex2f(self.width - bar_width - 20 + bar_width * speed_percent, 30)
        glVertex2f(self.width - bar_width - 20 + bar_width * speed_percent, 30 + bar_height)
        glVertex2f(self.width - bar_width - 20, 30 + bar_height)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update time-based animations
            delta_time = clock.tick(60) / 1000.0  # Convert to seconds
            self.car.update_wheel_rotation(delta_time)
            
            # Print info ke terminal setiap 60 frame
            self.frame_count += 1
            if self.frame_count % 60 == 0:
                print(f"\rCar: X={self.car.x:6.1f}, Z={self.car.z:6.1f}, "
                      f"Speed={self.car.speed:5.1f} km/h", end="")
            
            # Render frame
            self.render()
            
            # Swap buffers
            pygame.display.flip()
        
        pygame.quit()
        print("\n\nSimulation closed.")

if __name__ == "__main__":
    simulation = CitySimulation()
    simulation.run()