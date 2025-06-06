from extent import *
###测试完成可以顺序播放
"""
语音播报模块

功能：播报对应名字的语音

使用方式：
step1: board = Boardcast()
step2: running_thread_event.set()
step3: start_thread("cast", board.threading_sound)
step4: board.update_sound(name)

"""
class Boardcast():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.current_place = ""
        self.current_name = ""
    
###路径测试sound\shape\cri.mp3
    def _play_sound(self,place, name):
        """通用的播放声音方法"""
        print(f"尝试播放: {name}")
        
        if not os.path.exists(f"sound/{place}/{name}.mp3"):
            print(f"错误: 文件不存在 - {name}")
            return
            
        try:
            pygame.mixer.music.load(f"sound/{place}/{name}.mp3")
            pygame.mixer.music.play()
            
            # 调试: 显示播放状态
            print(f"开始播放 {name}")
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # 降低CPU使用率
            print(f"播放完成 {name}")
            
        except Exception as e:
            print(f"播放声音失败: {e}")
            
    def threading_sound(self):
        while running_thread_event.is_set():
            if cast_event.is_set():
                place = self.current_place
                name = self.current_name
                self._play_sound(place, name)
                cast_event.clear()
            time.sleep(0.1)  # 降低CPU使用率
        time.sleep(1)
    def update_sound(self, place, name):
        self.current_place = place
        self.current_name = name
        cast_event.set()
        
#####################################################################
def test():
    board = Boardcast()
    running_thread_event.set()
    start_thread("cast", board.threading_sound)
    
    print("\n=== 自动测试 ===")
    cmd = 1
    place="point"
    try:
    
        print(f"\n测试命令: {cmd}")
        board.update_sound(place,"1")
        time.sleep(2) 
        board._play_sound(place, 1)
        board._play_sound(place, 2)
    
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    finally:
        running_thread_event.clear()
        print("测试结束")

if __name__ == "__main__":
    test()