#!/bin/sh

outfile_wo_comments="blacklists/blacklist.txt"
outfile_w_comments="blacklists/blacklist_with_comments.txt"
blacklist_v4_file="blacklists/blacklist-v4.txt"
blacklist_v6_file="blacklists/blacklist-v6.txt"

auto_black_ass="auto/black_ass.txt"

black_names="uvd|umvd|fgup|grchc|roskomnad|federalnaya sluzhba|ufsb|zonatelecom|llc vk|vkontakte|ODNOKLASSNIKI|VKCOMPANY|mail.ru|mail-ru|mail_ru|VK-AS"
white_names="ruvds"

grep -iE "${black_names}" auto/all-ru-asn.txt   | grep -viE "${white_names}" | awk '{ print "# AS-Name: " $0 "\n" $1}' > ${auto_black_ass}
./network_list_from_as.py ${auto_black_ass} > ${outfile_w_comments}
./network_list_from_netname.py lists/ru-gov-netnames.txt >> ${outfile_w_comments}
grep -iE "${black_names}" auto/all-ru-ipv4.txt  | grep -viE "${white_names}" | awk '{ print "# NET-Name: " $0 "\n" $1}' >> ${outfile_w_comments}
grep -iE "${black_names}" auto/ripe-ru-ipv4.txt | grep -viE "${white_names}" | awk '{ print "# NET-Name: " $0 "\n" $1}' >> ${outfile_w_comments}

# Remove comments by sed to avoid flooding WHOIS servers
grep -v "#" ${outfile_w_comments} | sort | uniq > ${outfile_wo_comments}

# Split blacklist into IPv4 and IPv6
grep ':' "${outfile_wo_comments}" | sort | uniq > "${blacklist_v6_file}"
grep -v ':' "${outfile_wo_comments}" | sort | uniq > "${blacklist_v4_file}"

echo "✓ Generated blacklist files"
echo "  Mixed (IPv4/IPv6): ${outfile_wo_comments} ($(wc -l < "${outfile_wo_comments}" | tr -d ' ') entries)"
echo "  IPv4 only: ${blacklist_v4_file} ($(wc -l < "${blacklist_v4_file}" | tr -d ' ') entries)"
echo "  IPv6 only: ${blacklist_v6_file} ($(wc -l < "${blacklist_v6_file}" | tr -d ' ') entries)"
