# %% Packages
import json
import jsbeautifier
import numpy as np
from numpy.random import randint

# %% Parameters
n_sequences = 2048
length_sequence = 13

# %% Generate sequence
sequences = randint(low=0, high=2, size=(n_sequences, length_sequence))
# the first sequence is a 13-Barker Code
sequences[0, :] = np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1])

# Take only unique sequences
_, index_unique = np.unique(np.array([str(e) for e in sequences]), return_index=True)
sequences = sequences[index_unique.sort(), :].reshape(-1, length_sequence)

# convert to list
sequences = sequences.tolist()
n_sequences = len(sequences)

# %% Generate associate index
ids = [str(current_id) for current_id in np.arange(1, n_sequences + 1).tolist()]
release_sequence = [{'release_sequence': current_sequence} for current_sequence in sequences]

# %% Data to be written
nested_dictionary = dict(zip(ids, release_sequence))

# %% Serializing json
options = jsbeautifier.default_options()
options.indent_size = 4
payload = jsbeautifier.beautify(json.dumps(nested_dictionary), options)

# %% Writing to sample.json
with open("../release_sequences.json", "w", encoding="utf-8") as outfile:
    outfile.write(payload)
