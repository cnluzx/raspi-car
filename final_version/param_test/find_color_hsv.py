import cv2
import numpy as np
import os

def nothing(x):
    pass

class ColorDebugger:
    def __init__(self, image_dir=None):
        self.image_dir = image_dir
        self.current_image_index = 0
        self.images = []
        
        # 创建窗口和滑动条
        self.window_name = 'Color Debugger'  # 处理后的图片窗口
        self.original_window_name = 'Original Image'  # 原图窗口
        self.panel_name = 'Control Panel'  # 控制面板窗口
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(self.window_name, 600, 400)
        
        cv2.namedWindow(self.original_window_name, cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(self.original_window_name, 600, 400)
        
        cv2.namedWindow(self.panel_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.panel_name, 500, 300)
        
        # 创建滑动条
        cv2.createTrackbar('H Min', self.panel_name, 0, 180, nothing)
        cv2.createTrackbar('S Min', self.panel_name, 0, 255, nothing)
        cv2.createTrackbar('V Min', self.panel_name, 0, 255, nothing)
        cv2.createTrackbar('H Max', self.panel_name, 180, 180, nothing)
        cv2.createTrackbar('S Max', self.panel_name, 255, 255, nothing)
        cv2.createTrackbar('V Max', self.panel_name, 255, 255, nothing)
        cv2.createTrackbar('Erode Iter', self.panel_name, 1, 10, nothing)
        cv2.createTrackbar('Dilate Iter', self.panel_name, 1, 10, nothing)
        
        # 如果指定了图像目录，则加载图像
        if self.image_dir:
            self.load_images()
    
    def load_images(self):
        """加载指定目录中的所有图像"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        try:
            self.images = [f for f in os.listdir(self.image_dir) 
                          if os.path.isfile(os.path.join(self.image_dir, f)) 
                          and os.path.splitext(f)[1].lower() in valid_extensions]
            if not self.images:
                print(f"错误：目录 {self.image_dir} 中没有找到图像文件")
        except Exception as e:
            print(f"加载图像时出错: {e}")
    
    def process_image(self, image):
        """使用当前滑动条参数处理图像"""
        # 获取滑动条值
        h_min = cv2.getTrackbarPos('H Min', self.panel_name)
        s_min = cv2.getTrackbarPos('S Min', self.panel_name)
        v_min = cv2.getTrackbarPos('V Min', self.panel_name)
        h_max = cv2.getTrackbarPos('H Max', self.panel_name)
        s_max = cv2.getTrackbarPos('S Max', self.panel_name)
        v_max = cv2.getTrackbarPos('V Max', self.panel_name)
        erode_iter = cv2.getTrackbarPos('Erode Iter', self.panel_name)
        dilate_iter = cv2.getTrackbarPos('Dilate Iter', self.panel_name)
        
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 创建颜色掩码
        # 特殊处理红色（在HSV中不连续）
        if h_min <= h_max:
            mask = cv2.inRange(hsv, np.array([h_min, s_min, v_min]), np.array([h_max, s_max, v_max]))
        else:
            # 红色情况：需要两个范围
            mask1 = cv2.inRange(hsv, np.array([h_min, s_min, v_min]), np.array([180, s_max, v_max]))
            mask2 = cv2.inRange(hsv, np.array([0, s_min, v_min]), np.array([h_max, s_max, v_max]))
            mask = cv2.bitwise_or(mask1, mask2)
        
        # 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        processed_mask = cv2.erode(mask, kernel, iterations=erode_iter)
        processed_mask = cv2.dilate(processed_mask, kernel, iterations=dilate_iter)
        
        return processed_mask
    
    def for_cap(self):
        """使用摄像头进行实时调试"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头")
            return
            
        cap.set(cv2.CAP_PROP_FPS, 15)
        
        print("提示:")
        print("按 's' 保存当前参数")
        print("按 'q' 退出")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法获取图像")
                break
                
            # 处理图像
            processed_mask = self.process_image(frame)
            
            # 获取当前滑动条值用于显示
            h_min = cv2.getTrackbarPos('H Min', self.panel_name)
            s_min = cv2.getTrackbarPos('S Min', self.panel_name)
            v_min = cv2.getTrackbarPos('V Min', self.panel_name)
            h_max = cv2.getTrackbarPos('H Max', self.panel_name)
            s_max = cv2.getTrackbarPos('S Max', self.panel_name)
            v_max = cv2.getTrackbarPos('V Max', self.panel_name)
            erode_iter = cv2.getTrackbarPos('Erode Iter', self.panel_name)
            dilate_iter = cv2.getTrackbarPos('Dilate Iter', self.panel_name)
            
            # 显示原图和处理后的图片
            cv2.imshow(self.original_window_name, frame)
            cv2.imshow(self.window_name, processed_mask)
            
            # 显示当前参数
            params_text = f"H: {h_min}-{h_max}, S: {s_min}-{s_max}, V: {v_min}-{v_max}"
            params_text += f" | Erode: {erode_iter}, Dilate: {dilate_iter}"
            cv2.putText(frame, params_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_parameters()
        
        cap.release()
        cv2.destroyAllWindows()

    def for_pic(self):
        """使用图像文件夹进行调试"""
        if not self.images:
            print("没有图像可处理")
            return
            
        current_image_index = 0
        
        print("提示:")
        print("按 'n' 下一张图像")
        print("按 'p' 上一张图像")
        print("按 's' 保存当前参数")
        print("按 'q' 退出")
        
        while True:
            # 读取当前图像
            img_path = os.path.join(self.image_dir, self.images[current_image_index])
            try:
                img = cv2.imread(img_path)
                if img is None:
                    print(f"无法读取图像: {img_path}")
                    current_image_index = (current_image_index + 1) % len(self.images)
                    continue
            except Exception as e:
                print(f"读取图像时出错: {e}")
                current_image_index = (current_image_index + 1) % len(self.images)
                continue
            
            # 获取当前滑动条值
            h_min = cv2.getTrackbarPos('H Min', self.panel_name)
            s_min = cv2.getTrackbarPos('S Min', self.panel_name)
            v_min = cv2.getTrackbarPos('V Min', self.panel_name)
            h_max = cv2.getTrackbarPos('H Max', self.panel_name)
            s_max = cv2.getTrackbarPos('S Max', self.panel_name)
            v_max = cv2.getTrackbarPos('V Max', self.panel_name)
            erode_iter = cv2.getTrackbarPos('Erode Iter', self.panel_name)
            dilate_iter = cv2.getTrackbarPos('Dilate Iter', self.panel_name)
            
            # 处理图像
            processed_mask = self.process_image(img)
            
            # 显示原图和处理后的图片
            cv2.imshow(self.original_window_name, img)
            cv2.imshow(self.window_name, processed_mask)
            
            # 显示当前图像信息和参数
            img_info = f"Image: {current_image_index+1}/{len(self.images)}"
            cv2.putText(img, img_info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            params_text = f"H: {h_min}-{h_max}, S: {s_min}-{s_max}, V: {v_min}-{v_max}"
            params_text += f" | Erode: {erode_iter}, Dilate: {dilate_iter}"
            cv2.putText(img, params_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 按键处理
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):  # 下一张
                current_image_index = (current_image_index + 1) % len(self.images)
            elif key == ord('p'):  # 上一张
                current_image_index = (current_image_index - 1) % len(self.images)
            elif key == ord('s'):  # 保存参数
                self.save_parameters()
            """使用图像文件夹进行调试"""
            if not self.images:
                print("没有图像可处理")
                return
                
            current_image_index = 0
            
            print("提示:")
            print("按 'n' 下一张图像")
            print("按 'p' 上一张图像")
            print("按 's' 保存当前参数")
            print("按 'q' 退出")
            
            while True:
                # 读取当前图像
                img_path = os.path.join(self.image_dir, self.images[current_image_index])
                try:
                    img = cv2.imread(img_path)
                    if img is None:
                        print(f"无法读取图像: {img_path}")
                        current_image_index = (current_image_index + 1) % len(self.images)
                        continue
                except Exception as e:
                    print(f"读取图像时出错: {e}")
                    current_image_index = (current_image_index + 1) % len(self.images)
                    continue
                
                # 处理图像
                processed_mask = self.process_image(img)
                
                # 显示原图和处理后的图片
                cv2.imshow(self.original_window_name, img)
                cv2.imshow(self.window_name, processed_mask)
                
                # 显示当前图像信息和参数
                img_info = f"Image: {current_image_index+1}/{len(self.images)}"
                cv2.putText(img, img_info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                params_text = f"H: {h_min}-{h_max}, S: {s_min}-{s_max}, V: {v_min}-{v_max}"
                params_text += f" | Erode: {erode_iter}, Dilate: {dilate_iter}"
                cv2.putText(img, params_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 按键处理
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('n'):  # 下一张
                    current_image_index = (current_image_index + 1) % len(self.images)
                elif key == ord('p'):  # 上一张
                    current_image_index = (current_image_index - 1) % len(self.images)
                elif key == ord('s'):  # 保存参数
                    self.save_parameters()
    
    def save_parameters(self):
        """保存当前参数到文件"""
        try:
            color_type = input("请输入当前颜色名称: ")
            if not color_type:
                color_type = "unknown"
                
            with open("color_ret.txt", 'a') as f:
                f.write(f"Color Name: {color_type}\n")
                f.write(f"Min HSV: {cv2.getTrackbarPos('H Min', self.panel_name)},{cv2.getTrackbarPos('S Min', self.panel_name)},{cv2.getTrackbarPos('V Min', self.panel_name)}\n")
                f.write(f"Max HSV: {cv2.getTrackbarPos('H Max', self.panel_name)},{cv2.getTrackbarPos('S Max', self.panel_name)},{cv2.getTrackbarPos('V Max', self.panel_name)}\n")
                f.write(f"Erode Iter: {cv2.getTrackbarPos('Erode Iter', self.panel_name)}\n")
                f.write(f"Dilate Iter: {cv2.getTrackbarPos('Dilate Iter', self.panel_name)}\n")
                f.write("-" * 50 + "\n")
                
            print(f"参数已保存为: {color_type}")
        except Exception as e:
            print(f"保存参数时出错: {e}")

if __name__ == "__main__":
    # 指定图像目录或留空以使用摄像头
    debugger = ColorDebugger(r"D:\table\new (1)\test_photo")
    
    # 选择模式：0 为摄像头模式，1 为图像文件夹模式
    mode = "0"
    #input("选择模式 (0: 摄像头, 1: 图像文件夹): ")
    if mode == '0':
        debugger.for_cap()
    elif mode == '1':
        debugger.for_pic()
    else:
        print("无效的选择")