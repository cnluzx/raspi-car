import cv2
import numpy as np
import time
from collections import Counter

class Detect_object:
    def __init__(self):
        self.if_shape_test = True
        self.if_color_test = True
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.area_min = 10000
        self.rectangle_thresh = 60
        self.up_trapezoid_thresh = 50
        self.down_trapezoid_thresh = 80
        self.square_thresh = 30
        self.canny_threshold1 = 50
        self.canny_threshold2 = 88
        self.roi_x = 5
        self.roi_y = 5
        self.roi_w = 5
        self.roi_h = 5
        self.ROI_range = 50
        self.red_low = (0, 0, 100)
        self.red_up = (50, 50, 255)  # 修正了这里的括号问题
        self.blue_low = (100, 0, 0)
        self.blue_up = (255, 50, 50)
        self.red_iter = 1
        self.blue_iter = 1
        self._threold = 50
        self.frame_count = 0
        self.init_trackbars()

    def init_trackbars(self):
        cv2.namedWindow("Parameters")
        cv2.createTrackbar("Area Min", "Parameters", self.area_min, 50000, self.nothing)
        cv2.createTrackbar("Rectangle Thresh", "Parameters", self.rectangle_thresh, 200, self.nothing)  # 修正了这里的名称拼写错误
        cv2.createTrackbar("Up Trapezoid Thresh", "Parameters", self.up_trapezoid_thresh, 100, self.nothing)
        cv2.createTrackbar("Down Trapezoid Thresh", "Parameters", self.down_trapezoid_thresh, 100, self.nothing)
        cv2.createTrackbar("Square Thresh", "Parameters", self.square_thresh, 50, self.nothing)
        cv2.createTrackbar("Canny Thresh1", "Parameters", self.canny_threshold1, 200, self.nothing)  # 修正了这里的名称拼写错误
        cv2.createTrackbar("Canny Thresh2", "Parameters", self.canny_threshold2, 200, self.nothing)

    def nothing(self, x):
        pass

    def update_parameters(self):
        self.area_min = cv2.getTrackbarPos("Area Min", "Parameters")
        self.rectangle_thresh = cv2.getTrackbarPos("Rectangle Thresh", "Parameters")
        self.up_trapezoid_thresh = cv2.getTrackbarPos("Up Trapezoid Thresh", "Parameters")
        self.down_trapezoid_thresh = cv2.getTrackbarPos("Down Trapezoid Thresh", "Parameters")
        self.square_thresh = cv2.getTrackbarPos("Square Thresh", "Parameters")
        self.canny_threshold1 = cv2.getTrackbarPos("Canny Thresh1", "Parameters")
        self.canny_threshold2 = cv2.getTrackbarPos("Canny Thresh2", "Parameters")

    def detect_shape_color(self, img):
        global img_two
        center_x_mu = 0
        center_y_mu = 0
        self.update_parameters()
        img_blur = cv2.GaussianBlur(img, (5, 5), 1)
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        img_median = cv2.medianBlur(img_gray, 5)
        self._threold += 2
        if self._threold > 170:
            self._threold = 50
        ret, img_two = cv2.threshold(img_gray, self._threold, 255, cv2.THRESH_BINARY_INV)
        img_canny = cv2.Canny(img_two, self.canny_threshold1, self.canny_threshold2)
        kernel = np.ones((5, 5))
        img_dilate = cv2.dilate(img_canny, kernel, iterations=1)
        img_erode = cv2.erode(img_dilate, kernel, iterations=1)
        img_gradient = cv2.morphologyEx(img_erode, cv2.MORPH_GRADIENT, np.ones((3, 3)))
        if self.if_shape_test:
            cv2.imshow("Gray", img_gray)
            cv2.imshow("img_two", img_two)
            cv2.imshow("Original", img)
            cv2.imshow("Canny", img_canny)
            cv2.imshow("img_Contours", img_gradient)
        contours, _ = cv2.findContours(img_gradient, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.area_min:
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)  # 调整了轮廓近似精度

                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    center_x = x + w / 2
                    center_y = y + h / 2
                    mu = cv2.moments(cnt)
                    center_x_mu = int(mu["m10"] / mu["m00"]) if mu["m00"] != 0 else 0
                    center_y_mu = int(mu["m01"] / mu["m00"]) if mu["m00"] != 0 else 0
                    approx = np.array(approx).squeeze()
                    sorted_points = approx[np.argsort(approx[:, 1])]
                    if sorted_points[0][0] <= sorted_points[1][0]:
                        A = sorted_points[0]
                        B = sorted_points[1]
                    else:
                        A = sorted_points[1]
                        B = sorted_points[0]
                    if sorted_points[2][0] <= sorted_points[3][0]:
                        C = sorted_points[2]
                        D = sorted_points[3]
                    else:
                        C = sorted_points[3]
                        D = sorted_points[2]
                    AB = int(np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2))
                    CD = int(np.sqrt((C[0]-D[0])**2 + (C[1]-D[1])**2))
                    AC = int(np.sqrt((A[0]-C[0])**2 + (A[1]-C[1])**2))
                    AD = int(np.sqrt((A[0]-D[0])**2 + (A[1]-D[1])**2))

                    angle_AB_CD = np.abs(np.arctan2(B[1]-A[1], B[0]-A[0]) - np.arctan2(D[1]-C[1], D[0]-C[0]))
                    angle_AC_BD = np.abs(np.arctan2(C[1]-A[1], C[0]-A[0]) - np.arctan2(D[1]-B[1], D[0]-B[0]))
                    
                    if AB - AC > self.rectangle_thresh and CD - AD > self.rectangle_thresh:
                        shape_type = "矩形"
                    elif min(angle_AB_CD, angle_AC_BD) < np.pi/18 and CD > AB:
                        shape_type = "上梯形"
                    elif min(angle_AB_CD, angle_AC_BD) < np.pi/18 and CD < AB:
                        shape_type = "下梯形"
                    elif AB - AC <= self.square_thresh and CD - AD <= self.square_thresh:
                        shape_type = "正方形"
                    else:
                        shape_type = "其他四边形"
                    print(f"检测到形状: {shape_type}, AB={AB:.1f}, CD={CD:.1f}, AC={AC:.1f}, AD={AD:.1f}")

                    hollow, color = self.detect_color(img_blur, center_x_mu, center_y_mu, x, y)
                    return shape_type, hollow, color

        cv2.waitKey(1)
        return None, None, None

    def detect_color(self, img, center_x, center_y, x, y):
        hollow = None
        color = None
        
        ROI_img = img_two[center_y-self.ROI_range:center_y+self.ROI_range, center_x-self.ROI_range:center_x+self.ROI_range]
        cv2.imshow("ROI", ROI_img)
        
        white_count = cv2.countNonZero(ROI_img)  
        black_count = ROI_img.size - white_count
        color_counts = { "black": black_count, "white": white_count}
        max_color = max(color_counts, key=color_counts.get)

        ROI_img_color=img[center_y-self.ROI_range:center_y+self.ROI_range, center_x-self.ROI_range:center_x+self.ROI_range]

        red_mask = cv2.inRange(ROI_img_color, self.red_low, self.red_up)
        red_mask = cv2.erode(red_mask, None, iterations=self.red_iter)
        red_mask = cv2.dilate(red_mask, None, iterations=self.red_iter)
        red_count = cv2.countNonZero(red_mask)

        blue_mask = cv2.inRange(ROI_img_color, self.blue_low, self.blue_up)
        blue_mask = cv2.erode(blue_mask, None, iterations=self.blue_iter)
        blue_mask = cv2.dilate(blue_mask, None, iterations=self.blue_iter)
        blue_count = cv2.countNonZero(blue_mask)

        edge_color_counts = {"red": red_count, "blue": blue_count}

        max_edge_color = max(edge_color_counts, key=edge_color_counts.get)
        print(f"边缘检测到颜色: {max_edge_color}")



        if max_color == "black":
            hollow = 2
            print("空心")
            if max_edge_color == "red":
                color = 1
            elif max_edge_color == "blue":
                color = 2
        else:
            hollow = 1
            print("实心")
            if max_edge_color == "red":
                color = 1
            elif max_edge_color == "blue":
                color = 2

        return hollow, color


