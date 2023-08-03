from flask import Flask, request, jsonify
import login_test  # 이것은 앞에서 만든 Selenium 스크립트입니다.
from flask_cors import CORS
import sqlite3
import schedule, threading, time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Your existing Flask code...


def check_and_delete_reservations():
    try:
        # Get the current date and time
        current_datetime = datetime.now()
        print("Current Timestamp:", current_datetime)
        # Get all rows from the Reservation table
        reservation_data = get_reservation_data()
        print(reservation_data)
        # Iterate through the rows to check conditions and delete if needed
        for row in reservation_data:
            selectedDay = datetime.strptime(row[4][:-14], '%Y-%m-%d')
            # next_future_date_str = row[4]  # Assuming nextFuture is a string representing a date
            # future_time_str = row[5]       # Assuming futureTime is a string representing time

            # # Convert next_future_date_str and future_time_str to datetime objects
            # year = int(next_future_date_str.split('년')[0].strip())
            # month = int(next_future_date_str.split('년')[1].split('월')[0].strip())
            # day = int(next_future_date_str.split('월')[1].split('일')[0].strip())

            # hour, minute = map(int, future_time_str.split(':'))
            # reservation_datetime = datetime(year, month, day, hour, minute)

            # Combine the date and time to get the complete datetime
            # reservation_datetime = datetime.combine(next_future_datetime, future_time_datetime.time())
            print(f'current_datetime: {current_datetime}, selectedDay: {selectedDay}')
            
            # ! 코드 수정: 로그인 진행 시간을 09:00로 지정

            if current_datetime.day == selectedDay.day and current_datetime.hour == 9 : # 테스트 시에 and 이후 제거and current_datetime.hour == 9
                # Perform the login_test method (or any other action you want)
                cookies, elapsed_time = login_test.login_test(
                    "https://www.debeach.co.kr/",
                    row[1], row[2], row[3], row[5], row[6], row[7], row[8], row[9], row[10], row[11]
                )
                # After performing the action, delete the reservation row
                delete_reservation_data(row[0])
                return str(elapsed_time), 200

    except Exception as e:
        delete_reservation_data(row[0])
        print('Error:', e)



app = Flask(__name__)
CORS(app)

# Function to insert data into the Reservation table
def insert_reservation_data(id, pw, personnel, selectedDay, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    # Prepare the SQL query
    query = """
    INSERT INTO Reservation (uid, upw, personnel, selectedDay, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Execute the query with the data provided
    cursor.execute(query, (id, pw, personnel, selectedDay, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck))

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
    print(f'rows: {rows}')
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
        selectedDay = request.form.get('selectedDay')
        nextFuture = request.form.get('nextFuture')
        nextSaturday = request.form.get('nextSaturday')
        nextSunday = request.form.get('nextSunday')
        futureTime = request.form.get('futureTime')
        saturdayTime = request.form.get('saturdayTime')
        sundayTime = request.form.get('sundayTime')
        wednesdayCheck = request.form.get('wednesdayCheck')
        
        # sqlite db 연결
        insert_reservation_data(id, pw, personnel, selectedDay, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck)

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
                'selectedDay' : row[4],
                'nextFuture': row[5],
                'futureTime': row[6],
                'nextSaturday': row[7],
                'saturdayTime': row[8],
                'nextSunday': row[9],
                'sundayTime': row[10],
                'wednesdayCheck': row[11],
            }
            reservations.append(reservation)

        # Return the data as a JSON response
        return jsonify({'reservations': reservations}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500
    

@app.route('/login', methods=['POST'])
def login_route(): # 스케줄링 기능 없이 로그인 및 예약 테스트
    try:
        print(request.form)
        id = request.form.get('id')
        pw = request.form.get('pw')
        personnel = request.form.get('personnel')
        selectedDay = request.form.get('selectedDay')
        nextFuture = request.form.get('nextFuture')
        nextSaturday = request.form.get('nextSaturday')
        nextSunday = request.form.get('nextSunday')
        futureTime = request.form.get('futureTime')
        wednesdayCheck = request.form.get('wednesdayCheck')
        saturdayTime = request.form.get('saturdayTime')
        sundayTime = request.form.get('sundayTime')

        cookies, elapsed_time = login_test.login_test(
            "https://www.debeach.co.kr/", id, pw, personnel, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck)

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


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(check_and_delete_reservations, trigger='cron', hour='*', minute='0', second='0')
# scheduler.add_job(check_and_delete_reservations, trigger='cron', second='0')
scheduler.start()
        
if __name__ == '__main__':
    

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    # Schedule the check_and_delete_reservations function to run every minute
    