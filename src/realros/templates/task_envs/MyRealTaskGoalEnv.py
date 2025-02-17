#!/bin/python3

import rospy
import numpy as np
from gymnasium import spaces
from gymnasium.envs.registration import register
from typing import List, Any, Dict, Optional

# Custom robot env
from realros.templates.robot_envs import MyRealRobotGoalEnv

# core modules of the framework
from realros.utils import ros_common
# from realros.utils import ros_controllers
from realros.utils import ros_markers

# Register your environment using the gymnasium register method to utilize gym.make("MyTaskGoalEnv-v0").
register(
    id='MyRealTaskGoalEnv-v0',
    entry_point='realros.templates.task_envs.MyRealTaskGoalEnv:MyRealTaskGoalEnv',
    max_episode_steps=100,
)


class MyRealTaskGoalEnv(MyRealRobotGoalEnv.MyRealRobotGoalEnv):
    """
    Use this custom env to implement a task using the robot/sensors related functions defined in the MyRobotGoalEnv
    """

    def __init__(self, new_roscore: bool = True, roscore_port: str = None, seed: int = None,
                 reset_env_prompt: bool = False, action_cycle_time: float = 0.0, default_port=False):
        """

        In the initialization statement, you can initialize any desired number and type of variables and pass the
        values to the environment as shown below:

        env = gym.make("MyTaskGoalEnv-v0", reset_env_prompt = True, new_roscore = True)

        """

        # if didn't include the variables above, uncomment here
        # new_roscore = True
        # roscore_port = None

        """
        seed for the environment. RealGoalEnv create a random number generator with a given seed. 
        The random number generator is stored as an instance variable (self.np_random) 
        so that it can be used by other methods in your class.
        """
        # if you didn't include the seed variable in __init__, uncomment here
        # seed = None

        """
        Whether to prompt the user for resetting the environment
        """
        # if you didn't include the seed variable in __init__, uncomment here
        # reset_env_prompt = False

        """
        variables to keep track of ros port
        """
        ros_port = None

        """
        Initialise the env
        """

        # launch a new roscore with default port
        if default_port:
            ros_port = self._launch_roscore(default_port=default_port)

        # Launch new roscore
        elif new_roscore:
            ros_port = self._launch_roscore(port=roscore_port)

        # ros_port of the already running roscore
        elif roscore_port is not None:
            ros_port = roscore_port

            # change to new rosmaster
            ros_common.change_ros_master(ros_port)

        else:
            """
            Check for roscore
            """
            if ros_common.is_roscore_running() is False:
                print("roscore is not running! Launching a new roscore!")
                ros_port = self._launch_roscore(port=roscore_port)

        # init the ros node
        if ros_port is not None:
            self.node_name = "TaskEnv" + "_" + ros_port
        else:
            self.node_name = "TaskEnv"

        rospy.init_node(self.node_name, anonymous=True)

        """
        Provide a description of the task.
        """
        rospy.loginfo("Starting Custom Task Env")

        """
        Load YAML param file
        """

        # add to ros parameter server
        # ros_common.ros_load_yaml(pkg_name="pkg_name", file_name="file_name.yaml", ns="ns")
        # self._get_params()

        """
        Define the action space.
        """
        # self.action_space = spaces.Discrete(n_actions)
        # self.action_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        # ROS often use double-precision (64-bit)
        # But if you are using Stable Baseline3, you need to define them as float32; otherwise it won't work

        """
        Define the observation space.

        observation space is a dictionary with 
            observation: 
            achieved_goal: 
            desired_goal: 
        """

        # Define the achieved_goal and desired_goal subspaces
        self.achieved_goal_space = spaces.Box(low=0, high=1, shape=(3,))
        self.desired_goal_space = spaces.Box(low=0, high=1, shape=(3,))

        # Define the overall observation space
        self.observation_space = spaces.Dict({
            'observation': spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32),
            'achieved_goal': self.achieved_goal_space,
            'desired_goal': self.desired_goal_space
        })

        """
        Define subscribers/publishers and Markers as needed.
        """

        # self.goal_marker = ros_markers.RosMarker(frame_id="world", ns="", marker_type=2, marker_topic="goal_pos",
        #                                          lifetime=10.0)

        """
        Init super class.
        """
        super().__init__(ros_port=ros_port, seed=seed, reset_env_prompt=reset_env_prompt,
                         action_cycle_time=action_cycle_time)

        """
        Finished __init__ method
        """
        rospy.loginfo("Finished Init of Custom Task Env")

    # -------------------------------------------------------
    #   Methods for interacting with the environment

    def _set_init_params(self, options: Optional[Dict[str, Any]] = None):
        """
        Set initial parameters for the environment.

        This method should be implemented here to set any initial parameters or state variables for the
        environment. This could include resetting joint positions, resetting sensor readings, or any other initial
        setup that needs to be performed at the start of each episode.

        Args:
            options (dict): Additional options for setting the initial parameters. Comes from the env.reset() method.

        """
        raise NotImplementedError()

    def _set_action(self, action):
        """
        Function to apply an action to the robot.

        This method should be implemented here to apply the given action to the robot. The action could be a
        joint position command, a velocity command, or any other type of command that can be applied to the robot.

        Args:
            action: The action to be applied to the robot.
        """
        raise NotImplementedError()

    def _get_observation(self):
        """
        Function to get an observation from the environment.

        This method should be implemented here to return an observation representing the current state of
        the environment. The observation could be a sensor reading, a joint state, or any other type of observation
        that can be obtained from the environment.

        Returns:
            An observation representing the current state of the environment.
        """
        raise NotImplementedError()

    def _get_achieved_goal(self):
        """
        Get the achieved goal from the environment.

        Returns:
            achieved_goal (Any): The achieved goal representing the current state of the environment.
        """
        raise NotImplementedError()

    def _get_desired_goal(self):
        """
        Get the desired goal from the environment.

        Returns:
            desired_goal (Any): The desired goal representing the target state of the environment.
        """
        raise NotImplementedError()

    def compute_reward(self, achieved_goal, desired_goal, info) -> float:
        """
        Compute the reward for achieving a given goal.

        This method should be implemented here to return a scalar reward value representing how well the agent
        is doing in the current episode. The reward could be based on the distance to a goal, the amount of time taken
        to reach a goal, or any other metric that can be used to measure how well the agent is doing.

        Args:
            achieved_goal (Any): The achieved goal representing the current state of the environment.
            desired_goal (Any): The desired goal representing the target state of the environment.
            info (dict): Additional information about the environment.

        Returns:
            reward (float): The reward for achieving the given goal.
        """

        raise NotImplementedError()

    def compute_terminated(self, achieved_goal, desired_goal, info):
        """
        Function to check if the episode is terminated due to reaching a terminal state.

        This method should be implemented here to return a boolean value indicating whether the episode has
        ended (e.g., because a goal has been reached or a failure condition has been triggered).

        Args:
            achieved_goal (Any): The achieved goal representing the current state of the environment.
            desired_goal (Any): The desired goal representing the target state of the environment.
            info (dict): Additional information for computing the termination condition.

        Returns:
            A boolean value indicating whether the episode has ended
            (e.g., because a goal has been reached or a failure condition has been triggered)
        """
        raise NotImplementedError()

    def compute_truncated(self, achieved_goal, desired_goal, info):
        """
        Function to check if the episode is truncated due non-terminal reasons.

        This method should be implemented here to return a boolean value indicating whether the episode has
        been truncated due to reasons other than reaching a terminal state.
        Truncated states are those that are out of the scope of the Markov Decision Process (MDP).
        This could include truncation due to reaching a maximum number of steps, or any other non-terminal condition
        that causes the episode to end early.

        Args:
            achieved_goal (Any): The achieved goal representing the current state of the environment.
            desired_goal (Any): The desired goal representing the target state of the environment.
            info (dict): Additional information for computing the truncation condition.

        Returns:
            A boolean value indicating whether the episode has been truncated.
        """
        raise NotImplementedError()

    # -------------------------------------------------------
    #   Include any custom methods available for the MyTaskEnv class

    def _get_params(self):
        """
        Function to get configuration parameters (optional)
        """
        raise NotImplementedError()

    # ------------------------------------------------------
    #   Task Methods for launching roscore

    @staticmethod
    def _launch_roscore(port=None, set_new_master_vars=False, default_port=False):
        """
        Launches a new roscore with the specified port. Only updates the ros_port.

        Return:
            ros_port: port of launched roscore
        """

        if port is None:
            port = 11311  # default port

        ros_port = ros_common.launch_roscore(port=port, set_new_master_vars=set_new_master_vars,
                                             default_port=default_port)

        # change to new rosmaster
        ros_common.change_ros_master(ros_port)

        return ros_port
