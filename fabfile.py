import sys

from fabric import task


def perform_sudo(context, command, error_message):
    result = context.sudo(command, hide='stderr')
    if not result.ok:
        print("{}: {}, exited".format(error_message, result.stderr))
        sys.exit(1)


def perform_run(context, command, error_message):
    result = context.run(command, hide='stderr')
    if not result.ok:
        print("{}}: {}, exited".format(error_message, result.stderr))
        sys.exit(1)


def perform_commands_sudo(context, command, error_message):
    result = context.sudo('sh -c "{}"'.format(command), hide='stderr')
    if not result.ok:
        print("{}: {}, exited".format(error_message, result.stderr))
        sys.exit(1)


def put_file(context, file_name, destination_path):
    try:
        context.put(file_name, destination_path)
    except OSError as oe:
        print("Couldn't copy file {}: {}, exited".format(file_name, oe))
        sys.exit(1)
    if file_name != destination_path:
        result = context.sudo('mv {} {}'.format(file_name, destination_path), hide='stderr')
        if not result.ok:
            print("Couldn't copy {} to destination folder: {}, exited".format(file_name, result.stderr))
            sys.exit(1)


@task
def get_system_ready(c):
    update_upgrade(c)
    install_kernel(c)
    install_networking(c)
    install_robotics(c)


@task
def update_upgrade(context):
    perform_sudo(context, 'apt -y update', "Couldn't update repositories")
    perform_sudo(context, 'apt -y upgrade', "Couldn't upgrade packets")
    print("System repositories upgraded")


@task
def install_kernel(context):
    perform_sudo(context, 'apt -y install binutils-dev', "Couldn't install packets")
    perform_sudo(context, 'apt -y install libsecret-1-dev', "Couldn't install packets")
    with open('filelist', 'r') as deb_list:
        for link in deb_list:
            print('Downloading {} file'.format(link))
            perform_run(context, 'wget {}'.format(link), "Couldn't download deb packet {}".format(link))
    perform_sudo(context, 'dpkg -i *.deb', "Couldn't install packets")
    perform_sudo(context, 'update-grub', "Couldn't upgrade grub")
    perform_sudo(context, 'rm -rf *.deb', "Couldn't delete downloaded files")
    print("Everything has been installed. The device needs to be rebooted")


@task
def install_robotics(context):
    install_userspace(context)
    upgrade_pip(context)
    install_math_libs(context)
    install_opencv(context)
    install_fuzzypy(context)
    install_tensorflow_lite(context)


@task
def upgrade_pip(context):
    perform_sudo(context, 'apt -y install python3-pip', "Couldn't install pip")
    perform_sudo(context, 'python3 -m pip install --upgrade pip', "Couldn't upgrade pip")
    print("pip updated")


@task
def install_math_libs(context):
    perform_sudo(context, 'apt -y install python3-numpy', "Couldn't install packets")
    print("Math libs successfully installed")


@task
def install_opencv(context):
    perform_sudo(context, 'python3 -m pip install opencv-contrib-python-headless', "Couldn't install packets")
    print("OpenCV installed")


@task
def install_fuzzypy(context):
    perform_sudo(context, 'python3 -m pip install fuzzypy', "Couldn't install packets")
    print("FuzzyPy installed")


@task
def install_tensorflow_lite(context):
    perform_run(context, 'wget https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp35-cp35m-linux_x86_64.whl',
                "Couldn't download TF Lite {}")
    perform_sudo(context, 'python3 -m pip install tflite_runtime-2.1.0.post1-cp35-cp35m-linux_x86_64.whl',
                 "Couldn't install TF Lite")
    perform_sudo(context, 'rm -rf ./python3 -m pip install tflite_runtime-2.1.0.post1-cp35-cp35m-linux_x86_64.whl', "Couldn't delete TF Lite")
    print("Tensorflow lite installed")


@task
def install_userspace(context):
    perform_sudo(context, 'add-apt-repository -y ppa:mraa/mraa', "Couldn't install packets")
    perform_sudo(context, 'apt update', "Couldn't update repositories")
    perform_sudo(context, 'apt -y install mraa-tools mraa-examples libmraa1 libmraa-dev libupm-dev libupm1 upm-examples', "Couldn't update repositories")
    perform_sudo(context, 'apt -y install python3-mraa', "Couldn't update repositories")

    put_file(context, './50-gpio.rules', '/etc/udev/rules.d/50-spi.rules')
    put_file(context, './50-i2c.rules', '/etc/udev/rules.d/50-i2c.rules')
    put_file(context, './50-gpio.rules', '/etc/udev/rules.d/50-gpio.rules')

    groups = ['spiuser', 'i2cuser', 'gpiouser']
    for group in groups:
        perform_sudo(context, 'groupadd {}'.format(group), "Couldn't add group {}".format(group))
        perform_sudo(context, 'adduser "$USER" {}'.format(group), "Couldn't add user to the group {}".format(group))

    print("Up board user space hardware drivers installed")
    print("The device needs to be rebooted")


@task
def install_networking(context):
    perform_sudo(context, 'apt -y install ifupdown', "Couldn't install wpasupplicant")
    perform_sudo(context, 'apt -y install wpasupplicant', "Couldn't install wpasupplicant")


@task
def install_ros(context):
    perform_commands_sudo(context, 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list', "Couldn't add ROS repo")
    perform_sudo(context, "apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654", "Couldn't add the key")
    perform_sudo(context, 'apt update', "Couldn't update repositories")
    perform_sudo(context, 'apt -y install ros-kinetic-ros-base', "Couldn't install ROS itself")
    perform_sudo(context, 'rosdep init', "Couldn't initialize rosdep")
    perform_run(context, 'rosdep update', "Couldn't update rodep")
    print('The ROS Kinetic has been installed. Please reboot the board')


@task
def install_pytorch(context):
    perform_sudo(context, 'python3 -m pip install torch==1.4.0+cpu torchvision==0.5.0+cpu -f https://download.pytorch.org/whl/torch_stable.html', "Couldn't install pytorch")
    print('PyTorch installed')


@task
def install_google_coral(context):
    perform_sudo(context, 'apt-get update', "Couldn't perform update")
    perform_commands_sudo(context, 'echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list', "Couldn't install coral repo")
    perform_commands_sudo(context, 'curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -', "Couldn't add coral key")
    perform_sudo(context, 'apt-get install libedgetpu1-std', "Couldn't install libedgetpu")
    perform_sudo(context, 'apt-get install edgetpu python3-edgetpu', "Couldn't perform update")
    perform_sudo(context, 'pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp35-cp35m-linux_x86_64.whl', "Couldn't perform update")
    put_file(context, './coral_test.py', './coral_test.py')
