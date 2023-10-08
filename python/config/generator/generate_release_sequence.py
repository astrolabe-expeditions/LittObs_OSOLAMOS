# %% Packages
import numpy as np
import json

from numpy.random import randint

# %% Parameters
n_sequences = 2048
length_sequence = 13

# %% Generate sequence
sequences = randint(low=0, high=2, size=(2048, 13))
# first sequence is a 13-Barker Code
sequences[0, :] = np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1])
# convert to list
sequences = sequences.tolist()

# %% Generate associate index
ids = [str(current_id) for current_id in np.arange(1, n_sequences + 1).tolist()]

# %% Data to be written
dictionary = {
    "rx_id": ids,
    "release_sequence": sequences,
}

# %% Serializing json
payload = json.dumps(dictionary, indent=4)

# %% Writing to sample.json
with open("../release_sequences.json", "w") as outfile:
    outfile.write(payload)
