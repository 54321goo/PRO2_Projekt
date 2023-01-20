# Flask importieren
from flask import Flask, render_template, request
# JSON importieren
import json
# Funktion notwendig, da das JSON File Daten in Form von einem Datum enthält.
from datetime import datetime, timedelta
# matplotlib ist für die Datenvisualisierung / Diagramm
import matplotlib.pyplot as plt
# smtplib ist für das Versenden von Emails.
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# hier wird definiert, wie das Bestätigungsmail aussehen wird.Dabei werden auch Angaben aus den JSON Files integriert.
def send_confirmation_email(form, createdReservations):
    msg = EmailMessage()
    msg['Subject'] = 'Ihre Reservationsbestätigung'
    msg['From'] = 'technical.user22@gmail.com'
    msg['To'] = form['email']

    rooms = f"{[reservation['Zimmer'] for reservation in createdReservations]}"

    content = f"""Guten Tag {form['vorname']} {form['nachname']}
    
    Vielen Dank für Ihre Reservation in unserem Hotel.
    
    Hiermit bestätigen wir Ihnen die Buchung vom {form['checkIn']} bis {form['checkOut']}. 
    Folgende Zimmer sind für Sie reserviert:
    {rooms}
    
    Wir freuen uns Sie bald bei uns begrüssen zu dürfen.
    
    Freundliche Grüsse
    Joanne Hermann
    """
# hier wird bestimmt, von welcher Mail-Adresse das Mail gesendet wird. In diesem Fall habe ich eine seperate Mail-Adresse erstellt.
    msg.set_content(content)
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.login('technical.user22@gmail.com', 'oogiwwrjvlpdxqqt')
    s.send_message(msg)
    s.quit()


