# main.py (增加登录验证后的版本)
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import requests
import io

from tuxun_agent import TuxunAgent

# ... (前面的代码不变) ...
load_dotenv()

GEMINI_API_KEY = os.getenv("API_KEY")
TUXUN_COOKIE = os.getenv("TUXUN_COOKIE")

if not GEMINI_API_KEY or not TUXUN_COOKIE:
    print("错误：无法加载 API_KEY 或 TUXUN_COOKIE。")
    print("请确保 .env 文件中已正确配置这两项。")
    exit()

try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    tuxun_agent = TuxunAgent(cookie=TUXUN_COOKIE)
except Exception as e:
    print(f"初始化服务时出错: {e}")
    exit()

# --- 新增的登录验证步骤 ---
if not tuxun_agent.verify_login():
    print("\n无法登录图寻服务器。请检查：")
    print("1. 你的网络连接是否正常。")
    print("2. 你的 .env 文件中的 TUXUN_COOKIE 是否正确且未过期。")
    exit()
# ---------------------------

def analyze_image_from_url(image_url: str) -> str:
    # ... (此函数内容不变) ...
    try:
        print(f"正在从URL下载图片...")
        image_response = requests.get(image_url, timeout=15)
        image_response.raise_for_status()
        
        img = Image.open(io.BytesIO(image_response.content))
        
        print("图片下载完成，正在请求 Gemini 分析...")
        prompt = """
        你是一位顶级的图寻（GeoGuessr）专家和地理学家。
        请根据这张街景图片，分析并只返回最可能的位置信息。

        请严格按照以下格式输出，不要添加任何多余的文字、解释或编号。
        在国家、省份/州、以及城市后面，用括号补充其在上一级行政区划中的大致方位。
        如果不确定某个层级，请填写该区域最知名的城市+方向。

        格式示例:
        大洲: 欧洲
        国家: 意大利 (欧洲南部)
        省份/州: 拉齐奥大区 (意大利中部)
        城市: 罗马 (拉齐奥大区中部)

        你的回答:
        大洲: [最可能的大洲]
        国家: [最可能的国家] ([在所属大洲的大致方位])
        省份/州: [最可能的省份/州] ([在所属国家的大致方位])
        城市: [最可能的城市] ([在所属省份/州的大致方位])
        """
        response = gemini_model.generate_content([prompt, img])
        return response.text
    except requests.exceptions.RequestException as e:
        return f"下载图片时出错: {e}"
    except Exception as e:
        return f"分析图片时发生未知错误: {e}"

if __name__ == "__main__":
    print("\n--- 自动化图寻助手已启动 ---")
    while True:
        # ... (主循环内容不变) ...
        game_id = input("\n请输入图寻的游戏ID (或输入 'q' 退出): ").strip()
        if game_id.lower() == 'q':
            break
        if not game_id:
            continue

        pano_id = tuxun_agent.get_pano_id(game_id)
        if not pano_id:
            continue

        image_url = tuxun_agent.get_google_streetview_image_url(pano_id)
        print(f"成功获取图片地址: {image_url}")
        
        analysis_result = analyze_image_from_url(image_url)
        
        print("\n--- Gemini 的分析结果 ---")
        print(analysis_result)
        print("--------------------------")

    print("程序已退出。")