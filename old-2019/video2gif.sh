#!/usr/bin/bash

# Example of usage:
# https://askubuntu.com/questions/648603/how-to-create-an-animated-gif-from-mp4-video-via-command-line
# sudo apt-get install ffmpeg

wget -O opengl-rotating-triangle.mp4 https://github.com/cirosantilli/media/blob/master/opengl-rotating-triangle.mp4?raw=true
ulimit -Sv 5000000
ffmpeg \
    -i opengl-rotating-triangle.mp4 \
    -r 15 \
    -vf scale=512:-1 \
    -ss 00:00:03 -to 00:00:06 \
    tmptmp.gif

# Speed up.
# http://blog.floriancargoet.com/slow-down-or-speed-up-a-gif-with-imagemagick/
convert -delay 10x100 tmptmp.gif output_not_compressed.gif

# The output gif is compressed.
# The only defect is that the output framerate cannot be adjusted.

# You may try this tool to compress the gif again.
# sudo apt install gifsicle
gifsicle -i output_not_compressed.gif -O3 --colors 256 -o output_compressed.gif
