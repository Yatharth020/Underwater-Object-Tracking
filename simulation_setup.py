import numpy as np
import pickle

max_depth = 1000
max_range = 5000
num_rays = 20
frequency = 20e3
pulse_width = 0.01
sample_rate = 2 * frequency
timesteps = 50
dt = 1

initial_positions = [np.array([500, 500, -70]), np.array([500, 20, -40])]
velocities = [np.array([1, 3, 0]), np.array([2, 0, 0])]

def sound_speed_profile(z):
    return 1500 + 0.017 * z

def trace_ray(initial_angle, max_range, max_depth):
    num_steps = 1000
    r = np.linspace(0, max_range, num_steps)
    z = r * np.tan(initial_angle)
    z = np.where(z < 0, -z, z)
    z = np.where(z > max_depth, 2 * max_depth - z, z)
    return r, z

initial_angles = np.linspace(-np.pi/6, np.pi/6, num_rays)
underwater_paths = [trace_ray(angle, max_range, max_depth) for angle in initial_angles]

def generate_pulse(frequency, pulse_width, sample_rate):
    t = np.arange(0, pulse_width, 1/sample_rate)
    fm = 1000
    beta = 0.5
    pulse = np.sin(2 * np.pi * frequency * t + beta * np.sin(2 * np.pi * fm * t))
    return pulse

pulse = generate_pulse(frequency, pulse_width, sample_rate)

def simulate_sonar_return(target_position, pulse, sample_rate, underwater_paths, time):
    received_signal = np.zeros_like(pulse)
    for path in underwater_paths:
        r, z = path
        dist_to_target = np.sqrt((r - target_position[0])**2 + (z - target_position[2])**2)
        closest_index = np.argmin(dist_to_target)
        distance = dist_to_target[closest_index]
        if distance > max_range:
            continue
        sound_speed = sound_speed_profile(z[closest_index])
        time_delay = distance / sound_speed
        samples_delay = int(time_delay * sample_rate)
        attenuation = np.exp(-0.001 * distance * (1 + 0.1 * np.sin(2 * np.pi * 0.1 * time)))
        doppler_factor = 1 + np.random.normal(0, 0.01)
        t = np.arange(0, len(pulse)) / sample_rate
        doppler_pulse = np.interp(t * doppler_factor, t, pulse)
        if 0 <= samples_delay < len(pulse):
            path_signal = attenuation * np.pad(doppler_pulse, (samples_delay, 0), 'constant')[:len(pulse)]
            received_signal += path_signal
    noise = np.random.normal(0, 0.01, len(received_signal))
    received_signal += noise
    return received_signal

def simulate_movement_and_measurements():
    np.random.seed(0)
    actual_positions = [initial_positions]
    measurements = [measurement_function(initial_positions[0][:2]) + np.random.normal(0, 0.1)]
    for _ in range(1, timesteps):
        new_positions = []
        for pos, vel in zip(actual_positions[-1], velocities):
            new_pos = pos + vel * dt
            new_pos[0] = np.clip(new_pos[0], 0, max_range)
            new_pos[2] = np.clip(new_pos[2], -max_depth, 0)
            new_positions.append(new_pos)
        actual_positions.append(new_positions)
        measurements.append([measurement_function(pos[:2]) + np.random.normal(0, 0.1) for pos in new_positions])
    return actual_positions, measurements

def state_transition(x, dt):
    F = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])
    return F @ x

def measurement_function(x):
    px, py = x[0], x[1]
    bearing = np.arctan2(py, px)
    return np.array([bearing])

if __name__ == "__main__":
    actual_positions, measurements = simulate_movement_and_measurements()
    with open('actual_positions.pkl', 'wb') as f:
        pickle.dump(actual_positions, f)
    with open('measurements.pkl', 'wb') as f:
        pickle.dump(measurements, f)
    print("Simulation data saved.")
