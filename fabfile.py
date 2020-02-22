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
        context.put(file_name, file_name)
    except OSError as oe:
        print("Couldn't copy file {}: {}, exited".format(file_name, oe))
        sys.exit(1)
    result = context.sudo('mv {} {}'.format(file_name, destination_path), hide='stderr')
    if not result.ok:
        print("Couldn't copy {} to destination folder: {}, exited".format(file_name, result.stderr))
        sys.exit(1)


@task
def get_system_ready(c):
    update_upgrade(c)
    install_kernel(c)
    install_robotics(c)


@task
def update_upgrade(context):
    perform_sudo(context, 'apt update', "Couldn't update repositories")
    perform_sudo(context, 'apt upgrade', "Couldn't upgrade packets")
    print("System repositories upgraded")


@task
def install_kernel(context):
    perform_sudo(context, 'apt install binutils-dev', "Couldn't install packets")
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
    perform_sudo(context, 'apt install python3-pip', "Couldn't install pip")
    perform_sudo(context, 'python3 -m pip install --upgrade pip', "Couldn't upgrade pip")
    print("pip updated")


@task
def install_math_libs(context):
    perform_sudo(context, 'apt install python3-numpy', "Couldn't install packets")
    print("Math libs successfully installed")


@task
def install_opencv(context):
    perform_sudo(context, 'apt install python3-opencv', "Couldn't install packets")
    print("OpenCV installed")


@task
def install_fuzzypy(context):
    perform_sudo(context, 'python3 -m pip install fuzzypy', "Couldn't install packets")
    print("FuzzyPy installed")


@task
def install_tensorflow_lite(context):
    perform_run(context, 'wget https://dl.google.com/coral/python/tflite_runtime-1.14.0-cp36-cp36m-linux_x86_64.whl',
                "Couldn't download TF Lite {}")
    perform_sudo(context, 'python3 -m pip install tflite_runtime-1.14.0-cp36-cp36m-linux_x86_64.whl', "Couldn't install TF Lite")
    perform_sudo(context, 'rm -rf ./tflite_runtime-1.14.0-cp36-cp36m-linux_x86_64.whl', "Couldn't delete TF Lite")
    print("Tensorflow lite installed")


@task
def install_userspace(context):
    perform_sudo(context, 'add-apt-repository ppa:aaeonaeu/upboard', "Couldn't add aaeon repo")
    perform_sudo(context, 'apt update', "Couldn't update repositories")
    perform_sudo(context, 'apt install upboard-extras', "Couldn't install up board user space hardware drivers")
    print("Up board user space hardware drivers installed")
