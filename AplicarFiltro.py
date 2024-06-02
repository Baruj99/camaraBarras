#Programa para ver continuamente la càmara y configurarla
#Versión 1.1
from pyzbar import pyzbar
import cv2
import subprocess
from PIL import Image
import numpy as np
import skimage.exposure

#Tomar la cámara conectada en el índice 0
#Debe haber conectada una cámara
cap = cv2.VideoCapture(0)
print('Se inició el capturador de video')
#Desactivar el enfoque automàtico
subprocess.check_output(["v4l2-ctl", "-d", "/dev/video0", "-c", "focus_automatic_continuous=0"])
#Establecer el enfoque manual a un valor
enfoque = 12
strenfoque="focus_absolute="+str(enfoque)
subprocess.check_output(["v4l2-ctl", "-d", "/dev/video0", "-c", strenfoque])

#Definir una funciòn vacía
def nothing(x):
    pass
#Definir la función para activar o desactivar el autoenfoque
def autoenfoque(val):
    if val == 1:
        #Activar el enfoque automàtico
        subprocess.check_output(["v4l2-ctl", "-d", "/dev/video0", "-c", "focus_automatic_continuous=1"])
    else:
        #Desactivar el enfoque automàtico
        subprocess.check_output(["v4l2-ctl", "-d", "/dev/video0", "-c", "focus_automatic_continuous=0"])
        strenfoque="focus_absolute="+str(12)
        subprocess.check_output(["v4l2-ctl", "-d", "/dev/video0", "-c", strenfoque])
        cv2.setTrackbarPos("Forzar enfoque", "Control de cámara", 12)
#Definir la función para cambiar el enfoque manual
def enfoque_manual(enfoque_m):
    if cv2.getTrackbarPos('Autoenfoque \n1 0 : OFF \n1 : ON', "Control de cámara") == 0:
        #Establecer el enfoque manual a un valor
        strenfoque="focus_absolute="+str(enfoque_m)
        subprocess.check_output(["v4l2-ctl", "-d", "/dev/video0", "-c", strenfoque])
#Crear las barras para el menú
cv2.namedWindow("Control de cámara")
cv2.createTrackbar("Pixel Izquierdo", "Control de cámara", 0, 500, nothing)
cv2.createTrackbar("Pixel Derecho", "Control de cámara", 800, 1280, nothing)
cv2.createTrackbar("Pixel Arriba", "Control de cámara", 0, 200, nothing)
cv2.createTrackbar("Pixel Abajo", "Control de cámara", 200, 800, nothing)
switch = 'Autoenfoque \n1 0 : OFF \n1 : ON'
cv2.createTrackbar(switch, "Control de cámara", 0, 1, autoenfoque)
cv2.createTrackbar("Forzar enfoque", "Control de cámara", 0, 40, enfoque_manual)
#Inicializar los valores de las barras del menú
cv2.setTrackbarPos("Pixel Izquierdo", "Control de cámara", 453)
cv2.setTrackbarPos("Pixel Derecho", "Control de cámara", 932)
cv2.setTrackbarPos("Pixel Arriba", "Control de cámara", 160)
cv2.setTrackbarPos("Pixel Abajo", "Control de cámara", 800)
cv2.setTrackbarPos("Forzar enfoque", "Control de cámara", 12)


