import numpy as np
import matplotlib.pyplot as plt
import pickle
from simulation_setup import underwater_paths, pulse, sample_rate, dt, simulate_sonar_return

with open('actual_positions.pkl', 'rb') as f:
    actual_positions = pickle.load(f)
with open('ukf_states.pkl', 'rb') as f:
    ukf_states = pickle.load(f)

def plot_results(ukf_states, actual_positions, title, filename):
    plt.figure(figsize=(12, 8))
    plt.plot(ukf_states[:, 0], ukf_states[:, 1], 'r-', label='UKF Estimate')
    plt.plot([pos[0][0] for pos in actual_positions], [pos[0][1] for pos in actual_positions], 'b-', label='Actual Path')
    plt.xlabel('X position (m)')
    plt.ylabel('Y position (m)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.show()

plot_results(ukf_states, actual_positions, "UKF Tracking Results - Best Tuned Parameters", 'ukf_tracking_results.png')

plt.figure(figsize=(12, 8))
for r, z in underwater_paths:
    plt.plot(r, -z, 'b-', alpha=0.3)
for i, target_positions in enumerate(zip(*actual_positions)):
    x = [pos[0] for pos in target_positions]
    z = [-pos[2] for pos in target_positions]
    plt.plot(x, z, '-o', label=f'Target {i+1}')
plt.xlabel('Range (m)')
plt.ylabel('Depth (m)')
plt.title('Underwater Sound Paths and Target Trajectories')
plt.legend()
plt.grid(True)
plt.gca().invert_yaxis()
plt.savefig('underwater_paths_and_trajectories.png')
plt.show()

rx_pulses = np.zeros((len(pulse), len(actual_positions)))
for j in range(len(actual_positions)):
    for pos in actual_positions[j]:
        rx_pulses[:, j] += simulate_sonar_return(pos, pulse, sample_rate, underwater_paths, j * dt)

plt.figure(figsize=(12, 6))
plt.imshow(np.abs(rx_pulses), aspect='auto', extent=[0, len(actual_positions)*dt, 0, len(pulse)/sample_rate*1000], 
           cmap='viridis', origin='lower')
plt.colorbar(label='Amplitude')
plt.xlabel('Time (s)')
plt.ylabel('Delay (ms)')
plt.title('Received Non-Constant SONAR Pulses with Underwater Paths')
plt.savefig('received_sonar_pulses.png')
plt.show()

final_position = actual_positions[-1][0][:2]
final_estimate = ukf_states[-1, :2]
error = np.linalg.norm(final_position - final_estimate)
print(f"Best estimation error: {error:.2f} meters")
best_Q = np.array([[0.001, 0, 0, 0], 
                   [0, 0.001, 0, 0], 
                   [0, 0, 0.001, 0], 
                   [0, 0, 0, 0.001]])
best_R = np.array([[0.2]])
best_P = np.eye(4) * 1

print(f"Best Q: {best_Q}")
print(f"Best R: {best_R}")
print(f"Best P: {best_P}")