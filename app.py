from flask import Flask, request, jsonify
import login_test
from flask_cors import CORS
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# DB 컬럼 정보 (id : INTEGER, 나머지 : TEXT)
# id: 고유 번호
# uid: 유저 아이디
# upw: 유저 비밀번호
# personnel: 인원
# selectedDay: 매크로 시작 날짜
# nextFuture: 14일 뒤 예약일
# futureTime: 14일 뒤 예약 시간
# nextSaturday: 10일 뒤 예약일
# saturdayTime: 10일 뒤 예약 시간
# nextSunday: 11일 뒤 예약 일
# sundayTime: 11일 뒤 예약 시간
# wednesdayCheck: 수요일 예약인지 아닌지 확인용. 수요일이면 '3'

# db에 등록된 예약 정보를 확인 후 매크로 실행, 예약 정보 제거


def check_and_delete_reservations():
    try:
        current_datetime = datetime.now()
        print("Current Timestamp:", current_datetime)
        reservation_data = get_reservation_data()
        print(reservation_data)

        # 예약 정보 테이블에서 매크로 시작 날짜와 현재 날짜가 동일한 정보가 있는지 확인
        for row in reservation_data:
            selectedDay = datetime.strptime(row[4], '%Y-%m-%d')
            print(
                f'current_datetime: {current_datetime}, selectedDay: {selectedDay}')

            # 로그인 진행 시간을 08:59:30로 지정
            # 테스트 시에는 and 이후 제거
            if current_datetime.day == selectedDay.day and current_datetime.hour == 8 and current_datetime.minute == 59 and current_datetime.second >= 30:

                # 매크로 실행(로그인)
                cookies, elapsed_time = login_test.login_test(
                    "https://www.debeach.co.kr/",
                    row[1], row[2], row[3], row[5], row[6], row[7], row[8], row[9], row[10], row[11]
                )
                # db에서 해당 예약 정보 제거
                delete_reservation_data(row[0])
                return str(elapsed_time), 200

    except Exception as e:
        delete_reservation_data(row[0])
        print('Error:', e)


# CORS 에러 해결 코드
app = Flask(__name__)
CORS(app)


# DB에 예약 정보 추가
def insert_reservation_data(id, pw, selectedDay, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck, futurePersonnel, saturdayPersonnel, sundayPersonnel):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """

    INSERT INTO Reservation (uid, upw, selectedDay, nextFuture, futureTime, nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck, futurePersonnel, saturdayPersonnel, sundayPersonnel)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (id, pw, selectedDay, nextFuture, futureTime,
                   nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck, futurePersonnel, saturdayPersonnel, sundayPersonnel))

    conn.commit()
    conn.close()


# 전체 테이블 정보 조회
def get_reservation_data():
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """
    SELECT * FROM Reservation
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()
    print(f'rows: {rows}')
    return rows


# 예약 정보 제거
def delete_reservation_data(id):
    conn = sqlite3.connect("C:/golf_db/golf_db.db")
    cursor = conn.cursor()

    query = """
    DELETE FROM Reservation WHERE id=?
    """

    cursor.execute(query, (id,))

    conn.commit()
    conn.close()


# 예약 등록 컨트롤러
@app.route('/reservation', methods=['POST'])
def reservation_route():
    try:
        print(request.form)
        id = request.form.get('id')
        pw = request.form.get('pw')
        futurePersonnel = request.form.get('futurePersonnel')
        saturdayPersonnel = request.form.get('saturdayPersonnel')
        sundayPersonnel = request.form.get('sundayPersonnel')
        selectedDay = request.form.get('selectedDay')
        nextFuture = request.form.get('nextFuture')
        nextSaturday = request.form.get('nextSaturday')
        nextSunday = request.form.get('nextSunday')
        futureTime = request.form.get('futureTime')
        saturdayTime = request.form.get('saturdayTime')
        sundayTime = request.form.get('sundayTime')
        wednesdayCheck = request.form.get('wednesdayCheck')

        insert_reservation_data(id, pw, selectedDay, nextFuture, futureTime,
                                nextSaturday, saturdayTime, nextSunday, sundayTime, wednesdayCheck, futurePersonnel, saturdayPersonnel, sundayPersonnel)

        return jsonify({'success': True}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# 예약 정보 조회 컨트롤러
@app.route('/reservation_table', methods=['GET'])
def reservation_table():
    try:
        reservation_data = get_reservation_data()

        # db 테이블 정보를 json 형태로 프론트에 반환
        reservations = []
        for row in reservation_data:
            reservation = {
                'id': row[0],
                'uid': row[1],
                'upw': row[2],
                'selectedDay': row[3],
                'nextFuture': row[4],
                'futureTime': row[5],
                'nextSaturday': row[6],
                'saturdayTime': row[7],
                'nextSunday': row[8],
                'sundayTime': row[9],
                'wednesdayCheck': row[10],
                'futurePersonnel': row[11],
                'saturdayPersonnel': row[12],
                'sundayPersonnel': row[13]
            }
            reservations.append(reservation)

        return jsonify({'reservations': reservations}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# DB 예약 정보 제거 컨트롤러
@app.route('/reservation_cancel/<int:id>', methods=['DELETE'])
def reservation_cancel_route(id):
    try:
        delete_reservation_data(id)

        return jsonify({'success': True}), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# 스케줄러 적용
scheduler = BackgroundScheduler(daemon=True)
# 배포용 코드: 59분 30초마다 매크로 실행 가능한 예약 정보를 탐색함.
scheduler.add_job(check_and_delete_reservations,
                  trigger='cron', hour='*', minute='59', second='30')
# 테스트용 코드: 50초가 될 때마다 스케줄링
# scheduler.add_job(check_and_delete_reservations,
#                   'interval', seconds=50)
scheduler.start()

if __name__ == '__main__':

    app.debug = True
    app.run(host='0.0.0.0', port=5000)
