# Práctica 1 - Web scraping 

## Descripción de la práctica

Consiste en la obtención de un dataset extraído de la página del programa SEER (The Surveillance, Epidemiology, and End Results) con la evolución histórica de los tipos de cáncer más importantes a través de técnicas de web scraping con un programa escrito en python.

## Miembros del equipo

* Alfredo Rubio Navarro
* Gabriel Loja Rodas

## Descripción de los ficheros

**src/query.py** : realiza la recoleción de los datos al fichero csv

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3749385.svg)](https://doi.org/10.5281/zenodo.3749385)  
**csv/evolucionCancer.csv** : fichero generado con los datos desglosados por raza y sexo de los principales tipos de cáncer
**csv/evolucionCancerTotales.csv** : fichero generado con los datos totalizados (para todos los tipos de cáncer) desglosado

**pdf/preguntas.pdf** : contiene las respuestas a las preguntas de la práctica

## Guía de uso:
`query.py [-t] [-a año] [-s] [-r] [-f ARCHIVO] [-h]`  

  -t : recoge solo el total de todos los tipos de cáncer, si no se indica desglosa por tipos  
  -a año : año del dataset (1975-2016), si no se indica se registran todos  
  -s : desglosa el dataset por sexo  
  -r : desglosa el dataset por raza  
  -f ARCHIVO : nombre del archivo de salida SIN extensión, por defecto es 'evolucionCancer'  
  -h : imprime la ayuda  

El programa requiere la versión 3 de python.
