# Russian government agencies and their associated networks.

### Blacklists are updated daily!

This repository contains Python scripts that allow you to retrieve network lists based on either an Autonomous System (AS) name or a Network name. Also you can download and parse the whole RIPE database to get information about Networks for the further analysis.

**Ready-to-use blacklists in multiple formats:**

- [Text blacklists in `blacklists/`](https://github.com/C24Be/AS_Network_List/tree/main/blacklists) - Plain text format with IPv4/IPv6 separation
- [Nginx configurations in `blacklists_nginx/`](https://github.com/C24Be/AS_Network_List/tree/main/blacklists_nginx) - Ready to include in your nginx config
- [IPTables/IPSet files in `blacklists_iptables/`](https://github.com/C24Be/AS_Network_List/tree/main/blacklists_iptables) - Optimized for iptables with ipset
- [Other network and ASN lists in `auto/`](https://github.com/C24Be/AS_Network_List/tree/main/auto) - Comprehensive Russian network data

## Files and features

### Core Scripts

- `network_list_from_as.py`: Retrieves a list of networks associated with a given AS name.
- `network_list_from_netname.py`: Retrieves a list of networks associated with a given Network name.
- `get_info_from_ripe.py`: Retrieves information about Russian AS numbers and Networks from RIPE database for the further analysis.
- `get_description.py`: Retrieves network names, AS names and organisation names from RIPE. Updates the lists in the folder `auto/`.
- `parse_ripe_db.py`: Parses the whole RIPE database to get information about Networks for the further analysis.
- `generate_nft_blacklist.py`: Takes text blacklist on the input and generates nftables config with sets.
- `check_nft_blacklist.py`: Checks IPv4/IPv6 address against generated nftables config.

### Blacklist Generators

- `blacklists_updater_txt.sh`: Generates text-based blacklists with IPv4/IPv6 separation
- `blacklists_updater_nginx.sh`: Generates nginx configuration files with deny directives
- `blacklists_updater_iptables.sh`: Generates ipset configuration files for iptables/ip6tables

### Generated Blacklists

**Text Format** (`blacklists/` folder):

- `blacklist.txt`: Mixed IPv4/IPv6 blacklist (**daily generated**)
- `blacklist-v4.txt`: IPv4-only blacklist (**daily generated**)
- `blacklist-v6.txt`: IPv6-only blacklist (**daily generated**)
- `blacklist_with_comments.txt`: Blacklist with network metadata (**daily generated**)

**Nginx Format** (`blacklists_nginx/` folder):

- `blacklist.conf`: Nginx deny rules for mixed IPv4/IPv6 (**daily generated**)
- `blacklist-v4.conf`: Nginx deny rules for IPv4 only (**daily generated**)
- `blacklist-v6.conf`: Nginx deny rules for IPv6 only (**daily generated**)
- `README.md`: Complete usage documentation for nginx integration

**IPTables/IPSet Format** (`blacklists_iptables/` folder):

- `blacklist.ipset`: IPSet configuration for mixed IPv4/IPv6 (**daily generated**)
- `blacklist-v4.ipset`: IPSet configuration for IPv4 only (**daily generated**)
- `blacklist-v6.ipset`: IPSet configuration for IPv6 only (**daily generated**)
- `README.md`: Complete usage documentation for iptables integration

**nftables Format** (`blacklists_nftables/` folder):

* `blacklist.nft`: nftables configuration for mixed IPv4/IPv6 (**daily generated**)
* `blacklist-v4.nft`: nftables configuration for IPv4 only (**daily generated**)
* `blacklist-v6.nft`: nftables configuration for IPv6 only (**daily generated**)
* `README.md`: Complete usage documentation for nftables integration


### Reference Lists

**Contributors are welcome!**

- `lists/ru-gov-netnames.txt`: A list of network names associated with the Russian government.
- `lists/ru-gov-asns.txt`: A list of AS numbers associated with the Russian government.

### Auto-Generated Data

- `auto/all-ru-*.txt`: **Monthly generated** lists of all Russian networks and ASNs
- `auto/ripe-ru-*.txt`: **Weekly generated** lists of Russian networks from RIPE database

<img width="240" alt="image" src="https://github.com/C24Be/AS_Network_List/assets/153936414/2ec89fa9-b39a-416d-b1a1-20ddc89377ed">

These scripts have been tested on MacOS, FreeBSD and Linux.

## Quick Start

### Using Pre-Generated Blacklists

No setup required! Just download and use:

**For Nginx:**

```bash
# Download and include in your nginx configuration
wget https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists_nginx/blacklist.conf
# Then add to your nginx config: include /path/to/blacklist.conf;
```

**For IPTables/IPSet:**

```bash
# Download and load into ipset
wget https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists_iptables/blacklist.ipset
ipset restore < blacklist.ipset
iptables -I INPUT -m set --match-set blacklist-v4 src -j DROP
ip6tables -I INPUT -m set --match-set blacklist-v6 src -j DROP
```

**For nftables:**
````bash
# Download and load into nftables
wget https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists_nftables/blacklist.nft
sudo nft -f blacklist.nft
# View the loaded rules
sudo nft list ruleset
````

**For Custom Applications:**

```bash
# Download plain text blacklist
wget https://raw.githubusercontent.com/C24Be/AS_Network_List/main/blacklists/blacklist.txt
```

See the README files in each folder for detailed usage instructions.

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

### `generate_nft_blacklist.py`
1. Generate nftables config from blacklist:

    ```bash
    ./generate_nft_blacklist.py blacklists/blacklist.txt blacklist.nft
    ```

### `check_nft_blacklist.py`
1. Check IP address against generated config:

    ```bash
    ./check_nft_blacklist.py blacklist.nft 77.37.166.239
    ```

## Screenshots

<img width="320" alt="image" src="https://github.com/C24Be/AS_Network_List/assets/153936414/71bd0ed4-0e9b-42f0-8e91-01964ea9b8e1">
<img width="1280" alt="image" src="https://github.com/C24Be/AS_Network_List/assets/153936414/e305bbca-ea76-47ff-971c-3a61a61cea70">

## Automated Workflows

This repository uses GitHub Actions to automatically update blacklists:

- **Daily Updates**: `update_blacklists.yml` - Updates all blacklist formats (text, nginx, iptables)
- **Monthly Updates**: `update_ru_all_lists.yml` - Updates comprehensive Russian network lists
- **Weekly Updates**: `parse_ripe_database.yml` - Parses RIPE database for Russian networks
- **Network Resolution**: `resolve_networks.yml` - Resolves network names and descriptions

All blacklists are automatically regenerated and committed to ensure you always have the latest data.

## Blacklist Format Comparison

| Format | Best For | Performance | Ease of Use | File Size |
|--------|----------|-------------|-------------|-----------|
| **Text** | Custom scripts, analysis | N/A | ⭐⭐⭐⭐⭐ | Small |
| **Nginx** | Web servers, reverse proxies | Good | ⭐⭐⭐⭐ | Medium |
| **IPSet** | Firewalls, large-scale blocking | Excellent | ⭐⭐⭐ | Medium |

**Recommendation**: Use IPSet for firewall-level blocking (best performance), Nginx for web application layer, and text format for custom integrations.

## Additional information

- [RIPE DB Inetnum](https://ftp.ripe.net/ripe/dbase/split/ripe.db.inetnum.gz)

## Contributing

We welcome contributions! Feel free to submit a pull request or open an issue.
