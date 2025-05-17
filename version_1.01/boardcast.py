import pygame

pygame.mixer.init()

def Recentage():
    pygame.mixer.music.load()

    pygame.mixer.music.play()   

    while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(1)   
def Triangle(self):
        # 加载mp3文件
        pygame.mixer.music.load("sound\\shape\\tri.mp3")
        # 播放音乐
        pygame.mixer.music.play()
        # 等待音乐播放完毕
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(1)        
    
def Cricle(self):
    # 加载mp3文件
    pygame.mixer.music.load("sound\\shape\\cri.mp3")
    # 播放音乐
    pygame.mixer.music.play()
    # 等待音乐播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1)        

def Star(self):
    # 加载mp3文件
    pygame.mixer.music.load("sound\\shape\\star.mp3")
    # 播放音乐
    pygame.mixer.music.play()
    # 等待音乐播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1)        

def white(self):
    pass

def black(self):
    pass

def red(self):
    # 加载mp3文件
    pygame.mixer.music.load("sound\\shape\\red.mp3")
    # 播放音乐
    pygame.mixer.music.play()
    # 等待音乐播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1)    

def green(self):
    # 加载mp3文件
    pygame.mixer.music.load("sound\\color\\green.mp3")
    # 播放音乐
    pygame.mixer.music.play()
    # 等待音乐播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1)

def blue(self):
    # 加载mp3文件
    pygame.mixer.music.load("sound\\color\\blue.mp3")
    # 播放音乐
    pygame.mixer.music.play()
    # 等待音乐播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1)

def yellow(self):
    pass

def ID(self, id):
    # 加载mp3文件
    pygame.mixer.music.load("sound\\point\\" + str(id) + ".mp3")
    pygame.mixer.music.play()
    # 等待音乐播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1)

if __name__ == '__main__':
    Recentage()
    