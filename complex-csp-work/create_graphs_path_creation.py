import numpy as np
import matplotlib.pyplot as plt

# Data for Path Creation Model A (After 100 trials).
x_1 = np.array([694.54, 976.76, 1217.90, 1297.77, 1306.25])
y_1 = np.array([1, 2, 3, 4, 5])

# Data for Path Creation Model B (After 100 trials).
x_2 = np.array([581.83, 941.23, 1290.57, 1600.52, 1893.17])
y_2 = np.array([1, 2, 3, 4, 5])

# Plot the lines and create the graph.
plt.plot(x_1, y_1, label="Path Creation Model A")
plt.plot(x_2, y_2, label="Path Creation Model B")
plt.xlabel('Number of iterations')
plt.ylabel('Number of paths created')
plt.legend()
plt.show()
