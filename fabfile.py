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


@task
def update_upgrade(context):
    perform_sudo(context, 'apt update', "Couldn't update repositories")
    perform_sudo(context, 'apt upgrade', "Couldn't upgrade packets")
    print("System repositories upgraded")


@task
def install_kernel(context):
    with open('filelist', 'r') as deb_list:
        for link in deb_list:
            perform_run(context, 'wget {}'.format(link), "Couldn't download deb packet {}".format(link))
    perform_sudo(context, 'dpkg -i *.deb', "Couldn't install packets")
    perform_sudo(context, 'update-grub', "Couldn't upgrade grub")
    print("Everything has been installed. The device needs to be rebooted")
