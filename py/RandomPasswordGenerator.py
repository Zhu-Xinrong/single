'''
    Copyright (c) Kendall 2024-2025. All rights reserved.
    Last Updated: 2025/8/4
'''
import random, string, pyperclip, getpass

def generate_password(length=12, include_digits=True, include_uppercase=True, include_lowercase=True, include_special_chars=True, exclude_similar=True):
    # 定义字符集
    char_sets = []
    if include_digits:
        digits = string.digits
        if exclude_similar:
            digits = digits.replace('0', '').replace('1', '')
        char_sets.append(digits)
    if include_uppercase:
        uppercase = string.ascii_uppercase
        if exclude_similar:
            uppercase = uppercase.replace('O', '').replace('I', '')
        char_sets.append(uppercase)
    if include_lowercase:
        lowercase = string.ascii_lowercase
        if exclude_similar:
            lowercase = lowercase.replace('l', '')
        char_sets.append(lowercase)
    if include_special_chars:
        specials = string.punctuation
        if exclude_similar:
            specials = ''.join(c for c in specials if c not in '|!;:,.')
        char_sets.append(specials)
    
    # 检查有效性
    if not char_sets:
        raise ValueError('必须至少选择一种字符类型。')
    
    # 生成基础密码（确保包含每种字符）
    password = []
    all_chars = ''.join(char_sets)
    
    for char_set in char_sets:
        password.append(random.choice(char_set))
    
    # 填充剩余长度
    remaining = length - len(password)
    if remaining > 0:
        password.extend(random.choices(all_chars, k=remaining))
    
    # 打乱并返回
    random.shuffle(password)
    return ''.join(password)

# 用户交互
try:
    length = int(input('密码长度（默认12）: ') or 12)
    if length < 8:
        print('警告：建议长度至少8位。')
        
    include_digits = (input('包含数字？（y/n, 默认 y）：') or 'y').lower() == 'y'
    include_uppercase = (input('包含大写字母？（y/n, 默认 y）：') or 'y').lower() == 'y'
    include_lowercase = (input('包含小写字母？（y/n, 默认 y）：') or 'y').lower() == 'y'
    include_special_chars = (input('包含特殊字符？（y/n, 默认 y）：') or 'y').lower() == 'y'
    exclude_similar = (input('排除易混淆字符？（y/n, 默认 y）：') or 'y').lower() == 'y'
    
    password = generate_password(length, include_digits, include_uppercase, include_lowercase, include_special_chars, exclude_similar)
    
    pyperclip.copy(password)
    getpass.getpass('密码已复制到剪贴板，按回车显示，或使用 Ctrl+C 退出。')
    print(f'生成的密码: {password}。')
except KeyboardInterrupt:
    print('已退出。')
except ValueError as e:
    print(f'错误: {e}。')
except Exception as e:
    print(f'意外错误: {e}。')