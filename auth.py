import pygame


class AuthModule:
    def __init__(self, password):
        self.password = password
        self.buffer = ""
        self.deactivated = False
        self.mute_requested = False

    def process_key_event(self, event):
        """Processa eventos de teclado vindos do Pygame"""
        if event.type == pygame.KEYDOWN:
            # Pega os modificadores (Ctrl, Shift, etc)
            mods = pygame.key.get_mods()
            
            # Atalho de emergência: Ctrl + Shift + U 
            # (Removemos a tecla 'Super/Windows' porque o Hyprland costuma roubar ela para atalhos do sistema)
            if event.key == pygame.K_u and (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_SHIFT):
                self.mute_requested = True
                return

            # Captura a digitação normal da senha
            if event.unicode:
                self.buffer += event.unicode
                # Mantém o buffer curto para não estourar memória se alguém digitar muito
                self.buffer = self.buffer[-len(self.password):]
                
                if self.buffer == self.password:
                    self.deactivated = True
