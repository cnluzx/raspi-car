import cv2
# 创建 VideoCapture 对象
cap = cv2.VideoCapture(0)##测试视频流
# 检查摄像头是否打开
if not cap.isOpened():
    print("无法打开摄像头")
    exit()
# 获取视频流
while True:
    # 读取一帧
    ret, frame = cap.read()
    # 检查是否读取成功
    if not ret:
        print("无法读取帧")
        break
    # 显示帧
    cv2.imshow("摄像头", frame)
    # 按下 ESC 键退出
    if cv2.waitKey(1) & 0xFF == 27:
        break
# 释放摄像头
cap.release()
# 销毁所有窗口
cv2.destroyAllWindows()