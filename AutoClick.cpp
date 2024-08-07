#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<Windows.h>
#define MouseEvent mouse_event
int main(){
    while(true){
        int click{};
		DWORD sleepTime{};
		char key[2]={};
        printf("输入点击次数: ");
        while(true){
            scanf("%d",&click);
            if(click>0){
				break;
            }
			printf("数据必须大于 0, 请重新输入: ");
        }
        printf("输入间隔时间 (单位: 毫秒): ");
		while(true){
			scanf("%lu",&sleepTime);
            if(sleepTime>0){
				break;
            }
			printf("数据必须大于 0, 请重新输入: ");
		}
        printf("按下左键 (0), 右键 (1) 还是中键 (2): ");
		while(true){
            scanf("%s",key);
            if((!(key[0]^'0')||!(key[0]^'1')||!(key[0]^'2'))&&!(key[1]^0)){
				break;
            }
            printf("输入错误, 请重新输入: ");
        }
        for(short i{5};i>=0;--i){
            printf("请在 %d 秒内将鼠标移动到指定位置.\r",i);
            if(!i){
                break;
            }
            Sleep(1000ul);
        }
        for(int i{};i<click;++i){
            switch(key[0]){
                case '0':{
                    MouseEvent(MOUSEEVENTF_LEFTDOWN|MOUSEEVENTF_LEFTUP,0,0,0,0);
                    break;
                }
                case '1':{
                    MouseEvent(MOUSEEVENTF_RIGHTDOWN|MOUSEEVENTF_RIGHTUP,0,0,0,0);
                    break;
                }
                case '2':{
                    MouseEvent(MOUSEEVENTF_MIDDLEDOWN|MOUSEEVENTF_MIDDLEUP,0,0,0,0);
                    break;
                }
            }
            Sleep(sleepTime);
        }
        printf("\n");
    }
    return 0;
}