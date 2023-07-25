from flask import Flask, request, jsonify
import login_test  # 이것은 앞에서 만든 Selenium 스크립트입니다.
from flask_cors import CORS

# from celery import Celery


# def make_celery(app):
#     celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task

#     class ContextTask(TaskBase):
#         abstract = True

#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery


app = Flask(__name__)
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379',
#     CELERY_RESULT_BACKEND='redis://localhost:6379'
# )
# celery = make_celery(app)
CORS(app)


@app.route('/login', methods=['POST'])
# @celery.task()
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

# Schedule the task to run 30 seconds from now
        # login_test.apply_async(args=[id, pw, personnel, nextFuture, nextSaturday, nextSunday,
        #                        futureTime, wednesdayCheck], eta=datetime.utcnow() + timedelta(seconds=30))
        cookies, elapsed_time = login_test.login_test(
            "https://www.debeach.co.kr/", id, pw, personnel, nextFuture, nextSaturday, nextSunday, futureTime, wednesdayCheck)

        return str(elapsed_time), 200

    except Exception as e:
        error_message = str(e)
        response = {'success': False, 'error': error_message}
        return jsonify(response), 500


# @celery.task()
def run_login_test(id, pw, personnel, nextFuture, nextSaturday, nextSunday, futureTime, wednesdayCheck):
    cookies, elapsed_time = login_test.login_test(
        "https://www.debeach.co.kr/", id, pw, personnel, nextFuture, nextSaturday, nextSunday, futureTime, wednesdayCheck)

    return str(elapsed_time)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
