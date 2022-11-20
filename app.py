from flask import Flask, render_template, request
import json
from datetime import datetime
app = Flask(__name__)


def process_data(form):
    # Überprüfung ob die gegebenen Daten im Formular die richtigen Datentypen sind.
    print(form)
    try:
        num_nights = int(form["anzahl_ez"])
    except ValueError:
        return render_template("failure.html", msg = "Die Anzahl Nächte ist keine Zahl.")
    try:
        num_pers = int(form["anzahl_dz"])
    except ValueError:
        return render_template("failure.html", msg ="Die Anzahl Personen ist keine Zahl.")
    try:
        num_hnumber = int(form["hausnummer"])
    except ValueError:
        return render_template("failure.html", msg = "Die Hausnummer ist keine Zahl. Wenn keine Hausnummer vorhanden ist, bitte 0 eingeben.")
    try:
        num_plz = int(form["plz"])
    except ValueError:
        return render_template("failure.html", msg = "Die Postleitzahl ist keine Zahl.")

    # Hier lesen wir die reservations.json Datei ein
    reservationen = []
    with open("data/reservationen.json", "r") as reservations_json:
        file_as_string = reservations_json.read()
        reservationen = json.loads(file_as_string)

    # Hier überprüfen wir, ob wir genügend Platz für den Gast haben

    # Zuerst itererieren wir über alle Zimmer und finden heraus, welche überhaupt
    # frei sind
    targetCheckInDate = form["checkIn"]
    targetCheckInDate = datetime.strptime(targetCheckInDate, "%Y-%m-%d")
    targetCheckOutDate = form["checkOut"]
    targetCheckOutDate = datetime.strptime(targetCheckOutDate, "%Y-%m-%d")

    # überprüfe, ob Checkout > Checkin
    if targetCheckInDate >= targetCheckOutDate:
        return render_template("failure.html", msg="Das Checkout Datum muss nach dem Checkin Datum sein.")

    requestedRooms = {
        "Einzelzimmer": int(form["anzahl_ez"]),
        "Doppelzimmer": int(form["anzahl_dz"]),
        "DoppelzimmerPlus":  int(form["anzahl_dzp"]),
        "Familienzimmer": int(form["anzahl_fz"]),
        "Studio": int(form["anzahl_st"])
    }

    freeRoomNumbers = {"Einzelzimmer": [str(i) for i in range(1,11)], "Doppelzimmer": [str(i) for i in range(11,21)], "DoppelzimmerPlus": [str(i) for i in range(21,31)], "Familienzimmer": [str(i) for i in range(31,41)], "Studio": [str(i) for i in range(41,51)]}
    for reservation in reservationen:
        roomType = reservation["Zimmer"].split(" ")[0]
        roomNumber = reservation["Zimmer"].split(" ")[1]
        checkInDate = reservation["Check-In"]
        checkInDate = datetime.strptime(checkInDate, "%m/%d/%Y")
        checkOutDate = reservation["Check-Out"]
        checkOutDate = datetime.strptime(checkOutDate, "%m/%d/%Y")

        # Falls sich die 2 Zeitintervalle nicht überschneiden, überspringen wir diese Reservation
        if targetCheckOutDate < checkInDate or targetCheckInDate > checkOutDate:
            continue
        else:
            try:
                freeRoomNumbers[roomType].remove(roomNumber)
            except ValueError:
                pass
    print(freeRoomNumbers)
    for roomType in freeRoomNumbers.keys():
        if len(freeRoomNumbers[roomType]) >= requestedRooms[roomType]:
            pass
        else:
            return "Error"

    # Hier wissen wir definitiv, dass genügend Zimmer vorhanden sind.
    # Wir machen eine neue reservation und speichern diese in unsere Tabelle

    i = 0
    for req in requestedRooms.keys():
        for _ in range(requestedRooms[req]):
            i += 1
            newReservation = {
                "id": len(reservationen) + i,
                "Zimmer": req,
                "name": form["nachname"] + " " + form["vorname"],
                "Check-In": form["checkIn"],
                "Check-Out": form["checkOut"]
            }
            reservationen.append(newReservation)

    with open('data/reservationen.json', "w") as reservations_json:
        reservations_json.write(json.dumps(reservationen))


    return "Success"
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # Wenn die Webseite mit GET aufgerufen wird, dann gibt die Webseite das Formular wieder.
        return render_template("index.html")
    elif request.method == 'POST':
        # Wenn die Webseite mit POST aufgerufen wird, dann werden die Daten ausgewertet.
        return process_data(request.form)
    else:
        return "Not Implemented"
if __name__ == "__main__":
    app.run(debug=True)
