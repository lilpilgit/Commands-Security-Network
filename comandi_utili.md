#####################################################################################

## H3C ##

*Ottengo il device name, serial number, macaddress...*
`display system manuinfo`

*Ottengo lo showtech del dispositivo*
`display diagnostic-information`

#####################################################################################

## HP ##

*creo la vlan*
`vlan <num>`

*metto l'interfaccia in trunk per quella vlan*
`tagged <num>`

*mostro le info per i dispositivi vicini*
`show lldp info remote-device`



#####################################################################################

## FORTINET ##

*informazioni per la singola interfaccia di rete*
`get hardware nic <port>`

*lanciare un qualsiasi comando come ping, traceroute,...*
`exec ping`

*consente di accedere alla management del secondo firewall di alta affidabilità, non passa tramite lo switching ma è diretto tramite il link di synch*
`exec ha manage`

*mostra tutti i parametri configurabili*
`show full-configuration`

*verificare se uno specifico ip può essere routato o meno*
`get router info routing-table details <ip>`

[PROCESSI]
*processi in running nel firewall*
`diagnose sys top`

*uccide un processo*
`diagnose test application <nome_processo> 99`

[--------]

*sarebbe lo show version cisco*
`get system status`

*stato dell'HA*
`get sys ha status`

*usato per verificare se le macchine in HA sono sincronizzate*
`diag sys ha checksum`

*mostra nel dettaglio l'hash per ogni valore, così da poterlo comparare*
`diag sys ha checksum show <vdom>`

*posso specificare per un tcpdump*
`diag sni pack <any/interface> "host <ip> and host <ip> and <port>" <level_verbose> <numero_di_pacchetti_da_catturare/0 == illimitato> <l(elle), serve per il timestamp>`

[DEBUG]

*reset del debug del flusso della sessione*
`diag debug reset`

*filtro da applicare per il debug*
`diag debug flow filter addr <ip>`

*fa leggere il debug sulla cli*
`diag debug flow show function-name enable`

*start del debug*
`diag debug enable`

*ferma il debug*
`diag debug disable`
[-----]

*debug del processo vpn all'interno dell'apparato, utile su vecchie versioni di firewall tipo la 5*
`diag debug application vpd`

*l'SSO prevede di avere un agente montata sul domain controller che permette di comunicare con il registro degli eventi di windows (ci sono 2 id che identificano il login e il logout fatto dall'utente), un collector (primary FSSO agent) che raccoglie i login/logout. Sul collector posso scartare gli utenti di sevizi che non devono per esempio poter accedere in internet con una security policy per esempio.Il collector è tra DC e firewall, tanti lo mettono su macchine di backup, e l'unica funzione che ha è quella di far comunicare firewall e DC. Se volessi vedere la situazione dei collettori usiamo questo comando*
`diag debug authd fsso server-status`




