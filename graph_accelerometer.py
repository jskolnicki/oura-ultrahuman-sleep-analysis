import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Generate realistic accelerometer data for walking over 10 seconds with detailed Z-axis dynamics, a very small jump motion, and two slowdown periods with stiffer arms
time_intervals = np.arange(0, 10, 0.05)  # 10 seconds at 50ms intervals

# Walking data with detailed Z-axis dynamics
x_walk = 0.1 * np.sin(2 * np.pi * time_intervals) + np.random.normal(0, 0.05, len(time_intervals))
y_walk = 0.1 * np.cos(2 * np.pi * time_intervals) + np.random.normal(0, 0.05, len(time_intervals))
z_walk = 9.8 + 0.5 * (np.sin(4 * np.pi * time_intervals) + 0.1 * np.sin(2 * np.pi * time_intervals)) + np.random.normal(0, 0.1, len(time_intervals))

# Introduce a very small jump motion in the middle of the dataset
jump_start = len(time_intervals) // 2 - 10
jump_end = len(time_intervals) // 2 + 10

x_jump = np.zeros(jump_end - jump_start)
y_jump = np.zeros(jump_end - jump_start)
z_jump = 9.8 + np.concatenate([
    np.linspace(0, 1, 5),   # Accelerate upwards
    np.linspace(1, 0, 5),   # Reach peak and start to fall
    np.linspace(0, -1, 5),  # Accelerate downwards
    np.linspace(-1, 0, 5)   # Reach bottom and start to rise
]) + np.random.normal(0, 0.1, jump_end - jump_start)

# Introduce a smaller variability period at the beginning of the dataset
slowdown_start_1 = len(time_intervals) // 3 - 10
slowdown_end_1 = slowdown_start_1 + 20

x_slowdown_1 = x_walk[slowdown_start_1:slowdown_end_1] * 0.4  # Reduced variability for stiffer arms
y_slowdown_1 = y_walk[slowdown_start_1:slowdown_end_1] * 0.4  # Reduced variability for stiffer arms
z_slowdown_1 = (9.8 + 0.3 * (np.sin(4 * np.pi * time_intervals[slowdown_start_1:slowdown_end_1]) + 
                0.1 * np.sin(2 * np.pi * time_intervals[slowdown_start_1:slowdown_end_1])) + np.random.normal(0, 0.1, slowdown_end_1 - slowdown_start_1))

# Introduce a slowdown motion towards the end of the dataset with smaller Z-axis peaks and reduced variability in X and Y axes
slowdown_start_2 = len(time_intervals) * 3 // 4
slowdown_end_2 = slowdown_start_2 + 20

x_slowdown_2 = x_walk[slowdown_start_2:slowdown_end_2] * 0.2  # Reduced variability for stiffer arms
y_slowdown_2 = y_walk[slowdown_start_2:slowdown_end_2] * 0.2  # Reduced variability for stiffer arms
z_slowdown_2 = (9.8 + 0.15 * (np.sin(4 * np.pi * time_intervals[slowdown_start_2:slowdown_end_2]) + 
                0.1 * np.sin(2 * np.pi * time_intervals[slowdown_start_2:slowdown_end_2])) + np.random.normal(0, 0.1, slowdown_end_2 - slowdown_start_2))

# Combine walking, jumping, and slowdown data
x_combined = np.concatenate([x_walk[:slowdown_start_1], x_slowdown_1, x_walk[slowdown_end_1:jump_start], x_jump, x_walk[jump_end:slowdown_start_2], x_slowdown_2, x_walk[slowdown_end_2:]])
y_combined = np.concatenate([y_walk[:slowdown_start_1], y_slowdown_1, y_walk[slowdown_end_1:jump_start], y_jump, y_walk[jump_end:slowdown_start_2], y_slowdown_2, y_walk[slowdown_end_2:]])
z_combined = np.concatenate([z_walk[:slowdown_start_1], z_slowdown_1, z_walk[slowdown_end_1:jump_start], z_jump, z_walk[jump_end:slowdown_start_2], z_slowdown_2, z_walk[slowdown_end_2:]])

# Create a DataFrame with the combined data
data_combined = pd.DataFrame({
    'Timestamp': pd.date_range(start='2024-06-30 12:00:00', periods=len(time_intervals), freq='50ms'),
    'X-axis': x_combined,
    'Y-axis': y_combined,
    'Z-axis': z_combined
})

# Plot the data for X, Y, and Z axes
fig, axs = plt.subplots(3, 1, figsize=(15, 10), sharex=True)

axs[0].plot(data_combined['Timestamp'], data_combined['X-axis'], label='X-axis', color='red')
axs[0].set_ylabel('Acceleration (m/s²)')
axs[0].set_title('X-axis Acceleration')

axs[1].plot(data_combined['Timestamp'], data_combined['Y-axis'], label='Y-axis', color='green')
axs[1].set_ylabel('Acceleration (m/s²)')
axs[1].set_title('Y-axis Acceleration')

axs[2].plot(data_combined['Timestamp'], data_combined['Z-axis'], label='Z-axis', color='blue')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Acceleration (m/s²)')
axs[2].set_title('Z-axis Acceleration')

for ax in axs:
    ax.grid(True)
    ax.legend()
    ax.set_xticklabels(data_combined['Timestamp'], rotation=45)

plt.tight_layout()
plt.savefig('results/graphs/sleep_history_graph1.png')
plt.show()