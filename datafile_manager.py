"""
File: datafile_manager.py

Description: Helper module for interaction with the testing and training data
files. Not to be confused with weightsfile_manager.py
"""


def save_data(data, filename):
    data = "\n".join(str(k) + ":" + str(v) for k, v, in data.iteritems()) + "\n"

    save_file = open(filename, "w")
    save_file.write(data)
    save_file.close()


def load_data(filename):
    save_file = open(filename, "r")
    data = save_file.readlines()
    save_file.close()

    data = [entry[:-1].split(":") for entry in data]
    data = {k: float(v) for k, v in data}

    return data


if __name__ == "__main__":
    pass
