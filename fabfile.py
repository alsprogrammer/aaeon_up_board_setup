import sys

from fabric import Connection, Config
from fabric import task
import getpass


def perform_sudo():
    


@task
def get_system_ready(c):
    update_upgrade(c)
    install_kernel(c)
    install_python3(c)


@task
def update_upgrade(c):
    result = c.sudo('apt update', hide='stderr')
    if not result.ok:
        print("Couldn't update repositories: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt upgrade', hide='stderr')
    if not result.ok:
        print("Couldn't upgrade packets: {}, exited".format(result.stderr))
        sys.exit(1)
    print("System repositories upgraded")


@task
def install_headers(c):
    print("Please start the ssh session in another terminal and connect to the robot:")
    print("ssh robot@192.168.0.102")
    print("providing robot address is 192.168.0.102")
    print("run command")
    print("sudo armbian-config")
    print("enter password and then go to menu Software/Headers")
    print("The kernel headers would be installed")
    print("After that close the terminal window and")
    input("Press Enter to continue...")
    print("Hope headers were installed")


@task
def compile_libgpiod(c):
    result = c.sudo('apt-get -y install libtool pkg-config', hide='stderr')
    if not result.ok:
        print("Couldn't install libtool pkg-config libs: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.run('git clone https://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git', hide='stderr')
    if not result.ok:
        print("Couldn't clone libgpiod repository: {}, exited".format(result.stderr))
        sys.exit(1)
    with c.cd('libgpiod', hide='stderr'):
        result = c.run('mkdir -p include/linux', hide='stderr')
        if not result.ok:
            print("Couldn't create headers dir: {}, exited".format(result.stderr))
            sys.exit(1)
        result = c.run('cp /usr/src/linux-headers-$(uname -r)/include/linux/compiler_types.h include/linux/.', hide='stderr')
        if not result.ok:
            print("Couldn't copy headers to the actual dir: {}, exited".format(result.stderr))
            sys.exit(1)
        result = c.run('./autogen.sh --enable-tools=yes --prefix=/usr/local CFLAGS="-I/usr/src/linux-headers-$(uname -r)/include/uapi -Iinclude"', hide='stderr')
        if not result.ok:
            print("Couldn't autogen: {}, exited".format(result.stderr))
            sys.exit(1)
        result = c.run('make', hide='stderr')
        if not result.ok:
            print("Couldn't make: {}, exited".format(result.stderr))
            sys.exit(1)
        result = c.sudo('make install', hide='stderr')
        if not result.ok:
            print("Couldn't make install: {}, exited".format(result.stderr))
            sys.exit(1)
        result = c.sudo('ldconfig', hide='stderr')
        if not result.ok:
            print("Couldn't start ldconfig: {}, exited".format(result.stderr))
            sys.exit(1)
    print("System repositories upgraded")


@task
def prepare_card(c, ssid, psk):
    cur_user_name = getpass.getuser()
    c.local('touch /media/{user}/boot/ssh'.format(user=cur_user_name))
    with open('/media/{user}/boot/wpa_supplicant.conf'.format(user=cur_user_name), 'w') as wpa:
        print('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev', file=wpa)
        print('update_config=1', file=wpa)
        print('country=RU', file=wpa)
        print('network={', file=wpa)
        print('    ssid="{ssid}"'.format(ssid=ssid), file=wpa)
        print('    psk="{psk}"'.format(psk=psk), file=wpa)
        print('    key_mgmt=WPA-PSK', file=wpa)
        print('}', file=wpa)


@task
def connection_test(c):
    result1 = c.sudo('whoami', hide='stderr')
    print(result1)
    result2 = c.run('id -u {}'.format(result1.stdout))
    print(result2)


@task
def create_user(c):
    result = c.sudo('useradd -s /usr/sbin/nologin -G i2c,video robot', hide='stderr')
    if not result.ok:
        print("Couldn't create robot user: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('mkdir /home/robot', hide='stderr')
    if not result.ok:
        print("Couldn't create robot user home directory: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Robot user successfully created")


@task
def install_python3(c):
    result = c.sudo('apt-get -y install python3', hide='stderr')
    if not result.ok:
        print("Couldn't install Python3: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('chmod 4775 /usr/bin/python3', hide='stderr')
    if not result.ok:
        print("Couldn't change access rights for Python3: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install python3-pip', hide='stderr')
    if not result.ok:
        print("Couldn't install pip3: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install python3-setuptools', hide='stderr')
    if not result.ok:
        print("Couldn't install setuptools: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install build-essential', hide='stderr')
    if not result.ok:
        print("Couldn't install buildessentials: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install python3-dev', hide='stderr')
    if not result.ok:
        print("Couldn't install python3-dev: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('python3 -m pip install wheel', hide='stderr')
    if not result.ok:
        print("Couldn't install python wheel: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Python3 successfully installed")


@task
def install_python35(c):
    result = c.run('wget https://www.python.org/ftp/python/3.5.3/Python-3.5.3.tar.xz', hide='stderr')
    if not result.ok:
        print("Couldn't get Python3.5.3: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.run('tar -xvf Python-3.5.3.tar.xz', hide='stderr')
    if not result.ok:
        print("Couldn't unpack Python3.5.3: {}, exited".format(result.stderr))
        sys.exit(1)
    with c.cd('Python-3.5.3'):
        result = c.run('./configure', hide='stderr')
        if not result.ok:
            print("Couldn't configure python: {}, exited".format(result.stderr))
            sys.exit(1)
        result = c.run('make', hide='stderr')
        if not result.ok:
            print("Couldn't run make: {}, exited".format(result.stderr))
            sys.exit(1)
    result = c.sudo('sh -c "cd /home/robot/Python-3.5.3 && make install"', hide='stderr')
    if not result.ok:
        print("Couldn't make install: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('python3.5 -m ensurepip', hide='stderr')
    if not result.ok:
        print("Couldn't install Python3.5 pip: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('chmod 4775 /usr/bin/python3.5', hide='stderr')
    if not result.ok:
        print("Couldn't change access rights for Python3: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install python3-setuptools', hide='stderr')
    if not result.ok:
        print("Couldn't install setuptools: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install build-essential', hide='stderr')
    if not result.ok:
        print("Couldn't install buildessentials: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install python3-dev', hide='stderr')
    if not result.ok:
        print("Couldn't install python3-dev: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('python3.5 -m pip install wheel', hide='stderr')
    if not result.ok:
        print("Couldn't install python wheel: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Python3.5 successfully installed")


@task
def install_math_libs(c):
    result = c.sudo('apt-get -y install python3-numpy', hide='stderr')
    if not result.ok:
        print("Couldn't install math libs: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Math libs successfully installed")


@task
def install_robo_libs(c):
    result = c.sudo('apt-get -y install autoconf autoconf-archive libtool libkmod-dev pkg-config', hide='stderr')
    if not result.ok:
        print("Couldn't install autoconf-archive libs: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('apt-get -y install python3-smbus python3-libgpiod', hide='stderr')
    if not result.ok:
        print("Couldn't install python3-smbus libs: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('python3 -m pip install adafruit-circuitpython-pca9685', hide='stderr')
    if not result.ok:
        print("Couldn't install dafruit-circuitpython-pca9685 libs: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('python3 -m pip install adafruit-circuitpython-mcp230xx', hide='stderr')
    if not result.ok:
        print("Couldn't install adafruit-circuitpython-mcp230xx libs: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('python3 -m pip install adafruit-circuitpython-ssd1306', hide='stderr')
    if not result.ok:
        print("Couldn't install adafruit-circuitpython-ssd1306 libs: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Robo libs successfully installed")


@task
def install_web_libs(c):
    result = c.sudo('python3 -m pip install pyramid', hide='stderr')
    if not result.ok:
        print("Couldn't install web libs: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Web libs successfully installed")


@task
def install_web_app(c):
    try:
        c.put('./app.py', './app.py')
    except OSError as oe:
        print("Couldn't copy file: {error}, ttyd, exited".format(oe))
        sys.exit(1)
    result = c.sudo('mv ./app.py /opt/', hide='stderr')
    if not result.ok:
        print("Couldn't copy app.py to destination folder: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Web apps successfully installed")


@task
def add_autoload(c):
    result = c.sudo('echo -e "@reboot sudo -u robot python3 /opt/app.py &\r\n@reboot sudo -u robot PYTHONSTARTUP=/home/robot/startup.py sh -c \'/opt/ttyd_linux.armhf -p 8080 python3\' &" | crontab -',
                    hide='stderr')
    if not result.ok:
        print("Couldn't add autoload elements to crontab: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Autoload successfully installed")


@task
def put_main_files(c):
    files = ['./startup.py', './robot.py', './main_program.py']
    for file_name in files:
        try:
            c.put(file_name, file_name)
        except OSError as oe:
            print("Couldn't copy file: {error}, {file_name}, exited".format(oe, file_name=file_name))
            sys.exit(1)

    result = c.sudo('chown robot:robot /home/robot/main_program.py', hide='stderr')
    if not result.ok:
        print("Couldn't change access rights of file: {}, exited".format(result.stderr))
        sys.exit(1)

    print("Robot files installed")


@task
def install_ttyd(c):
    try:
        c.put('./ttyd_linux.armhf', './ttyd_linux.armhf')
    except OSError as oe:
        print("Couldn't copy file: {error}, ttyd, exited".format(oe))
        sys.exit(1)
    result = c.sudo('chmod +x ./ttyd_linux.armhf', hide='stderr')
    if not result.ok:
        print("Couldn't make ttyd executable: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('mv ./ttyd_linux.armhf /opt/', hide='stderr')
    if not result.ok:
        print("Couldn't copy ttyd to destination folder: {}, exited".format(result.stderr))
        sys.exit(1)

    print("Ttyd installed")


@task
def put_html_files(c):
    result = c.sudo('apt-get -y install unzip', hide='stderr')
    if not result.ok:
        print("Couldn't install unzip: {}, exited".format(result.stderr))
        sys.exit(1)
    c.local('zip -r zhtml html')
    try:
        c.put('zhtml.zip', 'zhtml.zip')
    except OSError as oe:
        print("Couldn't copy html zip file: {error}, exited".format(error=oe))
        sys.exit(1)
    result = c.sudo('rm -rf /var/www/html/*', hide='stderr')
    if not result.ok:
        print("Couldn't delete previous files in /var/www/html: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('unzip zhtml.zip -d /var/www/', hide='stderr')
    if not result.ok:
        print("Couldn't unpack html files to /var/www/html: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.run('rm zhtml.zip', hide='stderr')
    if not result.ok:
        print("Couldn't unpack html files to /var/www/html: {}, exited".format(result.stderr))
        sys.exit(1)
    c.local('rm zhtml.zip')
    print("HTML files copied")


@task
def install_mjpeg_streamer(c):
    result = c.sudo('apt-get -y install cmake libjpeg62-turbo-dev', hide='stderr')
    if not result.ok:
        print("Couldn't install cmake and libjpeg62-turbo-dev: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.run('git clone https://github.com/jacksonliam/mjpg-streamer.git', hide='stderr')
    if not result.ok:
        print("Couldn't clone mjpeg-streamer source code: {}, exited".format(result.stderr))
        sys.exit(1)
    with c.cd('/home/robot/mjpg-streamer/mjpg-streamer-experimental'):
        result = c.run('make', hide='stderr')
        if not result.ok:
            print("Couldn't make: {}, exited".format(result.stderr))
            sys.exit(1)
    result = c.sudo('sh -c "cd /home/robot/mjpg-streamer/mjpg-streamer-experimental && make install"', hide='stderr')
    if not result.ok:
        print("Couldn't make install: {}, exited".format(result.stderr))
        sys.exit(1)
    print("mjpeg-streamer installed")


@task
def install_opencv(c):
    result = c.sudo('apt-get -y install python3-opencv', hide='stderr')
    if not result.ok:
        print("Couldn't install OpenCV: {}, exited".format(result.stderr))
        sys.exit(1)
    print("OpenCV installed")


@task
def install_fuzzypy(c):
    result = c.sudo('python3 -m pip install fuzzypy', hide='stderr')
    if not result.ok:
        print("Couldn't install FuzzyPy: {}, exited".format(result.stderr))
        sys.exit(1)
    print("FuzzyPy installed")


@task
def install_psutil(c):
    result = c.sudo('python3 -m pip install psutil', hide='stderr')
    if not result.ok:
        print("Couldn't install psutil: {}, exited".format(result.stderr))
        sys.exit(1)
    print("psutil installed")


@task
def install_tensorflow_lite(c):
    try:
        c.put('./tflite_runtime-1.14.0-cp37-cp37m-linux_armv7l.whl', './tflite_runtime-1.14.0-cp37-cp37m-linux_armv7l.whl')
    except OSError as oe:
        print("Couldn't copy file: {error}, ttyd, exited".format(oe))
        sys.exit(1)
    result = c.sudo('python3 -m pip install tflite_runtime-1.14.0-cp37-cp37m-linux_armv7l.whl', hide='stderr')
    if not result.ok:
        print("Couldn't install Tensorflow lite: {}, exited".format(result.stderr))
        sys.exit(1)
    result = c.sudo('rm -rf ./tflite_runtime-1.14.0-cp37-cp37m-linux_armv7l.whl', hide='stderr')
    if not result.ok:
        print("Couldn't delete wheel for tensorflow lite: {}, exited".format(result.stderr))
        sys.exit(1)
    print("Tensorflow lite installed")


@task
def upgrade_pip(c):
    result = c.sudo('python3 -m pip install --upgrade pip', hide='stderr')
    if not result.ok:
        print("Couldn't update pip: {}, exited".format(result.stderr))
        sys.exit(1)
    print("pip updated")


if __name__ == "__main__":
    sudo_pass = getpass.getpass("What's your sudo password?")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    c = Connection('192.168.0.2', user='aleksandr', connect_kwargs={"password": sudo_pass}, config=config)
    result1 = c.sudo('whoami', hide='stderr')
    print(result1)

    result2 = c.run('id -u {}'.format(result1.stdout))
    print(result2)
