import requests
from bs4 import BeautifulSoup
import re
import csv
import sys



#-----------------------------------------------------------------------------#

"""
    Muestra por pantalla la ayuda
"""
def ayuda():
    print("Uso: query [-t] [-a año] [-s] [-r] [-f ARCHIVO] [-h] ")
    print(" -t              recoge solo el total de todos los tipos de cáncer, si no se indica desglosa por tipos")
    print(" -a año          año del dataset (1975-2016), si no se indica se registran todos ")
    print(" -s              desglosa el dataset por sexo")
    print(" -r              desglosa el dataset por raza")
    print(" -f ARCHIVO      nombre del archivo de salida SIN extensión, por defecto es 'evolucionCancer'")
    print(" -h              imprime la ayuda")


#-----------------------------------------------------------------------------#


"""
    Parsea los parámetros pasados al comando en la línea de comandos
    Salida:
        Objeto de tipo diciconario con los parámetros procesados
"""
def recoge_parametros():

    # valores por defecto
    parametros = {"totales" : False,
                  "año" : 0, # todos los años
                  "raza" : False, 
                  "sexo" : False,
                  "fichero" : "evolucionCancer" }

    total_parametros = len(sys.argv)
    # el primer parámetro es el propio programa, empezamos por el segundo
    num_parametro = 2

    while num_parametro <= total_parametros:
        parametro = sys.argv[num_parametro-1]

        # solo totales
        if parametro == '-t':
            num_parametro += 1
            parametros['totales'] = True
        # raza
        elif parametro == '-r':
            num_parametro += 1
            parametros['raza'] = True

        # sexo 
        elif parametro == '-s':
            num_parametro += 1
            parametros['sexo'] = True

        # archivo de salida            
        elif parametro == '-a':
            try:
                año = sys.argv[num_parametro]
            except IndexError:
                # no hay más parámetros, falta el año
                print("No se ha indicado el año del dataset.")
                exit(0)

            if año.startswith('-'):
                # hay más parámetros pero no se ha indicado el año
                print("No se ha indicado el año del dataset.")
                exit(0)

            try:
                año = int(año)
            except ValueError:
                # el dato con el año no es un número entero válido
                print("El año del dataset no es válido.")
                exit(0)

            if año < 1975 or año > 2016:
                print("El año debe estar dentro de los valores válidos (1975-2016).")
                exit(0)

            parametros['año'] = año
            num_parametro += 2

        elif parametro == '-f':
            try:
                fichero = sys.argv[num_parametro]
            except IndexError:
                # falta el dato con el nombre del fichero
                print("No se ha indicado el nombre del archivo de salida.")
                exit(0)

            if fichero.startswith('-'):
                # hay más parámetros pero no se proporciona el nombre del fichero
                print("No se ha indicado el nombre del archivo de salida.")
                exit(0)

            # comprobamos que el nombre del fichero es válido
            caracteres_no_validos = re.findall(r'[^A-Za-z0-9_\-]',fichero)
            if len(caracteres_no_validos) > 0:
                print("El nombre del fichero no es válido.")
                exit(0)

            parametros['fichero'] = fichero
            num_parametro += 2

        elif parametro == '-h' or parametros == '-?':
            ayuda()
            exit(0)
        else:
            # parametro no reconocido
            print("Parámetro desconocido: %s" % parametro)
            ayuda()
            exit(0)

    return parametros


#-----------------------------------------------------------------------------#


"""
    Convertimos una lista en una cadena de caracteres
    Entrada:
        lista: Lista a convertir
        separador: cadena para dividir los elementos de la lista, por defecto está vacia
    Salida:
        cadena convertida
"""
def lista_a_cadena(lista, separador = ''):

    cadena = ''

    if type(lista) != list or type(separador) != str:
        # datos de entrada no válidos
        return cadena

    for item in lista:
        if len(cadena) > 0 and len(separador) > 0:
            cadena += separador
        cadena += str(item)

    return cadena


