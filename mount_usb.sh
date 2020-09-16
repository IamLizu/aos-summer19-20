#!/bin/sh
PATH=/usr/bin/
tmux new-session -d -s usb_watcher '/usr/bin/python3.8 /home/ubuntu/watch_driver.py'
