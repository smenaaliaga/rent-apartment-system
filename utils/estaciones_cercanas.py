from haversine import haversine
import pandas as pd

metros = pd.read_csv('../scraping/output/estaciones.csv')
metros = metros.drop_duplicates()

def estaciones_cercanas(deptos):
    deptos['distancia_estacion'] = 0
    deptos['estacion_cercana'] = ""
    for i, depto in deptos.iterrows() :
        result = []
        for j, metro in metros.iterrows() :
            distance = haversine(depto.lat, depto.long, metro.lat, metro.long)
            result.append([metro.nombre, distance])
        result = pd.DataFrame(result)
        result = result[result[1] == result[1].min()]
        deptos['distancia_estacion'][i] = result.iloc[0,1]
        deptos['estacion_cercana'][i] = result.iloc[0,0]
    return deptos