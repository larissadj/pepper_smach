#!/usr/bin/env python

'''
	1. $ roslaunch roslaunch pepper_bringup pepper_full.launch nao_ip:=<robot_ip> roscore_ip:=<roscore_ip> [network_interface:=<eth0|wlan0|vpn0>]
	2. $ python smach_touch_react_1.py
	3. $ rosrun smach_viewer smach_viewer.py 
'''

import rospy
import smach_ros
import smach
from naoqi_bridge_msgs.msg import HeadTouch
from std_msgs.msg import String
import threading
import time

class TouchCheck(smach.State):
    """ A module to detect if pepper's head is touched
    """
    def __init__(self):	
        smach.State.__init__(self, outcomes = ['success','waiting','failed'])
	self.m = threading.Lock()
	self.state_received = False
	rospy.Subscriber("/pepper_robot/head_touch", HeadTouch, self.callback)
    def callback(self, data):
	self.m.acquire()
	if data.state == 1:
	  self.state_received = True
	self.m.release()
		
    def execute(self, userdata):
	#wait for maximum 1 min 
	for i in range(0,600):
	    self.m.acquire()
	    if self.state_received:
		#we receive 1 
		return 'success'

	    self.m.release()

	    time.sleep(0.1)
	    return 'waiting'
	return 'failed'
	

class SaySpeech(smach.State):
    ''' give a speech
    '''
    def __init__(self):	
        smach.State.__init__(self, outcomes = ['success'])
    def execute(self, userdata):
	tts_publisher = rospy.Publisher('/speech', String, queue_size=1)
	rospy.sleep(1.0)
        tts_publisher.publish(String("Ich bin Pepper"))
        rospy.sleep(1.0)
	return 'success'        

def main():
    rospy.init_node('smach_touch_react')
    rate = rospy.Rate(10)
    sm_root = smach.StateMachine(outcomes=['success','failed'])

    with sm_root:

        smach.StateMachine.add('TOUCH_CHECKER', TouchCheck(), transitions={'success':'SAY_SPEECH', 'waiting':'TOUCH_CHECKER'})
	smach.StateMachine.add('SAY_SPEECH', SaySpeech())

    # Execute SMACH plan
    sis = smach_ros.IntrospectionServer('SM_Pepper', sm_root, '/SM_Pepper')
    sis.start()
    # Execute SMACH plan
    outcome = sm_root.execute()

    # Wait for ctrl-c to stop the application
    rospy.spin()
    sis.stop()
if __name__ == '__main__':
    main()
