#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "${SCRIPT_DIR}/blacklists_updater_common.subr"

# Output directory and files
nginx_output_dir="${SCRIPT_DIR}/blacklists_nginx"
nginx_output_file="${nginx_output_dir}/blacklist.conf"
nginx_v4_output_file="${nginx_output_dir}/blacklist-v4.conf"
nginx_v6_output_file="${nginx_output_dir}/blacklist-v6.conf"

# Create required directories if they don't exist
mkdir -p "${nginx_output_dir}" "${BLACKLISTS_DIR}"

# Function to generate nginx config from input file
generate_nginx_config() {
    local input_file="$1"
    local output_file="$2"
    local ip_version="$3"

    # Generate nginx configuration with header
    cat > "${output_file}" << EOF
# Nginx blacklist configuration ${ip_version}
# Auto-generated from $(basename ${input_file})
# Last updated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
#
# Usage: Include this file in your nginx server or location block:
#   include /path/to/$(basename ${output_file});
#

EOF

    # Add deny directives for each network/IP
    while IFS= read -r network; do
        # Skip empty lines
        [ -z "${network}" ] && continue
        echo "deny ${network};" >> "${output_file}"
    done < "${input_file}"

    # Add final newline
    echo "" >> "${output_file}"

    echo "✓ Generated ${ip_version}: ${output_file}"
    echo "  Total entries: $(grep -c "deny" "${output_file}")"
}

# Generate nginx configurations from blacklist files
generate_nginx_config "${BLACKLIST_FILE}" "${nginx_output_file}" "(mixed IPv4/IPv6)"
generate_nginx_config "${BLACKLIST_V4_FILE}" "${nginx_v4_output_file}" "(IPv4 only)"
generate_nginx_config "${BLACKLIST_V6_FILE}" "${nginx_v6_output_file}" "(IPv6 only)"
