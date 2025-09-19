#!/usr/bin/env python3
"""
Markdown文件清理工具

该模块提供了删除Markdown文件中包含指定关键字的行的功能。
支持多种匹配模式，包括精确匹配、部分匹配和正则表达式匹配。

作者: AI Assistant
版本: 1.0.0
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import List, Optional, Union


class MarkdownCleaner:
    """Markdown文件清理器类"""
    
    def __init__(self, keywords: Optional[List[str]] = None, 
                 mode: str = 'contains', 
                 case_sensitive: bool = False,
                 backup: bool = True):
        """
        初始化Markdown清理器
        
        Args:
            keywords: 要匹配的关键字列表
            mode: 匹配模式 ('exact', 'contains', 'regex')
            case_sensitive: 是否区分大小写
            backup: 是否创建备份文件
        """
        self.keywords = keywords or []
        self.mode = mode
        self.case_sensitive = case_sensitive
        self.backup = backup
        
        # 设置日志
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _match_line(self, line: str) -> bool:
        """
        检查行是否匹配关键字
        
        Args:
            line: 要检查的行内容
            
        Returns:
            如果行匹配关键字则返回True
        """
        if not self.keywords:
            return False
            
        line_to_check = line if self.case_sensitive else line.lower()
        
        for keyword in self.keywords:
            keyword_to_check = keyword if self.case_sensitive else keyword.lower()
            
            if self.mode == 'exact':
                if line_to_check.strip() == keyword_to_check.strip():
                    return True
            elif self.mode == 'contains':
                if keyword_to_check in line_to_check:
                    return True
            elif self.mode == 'regex':
                try:
                    flags = 0 if self.case_sensitive else re.IGNORECASE
                    if re.search(keyword_to_check, line_to_check, flags):
                        return True
                except re.error as e:
                    self.logger.warning(f"正则表达式错误: {keyword_to_check}, {e}")
                    
        return False
    
    def _create_backup(self, file_path: Path) -> Path:
        """
        创建文件备份
        
        Args:
            file_path: 原文件路径
            
        Returns:
            备份文件路径
        """
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
        backup_counter = 1
        
        # 如果备份文件已存在，添加数字后缀
        while backup_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup{backup_counter}")
            backup_counter += 1
            
        return backup_path
    
    def clean_file(self, file_path: Union[str, Path]) -> dict:
        """
        清理Markdown文件
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            包含操作结果的字典
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        if file_path.suffix.lower() not in ['.md', '.markdown']:
            self.logger.warning(f"文件可能不是Markdown文件: {file_path}")
        
        # 读取原文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(file_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
        
        # 创建备份
        backup_path = None
        if self.backup:
            backup_path = self._create_backup(file_path)
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.logger.info(f"已创建备份文件: {backup_path}")
        
        # 过滤行
        original_count = len(lines)
        filtered_lines = []
        removed_lines = []
        
        for line_num, line in enumerate(lines, 1):
            if self._match_line(line):
                removed_lines.append({
                    'line_number': line_num,
                    'content': line.rstrip()
                })
                self.logger.info(f"删除第{line_num}行: {line.rstrip()}")
            else:
                filtered_lines.append(line)
        
        # 写入清理后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(filtered_lines)
        
        result = {
            'file_path': str(file_path),
            'backup_path': str(backup_path) if backup_path else None,
            'original_lines': original_count,
            'remaining_lines': len(filtered_lines),
            'removed_lines': len(removed_lines),
            'removed_content': removed_lines
        }
        
        self.logger.info(f"清理完成: 原{original_count}行，删除{len(removed_lines)}行，剩余{len(filtered_lines)}行")
        
        return result
    
    def add_keyword(self, keyword: str) -> None:
        """添加关键字"""
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            self.logger.info(f"已添加关键字: {keyword}")
    
    def remove_keyword(self, keyword: str) -> None:
        """移除关键字"""
        if keyword in self.keywords:
            self.keywords.remove(keyword)
            self.logger.info(f"已移除关键字: {keyword}")
    
    def list_keywords(self) -> List[str]:
        """获取当前关键字列表"""
        return self.keywords.copy()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Markdown文件清理工具 - 删除包含指定关键字的行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python markdown_cleaner.py -k "微信公众号" file.md
  python markdown_cleaner.py -k "广告" -k "推广" --mode exact file.md
  python markdown_cleaner.py --keywords-file keywords.txt file.md
  python markdown_cleaner.py -k ".*关注.*" --mode regex file.md
        """
    )
    
    parser.add_argument('file', help='要处理的Markdown文件路径')
    parser.add_argument('-k', '--keyword', action='append', 
                       help='要匹配的关键字（可多次使用）')
    parser.add_argument('--keywords-file', 
                       help='包含关键字的文件路径（每行一个关键字）')
    parser.add_argument('-m', '--mode', choices=['exact', 'contains', 'regex'],
                       default='contains', help='匹配模式（默认: contains）')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                       help='区分大小写（默认不区分）')
    parser.add_argument('--no-backup', action='store_true',
                       help='不创建备份文件')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细信息')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 收集关键字
    keywords = []
    if args.keyword:
        keywords.extend(args.keyword)
    
    if args.keywords_file:
        try:
            with open(args.keywords_file, 'r', encoding='utf-8') as f:
                keywords.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"错误: 关键字文件不存在: {args.keywords_file}")
            sys.exit(1)
    
    if not keywords:
        print("错误: 必须提供至少一个关键字")
        sys.exit(1)
    
    # 创建清理器并执行
    try:
        cleaner = MarkdownCleaner(
            keywords=keywords,
            mode=args.mode,
            case_sensitive=args.case_sensitive,
            backup=not args.no_backup
        )
        
        result = cleaner.clean_file(args.file)
        
        print("\n清理结果:")
        print(f"文件: {result['file_path']}")
        print(f"原行数: {result['original_lines']}")
        print(f"删除行数: {result['removed_lines']}")
        print(f"剩余行数: {result['remaining_lines']}")
        
        if result['backup_path']:
            print(f"备份文件: {result['backup_path']}")
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
