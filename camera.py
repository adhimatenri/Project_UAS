# camera.py
import numpy as np

class Camera:
    def __init__(self):
        self.mode = 'follow'  # 'follow', 'top', 'free', 'side'
        self.x = 0.0
        self.y = 10.0
        self.z = 20.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0
        self.free_camera_angle = 0.0
        self.free_camera_height = 10.0
        self.free_camera_distance = 20.0  # Jarak dari mobil
    
    def set_mode(self, mode):
        self.mode = mode
        print(f"Camera mode: {mode.upper()}")
        
        # Reset angle untuk free mode
        if mode == 'free':
            self.free_camera_angle = 0.0
            self.free_camera_height = 10.0
            self.free_camera_distance = 20.0
    
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