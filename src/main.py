# importing some useful packages
# type:ignore
import matplotlib.pyplot as plt
# type:ignore
import matplotlib.image as mpimg
# type:ignore
import numpy as np
# type:ignore
import cv2
import math
import os
import shutil
from moviepy.editor import VideoFileClip

#################################


# reading in an image
image = mpimg.imread('test_images/solidWhiteRight.jpg')


# printing out some stats and plotting
# print('This image is:', type(image), 'with dimensions:', image.shape)
# plt.imshow(
#    image)  # if you wanted to show a single color channel image called 'gray', for example, call as plt.imshow(gray, cmap='gray')


#################################


def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)


def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def region_of_interest(img, vertices):
    """
    Applies an image mask.

    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    `vertices` should be a numpy array of integer points.
    """
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
    """
    NOTE: this is the function you might want to use as a starting point once you want to
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).

    Think about things like separating line segments by their
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of
    the lines and extrapolate to the top and bottom of the lane.

    This function draws `lines` with `color` and `thickness`.
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.

    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                            maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    draw_lines(line_img, lines)
    return line_img


# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, α=0.8, β=1., γ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.

    `initial_img` should be the image before any processing.

    The result image is computed as follows:

    initial_img * α + img * β + γ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, γ)


#################################


def process(img0: any) -> any:
    img = np.copy(img0)
    img = grayscale(img)
    img = canny(img, 50, 150)
    img = gaussian_blur(img, 3)

    # print(img.shape)
    (ym, xm) = img.shape
    (x0, x1) = (0, xm)
    (y0, y1) = (ym, ym // 2)
    vertices = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
    # print(vertices)
    img = region_of_interest(img, np.array([vertices]))

    # def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    hough_args = dict(
        # My quiz answers; section 4-16. This detects *other* lanes, but not ours!
        # rho=1,
        # theta=math.pi / 360,
        # threshold=10,
        # min_line_len=200,
        # max_line_gap=3,

        # The official quiz answers. Detects lots of nonsense lines!
        #rho=2,
        #theta=math.pi / 180,
        #threshold=15,
        #min_line_len=40,
        #max_line_gap=20,

        # Finally, parameters tweaked for this project.
        rho=2,
        theta=math.pi / 180,
        threshold=80,
        min_line_len=ym // 4,
        max_line_gap=ym // 8,
    )
    print(hough_args)
    lines = hough_lines(np.copy(img), **hough_args)
    # img = hough_lines(img, **hough_args)

    canny_img = weighted_img(lines, cv2.cvtColor(img, cv2.COLOR_GRAY2RGB))
    img = weighted_img(lines, np.copy(img0))

    return {'': img, '_canny': canny_img}


in_dir: str = "test_images"
out_dir: str = "test_images_output"

# shutil.rmtree(out_dir)
os.makedirs(out_dir, exist_ok=True)
for file in os.listdir(out_dir):
    os.remove(os.path.join(out_dir, file))
for file in os.listdir(in_dir):
    in_path = os.path.join(in_dir, file)
    images = process(mpimg.imread(in_path))
    for (suffix, image) in images.items():
        (basename, ext) = file.split('.')
        out_path = os.path.join(out_dir, ''.join([basename, suffix, '.', ext]))
        print(out_path)
        mpimg.imsave(out_path, image)
