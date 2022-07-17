import os


class_names = ['No raising hand', 'Raising hand']

# Model path
yolo = os.path.abspath('Models/yolo-tiny-onecls/best-model.pth')
yolo_cfg = os.path.abspath('Models/yolo-tiny-onecls/yolov3-tiny-onecls.cfg')

sppe50 = os.path.abspath('Models/sppe/fast_res50_256x192.pth')
sppe101 = os.path.abspath('Models/sppe/fast_res101_320x256.pth')

tsstg = os.path.abspath('Actionsrecognition/save/tsstg-model.pth')