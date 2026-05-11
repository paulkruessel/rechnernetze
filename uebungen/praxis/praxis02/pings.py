"""
Versuchsreihe: Ping-Messung mit icmplib
- Pingt mehrere Hosts jeweils 100-mal
- Speichert die Antwortzeiten
- Stellt die Ergebnisse grafisch dar
"""

from icmplib import ping
import matplotlib.pyplot as plt

HOSTS = {
    "Labor": "172.20.189.191",
    "HTWG": "www.htwg-konstanz.de",
    "Deutschland": "www.spiegel.de",
    "Nordamerika": "www.google.com",
    "Australien": "www.abc.net.au"
}

PING_COUNT = 100

def measure_ping(host, count):
    """
    Führt mehrere Pings aus und gibt die Antwortzeiten zurück.
    """
    print(f"Pinge {host} ...")

    result = ping(host, count=count, interval=0.2)

    rtts = result.rtts

    return rtts

def main():
    all_results = {}

    for name, host in HOSTS.items():
        try:
            rtts = measure_ping(host, PING_COUNT)
            all_results[name] = rtts
        except Exception as e:
            print(f"Fehler bei {host}: {e}")
            all_results[name] = []

    plt.figure(figsize=(12, 6))

    for name, rtts in all_results.items():
        if rtts:
            plt.plot(rtts, label=name)

    plt.title("Ping-Zeiten verschiedener Hosts")
    plt.xlabel("Ping-Nummer")
    plt.ylabel("Zeit (ms)")
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()