


## added by feiyu

# clear screen
alias cl="clear && printf '\e[3J'"

# ROS commands
alias setros='source devel/setup.bash'
alias setrosnetwork='export ROS_MASTER_URI=http://10.42.0.2:11311;export ROS_IP=10.42.0.1;unset ROS_HOSTNAME'
alias checkrosenv='env |grep ROS'

# commands
alias open_python='/usr/bin/env python'
#alias create_anaconda_env='conda create --name myenv'
alias open_anaconda='source ~/anaconda3/bin/activate; source activate mytf'
alias open_anaconda_rl='conda activate myrl'
alias open_anaconda_py2='conda activate py2'
alias close_anaconda='conda deactivate'
alias open_jupyter='open_anaconda; jupyter notebook'
alias open_jupyter_rl='open_anaconda_rl; jupyter notebook'

#alias set_vscode='cp -r ~/MyScripts/.vscode/ ./'
#alias set_gitignore='cp ~/MyScripts/.gitignore ./'

alias f='nautilus .'

alias rm='trash'
alias recmake='trash CMakeCache.txt; cmake ..'
alias mycmake='cd build; recmake; cd ..'
alias mymake='cd build; make -j12; cd ..'

# my cd list
alias cd_desktop='cd ~/Desktop/'
alias cd_downloads='cd ~/Downloads/'
alias cd_documents='cd ~/Documents'
alias cd_pictures='cd ~/Pictures/'

alias cd_slam='cd /home/feiyu/Documents/Projects/2018-winter/EECS432_CV_VO
'
alias cd_scripts='cd ~/MyScripts/'
alias cd_tk_tutorial='cd ~/Desktop/mypython/tk_tutorial'
alias cd_myRobotics='cd ~/Desktop/mypython/myRobotics'
alias cd_mypython='cd ~/Desktop/mypython'
alias cd_dl='cd ~/Desktop/dl'


alias cd_learn_coding='cd /home/feiyu/Desktop/learn_coding'
alias cd_leetcode='cd /home/feiyu/Desktop/learn_coding/leetcodes/lc_python'
alias cd_pythons='cd /home/feiyu/Desktop/learn_coding/pythons'

alias cd_rbt_motion='cd /home/feiyu/Desktop/mypython/PythonRobotics/PathTracking'

alias cd_courses='cd ~/Desktop/online-courses'
alias cd_ml='cd /home/feiyu/Desktop/ml/machine_learning_refined/notes'
alias cd_ml_py='cd /home/feiyu/Desktop/ml'

alias cd_c3_lectures='cd ~/Desktop/C3-DRL/lectures/posts; open_anaconda'
alias cd_shared='cd /home/feiyu/Documents/VirtualBox'
alias cd_label_tool='cd /home/feiyu/catkin_ws/src/simon_says/src/train_yolo/annonation_tool/labelImg'
alias cd_yolo='cd /home/feiyu/Documents/Projects/2019-spring/Yolo_as_Template_Matching'

alias cd_grasp='cd /home/feiyu/Desktop/XYZ-code/xyz_grasp_gen'
alias cd_alg='cd ~/Desktop/learn_algos'
alias cd_tools='cd /home/feiyu/Desktop/learn_coding/tools'

# common commands:
alias see_disk_size='du -hs ./'
alias see_disk='df -h'

# set bash
alias set_bash='subl ~/.bashrc'
alias set_aliase='subl ~/.bash_aliases'
alias set_voice='alsamixer'
# ros
alias printros='printenv | grep ROS'

alias git_log="git log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr)%C(bold blue) <%an> %Creset' --abbrev-commit"

alias add_python_path="export PYTHONPATH=$PWD${PYTHONPATH:+:${PYTHONPATH}}"
alias catmake="catkin_make -DCMAKE_BUILD_TYPE=RelWithDebInfo"
alias rebash="source ~/.bashrc && source ~/.bash_aliases"
alias bfg='java -jar ~/tools/bfg.jar'alias cd_xyz='cd /home/feiyu/Desktop/XYZ-code'
alias clip_video='bash ~/Desktop/learn_coding/tools/clip_video.sh'
alias hint_clip_video="echo 'bash ~/Desktop/learn_coding/tools/clip_video.sh video.avi 00:00:00 00:01:00 output.avi'"