def create_reservation(form):
    # Überprüfung ob die gegebenen Daten im Formular die richtigen Datentypen sind.
    # Fehlermeldung, wenn ein Feld leer ist.
    for field in form.keys():
        if form[field] == "":
            return render_template("message.html",title='Fehlermeldung',  msg="Mindestens ein Feld ist leer.")
    try:
    # Es wird geprüft ob die Hausnummer ein Integer ist. Wenn nicht, dann wird eine Fehlermeldung versendet.
        hnumber = int(form["hausnummer"])
    except ValueError:
        return render_template("message.html",title='Fehlermeldung', 
                               msg="Die Hausnummer ist keine Zahl. Wenn keine Hausnummer vorhanden ist, bitte 0 eingeben.")
    try:
    # Es wird geprüft ob die PLZ ein Integer ist. Wenn nicht, dann wird eine Fehlermeldung versendet.
        plz = int(form["plz"])
    except ValueError:
        return render_template("message.html",title='Fehlermeldung', msg="Die Postleitzahl ist keine Zahl.")

    # Hier wird definiert, dass es sich um ein Datum in folgender Form handelt. -> Jahr Monat Tag
    targetCheckInDate = datetime.strptime(form["checkIn"], "%Y-%m-%d")
    targetCheckOutDate = datetime.strptime(form["checkOut"], "%Y-%m-%d")

    # Es wird überprüft, ob Checkout > Checkin ist. Wenn nicht, wird eine Fehlermedlung versendet.
    if targetCheckInDate >= targetCheckOutDate:
        return render_template("message.html",title='Fehlermeldung', msg="Das Checkout Datum muss nach dem Checkin Datum sein.")

    #########################################################################################################################

    # Hier werden die Dateien eingelesen, um zu schauen ob die Reservierung (Nutzereingabe in das Formular) im Bezug zur Auslastung überhaupt möglich ist.
    with open("data/reservationen.json", "r") as file:
        reservations = json.loads(file.read())

    with open("data/hotelzimmer.json", "r") as file:
        rooms = json.loads(file.read())
    # Hier werden Variablen definiert, welche dann bei der Belegungsanalyse verwendet werden.
    totalRequestedRooms = 0
    numRequestedRooms = {}
    freeRoomNumbers = {}
    for roomType in rooms.keys():
        requiredRooms = int(form["num" + roomType])
        # totalRequestedRooms ist die Gesamtzahl der vom Benutzer geforderten Zimmer. Wenn diese Zahl = 0 ist, dann wird eine Fehlermeldung angezeigt. (-> Letzte Zeile dieses Code-Blockes)
        totalRequestedRooms += requiredRooms
        # numRequestedRooms ist ein dictionary wobei die jeweilige Zimmerkategorie der "key" ist und die Anzahl der angefragten Zimmer das "value".
        numRequestedRooms[roomType] = requiredRooms
        start = rooms[roomType]["ZimmerNrStart"]
        end = rooms[roomType]["ZimmerNrEnd"]
        # freeRoomNumbers ist ein dictionary wobei die jeweilige Zimmerkategorie der "key" ist und "value" zunächst Listen mit Zimmernummern der entsprechenden Zimmerkategorien.
        # nach der Belegungsanalyse sind dies die freien Zimmernummern.
        freeRoomNumbers[roomType] = [str(i) for i in range(start, end + 1)]

    if totalRequestedRooms == 0:
        return render_template("message.html",title='Fehlermeldung', msg="Sie haben noch kein Zimmer ausgewählt.")

    # Hier wird überprüft, ob genügend Platz für den Gast vorhanden ist
    # Zuerst wird über alle Zimmer itereriert und herausgefunden, welche überhaupt frei sind.
    for reservation in reservations:
    # mit dieser Split-Funktion wird die Zimmerkategorie von der Zimmerzahl getrennt. Wenn zum Beispiel Reservierung["Zimmer"] "Doppelzimmer 11" ist, wäre Reservierung["Zimmer"].split(" ") ["Doppelzimmer", "11"].
        roomType = reservation["Zimmer"].split(" ")[0]
        roomNumber = reservation["Zimmer"].split(" ")[1]
        checkInDate = datetime.strptime(reservation["Check-In"], "%m/%d/%Y")
        checkOutDate = datetime.strptime(reservation["Check-Out"], "%m/%d/%Y")

    # Falls sich die 2 Zeitintervalle nicht überschneiden, wird die jeweilige Reservation übersprungen.
    # Sonst ist das Zimmmer besetzt und es wird von freeRoomNumbers entfernt, sodass nur noch die freien Zimmer vorhanden sind..
        if targetCheckOutDate < checkInDate or targetCheckInDate > checkOutDate:
            continue
        elif roomNumber in freeRoomNumbers[roomType]:
            freeRoomNumbers[roomType].remove(roomNumber)
    # Hier wird geprüft ob die Anzahl freier Zimmer kleiner ist als die angefragte Anzahl. Wenn sie kleiner ist, dann hat es zu wenig freie Zimmer und eine Fehlermeldung entsteht.
    for roomType in freeRoomNumbers.keys():
        if len(freeRoomNumbers[roomType]) < numRequestedRooms[roomType]:
            return render_template("message.html",title='Fehlermeldung',
                                   msg=f'Leider sind zum gewünschten Zeitpunkt nicht genügend Zimmer des Typs "{roomType}" verfügbar.')

    # Hier ist es definitiv, dass genügend Zimmer vorhanden sind.
    # Es wird somit in der Tabelle im JSON File als neue Reservation gespeichert.
    createdReservations = []
    for roomType in rooms.keys():
        for room in range(numRequestedRooms[roomType]):
            newReservation = {
                "id": len(reservations) + 1,
                "Zimmer": roomType + " " + freeRoomNumbers[roomType][0],
                "Name": form["nachname"] + " " + form["vorname"],
                "Check-In": targetCheckInDate.strftime("%m/%d/%Y"),
                "Check-Out": targetCheckOutDate.strftime("%m/%d/%Y")
            }
            # freeRoomNumbers ist eine Liste der freien Zimmernummern.
            # Da jeweils das erste freie Zimmer der jeweiligen Zimmerkategorie für die Reservation gebucht wird, wird pop(0) verwendet. So wird das Zimmer dann aus der Liste entfernt.
            freeRoomNumbers[roomType].pop(0)
            # Hier wird die neue Reservation zur Tabelle mit den Reservierungen hinzugefügt, wie auch zur Liste mit den Reservierungen.
            reservations.append(newReservation)
            createdReservations.append(newReservation)

    with open('data/reservationen.json', "w") as file:
        file.write(json.dumps(reservations))
    # Hier wird das Bestätigungsmail versendet.
    send_confirmation_email(form, createdReservations)
    # Bei einer erfolgreichen Reservierung, gelangt der Nutzer auf eine Bestätigungsseite.
    successMsg = """
    Ihre Reservation war erfolgreich. Sie erhalten in kürze eine Bestätigung per E-Mail. 
    Wir freuen uns, Sie bald bei uns begrüssen zu dürfen und wünschen Ihnen eine angenehme Anreise!
    """
    return render_template("message.html", msg=successMsg)

