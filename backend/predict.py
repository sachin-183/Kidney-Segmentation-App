import torch
import cv2
import numpy as np
import segmentation_models_pytorch as smp

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = smp.UnetPlusPlus(
    encoder_name="resnet34",
    encoder_weights=None,
    in_channels=3,
    classes=1
)

checkpoint = torch.load("../model/unetpp_best.pth", map_location=device)

model.load_state_dict(checkpoint["model_state_dict"])
model.to(device)
model.eval()


def predict(image):

    original = image.copy()

    img = cv2.resize(image,(512,512))
    img = img/255.0

    img = np.transpose(img,(2,0,1))
    img = torch.tensor(img).unsqueeze(0).float().to(device)

    with torch.no_grad():
        output = model(img)

    mask = torch.sigmoid(output)
    mask = (mask > 0.5).float()

    mask = mask.squeeze().cpu().numpy()

    # resize mask to original size
    mask = cv2.resize(mask,(original.shape[1],original.shape[0]))

    mask = (mask*255).astype(np.uint8)

    # overlay
    overlay = original.copy()
    overlay[mask>127] = [0,0,255]

    # convert mask to 3 channel for visualization
    mask_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # resize images for display
    h, w = 400, 400
    original_disp = cv2.resize(original, (w, h))
    mask_disp = cv2.resize(mask_color, (w, h))
    overlay_disp = cv2.resize(overlay, (w, h))

    # Gap sizes and text bar
    gap = 20
    top_bar = 50
    border = 2 # Add a thin border like in the user's example
    
    # Create white background canvas
    # Total width: 3*w + 4*gap
    # Total height: h + top_bar + 2*gap
    bg_w = 3 * w + 4 * gap
    bg_h = h + top_bar + 2 * gap
    canvas = np.full((bg_h, bg_w, 3), 255, dtype=np.uint8)
    
    # Add an outer black frame to the whole canvas
    cv2.rectangle(canvas, (0, 0), (bg_w - 1, bg_h - 1), (0, 0, 0), border)

    # Put images into canvas
    y_offset = top_bar + gap
    canvas[y_offset : y_offset + h, gap : gap + w] = original_disp
    canvas[y_offset : y_offset + h, 2 * gap + w : 2 * gap + 2 * w] = mask_disp
    canvas[y_offset : y_offset + h, 3 * gap + 2 * w : 3 * gap + 3 * w] = overlay_disp
    
    # Add borders around each image panel
    for i in range(3):
        x_start = gap + i * (w + gap)
        cv2.rectangle(canvas, (x_start - border, y_offset - border), 
                      (x_start + w + border - 1, y_offset + h + border - 1), (0, 0, 0), border)
    
    # Put text into canvas
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (0, 0, 0)
    thickness = 2
    
    titles = ["Original", "Prediction Mask", "Overlay"]
    for i, title in enumerate(titles):
        (text_width, text_height), _ = cv2.getTextSize(title, font, font_scale, thickness)
        # Center of each panel
        center_x = gap + i * (w + gap) + w // 2
        
        x = center_x - text_width // 2
        y = top_bar # adjust vertical alignment
        cv2.putText(canvas, title, (x, y), font, font_scale, font_color, thickness)

    return canvas