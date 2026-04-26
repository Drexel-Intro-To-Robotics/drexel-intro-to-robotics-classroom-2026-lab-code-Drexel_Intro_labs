import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'bagpy'))

from bagpy import bagreader

bag = bagreader('square_run.bag')

imu = bag.message_by_topic('/imu')
odom = bag.message_by_topic('/odom')
cmd = bag.message_by_topic('/cmd_vel')

print("Done")