while True: #Bucle para siempre mantenerse leyendo el frame de la càmara
    #Capturar los frames utilizando la cámara
    #Leer frame
    _, frame = cap.read()
    #Leer los valores de los pixeles donde se desea cortar el frame
    p_i = cv2.getTrackbarPos("Pixel Izquierdo", "Control de cámara")
    p_d = cv2.getTrackbarPos("Pixel Derecho", "Control de cámara")
    p_ar = cv2.getTrackbarPos("Pixel Arriba", "Control de cámara")
    p_ab = cv2.getTrackbarPos("Pixel Abajo", "Control de cámara")
    #Recortar el frame
    img_cortada=frame[p_ar:p_ab, p_i:p_d]

    # convert to hsv
    lab = cv2.cvtColor(img_cortada,cv2.COLOR_BGR2LAB)
    L = lab[:,:,0]
    A = lab[:,:,1]
    B = lab[:,:,2]

    # negate A
    A = (255 - A)

    # multiply negated A by B
    nAB = 255 * (A/255) * (B/255)
    nAB = np.clip((nAB), 0, 255)
    nAB = np.uint8(nAB)


    # threshold using inRange
    range1 = 100
    range2 = 160
    mask = cv2.inRange(nAB,range1,range2)
    mask = 255 - mask

    # apply morphology opening to mask
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # antialias mask
    mask = cv2.GaussianBlur(mask, (0,0), sigmaX=3, sigmaY=3, borderType = cv2.BORDER_DEFAULT)
    mask = skimage.exposure.rescale_intensity(mask, in_range=(127.5,255), out_range=(0,255))

    # put white where ever the mask is zero
    result = img_cortada.copy()
    result[mask==0] = (255,255,255)



    #Colocar el texto para decirle al usuario que con la tecla ESC se termina el proceso
    cv2.putText(result, "ESC para salir", (20, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    #Colocar el texto para el código
    cv2.putText(result,"No. detectado", (20, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    #Inicia código para detectar valor de código de barras
    #Guardar el frame actual en el archivo './CamTmp/captura.jpg'
    cv2.imwrite('./CamTmp/captura.jpg', result)
    #Abrir la imagen usando una librería que permite girar la imagen
    imagen =  Image.open('./CamTmp/captura.jpg')
    #Iniciar la rotaciòn en un ángulo de 0, aumenta 45 grados cada iteración
    angulo_rotacion = 0
    angulo_aumento = 22.5
    #Gira hasta 180 grados
    while angulo_rotacion < 180:
        #Rotar imagen
        imagen_rotada = imagen.rotate(angulo_rotacion)
        #Guardar la imagen rotada en './CamTmp/capturaR.jpg'
        imagen_rotada = imagen_rotada.save('./CamTmp/capturaR.jpg')
        #Leer la imagen rotada
        imagenn = cv2.imread('./CamTmp/capturaR.jpg')
        #Detectar códigos de barras en la imagen
        codigos_encontrados = pyzbar.decode(imagenn)
        #Si se detecta al menos un código de barras en la imagen
        if len(codigos_encontrados) != 0:
            #Obtener el código detectado
            code_captura = codigos_encontrados[0].data.decode("utf-8")
            #Si se desea se puede imprimir el código detectado y el ángulo de rotación
            #print(f'-> Código: {code_captura} Ángulo: {angulo_rotacion}\n')
        else: #Si no se detecta ningún còdigo se le asigna el código 404
            code_captura = 404
        #Se aumenta el ángulo de rotación
        angulo_rotacion += angulo_aumento
        
    codigo_detectato = code_captura
    if codigo_detectato == '7506129430825': #si el còdigo es igual al de una lista entonces guarda el valor en "mensaje" correspondiente a esa lista 
        #print('Código 1')
        mensaje = 1
    elif codigo_detectato == '7503006758140':
        #print('Código 2')
        mensaje = 2
    elif codigo_detectato=='7503006758157':
        #print('Código 3')
        mensaje = 3
    elif codigo_detectato==404:
        #print("Código no detectado")
        mensaje = 0
    else:
        #print('Código no registrado')
        mensaje = 4
    #print('inicia la conexión en MODBUS')
    #print("Código = " + str(mensaje))
    #Código detectado
    print(codigo_detectato)
    #Termina código para detectar valor de código de barras
    cv2.putText(img_cortada,str(codigo_detectato), (20, 80), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
    #Mostrar el frame de la cámara recortado
    cv2.imshow("Frame", result)
    #Esperar 1 milisegundo para que se presione la tecla ESC
    key = cv2.waitKey(1)
    if key == 27:
        break #Si se presiona la tecla ESC se termina el proceso
cap.release() #Se libera el uso de la càmara
cv2.destroyAllWindows() #Se destruyen las ventanas creadas


# display it
#cv2.imshow("nAB", nAB)
#cv2.imshow("mask", mask)
#cv2.imshow("result", result)