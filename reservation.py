from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
from custom_exception import NoAvailableSlotsException


def find_closest_time(bk_time_list, futureTime):  # 최적시간 찾기
    # 조건: 지정시간 1시간 내외, 그 중 가장 가까운 시간 택 1
    # Convert futureTime to datetime for comparison
    target_time = datetime.strptime(futureTime, "%H:%M")

    # Initialize variables to track closest time
    closest_time = None
    min_diff = float('inf')

    # Iterate through bk_time_list
    for time_str in bk_time_list:
        # Convert time_str to datetime for comparison
        time = datetime.strptime(time_str, "%H:%M")

        # Calculate time difference in minutes
        diff = abs((time - target_time).total_seconds() // 60)

        # Check if the current time is closer than the previous closest time
        if diff <= 60:
            if diff < min_diff:
                closest_time = time_str
                min_diff = diff

    return closest_time


def reservation_test(driver, target_day, elements, target_month, futureTime, personnel, isWednesday):
    print("reservation_test module open!")

    for element in elements:
        # Find the <h2> element within the current element
        h2_elements = element.find_elements(By.TAG_NAME, 'h2')

        # Iterate through each <h2> element
        for h2_element in h2_elements:
            # Get the text value of the <h2> element
            h2_text = h2_element.text

            # Check if the target month is present in the text
            if target_month+'월' in h2_text:
                print(h2_text)
                table_element = h2_element.find_element(
                    By.XPATH, './following-sibling::table')

                td_elements = table_element.find_elements(
                    By.XPATH, './/td[@class="  "]')
                print('success to finding td_elements!')
                for td_element in td_elements:
                    a_elements = td_element.find_elements(
                        By.TAG_NAME, 'a')  # 에러
                    for a_element in a_elements:
                        a_text = a_element.text

                        if str(target_day) in a_text:
                            print('trying to find table..')
                            try:
                                td_element.click()
                            except Exception as e:
                                print(
                                    f"Error occurred while clicking on td_element: {e}")
                                driver.close()
                                return '해당 날짜에 예약 가능한 시간대가 없습니다.(버튼 로드 실패1)', 500
                            print('successed to finding reservable day!')
                            elements = driver.find_element(
                                By.CLASS_NAME, 'col-xs-7')

                           # 첫번째 예약 버튼 로드까지 기다림
                            try:
                                tr_elements_load = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                                    (By.XPATH, '//*[@id="booking-index"]/div[2]/div[2]/div/table/tbody/tr[1]/td[5]/button[1]')))
                            except TimeoutException:
                                print(
                                    "Timeout occurred. Element tr_elements_load was not found within the specified time.")
                                driver.close()
                                return '해당 날짜에 예약 가능한 시간대가 없습니다.(버튼 로드 실패2)', 500
                            time_tbody = elements.find_element(
                                By.XPATH, '//*[@id="booking-index"]/div[2]/div[2]/div/table/tbody')
                            tr_elements = time_tbody.find_elements(
                                By.TAG_NAME, "tr")
                            bk_time_list = []
                            td_elements_list = []
                            for tr in tr_elements:
                                td_elements = tr.find_elements(
                                    By.CLASS_NAME, "bk_time")
                                td_elements_list.extend(td_elements)
                                for td in td_elements:
                                    strong_element = td.find_element(
                                        By.TAG_NAME, "strong")
                                    bk_time_list.append(strong_element.text)

                            print("bk_time_list:", bk_time_list)
                            closest_time = find_closest_time(
                                bk_time_list, futureTime)

                            if closest_time is not None:
                                print("Closest time:", closest_time)
                            else:
                                print("There is no available time slot.")

                            # 가장 가까운 시간의 tr요소에서 예약 버튼 찾아서 클릭
                            for tr in tr_elements:
                                td_element = tr.find_element(
                                    By.CLASS_NAME, "bk_time")
                                strong_element = td_element.find_element(
                                    By.TAG_NAME, "strong")
                                if str(closest_time) == strong_element.text:
                                    print('find matched value!')
                                    reservation_btn = tr.find_elements(
                                        By.TAG_NAME, "button")[0]
                                    reservation_btn.click()

                                    # 인원 수 체크
                                    radio_element = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.XPATH, '//*[@id="form-create"]/div[6]/div')))
                                    print(radio_element)
                                    if personnel == '3':
                                        cnt3 = radio_element.find_element(
                                            By.XPATH, '//*[@id="form-create"]/div[6]/div/label[1]')
                                        cnt3.click()
                                    else:
                                        cnt4 = radio_element.find_element(
                                            By.XPATH, '//*[@id="form-create"]/div[6]/div/label[2]')
                                        cnt4.click()
                                    print("예약 완료!")
                                    return
                else:
                    print('cannot find matched a_text.. ㅜ.ㅜ')
                    if isWednesday:
                        return
                    else:
                        driver.close()
                        raise NoAvailableSlotsException(
                            '해당 날짜에 예약 가능한 시간대가 없습니다.')

        if target_month in h2_text:
            break
