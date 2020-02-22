# Aaeon Up board setup

At the moment my favorite single board computer for the robotics applications  is [Aaeon Up Board](https://www.aaeon.com/en/p/up-board-computer-board-for-professional-makers) (even despite the fact it's not as popular as Raspberry Pi).

You can use all the library and frameworks developed for the "big" computer on it as it's an usual x86-64 computer based on Intel® Atom™ x5-Z8350 Processor. 

Here is a Fabric script for installing Ubuntu kernel 4.15.0 for UP from PPA on Ubuntu 18.04.

You have to have installed fabric 2.5.0 on your computer. To do that, just perform the command

    sudo python3 -m pip install fabric==2.5.0
    
(or use *venv* or *conda* for installation).

Clone this repository

    git clone https://github.com/alsprogrammer/aaeon_up_board_setup.git
    
cd into the *aaeon_up_board_setup* directory

    cd aaeon_up_board_setup
    
and run the script

    python3 main.py
    
That's all.

Enjoy! :)
