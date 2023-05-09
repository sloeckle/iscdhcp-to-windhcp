# iscdhcp-to-windhcp

This script was written for a specific purpose, to migrate from ISC DHCP to Windows DHCP. A client of mine had ~700 vlans and class C scopes. Doing this by hand was not an option.

This script is offered as-is with no warranty or support whatsoever.

Things specific to the environment in which I wrote this script:

1) Scope names were included with a # right before the subnet line in dhcpd.conf. If this comment did not exist, then the subnet is used for the scope name.
2) Added an option to the script to reference a ms dhcp export XML file to find duplicates before generating powershell commands. In this particular environment, there were two DHCP servers. One old ms dhcp server and one old ISC dhcp server. We compared the old ms dhcp server xml export file to the dhcpd.conf file to find the subnets that needed to be added to the new ms dhcp server. If the variable is set then the script will attempt to read the xml file. If there is no xml file, leave the variable commented out.
3) Supports reservations buy reading the host lines from dhcpd.conf, compares their IP addresses to the scopes read from dhcpd.conf (and optionally filtered out by the xml comparison). If their first 3 octets match (again, class-c only) then output the powershell commands to register the reservation.
4) Also supports ms dhcp replication. This relationship should already be setup prior to running the powershell command output from this script. Setup the two variables at the top of the script to output the necessary powershell commands.
5) If a range doesn't exist for a isc dhcp scope, the script will set the range as .1 to .254.

Things this script was not designed to do:

1) Work with any subnets/scopes sizes other than a class C.
2) Work with any subnet/scope that has multiple ranges.
3) Import global options. This is easy enough to do by hand.
4) Import non-standard dhcp options such as nds clients, slp, or voip services. With basic python knowledge, you can add these.
5) Work with ipv6

Other notes:

There are many rstrip and lstrip lines in this script because of observed weirdness in the version of python3 on my mac. Just a workaround.

Lastly, I have no doubts that the script contains bugs, is basic, and could be written differently. It was written for one purpose and one environment. I thought someone could use it and/or make it better.