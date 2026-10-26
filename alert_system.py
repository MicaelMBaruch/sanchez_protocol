import cv2
import numpy as np
import pygame
import os
import subprocess
import time

class AlertSystem:
    def __init__(self, silent_mode=False):
        pygame.init()
        # pygame.mixer.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.font_large = pygame.font.SysFont(None, 120)
        self.font_medium = pygame.font.SysFont(None, 80)
        self.silent_mode = silent_mode
        self.alarm_muted_until = 0

    def override_system_volume(self):
        # Comando para Arch/Hyprland (Wireplumber/Pipewire)
        try:
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"])
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "1.0"])
        except Exception:
            pass # Fallback silencioso

    def render_ui(self, frame, text="", bg_color=(0, 0, 0), text_color=(255, 255, 255), flash=False):
        if flash and int(time.time() * 10) % 2 == 0:
            bg_color = (255, 0, 0)
            text_color = (255, 255, 0)

        self.screen.fill(bg_color)
        
        # 1. Renderiza a Câmera no centro da tela
        if frame is not None:
            # OpenCV usa BGR, Pygame usa RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Pygame inverte os eixos X e Y em relação as matrizes do Numpy
            frame_surf = pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))
            
            rect = frame_surf.get_rect(center=self.screen.get_rect().center)
            self.screen.blit(frame_surf, rect)

        # 2. Renderiza o Texto por cima da tela
        if text:
            img = self.font_large.render(text, True, text_color)
            # Joga o texto lá pro topo (Y=100) para não cobrir o rosto da câmera
            rect = img.get_rect(center=(self.screen.get_rect().centerx, 100))
            self.screen.blit(img, rect)

        pygame.display.flip()

    def play_sound(self, sound_type):
        if self.silent_mode or time.time() < self.alarm_muted_until:
            return
            
        # Implementação simulada, adicione os arquivos .wav na pasta assets
        # if sound_type == "warning" and not pygame.mixer.music.get_busy():
        #     pygame.mixer.music.load("assets/warning.wav")
        #     pygame.mixer.music.play()
        # elif sound_type == "alarm":
        #     self.override_system_volume()
        #     ...

    def mute_temporarily(self, seconds=15):
        self.alarm_muted_until = time.time() + seconds
        pygame.mixer.music.stop()

    def send_remote_notification(self, msg):
        # Pode usar ntfy.sh para receber no celular
        # subprocess.run(["curl", "-d", msg, "ntfy.sh/seu_topico_sanchez_secreto"])
        print(f"[NOTIFICAÇÃO ENVIADA]: {msg}")
