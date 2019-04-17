import pickle
import pygame
import numpy as np
import gym
import interface
import expert
import action


# DEFINES AND INITIALIZATIONS
# ----------------------------------------------------------------------------
# Number of sensors in observations
sensor_count = 65

# Number of availiable actions
action_count = 3

# Number of record iterations
episode_count = 2

# Number of steps per iteration
steps = 35000

# If track selection is done manually
manual_reset = True

# If wheel or keyboard is used
using_steering_wheel = True

# FILL HERE IF AUTOMATIC DRIVING
automatic = False

# file path
folder = "./demonstrations-long/"
name = "E_Track_2"

# All observations and their corresponding actions are stored here
observations_all = np.zeros((0, sensor_count))
actions_all = np.zeros((0, action_count))

# All observations and their corresponding actions are stored here
observations_all_less = np.zeros((0, sensor_count))
actions_all_less = np.zeros((0, action_count))

# Initialize the input interface
interface = interface.Interface(using_steering_wheel)

# Create the expert
expert = expert.Expert(interface, automatic=automatic)

out_file = open(folder + name, "wb")
out_file_less = open(folder + name + "-LESS", "wb")

for episode in range(episode_count):
    # Start torcs
    env = gym.TorcsEnv(manual=manual_reset)

    # Reset the expert
    expert.reset_values()

    # Observations and actions for this iteration are stored here
    observation_list = []
    action_list = []

    observation_list_less = []
    action_list_less = []

    print("#" * 100)
    print("# Episode: %d start" % episode)
    for i in range(steps):
        # If first iteration, get observation and action
        if i == 0:
            act = env.act
            obs = env.obs

        # If quit key is pressed, prematurely end this run
        if interface.check_key(pygame.KEYDOWN, pygame.K_q):
            break

        # Normalize the observation and add it to list of observations
        obs.normalize_obs()
        obs_list = obs.get_obs(angle=True, gear=True, opponents=True, rpm=True,
                               speedX=True, speedY=True,  track=True,
                               trackPos=True, wheelSpinVel=True)

        # Get the action that the expert would take
        act = expert.get_expert_act(obs, display=False)
        act.normalize_act()
        act_list = act.get_act(gas=True, gear=True, steer=True)
        action_list.append(act_list)
        observation_list.append(obs_list)
        if i % 2 == 0:
            action_list_less.append(act_list)
            observation_list_less.append(obs_list)
        act.un_normalize_act()

        # Execute the action and get the new observation
        obs = env.step(act)

    # Exit torcs
    env.end()

    observations_all = np.concatenate((observations_all, observation_list),
                                      axis=0)
    actions_all = np.concatenate((actions_all, action_list), axis=0)
    
    observations_all_less = np.concatenate((observations_all_less,
                                           observation_list_less), axis=0)
    actions_all_less = np.concatenate((actions_all_less, action_list_less),
                                      axis=0)

pickle.dump(observations_all, out_file)
pickle.dump(actions_all, out_file)
pickle.dump(observations_all_less, out_file_less)
pickle.dump(actions_all_less, out_file_less)
out_file.close()
out_file_less.close()