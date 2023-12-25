#!/bin/bash
# This is a helper function for clipping video.

# Example of usage:
# $ bash ~/xyz_log_tools/clip_video.sh video.avi 00:00:00 00:01:00 output.avi

# The 4 arguments are: 
# (1) Video file path
# (2) Start time of the video clip
# (3) Length to clip
# (4) Output file path

# Also you can put a shortcut in the bash_aliases:
# $ echo "alias clip_video='bash ~/Desktop/learn_coding/tools/clip_video.sh'" >> ~/.bash_aliases
# $ echo "alias hint_clip_video=\"echo 'bash ~/Desktop/learn_coding/tools/clip_video.sh video.avi 00:00:00 00:01:00 output.avi'\"" >> ~/.bash_aliases
# and then:
# $ hint_clip_video  
# $ clip_video video.avi 00:00:00 00:01:00 output.avi 


if [[ "$#"  -ne 4 ]] || [[ "$1" == "-h" ]]; then
    echo "Please input 4 arguments:"
    echo "  -- Video file path"
    echo "  -- Start time of the video clip"
    echo "  -- Length to clip"
    echo "  -- Output file filepath"
    exit 0
fi

ffmpeg -ss $2 -i $1 -t $3 -vcodec copy -acodec copy $4 

# Below is an example of the origin "ffmpeg" usage:
# $ ffmpeg -ss 00:02:22 -i src_video_file.mp4 -t 00:00:15 -vcodec copy -acodec copy output_video_file.mp4 