@app.route("/belegung")
def belegung():
    # Hier werden die JSON Dateien eingelesen, um die Belegung messen zu können.
    with open("data/reservationen.json", "r") as file:
        reservations = json.loads(file.read())

    with open("data/hotelzimmer.json", "r") as file:
        roomTypes = json.loads(file.read())
    # Hier wird definiert, dass die Belegung der nächsten 60 Tage angeschaut wird.
    today = datetime.now()
    # days ist eine Liste der Daten vom heutigen Zeitpunkt plus 60 Tage.
    days = [today + timedelta(days=x) for x in range(61)]
    # occupancies ist ein dictionary wobei der "key" die Zimmerkategorie ist und "value" zunächst eine leere Liste.
    occupancies = {}
    graphNames = []
    # für jeden Zimmertyp wird die Belegung seperat analysiert.
    for roomType in roomTypes.keys():
        occupancies[roomType] = []
        # Dieser Code filtert alle Reservierungen im JSON File Reservationen, indem sie nur die passenden Reservationen der Zimmerkategorie, welche gerade analysiert wird anschaut. (habe gegooglet wie man eine Liste mit solchen Bedinungen filtert :))
        reservationsOfType = list(filter(lambda x: x["Zimmer"].split(" ")[0] == roomType, reservations))

        for day in days:
            # availableRoomsOfType ist die Anzahl der Zimmer der Zimmerkategorie (frei und belegt)
            # für jede Reservation in der Liste der gefilterten Reservationen wird availableRoomsOfType um 1 verringert, wenn der aktuelle Tag (der analysiert wird) im Bereich [Checkin, Checkout] der Reservation befindet.
            availableRoomsOfType = roomTypes[roomType]["ZimmerNrEnd"] - roomTypes[roomType]["ZimmerNrStart"] + 1
            for reservation in reservationsOfType:
                checkInDate = datetime.strptime(reservation["Check-In"], "%m/%d/%Y")
                checkOutDate = datetime.strptime(reservation["Check-Out"], "%m/%d/%Y")
                if day >= checkInDate and day < checkOutDate:
                    availableRoomsOfType -= 1
            # nachdem alle Reservationen der Zimmerkategorie durchgesehen wurden, wird die endgültige Anzahl der verfügbaren Zimmer zur Liste occupancies[roomType] hinzugefügt.
            occupancies[roomType].append(availableRoomsOfType)

        name = f'{roomType}_belegung.png'
        graphNames.append(name)
        # Hier wird definiert, wie das Diagramm aussehen sollte. plt.  = Diagramm
        plt.figure(figsize=(8, 6), dpi=80)
        plt.plot(days, occupancies[roomType], color="#ffd85c", linewidth=3)
        plt.xticks(rotation=45)
        plt.yticks(range(0, max(occupancies[roomType]) + 1, 1))
        plt.title(f"Anzahl freie {roomType}", fontsize=18, color="#000000")
        plt.xlabel("Tage", fontsize=18, color="#000000")
        plt.ylabel("Anzahl", fontsize=18, color="#000000")
        plt.savefig(f'static/images/{name}', bbox_inches='tight', transparent=False)
        plt.clf()

    return render_template("occupancy.html", graphs=graphNames)
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Wenn die Webseite mit GET aufgerufen wird, dann gibt die Webseite das Formular wieder.
        return render_template("index.html")
    elif request.method == 'POST':
        # Wenn die Webseite mit POST aufgerufen wird, dann werden die Daten ausgewertet.
        return create_reservation(request.form)


if __name__ == "__main__":
    app.run(debug=True)