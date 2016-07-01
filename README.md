# Centrally-Indexed-P2P-Network-for-File-Transfer
Developed a peer-to-peer system with a centralized index to transfer files mimicking Bit-Torrent using socket programming in Python.

Assumptions:
Clients who share the RFCs have the required files store in a sub-folder /RFC/
Each RFC file is of the format RFC<number>_<RFC_Title>.txt
eg: for RFC1 the filename would be RFC1_title1.txt under the directory /RFC/

All commands are case sensitive.
The server is always running.

Instructions:
We are taking no command line arguments.
1.Change the IP address on the server to reflect that of the machine.
2.Change the IP address of each client to reflect its corresponding IP address
on the machine you are currently running it.
3.Issue GET,LOOKUP,LIST,ADD as appropriate.Note that for each command you need to
enter the RFC number and title correctly(Case sensitive).
4.When the client wishes to close the connection he enters the EXIT command.