#-----------------------------------------------------------------------------#

"""
    Genera la query para la tasa de nuevos casos que añadimos a la URL con las variables
    que filtan los datos de la consulta.
    Entrada:
        paramatros: diccionario con los parámetros pasados por línea de comandos
    Salida:
        String con la query resultante
"""
def procesa_parametros_casos(parametros):


    # Basándonos en las querys que generan las distintas consultas identificamos las variables que son necesarias.
    # La página utiliza el acento circunflejo (^) para separar elementos dentro de cada variable
    # La variables representativas son:
    # dir/db: 
    #   'seer2016' / '1'   para la base de datos con las tasas de nuevos casos
    #   'usmort2016' / '7' para la base de datos con las tasas de mortalidad
    # sel:  
    #   Es una lista con las distintas opciones de selección y filtrado de los datos a mostrar.
    # x: variables para el desglose de las filas
    # y: variables para el desglose de las columnas
    # dec: el número de decimales a mostrar

    # por defecto los años a mostrar son todos (1975-2016)
    años = lista_a_cadena(list(range(6,48)), ',')

    if parametros['totales']:
        tipos = '0'
    else:
        # seleccionamos solo los tipos de cáncer principales y que aparecen el ambas bases de datos
        tipos = '2,3,4,5,6,7,8,9,10,11,13,14,15,16,30,31,34,35,36,37,38,39,41,42,43,44,45,46,47,48,51,52,61,66,71,72,75,78,85,86,101'

        """
        2.  Lip
        3.  Tongue
        4.  Salivary Gland
        5.  Floor of Mouth
        6.  Gum and Other Mouth
        7.  Nasopharynx
        8.  Tonsil
        9.  Oropharynx
        10. Hypopharynx
        11. Other Oral Cavity and Pharynx
        13. Esophagus
        14. Stomach
        15. Small Intestine
        16. Colon and Rectum
        30. Anus, Anal Canal and Anorectum
        31. Liver and Intrahepatic Bile Duct
        34. Gallbladder
        35. Other Biliary
        36. Pancreas
        37. Retroperitoneum
        38. Peritoneum, Omentum and Mesentery
        39. Other Digestive Organs
        41. Nose, Nasal Cavity and Middle Ear
        42. Larynx
        43. Lung and Bronchus
        44. Pleura
        45. Trachea, Mediastinum and Other Respiratory Organs
        46. Bones and Joints
        47. Soft Tissue including Heart
        48. Skin
        51. Breast
        52. Female Genital System
        61. Male Genital System
        66. Urinary System
        71. Eye and Orbit
        72. Brain and Other Nervous System
        75- Endocrine System
        78. Lymphoma
        85. Myeloma
        86. Leukemia
        101. Miscellaneous Malignant Cancer
        """

    x_lst = []
    y_lst = []        

    if parametros['año'] == 0 and not parametros['totales']:
        x_lst.append('Site^' + tipos)
        x_lst.append('Year of diagnosis^' + años)
    elif parametros['año'] == 0 and parametros['totales']:
        x_lst.append('Year of diagnosis^' + años)
    elif parametros['año'] != 0 and parametros['totales']:
        pass
    else: # parametros['año'] != 0 and not parametros['totales']
        x_lst.append('Site^' + tipos)

    if parametros['año'] == 0:
        año = años
    else:    
        año = str(parametros['año'] - 1969)

    if parametros['raza']:
        raza = '1,2'
        y_lst.append('Race^1,2')
    else:
        raza = '0'

    if parametros['sexo']:
        sexo = '1,2'
        y_lst.append('Sex^1,2')
    else:
        sexo = '0'

    y_str = lista_a_cadena(y_lst, '^')
    x_str = lista_a_cadena(x_lst, '^')

    sel_lst = ['1', '0', '0', tipos, año, raza, sexo, '0' ]

    sel_str = lista_a_cadena(sel_lst, '^')

    query_dict = { 
        'dir' : 'seer2016',
        'db' : '1',
        'rpt' : 'TAB',
        'sel' : sel_str,
        'y' : y_str,
        'x' : x_str,
        'dec' : '2,2,2',
        'template' : 'null'
        }

    query_str = ''
    for clave, valor in query_dict.items():
        if query_str != '':
            query_str += '&'
        query_str += clave + "=" + valor

    return query_str


