import matplotlib.pyplot as plt

# Data from the excel sheet
data = {
    "No Loss": [58.831225, 58.23543, 58.953857, 57.918081, 57.803119],
    "20% Loss in Group A": [78.046877, 80.657627, 86.488579, 81.711281, 80.093459],
    "20% Loss in Group A + 20% 4->13": [84.599063, 94.182634, 117.788265, 97.418326, 121.626372],
    "20% Symmetric 13 All Links": ["DNF", "DNF", "DNF", "DNF", "DNF"],
    "13 Realistic Latency": [59.972937, 59.338416, 60.511138, 59.230787, 67.362425],
    "20% Node 4 All Connections": [76.673712, 68.591516, 91.62073, 66.652211, 71.645492]
}

# Convert "DNF" to None and calculate averages
averages = {}
for key, values in data.items():
    valid_values = [x for x in values if x != "DNF"]
    if valid_values:
        averages[key] = sum(valid_values) / len(valid_values)
    else:
        averages[key] = None

# Prepare data for plotting, excluding None values and sorting by average execution time
sorted_averages = sorted(
    ((label, avg) for label, avg in averages.items() if avg is not None),
    key=lambda x: x[1]
)

labels, average_values = zip(*sorted_averages)

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))

ax.bar(labels, average_values, color='skyblue')

# Set plot title and labels
ax.set_title('Average Execution Times')
ax.set_xlabel('Settings')
ax.set_ylabel('Average Time (seconds)')
ax.set_xticklabels(labels, rotation=45, ha='right')

# Show the plot
plt.tight_layout()
plt.show()