# %% Packages
import json
import jsbeautifier

# %% Data to be written
dictionary = {
    "waveform": {"pulse_width": 0.8,
                 "pulse_repetition_interval": 1,
                 "carrier_frequency": 10_000,
                 "frequency_shift": 400
                 },
    "processing": {"threshold_wake_up": 4,
                   "threshold_release": 4,
                   "n_sample_buffer": 500,
                   "n_sample_step": 128,
                   "sample_rate": 48_000
                   },
}

# %% Serializing json
options = jsbeautifier.default_options()
options.indent_size = 4
payload = jsbeautifier.beautify(json.dumps(dictionary), options)

# %% Writing to sample.json
with open("../config.json", "w", encoding="utf-8") as outfile:
    outfile.write(payload)
