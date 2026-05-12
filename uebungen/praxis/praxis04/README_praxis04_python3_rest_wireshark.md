# Praxis04 – README für die restlichen Versuche mit Python 3

Dieses README ist für Bash/Linux/Fedora/macOS/Git Bash gedacht.  
Alle Befehle verwenden `python3` und speichern Ausgaben mit `tee` in Logdateien.

Wichtig: Serverprogramme laufen weiter, bis sie ablaufen oder mit `Ctrl+C` beendet werden.  
Ein Server darf auf derselben IP/Port-Kombination nur einmal laufen. Wenn ein Server schon läuft, **nicht noch einmal denselben Serverbefehl starten**, sondern in einem zweiten Terminal den Client ausführen.

---

## 1. Überblick: Was laut bisherigen Logs schon erledigt ist

Aus deinen bisherigen Logs sind bereits vorhanden:

- TCP-Rechenserver-Clienttests lokal:
  - `SUM([1,2,3,4,5]) = 15`
  - `PRO([1,2,3,4,5]) = 120`
  - `MIN([-3,8,2,10]) = -3`
  - `MAX([-3,8,2,10]) = 10`
- UDP-Rechenserver-Clienttest lokal:
  - `SUM([1,2,3,4,5]) = 15`
- Mehrere parallele TCP-Clients:
  - Task-IDs 1 bis 5 wurden korrekt beantwortet.
- TCP und UDP auf gleicher Portnummer:
  - TCP-Echo auf `127.0.0.1:50000` funktioniert.
  - UDP-Echo auf `127.0.0.1:50000` funktioniert.
- Aufgabe 3.2 Hotspot-Client:
  - Client ohne explizites `bind()`: erledigt.
  - Client mit explizitem `bind()`: erledigt.
  - Ping vom Windows-Client zum Hotspot-Server: erledigt.

Noch sinnvoll nachzuholen:

1. Saubere Server-Logs mit `python3 -u`, falls Serverlogs fehlen oder leer sind.
2. Aufgabe 4 Portscanner.
3. Aufgabe 5 SMTP/OpenSSL und SMTP/Python.
4. Danach alle Logs erneut packen.

---

## 2. Vorbereitungen

Wechsle in deinen Skriptordner:

```bash
cd ~/studium/rechnernetze/uebungen/praxis/praxis04/scripts
```

Prüfe, ob alle Skripte vorhanden sind:

```bash
ls -1
```

Erwartet werden mindestens:

```text
calc_client_probe.py
calc_server_tcp_threaded.py
calc_server_udp.py
echo_client.py
echo_dual_tcp_udp_server.py
port_scanner_tcp_udp.py
smtp_socket_client.py
```

Optional: alten Log-Ordner anlegen und bisherige Logs verschieben:

```bash
mkdir -p old_logs
mv log_*.txt old_logs/ 2>/dev/null || true
```

---

## 3. Saubere lokale Server-Logs nachholen

Warum?  
Die Clientlogs sind schon gut. Serverlogs können aber teilweise leer sein, wenn Python-Ausgaben bei Pipes gepuffert werden. Mit `python3 -u` wird unbuffered ausgegeben, sodass `tee` die Serverausgaben zuverlässig mitschreibt.

---

### 3.1 TCP-Rechenserver lokal neu loggen

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- Unter Linux/Fedora: Loopback-Interface, meistens `lo`
- Unter Windows: Adapter für Loopback-Traffic, falls lokal unter Windows getestet wird

Display-Filter in Wireshark:

```text
tcp.port == 50001
```

Mitschneiden starten, bevor der Client ausgeführt wird. Danach Server und Client wie unten starten.  
Für die spätere Erklärung relevante Pakete:

- TCP-Verbindungsaufbau: `SYN`, `SYN/ACK`, `ACK`
- Nutzdaten Client → Server
- Nutzdaten Server → Client
- Verbindungsabbau

#### Terminal 1: TCP-Server starten

```bash
python3 -u calc_server_tcp_threaded.py --ip 127.0.0.1 --port 50001 2>&1 | tee log_calc_server_tcp_local_clean.txt
```

Lass diesen Server laufen.

