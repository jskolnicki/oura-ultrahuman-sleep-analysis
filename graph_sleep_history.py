import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, DateFormatter
import seaborn as sns
import numpy as np

# Read the CSV data
df = pd.read_csv('sleep_history.csv')

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Set date as index
df.set_index('date', inplace=True)

# Calculate monthly average
monthly_avg = df.resample('M').mean()

# Calculate yearly averages
yearly_avg = df.resample('Y').mean()

# Create the plot with a larger figure size
plt.figure(figsize=(20, 12))
sns.set_style("whitegrid")

# Plot monthly average with increased linewidth
plt.plot(monthly_avg.index, monthly_avg['hours_of_sleep_rounded'], color='#1E90FF', linewidth=3)

# Plot yearly trend line with increased linewidth
plt.plot(yearly_avg.index, yearly_avg['hours_of_sleep_rounded'], '--', color='#FFA500', linewidth=3)

# Customize the plot
plt.title('Monthly Average Sleep Duration with Yearly Trend (2019-2024)', fontsize=28)

# Increase spacing and font size for y-axis
plt.ylabel('Average Sleep Duration (hours)', fontsize=20, labelpad=20)

# Increase spacing and font size for x-axis
plt.xlabel('Year', fontsize=20, labelpad=20)

# Adjust y-axis to zoom in slightly
plt.ylim(6, 8)  # Adjust these values as needed to best showcase your data

# Customize x-axis
plt.gca().xaxis.set_major_locator(YearLocator())
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y'))

# Increase font size for tick labels
plt.tick_params(axis='both', which='major', labelsize=18)

# Add legend with increased font size
plt.legend(['Monthly Average', 'Yearly Trend'], loc='upper right', fontsize=20)

# Adjust layout and save the plot
plt.tight_layout()
plt.savefig('results/graphs/sleep_history_graph.png')
plt.show()