#!/bin/sh

outfile_wo_comments="blacklist.txt"
outfile_w_comments="blacklist_with_comments.txt"

url_ass="https://raw.githubusercontent.com/C24Be/AS_Network_List/main/lists/ru-gov-ass.txt"
url_nets="https://raw.githubusercontent.com/C24Be/AS_Network_List/main/lists/ru-gov-netnames.txt"

./network_list_from_as.py ${url_ass} > ${outfile_w_comments}
./network_list_from_netname.py ${url_nets} >> ${outfile_w_comments}

# Remove comments by sed to avoid flooding WHOIS servers
grep -v "#" ${outfile_w_comments} > ${outfile_wo_comments}
