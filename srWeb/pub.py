import argparse

import cv2
import torch
import torch.backends.cudnn as cudnn
import numpy as np

from .models import NetSrcnn
from .utils import img_psnr


# Define the param
# parser = argparse.ArgumentParser()
# parser.add_argument('--weights-file', type=str, required=True)
# parser.add_argument('--image-file', type=str, required=True)
# parser.add_argument('--scale', type=int, default=3)
# args = parser.parse_args()


def handleImage(img_path, file_name):
    # Using the cuda
    cudnn.benchmark = True
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    # Define the net
    model = NetSrcnn().to(device)

    # Load the param
    model.load_state_dict(torch.load("./static/pths/best.pth"))
    model.eval()

    img = cv2.imread(img_path)

    img_width = (img.shape[1] // 4) * 4
    img_height = (img.shape[0] // 4) * 4
    # Bicubic
    img = cv2.resize(img, (img_width, img_height), interpolation=cv2.INTER_CUBIC)
    img = cv2.resize(img, (img_width // 4, img_height // 4), interpolation=cv2.INTER_CUBIC)
    img = cv2.resize(img, (img.shape[1] * 4, img.shape[0] * 4), interpolation=cv2.INTER_CUBIC)
    # cv2.imwrite("./data/" + "bicubic.bmp", img)
    b_img = img

    # SRCNN
    img = np.array(img).astype(np.float32)
    ycbcr = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    luminance = ycbcr[..., 0] / 255.
    luminance = torch.from_numpy(luminance).to(device)
    luminance = luminance.unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        preds = model(luminance).clamp(0.0, 1.0)

    psnr = img_psnr(luminance, preds)
    print('PSNR: {:.2f}'.format(psnr))

    preds = preds.mul(255.0).cpu().numpy().squeeze(0).squeeze(0)
    output = np.array([preds, ycbcr[..., 1], ycbcr[..., 2]]).transpose([1, 2, 0])
    output = cv2.cvtColor(output, cv2.COLOR_YCR_CB2BGR)
    cv2.imwrite("./static/redata/" + file_name+"_sr.bmp", output)
    return True
