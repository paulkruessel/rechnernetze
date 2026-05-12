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

Noch sinnvoll nachzuholen:

1. Saubere Server-Logs mit `python3 -u`, weil deine bisherigen Serverlogs teilweise leer oder durch einen zweiten Serverstart überschrieben sind.
2. Aufgabe 3.2 mit Handy-Hotspot/WLAN.
3. Aufgabe 4 Portscanner.
4. Aufgabe 5 SMTP/OpenSSL und SMTP/Python.
5. Danach alle Logs erneut packen.

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
Die Clientlogs sind schon gut. Deine Serverlogs sind aber teilweise leer, weil Python-Ausgaben bei Pipes gepuffert werden können. Mit `python3 -u` wird unbuffered ausgegeben, sodass `tee` die Serverausgaben zuverlässig mitschreibt.

---

### 3.1 TCP-Server lokal neu loggen

#### Terminal 1: TCP-Server starten

```bash
python3 -u calc_server_tcp_threaded.py --ip 127.0.0.1 --port 50001 2>&1 | tee log_calc_server_tcp_local_clean.txt
```

Lass diesen Server laufen.

#### Terminal 2: einige TCP-Clients ausführen

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

---

### 3.2 UDP-Server lokal sauber loggen

#### Terminal 1: UDP-Server starten

```bash
python3 -u calc_server_udp.py --ip 127.0.0.1 --port 50002 --seconds 60 2>&1 | tee log_calc_server_udp_local_clean.txt
```

#### Terminal 2: UDP-Client ausführen

```bash
python3 calc_client_probe.py --proto udp --server-ip 127.0.0.1 --server-port 50002 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_udp_sum_clean.txt
```

Der UDP-Server beendet sich nach `--seconds 60` automatisch.

---

## 4. Aufgabe 3.2 – Netzwerk-Kommunikation per Handy-Hotspot

NordVPN/MeshNet wird hier nicht verwendet. Stattdessen werden beide Geräte in denselben Handy-Hotspot gebracht.

### 4.1 IP-Adressen bestimmen

Auf beiden Geräten ausführen:

```bash
ip addr
```

Falls `ip` nicht verfügbar ist:

```bash
ifconfig
```

Notiere:

```text
SERVER_HOTSPOT_IP=<IP des Geräts, auf dem der Server läuft>
CLIENT_HOTSPOT_IP=<IP des Geräts, auf dem der Client läuft>
```

Beispiel:

```text
SERVER_HOTSPOT_IP=192.168.43.120
CLIENT_HOTSPOT_IP=192.168.43.55
```

---

### 4.2 Verbindung per Ping testen

Auf dem Client-Gerät:

```bash
ping -c 4 172.20.10.2
```

Beispiel:

```bash
ping -c 4 192.168.43.120
```

Ausgabe speichern:

```bash
ping -c 4 172.20.10.2 2>&1 | tee log_hotspot_ping.txt
```

---

### 4.3 TCP-Rechenserver im Hotspot starten

Auf dem Server-Gerät:

```bash
python3 -u calc_server_tcp_threaded.py --ip 172.20.10.2 --port 50001 2>&1 | tee log_calc_server_tcp_hotspot_clean.txt
```

Beispiel:

```bash
python3 -u calc_server_tcp_threaded.py --ip 192.168.43.120 --port 50001 2>&1 | tee log_calc_server_tcp_hotspot_clean.txt
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

Auf dem Client-Gerät:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 172.20.10.2 --server-port 50001 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_auto_port.txt
```

Beispiel:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 192.168.43.120 --server-port 50001 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_auto_port.txt
```

Wichtig für die spätere Erklärung:

- Vor `connect()` zeigt `getsockname()` typischerweise `('0.0.0.0', 0)`.
- Nach `connect()` zeigt `getsockname()` die tatsächlich verwendete lokale IP und den automatisch vergebenen lokalen Port.
- Der lokale Port ist ein kurzlebiger Ephemeral Port, den das Betriebssystem auswählt.

---

### 4.5 Client mit explizitem lokalem Binding

Auf dem Client-Gerät:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 172.20.10.2 --server-port 50001 --bind-ip 172.20.10.4 --bind-port 50010 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_bound_port.txt
```

Beispiel:

```bash
python3 calc_client_probe.py --proto tcp --server-ip 192.168.43.120 --server-port 50001 --bind-ip 192.168.43.55 --bind-port 50010 --op SUM --numbers 1 2 3 4 5 2>&1 | tee log_calc_client_tcp_hotspot_bound_port.txt
```

Wichtig für die spätere Erklärung:

- Mit `sock.bind((172.20.10.4, 50010))` setzt der Client seine lokale IP und seinen lokalen Port selbst.
- Nach `connect()` sollte `getsockname()` genau diese IP und diesen Port zeigen.
- Falls `Address already in use` kommt, nimm einen anderen lokalen Port, zum Beispiel `50011` oder `50012`.

---

### 4.6 Server beenden

