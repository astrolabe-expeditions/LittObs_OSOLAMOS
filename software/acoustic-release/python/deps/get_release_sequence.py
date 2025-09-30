""" returns the release sequence associated with that id. """
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
def get_release_sequence(rx_id):
    # get json payload
    """
    The get_release_sequence function takes in a rx_id and returns the
    release sequence associated with that id.

    :param rx_id: Find the release sequence in the json file
    :return: An array of release times

    """

    with open(REPO.working_tree_dir + "/config/release_sequences.json", encoding="utf-8") as file:
        dictionary = json.load(file)

    # find the id's index
    try:
        return np.array(dictionary[rx_id]["release_sequence"])
    except Exception as exc:
        raise FileNotFoundError("There is no release sequence for this ID.") from exc
