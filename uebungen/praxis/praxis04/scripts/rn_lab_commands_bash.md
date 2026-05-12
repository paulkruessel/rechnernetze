# Praxis 04 – Bash/Linux/macOS/Git-Bash Commands

Alle Logs werden mit `tee` in Dateien gespeichert. Führe die Commands im Ordner aus, in dem die Python-Skripte liegen.

Falls dein System nicht `python3`, sondern `python` verwendet, ersetze in allen Befehlen `python3` durch `python`.

---

## 0) IP-Adressen für Hotspot/WLAN herausfinden

### Linux
```bash
ip addr
```

Alternative:
```bash
ifconfig
```

### macOS
```bash
ifconfig
```

### Windows CMD/PowerShell, falls doch benötigt
```powershell
ipconfig
```

Notiere:

```text
SERVER_HOTSPOT_IP=...
CLIENT_HOTSPOT_IP=...
```

Beispiel:

```text
SERVER_HOTSPOT_IP=192.168.43.120
CLIENT_HOTSPOT_IP=192.168.43.55
```

---

## 1) Aufgabe 3.1 und 3.3 – Rechenserver lokal TCP mit Threads

### Terminal 1: Server starten

```bash
python3 calc_server_tcp_threaded.py --ip 127.0.0.1 --port 50001 2>&1 | tee log_calc_server_tcp_local.txt
```

Server laufen lassen. Danach in einem zweiten Terminal die Clients starten.

### Terminal 2: TCP-Clients starten

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_sum.txt
```

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op PRO --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_pro.txt
```

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op MIN --numbers -3 8 2 10 2>&1 | tee log_calc_client_tcp_min.txt
```

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op MAX --numbers -3 8 2 10 2>&1 | tee log_calc_client_tcp_max.txt
```

### Mehrere Clients gleichzeitig starten

```bash
for i in 1 2 3 4 5; do
  python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --task-id "$i" --op SUM --numbers "$i" 2 3 > "log_calc_client_parallel_$i.txt" 2>&1 &
done
wait
cat log_calc_client_parallel_*.txt | tee log_calc_clients_parallel_all.txt
```

### Telnet-Test

```bash
telnet 127.0.0.1 50001
```

Falls `telnet` nicht installiert ist:

```bash
nc 127.0.0.1 50001
```

Hinweis: Telnet/Netcat testet hier vor allem, ob der TCP-Port erreichbar ist. Die eigentliche Rechenanfrage ist binär und wird sinnvoll mit dem Python-Client getestet.

---

## 2) Aufgabe 3.1 – Rechenserver lokal UDP

### Terminal 1: UDP-Server starten

```bash
python3 calc_server_udp.py --ip 127.0.0.1 --port 50002 --seconds 120 2>&1 | tee log_calc_server_udp_local.txt
```

### Terminal 2: UDP-Client starten

```bash
python3 calc_client_probe.py --proto udp --server-ip 127.0.0.1 --server-port 50002 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_udp_sum.txt
```

---

## 3) Aufgabe 3.2 – Netzwerk-Kommunikation per Handy-Hotspot statt NordVPN

Beide Geräte müssen im gleichen Handy-Hotspot oder WLAN sein.

### Auf dem Server-Gerät

Ersetze `SERVER_HOTSPOT_IP` durch die echte IP des Server-Geräts.

```bash
python3 calc_server_tcp_threaded.py --ip SERVER_HOTSPOT_IP --port 50001 2>&1 | tee log_calc_server_tcp_hotspot.txt
```

Beispiel:

```bash
python3 calc_server_tcp_threaded.py --ip 192.168.43.120 --port 50001 2>&1 | tee log_calc_server_tcp_hotspot.txt
```

### Auf dem Client-Gerät: Erreichbarkeit testen

```bash
ping SERVER_HOTSPOT_IP
```

Beispiel:

```bash
ping 192.168.43.120
```

Mit begrenzter Anzahl an Pings unter Linux:

```bash
ping -c 4 SERVER_HOTSPOT_IP
```

### Client ohne explizites lokales Binding

```bash
python3 calc_client_probe.py --proto tcp --server-ip SERVER_HOTSPOT_IP --server-port 50001 2>&1 | tee log_calc_client_tcp_hotspot_auto_port.txt
```

Beispiel:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 192.168.43.120 --server-port 50001 2>&1 | tee log_calc_client_tcp_hotspot_auto_port.txt
```

### Client mit expliziter lokaler IP und lokalem Port

Ersetze `CLIENT_HOTSPOT_IP` durch die echte IP des Client-Geräts.

```bash
python3 calc_client_probe.py --proto tcp --server-ip SERVER_HOTSPOT_IP --server-port 50001 --bind-ip CLIENT_HOTSPOT_IP --bind-port 50010 2>&1 | tee log_calc_client_tcp_hotspot_bound_port.txt
```

Beispiel:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 192.168.43.120 --server-port 50001 --bind-ip 192.168.43.55 --bind-port 50010 2>&1 | tee log_calc_client_tcp_hotspot_bound_port.txt
```

