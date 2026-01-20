# camera.py
import numpy as np

class Camera:
    def __init__(self):
        self.mode = 'follow'  # 'follow', 'orbital', 'top', 'free', 'side'
        self.x = 0.0
        self.y = 10.0
        self.z = 20.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0
        
        # Free camera mode properties
        self.free_camera_angle = 0.0
        self.free_camera_height = 10.0
        self.free_camera_distance = 20.0  # Jarak dari mobil
        
        # Orbital camera mode properties (mouse-controlled)
        self.orbital_angle = 180.0  # Horizontal rotation (azimuth)
        self.orbital_pitch = 15.0   # Vertical angle (elevation)
        self.orbital_distance = 20.0
        self.is_mouse_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_sensitivity = 0.3  # Degrees per pixel
    
    def set_mode(self, mode):
        self.mode = mode
        print(f"Camera mode: {mode.upper()}")
        
        # Reset angle untuk free mode
        if mode == 'free':
            self.free_camera_angle = 0.0
            self.free_camera_height = 10.0
            self.free_camera_distance = 20.0
        
        # Reset orbital camera properties
        elif mode == 'orbital':
            self.orbital_angle = 180.0
            self.orbital_pitch = 15.0
            self.orbital_distance = 20.0
            self.is_mouse_dragging = False
    
    def update(self, car):
        if self.mode == 'follow':
            # Kamera mengikuti mobil dari belakang
            angle_rad = np.radians(car.direction)
            distance = 15.0
            height = 5.0
            
            self.x = car.x - np.sin(angle_rad) * distance
            self.z = car.z - np.cos(angle_rad) * distance
            self.y = car.y + height
            
            self.target_x = car.x + np.sin(angle_rad) * 10
            self.target_z = car.z + np.cos(angle_rad) * 10
            self.target_y = car.y + 2.0
        
        elif self.mode == 'orbital':
            # Mouse-controlled orbital camera using spherical coordinates
            angle_rad = np.radians(self.orbital_angle)
            pitch_rad = np.radians(self.orbital_pitch)
            
            # Calculate camera position using spherical coordinates
            self.x = car.x + self.orbital_distance * np.cos(pitch_rad) * np.sin(angle_rad)
            self.z = car.z + self.orbital_distance * np.cos(pitch_rad) * np.cos(angle_rad)
            self.y = car.y + self.orbital_distance * np.sin(pitch_rad)
            
            # Always target the car
            self.target_x = car.x
            self.target_y = car.y + 2.0
            self.target_z = car.z
            
        elif self.mode == 'top':
            # Kamera dari atas
            self.x = car.x
            self.y = 50.0
            self.z = car.z
            self.target_x = car.x
            self.target_y = 0.0
            self.target_z = car.z + 10.0
            
        elif self.mode == 'free':
            # Kamera bebas mengorbit mobil
            angle_rad = np.radians(self.free_camera_angle)
            
            # Posisi kamera mengelilingi mobil
            self.x = car.x + np.cos(angle_rad) * self.free_camera_distance
            self.z = car.z + np.sin(angle_rad) * self.free_camera_distance
            self.y = car.y + self.free_camera_height
            
            # Target selalu di mobil
            self.target_x = car.x
            self.target_y = car.y + 2.0
            self.target_z = car.z
            
        elif self.mode == 'side':
            # Kamera dari samping kiri
            angle_rad = np.radians(car.direction + 90)  # 90° dari depan (samping)
            distance = 12.0
            
            self.x = car.x + np.sin(angle_rad) * distance
            self.z = car.z + np.cos(angle_rad) * distance
            self.y = car.y + 4.0  # Sedikit lebih tinggi
            
            self.target_x = car.x
            self.target_y = car.y + 1.5
            self.target_z = car.z
    
    def move_forward(self):
        if self.mode == 'free':
            self.free_camera_height += 2.0
    
    def move_backward(self):
        if self.mode == 'free':
            self.free_camera_height = max(2.0, self.free_camera_height - 2.0)
    
    def turn_left(self):
        if self.mode == 'free':
            self.free_camera_angle += 10.0
    
    def turn_right(self):
        if self.mode == 'free':
            self.free_camera_angle -= 10.0
    
    def zoom_in(self):
        if self.mode == 'free':
            self.free_camera_distance = max(5.0, self.free_camera_distance - 2.0)
    
    def zoom_out(self):
        if self.mode == 'free':
            self.free_camera_distance = min(50.0, self.free_camera_distance + 2.0)
    
    # Mouse control methods for orbital camera
    def start_mouse_drag(self, mouse_x, mouse_y):
        """Initialize mouse drag for orbital camera"""
        if self.mode == 'orbital':
            self.is_mouse_dragging = True
            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y
    
    def update_mouse_drag(self, mouse_x, mouse_y):
        """Update camera angles based on mouse movement"""
        if self.mode == 'orbital' and self.is_mouse_dragging:
            # Calculate mouse delta
            delta_x = mouse_x - self.last_mouse_x
            delta_y = mouse_y - self.last_mouse_y
            
            # Update horizontal angle (azimuth)
            self.orbital_angle -= delta_x * self.mouse_sensitivity
            # Wrap angle to 0-360 range
            self.orbital_angle = self.orbital_angle % 360.0
            
            # Update vertical angle (pitch) with clamping
            self.orbital_pitch += delta_y * self.mouse_sensitivity
            self.orbital_pitch = max(-85.0, min(85.0, self.orbital_pitch))
            
            # Update last mouse position
            self.last_mouse_x = mouse_x
            self.last_mouse_y = mouse_y
    
    def end_mouse_drag(self):
        """End mouse drag"""
        if self.mode == 'orbital':
            self.is_mouse_dragging = False
    
    def mouse_wheel_zoom(self, delta):
        """Adjust orbital camera distance with mouse wheel"""
        if self.mode == 'orbital':
            self.orbital_distance -= delta * 2.0
            self.orbital_distance = max(5.0, min(50.0, self.orbital_distance))