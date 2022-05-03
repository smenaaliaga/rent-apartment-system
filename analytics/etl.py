############################
## Extract Transform Load ##
############################
import pandas as pd
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
df = df[df.columns[~df.columns.isin(['titulo','currency_symbol','search_gc', 'descripcion','ubicacion','url'])]]
# Si no hay valor de gasto comun, se asigna 0
df['gastos_comunes'] = df['gastos_comunes'].fillna(0)
# Agregar precio total
df['total'] = df['precio'] + df['gastos_comunes']
# Si no hay valor en estacion_cercana, se asigna 'Sin estacion cercana'
df['estacion_cercana'] = df['estacion_cercana'].fillna('Sin estación cercana')
# Si la estación esta lejana, se añade 3000 mts como referencia,
# recordar que una estación cercana se considera como menor a 2000 mts 
df['distancia_estacion'] = df['distancia_estacion'].fillna(3000)
# Si no hay valor en estacionamientos y bodegas, se asigna 0
df['estacionamientos'] = df['estacionamientos'].fillna(0)
df['bodegas'] = df['bodegas'].fillna(0)
# Se eliminan otras registros sin datos
print('==> Total de registros con NaN x columna :')
print(df.isnull().sum())
df = df.dropna()
# Resutado final
print('==> Total de registros :', df.shape)
#### Guardar el archivo
df.to_csv('analytics/data/departamentos_clean.csv', index=False)
print('Finalizado!')