---

## 4) Aufgabe 3.2 Frage 5 – TCP und UDP auf gleicher Portnummer

### Terminal 1: Dual-Echo-Server starten

```bash
python3 echo_dual_tcp_udp_server.py --ip 127.0.0.1 --port 50000 --seconds 120 2>&1 | tee log_echo_dual_server.txt
```

### Terminal 2: TCP und UDP testen

```bash
python3 echo_client.py --proto tcp --server-ip 127.0.0.1 --server-port 50000 --message "Hello TCP" 2>&1 | tee log_echo_tcp_same_port.txt
```

```bash
python3 echo_client.py --proto udp --server-ip 127.0.0.1 --server-port 50000 --message "Hello UDP" 2>&1 | tee log_echo_udp_same_port.txt
```

---

## 5) Aufgabe 4 – Portscanner

Nur ausführen, wenn du im HTWG-VPN bist.

### TCP Scan Ports 1 bis 50

```bash
python3 port_scanner_tcp_udp.py --proto tcp --host 141.37.122.107 --start 1 --end 50 --timeout 1 --workers 50 2>&1 | tee log_scan_tcp_141_37_122_107.txt
```

### UDP Scan Ports 1 bis 50

```bash
python3 port_scanner_tcp_udp.py --proto udp --host 141.37.168.26 --start 1 --end 50 --timeout 1 --workers 50 2>&1 | tee log_scan_udp_141_37_168_26.txt
```

### Echo-Port 7 testen

TCP:

```bash
python3 echo_client.py --proto tcp --server-ip 141.37.122.107 --server-port 7 --message "Echo-Test TCP" 2>&1 | tee log_echo_remote_tcp_7.txt
```

UDP:

```bash
python3 echo_client.py --proto udp --server-ip 141.37.168.26 --server-port 7 --message "Echo-Test UDP" 2>&1 | tee log_echo_remote_udp_7.txt
```

---

## 6) Aufgabe 5.1 – SMTP über OpenSSL

### Base64 für Username und Passwort erzeugen

Username:

```bash
python3 -c "import base64; print(base64.b64encode('DEIN_USERNAME'.encode()).decode())"
```

Passwort:

```bash
python3 -c "import base64; print(base64.b64encode('DEIN_PASSWORT'.encode()).decode())"
```

Achtung: Passwort nicht in Logs oder in den Chat kopieren.

### OpenSSL starten

```bash
openssl s_client -starttls smtp -crlf -connect asmtp.htwg-konstanz.de:587 2>&1 | tee log_smtp_openssl_connection.txt
```

Danach interaktiv eingeben. Wichtig: `rcpt to` kleinschreiben.

```text
ehlo localhost
auth login
BASE64_USERNAME
BASE64_PASSWORT
mail from:<pa871kru@htwg-konstanz.de>
rcpt to:<kruesselpaul@gmail.com>
data
from: pa871kru@htwg-konstanz.de
to: kruesselpaul@gmail.com
subject: RN Labor OpenSSL Test

Dies ist eine Testmail per OpenSSL.
.
quit
```

### Fake-From-Test nur an dich selbst

```text
ehlo localhost
auth login
BASE64_USERNAME
BASE64_PASSWORT
mail from:<beliebig@example.com>
rcpt to:<kruesselpaul@gmail.com>
data
from: Fantasie Name <fake.absender@example.com>
to: kruesselpaul@gmail.com
subject: RN Labor Fake From Test

Dies ist ein kontrollierter Test an mich selbst.
.
quit
```

Hinweis: Dies nur kontrolliert an die eigene Adresse verwenden und nicht an andere Personen senden.

---

## 7) Aufgabe 5.2 – SMTP in Python

Normale Testmail:

```bash
python3 smtp_socket_client.py --username DEIN_USERNAME --from-envelope pa871kru@htwg-konstanz.de --from-header "Dein Name <pa871kru@htwg-konstanz.de>" --to kruesselpaul@gmail.com --subject "RN Labor Python SMTP Test" --body "Testmail per Python-Socket" 2>&1 | tee log_smtp_python.txt
```

Fake-From-Test nur an dich selbst:

```bash
python3 smtp_socket_client.py --username DEIN_USERNAME --from-envelope beliebig@example.com --from-header "Fantasie Name <fake.absender@example.com>" --to kruesselpaul@gmail.com --subject "RN Labor Fake From Python Test" --body "Kontrollierter Test an mich selbst" 2>&1 | tee log_smtp_python_fake_from.txt
```

Das Skript fragt dein Passwort interaktiv ab. Bitte das Passwort nicht in Logs kopieren.

---

## 8) Alle erzeugten Logs sammeln

Nach den Versuchen kannst du alle Logs zusammenpacken:

```bash
tar -czf praxis04_logs.tar.gz log_*.txt
```

Oder als ZIP, falls `zip` installiert ist:

```bash
zip praxis04_logs.zip log_*.txt
```

Dann die Datei hier hochladen.
