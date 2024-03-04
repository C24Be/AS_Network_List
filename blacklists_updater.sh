#!/bin/sh

outfile_wo_comments="blacklists/blacklist.txt"
outfile_w_comments="blacklists/blacklist_with_comments.txt"

auto_black_ass="auto/black_ass.txt"

grep -iE "uvd|fgup|grchc|roskomnad" auto/all-ru-asn.txt | awk '{ print "# AS-Name: " $0 "\n" $1}' > ${auto_black_ass}

./network_list_from_as.py ${auto_black_ass} > ${outfile_w_comments}
./network_list_from_netname.py lists/ru-gov-netnames.txt >> ${outfile_w_comments}
grep -iE "uvd|fgup|grchc|roskomnad" auto/all-ru-ipv4.txt  | awk '{ print "# AS-Name: " $0 "\n" $1}' >> ${outfile_w_comments}
grep -iE "uvd|fgup|grchc|roskomnad|federalnaya sluzhba|ufsb" auto/ripe-ru-ipv4.txt | awk '{ print "# AS-Name: " $0 "\n" $1}' >> ${outfile_w_comments}

# Remove comments by sed to avoid flooding WHOIS servers
grep -v "#" ${outfile_w_comments} | sort | uniq > ${outfile_wo_comments}
