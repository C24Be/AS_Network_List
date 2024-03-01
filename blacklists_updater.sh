#!/bin/sh

outfile_wo_comments="blacklist.txt"
outfile_w_comments="blacklist_comments.txt"

url_ass="https://raw.githubusercontent.com/C24Be/AS_Network_List/main/lists/ru-gov-ass.txt"
url_nets="https://raw.githubusercontent.com/C24Be/AS_Network_List/main/lists/ru-gov-netnames.txt"

./network_list_from_as.py ${url_ass} -q > ${outfile_wo_comments}
./network_list_from_netname.py ${url_nets} -q >> ${outfile_wo_comments}

./network_list_from_as.py ${url_ass} > ${outfile_w_comments}
./network_list_from_netname.py ${url_nets} >> ${outfile_w_comments}
