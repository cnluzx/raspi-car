import cv2
import numpy as np
import time
from collections import Counter

global frame_count
frame_count = 0
class Detect_object:
    def __init__(self):
        self.if_shape_test = True
        self.if_color_test = True
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.area_min = 10000
        self.rectangle_thresh = 66
        self.square_thresh = 38
        self.canny_threshold1 = 50
        self.canny_threshold2 = 100
        self.roi_x = 5
        self.roi_y = 5
        self.roi_w = 5
        self.roi_h = 5
        self.ROI_range = 50
        self.red_low = (0, 0, 100)
        self.red_up = (50, 50, 255)  # 调阈值
        self.blue_low = (100, 0, 0)
        self.blue_up = (255, 50, 50)
        self.yellow_low = (20, 100, 100)  # 添加黄色阈值
        self.yellow_up = (30, 255, 255)   # 添加黄色阈值
        self.red_iter = 1
        self.blue_iter = 1
        self.yellow_iter = 1  # 添加黄色迭代次数
        self._threold = 70

        self.init_trackbars()

    def init_trackbars(self):
        cv2.namedWindow("Parameters")
        cv2.createTrackbar("Area Min", "Parameters", self.area_min, 50000, self.nothing)
        cv2.createTrackbar("Canny Thresh1", "Parameters", self.canny_threshold1, 200, self.nothing)  # 修正了这里的名称拼写错误
        cv2.createTrackbar("Canny Thresh2", "Parameters", self.canny_threshold2, 200, self.nothing)

    def nothing(self, x):
        pass

    def update_parameters(self):
        self.area_min = cv2.getTrackbarPos("Area Min", "Parameters")
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
            self._threold = 70
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

            #    A
            #   / \
            #  B---C
                if len(approx) == 3:
                    shape_type = "三角形"
                    mu = cv2.moments(cnt)
                    center_x = int(mu["m10"] / mu["m00"]) if mu["m00"] != 0 else 0
                    center_y = int(mu["m01"] / mu["m00"]) if mu["m00"] != 0 else 0
                    print(f"三角形中心: ({center_x}, {center_y})")
                    # 获取三个顶点
                    pts = approx.squeeze()  # 形状应为(3,2)
                    # 方法一：直接按原始顺序访问
                    A = pts[0]  # 第一个顶点 [x0,y0]
                    B = pts[1]  # 第二个顶点 [x1,y1]
                    C = pts[2]  # 第三个顶点 [x2,y2]
                    y_coords = pts[:, 1]    # 所有y坐标
                    sorted_idx = np.argsort(y_coords)
                    top_point = pts[sorted_idx[0]]  # y最小的点
                    bottom_point = pts[sorted_idx[2]] # y最大的点 好像没用到
                    # 判断三角形朝向
                    if y_coords[0] < y_coords[1] and y_coords[0] < y_coords[2]:
                        shape_type = "上三角"  # 有一个顶点明显在上方
                        hollow, color = self.detect_color(img_blur, center_x, center_y, int(top_point[0]), int(top_point[1]))
                    elif y_coords[0] > y_coords[1] and y_coords[0] > y_coords[2]:
                        shape_type = "下三角"  # 有一个顶点明显在下方
                        hollow, color = self.detect_color(img_blur, center_x, center_y, int(bottom_point[0]), int(bottom_point[1]))
                    else:
                        shape_type = "其他三角形"##66666
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    center_x = x + w / 2
                    center_y = y + h / 2
                    mu = cv2.moments(cnt)
                    center_x_mu = int(mu["m10"] / mu["m00"]) if mu["m00"] != 0 else 0
                    center_y_mu = int(mu["m01"] / mu["m00"]) if mu["m00"] != 0 else 0
                    approx = np.array(approx).squeeze()
                    sorted_points = approx[np.argsort(approx[:, 1])]

                    
                    # A —— B
                    # |    |
                    # D —— C

                    if sorted_points[0][0] <= sorted_points[1][0]:
                        A = sorted_points[0]
                        B = sorted_points[1]
                    else:
                        A = sorted_points[1]
                        B = sorted_points[0]
                    if sorted_points[2][0] <= sorted_points[3][0]:
                        D = sorted_points[2]
                        C = sorted_points[3]
                    else:
                        D = sorted_points[3]
                        C = sorted_points[2]
                    print(A,B,C,D)
                    AB = int(np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2))
                    CD = int(np.sqrt((C[0]-D[0])**2 + (C[1]-D[1])**2))
                    AC = int(np.sqrt((A[0]-C[0])**2 + (A[1]-C[1])**2))
                    AD = int(np.sqrt((A[0]-D[0])**2 + (A[1]-D[1])**2))

                    angle_AB_CD = np.abs(np.arctan2(B[1]-A[1], B[0]-A[0]) - np.arctan2(C[1]-D[1], C[0]-D[0]))
                    angle_AB_AD = np.abs(np.arctan2(B[1]-A[1], B[0]-A[0]) - np.arctan2(D[1]-A[1], D[0]-A[0]))
                    print(angle_AB_AD*180/np.pi,angle_AB_CD*180/np.pi)
                    ###矩形和正方形各成检测对，梯形检测使用角度判断，精度很高
                    if AB - AD > self.rectangle_thresh and CD - AD > self.rectangle_thresh:
                        shape_type = "矩形"
                    elif angle_AB_CD < np.pi/18 and angle_AB_AD >np.pi/1.8:
                        shape_type = "上梯形"
                    elif angle_AB_CD < np.pi/18 and angle_AB_AD < np.pi/2.25 :
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

        # 添加黄色检测
        yellow_mask = cv2.inRange(ROI_img_color, self.yellow_low, self.yellow_up)
        yellow_mask = cv2.erode(yellow_mask, None, iterations=self.yellow_iter)
        yellow_mask = cv2.dilate(yellow_mask, None, iterations=self.yellow_iter)
        yellow_count = cv2.countNonZero(yellow_mask)

        edge_color_counts = {"red": red_count, "blue": blue_count, "yellow": yellow_count}

        max_edge_color = max(edge_color_counts, key=edge_color_counts.get)
        print(f"边缘检测到颜色: {max_edge_color}")

        if max_color == "black":
            hollow = 2
            print("空心")
            if max_edge_color == "red":
                color = 1
            elif max_edge_color == "blue":
                color = 2
            elif max_edge_color == "yellow":
                color = 3
        else:
            hollow = 1
            print("实心")
            if max_edge_color == "red":
                color = 1
            elif max_edge_color == "blue":
                color = 2
            elif max_edge_color == "yellow":
                color = 3

        return hollow, color


# def capture_frame():
    
#     if not detector.cap.isOpened():
#         print("无法打开摄像头")
#         exit()
#     ret,frame=detector.cap.read()
   
#     if ret:
        
#         cv2.imwrite("captured_frame.jpg", frame)  # 保存为jpg格式
#     detector.cap.release()
#     cv2.destroyAllWindows()
#     return ret,frame

def main(img):
    most_common_shape=None
    most_common_hollow=None
    most_common_color=None
    results = []
    i = 0
    while i < 37:
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
        return True,most_common_shape,most_common_hollow,most_common_color
    else:
        print("没有检测到有效的形状和颜色")
        return False,None,None,None
    

if __name__ == '__main__':
    detector = Detect_object()
    img = cv2.imread("frame.jpg")
    main(img)
