import torch
from models import vgg19
from PIL import Image
from torchvision import transforms
import gradio as gr
import cv2
import numpy as np

model_path = "pretrained_models/model_qnrf.pth"
url = "https://drive.google.com/uc?id=1nnIHPaV9RGqK8JHL645zmRvkNrahD9ru"

device = torch.device('cpu')  # device can be "cpu" or "gpu"

model = vgg19()
model.to(device)
model.load_state_dict(torch.load(model_path, device))
model.eval()


def predict(inp):
    print(type(inp))
    inp = Image.fromarray(inp.astype('uint8'), 'RGB')
    inp = transforms.ToTensor()(inp).unsqueeze(0)
    inp = inp.to(device)
    with torch.set_grad_enabled(False):
        outputs, _ = model(inp)
    count = torch.sum(outputs).item()
    vis_img = outputs[0, 0].cpu().numpy()
    # normalize density map values from 0 to 1, then map it to 0-255.
    vis_img = (vis_img - vis_img.min()) / (vis_img.max() - vis_img.min() + 1e-5)
    vis_img = (vis_img * 255).astype(np.uint8)
    vis_img = cv2.applyColorMap(vis_img, cv2.COLORMAP_JET)
    vis_img = cv2.cvtColor(vis_img, cv2.COLOR_BGR2RGB)
    return vis_img, int(count)


title = "Crowd Counting"
desc = " "
examples = [
    [],
    [],
    [],
]
inputs = gr.inputs.Image(label="Image of Crowd")
outputs = [gr.outputs.Image(label="Predicted Density Map"), gr.outputs.Label(label="Predicted Count")]
gr.Interface(fn=predict, inputs=inputs, outputs=outputs, title=title, description=desc,
             allow_flagging=False).launch()