#-----------------------------------------------------------------------------#

"""
    Genera la query para las tasas de mortalidad que añadimos a la URL con las variables
    que filtan los datos de la consulta.
    Entrada:
        paramatros: diccionario con los parámetros pasados por línea de comandos
    Salida:
        String con la query resultante
"""
def procesa_parametros_muertes(parametros):


    años = lista_a_cadena(list(range(16,58)), ',')

    if parametros['totales']:
        tipos = '1'
    else:
        # seleccionamos solo los tipos de cáncer principales y que aparecen el ambas bases de datos
        tipos =  '3,4,5,6,7,8,9,10,11,12,14,15,16,17,20,21,24,25,26,27,28,29,31,32,33,34,35,36,37,38,41,42,51,56,61,62,63,66,69,70,83'
        """
        3.  Lip
        4.  Tongue
        5.  Salivary Gland
        6.  Floor of Mouth
        7.  Gum and Other Mouth
        8.  Nasopharynx
        9.  Tonsil
        10. Oropharynx
        11. Hypopharynx
        12. Other Oral Cavity and Pharynx
        13. Esophagus
        15. Stomach
        16. Small Intestine
        17. Colon and Rectum
        20. Anus, Anal Canal and Anorectum
        21. Liver and Intrahepatic Bile Duct
        24. Gallbladder
        25. Other Biliary
        26. Pancreas
        27. Retroperitoneum
        28. Peritoneum, Omentum and Mesentery
        29. Other Digestive Organs
        31. Nose, Nasal Cavity and Middle Ear
        32. Larynx
        33. Lung and Bronchus
        34. Pleura
        35. Trachea, Mediastinum and Other Respiratory Organs
        36. Bones and Joints
        37. Soft Tissue including Heart
        38. Skin
        41. Breast
        42. Female Genital System
        51. Male Genital System
        56. Urinary System
        61. Eye and Orbit
        62. Brain and Other Nervous System
        63- Endocrine System
        66. Lymphoma
        69. Myeloma
        70. Leukemia
        83. Miscellaneous Malignant Cancer
        """

    x_lst = []
    y_lst = []        

    if parametros['año'] == 0 and not parametros['totales']:
        x_lst.append('Site^' + tipos)
        x_lst.append('Year of death^' + años)
    elif parametros['año'] == 0 and parametros['totales']:
        x_lst.append('Year of death^' + años)
    elif parametros['año'] != 0 and parametros['totales']:
        pass
    else: # parametros['año'] != 0 and not parametros['totales']
        x_lst.append('Site^' + tipos)

    if parametros['año'] == 0:
        año = años
    else:    
        año = str(parametros['año'] - 1959)

    if parametros['raza']:
        raza = '1,2'
        y_lst.append('Race^1,2')
    else:
        raza = '0'

    if parametros['sexo']:
        sexo = '1,2'
        y_lst.append('Sex^1,2')
    else:
        sexo = '0'

    y_str = lista_a_cadena(y_lst, '^')
    x_str = lista_a_cadena(x_lst, '^')

    sel_lst = ['1', '0', tipos, año, raza, sexo, '0' ]

    sel_str = lista_a_cadena(sel_lst, '^')

    query_dict = { 
        'dir' : 'usmort2016',
        'db' : '7',
        'rpt' : 'TAB',
        'sel' : sel_str,
        'y' : y_str,
        'x' : x_str,
        'dec' : '2,2,2',
        'template' : 'null'
        }

    query_str = ''
    for clave, valor in query_dict.items():
        if query_str != '':
            query_str += '&'
        query_str += clave + "=" + valor

    return query_str


