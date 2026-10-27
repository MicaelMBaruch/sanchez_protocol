# build_encodings.py
import os
import pickle
import face_recognition
import argparse

def build_cache(dataset_dir="rostos_permitidos", cache_file="encodings.pkl", jitters=5):
    print(f"[INFO] Processando rostos no diretório '{dataset_dir}'...")
    
    if not os.path.exists(dataset_dir):
        print(f"[ERRO] Diretório '{dataset_dir}' não encontrado.")
        return

    known_encodings = []
    known_names = []

    for filename in os.listdir(dataset_dir):
        if filename.lower().endswith((".jpg", ".png", ".jpeg")):
            filepath = os.path.join(dataset_dir, filename)
            # O nome da pessoa será o nome do arquivo, removendo números e extensão (ex: micael_1.jpg -> micael)
            base_name = os.path.splitext(filename)[0]
            name = "".join([c for c in base_name if not c.isdigit()]).strip("_").upper()
            
            print(f"[INFO] Extraindo características de: {name} ({filename})")
            
            img = face_recognition.load_image_file(filepath)
            # num_jitters aplica pequenas distorções na imagem para criar uma assinatura mais resiliente
            encodings = face_recognition.face_encodings(img, num_jitters=jitters)
            
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)
            else:
                print(f"[AVISO] Nenhum rosto detectado em {filename}.")

    # Serializando os dados para um arquivo binário ultrarrápido
    data = {"encodings": known_encodings, "names": known_names}
    
    with open(cache_file, "wb") as f:
        pickle.dump(data, f)
        
    print(f"[SUCESSO] Cache salvo em '{cache_file}' com {len(known_names)} assinaturas faciais cadastradas.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera o cache serializado de encodings faciais.")
    parser.add_argument("-d", "--dataset", type=str, default="rostos_permitidos", help="Caminho para a pasta de fotos")
    parser.add_argument("-c", "--cache", type=str, default="encodings.pkl", help="Nome do arquivo de saída")
    parser.add_argument("-j", "--jitters", type=int, default=5, help="Nº de distorções para aumento de precisão")
    args = parser.parse_args()
    
    build_cache(args.dataset, args.cache, args.jitters)
