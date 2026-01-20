# weather.py - Performance-Optimized Weather System
import numpy as np
from OpenGL.GL import *
import random

class WeatherSystem:
    def __init__(self):
        # Fog settings
        self.fog_enabled = False
        self.fog_color = (0.1, 0.1, 0.15, 1.0)  # Bluish-gray matching night sky
        self.fog_density = 0.014  # Enhanced haze (40% increase)
        
        # Snowfall particle system
        self.num_particles = 210  # Enhanced snowfall (40% increase)
        self.particles = []
        self.particle_spawn_radius = 40.0
        self.particle_spawn_height = 30.0
        
        # Initialize particle pool
        self.init_particles()
        
        print("🌨️  Weather system initialized:")
        print(f"   Fog: Exponential squared (density={self.fog_density})")
        print(f"   Snowflakes: {self.num_particles} particles")
    
    def init_particles(self):
        """Initialize snowflake particle pool"""
        for i in range(self.num_particles):
            particle = {
                'x': random.uniform(-self.particle_spawn_radius, self.particle_spawn_radius),
                'y': random.uniform(0, self.particle_spawn_height),
                'z': random.uniform(-self.particle_spawn_radius, self.particle_spawn_radius),
                'fall_speed': random.uniform(0.1, 0.3),
                'drift_x': random.uniform(-0.02, 0.02),
                'drift_z': random.uniform(-0.02, 0.02)
            }
            self.particles.append(particle)
    
    def enable_fog(self):
        """Enable OpenGL hardware fog"""
        glEnable(GL_FOG)
        glFogi(GL_FOG_MODE, GL_EXP2)  # Exponential squared for smooth falloff
        glFogfv(GL_FOG_COLOR, self.fog_color)
        glFogf(GL_FOG_DENSITY, self.fog_density)
        glHint(GL_FOG_HINT, GL_NICEST)
        self.fog_enabled = True
        print("   ✓ Atmospheric fog enabled")
    
    def disable_fog(self):
        """Disable OpenGL fog"""
        glDisable(GL_FOG)
        self.fog_enabled = False
        print("   ✗ Atmospheric fog disabled")
    
    def update(self, camera):
        """Update particle positions relative to camera"""
        for particle in self.particles:
            # Apply falling motion
            particle['y'] -= particle['fall_speed']
            
            # Apply wind drift
            particle['x'] += particle['drift_x']
            particle['z'] += particle['drift_z']
            
            # Recycle particle if it hits the ground or goes too far
            if particle['y'] < 0 or abs(particle['x'] - camera.x) > self.particle_spawn_radius * 2 or abs(particle['z'] - camera.z) > self.particle_spawn_radius * 2:
                # Respawn above camera with random offset
                particle['x'] = camera.x + random.uniform(-self.particle_spawn_radius, self.particle_spawn_radius)
                particle['y'] = camera.y + self.particle_spawn_height + random.uniform(0, 10)
                particle['z'] = camera.z + random.uniform(-self.particle_spawn_radius, self.particle_spawn_radius)
                particle['fall_speed'] = random.uniform(0.1, 0.3)
                particle['drift_x'] = random.uniform(-0.02, 0.02)
                particle['drift_z'] = random.uniform(-0.02, 0.02)
    
    def render(self):
        """Render snowflakes efficiently using GL_POINTS"""
        # Disable lighting for particles
        glDisable(GL_LIGHTING)
        
        # Enable blending for soft particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set point size for snowflakes
        glPointSize(3.0)
        
        # Set snowflake color (white with slight transparency)
        glColor4f(1.0, 1.0, 1.0, 0.8)
        
        # Draw all particles in a single batch
        glBegin(GL_POINTS)
        for particle in self.particles:
            glVertex3f(particle['x'], particle['y'], particle['z'])
        glEnd()
        
        # Reset point size
        glPointSize(1.0)
        
        # Disable blending
        glDisable(GL_BLEND)
        
        # Re-enable lighting
        glEnable(GL_LIGHTING)
    
    def cleanup(self):
        """Clean up weather system resources"""
        if self.fog_enabled:
            self.disable_fog()
        print("🧹 Weather system cleaned up")
