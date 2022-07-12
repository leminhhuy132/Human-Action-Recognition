
# mode = ['examination', 'study']
mode = 'study'

# class
if mode == 'study':
    class_names = ['Writing', 'Raising hand', 'Turned around', 'Lie on the desk', 'Nomal']
elif mode == 'examination':
    class_names = ['Turned around', 'Document exchange', 'Nomal']

# Model path
yolo = '/home/minhhuy/Desktop/Python/Human-Falling-Detect-Tracks/Models/yolo-tiny-onecls/best-model.pth'
yolo_cfg = '/home/minhhuy/Desktop/Python/Human-Falling-Detect-Tracks/Models/yolo-tiny-onecls/yolov3-tiny-onecls.cfg'

sppe50 = '/home/minhhuy/Desktop/Python/Human-Falling-Detect-Tracks/Models/sppe/fast_res50_256x192.pth'
sppe101 = '/home/minhhuy/Desktop/Python/Human-Falling-Detect-Tracks/Models/sppe/fast_res101_320x256.pth'

tsstg = '/home/minhhuy/Desktop/Python/Human-Falling-Detect-Tracks/Models/TSSTG/tsstg-model.pth'