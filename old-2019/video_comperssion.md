AVI Video Compression


Via the Terminal cd to the folder containing the avi file and run this command:

ffmpeg -i input.avi -vcodec msmpeg4v2 output.avi

Replace "input.avi" with the name of your avi video. The compressed video will be created in the current folder having this name: output.avi.

MP4 Video Compression


Using the Terminal cd to the target folder and run this command:

ffmpeg -i input.mp4 -acodec mp2 output.mp4

Replace "input.mp4" with the name of your mp4 video. The compressed video will be saved in the current folder having this name: output.mp4.