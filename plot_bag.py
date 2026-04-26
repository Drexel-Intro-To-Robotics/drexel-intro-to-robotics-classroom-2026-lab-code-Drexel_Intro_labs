import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt


def plot_all(run_name):
    base = f"{run_name}/"

    # Load data
    # IMU csv is very large, so only take a portion of it
    imu = pd.read_csv(
    base + "imu.csv",
    usecols=['Time', 'angular_velocity.z'])[::10]

    # Odom csv is very large, so only take a portion of it
    odom = pd.read_csv(
    base + "odom.csv",
    usecols=['pose.pose.position.x', 'pose.pose.position.y'])[::5]
    
    cmd = pd.read_csv(base + "cmd_vel.csv")

    # Trajectory
    plt.figure()
    plt.plot(odom['pose.pose.position.x'],
             odom['pose.pose.position.y'])
    plt.title(f"{run_name} Trajectory")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis('equal')
    plt.savefig(base + "trajectory.png")
    plt.close()

    # Velocity
    plt.figure()
    plt.plot(cmd['Time'], cmd['linear.x'], label='Linear Velocity')
    plt.plot(cmd['Time'], cmd['angular.z'], label='Angular Velocity')
    plt.title(f"{run_name} Velocity")
    plt.xlabel("Time")
    plt.legend()
    plt.savefig(base + "velocity.png")
    plt.close()

    # IMU
    plt.figure()
    plt.plot(imu['Time'], imu['angular_velocity.z'])
    plt.title(f"{run_name} IMU Angular Velocity (Z)")
    plt.xlabel("Time")
    plt.ylabel("rad/s")
    plt.savefig(base + "imu.png")
    plt.close()


# Run for all experiments
#plot_all("circle_run")
print("Completed circle")
plot_all("square_run")
print("Completed square")
#plot_all("nav_run")
print("Completed nav")
#plot_all("dance_run")
print("Completed dance")