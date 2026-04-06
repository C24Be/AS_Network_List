#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "${SCRIPT_DIR}/blacklists_updater_common.subr"

ensure_blacklist_base_dirs

grep -iE "${BLACK_NAMES}" "${AUTO_ALL_ASN_FILE}" | grep -viE "${WHITE_NAMES}" | awk '{ print "# AS-Name: " $0 "\n" $1}' > "${AUTO_BLACK_ASS_FILE}"
"${NETWORK_LIST_FROM_AS}" "${AUTO_BLACK_ASS_FILE}" > "${BLACKLIST_WITH_COMMENTS_FILE}"
"${NETWORK_LIST_FROM_NETNAME}" "${RU_GOV_NETNAMES_FILE}" >> "${BLACKLIST_WITH_COMMENTS_FILE}"
grep -iE "${BLACK_NAMES}" "${AUTO_ALL_V4_FILE}"  | grep -viE "${WHITE_NAMES}" | awk '{ print "# NET-Name: " $0 "\n" $1}' >> "${BLACKLIST_WITH_COMMENTS_FILE}"
grep -iE "${BLACK_NAMES}" "${AUTO_RIPE_V4_FILE}" | grep -viE "${WHITE_NAMES}" | awk '{ print "# NET-Name: " $0 "\n" $1}' >> "${BLACKLIST_WITH_COMMENTS_FILE}"

# Remove comments by sed to avoid flooding WHOIS servers
grep -v "#" "${BLACKLIST_WITH_COMMENTS_FILE}" | sort | uniq > "${BLACKLIST_FILE}"

# Split blacklist into IPv4 and IPv6
grep ':' "${BLACKLIST_FILE}" | sort | uniq > "${BLACKLIST_V6_FILE}"
grep -v ':' "${BLACKLIST_FILE}" | sort | uniq > "${BLACKLIST_V4_FILE}"

echo "✓ Generated blacklist files"
echo "  Mixed (IPv4/IPv6): ${BLACKLIST_FILE} ($(wc -l < "${BLACKLIST_FILE}" | tr -d ' ') entries)"
echo "  IPv4 only: ${BLACKLIST_V4_FILE} ($(wc -l < "${BLACKLIST_V4_FILE}" | tr -d ' ') entries)"
echo "  IPv6 only: ${BLACKLIST_V6_FILE} ($(wc -l < "${BLACKLIST_V6_FILE}" | tr -d ' ') entries)"
