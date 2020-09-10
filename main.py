import pyudev # python library for libudev which is api for enumerating and introspecting local devices
import time # helps playing with time
import os # helps playing with operating system itself
import subprocess # helps playing with processes

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

i = 0 # to count storage devices
mount_locs = [] # stores mountpoints of already mounted usb

for device in iter(monitor.poll, None):
    if device.action == 'add':
        time.sleep(15) # giving some time to get the device ready
        usb_devices = [] # stores inserted devices 'partitions'

        for device in context.list_devices(MAJOR='8', subsystem='block'): # looping through usb partitions
            if (device.device_type == 'partition'):
                usb_devices.append("{}".format(device.device_node)) # adding a partition to usb_devices list
                print("Found {}".format(device.device_node))

        if len(usb_devices) != 0:
            for stick in usb_devices:
                # finding mountpoint of a partition
                execute = 'lsblk -o name,mountpoint | grep {}'.format(stick[-4:]) 
                output = subprocess.check_output(execute, shell=True)

                # if partition not mounted, then, 
                if b'/home/ubuntu/smb-devices/storage' not in output: # b'string' because what we have in output is bytecode
                    if len(mount_locs) >= 1:
                        for m in mount_locs:
                            # checking for not used mountpoints
                            check = "ls -l {} || echo 'Input/output error'".format(m)

                            os.system(check + "> /home/ubuntu/mount_loc_output.txt")
                            if os.path.exists('/home/ubuntu/mount_loc_output.txt'):
                                dump = open('/home/ubuntu/mount_loc_output.txt')
                                error = dump.read()
                                dump.close()
                                os.remove('/home/ubuntu/mount_loc_output.txt')

                                # if unused mountpoint found, unmount that
                                if 'Input/output error' in error:
                                    print('Umount: {}'.format(m))
                                    os.system('sudo umount {}'.format(m))
                    # if the script is instally starting, abandon all existing unused mount points
                    if len(mount_locs) == 0:
                        os.system('sudo umount /home/ubuntu/smb-devices/*')
                    
                    # failsafe: unmount & check & delete
                    print('Umount: /home/ubuntu/smb-devices/storage{}'.format(i))
                    os.system('sudo umount /home/ubuntu/smb-devices/storage{}'.format(i))
                    os.system('find /home/ubuntu/smb-devices/. -type d -empty -delete')

                    # create a mount point with storage{0,1,2,...,n}
                    print('Create: /home/ubuntu/smb-devices/storage{}'.format(i))
                    os.system('mkdir /home/ubuntu/smb-devices/storage{}'.format(i))

                    mount_locs.append('/home/ubuntu/smb-devices/storage{}'.format(i)) # save created mountpoint to mount_locs list
                    print('Added /home/ubuntu/smb-devices/storage{} to mounted locations.'.format(i))

                    os.system('sudo mount {} /home/ubuntu/smb-devices/storage{}'.format(stick, i)) #finally mount the partition
                    print('Mounted {} on /home/ubuntu/smb-devices/storage{}'.format(stick, i))
                    i = i + 1 # increase i to create storage1 after 0, 2 after 1,...n+1 after n.
                
                # if the partitions is already mounted, ignore remount
                else:
                    print('Already mounted: {}'.format(stick))