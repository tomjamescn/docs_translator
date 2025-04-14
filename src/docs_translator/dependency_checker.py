"""依赖检查模块。

此模块提供检查和提示缺失依赖包的功能。
"""

import re
import logging
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class DependencyChecker:
    """依赖检查器类。
    
    检查依赖包是否存在，并提供安装建议。
    """
    
    @staticmethod
    def check_error_for_missing_dependencies(error_message: str) -> Optional[List[str]]:
        """从错误消息中检查是否有缺失的依赖包。
        
        Parameters
        ----------
        error_message : str
            错误消息
            
        Returns
        -------
        Optional[List[str]]
            缺失的依赖包列表，如果没有检测到则返回None
        """
        missing_deps = []
        
        # 检查 pkg_resources.DistributionNotFound 错误
        dist_not_found_pattern = r"DistributionNotFound: The '([^']+)' distribution was not found"
        dist_matches = re.findall(dist_not_found_pattern, error_message)
        if dist_matches:
            missing_deps.extend(dist_matches)
        
        # 检查 ModuleNotFoundError 错误
        module_not_found_pattern = r"ModuleNotFoundError: No module named '([^']+)'"
        module_matches = re.findall(module_not_found_pattern, error_message)
        if module_matches:
            missing_deps.extend(module_matches)
        
        # 检查 ImportError 错误
        import_error_pattern = r"ImportError: No module named ([^\s]+)"
        import_matches = re.findall(import_error_pattern, error_message)
        if import_matches:
            missing_deps.extend(import_matches)
        
        return missing_deps if missing_deps else None
    
    @staticmethod
    def get_installation_instructions(missing_deps: List[str]) -> str:
        """获取安装指令。
        
        Parameters
        ----------
        missing_deps : List[str]
            缺失的依赖包列表
            
        Returns
        -------
        str
            安装指令
        """
        instructions = "检测到缺少以下依赖包:\n"
        
        for dep in missing_deps:
            instructions += f"  - {dep}\n"
        
        instructions += "\n您可以通过以下命令安装这些依赖包:\n\n"
        
        for dep in missing_deps:
            instructions += f"pip install --no-deps {dep}\n"
        
        instructions += "\n如果上述命令不起作用，您可能需要安装完整依赖:\n\n"
        
        for dep in missing_deps:
            instructions += f"pip install {dep}\n"
        
        return instructions