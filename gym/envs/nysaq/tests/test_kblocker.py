import pytest, inspect, os, json
import numpy as np
from gym.envs.nysaq import KBlockerEnv
from gym.spaces import Box, Discrete


def get_k_blocker_env(fileName):
    config_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    config_path = config_folder + '/assets/' + fileName
    task = KBlockerEnv(config_path)
    return task

@pytest.mark.parametrize("fileName,observations", [
    ('rbmConfig1bt', Box(np.array([0]*4),np.array([4,5]*2))),
    ('rbmConfig2bt', Box(np.array([0]*6),np.array([7,4]*3)))
])
def test_k_blocker_observation(fileName, observations):
    task = get_k_blocker_env(fileName)
    assert task.observation_space == observations


def test_k_blocker_observation_dimensions():
    fileName = 'rbmConfig1bt'
    task = get_k_blocker_env(fileName)

    step_obs = task.step(task.action_space.sample())
    assert len(step_obs[0]) == task.observation_space.shape[0]
    assert step_obs[1] == 0  # No reward because still in 1st or 2nd row

    reset_obs = task.reset()
    assert len(reset_obs) == task.observation_space.shape[0]


@pytest.mark.parametrize("fileName,actions", [
    ('rbmConfig1bt', Discrete(16)),
    ('rbmConfig2bt', Discrete(64))
])
def test_k_blocker_actions(fileName, actions):
    task = get_k_blocker_env(fileName)
    assert task.action_space == actions

# normal walk,
# avoiding falling off the edge
# avoiding running each other over.
# avoiding going into the blockers
@pytest.mark.parametrize("cc, action, nc", [
    ([(0,0),(3,0)], 4, [(1,0),(2,0)]),  #action: [0,1]
    ([(0,0),(3,0)], 1, [(0,0),(3,0)]),  #action: [1,0]
    ([(0,0),(3,0)], 14, [(0,0),(3,1)]),  #action: [2,3]
    ([(1,1),(2,1)], 4, [(1,1),(2,1)]),  #action: [0,1]
    ([(0,3),(3,3)], 15, [(0,3),(3,4)])  #action: [3,3] The blocker is on the left
])
def test_k_blocker_coords(cc, action, nc):
    fileName = 'rbmConfig1bt'
    task = get_k_blocker_env(fileName)

    task._KBlockerEnv__coords = cc
    task._KBlockerEnv__gap = task._KBlockerEnv__grid_x - 1
    task.step(action)
    assert task._KBlockerEnv__coords == nc

# winning
@pytest.mark.parametrize("cc, action, exp_rew, exp_done", [
    ([(0,3),(3,3)], 15, 5, False),  #action : (3,3)
    ([(0,3),(3,4)], 15, 0, True),  #action : (3,3)
    ([(0,3),(3,4)], 8,  0, True)  #action : (2,2)
])
def test_k_blocker_winning(cc, action, exp_rew, exp_done):
    fileName = 'rbmConfig1bt'
    task = get_k_blocker_env(fileName)

    task._KBlockerEnv__coords = cc
    task._KBlockerEnv__gap = task._KBlockerEnv__grid_x - 1
    _, rew, done, _y = task.step(action)

    assert task._WIN_REWARD == 5  # Loaded from Config
    assert task._PLAY_REWARD == 0  # Loaded from Config
    assert rew == exp_rew
    assert done == exp_done


# defend
@pytest.mark.parametrize("cc, action, exp_rew, exp_done", [
    ([(0,3),(2,3)], 15, 0, False),#action : (3,3)
    ([(1,3),(3,3)], 15, 0, False)#action : (3,3)
])
def test_k_blocker_defending(cc, action, exp_rew, exp_done):
    fileName = 'rbmConfig1bt'
    task = get_k_blocker_env(fileName)

    task._KBlockerEnv__coords = cc
    task._KBlockerEnv__gap = task._KBlockerEnv__grid_x - 1
    _, rew, done, _ = task.step(action)
    assert rew == exp_rew
    assert done == exp_done
