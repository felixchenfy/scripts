
# Speed up
ffmpeg -i input.mkv -vf "setpts=0.2*PTS" -an output.mkv
ffmpeg -i exercise.avi -vf "setpts=0.2*PTS" -an output.avi

# Change framerate

MP4Box -add test_track1.h264:fps=30 -new DestMovie.mp4
MP4Box -add exercise.avi:fps=50 -new DestMovie.mp4


# Clip video

ffmpeg -ss 00:05:17 -t 00:06:35 -i my.mp4 -vcodec copy -acodec copy output1.mp4



ffmpeg -i output1.mp4 -vf "setpts=0.2*PTS" -an output2.mp4
ffmpeg -i output1.mp4 -vf "setpts=0.5*PTS" -an output3.mp4
