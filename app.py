from flask import Flask, render_template, request

app = Flask(__name__)


def process_data(form):
    # Überprüfung ob die gegebenen Daten im Formular die richtigen Datentypen sind.
    try:
        num_nights = int(form["anzahl_nächte"])
    except ValueError:
        return render_template("failure.html", msg = "Die Anzahl Nächte ist keine Zahl.")
    try:
        num_pers = int(form["anzahl_personen"])
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
