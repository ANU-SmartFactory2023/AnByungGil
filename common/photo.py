import cv2
import http.client
import json
import numpy as np

class ImageCV:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def count_white_pixels(self, image):
        # 이미지를 흑백으로 변환
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 가우시안 블러를 사용하여 입력 영상의 잡음 제거
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # 이진화를 위한 임계값 설정 (여기서는 40을 기준으로 이진화)
        _, binary_image = cv2.threshold(blurred_image, 40, 255, cv2.THRESH_BINARY)

        # 흰색 픽셀 수 계산
        white_pixel_count = np.sum(binary_image == 255)

        return white_pixel_count

def run_webcam_binarization():
    # ImageCV 클래스의 인스턴스 생성
    # 웹캠 열기
    image_processor = ImageCV()

    while True:
        image = image_processor.cap.read()[1]

        # binarize_webcam 메서드 호출
        final_white_pixel_count = image_processor.count_white_pixels(image)

        # 결과 출력
        print(f'white pixel : {final_white_pixel_count}')

        if final_white_pixel_count is not None and final_white_pixel_count >= 10000:
            print("Poor")
            break

    # 웹캠 해제 및 창 닫기
    image_processor.cap.release()
    
    # 모든 창 닫기
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_webcam_binarization()