Im Server-Terminal:

```text
Ctrl+C
```

---

## 5. Aufgabe 3.2 Frage 5 – TCP und UDP auf gleicher Portnummer

Du hast hierfür bereits Logs, aber falls du sie sauber neu erzeugen möchtest:

### Terminal 1: Dual-Echo-Server starten

```bash
python3 -u echo_dual_tcp_udp_server.py --ip 127.0.0.1 --port 50000 --seconds 60 2>&1 | tee log_echo_dual_server_clean.txt
```

### Terminal 2: TCP-Test

```bash
python3 echo_client.py --proto tcp --server-ip 127.0.0.1 --server-port 50000 --message "Hello TCP" 2>&1 | tee log_echo_tcp_same_port_clean.txt
```

### Terminal 2: UDP-Test

```bash
python3 echo_client.py --proto udp --server-ip 127.0.0.1 --server-port 50000 --message "Hello UDP" 2>&1 | tee log_echo_udp_same_port_clean.txt
```

Erwartete Aussage:

```text
Ja, ein Server kann auf derselben numerischen Portnummer gleichzeitig TCP und UDP anbieten, weil TCP-Ports und UDP-Ports getrennte Namensräume besitzen.
```

---

## 6. Aufgabe 4 – Portscanner

Wichtig: Diese Aufgabe funktioniert nur, wenn du im HTWG-VPN bist oder dich im passenden Hochschulnetz befindest.

### 6.1 HTWG-VPN prüfen

Ein einfacher Test:

```bash
ping -c 4 141.37.122.107 2>&1 | tee log_vpn_ping_141_37_122_107.txt
```

Falls keine Antwort kommt, heißt das nicht zwingend, dass der Server nicht erreichbar ist, aber bei vollständigem Timeout ist vermutlich VPN/Netz nicht korrekt.

---

### 6.2 TCP-Portscan 1 bis 50

```bash
python3 port_scanner_tcp_udp.py --proto tcp --host 141.37.122.107 --start 1 --end 50 --timeout 1 --workers 50 2>&1 | tee log_scan_tcp_141_37_122_107.txt
```

Erwartung:

- Offene TCP-Ports erscheinen als `open`.
- Geschlossene oder gefilterte Ports erscheinen als `closed_or_filtered` mit einem `connect_ex`-Code.
- Für Aufgabe 4 brauchst du die Liste der offenen TCP-Ports.

---

### 6.3 UDP-Portscan 1 bis 50

```bash
python3 port_scanner_tcp_udp.py --proto udp --host 141.37.168.26 --start 1 --end 50 --timeout 1 --workers 50 2>&1 | tee log_scan_udp_141_37_168_26.txt
```

Erwartung:

- UDP-Port mit Antwort: `response_open_or_echo`
- UDP-Port ohne Antwort: `no_response_open_or_filtered`
- UDP-Port mit ICMP/Port-Unreachable-Fehler: je nach System `closed_icmp_port_unreachable` oder `os_error_probably_closed`

Hinweis: Unter Linux werden UDP-ICMP-Fehler nicht immer exakt wie unter Windows als 10054 angezeigt. Für den Bericht kann man erklären, dass Windows häufig Fehler 10054 ausgibt, Linux dagegen abhängig vom Socket/Kernel eine andere `OSError`-Darstellung oder nur Timeout zeigt.

---

### 6.4 Echo-Port 7 testen

TCP-Echo:

```bash
python3 echo_client.py --proto tcp --server-ip 141.37.122.107 --server-port 7 --message "Echo-Test TCP" 2>&1 | tee log_echo_remote_tcp_7.txt
```

UDP-Echo:

```bash
python3 echo_client.py --proto udp --server-ip 141.37.168.26 --server-port 7 --message "Echo-Test UDP" 2>&1 | tee log_echo_remote_udp_7.txt
```

Für den Bericht wichtig:

- Bei TCP sieht man im Wireshark-Mitschnitt typischerweise:
  - SYN
  - SYN/ACK
  - ACK
  - Daten
  - Echo-Antwort
  - Verbindungsabbau mit FIN/ACK oder RST
- Bei UDP gibt es keinen Verbindungsaufbau:
  - Client sendet ein UDP-Datagramm.
  - Server antwortet mit einem UDP-Datagramm, falls der Dienst offen ist und antwortet.
  - Bei geschlossenem UDP-Port kann ICMP Destination Unreachable / Port Unreachable auftreten.

---

## 7. Aufgabe 5.1 – SMTP über OpenSSL

Achtung: Passwort nicht in Logs speichern und nicht in den Chat kopieren.

### 7.1 Base64 für Username und Passwort erzeugen

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

### 7.2 OpenSSL-Verbindung öffnen

```bash
openssl s_client -starttls smtp -crlf -connect asmtp.htwg-konstanz.de:587 2>&1 | tee log_smtp_openssl_connection.txt
```

Danach interaktiv eingeben. Wichtig: `rcpt to` kleinschreiben.

