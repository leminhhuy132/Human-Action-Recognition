import numpy as np
import pandas as pd
import random
from collections import Counter

pose_file = 'bth_pose.csv'

annot = pd.read_csv(pose_file)
# Remove NaN.
idx = annot.iloc[:, 2:-1].isna().sum(1) > 0
idx = np.where(idx)[0]
annot = annot.drop(idx)

labels = annot['label']
s = Counter(labels)
print(s)


idx = random.sample(annot[annot['label'] == 5].index.tolist(), k=10000)
annot = annot.drop(index=idx)

for i in range(4):
    annot = annot.append(annot[annot['label'] == 3])

labels = annot['label']
s = Counter(labels)
print(s)

# file_name = str(pose_file.split('.')[0]) + '_balance.csv'
# annot.to_csv(pose_file, mode='w', index=False)