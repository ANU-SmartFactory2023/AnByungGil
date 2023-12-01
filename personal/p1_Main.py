from enum import Enum
import time
from motor import Motor, GuideMotorStep
from sensor import Sensor
from server_communication import ServerComm
from model import ProcessModel
import os
import sys

# 현재 스크립트 파일의 디렉토리 경로
current_path = os.path.dirname(__file__)
# 외부 폴더의 경로 지정 (예: /home/pi/external_folder)
external_path = os.path.join(current_path, '/home/admin3/test/common')
# sys.path에 외부 폴더 경로 추가
sys.path.append(external_path)

class Step(Enum):
    start = 0
    input_part_sensor_check = 10
    wait_server_state = 20
    go_rail = 30
    photo_part_detect_sensor_check = 50
    stop_rail = 100
    photo_process = 150
    servo_motor_drive = 300
    go_rail_next = 350
    process_check = 370
    sonic_part_detect_sensor_check = 400
    slow_rail = 500

current_step = Step.start
running = True

sensor = Sensor()
server_comm = ServerComm()
motor = Motor()  # 모터 핀 번호

pass_or_fail = ''

INPUT_PART_SENSOR_PIN_NO = 17
PHOTO_PART_SENSOR_PIN_NO = 18
SONIC_PART_SENSOR_PIN_NO1 = 19

while running:
    print("running : " + str(running))  # 디버깅확인용
    time.sleep(0.1)

    match current_step:
        case Step.start:  # 초기 상태, 시스템 시작
            print(Step.start)
            motor.doGuideMotor(GuideMotorStep.stop)  # 서보 정렬
            motor.stopConveyor()  # DC모터 정지
            # 시작하기전에 검사할 것들 : 통신확인여부, 모터정렬, 센서 검수
            current_step = Step.input_part_sensor_check
        
        case Step.input_part_sensor_check:
            print(Step.input_part_sensor_check)
            if sensor.get_ir_sensor(INPUT_PART_SENSOR_PIN_NO):
                # 1번핀의 감지상태
                # 서버에게 센서 감지상태를 포스트로 전달한다.
                server_comm.ready(sensor.get_ir_sensor(INPUT_PART_SENSOR_PIN_NO))
                current_step = Step.wait_server_state
            
        case Step.wait_server_state:  # 서버로부터 ok 받을 때까지 대기
            print(Step.wait_server_state)
            result = server_comm.ready()  # get으로 물어보는 함수
            if result == "ok":
                current_step = Step.go_rail
            
        case Step.go_rail:  # DC모터 구동
            print(Step.go_rail)
            result = motor.doConveyor()
            current_step = Step.photo_part_detect_sensor_check

        case Step.photo_part_detect_sensor_check:  # 포토센서 감지 상태 확인
            print(Step.photo_part_detect_sensor_check)
            if sensor.get_ir_sensor(PHOTO_PART_SENSOR_PIN_NO):
                server_comm.photoStart()
                current_step = Step.stop_rail

        case Step.stop_rail:  # DC모터 정지
            print(Step.stop_rail)
            result = motor.stopConveyor()
            current_step = Step.photo_process
        
        case Step.photo_process:
            print(Step.photo_process)
            result = sensor.get_photo_sensor()  # 이미지 처리 값
            pass_or_fail = server_comm.photoEnd(result)  # 서버에 값을 전달(result)

            current_step = Step.servo_motor_drive
                
        case Step.servo_motor_drive:  # p or f 따라 서보모터 제어
            motor_step = motor.doGuideMotor(GuideMotorStep.stop)
            if (pass_or_fail == 'fail'):
                motor_step = GuideMotorStep.fail
            else:
                motor_step = GuideMotorStep.good

            motor.doGuideMotor(motor_step)
            current_step = Step.go_rail_next

        case Step.go_rail_next:  # DC모터 재구동, 다음 단계로 이동
            print(Step.go_rail)
            result = motor.doConveyor()
            current_step = Step.process_check
            
        case Step.process_check:
            if pass_or_fail == 'fail':  # 불량이므로 5초 대기
                motor_step = motor.doGuideMotor(GuideMotorStep.fail)
            else:
                motor_step = motor.doGuideMotor(GuideMotorStep.good)

            motor.doGuideMotor(motor_step)
            current_step = Step.sonic_part_detect_sensor_check

        case Step.sonic_part_detect_sensor_check:  # 초음파센서 물체 감지
            print(Step.sonic_part_detect_sensor_check)
            if sensor.get_ir_sensor(SONIC_PART_SENSOR_PIN_NO1):
                current_step = Step.slow_rail

        case Step.slow_rail:  # DC모터 천천히 구동
            print(Step.slow_rail)
            result = motor.slowConveyor()
            current_step = Step.start