# Импорт пакета панд

import pandas as pd

  
# создать словарь по пять полей в каждом

data = {

    'A':['A1', 'A2', 'A3', 'A4', 'A5'], 

    'B':['B1', 'B2', 'B3', 'B4', 'B5'], 

    'C':['C1', 'C2', 'C3', 'C4', 'C5'], 

    'D':['D1', 'D2', 'D3', 'D4', 'D5'], 

    'E':['E1', 'E2', 'E3', 'E4', 'E5'] }

  
# Конвертировать словарь в DataFrame

df = pd.DataFrame(data)

  
# Удалить три столбца в качестве базы индекса

df.drop(df.columns[[0, 4, 2]], axis = 1, inplace = True)

  
print(df)