#### Terminal 2: TCP-Clients ausführen

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_sum_clean.txt
```

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op PRO --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_pro_clean.txt
```

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op MIN --numbers -3 8 2 10 2>&1 | tee log_calc_client_tcp_min_clean.txt
```

```bash
python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --op MAX --numbers -3 8 2 10 2>&1 | tee log_calc_client_tcp_max_clean.txt
```

#### Terminal 2: parallele Clients für Aufgabe 3.3

Auch dieser Teil kann im gleichen Wireshark-Mitschnitt mitlaufen. Man sieht dann mehrere TCP-Verbindungen auf denselben Serverport.

```bash
for i in 1 2 3 4 5; do
  python3 calc_client_probe.py --proto tcp --server-ip 127.0.0.1 --server-port 50001 --task-id "$i" --op SUM --numbers "$i" 2 3 > "log_calc_client_parallel_clean_$i.txt" 2>&1 &
done
wait
cat log_calc_client_parallel_clean_*.txt | tee log_calc_clients_parallel_clean_all.txt
```

#### Terminal 1: Server beenden

Nach den Clients im Server-Terminal:

```text
Ctrl+C
```

Falls der Server danach nicht beendet ist:

```bash
ss -ltnp | grep ':50001'
```

Dann die PID beenden:

```bash
kill <PID>
```

Nur falls nötig:

```bash
kill -9 <PID>
```

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_calc_tcp_local.pcapng
```

---

### 3.2 UDP-Rechenserver lokal sauber loggen

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- Unter Linux/Fedora: Loopback-Interface `lo`

Display-Filter:

```text
udp.port == 50002
```

Für die spätere Erklärung relevante Pakete:

- ein UDP-Datagramm Client → Server mit der Rechenanfrage
- ein UDP-Datagramm Server → Client mit der Antwort
- kein TCP-Handshake, weil UDP verbindungslos ist

#### Terminal 1: UDP-Server starten

```bash
python3 -u calc_server_udp.py --ip 127.0.0.1 --port 50002 --seconds 60 2>&1 | tee log_calc_server_udp_local_clean.txt
```

#### Terminal 2: UDP-Client ausführen

```bash
python3 calc_client_probe.py --proto udp --server-ip 127.0.0.1 --server-port 50002 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_udp_sum_clean.txt
```

Der UDP-Server beendet sich nach `--seconds 60` automatisch.

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_calc_udp_local.pcapng
```

---

## 4. Aufgabe 3.2 – Netzwerk-Kommunikation per Handy-Hotspot

NordVPN/MeshNet wird hier nicht verwendet. Stattdessen werden beide Geräte in denselben Handy-Hotspot gebracht.

Deine bisherigen Werte:

```text
Server-IP im Hotspot: 172.20.10.2
Client-IP im Hotspot: 172.20.10.4
```

---

### 4.1 IP-Adressen bestimmen

#### Wireshark-Mitschnitt

Nein, hierfür ist kein Wireshark-Mitschnitt nötig.

Auf beiden Geräten ausführen:

```bash
ip addr
```

Falls `ip` nicht verfügbar ist:

```bash
ifconfig
```

Unter Windows:

```bash
ipconfig
```

Notiere:

```text
SERVER_HOTSPOT_IP=<IP des Geräts, auf dem der Server läuft>
CLIENT_HOTSPOT_IP=<IP des Geräts, auf dem der Client läuft>
```

---

### 4.2 Verbindung per Ping testen

#### Wireshark-Mitschnitt

Optional, aber nicht zwingend. Für den Bericht reicht dein Ping-Log.

Wenn du es mitschneiden möchtest:

Interface:

- WLAN-/Hotspot-Interface, nicht Loopback

Display-Filter:

```text
icmp || icmpv6
```

Auf dem Client-Gerät:

```bash
ping -c 4 172.20.10.2
```

Unter Windows oder Git Bash kann auch der Windows-Ping verwendet werden:

```bash
ping 172.20.10.2
```

Ausgabe speichern, falls möglich:

```bash
ping -c 4 172.20.10.2 2>&1 | tee log_hotspot_ping.txt
```

Dein bereits vorhandener Ping-Nachweis:

```text
4 Pakete gesendet, 4 empfangen, 0 % Verlust.
Minimum 3 ms, Maximum 83 ms, Mittelwert 23 ms.
```

---

### 4.3 TCP-Rechenserver im Hotspot starten

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden, falls du ihn noch einmal ausführst.

Wo mitschneiden?

- Auf dem Server-Gerät: WLAN-/Hotspot-Interface
- Alternativ auf dem Client-Gerät: WLAN-/Hotspot-Interface

Display-Filter:

```text
ip.addr == 172.20.10.2 && ip.addr == 172.20.10.4 && tcp.port == 50001
```

Falls andere IPs verwendet werden, entsprechend ersetzen.

Für die spätere Erklärung relevante Pakete:

- TCP-Handshake zwischen Client und Server
- Client sendet 28 Byte Rechenanfrage
- Server sendet 8 Byte Antwort
- Ergebnis: `(5000, 15)`

Auf dem Server-Gerät:

```bash
python3 -u calc_server_tcp_threaded.py --ip 172.20.10.2 --port 50001 2>&1 | tee log_calc_server_tcp_hotspot_clean.txt
```

Beispiel mit deiner bisherigen Server-IP:

```bash
python3 -u calc_server_tcp_threaded.py --ip 172.20.10.2 --port 50001 2>&1 | tee log_calc_server_tcp_hotspot_clean.txt
```

Falls `Address already in use` kommt:

```bash
ss -ltnp | grep ':50001'
```

Dann den alten Prozess beenden:

```bash
kill <PID>
```

Oder für den Hotspot-Test einen anderen Port verwenden, zum Beispiel `50011`. Dann aber denselben Port auch im Client verwenden.

---

### 4.4 Client ohne explizites lokales Binding

#### Wireshark-Mitschnitt

Ja, wenn du den Hotspot-Versuch noch einmal sauber mitschneiden möchtest.  
Dieser Schritt gehört zum gleichen Mitschnitt wie Abschnitt 4.3.

Display-Filter:

```text
ip.addr == 172.20.10.2 && ip.addr == 172.20.10.4 && tcp.port == 50001
```

Auf dem Client-Gerät:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 172.20.10.2 --server-port 50001 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_auto_port.txt
```

