from PIL import Image
import numpy as np

img = Image.open("layers/Accessories/BELT BLACK RING#5.png")
background = Image.open("layers/Background/Blue#100.png")

background.paste(img, (0, 0), img)
background.save('how_to_superimpose_two_images_01.png',"PNG")