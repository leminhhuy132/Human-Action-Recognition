"""
This script to create .csv videos frames action annotation file.

- It will play a video frame by frame control the flow by [a] and [d]
 to play previos or next frame.
- Open the annot_file (.csv) and label each frame of video with number
 of action class.
"""
#unset SESSION_MANAGER
import os
import cv2
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import class_names, mode
from fn import vis_frame_fast
import torch


columns = ['video', 'frame', 'Nose_x', 'Nose_y', 'Nose_s', 'LShoulder_x', 'LShoulder_y', 'LShoulder_s',
           'RShoulder_x', 'RShoulder_y', 'RShoulder_s', 'LElbow_x', 'LElbow_y', 'LElbow_s', 'RElbow_x',
           'RElbow_y', 'RElbow_s', 'LWrist_x', 'LWrist_y', 'LWrist_s', 'RWrist_x', 'RWrist_y', 'RWrist_s',
           'LHip_x', 'LHip_y', 'LHip_s', 'RHip_x', 'RHip_y', 'RHip_s', 'LKnee_x', 'LKnee_y', 'LKnee_s',
           'RKnee_x', 'RKnee_y', 'RKnee_s', 'LAnkle_x', 'LAnkle_y', 'LAnkle_s', 'RAnkle_x', 'RAnkle_y',
           'RAnkle_s', 'label']

video_folder = 'Home/videos/bth'
pose_file = 'bth_pose.csv'

file_name = str(pose_file.split('.')[0]) + '_check.csv'
if os.path.exists(file_name):
    os.remove(file_name)

annot = pd.read_csv(pose_file)
# Remove NaN.
idx = annot.iloc[:, 2:-1].isna().sum(1) > 0
idx = np.where(idx)[0]
annot = annot.drop(idx)

video_list = annot.iloc[:, 0].unique()
print(video_list)

index_video_to_play = 0
while index_video_to_play < len(video_list):
    video_file = os.path.join(video_folder, video_list[index_video_to_play])
    print(os.path.basename(video_file))

    annot_2 = annot[annot['video'] == video_list[index_video_to_play]].reset_index(drop=True)
    frames_idx = annot_2.iloc[:, 1].tolist()
    label = annot_2.iloc[:, -1].tolist()
    result = annot_2.iloc[:, 2:41]
    video = annot_2.iloc[:, 0].tolist()

    cap = cv2.VideoCapture(video_file)
    i = 0
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frames_idx[i])
        ret, frame = cap.read()
        h, w, _ = frame.shape
        if ret:
            cls_name = class_names[label[i]]
            result_i = result.iloc[i]

            xys = result_i.values.reshape(13, 3)
            xy = torch.tensor(xys[:, 0:2]*[w, h])
            scr = xys[:, -1].copy().reshape(len(xys[:, -1]), 1)
            scr = torch.tensor(scr)
            result_i = [{'keypoints': xy, 'kp_score': scr}]

            frame = vis_frame_fast(frame, result_i)

            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.putText(frame, 'Videos: {}     Total_frames: {}        Frame: {}       Pose: {} '.format(
                video_list[index_video_to_play], len(result), frames_idx[i], cls_name),
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2)
            cv2.imshow('frame', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'):  # back frame
                i -= 1

            elif key == ord('d'):  # next frame
                i += 1
                if len(frames_idx) == i:
                    break
            elif key == ord('f'):  # next and delete frame
                video.pop(i)
                frames_idx.pop(i)

                result = result.drop(index=i)
                label.pop(i)
                i += 1
                if len(frames_idx) == i:
                    break
        else:
            break
    index_video_to_play += 1

    cap.release()
    cv2.destroyAllWindows()

    data = np.concatenate((np.reshape(video, (len(video), 1)), np.reshape(frames_idx, (len(frames_idx), 1)), result, np.reshape(label, (len(label), 1))), axis=1)
    print(data)
    df = pd.DataFrame(columns=columns, data=data)
    if os.path.exists(file_name):
        df.to_csv(file_name, mode='a', header=False, index=False)
    else:
        df.to_csv(file_name, mode='w', index=False)

