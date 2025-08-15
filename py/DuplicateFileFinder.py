'''
    Copyright (c) Kendall 2025. All rights reserved.
    Last Updated: 2025/8/1
'''
import os, hashlib, time
from collections import defaultdict
from tqdm import tqdm

class NoDuplicateFiles(Exception): pass

def compute_hash(file_path):
    '''计算文件的MD5哈希值，分块读取以处理大文件'''
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)  # 8KB块
                if not chunk: break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, PermissionError) as e:
        print(f'\n无法读取文件 {file_path}：{str(e)}。')
        return None

def find_duplicate_files(root_dirs):
    '''查找并返回重复文件的列表'''
    size_groups = defaultdict(list)
    start = time.time()
    file_count = 0
    valid_files = 0
    
    print('扫描文件结构中……')
    # 获取需要遍历的文件总数
    total_files = 0
    for root_dir in root_dirs:
        for _, _, filenames in os.walk(root_dir): total_files += len(filenames)

    # 遍历所有文件，按大小分组
    for root_dir in root_dirs:
        for dirpath, _, filenames in os.walk(root_dir): total_files += len(filenames)
    
    file_progress = tqdm(total=total_files, desc='扫描文件', unit='个文件')
    
    # 遍历所有文件，按大小分组
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_count += 1
            abs_path = os.path.abspath(os.path.join(dirpath, filename))
            
            # 更新进度条
            file_progress.update(1)
                
            try:
                size = os.path.getsize(abs_path)
                size_groups[size].append(abs_path)
                valid_files += 1
            except OSError as e: file_progress.write(f'跳过无法访问的文件 {abs_path}：{str(e)}。')
    
    # 关闭进度条
    file_progress.close()
    
    scan_time = time.time() - start
    print(f'\n扫描完成！耗时 {scan_time:.2f} 秒。')
    print(f'共扫描 {file_count} 个文件，其中 {valid_files} 个有效文件。')
    print(f'找到 {len(size_groups)} 个相同大小的文件组。')
    
    duplicates = []
    start_hash = time.time()
    
    # 计算需要处理哈希的文件总数
    total_hashes = sum(len(files) for files in size_groups.values() if len(files) >= 2)
    
    if total_hashes == 0:
        print('\n没有需要计算哈希的文件。')
        return duplicates
    
    print('\n计算文件哈希值……')
    # 创建哈希计算进度条
    hash_progress = tqdm(total=total_hashes, desc='计算哈希', unit='个文件')
    
    # 检查每个大小组中的哈希重复
    for size, files in size_groups.items():
        if len(files) < 2: continue  # 无重复可能
        
        hash_map = defaultdict(list)
        for file_path in files:
            file_hash = compute_hash(file_path)
            if file_hash is not None: hash_map[file_hash].append(file_path)
            
            # 更新哈希进度条
            hash_progress.update(1)
        
        # 收集哈希重复的组
        for paths in hash_map.values():
            if len(paths) >= 2: duplicates.append(paths)
    
    # 关闭进度条
    hash_progress.close()
    
    hash_time = time.time() - start_hash
    print(f'\n哈希计算完成！耗时 {hash_time:.2f} 秒。')
    print(f'找到 {len(duplicates)} 组重复文件。')
    
    return duplicates

def export_to_markdown(duplicate_groups, output_file, scanned_dirs):
    '''将重复文件组导出为 Markdown 文件'''
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# 重复文件报告\n\n')
        
        f.write('## 扫描文件夹\n')
        for i, path in enumerate(scanned_dirs, 1): f.write(f'{i}. `{path}`\n')
        f.write('\n')

        try:
            if not duplicate_groups:
                raise NoDuplicateFiles('未找到重复文件。')
        
            total_duplicates = sum(len(group) for group in duplicate_groups)
            unique_duplicates = total_duplicates - len(duplicate_groups)
            f.write(f'## 报告摘要\n')
            f.write(f'- **重复文件组数**: {len(duplicate_groups)}\n')
            f.write(f'- **重复文件总数**: {total_duplicates}\n')
            f.write(f'- **可释放空间**: {unique_duplicates} 个文件的空间\n\n')
            
            f.write('## 重复文件详情\n\n')
            for index, group in enumerate(duplicate_groups, 1):
                f.write(f'### 第{index}组 （{len(group)}个相同文件）\n')
                for path in group: f.write(f'- `{path}`\n')
                f.write('\n')
        except NoDuplicateFiles:
            f.write('## 未找到重复文件。\n')
        finally:
            f.write('\n---\n')
            f.write('> 报告生成时间：' + time.strftime('%Y-%m-%d %H:%M:%S') + '。  ')
            f.write('\n> 工具：Duplicate File Finder by [Kendall](https://github.com/Zhu-Xinrong/)。')

try:
    root_dirs = []
    print('添加要扫描的文件夹（输入空行结束添加）：')
    i = 1
    while True:
        dir_path = input(f'添加第{i}个文件夹：').strip()
        if not dir_path: break
        if os.path.isdir(dir_path):
            root_dirs.append(dir_path)
            i += 1
        else: print(f'错误：路径 {dir_path} 不存在或不是文件夹，请重新输入。')
    
    if not root_dirs:
        print('错误：未添加任何有效文件夹。')
        exit(1)

    default_output = f'duplicates_report_{time.strftime('%Y%m%d_%H%M%S')}.md'
    output_prompt = f'请输入要保存的 Markdown 文件名（默认: {default_output}）: '
    output_file = input(output_prompt).strip() or default_output
    
    if not output_file.endswith('.md'): output_file += '.md'
    
    print('\n开始扫描……')
    duplicate_groups = find_duplicate_files(root_dirs)
    
    print('\n生成报告中……')
    export_to_markdown(duplicate_groups, output_file, root_dirs)
    
    abs_path = os.path.abspath(output_file)
    print(f'\n扫描完成！结果已导出到: {abs_path}。')
    
    if duplicate_groups:
        total_duplicates = sum(len(group) for group in duplicate_groups)
        unique_duplicates = total_duplicates - len(duplicate_groups)
        print(f'发现 {len(duplicate_groups)} 组重复文件。')
        print(f'共 {total_duplicates} 个文件存在重复。')
        print(f'可释放空间: 删除 {unique_duplicates} 个重复文件可节省空间。')
    else: print('未发现重复文件。')
except KeyboardInterrupt: print('\n操作已取消。')
except Exception as e: print(f'\n发生错误：{e}。')