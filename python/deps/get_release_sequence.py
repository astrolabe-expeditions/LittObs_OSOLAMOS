# %% Packages
import json
import logging
import numpy as np

# %% Init logger
logging.basicConfig(filename="./logs/rx_log.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S')


# %% Function
def get_release_sequence(rx_id):
    # get json payload
    dictionary = json.load(open("./config/release_sequences.json"))

    # get parameters inside payload
    release_sequences = dictionary["release_sequence"]
    rx_id_index = dictionary["rx_id"]

    # find the id's index
    try:
        index_rx_id = rx_id_index.index(rx_id)
        return np.array(release_sequences[index_rx_id])

    except:
        logging.error("There is no release sequence for this ID.")
        raise "There is no release sequence for this ID."