Beispiel mit deiner bisherigen Server-IP:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 172.20.10.2 --server-port 50001 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_auto_port.txt
```

Dein vorhandener Log zeigt:

```text
Lokale Client-Adresse nach connect(): 172.20.10.4:62358
Server-Adresse: 172.20.10.2:50001
Antwort: (5000, 15)
```

Wichtig für die spätere Erklärung:

- Vor `connect()` ist die lokale Adresse unter Windows noch nicht sinnvoll abrufbar.
- Nach `connect()` zeigt `getsockname()` die tatsächlich verwendete lokale IP und den automatisch vergebenen lokalen Port.
- Der lokale Port ist ein kurzlebiger Ephemeral Port, den das Betriebssystem auswählt.

---

### 4.5 Client mit explizitem lokalem Binding

#### Wireshark-Mitschnitt

Ja, wenn du den Hotspot-Versuch noch einmal sauber mitschneiden möchtest.  
Dieser Schritt kann ebenfalls im gleichen Mitschnitt wie Abschnitt 4.3 und 4.4 enthalten sein.

Display-Filter:

```text
ip.addr == 172.20.10.2 && ip.addr == 172.20.10.4 && tcp.port == 50001
```

Auf dem Client-Gerät:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 172.20.10.2 --server-port 50001 --bind-ip 172.20.10.4 --bind-port 50010 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_bound_port.txt
```

Beispiel mit deinen bisherigen IPs:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 172.20.10.2 --server-port 50001 --bind-ip 172.20.10.4 --bind-port 50010 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_bound_port.txt
```

Dein vorhandener Log zeigt:

```text
Lokale Client-Adresse nach bind(): 172.20.10.4:50010
Lokale Client-Adresse nach connect(): 172.20.10.4:50010
Server-Adresse: 172.20.10.2:50001
Antwort: (5000, 15)
```

Wichtig für die spätere Erklärung:

- Mit `sock.bind((172.20.10.4, 50010))` setzt der Client seine lokale IP und seinen lokalen Port selbst.
- Nach `connect()` bleibt genau diese lokale Adresse erhalten.
- Falls `Address already in use` kommt, nimm einen anderen lokalen Port, zum Beispiel `50011` oder `50012`.

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_calc_tcp_hotspot.pcapng
```

---

### 4.6 Server beenden

#### Wireshark-Mitschnitt

Nein.

Im Server-Terminal:

```text
Ctrl+C
```

---

## 5. Aufgabe 3.2 Frage 5 – TCP und UDP auf gleicher Portnummer

Du hast hierfür bereits Logs, aber falls du sie sauber neu erzeugen möchtest:

### 5.1 Dual-Echo-Server starten

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- Lokal: Loopback-Interface `lo`

Display-Filter:

```text
tcp.port == 50000 || udp.port == 50000
```

Für die spätere Erklärung relevante Pakete:

