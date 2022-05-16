############################
## Extract Transform Load ##
############################
import pandas as pd
import sys
sys.path.append('utils/')
from estaciones_cercanas import estaciones_cercanas
#### Carga el archivo
df = pd.read_csv('analytics/data/departamentos.csv')
print(df)
#### Conversión del tipo de dato
df['precio'] = df['precio'].astype(float)
df['gastos_comunes'] = df['gastos_comunes'].astype(float)
df['superficie_total'] = df['superficie_total'].replace(to_replace=",", value='.', regex=True)
df['superficie_total'] = df['superficie_total'].astype(float)
df['superficie_util'] = df['superficie_util'].replace(to_replace=",", value='.', regex=True)
df['superficie_util'] = df['superficie_util'].astype(float)
# Filtro de columnas no consideradas
df = df[df.columns[~df.columns.isin(['titulo','currency_symbol','search_gc','descripcion','direccion','ubicacion','url'])]]
# Se filtran columna de estación de metro cercanas, dado que se obtiene de otra manera
df = df[df.columns[~df.columns.isin(['estacion_cercana','distancia_estacion'])]]
# Si no hay valor de gasto comun, se asigna 0
df['gastos_comunes'] = df['gastos_comunes'].fillna(0)
# Agregar precio total
df['precio_total'] = df['precio'] + df['gastos_comunes']
# Si no hay valor en estacionamientos y bodegas, se asigna 0
df['estacionamientos'] = df['estacionamientos'].fillna(0)
df['bodegas'] = df['bodegas'].fillna(0)
# Se eliminan otras registros sin datos
print('==> Total de registros con NaN x columna :')
print(df.isnull().sum())
df = df.dropna()
# Función que, dada las latitudes y longitudes de los deptos, 
# devuelve el metro mas cercano a estos y su distancia en metros
df = estaciones_cercanas(df)
# Resutado final
print('==> Total de registros :', df.shape)
#### Guardar el archivo
df.to_csv('analytics/data/departamentos_clean.csv', index=False)
print('Finalizado!')