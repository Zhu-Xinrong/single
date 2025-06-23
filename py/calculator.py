'''
    Copyright (c) Kendall 2023 - 2024. All rights reserved.
    LastUpdate  03/30/2024 Sat.
'''
import decimal

# 定义函数getFormula，用于获取表达式中的数字和运算符
def getFormula(formula = ''):
    # 定义运算符列表
    operators = ['+', '-', '*', '/', '^', 'r', '%', '//', '!']
    # 遍历运算符列表，查找表达式中的运算符
    for i in operators:
        if formula.find(i) != -1:
            operator = i
    # 获取表达式中的数字，并将其赋值给num1和num2
    num1 = formula[:formula.find(operator)]
    num2 = formula[formula.find(operator)+1:]
    return num1, operator, num2

# 定义函数calculate，用于计算表达式的值
def calculate(num1, operator, num2):
    # 将数字转换为decimal类型
    num1 = decimal.Decimal(num1)
    if num2 != '':
        num2 = decimal.Decimal(num2)
    # 根据运算符计算表达式的值
    if operator == '+':
        return num1 + num2
    elif operator == '-':  
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        return num1 / num2
    elif operator == '^':
        return pow(num1, num2)
    elif operator == 'r':
        temp = pow(num2, 1 / num1)
        if int(temp) == temp:
            temp = int(temp)
        return temp
    elif operator == '!':
        ruselt = 1
        for i in range(2, int(num1) + 1):
            ruselt *= i
        return ruselt
    elif operator == '%':
        return num1 % num2
    elif operator == '//':
        return num1 // num2
    
# 定义函数binary，用于将数字转换为指定进制的数字
def binary(rawNumber = '', targetBinary = 2):
    # 根据rawNumber的第二个字符，判断rawNumber的进制
    if rawNumber[1] == 'b':
        rawBinary = 2
    elif rawNumber[1] == 'o':
        rawBinary = 8
    elif rawNumber[1] == 'x':
        rawBinary = 16
    else:
        rawBinary = 10
    # 将rawNumber转换为int类型
    temp = int(rawNumber, rawBinary)
    # 根据targetBinary的值，将temp转换为指定进制的数字
    if targetBinary == 2:
        ruselt = bin(temp)
    elif targetBinary == 8:
        ruselt = oct(temp)
    elif targetBinary == 16:
        ruselt = hex(temp)
    else:
        ruselt = temp
    return ruselt

if __name__ == '__main__':
    memory = 0
    last_result = 0
    # 循环输入表达式，计算表达式的值
    while True:
        formula = input('输入一个算式或功能，或输入 exit 退出：')
        # 如果输入的是binary，则调用binary函数，将数字转换为指定进制的数字
        if formula == 'binary':
            rawNumber = input('源数字：')
            targetBinary = int(input('目标进制：'))
            print(binary(rawNumber, targetBinary))
        elif formula == 'color':
            mode = int(input('将 RGB 转为16进制（0）还是将16进制转为 RGB（1）：'))
            colors = ['红', '绿', '蓝']
            rgb = []
            if mode == 0:
                for i in range(3):
                    rgb.append(int(input(colors[i] + '的数值：')))
                print('#', end = '')
                for i in range(3):
                    temp = hex(rgb[i])[2:]
                    if len(temp) == 1:
                        temp = '0' + temp
                    print(temp, end = '')
                print('\n')
            elif mode == 1:
                hex_ = input('输入16进制数：')[1:]
                for i in range(0, 6, 2):
                    rgb.append(hex_[i:i+2])
                for i in range(3):
                    print(colors[i] + '的值为' + str(int('0x' + rgb[i], 16)))
        elif formula == 'exit':
            break
        elif formula == 'MR':
            print(memory)
        elif formula == 'MC':
            memory = 0
        elif formula == 'M+':
            memory += last_result
        elif formula == 'M-':
            memory -= last_result
        else:
            # 调用getFormula函数，获取表达式中的数字和运算符
            num1, operator, num2 = getFormula(formula)
            # 如果运算符是//，则去掉num2的第一个字符
            if operator == '//':
                num2 = num2[1:]
            # 调用calculate函数，计算表达式的值
            result = calculate(num1, operator, num2)
            print(num1 + operator + num2 + "=" + str(result))
            last_result = result