- TCP: Verbindungsaufbau, Echo-Daten, Antwort
- UDP: ein Datagramm hin, ein Datagramm zurück
- TCP und UDP verwenden dieselbe numerische Portnummer, sind aber unterschiedliche Transportprotokolle

#### Terminal 1: Dual-Echo-Server starten

```bash
python3 -u echo_dual_tcp_udp_server.py --ip 127.0.0.1 --port 50000 --seconds 60 2>&1 | tee log_echo_dual_server_clean.txt
```

### 5.2 TCP-Test

```bash
python3 echo_client.py --proto tcp --server-ip 127.0.0.1 --server-port 50000 --message "Hello TCP" 2>&1 | tee log_echo_tcp_same_port_clean.txt
```

### 5.3 UDP-Test

```bash
python3 echo_client.py --proto udp --server-ip 127.0.0.1 --server-port 50000 --message "Hello UDP" 2>&1 | tee log_echo_udp_same_port_clean.txt
```

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_echo_tcp_udp_same_port.pcapng
```

Erwartete Aussage:

```text
Ja, ein Server kann auf derselben numerischen Portnummer gleichzeitig TCP und UDP anbieten, weil TCP-Ports und UDP-Ports getrennte Namensräume besitzen.
```

---

## 6. Aufgabe 4 – Portscanner

Wichtig: Diese Aufgabe funktioniert nur, wenn du im HTWG-VPN bist oder dich im passenden Hochschulnetz befindest.

Dein VPN-Log zeigt bereits:

```text
Initialization Sequence Completed
VPN-IP: 141.37.207.4
```

Der Ping auf `141.37.122.107` hatte 100 % Verlust. Das ist nicht automatisch ein Problem, weil ICMP blockiert sein kann. Entscheidend sind die TCP-/UDP-Tests.

---

### 6.1 HTWG-VPN prüfen

#### Wireshark-Mitschnitt

Nein, für den VPN-Start selbst ist kein Wireshark-Mitschnitt nötig.

VPN starten, falls noch nicht aktiv:

```bash
sudo openvpn --config ~/Downloads/HTWG-MFA-SOSE26-STUD.ovpn
```

VPN ist aktiv, wenn im OpenVPN-Log steht:

```text
Initialization Sequence Completed
```

Optionaler Ping-Test:

```bash
ping -c 4 141.37.122.107 2>&1 | tee log_vpn_ping_141_37_122_107.txt
```

Wenn der Ping fehlschlägt, trotzdem mit TCP-/UDP-Portscan fortfahren.

---

### 6.2 TCP-Portscan 1 bis 50

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- VPN-Interface, unter Linux meist `tun0`

Display-Filter:

```text
ip.addr == 141.37.122.107 && tcp
```

Alternativ enger:

```text
ip.addr == 141.37.122.107 && tcp.port >= 1 && tcp.port <= 50
```

Für die spätere Erklärung relevante Fälle:

- TCP-Port offen: `SYN`, `SYN/ACK`, `ACK`
- TCP-Port geschlossen: häufig `RST/ACK`
- TCP-Port gefiltert/nicht erreichbar: Timeout bzw. keine Antwort

Portscan ausführen:

```bash
python3 port_scanner_tcp_udp.py --proto tcp --host 141.37.122.107 --start 1 --end 50 --timeout 1 --workers 50 2>&1 | tee log_scan_tcp_141_37_122_107.txt
```

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_scan_tcp_141_37_122_107.pcapng
```

---

### 6.3 UDP-Portscan 1 bis 50

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- VPN-Interface, unter Linux meist `tun0`

Display-Filter:

```text
ip.addr == 141.37.168.26 && (udp || icmp)
```

Für die spätere Erklärung relevante Fälle:

- UDP-Port mit Antwort: UDP-Anfrage und UDP-Antwort
- UDP-Port ohne Antwort: Timeout, Status unklar/offen/gefiltert
- UDP-Port geschlossen: ICMP Destination Unreachable / Port Unreachable möglich

Portscan ausführen:

