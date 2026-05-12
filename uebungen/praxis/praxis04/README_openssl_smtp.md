# README – SMTP-Test mit OpenSSL

Dieses README beschreibt nur den OpenSSL-Teil aus Aufgabe 5.  
Passwort und Base64-Zugangsdaten dürfen nicht in die Abgabe oder in öffentliche Logs übernommen werden.

---

## 1 Username und Passwort decodieren

Mein Username:
```
cGE4NzFrcnU=
```
Mein Passwort:
```
bWRQc2lzK3MxNDA5MDM=
```

---

## 2. OpenSSL-Verbindung zum SMTP-Server öffnen

```bash
openssl s_client -starttls smtp -crlf -connect asmtp.htwg-konstanz.de:587
```

Nach dem Verbindungsaufbau erscheinen Zertifikats- und TLS-Informationen. Danach können SMTP-Kommandos eingegeben werden.

---

## 3. Normale Testmail senden

```text
ehlo localhost
auth login
cGE4NzFrcnU=
bWRQc2lzK3MxNDA5MDM=
mail from:pa871kru@htwg-konstanz.de
rcpt to:kruesselpaul@gmail.com
data
from: pa871kru@htwg-konstanz.de
to: kruesselpaul@gmail.com
subject: RN Labor OpenSSL Test nicht Fake

Dies ist eine Testmail per OpenSSL.
.
quit
```

---

## 4. Test mit abweichendem sichtbaren Absender

Diesen Versuch nur kontrolliert an die eigene Adresse senden.

```text
ehlo localhost
auth login
cGE4NzFrcnU=
bWRQc2lzK3MxNDA5MDM=
mail from:fake@apple.com
rcpt to:kruesselpaul@gmail.com
data
from: Apple Support support@apple.com
to: kruesselpaul@gmail.com
subject: Supportalarm

Dies ist kein kontrollierter Test an mich selbst. Dies ist ein Supportfall
.
quit
```
