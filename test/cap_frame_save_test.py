import cv2

cap = cv2.VideoCapture(0)  # 创建 VideoCapture 对象，参数为摄像头索引   
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if cap.isOpened():  # 检查摄像头是否打开
    print("摄像头已打开")
    ret, frame = cap.read()  # 从摄像头读取一帧图像
   
    cv2.imwrite("Frame.jpg", frame)  # 显示图像

    cv2.imshow("Frame", frame)  # 显示图像
    cv2.waitKey(0)  # 等待按键按下
cap.release()  # 释放摄像头资源
cv2.destroyAllWindows()  # 销毁所有窗口
