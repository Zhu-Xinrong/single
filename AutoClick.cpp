#define _CRT_SECURE_NO_WARNINGS
#include<stdio.h>
#include<Windows.h>

int main() {
	while (1) {
		int count, sleep, key;
		printf("输入点击次数：");
		scanf("%d", &count);
		printf("输入间隔时间（以毫秒为单位）：");
		scanf("%d", &sleep);
		printf("按下左键（0）、右键（1）还是中键（2）：");
		scanf("%d", &key);
		if (count < 1 or sleep < 1) {
			printf("数值不可为负数或为0");
		}
		else {
			printf("请在倒计时结束之前将鼠标移动到指定位置： ");
			for (int i = 5; i > 0; i--) {
				printf("\b%d", i);
				Sleep(1000);
			}
			for (int i = 0; i < count; i++) {
				switch (key) {
				case 0: {
					mouse_event(MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
					break;
				}
				case 1: {
					mouse_event(MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
					break;
				}
				case 2: {
					mouse_event(MOUSEEVENTF_MIDDLEDOWN | MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0);
				}
				}
				Sleep(sleep);
			}
		}
		printf("\n");
	}
}