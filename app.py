from flask import Flask, request, jsonify
import login_test  # 이것은 앞에서 만든 Selenium 스크립트입니다.
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# Function to insert data into the Reservation table
def insert_reservation_data(id, pw, personnel, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    # Prepare the SQL query
    query = """
    INSERT INTO Reservation (uid, upw, personnel, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Execute the query with the data provided
    cursor.execute(query, (id, pw, personnel, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    

# Function to retrieve all rows from the Reservation table
def get_reservation_data():
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    # Prepare the SQL query
    query = """
    SELECT * FROM Reservation
    """

    # Execute the query and fetch all rows
    cursor.execute(query)
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    return rows

# Function to delete a reservation from the Reservation table
def delete_reservation_data(id):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    # Prepare the SQL query
    query = """
    DELETE FROM Reservation WHERE id=?
    """

    # Execute the query with the id provided
    cursor.execute(query, (id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



@app.route('/reservation', methods=['POST'])
def reservation_route():
    try:
        print(request.form)
        id = request.form.get('id')
        pw = request.form.get('pw')
        personnel = request.form.get('personnel')
        nextFuture = request.form.get('nextFuture')
        nextSaturday = request.form.get('nextSaturday')
        nextSunday = request.form.get('nextSunday')
        futureTime = request.form.get('futureTime')
        saturdayTime = request.form.get('saturdayTime')
        sundayTime = request.form.get('sundayTime')
        wednesdayCheck = request.form.get('wednesdayCheck')
        
        # sqlite db 연결
        insert_reservation_data(id, pw, personnel, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck)

        return jsonify({'success': True}), 200
        
    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500
    
@app.route('/reservation_table', methods=['GET'])
def reservation_table():
    try:
        # Get all rows from the Reservation table
        reservation_data = get_reservation_data()

        # Convert the data into a list of dictionaries (JSON format)
        reservations = []
        for row in reservation_data:
            reservation = {
                'id': row[0],
                'uid': row[1],
                'upw': row[2],
                'personnel': row[3],
                'nextFuture': row[4],
                'futureTime': row[5],
                'nextSaturday': row[6],
                'saturdayTime': row[7],
                'nextSunday': row[8],
                'sundayTime': row[9],
                'wednesdayCheck': row[10],
            }
            reservations.append(reservation)

        # Return the data as a JSON response
        return jsonify({'reservations': reservations}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500
    

@app.route('/login', methods=['POST'])
def login_route():
    try:
        print(request.form)
        id = request.form.get('id')
        pw = request.form.get('pw')
        personnel = request.form.get('personnel')
        nextFuture = request.form.get('nextFuture')
        nextSaturday = request.form.get('nextSaturday')
        nextSunday = request.form.get('nextSunday')
        futureTime = request.form.get('futureTime')
        wednesdayCheck = request.form.get('wednesdayCheck')

        cookies, elapsed_time = login_test.login_test(
            "https://www.debeach.co.kr/", id, pw, personnel, nextFuture, nextSaturday, nextSunday, futureTime, wednesdayCheck)

        return str(elapsed_time), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


@app.route('/reservation_cancel/<int:id>', methods=['DELETE'])
def reservation_cancel_route(id):
    try:
        # Delete the reservation with the provided id
        delete_reservation_data(id)

        return jsonify({'success': True}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)