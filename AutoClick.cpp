#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<windows.h>
class CAutoClick{
    private:
        char button;
        int click,counter;
        DWORD sleepTime;
    protected:
        auto clickBase(){
            switch(button){
                case 'L':{
                    mouse_event(MOUSEEVENTF_LEFTDOWN|MOUSEEVENTF_LEFTUP,0,0,0,0);
                    break;
                }case 'M':{
                    mouse_event(MOUSEEVENTF_MIDDLEDOWN|MOUSEEVENTF_MIDDLEUP,0,0,0,0);
                    break;
                }case 'R':{
                    mouse_event(MOUSEEVENTF_RIGHTDOWN|MOUSEEVENTF_RIGHTUP,0,0,0,0);
                    break;
                }
            }
        }
    public:
        CAutoClick():
            button{},click{},counter{1},sleepTime{}{}
        ~CAutoClick(){}
        auto set(char button,int click,DWORD sleepTime){
            this->button=button;
            this->click=click;
            this->sleepTime=sleepTime;
        }
        auto run(){
            for(;counter<=click;++counter){
                clickBase();
                if(counter==click){
                    break;
                }
                Sleep(sleepTime);
            }
        }
};
auto main()->int{
    CAutoClick c;
    int click{};
	DWORD sleepTime{};
	char button[2]{};
    while(true){
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
			printf("输入数据必须大于 0, 请重新输入: ");
		}
        printf("按下左键 (L), 中键 (M), 还是右键 (R): ");
		while(true){
            scanf("%s",button);
            if(((button[0]=='L')||(button[0]=='M')||(button[0]=='R'))&&(button[1]==0)){
				break;
            }
            printf("输入错误, 请重新输入: ");
        }
        for(short i{5};i>=0;--i){
            printf("请在 %d 秒内将鼠标移动到指定位置.\r",i);
            if(!i){
                break;
            }
            Sleep(1000);
        }
        puts("\n正在应用配置.");
        c.set(button[0],click,sleepTime);
        puts("开始执行.");
        c.run();
        puts("执行完毕.\n");
    }
    return 0;
}