from flask import Flask, render_template, request
import json
from datetime import datetime
# smtplib ist für das Versenden von Emails.
import smtplib
from email.message import EmailMessage

app = Flask(__name__)


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

    msg.set_content(content)
    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    s.login('technical.user22@gmail.com', 'dsqpjsfoqksmzejy')
    s.send_message(msg)
    s.quit()


def create_reservation(form):
    # Überprüfung ob die gegebenen Daten im Formular die richtigen Datentypen sind.
    # print(form)
    for field in form.keys():
        if form[field] == "":
            return render_template("message.html",title='Fehlermeldung',  msg="Mindestens ein Feld ist leer.")
    try:
        hnumber = int(form["hausnummer"])
    except ValueError:
        return render_template("message.html",title='Fehlermeldung', 
                               msg="Die Hausnummer ist keine Zahl. Wenn keine Hausnummer vorhanden ist, bitte 0 eingeben.")
    try:
        plz = int(form["plz"])
    except ValueError:
        return render_template("message.html",title='Fehlermeldung', msg="Die Postleitzahl ist keine Zahl.")

    targetCheckInDate = datetime.strptime(form["checkIn"], "%Y-%m-%d")
    targetCheckOutDate = datetime.strptime(form["checkOut"], "%Y-%m-%d")

    # überprüfe, ob Checkout > Checkin
    if targetCheckInDate >= targetCheckOutDate:
        return render_template("message.html",title='Fehlermeldung', msg="Das Checkout Datum muss nach dem Checkin Datum sein.")

    #########################################################################################################################

    # Hier lesen wir die unsere Dateien ein
    with open("data/reservationen.json", "r") as file:
        reservations = json.loads(file.read())

    with open("data/hotelzimmer.json", "r") as file:
        rooms = json.loads(file.read())

    totalRequestedRooms = 0
    numRequestedRooms = {}
    freeRoomNumbers = {}
    for roomType in rooms.keys():
        requiredRooms = int(form["num" + roomType])
        totalRequestedRooms += requiredRooms
        numRequestedRooms[roomType] = requiredRooms
        start = rooms[roomType]["ZimmerNrStart"]
        end = rooms[roomType]["ZimmerNrEnd"]
        freeRoomNumbers[roomType] = [str(i) for i in range(start, end + 1)]

    if totalRequestedRooms == 0:
        return render_template("message.html",title='Fehlermeldung', msg="Sie haben noch kein Zimmer ausgewählt.")

    # Hier überprüfen wir, ob wir genügend Platz für den Gast haben
    # Zuerst itererieren wir über alle Zimmer und finden heraus, welche überhaupt frei sind
    for reservation in reservations:
        roomType = reservation["Zimmer"].split(" ")[0]
        roomNumber = reservation["Zimmer"].split(" ")[1]
        checkInDate = datetime.strptime(reservation["Check-In"], "%m/%d/%Y")
        checkOutDate = datetime.strptime(reservation["Check-Out"], "%m/%d/%Y")

        # Falls sich die 2 Zeitintervalle nicht überschneiden, überspringen wir diese Reservation.
        # Sonst ist das Zimmmer besetzt und wir müssen es von freeRoomNumbers entfernen.
        if targetCheckOutDate < checkInDate or targetCheckInDate > checkOutDate:
            continue
        elif roomNumber in freeRoomNumbers[roomType]:
            freeRoomNumbers[roomType].remove(roomNumber)

    for roomType in freeRoomNumbers.keys():
        if len(freeRoomNumbers[roomType]) < numRequestedRooms[roomType]:
            return render_template("message.html",title='Fehlermeldung',
                                   msg=f'Leider sind zum gewünschten Zeitpunkt nicht genügend Zimmer des Typs "{roomType}" verfügbar.')

    # Hier wissen wir definitiv, dass genügend Zimmer vorhanden sind.
    # Wir machen neue Reservationen und speichern diese in unsere Tabelle
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
            freeRoomNumbers[roomType].pop(0)
            reservations.append(newReservation)
            createdReservations.append(newReservation)

    with open('data/reservationen.json', "w") as file:
        file.write(json.dumps(reservations))

    #send_confirmation_email(form, createdReservations)

    successMsg = """
    Ihre Reservation war erfolgreich. Sie erhalten in kürze eine Bestätigung per E-Mail. 
    Wir freuen uns, Sie bald bei uns begrüssen zu dürfen und wünschen Ihnen eine angenehme Anreise!
    """
    return render_template("message.html", msg=successMsg)


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