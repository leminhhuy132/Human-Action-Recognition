
"""
This script to create dataset and labels by clean off some NaN, do a normalization,
label smoothing and label weights by scores.
"""
import pickle
import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from config import class_names


main_parts = ['Nose_x', 'Nose_y', 'LShoulder_x', 'LShoulder_y', 'RShoulder_x', 'RShoulder_y', 'LElbow_x', 'LElbow_y', 'RElbow_x',
              'RElbow_y', 'LWrist_x', 'LWrist_y',  'RWrist_x', 'RWrist_y']
main_idx_parts = [0, 1, 2, 3, 4, 5, 6, -1]  # 1.5
csv_pose_file = 'Home-pose+score.csv'
save_path = 'train.pkl'

# Params.
smooth_labels_step = 8
n_frames = 30
skip_frame = 1

annot = pd.read_csv(csv_pose_file)

# Remove NaN.
idx = annot.iloc[:, 2:-1][main_parts].isna().sum(1) > 0
idx = np.where(idx)[0]
annot = annot.drop(idx)
# One-Hot Labels.
label_onehot = pd.get_dummies(annot['label'])
annot = annot.drop('label', axis=1).join(label_onehot)  # annot = [video, frame, 13, label(1 0 0 0 0 0 0)]  ...x48
cols = label_onehot.columns.values  # cols = [0, 1, 2, 3, 4, 5, 6]


def scale_pose(xy):
    """
    Normalize pose points by scale with max/min value of each pose.
    xy : (frames, parts, xy) or (parts, xy)
    """
    if xy.ndim == 2:
        xy = np.expand_dims(xy, 0)
    xy_min = np.nanmin(xy, axis=1)
    xy_max = np.nanmax(xy, axis=1)
    for i in range(xy.shape[0]):
        xy[i] = ((xy[i] - xy_min[i]) / (xy_max[i] - xy_min[i])) * 2 - 1
    return xy.squeeze()


def seq_label_smoothing(labels, max_step=10):
    steps = 0
    remain_step = 0
    target_label = 0
    active_label = 0
    start_change = 0
    max_val = np.max(labels)
    min_val = np.min(labels)
    for i in range(labels.shape[0]):
        if remain_step > 0:
            if i >= start_change:
                labels[i][active_label] = max_val * remain_step / steps
                labels[i][target_label] = max_val * (steps - remain_step) / steps \
                    if max_val * (steps - remain_step) / steps else min_val
                remain_step -= 1
            continue

        diff_index = np.where(np.argmax(labels[i:i+max_step], axis=1) - np.argmax(labels[i]) != 0)[0]
        if len(diff_index) > 0:
            start_change = i + remain_step // 2
            steps = diff_index[0]
            remain_step = steps
            target_label = np.argmax(labels[i + remain_step])
            active_label = np.argmax(labels[i])
    return labels


def graphSample(labels):
    class_num = np.zeros(len(class_names))
    labels = labels.argmax(axis=1)
    s = Counter(labels)
    for i in s:
        class_num[i] = s[i]
    idx_class = range(len(class_names))
    plt.bar(idx_class, class_num)
    plt.xticks(idx_class, class_names)

    for x, y in zip(idx_class, class_num):
        plt.text(x + 0.02, y + 0.05, '%d' % y, ha='center', va='bottom')
    plt.savefig('../Data/graph.jpg')
    plt.show()


def balance_training_data(feature, labels):
    labels = labels.argmax(axis=1)
    s = Counter(labels)
    vol = []
    for i in s:
        vol.append(s[i])
    varian()


feature_set = np.empty((0, n_frames, 14, 3))
labels_set = np.empty((0, len(cols)))
vid_list = annot['video'].unique()
for vid in vid_list:
    print(f'Process on: {vid}')
    data = annot[annot['video'] == vid].reset_index(drop=True).drop(columns='video')  # data = [frame, 13, label(binary)] ...x47

    # Label Smoothing.
    esp = 0.1
    data[cols] = data[cols] * (1 - esp) + (1 - data[cols]) * esp / (len(cols) - 1)
    data[cols] = seq_label_smoothing(data[cols].values, smooth_labels_step)

    # Separate continuous frames.
    frames = data['frame'].values
    frames_set = []
    fs = [0]
    for i in range(1, len(frames)):
        if frames[i] < frames[i-1] + 10:
            fs.append(i)
        else:
            frames_set.append(fs)
            fs = [i]
    frames_set.append(fs)

    for fs in frames_set:
        xys = data.iloc[fs, 1:-len(cols)]  # xys = [13]
        xys = xys.values.reshape(-1, 13, 3)  # xys = [[[1], [2], [3],....,[13]],.....]
        # Scale pose normalize.
        xys[:, :, :2] = scale_pose(xys[:, :, :2])  # x and y
        # Add center point.
        xys = np.concatenate((xys, np.expand_dims((xys[:, 1, :] + xys[:, 2, :]) / 2, 1)), axis=1)
        # xys = [[[1], [2], [3],....,[13], [center point]],.....]

        # Weighting main parts score.
        scr = xys[:, :, -1].copy()
        scr[:, main_idx_parts] = np.minimum(scr[:, main_idx_parts] * 1.5, 1.0)
        # ['LShoulder_s', 'RShoulder_s', 'LHip_s', 'RHip_s', 'center point']

        # Mean score.
        scr = scr.mean(1)

        # Targets.
        lb = data.iloc[fs, -len(cols):].values
        # Apply points score mean to all labels.
        lb = lb * scr[:, None]

        for i in range(xys.shape[0] - n_frames):  # xys > n_frames = 30
            feature_set = np.append(feature_set, xys[i:i+n_frames][None, ...], axis=0)
            labels_set = np.append(labels_set, lb[i:i+n_frames].mean(0)[None, ...], axis=0)

    # with open(save_path, 'wb') as f:
    #     pickle.dump((feature_set, labels_set), f)
xtrain, xtest,ytrain, ytest = train_test_split(feature_set, labels_set, train_size=0.7)
with open('../Data/train07.pkl', 'wb') as f:
    pickle.dump((xtrain, ytrain), f)
with open('../Data/test03.pkl', 'wb') as f:
    pickle.dump((xtest, ytest), f)
graphSample(labels_set)

