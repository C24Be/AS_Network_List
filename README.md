# AS Network List

## Description

This Python script retrieves and prints the network prefixes announced by a specified Autonomous System (AS). It leverages the RIPE Stat Data API to fetch the data.

**Note:** This script has been tested on MacOS and Linux.

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

## Usage

1. Run the script with the AS number as an argument:

    ```bash
    python as_network_list.py AS61280
    ```

2. To disable all output except the prefixes, use the `--quiet` or `-q` switch:

    ```bash
    python as_network_list.py AS61280 --quiet
    ```

3. To print a help message, use the `-h` or `--help` switch:

    ```bash
    python as_network_list.py --help
    ```

## Screenshot

![Screenshot](https://github.com/C24Be/AS_Network_List/assets/153936414/574b072c-9104-4e02-b2c0-3609433bdfc4)

