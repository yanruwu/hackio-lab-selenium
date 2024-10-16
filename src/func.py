
from bs4 import BeautifulSoup



import pandas as pd
import numpy as np

from time import sleep
import re
import random as rand
from tqdm import tqdm

from selenium import webdriver  # Selenium es una herramienta para automatizar la interacción con navegadores web.
from webdriver_manager.chrome import ChromeDriverManager  # ChromeDriverManager gestiona la instalación del controlador de Chrome.
from selenium.webdriver.common.keys import Keys  # Keys es útil para simular eventos de teclado en Selenium.
from selenium.webdriver.support.ui import Select  # Select se utiliza para interactuar con elementos <select> en páginas web.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException # Excepciones comunes de selenium que nos podemos encontrar 


def get_table(table_text, headers, location):
    """
    Convierte el texto de una tabla en formato string en un DataFrame de pandas con columnas estructuradas.

    Args:
        table_text (str): El texto de la tabla con datos meteorológicos separados por saltos de línea.
        headers (list): Lista de encabezados de las columnas que serán asignados al DataFrame final.
        location (str): Ubicación geográfica relacionada con los datos de la tabla.

    Returns:
        pd.DataFrame: Un DataFrame con los datos de la tabla procesada, incluyendo columnas adicionales 
        para 'Month' y 'Location'.
    """
    table_list = table_text.split("\n")

    split_number = table_list.index('Max Avg Min')-1
    table_final = []
    for i in range(1, split_number+1):
        table_final.append(table_list[i::split_number])

    df_inicial = pd.DataFrame(table_final)
    df_final = pd.DataFrame()
    for j in range(df_inicial.shape[1]):
        df_intermedio = df_inicial[j].str.split(" ", expand=True)
        df_final = pd.concat([df_final, df_intermedio], axis=1)

    df_final.columns = df_final.iloc[0]

    month = df_final.iloc[0,0]
    newcols = [headers[0]]

    for h in headers[1:-1]:
        for i in range(1,4):
            newcols.append(re.sub(r"\(.+\)"," ",h)+df_final.columns[i])

    newcols.append("Precipitations")

    df_final.columns = newcols

    df_final.drop(index = 0, inplace = True)
    df_final.reset_index(drop = True, inplace=True)
    df_final.insert(column="Month", loc=0, value = month)
    df_final.insert(column="Location", loc=0, value = location)
    return df_final


def wait_and_click(drivers, xpath):
    """
    Espera a que un elemento esté disponible en el DOM, luego intenta hacer clic en él hasta 5 veces.

    Args:
        drivers (selenium.webdriver): El controlador de Selenium que gestiona la interacción con el navegador.
        xpath (str): La ruta xpath del elemento que se quiere encontrar y hacer clic.

    Returns:
        WebElement: El botón o elemento en el que se ha hecho clic.
    """
    tries = 0
    while True and tries < 5:
        try:
            button = WebDriverWait(drivers, 5).until(EC.presence_of_element_located(("xpath", xpath)))
            sleep(2)
            button.click()
            break
        except:
            tries += 1
            print("Try number", tries)
            continue
    return button


def tables2(tabletext, tablehtml):
    """
    Procesa el texto de una tabla y el HTML para generar un DataFrame estructurado con encabezados mejorados.

    Args:
        tabletext (str): Texto de la tabla con los datos, en formato sin procesar.
        tablehtml (str): Código HTML de la tabla que contiene los encabezados.

    Returns:
        pd.DataFrame: Un DataFrame con los datos de la tabla procesada y encabezados ajustados.
    """
    soup2 = BeautifulSoup(tablehtml, "html.parser")
    headers2 = [h.text for h in soup2.find("thead").findAll("th")]

    amounts = ["High", "Avg", "Low"]

    new_headers = []
    new_headers.append("Date")
    for h in headers2[1:5]:
        for a in amounts: 
            new_headers.append(a +" "+ h)

    for a in ["High", "Low"]:
        new_headers.append(a +" "+ headers2[5])
    new_headers.append(headers2[-1])
    table2 = tabletext.replace("°F ", "").replace("% ", "").replace("mph ", "").replace("in", "").split()
    df_table2 = pd.DataFrame(np.reshape(table2, (int(len(table2)/16),16)))
    df_table2.columns = new_headers

    return df_table2