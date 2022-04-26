from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd

# Instancia de Chrome
driver = webdriver.Chrome(ChromeDriverManager().install())
# DataFrame de Departamentos
df_deptos = pd.DataFrame(
    columns=['titulo', 'comuna', 'ubi_lat', 'ubi_lon', 'descripcion', 'superficie_util', 'dormitorios', 'baños', 'estacionamiento', 'bodegas', 'precio', 'fecha_publicacion' 'url'])
# URL Semilla
url = 'https://www.toctoc.com/arriendo/departamento/metropolitana/'
#comunas = ['santiago', 'las-condes', 'la-reina', 'penalolen', 'la-florida', 'providencia', 'nunoa', 'macul']
comunas = ['santiago']
for comuna in comunas :
    print('==> Iteración de comuna : ', comuna)
    # Request URL
    driver.get(url + comuna)
    # Cargar dinamica de más deptos
    for i in range(2) :
        try: 
            # Instanciar boton de carga una vez exista
            btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[@id="btnCargarMas"]'))
            )
            # Click a boton de carga
            btn.click() 
            # Esperar que se cargue la información cargada
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//li[@class="un-ress tp3"]//h3[@class="dir etc"]'))
            )
        except :
            break
    # Obtener todos los departamentos
    deptos = driver.find_elements(By.XPATH, '//li[@class="un-ress tp3"]')
    # Recorrer cada uno de los departamentos obtenidos
    for depto in deptos :
        # Obtener el link del departamento
        depto_link = depto.find_element(By.XPATH, './/a[@class="lnk-info"]')
        try :
            # Abrir el linl del usuario
            #depto_link.click()
            driver.execute_script("arguments[0].click();", depto_link)
            # Pasar a nueva pestaña
            driver.switch_to.window(driver.window_handles[1])
            # Esperar hasta que la data este disponible
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//h1[@class="tt-ficha"]'))
            )
            # Obteneción de data
            titulo = driver.find_element(By.XPATH, './/h1[@class="tt-ficha"]').text
            precio = driver.find_element(By.XPATH, './/div[@class="precio-b"]/strong').text
            precio = precio.replace('$ ', '').replace('.', '')
            ubi_lat = driver.find_element(By.XPATH, './/input[@id="h_br_lat"]').get_attribute('value')
            ubi_lon = driver.find_element(By.XPATH, './/input[@id="h_br_lon"]').get_attribute('value')
            webelement_descs = driver.find_elements(By.XPATH, './/ul[@class="list_adicional clearfix"]/li')
            descripciones = []
            for descripcion in webelement_descs :
                descripciones.append(descripcion.text)
            superficie_util = driver.find_element(By.XPATH, './/li[@class="metrosUtiles"]/strong').text
            superficie_util = superficie_util.replace(' m²', '')
            dormitorios = driver.find_element(By.XPATH, './/li[@class="dormitorios"]/strong').text
            baños = driver.find_element(By.XPATH, './/li[@class="baños"]/strong').text
            estacionamiento = driver.find_element(By.XPATH, './/li[@class="estacionamientos"]/strong').text
            bodegas = driver.find_element(By.XPATH, './/li[@class="bodegas"]/strong').text
            fecha_publicacion = driver.find_element(By.XPATH, './/li[./span[contains(text(),"publicación:")]]/strong').text
            url = driver.current_url
            dic = {
                'titulo': titulo, 
                'precio': precio, 
                'comuna' : comuna,
                'ubi_lat': ubi_lat,
                'ubi_lon' : ubi_lon,
                'descripciones' : descripciones,
                'superficie_util' : superficie_util,
                'dormitorios' : dormitorios,
                'baños' : baños,
                'estacionamiento' : estacionamiento,
                'bodegas' : bodegas,
                'fecha_publicacion' : fecha_publicacion,
                'url' : url
                }
            print('Result: ', dic)
            df_deptos = df_deptos.append(dic, ignore_index = True)
            # Cerrar pestaña
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e :
            print(e)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

# Export deptos DataFrame to JSON
df_deptos.to_json(r'scraping/output/toctoc.json', orient="records", lines = True)