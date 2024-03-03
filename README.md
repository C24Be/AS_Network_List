# Russian government agencies and their associated networks.

This repository contains Python scripts that allow you to retrieve network lists based on either an Autonomous System (AS) name or a Network name. Also you can download and parse the whole RIPE database to get information about Networks for the further analysis.

- [Look at compiled lists and blacklists in the folder `auto/`](https://github.com/C24Be/AS_Network_List/tree/main/auto)

## Files and features

- `network_list_from_as.py`: Retrieves a list of networks associated with a given AS name.
- `network_list_from_netname.py`: Retrieves a list of networks associated with a given Network name.
- `get_info_from_ripe.py`: Retrieves information about Russian AS numbers and Networks from RIPE database for the further analysis.
- `get_description.py`: Retrieves network names, AS names and organisation names from RIPE. Updates te lists in the folder `auto/`.
- `parse_ripe_db.py`: Parses the whole RIPE database to get information about Networks for the further analysis.

- **Contributors are welcome!**
  - `lists/ru-gov-netnames.txt`: A list of network names associated with the Russian government.
  - `lists/ru-gov-asns.txt`: A list of AS numbers associated with the Russian government.

- `blacklist_updater.sh`: Static blacklist updater.

- `auto/blacklist.txt`: Static **daily generated** blacklist!
- `auto/blacklist_with_comments.txt`: Static **daily generated** blacklist with comments!
- `auto/all-ru-*.txt`: Static **monthly generated** lists of Russian networks and ASNs!
- `auto/ripe-db-*.txt`: Static **weekly generated** lists of Russian networks from RIPE database!

<img width="240" alt="image" src="https://github.com/C24Be/AS_Network_List/assets/153936414/2ec89fa9-b39a-416d-b1a1-20ddc89377ed">

These scripts have been tested on MacOS, FreeBSD and Linux.

## Prerequisites

- Python 3: Download it from the [official website](https://www.python.org/downloads/).

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

    If this step causes issue `PEP 668` due to python version >=3.12 and you're unfamiliar with virtual environments, use this workaround:

    ```bash
    pip install -r requirements.txt --break-system-packages
    ```

## Usage

### `network_list_from_as.py`

1. Run the script with the AS number as an argument:

    ```bash
    ./network_list_from_as.py AS61280
    ```

2. Run the script with a URL to a file in a GitHub repository as an argument:

    ```bash
    ./network_list_from_as.py https://github.com/C24Be/AS_Network_List/blob/main/lists/ru-gov-asns.txt
    ```

    Or better use the raw file link:

    ```bash
    ./network_list_from_as.py https://raw.githubusercontent.com/C24Be/AS_Network_List/main/lists/ru-gov-asns.txt
    ```

3. To display a help message, use the `-h` or `--help` switch:

    ```bash
    ./network_list_from_as.py --help
    ```

### `network_list_from_netname.py`

1. Run the script with a file containing a list of network names as an argument:

    ```bash
    ./network_list_from_netname.py lists/ru-gov-netnames.txt
    ```

2. Run the script with a URL to a file in a GitHub repository as an argument:

    ```bash
    ./network_list_from_netname.py https://github.com/C24Be/AS_Network_List/blob/main/lists/ru-gov-netnames.txt
    ```

    Or better use the raw file link:

    ```bash
    ./network_list_from_netname.py https://raw.githubusercontent.com/C24Be/AS_Network_List/main/lists/ru-gov-netnames.txt
    ```

3. To display a help message, use the `-h` or `--help` switch:

    ```bash
    ./network_list_from_netname.py --help
    ```

## Screenshots

<img width="320" alt="image" src="https://github.com/C24Be/AS_Network_List/assets/153936414/71bd0ed4-0e9b-42f0-8e91-01964ea9b8e1">
<img width="1280" alt="image" src="https://github.com/C24Be/AS_Network_List/assets/153936414/e305bbca-ea76-47ff-971c-3a61a61cea70">

## Additional information

- [RIPE DB Inetnum](https://ftp.ripe.net/ripe/dbase/split/ripe.db.inetnum.gz)

## Contributing

We are welcome contributions! Feel free to submit a pull request or open an issue.
