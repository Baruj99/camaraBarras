#Programa simplificado para establecer conexión entre el lector de códigos y el PLC
#Versión 1.0
from pyzbar import pyzbar
import cv2
import subprocess
from PIL import Image
import easymodbus.modbusClient
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

while True: #Bucle para siempre mantenerse leyendo el código de barras
    #Capturar los frames utilizando la cámara
    #Leer frame
    _, img_interes = cap.read()
    #Recortar el frame
    frame = img_interes[160:800, 453:932]
    #Guardar el frame actual en el archivo './CamTmp/captura.jpg'
    cv2.imwrite('./CamTmp/captura.jpg', frame)
    #Abrir la imagen usando una librería que permite girar la imagen
    imagen =  Image.open('./CamTmp/captura.jpg')
    #Iniciar la rotaciòn en un ángulo de 0, aumenta 45 grados cada iteración
    angulo_rotacion = 0
    angulo_aumento = 45
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
    print(codigo_detectato)
    """#Se conecta a la IP del servidor MODBUS en el puerto correspondiente
    modbus_client = easymodbus.modbusClient.ModbusClient('172.16.24.78',504) #Crear instancia para conexion en esta IP y puerto
    modbus_client.connect() #Conectar a cliente modbus
    #Escribir en el registro 0 el mensaje correspondiente al código de barras
    modbus_client.write_single_register(0, mensaje)	#Escribir el valor del mensaje al registro 0
    #Cierra la conexión en MODBUS
    modbus_client.close()"""
    #Esperar 1 milisegundo para que se presione la tecla ESC
    key = cv2.waitKey(1)
    if key == 27:
        break #Si se presiona la tecla ESC se termina el proceso
cap.release() #Se libera el uso de la càmara
cv2.destroyAllWindows() #Se destruyen las ventanas creadas
