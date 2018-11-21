#!/usr/bin/env python

import rospy
import smach_ros
import smach
from naoqi_bridge_msgs.msg import HeadTouch
from std_msgs.msg import String

class TouchCheck(smach.State):
    """ A module to detect if pepper's head is touched
    """
    #@smach.cb_interface(outcomes = ['success','waiting']) ## same
    def __init__(self):	
        smach.State.__init__(self, outcomes = ['success','waiting'])

    def callback(data): 
        rospy.loginfo( "I heard %u %u" % (data.button, data.state))
        
    def execute(self):
	#pub = rospy.Publisher('/pepper_robot/head_touch', HeadTouch, queue_size=1)
	rospy.Subscriber("/pepper_robot/head_touch", HeadTouch)
	if (callback):
	    return 'success'
	    rospy.loginfo('touch detected')
	else:
	    return 'waiting'
	

class SaySpeech(smach.State):
    ''' give a speech
    '''
    def __init__(self):	
        smach.State.__init__(self, outcomes = ['success'])
    def execute(self, userdata):
	tts_publisher = rospy.Publisher('/speech', String, queue_size=1)
	rospy.sleep(5.0)
	#hello_str = "ich bin pepper, mein Kopf wird angefasst."
        #rospy.loginfo(hello_str)
        tts_publisher.publish(String("Ich bin Pepper"))
        rospy.sleep(7.0)
	return 'success'
	
	    
	
        

def main():
    rospy.init_node('smach_touch_react')
    rate = rospy.Rate(10)
    sm_root = smach.StateMachine(outcomes=['success'])

    with sm_root:

        smach.StateMachine.add('TOUCH_CHECK', TouchCheck(), transitions={'success':'SAY_SPEECH', 'waiting':'TOUCH_CHECK'})
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
