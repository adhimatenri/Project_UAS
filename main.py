# main.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from car import Car
from city import City
from road import Road
from camera import Camera
from weather import WeatherSystem

class CitySimulation:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        
        # Initialize systems in correct order
        self.road = Road()  # Road system first
        self.car = Car()    # Car second
        self.city = City()  # City last
        self.camera = Camera()
        self.weather = WeatherSystem()  # Weather system for atmosphere
        
        # Link systems together for proper integration
        self.car.set_road_system(self.road)
        self.city.set_road_system(self.road)
        
        self.light_position = [50.0, 50.0, 50.0, 1.0]
        self.light_color = [1.0, 1.0, 1.0, 1.0]
        self.frame_count = 0
        self.running = True
        
        # Simple FPS tracking
        self.current_fps = 60.0
        
        # UI text texture cache for performance optimization
        self.text_texture_cache = {}
        self.cached_fps = 0
        self.cached_speed = 0
        self.cached_position = (0, 0)
        self.cached_camera_info = ""
        
        # Initialize PyGame
        pygame.init()
        pygame.display.set_mode(
            (width, height), 
            pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Simulasi Kota 3D - Kelompok 7")
        
        # Initialize font untuk info
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 20)
        
        self.init_opengl()
        
    def get_or_create_text_texture(self, cache_key, text, color=(255, 255, 255)):
        """Get cached texture or create new one if text changed - Performance optimization"""
        if cache_key in self.text_texture_cache:
            cached_tex_id, cached_text = self.text_texture_cache[cache_key]
            if cached_text == text:
                return cached_tex_id
            else:
                # Text changed, delete old texture
                glDeleteTextures([cached_tex_id])
        
        # Create new texture
        text_surface = self.font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        w, h = text_surface.get_size()
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        self.text_texture_cache[cache_key] = (tex_id, text)
        return tex_id
        
        print("\n" + "="*80)
        print("3D CITY SIMULATION - ENHANCED MAZE CITY")
        print("="*80)
        print("🚗 ENHANCED CAR CONTROLS:")
        print("W/S - Gas/Rem (Improved acceleration)")
        print("A/D - Belok Kiri/Kanan (Enhanced steering)")
        print("SPACE - Rem Darurat")
        print("R - Reset Posisi (Smart spawn)")
        print("")
        print("📷 CAMERA CONTROLS:")
        print("1 - Follow (Behind car)")
        print("2 - Orbital (Mouse-controlled rotation)")
        print("3 - Top (Bird's eye view)")
        print("4 - Free (Arrow keys control)")
        print("5 - Side (Lateral view)")
        print("Mouse: Drag to rotate, Wheel to zoom (Orbital mode)")
        print("Panah Atas/Bawah - Naik/Turun Kamera (Free mode)")
        print("Panah Kiri/Kanan - Putar Kamera (Free mode)")
        print("PageUp/PageDown - Zoom In/Out (Free mode)")
        print("")
        print("ESC - Keluar")
        print("="*80)
        
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        # Night Mode Background
        glClearColor(0.05, 0.05, 0.2, 1.0)  # Warna langit malam (biru gelap)
        
        # Enable fog for atmospheric effect
        # Enable fog for atmospheric effect
        self.weather.enable_fog()
        
        # Initialize City GL resources (Texture, etc)
        self.city.setup_gl_resources()
    

    
    def draw_fps_display(self):
        """Draw real-time FPS counter with color coding"""
        # Determine FPS color based on performance
        if self.current_fps >= 55:
            fps_color = (0, 255, 0)      # Green - Good performance
        elif self.current_fps >= 45:
            fps_color = (255, 255, 0)    # Yellow - Acceptable
        else:
            fps_color = (255, 0, 0)      # Red - Poor performance
        
        # Format FPS text
        fps_text = f"FPS: {self.current_fps:.1f}"
        fps_surface = self.font.render(fps_text, True, fps_color)
        fps_data = pygame.image.tostring(fps_surface, "RGBA", True)
        fps_w, fps_h = fps_surface.get_size()
        
        # Position in top-right corner
        fps_x = self.width - fps_w - 20
        fps_y = 20
        
        # Create and bind texture
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, fps_w, fps_h, 0, 
                    GL_RGBA, GL_UNSIGNED_BYTE, fps_data)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(fps_x, fps_y)
        glTexCoord2f(1, 1); glVertex2f(fps_x + fps_w, fps_y)
        glTexCoord2f(1, 0); glVertex2f(fps_x + fps_w, fps_y + fps_h)
        glTexCoord2f(0, 0); glVertex2f(fps_x, fps_y + fps_h)
        glEnd()
        
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([tex_id])

    def handle_events(self):
        """Handle keyboard and mouse events dengan PyGame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Mouse events for orbital camera
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.camera.start_mouse_drag(mouse_x, mouse_y)
            
            elif event.type == pygame.MOUSEMOTION:
                if self.camera.mode == 'orbital':
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.camera.update_mouse_drag(mouse_x, mouse_y)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.camera.end_mouse_drag()
            
            elif event.type == pygame.MOUSEWHEEL:
                if self.camera.mode == 'orbital':
                    self.camera.mouse_wheel_zoom(event.y)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_o:
                    self.car.toggle_auto_mode()
                
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
                
                # Kontrol kamera (updated order)
                elif event.key == pygame.K_1:
                    self.camera.set_mode('follow')
                elif event.key == pygame.K_2:
                    self.camera.set_mode('orbital')
                elif event.key == pygame.K_3:
                    self.camera.set_mode('top')
                elif event.key == pygame.K_4:
                    self.camera.set_mode('free')
                elif event.key == pygame.K_5:
                    self.camera.set_mode('side')
                
                # Kontrol zoom (free mode only)
                elif event.key == pygame.K_PAGEUP:
                    self.camera.zoom_in()
                elif event.key == pygame.K_PAGEDOWN:
                    self.camera.zoom_out()
        
        # Handle key holds (untuk arrow keys di free mode)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.camera.move_forward()
        if keys[pygame.K_DOWN]:
            self.camera.move_backward()
        if keys[pygame.K_LEFT]:
            self.camera.turn_left()
        if keys[pygame.K_RIGHT]:
            self.camera.turn_right()
    
    def setup_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width/self.height, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
    
    def setup_lighting(self):
        # Moonlight (Bluish, lower intensity)
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.4, 0.4, 0.7, 1.0]) # Cahaya bulan kebiruan
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0]) # Ambient gelap
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
    
    def update_dynamic_lighting(self):
        """Dynamic lighting manager: Activates street lights closest to car"""
        # Collect all street light positions (based on road grid known in City/Road)
        # Replicating logic from City.draw_street_lights for efficiency
        light_candidates = []
        
        # Horizontal roads: z = -30, 0, 30
        for road_z in [-30, 0, 30]:
            for x in range(-100, 101, 25): # Loop range matching city.py
                # Skip intersection areas (approximate)
                if not any(abs(x - rx) <= 10 for rx in [-30, 0, 30]):
                    light_candidates.append([x, 4.0, road_z - 8])
                    light_candidates.append([x, 4.0, road_z + 8])
                    
        # Vertical roads: x = -30, 0, 30
        for road_x in [-30, 0, 30]:
            for z in range(-80, 81, 25):
                if not any(abs(z - rz) <= 10 for rz in [-30, 0, 30]):
                    light_candidates.append([road_x - 8, 4.0, z])
                    light_candidates.append([road_x + 8, 4.0, z])
        
        # Sort by distance to car
        car_pos = np.array([self.car.x, self.car.y, self.car.z])
        
        # Calculate squared distances for speed
        def dist_sq(pos):
            return (pos[0]-car_pos[0])**2 + (pos[2]-car_pos[2])**2
            
        light_candidates.sort(key=dist_sq)
        
        # Use up to 6 closest lights (GL_LIGHT1 to GL_LIGHT6)
        max_lights = 6
        active_lights = light_candidates[:max_lights]
        
        for i in range(max_lights):
            light_id = GL_LIGHT1 + i
            if i < len(active_lights):
                pos = active_lights[i]
                glEnable(light_id)
                
                # Position (w=1 for point light)
                glLightfv(light_id, GL_POSITION, [pos[0], pos[1], pos[2], 1.0])
                
                # Yellowish street light color
                glLightfv(light_id, GL_DIFFUSE, [1.0, 0.8, 0.4, 1.0])
                glLightfv(light_id, GL_SPECULAR, [1.0, 0.8, 0.4, 1.0])
                
                # Attenuation (falloff) - distinct pools of light
                glLightf(light_id, GL_CONSTANT_ATTENUATION, 0.1)
                glLightf(light_id, GL_LINEAR_ATTENUATION, 0.1)
                glLightf(light_id, GL_QUADRATIC_ATTENUATION, 0.02)
            else:
                glDisable(light_id)
    
    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        self.setup_projection()
        self.setup_lighting()
        self.update_dynamic_lighting()
        
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
        
        # Update dan gambar mobil - PASS BUILDINGS FOR COLLISION
        self.car.update(self.city.get_buildings_for_collision())
        self.car.render()
        
        # Update and render weather (snowfall particles)
        self.weather.update(self.camera)
        self.weather.render()
        
        # UI informasi
        self.draw_ui()
        
        # Debug info di terminal
        if self.frame_count % 180 == 0:  # Setiap 3 detik
            self.print_debug_info()
    
    def draw_grid(self, size=100, step=10):
        """Draw grid untuk membantu visualisasi 3D"""
        glBegin(GL_LINES)
        glColor3f(0.5, 0.5, 0.5)
        for i in range(-size, size+1, step):
            # Garis sejajar sumbu X
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            # Garis sejajar sumbu Z
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
        glEnd()
    
    def draw_ui(self):
        """Draw UI with optimized text caching - reduces texture operations from 10-12 to 1-2 per frame"""
        # Switch ke orthographic projection untuk 2D UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Build dynamic text only when values change significantly
        # FPS - update if changed by ≥0.5
        fps_text = f"FPS: {self.current_fps:.1f}"
        if abs(self.current_fps - self.cached_fps) >= 0.5:
            self.cached_fps = self.current_fps
        else:
            fps_text = f"FPS: {self.cached_fps:.1f}"
        
        # Position - update if changed by ≥5 units
        pos_x, pos_z = self.car.x, self.car.z
        if abs(pos_x - self.cached_position[0]) >= 5 or abs(pos_z - self.cached_position[1]) >= 5:
            self.cached_position = (pos_x, pos_z)
        pos_text = f"Posisi: X={self.cached_position[0]:6.1f}, Z={self.cached_position[1]:6.1f}"
        
        # Speed - update if changed by ≥1.0
        speed = abs(self.car.speed)
        if abs(speed - self.cached_speed) >= 1.0:
            self.cached_speed = speed
        speed_text = f"Kecepatan: {self.cached_speed:5.1f} km/h"
        
        # Camera info
        camera_info = ""
        if self.camera.mode == 'orbital':
            camera_info = (f"Orbital Cam: Angle={self.camera.orbital_angle:.1f}°, "
                          f"Pitch={self.camera.orbital_pitch:.1f}°, "
                          f"Distance={self.camera.orbital_distance:.1f}")
        elif self.camera.mode == 'free':
            camera_info = f"Free Cam: Sudut={self.camera.free_camera_angle:.1f}°, Tinggi={self.camera.free_camera_height:.1f}"
        
        # Build info lines - static lines are cached, dynamic updated only when changed
        info_lines = [
            (f"fps_{self.cached_fps:.1f}", fps_text),
            (f"pos_{self.cached_position[0]:.0f}_{self.cached_position[1]:.0f}", pos_text),
            (f"speed_{self.cached_speed:.0f}", speed_text),
            (f"cam_{self.camera.mode}", f"Kamera: {self.camera.mode.upper()}"),
            (f"dir_{self.car.direction:.0f}", f"Arah: {self.car.direction:.1f}°"),
            ("buildings_static", f"Grid Road System - {len(self.city.buildings)} Buildings"),
            ("controls_static", "WASD: Mengemudi | 1/2/3/4/5: Kamera | R: Reset | ESC: Keluar")
        ]
        
        # Add navigation help if off road
        if not self.car.is_on_road(self.car.x, self.car.z):
            info_lines.append(("offroad_warning", "⚠️ OFF ROAD - Return to road!"))
        
        # Show mode-specific camera info
        if camera_info:
            info_lines.append((f"cam_info_{self.camera.mode}", camera_info))
            if self.camera.mode == 'orbital':
                info_lines.append(("mouse_help_static", "Mouse: Drag to rotate | Wheel to zoom"))
            
        # Render cached textures
        for i, (cache_key, line_text) in enumerate(info_lines):
            tex_id = self.get_or_create_text_texture(cache_key, line_text)
            
            # Get text dimensions from font (lightweight, no texture creation)
            text_surface = self.font.render(line_text, True, (255, 255, 255))
            w, h = text_surface.get_size()
            
            # Bind cached texture
            glBindTexture(GL_TEXTURE_2D, tex_id)
            
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(10, 10 + i*25)
            glTexCoord2f(1, 1); glVertex2f(10 + w, 10 + i*25)
            glTexCoord2f(1, 0); glVertex2f(10 + w, 10 + i*25 + h)
            glTexCoord2f(0, 0); glVertex2f(10, 10 + i*25 + h)
            glEnd()
            
            glDisable(GL_BLEND)
            glDisable(GL_TEXTURE_2D)
            
            # Note: Texture NOT deleted here - it's cached for reuse!
        
        # Speed bar (progress bar visual)
        speed_percent = min(abs(self.car.speed) / self.car.max_speed, 1.0)
        bar_width = 200
        bar_height = 15
        
        # Background bar (abu-abu)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(self.width - bar_width - 20, 30)
        glVertex2f(self.width - 20, 30)
        glVertex2f(self.width - 20, 30 + bar_height)
        glVertex2f(self.width - bar_width - 20, 30 + bar_height)
        glEnd()
        
        # Fill bar (hijau ke merah berdasarkan kecepatan)
        r = min(1.0, speed_percent * 2)
        g = min(1.0, 2.0 - speed_percent * 2)
        glColor3f(r, g, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(self.width - bar_width - 20, 30)
        glVertex2f(self.width - bar_width - 20 + bar_width * speed_percent, 30)
        glVertex2f(self.width - bar_width - 20 + bar_width * speed_percent, 30 + bar_height)
        glVertex2f(self.width - bar_width - 20, 30 + bar_height)
        glEnd()
        
        # Speed text di samping bar
        speed_text = f"{abs(self.car.speed):.1f} km/h"
        speed_surface = self.font.render(speed_text, True, (255, 255, 255))
        speed_data = pygame.image.tostring(speed_surface, "RGBA", True)
        speed_w, speed_h = speed_surface.get_size()
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, speed_w, speed_h, 0, 
                    GL_RGBA, GL_UNSIGNED_BYTE, speed_data)
        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.width - bar_width - 20, 50)
        glTexCoord2f(1, 1); glVertex2f(self.width - bar_width - 20 + speed_w, 50)
        glTexCoord2f(1, 0); glVertex2f(self.width - bar_width - 20 + speed_w, 50 + speed_h)
        glTexCoord2f(0, 0); glVertex2f(self.width - bar_width - 20, 50 + speed_h)
        glEnd()
        
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([tex_id])
        
        # Restore 3D settings
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def print_debug_info(self):
        """Print debug info ke terminal untuk troubleshooting"""
        print(f"\n=== ENHANCED CITY SIMULATION INFO ===")
        print(f"🚗 Car: Position=({self.car.x:.1f}, {self.car.z:.1f}), Speed={self.car.speed:.1f} km/h")
        print(f"🛣️  Road: On road = {self.car.is_on_road(self.car.x, self.car.z)}")
        print(f"🏢 Buildings: {len(self.city.buildings)} total in {len(self.road.city_blocks)} blocks")
        print(f"📷 Camera: {self.camera.mode} mode")
        print(f"⚡ Performance: {self.frame_count//60}s runtime")
    
    def run(self):
        """Main game loop with FPS monitoring"""
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        print("\n🚗 Enhanced 3D Maze City Simulation")
        print("🔧 Loading complete! Navigate the optimized 3x3 road grid...")
        print(f"🏙️ City ready: {len(self.city.buildings)} buildings in themed districts")
        print(f"🛣️ Road network: 3x3 grid with 9 intersections (64% fewer calculations)")
        print("📊 Real-time FPS monitoring enabled!")
        
        # Compile city geometry to GPU display list for performance
        print("⚡ Compiling static geometry to GPU...")
        self.city.compile_static_geometry()
        
        while self.running:
            # Simple FPS tracking
            self.current_fps = clock.get_fps()
            
            # Handle input events
            self.handle_events()
            
            # Update frame count
            self.frame_count += 1
            
            # Render frame
            self.render()
            
            # Swap buffers
            pygame.display.flip()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        # Cleanup GPU resources
        self.city.cleanup()
        self.road.cleanup()
        self.weather.cleanup()
        
        # Cleanup text texture cache
        for tex_id, _ in self.text_texture_cache.values():
            glDeleteTextures([tex_id])
        self.text_texture_cache.clear()
        print("🧹 UI text texture cache cleaned up")
        
        pygame.quit()
        print(f"\n✅ Optimized simulation closed! Average FPS: {self.current_fps:.1f}")

if __name__ == "__main__":
    simulation = None
    try:
        simulation = CitySimulation()
        simulation.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Pastikan semua library terinstall:")
        print("pip install pygame numpy PyOpenGL Pillow")
    finally:
        # Ensure cleanup even if error occurs
        if simulation is not None:
            try:
                simulation.city.cleanup()
                simulation.road.cleanup()
                simulation.weather.cleanup()
                # Cleanup text cache
                for tex_id, _ in simulation.text_texture_cache.values():
                    glDeleteTextures([tex_id])
            except:
                pass