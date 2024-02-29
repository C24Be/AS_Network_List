# AS Prefixes List Script

## Description

* This Python script retrieves and prints the prefixes announced by a specified Autonomous System (AS). It uses the RIPE Stat Data API to fetch the data.

* Tested only on MacOS and Linux :)

## Installation

1. Make sure you have Python 3 installed. You can download it from the [official website](https://www.python.org/downloads/).

2. Clone this repository:

    ```bash
    git clone https://github.com/C24Be/AS_Network_List.git
    ```

3. Navigate to the repository folder:

    ```bash
    cd AS_Network_List
    ```

4. Install requirements:

    ```bash
    ./requirements.sh
    ```

## Usage

1. Run the script with the AS number as an argument:

    ```bash
    python as_network_list.py AS61280
    ```

2. If you want to disable all output except the prefixes, use the --quiet or -q switch:

    ```bash
    python as_network_list.py AS61280 --quiet
    ```

3. If you run the script with the -h or --help switch, it will print a help message:

    ```bash
    python as_network_list.py --help
    ```
