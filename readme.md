Eine Projektbeschreibung mit Überlegungen und Entstehungsdetails mit Projektidee und Diagramme. Anleitung oder Walkthrough wie das Projekt installiert und benutzt wird, welche Funktionen vorhanden sind und wie diese eingesetzt werden.

**Problembeschreibung/Motivation**
 - Warum dieses Projekt:
_Spannend zu sehen, was bei einem Reservationstool alles beachtet werden muss. Motivation: Ich reise gerne und buche öfters Hotels._

 - Welches Problem löst das Projekt:
_Einfache Hotelreservation ohne persönlichen Kontakt._

 - Was macht das Projekt:
_Kann Hotelreservationen buchen._

**Betrieb**
 - Welche zusätzliche Pakete müssen bei Bedarf installiert werden. (Muss im Normalfall nicht beachtet werden. Python muss nicht erwähnt werden, da das bei einem Python Projekt impliziert ist.)
 - Was muss man bei der Ausführung beachten. Was muss eventuell davor noch gemacht werden.
 - Welch Datei muss ausgeführt werden

**Benutzung**
- Wie wird das Projekt benutzt
- Welche Optionen oder auch Spezialitäten existieren

**Architektur**
- Hier bei Bedarf eine kurze Beschreibung des Ablaufs des Programms auf Code Ebene z.B. als Ablaufdiagramm.

**Ungelöste/unbearbeitete Probleme**
 - Was wurde nicht gelöst
_Es werden nicht alle Kundendaten gespeichert. (keine Art von «Gästebuch»)_
  - Welche Verbesserungen könnten noch gemacht werden.

Read Me:

1. **Problembeschreibung**

Da das Reisen immer beliebter wird und Hotels somit mehr Gäste erwarten, ist eine digitale Lösung gefragt, um den Aufwand zu minimieren. Mit diesem Projekt soll für Hotels, sowie Gäste eine Lösung geboten werden, um Hotelzimmer ohne persönlichen Kontakt reservieren zu können.

**Relevante Informationen für eine Reservation:**

- Persönliche Angaben (Vorname, Name, Adresse, E-Mail)
- An- und Abreisedatum
- Anzahl Nächte
- Gewünschte Zimmer

1. **Betrieb**

Alle vorhandenen Dateien müssen von GitHub heruntergeladen werden. Anschliessend muss das Kommando py app.py ausgeführt werden, um den Server zu starten.

1. **Benutzung**

Zuerst muss die Webseite via [http://127.0.0.1:5000](http://127.0.0.1:5000/) geöffnet werden. Anschliessend gelingt man auf die Startseite, wo ein Formular ausgefüllt werden muss. Es können mehrere verschiedene Hotelzimmer mit einem Formular gebucht werden.

![](image%20read%20me/bild1.png?raw=true)

Nach erfolgreicher Eingabe der gültigen Daten und Prüfung der Zimmerkapazitäten wird die Buchung bestätigt und ein Bestätigungsmail wird versendet.

![](RackMultipart20221204-1-62qlpk_html_c73e8613a94265.png)

![](RackMultipart20221204-1-62qlpk_html_44f6a9914255e1b9.png)

Falls die eingegebenen Daten unvollständig oder nicht korrekt sind, wird eine Fehlermeldung angezeigt und das Formular muss erneut eingereicht werden.

![](RackMultipart20221204-1-62qlpk_html_11555f3a8ff2795d.png)

1. **Architektur**

In diesem Projekt werden zwei Datenbanken als json Files verwendet:

_hotelzimmer.json:_
Zimmername: Angabe der Zimmerkategorie

Kapazität: Anzahl Personen, welche sich in diesem Zimmer aufhalten können.
 ZimmerNrStart: Interne Zahl, um die Anzahl der Zimmer zu bestimmen. Die Zahl ist einzigartig. Das ist die erste Zimmernummer der jeweiligen Zimmerkategorie.
 ZimmerNrEnd: Interne Zahl, um die Anzahl der Zimmer zu bestimmen. Die Zahl ist einzigartig. Das ist die letzte Zimmernummer der jeweiligen Zimmerkategorie.

_reservationen.json:_
id: Reservationsnummer. Eindeutige Zahl.
 Zimmer: Zimmername und Nummer
 Name: Vollständiger Name des Gastes (Nachname + Vorname)
 Check-In: Datum (MM/DD/YYYY)
 Check-Out: Datum (MM/DD/YYYY)

Diese beiden Datensätze werden bei der Überprüfung der Zimmerkapazitäten verwendet.
 Eine neue Reservation eines Gastes wird im _reservationen.json_ File abgespeichert. Pro Zimmer wird jeweils eine seperate Reihe erfasst.

**Ablaufdiagramm**

![](RackMultipart20221204-1-62qlpk_html_5202ce72d4b83f3c.png)

**Logik für die Zimmerverfügbarkeit**

1. Zuerst wird angenommen, dass alle Zimmer verfügbar sind. Diese Zimmer werden in eine Liste hinzugefügt.

2. Danach werden alle vorhandenen Reservationen einzeln analysiert. Ein Zimmer wird von der Liste entfernt, wenn sich die Zeitintervalle überschneiden.

1. Zeitintervall: Gewünschtes Check-In und Check-Out Datum

2. Zeitintervall: Reservationsintervall des betrachteten Zimmers

3. Anschliessend berechnet das System die Anzahl verfügbarer Zimmer pro Zimmerkategorie und überprüft gleichzeitig, ob genügend Zimmer vorhanden sind.

4. Falls zu wenige Zimmer vorhanden sind, erscheint eine Fehlermeldung und die Buchung wird abgebrochen.

5. Falls die Prüfung erfolgreich ist, wird die Reservation getätigt und die Datenbank mit der neuen Buchung aktualisiert.

**Fehlermeldungen**

Falls…

…mindestens ein Feld leer ist.

…die Hausnummer und/oder PLZ keine Zahlen sind.

…das Check-Out Datum kleiner oder gleich Check-In Datum ist.

…die Gesamtzahl der ausgewählten Zimmer gleich 0 ist.

…nicht genügend Zimmer verfügbar sind.

1. **Verbesserungspotenzial**

- Login-System, sodass der Gast eine Übersicht über alle seine Buchungen erhält und auch die Möglichkeit hat, diese zu bearbeiten.
- Aktuell werden die persönlichen Daten der Gäste nicht komplett in einem «Gästebuch» gespeichert. Dies könnte künftig implementiert werden.
- Bilderkatalog, sodass der Gast einen visuellen Eindruck erhält.
