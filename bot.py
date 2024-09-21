import requests
import sys
import time

class MoonBix():
    query_id = None
    access_token = None
    def __init__(self, query_id):
        self.query_id = query_id
    
    def header(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Content-Type": "application/json",
            "Origin": "https://www.binance.com",
            "Referer": "https://www.binance.com/en/game/tg/moon-bix",
            "x-growth-token": self.access_token
        }
    
    def eligibility_check(self):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-eligibility"
        data = {
            "resourceId":2056,
            "orionBusinessTypeList":["TG_mini_app_01"]
        }
    
    def get_task(self):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list"
        data = {"resourceId":2056}
    
    def get_token(self):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken"
        data = {
            "queryString": self.query_id,
            "socialType": "telegram"
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            if response.json()['code'] == '000000':
                self.access_token = response.json()['data']['accessToken']
            else:
                print("Error: ", response.json()['message'])
        else:
            print("Error: ", response.status_code)
    
    def get_user_info(self):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info"
        data = {
            "resourceId": 2056
        }
        response = requests.post(url, json=data, headers=self.header())
        if response.status_code == 200:
            if response.json()['code'] == '000000':
                self.user_info = response.json()['data']
            else:
                print("Error: ", response.json()['message'])
                
    def wait_playing(self, seconds = 0):
        while seconds >= 0:
            seconds -= 1
            print(f"Wait {seconds} s", end="\r")
            time.sleep(1)
        time.sleep(1)
            
    def play_game(self):
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start"
        data = {
            "resourceId": 2056
        }
        response = requests.post(url, json=data, headers=self.header())
        if response.json()['code'] == '116002':
            print("No games left to be played!")
            return False
        if response.json()['code'] != '000000':
            print("Game start error !")
            return False
        
        print("Game Started!")
        game_metainfo = response.json()
        url = "https://vemid42929.pythonanywhere.com/api/v1/moonbix/play"
        response = requests.post(url, json=game_metainfo)
        if response.json()['message'] != 'success':
            print("Could not get game payload!")
            return False
        
        result_game = response.json()['game']

        print("Waiting 45 seconds to complete the game...")
        self.wait_playing(45)
        url = "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete"
        data = {
            "resourceId": 2056,
            "payload": result_game['payload'],
            "log": result_game['log']
        }
        response = requests.post(url, json=data, headers=self.header())
        if response.json()['code'] == '000000' and response.json()['success']:
            print(f"Game completed ! Reward: {result_game['log']}")
            return True
        else:
            print("Game completion error !")
            return False
            
    def play(self):
        max_game = 6
        self.get_token()
        self.eligibility_check()
        while True:
            try:
                self.get_user_info()
                game_remaining = self.user_info['metaInfo']['totalAttempts'] - self.user_info['metaInfo']['consumedAttempts']
                while game_remaining > 0:
                    print("Total Game Remaining: ", self.user_info['metaInfo']['totalAttempts'] - self.user_info['metaInfo']['consumedAttempts'])
                    self.play_game()
                    game_remaining -= 1
                    time.sleep(2)
                
                print("All games completed!")
                self.get_user_info()
                wait_times = max_game - (self.user_info['metaInfo']['totalAttempts'] - self.user_info['metaInfo']['consumedAttempts'])
                total_wait = (wait_times * 600) + (self.user_info['metaInfo']['attemptRefreshCountDownTime'] / 1000)
                
                self.wait_playing(total_wait)
            except KeyboardInterrupt:
                sys.exit()
        
if __name__ == "__main__":
    # read data from file
    
    with open("data.txt", "r") as file:
        query_id = file.read()
    if not query_id:
        print("Query ID not found!")
        sys.exit()
    try:
        app = MoonBix(query_id)
        app.play()
    except KeyboardInterrupt:
        sys.exit() 
