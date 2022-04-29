desc = 'gastos comunes 60000'
desc1 = 'el gasto comun 80000 aproximadamente'
desc2 = 'el departamento los gastos comunes son aprox 60000'

gc = 'gastos comunes'

if gc in desc2 :
    i = desc2.find(gc)
    print(i)
    print(desc2[(i-25 if i-25> 0 else 0):(i+25 if i+25< len(desc2) else len(desc2))])