```text
ehlo localhost
auth login
BASE64_USERNAME
BASE64_PASSWORT
mail from:<deine.htwg.adresse@htwg-konstanz.de>
rcpt to:<deine.private.zieladresse@example.com>
data
from: deine.htwg.adresse@htwg-konstanz.de
to: deine.private.zieladresse@example.com
subject: RN Labor OpenSSL Test

Dies ist eine Testmail per OpenSSL.
.
quit
```

Falls du nicht möchtest, dass Base64-Zeilen im Log stehen, starte OpenSSL ohne `tee` und schreibe danach nur eine kurze eigene Notiz in eine Logdatei:

```bash
echo "OpenSSL SMTP Test durchgeführt: Verbindung zu asmtp.htwg-konstanz.de:587, STARTTLS, AUTH LOGIN, mail from, rcpt to, data, quit." | tee log_smtp_openssl_summary.txt
```

---

### 7.3 Fake-From-Test nur an dich selbst

Nur kontrolliert an deine eigene Zieladresse senden.

```text
ehlo localhost
auth login
BASE64_USERNAME
BASE64_PASSWORT
mail from:<beliebig@example.com>
rcpt to:<deine.private.zieladresse@example.com>
data
from: Fantasie Name <fake.absender@example.com>
to: deine.private.zieladresse@example.com
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

Das Skript `smtp_socket_client.py` verwendet keine `smtplib`, sondern direkt Socket, STARTTLS und `ssl.wrap_socket`.

### 8.1 Normale Testmail

```bash
python3 smtp_socket_client.py \
  --username DEIN_USERNAME \
  --from-envelope deine.htwg.adresse@htwg-konstanz.de \
  --from-header "Dein Name <deine.htwg.adresse@htwg-konstanz.de>" \
  --to deine.private.zieladresse@example.com \
  --subject "RN Labor Python SMTP Test" \
  --body "Testmail per Python-Socket" \
  2>&1 | tee log_smtp_python.txt
```

Das Passwort wird interaktiv abgefragt.

---

### 8.2 Fake-From-Test nur an dich selbst

```bash
python3 smtp_socket_client.py \
  --username DEIN_USERNAME \
  --from-envelope beliebig@example.com \
  --from-header "Fantasie Name <fake.absender@example.com>" \
  --to deine.private.zieladresse@example.com \
  --subject "RN Labor Fake From Python Test" \
  --body "Kontrollierter Test an mich selbst" \
  2>&1 | tee log_smtp_python_fake_from.txt
```

Falls du sensible Informationen im Log siehst, entferne sie vor dem Hochladen.

---

## 9. Wireshark-Mitschnitte

Für die Abgabe brauchst du nicht zwingend riesige Mitschnitte, aber für die Erklärung solltest du zu den folgenden Fällen je einen Screenshot oder eine kurze Beobachtung notieren:

### 9.1 TCP-Rechenserver lokal

Filter:

```text
tcp.port == 50001
```

Zu erklären:

- `connect()` im Client löst SYN aus.
- `accept()` im Server wird durch den eingehenden Verbindungsaufbau abgeschlossen.
- `sendall()` im Client sendet die Rechenanfrage.
- `recv()` im Server wird durch die Clientdaten abgeschlossen.
- `sendall()` im Server sendet die Antwort.
- `recv()` im Client wird durch die Serverantwort abgeschlossen.

### 9.2 UDP-Rechenserver lokal

Filter:

```text
udp.port == 50002
```

Zu erklären:

- Kein Verbindungsaufbau.
- Ein Datagramm Client → Server.
- Ein Datagramm Server → Client.

### 9.3 TCP/UDP auf gleicher Portnummer

Filter:

```text
tcp.port == 50000 || udp.port == 50000
```

Zu erklären:

- TCP und UDP können dieselbe Portnummer verwenden.
- Es sind trotzdem unterschiedliche Transportprotokolle.

### 9.4 Portscanner

TCP-Filter:

```text
ip.addr == 141.37.122.107 && tcp
```

UDP-Filter:

```text
ip.addr == 141.37.168.26 && (udp || icmp)
```

Zu erklären:

- TCP offen: SYN, SYN/ACK, ACK.
- TCP geschlossen: RST/ACK oder Timeout.
- UDP offen mit Antwort: UDP-Anfrage und UDP-Antwort.
- UDP geschlossen: keine Antwort oder ICMP Port Unreachable.

---

## 10. Logs am Ende sammeln

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

## 11. Was du mir danach schicken solltest

Bitte hochladen oder reinkopieren:

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
log_smtp_openssl_summary.txt oder log_smtp_openssl_connection.txt ohne Secrets
log_smtp_python.txt ohne Secrets
log_smtp_python_fake_from.txt ohne Secrets
```

Wenn einzelne Logs nicht möglich sind, zum Beispiel wegen fehlendem VPN oder Mail-Zugang, kurz dazuschreiben, was passiert ist.
