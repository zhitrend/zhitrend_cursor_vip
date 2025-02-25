#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logo
print_logo() {
    echo -e "${CYAN}"
    cat << "EOF"
   ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗      ██████╗ ██████╗  ██████╗   
  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗     ██╔══██╗██╔══██╗██╔═══██╗  
  ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝     ██████╔╝██████╔╝██║   ██║  
  ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗     ██╔═══╝ ██╔══██╗██║   ██║  
  ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║     ██║     ██║  ██║╚██████╔╝  
   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝  
EOF
    echo -e "${NC}"
}

# 获取下载文件夹路径
get_downloads_dir() {
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "$HOME/Downloads"
    else
        if [ -f "$HOME/.config/user-dirs.dirs" ]; then
            . "$HOME/.config/user-dirs.dirs"
            echo "${XDG_DOWNLOAD_DIR:-$HOME/Downloads}"
        else
            echo "$HOME/Downloads"
        fi
    fi
}

# 獲取最新版本
get_latest_version() {
    echo -e "${CYAN}ℹ️ 正在檢查最新版本...${NC}"
    local latest_release
    latest_release=$(curl -s https://api.github.com/repos/yeongpin/cursor-free-vip/releases/latest)
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 無法獲取最新版本信息${NC}"
        exit 1
    fi
    
    VERSION=$(echo "$latest_release" | grep -o '"tag_name": ".*"' | cut -d'"' -f4 | tr -d 'v')
    echo -e "${GREEN}✅ 找到最新版本: ${VERSION}${NC}"
}

# 檢測系統類型和架構
detect_os() {
    if [[ "$(uname)" == "Darwin" ]]; then
        # 检测 macOS 架构
        ARCH=$(uname -m)
        if [[ "$ARCH" == "arm64" ]]; then
            OS="mac_arm64"
            echo -e "${CYAN}ℹ️ 检测到 macOS ARM64 架构${NC}"
        else
            OS="mac_intel"
            echo -e "${CYAN}ℹ️ 检测到 macOS Intel 架构${NC}"
        fi
    elif [[ "$(uname)" == "Linux" ]]; then
        OS="linux"
        echo -e "${CYAN}ℹ️ 检测到 Linux 系统${NC}"
    else
        # 假设是 Windows
        OS="windows"
        echo -e "${CYAN}ℹ️ 检测到 Windows 系统${NC}"
    fi
}

# 下載並安裝
install_cursor_free_vip() {
    local downloads_dir=$(get_downloads_dir)
    local binary_name="CursorFreeVIP_${VERSION}_${OS}"
    local binary_path="${downloads_dir}/cursor-free-vip"
    local download_url="https://github.com/yeongpin/cursor-free-vip/releases/download/v${VERSION}/${binary_name}"
    
    echo -e "${CYAN}ℹ️ 正在下載到 ${downloads_dir}...${NC}"
    echo -e "${CYAN}ℹ️ 下載鏈接: ${download_url}${NC}"
    
    # 先检查文件是否存在
    if curl --output /dev/null --silent --head --fail "$download_url"; then
        echo -e "${GREEN}✅ 文件存在，开始下载...${NC}"
    else
        echo -e "${RED}❌ 下载链接不存在: ${download_url}${NC}"
        echo -e "${YELLOW}⚠️ 尝试不带架构的版本...${NC}"
        
        # 尝试不带架构的版本
        if [[ "$OS" == "mac_arm64" || "$OS" == "mac_intel" ]]; then
            OS="mac"
            binary_name="CursorFreeVIP_${VERSION}_${OS}"
            download_url="https://github.com/yeongpin/cursor-free-vip/releases/download/v${VERSION}/${binary_name}"
            echo -e "${CYAN}ℹ️ 新下载链接: ${download_url}${NC}"
            
            if ! curl --output /dev/null --silent --head --fail "$download_url"; then
                echo -e "${RED}❌ 新下载链接也不存在${NC}"
                exit 1
            fi
        else
            exit 1
        fi
    }
    
    # 下载文件
    if ! curl -L -o "${binary_path}" "$download_url"; then
        echo -e "${RED}❌ 下載失敗${NC}"
        exit 1
    fi
    
    # 检查下载的文件大小
    local file_size=$(stat -f%z "${binary_path}" 2>/dev/null || stat -c%s "${binary_path}" 2>/dev/null)
    echo -e "${CYAN}ℹ️ 下載的文件大小: ${file_size} 字節${NC}"
    
    # 如果文件太小，可能是错误信息
    if [ "$file_size" -lt 1000 ]; then
        echo -e "${YELLOW}⚠️ 警告: 下載的文件太小，可能不是有效的可執行文件${NC}"
        echo -e "${YELLOW}⚠️ 文件內容:${NC}"
        cat "${binary_path}"
        echo ""
        echo -e "${RED}❌ 下載失敗，請檢查版本號和操作系統是否正確${NC}"
        exit 1
    fi
    
    echo -e "${CYAN}ℹ️ 正在設置執行權限...${NC}"
    chmod +x "${binary_path}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 安裝完成！${NC}"
        echo -e "${CYAN}ℹ️ 程序已下載到: ${binary_path}${NC}"
        echo -e "${CYAN}ℹ️ 正在啟動程序...${NC}"
        
        # 直接运行程序
        "${binary_path}"
    else
        echo -e "${RED}❌ 安裝失敗${NC}"
        exit 1
    fi
}

# 主程序
main() {
    print_logo
    get_latest_version
    detect_os
    install_cursor_free_vip
}

# 運行主程序
main 