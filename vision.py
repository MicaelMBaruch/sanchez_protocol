import cv2
import face_recognition
import numpy as np
import os
import pickle

class VisionModule:
    def __init__(self, cache_file="encodings.pkl"):
        self.cap = cv2.VideoCapture(0)
        self.known_encodings = []
        self.known_names = []
        
        # Carrega o cache serializado em milissegundos
        self._load_encodings_from_cache(cache_file)
        
        self.FOCAL_LENGTH = 600
        self.KNOWN_FACE_WIDTH = 14.0 
        
        self.frame_skip_rate = 3
        self.frame_count = 0
        self.last_faces_data = []

    def _load_encodings_from_cache(self, cache_file):
        """Lê o arquivo .pkl contendo as matrizes da rede neural pré-computadas."""
        if not os.path.exists(cache_file):
            print(f"[ERRO CRÍTICO] Cache '{cache_file}' não encontrado.")
            print("Execute 'python build_encodings.py' antes de iniciar o protocolo.")
            return

        with open(cache_file, "rb") as f:
            data = pickle.load(f)
            self.known_encodings = data["encodings"]
            self.known_names = data["names"]
            print(f"[VISION] {len(self.known_names)} rostos pré-carregados do cache em tempo recorde.")

    def check_camera_covered(self, frame):
        # Se a imagem estiver muito escura ou com variância muito baixa, está coberta
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = np.var(gray)
        mean_brightness = np.mean(gray)
        return variance < 50 or mean_brightness < 20

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret: return None, {"covered": True, "faces": []}

        covered = self.check_camera_covered(frame)
        if covered:
            return frame, {"covered": True, "faces": []}

        self.frame_count += 1


        # Reduzir tamanho para processar mais rápido
        if self.frame_count % self.frame_skip_rate == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small)
            face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

            self.last_faces_data = []
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.6)
                name = "Desconhecido"
                if True in matches:
                    name = self.known_names[matches.index(True)]

                # Calcular distância aproximada
                pixel_width = (right - left) * 4 # Multiplica por 4 devido ao resize
                distance_cm = (self.KNOWN_FACE_WIDTH * self.FOCAL_LENGTH) / pixel_width if pixel_width > 0 else 999

                self.last_faces_data.append({
                    "name": name,
                    "distance": distance_cm,
                    "box": (top*4, right*4, bottom*4, left*4)
                })

        for face in self.last_faces_data:
            top, right, bottom, left = face["box"]
            name = face["name"]

            is_known = name != "DESCONHECIDO"
            color = (0, 255, 0) if is_known else (0,0,255)
            # Desenha Caixa
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Fundo escuro para o texto ficar legível
            cv2.rectangle(frame, (left, top - 35), (right, top), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, top - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        return frame, {"covered": False, "faces": self.last_faces_data}
