# %% Packages
import sys
import json
import logging
import git
import numpy as np

# %% Init logger
REPO = git.Repo('.', search_parent_directories=True)
logging.basicConfig(filename=sys.path[0] + "/logs/rx_log.log",
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    datefmt='%d-%b-%y %H:%M:%S')


# %% Function
def get_wake_up_tones(rx_id):

    """
    The get_wake_up_tones function takes in a rx_id and returns the
        wake-up tones associated with that id.

    :param rx_id: Find the release sequence in the json file
    :return: The wake-up tones for a given rx_id

    """

    # get json payload
    with open(REPO.working_tree_dir + "/config/release_sequences.json", encoding="utf-8") as file:
        dictionary = json.load(file)

    # find the id's index
    try:
        return np.array(dictionary[rx_id]["wake_up_tones"])
    except Exception as exc:
        raise FileNotFoundError("There is no wake up tones for this ID.") from exc
