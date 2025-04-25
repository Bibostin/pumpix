import cv2
from PIL import Image
import numpy as np

# 8 neighbor filter kernel
n8 = np.array([[1, 1, 1],
               [1, 1, 1],
               [1, 1, 1]],
              np.uint8)

# 4 neighbor filter kernel
n4 = np.array([[0, 1, 0],
               [1, 1, 1],
               [0, 1, 0]],
              np.uint8)

def rasterise(
        src, k=3, scale=2,  blur=0,
        erode=0, saturation=0, contrast=0,
        color=True, alpha=True
    ):

    # Most images have a colour mode that pillow can determine:
    # Luminance (L) - each pixels shade (greyscale is one 8 bit int (0-256)
    # Pallette images (P) - each pixels colour is one 8 bit int
    # Red Green Blue (RGB - each pixels colour is three 8 bit ints
    # Red Green Blue Alpha (RGBA) - RGB, but with a additional int for opacity

    # if we are working with an alpha parsable image, check the image is RGBA or P
    # if its a P  it doesn't have an alpha channel, and must be converted to RGBA
    img_pillow = Image.open(src)
    if (img_pillow.mode == 'RGBA' or img_pillow.mode == 'P'):
        if img_pillow.mode != 'RGBA':
            img_pillow = img_pillow.convert('RGBA')
        alpha_mode = True
    # Otherwise if we aren't preserving alpha if the image isnt RGB, or L
    # convert it to RGB to ensure a standard input.
    elif img_pillow.mode != 'RGB' and img_pillow.mode != 'L':
        img_pillow = img_pillow.convert('RGB')
        alpha_mode = False
    # otherwise we have an RGB / L image and can proceed
    else:
        alpha_mode = False

    # In this section we translate our image data into a format that is easier
    # to work with using cv2.

    # if we are working with a opaque image (RGBA) and want to preserve its alpha
    # extract it seperately, then convert the image to RGB
    img = np.asarray(img_pillow)
    if color and alpha_mode:
        a = img[:, :, 3]
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        h, w, c = img.shape
    # If we only have color, ignore alpha and go straight to the required structure.
    elif color:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
    # otherwise this is is an L image, pull colour and set it to 0 hard.
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        h, w = img.shape
        c = 0
    # increase the saturation of the image
    if saturation in [1.5, 2.0, 2.5]:
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        hsv[..., 1] = np.clip(hsv[..., 1] * saturation, 0, 255)
        img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    # increase the contrast of the image
    if contrast in [1.25, 1.5]:
        img = cv2.convertScaleAbs(img, alpha=contrast, beta=0)
    # make the edges of the image more pronounced
    if erode == 1:
        img = cv2.erode(img, n4, iterations=1)
    elif erode == 2:
        img = cv2.erode(img, n8, iterations=1)
    # Smooth the overal nosie in the image to make it look cleaner
    if blur in [50, 100, 200]:
        img = cv2.bilateralFilter(img, 15, blur, 20)

    # scale the image down by a scale factor that corrolates to desired pixel
    # size, with alpha scaled if needed.
    d_h = int(h / scale)
    d_w = int(w / scale)
    img = cv2.resize(img, (d_w, d_h), interpolation=cv2.INTER_NEAREST)
    if alpha_mode:
        a = cv2.resize(a, (d_w, d_h), interpolation=cv2.INTER_NEAREST)

    if color:
        img_cp = img.reshape(-1, c)
    else:
        img_cp = img.reshape(-1)
    img_cp = img_cp.astype(np.float32)

    # perform k-means clustering on the image data to determine which colours
    # are the most prominent. Where the max no. of colours is k.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(img_cp, k, None, criteria, 10, cv2.KMEANS_PP_CENTERS)
    center = center.astype(np.uint8)
    result = center[label.flatten()]
    result = result.reshape((img.shape))

    # Scale back up to the original image size, with alpha scaled + merged if needed
    result = cv2.resize(result, (d_w * scale, d_h * scale), interpolation=cv2.INTER_NEAREST)
    if alpha_mode:
        a = cv2.resize(a, (d_w * scale, d_h * scale), interpolation=cv2.INTER_NEAREST)
        r, g, b = cv2.split(result)
        result = cv2.merge((r, g, b, a))

    # iterate through each cluster color, and genereate a RGB hexcode.
    colors = []
    for res_c in center:
        color_code = '#{0:02x}{1:02x}{2:02x}'.format(res_c[2], res_c[1], res_c[0])
        colors.append(color_code)

    return result, colors
