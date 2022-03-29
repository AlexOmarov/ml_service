#для примера просто 3D график из полученных значений
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA

import numpy as np
import math


import csv
reader = csv.reader(open('data.csv'))
headers = next(reader, None)
X = list(reader)
X = np.array(X)
X = X.astype(np.float)

X_principal = pd.DataFrame(X)

X_principal.columns = ['P1', 'P2']

print(X_principal.head())

# Numpy массив всех меток кластера, назначенных каждой точке данных

db_default = DBSCAN(eps = 0.05, min_samples = 8).fit(X_principal)

labels = db_default.labels_
print(labels)
# Создание метки для сопоставления цветов

colours = {}
import matplotlib.pyplot as plt
import random

for label in labels:
    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    while colours.__contains__(color):
        color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    colours[label] = color

# Построение цветового вектора для каждой точки данных

cvec = [colours[label] for label in labels]

# Для построения легенды о сюжете
legend = []
clusters = []
i = 1
for color in colours.values():
    r = plt.scatter(X_principal['P1'], X_principal['P2'], color=color)
    legend.append(r)
    clusters.append("Кластер " + i.__str__())
    i = i + 1

# Построение P1 на оси X и P2 на оси Y
# в соответствии с определенным вектором цвета

plt.figure(figsize=(9, 9))

plt.scatter(X_principal['P1'], X_principal['P2'], c=cvec)

# Построение легенды

plt.legend(legend, clusters)

plt.show()