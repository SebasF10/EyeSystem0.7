import os
import cv2
import imutils
import mediapipe as mp
import numpy as np
from collections import deque
from datetime import datetime

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

def aplicar_mejoras_imagen(imagen):
    # Convertir a LAB para mejor procesamiento de color
    lab = cv2.cvtColor(imagen, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Aplicar CLAHE al canal L
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Mejorar nitidez
    kernel_sharpen = np.array([[-1,-1,-1],
                              [-1,9,-1],
                              [-1,-1,-1]])
    l = cv2.filter2D(l, -1, kernel_sharpen)
    
    # Recombinar canales
    lab = cv2.merge([l, a, b])
    imagen_mejorada = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Reducción de ruido preservando bordes
    imagen_mejorada = cv2.bilateralFilter(imagen_mejorada, 9, 75, 75)
    
    return imagen_mejorada

def verificar_calidad_rostro(rostro, face_landmarks):
    if face_landmarks is None:
        return False
        
    # Verificar brillo promedio
    gray = cv2.cvtColor(rostro, cv2.COLOR_BGR2GRAY)
    brillo_promedio = np.mean(gray)
    if brillo_promedio < 40 or brillo_promedio > 220:
        return False
    
    # Verificar contraste
    contraste = np.std(gray)
    if contraste < 20:
        return False
    
    # Verificar borrosidad
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 100:
        return False
        
    return True

def ejecutar(nombre_carpeta):
    rutadata = "C:/Users/USER/Desktop/Interfaz-3.0-main/formularios/Data"
    personadata = os.path.join(rutadata, nombre_carpeta)

    if not os.path.exists(personadata):
        print("Carpeta creada:", personadata)
        os.makedirs(personadata)

    # Configuración mejorada de la cámara
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Mayor resolución
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
    
    if not cap.isOpened():
        print("Error al abrir la cámara")
        exit()

    faceclasif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = 0
    fotos_descartadas = 0
    ultima_captura = datetime.now()
    intervalo_captura = 0.1  # segundos entre capturas
    
    # Buffer para estabilización
    pose_buffer = deque(maxlen=5)
    landmarks_buffer = deque(maxlen=5)
    
    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        refine_landmarks=True) as face_mesh:
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error al leer frame")
                break

            # Procesamiento inicial del frame
            frame = imutils.resize(frame, width=640)  # Aumentado para mejor calidad
            frame = cv2.flip(frame, 1)
            frame_mejorado = aplicar_mejoras_imagen(frame)
            gray = cv2.cvtColor(frame_mejorado, cv2.COLOR_BGR2GRAY)
            auxframe = frame_mejorado.copy()

            # Detección de rostros mejorada
            faces = faceclasif.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100),  # Aumentado para mejor calidad
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            tiempo_actual = datetime.now()
            tiempo_transcurrido = (tiempo_actual - ultima_captura).total_seconds()

            # Mostrar estadísticas
            cv2.putText(frame, f"Capturas: {count}/300", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Descartadas: {fotos_descartadas}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    # Agregar padding para incluir más contexto facial
                    padding = int(0.2 * w)  # Aumentado para capturar más contexto
                    x1 = max(0, x - padding)
                    y1 = max(0, y - padding)
                    x2 = min(frame.shape[1], x + w + padding)
                    y2 = min(frame.shape[0], y + h + padding)
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    rostro = auxframe[y1:y2, x1:x2]
                    
                    if rostro.size > 0:
                        # Procesar landmarks faciales
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = face_mesh.process(frame_rgb)
                        
                        if results.multi_face_landmarks and tiempo_transcurrido >= intervalo_captura:
                            landmarks = results.multi_face_landmarks[0]
                            landmarks_buffer.append(landmarks)
                            
                            # Verificar estabilidad de landmarks
                            if len(landmarks_buffer) == landmarks_buffer.maxlen:
                                # Procesar y guardar imagen si pasa las verificaciones
                                if verificar_calidad_rostro(rostro, landmarks):
                                    rostro = cv2.resize(rostro, (1024, 1024), 
                                                      interpolation=cv2.INTER_LANCZOS4)
                                    
                                    # Aplicar mejoras finales
                                    rostro = aplicar_mejoras_imagen(rostro)
                                    
                                    filename = f'rostro_{count:03d}.jpg'
                                    path = os.path.join(personadata, filename)
                                    cv2.imwrite(path, rostro, [cv2.IMWRITE_JPEG_QUALITY, 100])
                                    count += 1
                                    ultima_captura = tiempo_actual
                                else:
                                    fotos_descartadas += 1
                            
                            # Dibujar malla facial
                            mp_drawing.draw_landmarks(
                                frame,
                                landmarks,
                                mp_face_mesh.FACEMESH_TESSELATION,
                                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1),
                                mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))

            cv2.imshow("Captura de Rostros con Malla Facial", frame)
            k = cv2.waitKey(1) & 0xFF
            if k == 27 or count >= 200:  # Aumentado a 300 fotos
                break

    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\nProceso completado:")
    print(f"- Fotos capturadas: {count}")
    print(f"- Fotos descartadas: {fotos_descartadas}")
    print(f"- Calidad de captura: {(count/(count+fotos_descartadas))*100:.2f}%")
