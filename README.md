# raspi-car
a small step to figure out the problem  
and it is my first time to push my code on the platform  
现在要解决的问题：  
1、树莓派通信问题，pyserial 感觉不是很正常，只有在下位机启动的时候才能传输的了信息  
2、上位机处理opencv的阈值，现在还没有解决四种颜色的识别，现在的话识别方式是否需要改进？  
我之前用的是分别处理中心区域的颜色和边界矩形框一角颜色，Q是对比中心黑白面积，现在看来Q的会好点
3、路径算法怎么实现？起点出发 ahead，right，中途识别到色块停止（使用灰度传感器），然后左右扫，可以尝试加入多次判断，然后继续ahead，left，left，识别，ahead，left，left，重复识别，right，right，终点
