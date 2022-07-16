"""
This script to extract skeleton joints position and score.

- This 'annot_folder' is a action class and bounding box for each frames that came with dataset.
    Should be in format of [frame_idx, action_cls, xmin, ymin, xmax, ymax]
        Use for crop a person to use in pose estimation model.
- If have no annotation file you can leave annot_folder = '' for use Detector model to get the
    bounding box.
"""

import os
import cv2
import time
import torch
import pandas as pd
import numpy as np

from DetectorLoader import TinyYOLOv3_onecls
from PoseEstimateLoader import SPPE_FastPose
from fn import vis_frame_fast

save_path = 'Home-pose+score.csv'

annot_file = 'Home_new.csv'  # from create_dataset_1.py
video_folder = 'Home/videos/'
annotation_folder = 'Home/annot'  # bounding box annotation for each frame.

# DETECTION MODEL.
detector = TinyYOLOv3_onecls()

# POSE MODEL.
inp_h = 320
inp_w = 256
pose_estimator = SPPE_FastPose('resnet50', inp_h, inp_w)
class_names = ['Writing', 'Raising hand', 'Turned around', 'Lie on the desk', 'Nomal']
# with score.
columns = ['video', 'frame', 'Nose_x', 'Nose_y', 'Nose_s', 'LShoulder_x', 'LShoulder_y', 'LShoulder_s',
           'RShoulder_x', 'RShoulder_y', 'RShoulder_s', 'LElbow_x', 'LElbow_y', 'LElbow_s', 'RElbow_x',
           'RElbow_y', 'RElbow_s', 'LWrist_x', 'LWrist_y', 'LWrist_s', 'RWrist_x', 'RWrist_y', 'RWrist_s',
           'LHip_x', 'LHip_y', 'LHip_s', 'RHip_x', 'RHip_y', 'RHip_s', 'LKnee_x', 'LKnee_y', 'LKnee_s',
           'RKnee_x', 'RKnee_y', 'RKnee_s', 'LAnkle_x', 'LAnkle_y', 'LAnkle_s', 'RAnkle_x', 'RAnkle_y',
           'RAnkle_s', 'label']


def normalize_points_with_size(points_xy, width, height, flip=False):
    points_xy[:, 0] /= width
    points_xy[:, 1] /= height
    if flip:
        points_xy[:, 0] = 1 - points_xy[:, 0]
    return points_xy


annot = pd.read_csv(annot_file)  # annot = [video, frame, label]
vid_list = annot['video'].unique()
for vid in vid_list:
    print(f'Process on: {vid}')
    df = pd.DataFrame(columns=columns)
    cur_row = 0

    # Pose Labels.
    frames_label = annot[annot['video'] == vid].reset_index(drop=True)

    cap = cv2.VideoCapture(os.path.join(video_folder, vid))
    frames_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    # Bounding Boxs Labels.
    annotation_file = os.path.join(annotation_folder, vid.split('.')[0] + '.txt')
    annotation = None
    if os.path.exists(annotation_file):
        annotation = pd.read_csv(annotation_file, header=None,
                                names=['frame_idx', 'class', 'xmin', 'ymin', 'xmax', 'ymax'])
        annotation = annotation.dropna().reset_index(drop=True)  # Remove missing values.
        assert frames_count == len(annotation), 'frame count not equal! {} and {}'.format(frames_count, len(annotation))

    fps_time = 0
    i = 1
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cls_idx = int(frames_label[frames_label['frame'] == i]['label'])

            if annotation:
                bb = np.array(annotation.iloc[i-1, 2:].astype(int))
            else:
                bb = detector.detect(frame)
                if bb is None:
                    bb = torch.tensor([[0, 0, 0, 0, 1.0000, 1.0000, 0.0000]])  #  [top, left, bottom, right, bbox_score, class_score, class]
                    bb = bb[0, :4].numpy().astype(int)
                else:
                    bb = bb[0, :4].numpy().astype(int)
            bb[:2] = np.maximum(0, bb[:2] - 5)
            bb[2:] = np.minimum(frame_size, bb[2:] + 5) if bb[2:].any() != 0 else bb[2:]

            result = []
            if bb.any() != 0:
                result = pose_estimator.predict(frame, torch.tensor(bb[None, ...]),
                                                torch.tensor([[1.0]]))  # image, bboxs, bboxs_scores

            if len(result) > 0:
                pt_norm = normalize_points_with_size(result[0]['keypoints'].numpy().copy(),
                                                    frame_size[0], frame_size[1])
                pt_norm = np.concatenate((pt_norm, result[0]['kp_score']), axis=1)  # pt_norm = ['keypoints', 'kp_score']

                # idx = result[0]['kp_score'] <= 0.05
                # pt_norm[idx.squeeze()] = np.nan
                row = [vid, i, *pt_norm.flatten().tolist(), cls_idx]
                scr = result[0]['kp_score'].mean()
            else:
                row = [vid, i, *[np.nan] * (13 * 3), cls_idx]
                scr = 0.0

            df.loc[cur_row] = row
            cur_row += 1

            # VISUALIZE.
            # frame = vis_frame_fast(frame, result)
            # frame = cv2.rectangle(frame, (bb[0], bb[1]), (bb[2], bb[3]), (0, 255, 0), 2)
            # frame = cv2.putText(frame, vid + '   Frame:' + str(i),
            #                     (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            # frame = cv2.putText(frame, 'Pose: {}, Score: {:.4f}'.format(class_names[cls_idx], scr),
            #                     (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            #
            # if not len(annotation_file):
            #     frame = cv2.putText(frame, 'No annotation',
            #                         (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            #
            # frame = frame[:, :, ::-1]
            # fps_time = time.time()
            i += 1

            # cv2.imshow('frame', frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            elif key & 0xFF == ord('p'):
                key = cv2.waitKey(0)
                if key & 0xFF == ord('q'):
                    break
        else:
            break

    # cap.release()
    cv2.destroyAllWindows()


    if os.path.exists(save_path):
        df.to_csv(save_path, mode='a', header=False, index=False)
    else:
        df.to_csv(save_path, mode='w', index=False)
