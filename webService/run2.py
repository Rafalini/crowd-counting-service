import torch, torchvision
print(torch.__version__, torch.cuda.is_available())
# install detectron2: (Colab has CUDA 10.1 + torch 1.8)
# See https://detectron2.readthedocs.io/Vtutorials/install.html for instructions
# assert torch.__version__.startswith("1.8")   # need to manually install torch 1.8 if Colab changes its default version
# exit(0)  # After installation, you need to "restart runtime" in Colab. This line can also restart runtime
# Some basic setup:
# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.utils.visualizer import ColorMode

import cv2
from google.colab.patches import cv2_imshow

import os

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = os.path.join("/model/model.pth")

cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 13

predictor = DefaultPredictor(cfg)

from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

from detectron2.data.catalog import Metadata

clothes_metadata = Metadata()
clothes_metadata.set(thing_classes = ['short_sleeved_shirt', 'long_sleeved_shirt', 'short_sleeved_outwear',
                                 'long_sleeved_outwear', 'vest', 'sling', 'shorts', 'trousers', 'skirt',
                                 'short_sleeved_dress', 'long_sleeved_dress', 'vest_dress', 'sling_dress'])

for fn in uploaded.keys():
  im = cv2.imread(fn)
  outputs = predictor(im)
  v = Visualizer(im[:, :, ::-1],
                    metadata=clothes_metadata,
                    scale=0.5,
                    instance_mode=ColorMode.IMAGE_BW   # remove the colors of unsegmented pixels. This option is only available for segmentation models
      )
  out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
  cv2_imshow(out.get_image()[:, :, ::-1])

  import uuid

boxes = {}
for coordinates in outputs["instances"].to("cpu").pred_boxes:
  coordinates_array = []
  for k in coordinates:
    coordinates_array.append(int(k))

  boxes[uuid.uuid4().hex[:].upper()] = coordinates_array
for k,v in boxes.items():
  crop_img = im[v[1]:v[3], v[0]:v[2], :]
  cv2_imshow(crop_img)
