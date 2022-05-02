import PySimpleGUI as sg
import create_keypair as ckp
import schnorr_lib as sl
import os
import json 

G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

lista_documentos = []

def hashPDF(file, BLOCK_SIZE):
    # hash=sha256()
    with open(file, 'rb') as f: # Open the file to read it's bytes
        fb = f.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
        M = sl.sha256(fb)
    return M


def make_win1():

    layout = [[sg.Text('Programa de Firmas Schnorr')],
            [sg.Button("Cambiar mis claves"),sg.Button("Esquema MuSig")],
            [sg.Button('Verificar Firma'), sg.Button('Salir')]]
    return sg.Window('Ventana para Generar Claves Iniciales', layout, finalize=True)

def make_win2():

    layout = [[sg.Text('Ventana para Esquema MuSig')],
            [sg.Button('Generar mis claves Iniciales'),sg.Button("Generar mi Firma Esquema MuSig")],
            [sg.Button("Juntar Firmas"),sg.Button("Juntar Documentos")],
            [sg.Button('Salir')]]
    return sg.Window('Programa de Firmas Schnorr', layout, finalize=True)


def make_win3():

    layout = [[sg.Text('Esquema Firmas')],
            [sg.Text("Elegir el archivo para Firmar: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo-")],
            [sg.Text("Elegir el archivo con las claves: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo4-")],
            [sg.Text("Ingresa el numero de usuario que firma:")],
            [sg.Input(key='-Claves-', enable_events=True)],
            [sg.Button('Firmar el Documento'),sg.Button('Regresar')]]
    return sg.Window('Firma Individual', layout, finalize=True)

def make_win4():

    layout = [[sg.Text('Ventana de Verificación')],
            [sg.Text("Elegir el archivo: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo2-")],
            [sg.Text("Elegir el archivo con la firma: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo6-")],
            [sg.Button("Verificar"), sg.Button("Regresar")]]
    return sg.Window('Verificar Firma de un Documento', layout, finalize=True)

def make_win5():

    layout = [[sg.Text('Generación de firma Conjunta del Esquema')],
            [sg.Text("Elegir el archivo con las firmas individuales: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo5-")],
            [sg.Button('Generar Firma MuSig'),sg.Button('Regresar')]]
    return sg.Window('Generación de Esquema MuSig', layout, finalize=True)

def make_win6():

    layout = [[sg.Text('Programa para juntar archivos tipo JSON')],
            [sg.Text("Elegir el archivo: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo3-")],
            [sg.Button('Agregar Documento'), sg.Button('Borrar Documentos')],
            [sg.Button("Descargar Documento"), sg.Button("Regresar")]]
    return sg.Window('Ventana para Juntar Documento', layout, finalize=True)

def make_win7():

    layout = [[sg.Text('Primer Paso Esquema MuSig para generar las claves iniciales')],
            [sg.Text("Elegir el archivo que se planea Firmar: "), sg.Input(change_submits=True), sg.FileBrowse(key="-Archivo7-")],
            [sg.Button("Crear Claves Esquema"),sg.Button("Regresar")]]
    return sg.Window('Ventana para Generar Claves Iniciales', layout, finalize=True)

def make_win8():

    layout = [[sg.Text('Cambiar mis Claves Privada y Publica')],
            [sg.Button("Cambiar Claves"),sg.Button("Regresar")]]
    return sg.Window('Ventana para Generar Claves Iniciales', layout, finalize=True)


window1, window2 = make_win1(), None        # start off with 1 window open

