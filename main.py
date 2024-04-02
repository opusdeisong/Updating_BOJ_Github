import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class BaekjoonHub(QWidget):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.initUI()

    def initUI(self):
        # 윈도우 타이틀 설정
        self.setWindowTitle('Baekjoon Hub Automation')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # 백준 계정 ID 입력 레이아웃
        inputLayout = QHBoxLayout()
        label = QLabel('백준 계정 ID를 입력해주세요.')
        inputLayout.addWidget(label)

        self.idInput = QLineEdit()
        inputLayout.addWidget(self.idInput)

        inputButton = QPushButton('입력')
        inputButton.clicked.connect(self.inputID)
        inputLayout.addWidget(inputButton)

        layout.addLayout(inputLayout)

        # 시작 버튼
        startButton = QPushButton('시작')
        startButton.clicked.connect(self.startAutomation)
        layout.addWidget(startButton)

        # 문제 리스트 레이블
        self.problemListLabel = QLabel('문제 리스트:')
        layout.addWidget(self.problemListLabel)

        # 문제 리스트 텍스트 에디터
        self.problemListText = QTextEdit()
        self.problemListText.setReadOnly(True)
        layout.addWidget(self.problemListText)

        # 결과 텍스트 에디터
        self.resultText = QTextEdit()
        self.resultText.setReadOnly(True)
        layout.addWidget(self.resultText)

        # 진행률 프로그레스바
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progressBar)

        # 확인 버튼
        self.confirmButton = QPushButton('확인')
        self.confirmButton.clicked.connect(self.close)
        self.confirmButton.setEnabled(False)
        layout.addWidget(self.confirmButton)

        self.setLayout(layout)

    def inputID(self):
        try:
            # 크롬 드라이버가 없으면 새로 생성
            if not self.driver:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

            ID = self.idInput.text()
            url = f"https://www.acmicpc.net/user/{ID}"
            self.driver.get(url)
            selector = "body > div.wrapper > div.container.content > div.row > div:nth-child(2) > div > div.col-md-9 > div:nth-child(2) > div.panel-body > div"

            try:
                # 선택자에 해당하는 요소가 나타날 때까지 최대 10초 대기
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                text = element.text.strip()
                problem_list = text.split()
                self.problemListText.append(', '.join(problem_list))
                self.resultText.append("문제 리스트를 성공적으로 추출했습니다.")
            except:
                self.resultText.append("선택자에 해당하는 요소를 찾을 수 없습니다.")

            # 백준 허브 설치 및 사용 안내 메시지
            text = """
            1단계 : 백준 허브를 확장프로그램으로 크롬에서 설치하세요. 링크 : https://chrome.google.com/webstore/detail/%EB%B0%B1%EC%A4%80%ED%97%88%EB%B8%8Cbaekjoonhub/ccammcjdkpgjmcpijpahlehmapgmphmk?utm_source=ext_app_menu
            2단계 : 백준 허브에 본인의 깃허브 계정과 레포지토리를 연결하세요.
            3단계 : 본인의 백준 계정에 로그인 한 후 시작 버튼을 누르세요.
            """
            self.resultText.append(text)
        except Exception as e:
            self.resultText.append(f"오류 발생: {str(e)}")

    def startAutomation(self):
        try:
            problem_list = self.problemListText.toPlainText().split(', ')
            ID = self.idInput.text()

            total_problems = len(problem_list)
            for i, problem in enumerate(problem_list, 1):
                url = f"https://www.acmicpc.net/status?from_mine=1&problem_id={problem}&user_id={ID}"
                self.driver.get(url)
                time.sleep(5)
                progress = int((i / total_problems) * 100)  # 진행률을 정수로 변환
                self.progressBar.setValue(progress)

            self.resultText.append("자동화가 완료되었습니다.")
            self.confirmButton.setEnabled(True)
        except Exception as e:
            self.resultText.append(f"오류 발생: {str(e)}")

    def closeEvent(self, event):
        # 윈도우 종료 시 크롬 드라이버 종료
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BaekjoonHub()
    ex.show()
    sys.exit(app.exec_())
