import RPi.GPIO as GPIO
from enum import Enum
import time
from Motortest import Motor, GuideMotorStep  # Motortest가 모듈 이름이라고 가정합니다.

servo_pin = 17

# GPIO 핀 번호 지정 방식 설정
GPIO.setmode(GPIO.BCM)

# Motor 클래스 인스턴스 생성
motor = Motor(servo_pin)

try:
    # 서보 모터 동작 예제
    motor.doGuideMotor(GuideMotorStep.reset)  # 0
    time.sleep(2)  # 2초 대기
    motor.doGuideMotor(GuideMotorStep.good)  # 좋은 상태에 따라 서보 모터 동작 180
    time.sleep(2)  # 2초 대기
    motor.doGuideMotor(GuideMotorStep.stop)  # 정지 상태에 따라 서보 모터 동작 90
    time.sleep(2)  # 2초 대기
    motor.doGuideMotor(GuideMotorStep.fail)  # 실패 상태에 따라 서보 모터 동작 135
    time.sleep(2)  # 2초 대기
    motor.doGuideMotor(GuideMotorStep.badGrade)  # 나쁜 등급 상태에 따라 서보 모터 동작 45
    time.sleep(2)  # 2초 대기
    motor.doGuideMotor(GuideMotorStep.goodGrade)  # 좋은 등급 상태에 따라 서보 모터 동작 135
    time.sleep(2)  # 2초 대기
    motor.doGuideMotor(GuideMotorStep.re)  # 0
    time.sleep(2)  # 2초 대기

finally:
    # 정리 작업 수행
    motor.cleanup()