def capture_frame(self):
    
    if not self.cap.isOpened():
        print("无法打开摄像头")
        exit()
    ret,frame=self.cap.read()
   
    if ret:
        
        cv2.imwrite("captured_frame"+str(self.frame_count)+".jpg", frame)  # 保存为jpg格式
        self.frame_count += 1
        print("图像已保存为 captured_frame+x.jpg")
    self.cap.release()
    cv2.destroyAllWindows()
    return ret,frame
if __name__ == "__main__":
    detector = Detect_object()
    img = cv2.imread("D:/table/berryPI/photo/29.jpg")  # 使用正斜杠路径更安全

    results = []
    i = 0
    while i < 33:
        # 添加窗口显示和退出检测
        cv2.imshow("Detection Preview", img)
        if cv2.waitKey(1) == 27:  # ESC退出
            break
        
        # 执行检测
        shape1, hollow, color = detector.detect_shape_color(img)
        
        # 收集有效结果
        if None not in (shape1, hollow, color):
            results.append((shape1, hollow, color))
            print(f"第{i+1}次检测 - 形状: {shape1}, 空心: {hollow}, 颜色: {color}")
        
        i += 1
        time.sleep(0.1)  # 调整到循环末尾

    cv2.destroyAllWindows()

    if results:
        shapes, hollows, colors = zip(*results)
        most_common_shape = Counter(shapes).most_common(1)[0][0]
        most_common_hollow = Counter(hollows).most_common(1)[0][0]
        most_common_color = Counter(colors).most_common(1)[0][0]

        if most_common_shape == "矩形":
            if most_common_hollow == 1:
                Shape = 1
            elif most_common_hollow == 2:
                Shape = 2
        elif most_common_shape == "上梯形":
            if most_common_hollow == 1:
                Shape = 3
            elif most_common_hollow == 2:
                Shape = 4
        elif most_common_shape == "下梯形":
            if most_common_hollow == 1:
                Shape = 5
            elif most_common_hollow == 2:
                Shape = 6
        elif most_common_shape == "正方形":
            if most_common_hollow == 1:
                Shape = 7
            elif most_common_hollow == 2:
                Shape = 8
        else:
            Shape = None

        print(f"最终的形状: {most_common_shape}, 最终的空心: {most_common_hollow}, 最终的颜色: {most_common_color}")
        print(f"最终确定的形状代号: {Shape}")
    else:
        print("没有检测到有效的形状和颜色")
