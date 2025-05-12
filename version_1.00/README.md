# raspi-car
a small step to figure out the problem  
and it is my first time to push my code on the platform  
现在要解决的问题：  
1、树莓派通信问题，pyserial 感觉不是很正常，只有在下位机启动的时候才能传输的了信息  （留给恺瑞）
2、上位机处理opencv的阈值，现在还没有解决四种颜色的识别，现在的话识别方式是否需要改进？  （算了）
我之前用的是分别处理中心区域的颜色和边界矩形框一角颜色，Q是对比中心黑白面积，现在看来Q的会好点  （已解决）
3、路径算法怎么实现？起点出发 ahead，right，中途识别到色块停止（使用灰度传感器），然后左右扫，可以尝试加入多次判断，然后继续ahead，left，left，识别，ahead，left，left，重复识别，right，right，终点  
4、这个detect_object 是我一开始写的，效果针对某种场合还行，需要调阈值，不然不是很准，这个和我上面说的方法一样，检测中间和边缘，对比判断是否空心，这个thresh 的逻辑在判断图形的时候还算ok  

问题:1.串口需要下位机启动后按复位才能正常识别  可能是串口卡了，暂未解决
2.右电机卡，转弯有点问题    已解决，硬件问题
3，下位机dma可能发送不到串口  解决办法，先使用printf