while True:             # Event Loop
    window, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED or event == 'Salir' or event == 'Regresar':
        window.close()
        if window == window2:       # if closing win 2, mark as closed
            window2 = None
        elif window == window1:     # if closing win 1, exit program
            break

    elif event == 'Generar mi Firma Esquema MuSig':
        window3 = make_win3()

    elif event == 'Firmar el Documento':
        size = os.path.getsize(values["-Archivo-"])

        n_usuario = int(float(values["-Claves-"]))

        M = hashPDF(values["-Archivo-"], size)
        s = sl.schnorr_musig_firmar('claves_firma.json', M, n_usuario)


        #llave_privada = privada.hex()

        sg.Popup("Firma Usuario: ", s)


    elif event == 'Verificar Firma':
        window4 = make_win4()

    elif event == 'Verificar':
        size = os.path.getsize(values['-Archivo2-']) 
        M = hashPDF(values['-Archivo2-'], size)
        

        path_firma = values['-Archivo6-']
        result = sl.schnorr_verify_musig(M, path_firma)

        if result:
            sg.Popup("La firma es VALIDA para este mensaje y clave pública")
        else:
            sg.Popup("La firma no es VALIDA para este mensaje y clave pública")

    elif event == "Crear Claves Esquema":
        # sig_bytes = bytes.fromhex(values["-Firma-"])
        size = os.path.getsize(values["-Archivo7-"])
        M = hashPDF(values["-Archivo7-"], size)

        with open('users.json', 'r') as f:
            data = json.load(f)

        priv_key = data['users'][0]['privateKey']


        di = sl.int_from_hex(priv_key)

        Pi = sl.pubkey_point_gen_from_int(di)

        t = sl.xor_bytes(sl.bytes_from_int(di), sl.tagged_hash("BIP0340/aux", sl.get_aux_rand()))
        ki = sl.int_from_bytes(sl.tagged_hash("BIP0340/nonce", t + sl.bytes_from_point(Pi) + M)) % n
        if ki == 0:
            raise RuntimeError('Failure. This happens only with negligible probability.')
        
        # Ri = ki * G
        Ri = sl.point_mul(G, ki)

        assert Ri is not None

        #Pi = sl.pubkey_gen_from_hex(priv_key)

        sg.Popup("Clave Publica", Pi, "Ri", Ri)

        #cl = str(sl.int_from_bytes(Pi))

        Ri = str(Ri)
        data = {'Clave Publica': str(Pi),'Ri': Ri, 'Ki': ki}

        with open('claves_iniciales.json', 'w') as f:
            json.dump(data, f)

    elif event == 'Juntar Firmas':
        window5 = make_win5()

    elif event == 'Generar Firma MuSig':

        path_claves = values['-Archivo5-']
        with open(path_claves, 'r') as f:
            data = json.load(f)

        Rsum = data[0]['Sumatoria R']

        s_suma = 0
        for i in data: 
            s_i = i['firma']
            s_suma += s_i

        s_suma = s_suma % n

        signature_bytes = sl.bytes_from_point(Rsum) + sl.bytes_from_int(s_suma)


        X = sl.bytes_from_point(data[0]['firma agregada'])

        sg.Popup("Firma", signature_bytes.hex(), "Firma Agregada", X.hex())

#        signature_bytes = sl.int_from_bytes(signature_bytes)

        X = sl.int_from_bytes(X)

        signature_bytes = str(signature_bytes)


        datos_firma = {'Firma': signature_bytes, 'Firma Agregada': X}

        with open('firma_digital.json', 'w') as f:
            json.dump(datos_firma, f)    
        
    elif event == 'Juntar Documentos':
        window6 = make_win6()

    elif event == 'Agregar Documento':
        path_archivo = values["-Archivo3-"]
        lista_documentos.append(path_archivo)
        print(lista_documentos)
        sg.PopupScrolled("Los siguientes archivos son los que se van a juntar: \n", f"{lista_documentos}")

    
    elif event == 'Descargar Documento':
        sl.merge_JsonFiles(lista_documentos)
        sg.Popup('Se ha descargado el documento')

    elif event == 'Borrar Documentos':
        lista_documentos = []

    elif event == 'Generar mis claves Iniciales':
        window7 = make_win7()

    elif event == 'Cambiar mis claves':
        window8 = make_win8()

    elif event == "Cambiar Claves":
        ckp.create_keypair(1)["users"]

        sg.Popup('Se han cambiado las claves de manera exitosa')

    elif event == "Esquema MuSig":
        window2 = make_win2()

window.close()