```bash
python3 port_scanner_tcp_udp.py --proto udp --host 141.37.168.26 --start 1 --end 50 --timeout 1 --workers 50 2>&1 | tee log_scan_udp_141_37_168_26.txt
```

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_scan_udp_141_37_168_26.pcapng
```

Hinweis für Linux/Fedora:

Unter Windows wird ein geschlossener UDP-Port oft als Fehler 10054 angezeigt. Unter Linux kann derselbe Fall je nach System als anderer `OSError`, als ICMP-Paket im Mitschnitt oder nur als Timeout sichtbar sein.

---

### 6.4 Echo-Port 7 TCP testen

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- VPN-Interface `tun0`

Display-Filter:

```text
ip.addr == 141.37.122.107 && tcp.port == 7
```

Für die spätere Erklärung:

- TCP-Handshake
- gesendete Echo-Nachricht
- gleiche oder entsprechende Antwort vom Echo-Dienst
- Verbindungsabbau

TCP-Echo:

```bash
python3 echo_client.py --proto tcp --server-ip 141.37.122.107 --server-port 7 --message "Echo-Test TCP" 2>&1 | tee log_echo_remote_tcp_7.txt
```

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_echo_tcp_7.pcapng
```

---

### 6.5 Echo-Port 7 UDP testen

#### Wireshark-Mitschnitt

Ja, diesen Versuch mitschneiden.

Interface:

- VPN-Interface `tun0`

Display-Filter:

```text
ip.addr == 141.37.168.26 && udp.port == 7
```

Für die spätere Erklärung:

- UDP-Anfrage an Port 7
- UDP-Antwort vom Echo-Dienst
- kein Verbindungsaufbau

UDP-Echo:

```bash
python3 echo_client.py --proto udp --server-ip 141.37.168.26 --server-port 7 --message "Echo-Test UDP" 2>&1 | tee log_echo_remote_udp_7.txt
```

#### Wireshark-Mitschnitt speichern

Speichere den Mitschnitt zum Beispiel als:

```text
wireshark_echo_udp_7.pcapng
```

---

## 7. Aufgabe 5.1 – SMTP über OpenSSL

Achtung: Passwort nicht in Logs speichern und nicht in den Chat kopieren.

---

### 7.1 Base64 für Username und Passwort erzeugen

#### Wireshark-Mitschnitt

Nein, hierfür ist kein Wireshark-Mitschnitt nötig.

Username:

```bash
python3 -c "import base64; print(base64.b64encode('DEIN_USERNAME'.encode()).decode())"
```

Passwort:

```bash
python3 -c "import base64; print(base64.b64encode('DEIN_PASSWORT'.encode()).decode())"
```

Die Base64-Werte nur lokal verwenden.

---

### 7.2 OpenSSL-Verbindung öffnen und Mail senden

#### Wireshark-Mitschnitt

Optional. Da STARTTLS verwendet wird, sind nach dem TLS-Start die Inhalte verschlüsselt.  
Für die Erklärung kann ein Mitschnitt trotzdem sinnvoll sein, um TCP-Verbindung, SMTP-Begrüßung und STARTTLS zu sehen.

Interface:

- aktive Netzwerkverbindung oder VPN-Interface, je nach Verbindung

Display-Filter:

```text
tcp.port == 587 || smtp
```

Falls `smtp` nach STARTTLS nichts mehr dekodiert, ist das normal, weil der Datenstrom dann TLS-verschlüsselt ist.

OpenSSL starten:

```bash
openssl s_client -starttls smtp -crlf -connect asmtp.htwg-konstanz.de:587
```

Danach interaktiv eingeben. Wichtig: `rcpt to` kleinschreiben.

```text
ehlo localhost
auth login
cGE4NzFrcnU=
bWRQc2lzK3MxNDA5MDM=
mail from:pa871kru@htwg-konstanz.de
rcpt to:kruesselpaul@gmail.com
data
from: deine.htwg.adresse@htwg-konstanz.de
to: kruesselpaul@gmail.com
subject: RN Labor OpenSSL Test

Dies ist eine Testmail per OpenSSL.
.
quit
```

Falls du eine kurze Logdatei ohne Secrets erzeugen möchtest:

```bash
echo "OpenSSL SMTP Test durchgeführt: Verbindung zu asmtp.htwg-konstanz.de:587, STARTTLS, AUTH LOGIN, mail from, rcpt to, data, quit." | tee log_smtp_openssl_summary.txt
```

#### Wireshark-Mitschnitt speichern

Falls mitgeschnitten wurde:

```text
wireshark_smtp_openssl_587.pcapng
```

---

### 7.3 Fake-From-Test nur an dich selbst

#### Wireshark-Mitschnitt

Optional. Der Inhalt ist wegen TLS verschlüsselt. Für die fachliche Beobachtung ist wichtiger, was im Mailprogramm ankommt.

Nur kontrolliert an deine eigene Zieladresse senden.

