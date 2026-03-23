# Roadmap: ATAK-CIV & 7S-Rapport Integration (4G/5G)

## 1. Målbild & Koncept
Skapa ett robust ledningssystem där personal i fält kan använda ATAK-CIV över 4G/5G mobildata för att se varandra (Blue Force Tracking) och där "7S-rapporter" från det befintliga rapportsystemet automatiskt omvandlas till taktiska kartpunkter (Cursor on Target / CoT) som uppdateras på skärmarna. På staben rullar WinTAK (Windows-versionen av ATAK) på en 65-tums TV, filtrerad för att ge en omedelbar överblick av alla inkomna fientliga rapporter.

## 2. Arkitektur (The Missing Link: TAK Server)
Appen från Google Play är en ren klient. För att mobiler ska kunna prata med varandra ifrån olika mobilnät (t.ex. Telia 4G och Tele2 5G), måste all trafik gå via en central nätverksnod, en **TAK Server**.

*   **Klienter i fält:** Android-telefoner med ATAK-CIV.
*   **Server:** "FreeTAKServer" (FTS) eller liknande. Snurrar på en egen dator med publik IP eller via en billig molntjänst/VPS.
*   **Stabsklient (TV):** En PC med Windows som kör **WinTAK** och som ansluter till samma TAK Server.
*   **7S-Bryggan:** Stabens Python-backend (den som läser Signal-meddelanden enligt `stab-roadmap.md`) utökas så att den automatiskt översätter alla inkomna 7S-rapporter till ATAK-språket "CoT XML" och puchar in dem i TAK-servern.

---

## 3. Fasplan för Genomförande (Från Ax till Limpa)

### Fas 1: Grunduppsättning (Lokalt / Utan Server)
1.  **Säkerställ ATAK-CIV:** Det du laddat ner från Google Play är rätt (ATAK-CIV). Du kan eventuellt behöva ladda ner plugins senare, men för stunden behövs inga.
2.  **Lär känna gränssnittet:**
    *   Sätt ditt *Callsign* (ditt namn i nätverket, t.ex. "Alpha").
    *   Lär dig skicka fasta markörer.
    *   Bekanta dig med kart-källor (ladda ner en lokal karta eller ställ in online-kartor).
3.  **WIFI-test (Valfritt):** Om två mobiler befinner sig på *samma WiFi-nätverk* upptäcker ATAK ofta varandra automatiskt via Multicast. Testa detta om ni vill bekräfta att apparna fungerar innan vi sätter upp servern.

### Fas 2: Uppsättning av ATAK-Server / FTS (Möjliggör 4G)
För att knyta ihop alla enheter över internet behöver vi hosta en FreeTAKServer (FTS).
1.  **Välj driftsmiljö:** Antingen en maskin stående hos er (kräver port forwarding i routern för port 8080 TCP etc), *eller* det rekommenderade: en molnserver (Ubuntu Linux) för ca 50-100 kr/mån (t.ex. Hetzner, DigitalOcean).
2.  **Installation av FTS:** Jag assisterar med exakta terminalkommandon (ZeroTouch installation) för att sätta upp FreeTAKServer på nolltid.
3.  **Anslut Mobilerna:** Under "Network Preferences -> Manage Server Connections" i telefonernas ATAK-app fyller ni i serverns IP-adress. Nu kan alla se varandra över 4G!

### Fas 3: Integrera 7S Rapporter (Python-Bryggan)
ATAK kommunicerar via `Cursor on Target (CoT)`. Vi bygger ut vår Python-lösning (`main.py`) så att den pratar med ATAK-nätverket.
1.  **Mottagning:** Precis som tidigare läser programmet 7S-textsträngen från Signal.
2.  **Konvertering till CoT:** Koden skapar dynamiskt ett XML-meddelande.
    *   *Plats:* 7S-MGRS konverteras till Latitude/Longitude och läggs i XML.
    *   *Klassificering:* Punkten markeras som en fientlig observation (ex. röd ikon, CoT-typ: `a-h-G`).
    *   *Information:* Hela rapporttexten (inkl. Sagesman och Stund) stoppas in under *Remarks*-fältet i CoT-meddelandet, så att man kan klicka på ikonen för att läsa alla 7S-detaljer.
3.  **Sändning:** Python-koden trycker via TCP-socket in meddelandet till FreeTAKServer, som direkt pushar ut det till alla uppkopplade mobiltelefoner.

### Fas 4: Stabs-TV med WinTAK
1.  **Installera WinTAK:** Ladda ner WinTAK-CIV från tak.gov till stabsdatorn (den med 65-tums TV:n).
2.  **Anslut WinTAK:** Logga in på FreeTAKServer med stabs-datorn.
3.  **Filtrering ("7S Report Filter"):** I WinTAK navigerar vi till *Data Filters*. Här stänger vi av visning av egen trupp/blåa styrkor och skapar ett hårt filter på fientliga indikatorer. På så sätt hålls kartan enormt ren och visar *bara* inkomna 7S-rapporter.
4.  **Notiser & Larm (Valfritt):** Sätt upp Audio Alerts i WinTAK för när en red mark (fientlig CoT) dyker upp.

---

## Hur vi går vidare
Vi kan hantera i vilken ordning du vill:
1.  **Fokus PWA/Stab-projektet först:** Vi börjar bygga **Python-bryggan (7S till CoT-XML)** som skickar punkter lokalt (Fas 3) för att säkerställa att din vision om rapportkonvertering fungerar.
2.  **Fokus ATAK Fält först:** Vi fokuserar omedelbart på **FreeTAKServer (Fas 2)** för att du och dina kollegor ska få P2P-kommunikation över mobiltelefonerna.

Vad prioriterar vi?
