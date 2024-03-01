# Get network lists from AS name or Network name

## Description

* If you know AS name, use the script `network_list_from_as.py` to get the list of networks.
* If you know the network name, use the script `network_list_from_netname.py` to get the list of networks.


**Note:** This scripts has been tested on MacOS and Linux.

## Prerequisites

- Python 3: You can download it from the [official website](https://www.python.org/downloads/).

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/C24Be/AS_Network_List.git
    ```

2. Navigate to the repository folder:

    ```bash
    cd AS_Network_List
    ```

3. Install the required Python packages:

    ```bash
    ./requirements.sh
    ```

## Usage of the `network_list_from_as.py` script

1. Run the script with the AS number as an argument:

    ```bash
    python network_list_from_as.py AS61280
    ```

2. To disable all output except the prefixes, use the `--quiet` or `-q` switch:

    ```bash
    python network_list_from_as.py AS61280 -q
    ```

3. To print a help message, use the `-h` or `--help` switch:

    ```bash
    python network_list_from_as.py --help
    ```

## Usage of the `network_list_from_netname.py` script

1. Run the script with the list of network names in a file as an argument:

    ```bash
    python network_list_from_netname.py files/blacklist4.txt
    ```

2. Run the script with the list of network names in the github repository as an argument:

    ```bash
    python network_list_from_netname.py https://github.com/AntiZapret/antizapret/blob/master/blacklist4.txt
    ```

    or better use the raw file link:

    ```bash
    python network_list_from_netname.py https://raw.githubusercontent.com/AntiZapret/antizapret/master/blacklist4.txt
    ```

3. To print a help message, use the `-h` or `--help` switch:

    ```bash
    python network_list_from_netname.py --help
    ```

## Screenshots

![Screenshot](https://github.com/C24Be/AS_Network_List/assets/153936414/574b072c-9104-4e02-b2c0-3609433bdfc4)