```text
ehlo localhost
auth login
cGE4NzFrcnU=
bWRQc2lzK3MxNDA5MDM=
mail from:yourmum@gmail.com
rcpt to:kruesselpaul@gmail.com
data
from: Fantasie Name yourmum2@gmail.com
to: kruesselpaul@gmail.com
subject: RN Labor Fake From Test

Dies ist ein kontrollierter Test an mich selbst.
.
quit
```

Für den Bericht beobachten:

- Der Envelope-Absender aus `mail from` und der sichtbare Header `from:` können unterschiedlich sein.
- Im Mailprogramm wird oft primär der Header-From angezeigt.
- Moderne Mailserver/Clients können solche Mails durch SPF/DKIM/DMARC oder Warnhinweise als verdächtig markieren.

---

## 8. Aufgabe 5.2 – SMTP in Python

Das Skript `smtp_socket_client.py` verwendet keine `smtplib`, sondern direkt Socket, STARTTLS und SSL/TLS.

---

### 8.1 Normale Testmail

#### Wireshark-Mitschnitt

Optional. Da STARTTLS verwendet wird, ist nach dem TLS-Start der SMTP-Inhalt verschlüsselt.

Display-Filter:

```text
tcp.port == 587 || smtp
```

Normale Testmail:

```bash
python3 smtp_socket_client.py \
  --username DEIN_USERNAME \
  --from-envelope deine.htwg.adresse@htwg-konstanz.de \
  --from-header "Dein Name pa871kru@htwg-konstanz.de" \
  --to kruesselpaul@gmail.com \
  --subject "RN Labor Python SMTP Test" \
  --body "Testmail per Python-Socket" \
  2>&1 | tee log_smtp_python.txt
```

Das Passwort wird interaktiv abgefragt.

#### Wireshark-Mitschnitt speichern

Falls mitgeschnitten wurde:

```text
wireshark_smtp_python_587.pcapng
```

---

### 8.2 Fake-From-Test nur an dich selbst

#### Wireshark-Mitschnitt

Optional. Der Inhalt ist wegen TLS verschlüsselt. Für die Beobachtung ist wichtiger, was im Mailpostfach sichtbar ist.

```bash
python3 smtp_socket_client.py \
  --username DEIN_USERNAME \
  --from-envelope beliebig@example.com \
  --from-header "Fantasie Name yourmum2@gmail.com" \
  --to kruesselpaul@gmail.com \
  --subject "RN Labor Fake From Python Test" \
  --body "Kontrollierter Test an mich selbst" \
  2>&1 | tee log_smtp_python_fake_from.txt
```

Falls du sensible Informationen im Log siehst, entferne sie vor dem Hochladen.

---

## 9. Logs am Ende sammeln

#### Wireshark-Mitschnitt

Nein, hier werden nur Logdateien gesammelt.

Alle Logs in ein Archiv packen:

```bash
tar -czf praxis04_logs_final.tar.gz log_*.txt
```

Oder als ZIP:

```bash
zip praxis04_logs_final.zip log_*.txt
```

Danach `praxis04_logs_final.tar.gz` oder `praxis04_logs_final.zip` hochladen.

---

## 10. Was du mir danach schicken solltest

Bitte hochladen oder reinkopieren, soweit vorhanden:

```text
log_calc_server_tcp_local_clean.txt
log_calc_client_tcp_sum_clean.txt
log_calc_client_tcp_pro_clean.txt
log_calc_client_tcp_min_clean.txt
log_calc_client_tcp_max_clean.txt
log_calc_clients_parallel_clean_all.txt
log_calc_server_udp_local_clean.txt
log_calc_client_udp_sum_clean.txt
log_hotspot_ping.txt
log_calc_server_tcp_hotspot_clean.txt
log_calc_client_tcp_hotspot_auto_port.txt
log_calc_client_tcp_hotspot_bound_port.txt
log_scan_tcp_141_37_122_107.txt
log_scan_udp_141_37_168_26.txt
log_echo_remote_tcp_7.txt
log_echo_remote_udp_7.txt
log_smtp_openssl_summary.txt oder eine kurze eigene Notiz ohne Secrets
log_smtp_python.txt ohne Secrets
log_smtp_python_fake_from.txt ohne Secrets
```

Wireshark-Dateien musst du mir nicht unbedingt hochladen, wenn die Logs vollständig sind. Für die LaTeX-Ausarbeitung reichen meistens kurze Notizen oder Screenshots zu den beobachteten Paketfolgen.