#-----------------------------------------------------------------------------#

"""
    Unifica en un solo diccionario los dos pasados como parámetros
    Si hay claves duplicadas, se asigna el valor del segundo diccionario
    Entrada: diccionarios a fusionar
    Salida: el diccinario resultante
"""
def fusionar_diccionarios(x_dict, y_dict):
    z_dict = x_dict.copy()
    z_dict.update(y_dict)
    return z_dict

#-----------------------------------------------------------------------------#


"""
    Extraemos los datos de la url pasada como parámetro
    Entrada:
        - url: la dirección completa de donde extraer los datos
        - parametros: la lista con los parámetros suministados al programa
        - campos: la lista con los campos de las variables a extraer
    Salida:
        Lista con los registros extraidos, cada elemento de la lista es un diccionario
"""
def consulta_web(url, parametros, campos):

    lista_resultado = []

    # definimos la identificación del agente 
    firefox = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0'
    headers = {'user-agent': firefox}

    try:
        pagina = requests.get(url, headers=headers, timeout=5)
    except requests.exceptions.Timeout:
        print("Tiempo de espera agotado, abortamos la extracción.")
        exit(0)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    # usamos el parser 'html5lib' por que aunque es más lento, arregla el html cuando faltan etiquetas de inicio o final
    soup = BeautifulSoup(pagina.content, 'html5lib') 

    try:
        tabla = soup.find("table", summary="Prevalence statistics")
        filas = tabla.find_all("tr")
    except AttributeError:
        print("No se han encontrado datos en la página.")
        return []

    if filas == None or len(filas) == 0:
        print("No se han encontrado datos para extraer.")
        return []

    # valores iniciales por defecto
    tipo_cancer = ""
    año = 0

    for fila in filas:

        # saltamos las cabeceras
        if fila.parent.name == 'thead':
            continue

        # inicializamos el dicionario que almacenrá los registros a grabar en el fichero csv
        registro = {}

        try:

            if parametros['año'] == 0 and not parametros['totales']:
                th0 = fila.find("th", class_="th0")              
                th1 = fila.find("th", class_="th1")
                if th0 != None:
                    tipo_cancer = th0.string
                if th1 != None:
                    año = th1.string

                registro['tipo_cancer'] = tipo_cancer
                registro['año'] = año                  

            elif parametros['año'] == 0 and parametros['totales']:
                th0 = fila.find("th", class_="th0")
                if th0 != None:
                    año = th0.string

                registro['año'] = año

            elif parametros['año'] != 0 and parametros['totales']:
                año = parametros['año']
                registro['año'] = año

            else: # parametros['año'] != 0 and not parametros['totales']
                año = parametros['año']
                th0 = fila.find("th", class_="th0")
                if th0 != None:
                    tipo_cancer = th0.string

                registro['tipo_cancer'] = tipo_cancer
                registro['año'] = año


            columnas = fila.find_all("td")

        except AttributeError:
            print("No se han encontrado datos el la fila para extraer, pasamos a la siguiente")
            continue
           
        if len(columnas) == 0:
            print("No se han encontrado datos el la fila para extraer, pasamos a la siguiente")
            continue

        for pos_item in range(len(columnas)):
            if columnas[pos_item].string !=  None and columnas[pos_item].string != '':
                try:
                    registro[campos[pos_item]] = float(columnas[pos_item].string)
                except ValueError:
                    pass

        lista_resultado.append(registro)


    return lista_resultado


#-----------------------------------------------------------------------------#





