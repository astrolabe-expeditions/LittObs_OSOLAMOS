# %% Packages
import sys
import json
import logging
import numpy as np

# %% Init logger
logging.basicConfig(filename=sys.path[0] + "/logs/rx_log.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S')


# %% Function
def get_release_tones(rx_id):
    """
    The get_release_tones function takes in a rx_id and returns the release sequence for that id.

    :param rx_id: Find the release tones for that specific id
    :return: The release sequence for a specific id
    """

    # get json payload
    with open("../config/release_sequences.json", encoding="utf-8") as file:
        dictionary = json.load(file)

    # find the id's index
    try:
        return np.array(dictionary[rx_id]["release_tones"])
    except Exception as exc:
        raise FileNotFoundError("There is no release tones for this ID.") from exc
