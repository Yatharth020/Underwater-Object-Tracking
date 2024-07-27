import numpy as np
import pickle
from filterpy.kalman import UnscentedKalmanFilter, MerweScaledSigmaPoints
from simulation_setup import state_transition, measurement_function

def run_ukf(initial_state, P, R, Q, measurements):
    points = MerweScaledSigmaPoints(4, alpha=0.1, beta=2., kappa=1.)
    ukf = UnscentedKalmanFilter(dim_x=4, dim_z=1, dt=1, hx=measurement_function, fx=state_transition, points=points)
    ukf.x = initial_state
    ukf.P = P
    ukf.R = R
    ukf.Q = Q
    ukf_states = []
    for measurement in measurements:
        ukf.predict()
        ukf.update(measurement[0])
        ukf_states.append(ukf.x)
    ukf_states = np.array(ukf_states)
    return ukf_states

if __name__ == "__main__":
    best_Q = np.array([[0.001, 0, 0, 0], 
                       [0, 0.001, 0, 0], 
                       [0, 0, 0.001, 0], 
                       [0, 0, 0, 0.001]])
    best_R = np.array([[0.2]])
    best_P = np.eye(4) * 1

    initial_state = np.array([500, 500, 1, 3])
    with open('actual_positions.pkl', 'rb') as f:
        actual_positions = pickle.load(f)
    with open('measurements.pkl', 'rb') as f:
        measurements = pickle.load(f)

    ukf_states = run_ukf(initial_state, best_P, best_R, best_Q, measurements)
    with open('ukf_states.pkl', 'wb') as f:
        pickle.dump(ukf_states, f)
    print("UKF states saved.")
