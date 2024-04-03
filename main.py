import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class InputIDThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, driver, ID):
        super().__init__()
        self.driver = driver
        self.ID = ID

    def run(self):
        try:
            url = f"https://www.acmicpc.net/user/{self.ID}"
            self.driver.get(url)
            selector = "body > div.wrapper > div.container.content > div.row > div:nth-child(2) > div > div.col-md-9 > div:nth-child(2) > div.panel-body > div"

            try:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                text = element.text.strip()
                problem_list = text.split()
                self.finished.emit(', '.join(problem_list))
            except:
                self.finished.emit("선택자에 해당하는 요소를 찾을 수 없습니다.")
        except Exception as e:
            self.finished.emit(f"오류 발생: {str(e)}")

class AutomationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, driver, problem_list, ID):
        super().__init__()
        self.driver = driver
        self.problem_list = problem_list
        self.ID = ID

    def run(self):
        try:
            total_problems = len(self.problem_list)
            for i, problem in enumerate(self.problem_list, 1):
                url = f"https://www.acmicpc.net/status?from_mine=1&problem_id={problem}&user_id={self.ID}"
                self.driver.get(url)
                time.sleep(5)
                progress = int((i / total_problems) * 100)
                self.progress.emit(progress)

            self.finished.emit("자동화가 완료되었습니다.")
        except Exception as e:
            self.finished.emit(f"오류 발생: {str(e)}")

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
            if not self.driver:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

            ID = self.idInput.text()
            self.inputIDThread = InputIDThread(self.driver, ID)
            self.inputIDThread.finished.connect(self.handleInputIDFinished)
            self.inputIDThread.start()
        except Exception as e:
            self.resultText.append(f"오류 발생: {str(e)}")

    def handleInputIDFinished(self, result):
        self.problemListText.append(result)
        if "선택자에 해당하는 요소를 찾을 수 없습니다." not in result and "오류 발생" not in result:
            self.resultText.append("문제 리스트를 성공적으로 추출했습니다.")
            text = """
            1단계 : 백준 허브를 확장프로그램으로 크롬에서 설치하세요. 링크 : https://g.co/kgs/RFHU5JE
            2단계 : 백준 허브에 본인의 깃허브 계정과 레포지토리를 연결하세요.
            3단계 : 본인의 백준 계정에 로그인 한 후 시작 버튼을 누르세요.
            """
            self.resultText.append(text)

    def startAutomation(self):
        try:
            problem_list = self.problemListText.toPlainText().split(', ')
            ID = self.idInput.text()

            self.automationThread = AutomationThread(self.driver, problem_list, ID)
            self.automationThread.progress.connect(self.progressBar.setValue)
            self.automationThread.finished.connect(self.handleAutomationFinished)
            self.automationThread.start()
        except Exception as e:
            self.resultText.append(f"오류 발생: {str(e)}")

    def handleAutomationFinished(self, result):
        self.resultText.append(result)
        self.confirmButton.setEnabled(True)

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
