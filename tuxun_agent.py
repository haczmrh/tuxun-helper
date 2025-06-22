# tuxun_agent.py (完整修正版)
import requests
from typing import Optional

class TuxunAgent:
    """一个简化的代理，用于和 tuxun.fun 的 API 进行交互。"""

    def __init__(self, cookie: str):
        if not cookie:
            raise ValueError("Cookie 不能为空。")
        self.base_url = "https://tuxun.fun"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Cookie': cookie
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def verify_login(self) -> bool:
        """通过请求用户简要信息来验证 Cookie 是否有效。"""
        url = f"{self.base_url}/api/get_profile"
        print("正在验证 Tuxun Cookie...")
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200 and response.json().get('data'):
                user_id = response.json()['data']['userId']
                print(f"Cookie 有效，当前用户 UID: {user_id}")
                return True
            else:
                print(f"Cookie 验证失败，服务器返回: {response.status_code}")
                return False
        except Exception as e:
            print(f"验证登录时发生网络错误: {e}")
            return False

    def get_pano_id(self, game_id: str) -> Optional[str]:
        """根据游戏ID获取街景的 Pano ID。"""
        url = f"{self.base_url}/api/v0/tuxun/solo/get?gameId={game_id}"
        print(f"正在向图寻服务器请求游戏数据 (ID: {game_id})...")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and data.get('data') and data['data'].get('rounds'):
                pano_id = data['data']['rounds'][-1]['panoId']
                print(f"成功获取 Pano ID: {pano_id}")
                return pano_id
            else:
                print("错误：返回的数据格式不正确，找不到 Pano ID。")
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print("错误：游戏ID未找到或已过期。")
            else:
                print(f"HTTP 错误: {e}")
                print("请检查你的Tuxun Cookie是否正确或已过期。")
            return None
        except Exception as e:
            print(f"请求游戏数据时发生未知错误: {e}")
            return None

    def get_google_streetview_image_url(self, pano_id: str) -> str:
        """根据 Pano ID 构建 Google 街景图片 URL。（旧方法，可保留）"""
        return f"https://streetviewpixels-pa.googleapis.com/v1/thumbnail?panoid={pano_id}&cb_client=maps_sv.tactile.gps&w=1024&h=768&yaw=0&pitch=0&thumbfov=100"
    
    def get_all_directional_image_urls(self, pano_id: str) -> dict[str, str]:
        """
        根据 Pano ID 构建四个基本方向（前、右、后、左）的 Google 街景图片 URL。
        通过改变 yaw 参数来实现，0=前, 90=右, 180=后, 270=左。
        """
        urls = {}
        base_url = f"https://streetviewpixels-pa.googleapis.com/v1/thumbnail?panoid={pano_id}&cb_client=maps_sv.tactile.gps&w=1024&h=768&pitch=0&thumbfov=100"
        directions = {
            "前": 0,
            "右": 90,
            "后": 180,
            "左": 270,
        }
        print("正在生成四个方向的图片URL...")
        for name, yaw in directions.items():
            urls[name] = f"{base_url}&yaw={yaw}"
        return urls