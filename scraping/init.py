import os 
from datetime import datetime
import time
import random

now = datetime.now()
dt_day = now.strftime("%d-%m-%Y")
dt_time = now.strftime("%d-%m-%Y %H:%M:%S")

comunas = [
    'santiago', 'las-condes', 'la-reina', 'penalolen', 'la-florida', 'providencia', 'nunoa', 'macul'
    'vitacura', 'cerro-navia', 'conchali', 'el-bosque', 'estacion-central', 'la-granja', 'la-pintana',
    'lo-prado', 'maipu', 'pedro-aguirre-cerda', 'pudahuel', 'quilicura', 'quinta-normal', 'recoleta',
    'renca', 'san-joaquin', 'san-bernardo', 'san-miguel', 'independencia', 'la-cisterna', 'huechuraba', 'cerrillos'
]

f = open('scraping/log/portalinmobiliario_' + dt_day +'.txt', "a+")
f.write("Init scraping " + dt_time + '\n')
f.close()

for comuna in comunas :
    f = open('scraping/log/portalinmobiliario_' + dt_day +'.txt', "a+")
    f.write("===> Comuna scraping : " + comuna + '\n')
    f.close()
    os.system("python3 scraping/scp_portalinmobiliario.py " + comuna) 
    sleep = random.randint(60, 180)
    time.sleep(sleep)
