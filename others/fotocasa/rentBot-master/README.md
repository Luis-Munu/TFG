# rentBot - Fotocasa

#### By _**Javier Guimerans Alonso, Gerson Villalba Arana**_

### Tipología y ciclo de vida de los datos
### PRA1: Web Scraping

## Descripción

El proyecto pretende cumplir con las especificaciones detalladas para 
el cumplimiento de la práctica PRA1 de la asignatura Tipología y 
ciclo de vida de los datos de la UOC.

El proyecto consiste en la programación de un bot que, realizando 
web scraping, consiga datos de alquileres de viviendas en las ciudades 
solicitadas. 

Como fuente de datos se toma la web Fotocasa.es, web de referencia en España
para la venta y alquiler de viviendas.

Los datos obtenidos se guardarán en formato CSV en la carpeta \data.
También se realiza además un análisis exploratorio de los datos para 
comprobar su validez y la utilidad que éstos pueden tener en gran cantidad 
de aplicaciones en el área _data science_.


## Datos obtenidos

Los datos obtenidos tienen la siguiente información:

* ID Número identificativo de la vivienda.
* Precio (€/mes): Precio de la vivienda en euros mensuales.
* Tipo: Tipo de vivienda.
* Teléfono: Número de teléfono del anunciante.
* Ciudad: Ciudad donde se encuentra el inmueble.
* Dirección: Calle donde se encuentra el inmueble.
* Barrio: Barrio donde se encuentra la vivienda.
* Habitaciones: Número de habitaciones.
* Baños: Número de baños.
* Superficie (m2): Superficie de la vivienda en metros cuadrados.
* Planta: Planta donde se encuentra la vivienda.
* Ascensor: La vivienda dispone de ascensor.
* Terraza: La vivienda dispone de terraza.
* Parking: La vivienda dispone de parking.
* Calefacción: La vivienda dispone de calefacción.
* Aire: La vivienda dispone de aire acondicionado.
* Balcón: La vivienda dispone de balcón.
* Precio del m2 (€/m2): Relación entre el precio y la superficie 
de la vivienda en euros por metro cuadrado.

## Intrucciones de uso
Para descargar los datos de un conjunto de municipios, ejecutar la
siguiente instrucción en el directorio raíz:

python rentBot.py ciudad1 ciudad2 ciudad3 ...

Si alguna de las ciudades contiene algún espacio en su nombre, será
necesario escribir el nombre de la ciudad entre comillas.

Tras la ejecución del script, se guardan los datos correspondientes de las
ciudades seleccionadas en la carpeta /data con la fecha y hora en el nombre 
de archivo.

## Requesitos especiales
El script hace uso del driver "chromedriver" para realizar el web scraping, 
incluido en la carpeta /chromedriver.


## Limitaciones conocidas

* Para salvar el bloqueo por parte del servidor web, el web scraping se 
realiza con tiempos de espera, lo que provoca que la carga de datos sea
relativamente lenta.

## Datos de muestra
Los datos de muestra han sido publicados también en Zenodo.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6409348.svg)](https://doi.org/10.5281/zenodo.6409348)


## Licencia
Ver archivo LICENSE