"""Named constants used throughout the model."""

import numpy as np

MR_ORIFICE_CONSTANT = 50.16
SIGMOID_CLIP = 500.0
VALVE_OPEN_THRESHOLD = 20.0
CONVERGENCE_TOL = 1e-3
INITIAL_VOLUMES = np.array([120.0, 60.0, 120.0, 60.0,
                             900.0, 3200.0, 170.0, 370.0])
