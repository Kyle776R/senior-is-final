import numpy as np
import matplotlib.pyplot as plt

# # Data for Algorithm #1 (After 50 trials).
# x_1 = np.array([9, 16, 25, 36, 49])
# y_1 = np.array([297.96, 413.74, 589.6, 784.32, 1243])
#
# # Data for Algorithm #2 (After 50 trials).
# x_2 = np.array([9, 16, 25, 36, 49])
# y_2 = np.array([279.32, 535.58, 1096.34, 1783.42, 5465.33])

# Data for Algorithm #1 (After 100 trials).
# Line of best fit: y = 23.99x + 26.82
x_1 = np.array([9, 16, 25, 36, 49])
y_1 = np.array([286.5, 417.86, 589.94, 805.7, 1273.27])

# Data for Algorithm #2 (After 100 trials).
# Line of best fit: y = 141.12x - 1798.97
x_2 = np.array([9, 16, 25, 36, 49])
y_2 = np.array([282.46, 541.52, 1052.14, 1825.45, 6355.25])

# Plot the lines and create the graph.
plt.plot(x_1, y_1, label="Algorithm #1")
plt.plot(x_2, y_2, label="Algorithm #2")
plt.xlabel('Number of pickups')
plt.ylabel('Number of iterations')
plt.legend()
plt.show()
