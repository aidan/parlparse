import os

cmd = 'convert -density 72 a.pdf[0] -resize 300 -bordercolor black -border 3 aa%03d.png'

# and so on

# make an overlapping mosaic
cmd1 = 'composite -size 600x400 xc:skyblue prev.png'
cmd2 = 'composite -geometry 200x-1+50+50 page.png prev.png prev.png



import Image
import PngImagePlugin
info = PngImagePlugin.PngInfo()
info.add_text("key", "value")

im = Image.open("a.png")
print im.info

im.save("anew.png", pnginfo=info)