""" 
    Rutina principal
"""
def run():

    # lista con los nombres de las variables comunes a los dos registros:
    # - el tipo de cáncer 
    # - el año, en el caso de que no se especifique
    campos = []

    # lista con los campos relativos a las variables de los nuevos casos
    campos_casos = []
    # lista con los campos relativos a las variables de los fallecimientos
    campos_muertes = []

    # obrenemos los parámetros pasados el la línea de comandos
    parametros = recoge_parametros()

    print("Parámetros: ")
    print("  Solo totales........", end='')
    print("si" if parametros['totales'] else "no")
    print("  Año extracción......", end='')
    print("todos (1975-2016)" if parametros['año'] == 0 else parametros['año'])
    print("  Separar por raza....", end='')
    print("si" if parametros['raza'] else "no")
    print("  Separar por sexo....", end='')
    print("si" if parametros['sexo'] else "no")
    print("  Fichero de salida..." + parametros['fichero'] + ".csv")
    print()


    if parametros['año'] == 0 and not parametros['totales']:
        campos.append('tipo_cancer')
        campos.append('año')          
    elif parametros['año'] == 0 and parametros['totales']:
        campos.append('año')
    elif parametros['año'] != 0 and parametros['totales']:
        campos.append('año')
    else: # parametros['año'] != 0 and not parametros['totales']
        campos.append('tipo_cancer')
        campos.append('año')


    if parametros['raza'] and parametros['sexo']:
        campos_casos = ['casos_hombre_raza_blanca', 'casos_mujer_raza_blanca', 'casos_hombre_raza_negra', 'casos_mujer_raza_negra']
        campos_muertes = ['muertes_hombre_raza_blanca', 'muertes_mujer_raza_blanca', 'muertes_hombre_raza_negra', 'muertes_mujer_raza_negra']
        
    elif parametros['raza'] and not parametros['sexo']:
        campos_casos = ['casos_raza_blanca', 'casos_raza_negra']
        campos_muertes = ['muertes_raza_blanca', 'muertes_raza_negra']

    elif not parametros['raza'] and parametros['sexo']:
        campos_casos = ['casos_hombre', 'casos_mujer']
        campos_muertes = ['muertes_hombre', 'muertes_mujer']

    else:
        campos_casos =  ['casos_todas_razas_y_sexos']
        campos_muertes = ['muertes_todas_razas_y_sexos']

    # url principal del sitio
    inicio = 'https://canques.seer.cancer.gov/cgi-bin/cq_submit?'

    # transformamos los parámetos en una cadena que añadimos a la url 
    print("Generamos query consulta tasa nuevos casos....", end='')
    consulta_casos = procesa_parametros_casos(parametros)
    print("OK")

    print("Generamos query consulta tasa fallecimientos....", end='')
    consulta_muertes = procesa_parametros_muertes(parametros)
    print("OK")


    # lista con los registros obtenidos de cada una de las consultas
    print("Obteniendo datos nuevos casos....", end='')
    lista_casos = consulta_web(inicio + consulta_casos, parametros, campos_casos)
    print("OK" if len(lista_casos) > 0 else "Error")

    print("Obteniendo datos fallecimientos....", end='')
    lista_muertes = consulta_web(inicio + consulta_muertes, parametros, campos_muertes)
    print("OK" if len(lista_muertes) > 0 else "Error")

    # unimos todos los campos para grabar el registro
    campos_totales = campos + campos_casos + campos_muertes

    # volcamos los datos al fichero csv
    with open(parametros['fichero'] + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos_totales)
        writer.writeheader()

        # comprobamos que la longitud de ambas consultas, casos y muertes es la misma
        if len(lista_casos) != len(lista_muertes):
            print("Los datos de las consultas de casos y muertes no coinciden")
            return

        print("Grabamos datos en fichero....", end='')
        for num_registro in range(0,len(lista_casos)):
            registro_final =  fusionar_diccionarios(lista_casos[num_registro], lista_muertes[num_registro])
            # registramos los datos en el fichero
            writer.writerow(registro_final)
        print("OK")


#-----------------------------------------------------------------------------#


if __name__ == "__main__":
    run()


