import json

# Data to be written
dictionnary = {
    "waveform": {"pulse_width" : 0.8,
                 "pulse_repetition_interval" : 1,
                 "carrier_frequency" : 10_000,
                 "frequency_shift" : 400
                 },
    "processing": {"threshold_wake_up": 4,
                   "threshold_release": 4,
                   "n_sample_buffer": 128,
                   "n_sample_step": 50,
                   "wake_up_tone": [9_250, 10_000, 10_750]
                   },
    "rx_id": 1,
    "release_sequence": [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]

}
 
# Serializing json
payload = json.dumps(dictionnary, indent=4)
 
# Writing to sample.json
with open("config.json", "w") as outfile:
    outfile.write(payload)