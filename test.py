from matplotlib import font_manager
import os

# .ttf 폰트 경로 설정
font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')

# 폰트 파일을 직접 로드하고 확인
font = font_manager.FontProperties(fname=font_path)

# 폰트 이름 확인
print("Loaded font name:", font.get_name())