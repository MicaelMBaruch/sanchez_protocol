import argparse
import time
import sys
import pygame
import cv2
from vision import VisionModule
from alert_system import AlertSystem
from auth import AuthModule

# Estados
IDLE = "IDLE"
WARNING = "WARNING"
THANK_YOU = "THANK_YOU"
ALARM = "ALARM"
CAM_COVERED = "CAM_COVERED"

def main():
    parser = argparse.ArgumentParser(description="Protocolo Sanchez de Segurança")
    parser.add_argument("-s", "--silent", action="store_true", help="Ativa sem alarmes sonoros")
    args = parser.parse_args()

    vision = VisionModule()
    alert = AlertSystem(silent_mode=args.silent)
    auth = AuthModule(password="senha123") # Idealmente carregar de variável de ambiente

    state = IDLE
    state_timer = time.time()
    last_distance = 999

    print("Protocolo Sanchez Ativado. Protegendo o sistema...")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass # Impede que fechem no 'X' (se houver borda)
            elif event.type == pygame.KEYDOWN:
                auth.process_key_event(event)       

        # 1. Verifica Desativação
        if auth.deactivated:
            alert.render_ui(frame, "PROTOCOLO DESATIVADO", bg_color=(0, 255, 0))
            time.sleep(2)
            break

        if auth.mute_requested:
            alert.mute_temporarily(15)
            auth.mute_requested = False
            # Bloqueia a tela/pede senha através da interface se necessário

        # 2. Processa Câmera
        frame, data = vision.process_frame()
        
        # Permite renderizar eventos do pygame para não travar a janela
        pygame.event.pump()

        # 3. Analisa ameaças
        known_present = any(f["name"] != "Desconhecido" for f in data["faces"])
        unknown_faces = [f for f in data["faces"] if f["name"] == "Desconhecido"]
        
        is_threat = len(unknown_faces) > 0 and not known_present
        current_distance = min([f["distance"] for f in unknown_faces]) if is_threat else 999

        # 4. Máquina de Estados
        if data["covered"]:
            if state != CAM_COVERED:
                state = CAM_COVERED
                state_timer = time.time()
            
            if time.time() - state_timer < 5:
                alert.render_ui(frame, "DESCUBRA A CÂMERA", bg_color=(200, 100, 0))
                alert.play_sound("warning")
            else:
                state = ALARM
                
        elif state == CAM_COVERED and not data["covered"]:
            state = IDLE

        elif is_threat:
            if state == IDLE or state == THANK_YOU:
                state = WARNING
                last_distance = current_distance
                state_timer = time.time()
            
            elif state == WARNING:
                alert.render_ui(frame, "AFASTE-SE 2 PASSOS", bg_color=(255, 100, 0))
                alert.play_sound("warning")
                
                # Se persistir por 5 segundos ou se aproximar mais de 15cm repentinamente
                if (time.time() - state_timer > 5) or (current_distance < last_distance - 15):
                    state = ALARM
                    alert.send_remote_notification("TENTATIVA DE ROUBO DETECTADA!")
                
                # Se a pessoa recuou (distância aumentou 30cm, simulando 2 passos)
                elif current_distance > last_distance + 30:
                    state = THANK_YOU
                    state_timer = time.time()

            elif state == ALARM:
                alert.override_system_volume()
                alert.render_ui(frame, "ALARME DE ROUBO!", flash=True)
                alert.play_sound("alarm")

        else: # Sem ameaças
            if state == THANK_YOU:
                alert.render_ui(frame, "OBRIGADO", text_color=(0, 255, 0))
                if time.time() - state_timer > 3: # Exibe por 3 segundos
                    state = IDLE
            elif state != ALARM: # Uma vez no alarme, só sai com senha
                state = IDLE
                alert.render_ui(frame)

    # Limpeza
    vision.cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
