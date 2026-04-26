#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist, PoseStamped, Quaternion
from nav_msgs.msg import Odometry
import math
import tf
import random


class myTurtle():
    
    
    def __init__(self) -> None:
        """_summary_
        
        create all the nessary pubs/subs here and all the nessary other things
        
        """
        rospy.init_node('my_turtle', anonymous=True)    # Initialize ROS node

        # Publisher for velocity commands and odometry updates
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_cb)

        # Subscriber for nav pos goals
        self.goal_sub = rospy.Subscriber(
            "/move_base_simple/goal",
            PoseStamped,
            self.nav_to_pose
        )

        self.rate = rospy.Rate(10)  # Loop rate

        # Robot state variables
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
    
        

    def nav_to_pose(self, goal):
        # type: (PoseStamped) -> None
        """
        This is a callback function. It should extract data from goal, drive in a striaght line to reach the goal and
        then spin to match the goal orientation.
        :param goal: PoseStamped
        :return:
        """

        # Goal coords
        goal_x = goal.pose.position.x
        goal_y = goal.pose.position.y

        # Difference between goal and current coords
        dx = goal_x - self.x
        dy = goal_y - self.y

        # Angle to goal and angle difference
        target_angle = math.atan2(dy, dx)
        turn_angle = math.atan2(
            math.sin(target_angle - self.theta),
            math.cos(target_angle - self.theta)
        )

        self.rotate(turn_angle) # Rotate toward goal

        # Drive straight to goal
        distance = math.sqrt(dx**2 + dy**2)
        self.drive_straight(distance, 0.2)

        # Extract goal orientation
        orientation_q = goal.pose.orientation
        (_, _, goal_theta) = self.convert_to_euler(orientation_q)

        # Match goal orientation
        final_turn = math.atan2(
            math.sin(goal_theta - self.theta),
            math.cos(goal_theta - self.theta)
        )
        self.rotate(final_turn)

    def odom_cb(self,msg:Odometry) ->None:
        """_summary_
        Get the odom and update the internal location of the robot
        Args:
            msg (Odometry): _description_
        """
        # Update position
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        # Extract orientation quaternion and convert to Euler
        orientation_q = msg.pose.pose.orientation
        (_, _, yaw) = self.convert_to_euler(orientation_q)
        self.theta = yaw
    
    def stop(self)->None:
        """_summary_
        
        Stop moving
        """
        # Create empty Twist message and publish zero velocity
        twist = Twist()
        self.cmd_pub.publish(twist)
        
        
    def drive_straight(self, dist: float, vel: float)->None:
        """_summary_

        Args:
            dist (_type_): _description_
        """
        # Record starting position
        start_x = self.x
        start_y = self.y

        # Create velocity command
        twist = Twist()
        twist.linear.x = vel

        # Loop until given distance reached
        while not rospy.is_shutdown():
            # Current distance traveled
            current_dist = math.sqrt((self.x - start_x)**2 + (self.y - start_y)**2)

            # Stop when distance reached
            if current_dist >= dist:
                break

            self.cmd_pub.publish(twist) # Publish velocity command
            self.rate.sleep()   # Maintain loop rate

        self.stop() # Stop after motion complete
        
    
    def spin_wheels(self, u1, u2, time):
        """
        Spin the two wheels

        :param u1: wheel 1 speed
        :param u2: wheel 2 speed
        :param time: time to drive
        :return: None
        """
        twist = Twist() # Create velocity command

        # Convert differential drive values to forward and rotational velocity
        twist.linear.x = (u1 + u2) / 2.0    # Forward vel
        twist.angular.z = (u2 - u1)    # Rotational vel

        start_time = rospy.Time.now().to_sec()  # Record start time

        # Spin the wheels for the given time
        while rospy.Time.now().to_sec() - start_time < time:
            self.cmd_pub.publish(twist) # Publish velocity
            self.rate.sleep() # Maintain loop rate

        self.stop() # Stop after time elapsed

    def rotate(self, angle):
        """
        Rotate in place
        :param angle: angle to rotate
        :return: None
        """
        # Create velocity command
        twist = Twist()
        angular_speed = 0.3 # Fixed angular velocity

        target_theta = self.theta + angle    # Record starting orientation

        # Loop until given rotation achieved
        while not rospy.is_shutdown():
            # Find angle difference between current and goal
            error = math.atan2(
                math.sin(target_theta - self.theta),
                math.cos(target_theta - self.theta)
            )

            # If error is less than tolerance, break out of loop
            if abs(error) < 0.01:
                break

            # Set rotation direction and publish command
            twist.angular.z = angular_speed if error > 0 else -angular_speed
            self.cmd_pub.publish(twist)
            self.rate.sleep()   # Maintain loop rate

        self.stop() # Stop when done
    
    def convert_to_euler(self, quat):
        # type: (Quaternion) -> float
        """
        This might be helpful to have
        :param quat: quaternion 
        :return: euler angles
        """
        return tf.transformations.euler_from_quaternion([
            quat.x,
            quat.y,
            quat.z,
            quat.w
        ])
        
    def drive_circle(self, radius):
        """
        Drive robot in a circle of given radius
        """
        
        # Create velocity command
        twist = Twist()

        linear_speed = 0.2  # Contant linear speed
        angular_speed = linear_speed / radius   # Angular velocity

        # Assign above velocities to twist
        twist.linear.x = linear_speed
        twist.angular.z = angular_speed

        # Spin until terminated
        while not rospy.is_shutdown():
            self.cmd_pub.publish(twist)
            self.rate.sleep()

    def random_dance(self, duration):
        """
        Randomly move around
        """
        start_time = rospy.Time.now().to_sec()

        # Issue random move commands for the full duration
        while rospy.Time.now().to_sec() - start_time < duration:

            twist = Twist() # Create velocity command

            twist.linear.x = random.uniform(0.0, 0.3)   # Random linear speed
            twist.angular.z = random.uniform(-1.5, 1.5) # Random angular speed

            # Hold motion for 0.25s
            hold_start = rospy.Time.now().to_sec()

            while rospy.Time.now().to_sec() - hold_start < 0.25:
                self.cmd_pub.publish(twist) # Publish the command
                self.rate.sleep()   # Sleep

        self.stop() # Stop after complete

def main():
    """_summary_
    create all the node start up here
    """
    
    
    robot = myTurtle()

    task = "square"

    if task == "circle":
        robot.drive_circle(0.5)
    elif task == "square":
        for _ in range(5):
            robot.drive_straight(0.5, 0.2)
            robot.rotate(1.5708)
        robot.stop()
    elif task == "nav":
        rospy.spin()
    elif task == "dance":
        robot.random_dance(20)



if __name__ == '__main__':
    main()