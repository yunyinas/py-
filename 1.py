import sys
import time
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# 颜色与动画配置（优化速度）
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"

# 核心配置
LAST_CARD_FILE = "last_card.txt"
MAX_ATTEMPTS = 3
WORKSPACE = "/storage/emulated/0/Download/云吟工作区"
SUB_DIRS_AND_FILES = [
    "pak", "打包", "解包", "配置", "特征码", 
    "提取dat", "提取配置", "小包", "配料表.txt"
]
DAT_DIR = os.path.join(WORKSPACE, "提取dat")  
UNPACK_DAT_DIR = os.path.join(WORKSPACE, "解包/dat")  
UNPACK_UEXP_DIR = os.path.join(WORKSPACE, "解包/uexp")  

# 工具路径配置
TERMUX_HOME = "/data/user/0/com.termux/files/home/"
TOOLS_ROOT = TERMUX_HOME
QUICKBMS_PATH = os.path.join(TOOLS_ROOT, "quickbms/quickbms")
URPACK_PATH = os.path.join(TOOLS_ROOT, "urpack/urpack")
DAT_SCRIPT_PATH = os.path.join(TOOLS_ROOT, "quickbms/解包.bms")  


# -------------------- 工具初始化 --------------------
def create_termux_folders():
    needed_folders = ["scripts", "urpack", "quickbms"]
    for folder in needed_folders:
        folder_path = os.path.join(TERMUX_HOME, folder)
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                animate_text(f"✅ 已创建目录：{folder_path}", GREEN, 0.02)
            except Exception as e:
                animate_text(f"❌ 创建目录失败：{folder_path}，错误：{str(e)}", RED, 0.02)
        else:
            animate_text(f"✅ 目录已存在：{folder_path}", YELLOW, 0.02)

    # 复制 quickbms 工具
    source_quickbms = "/sdcard/Download/quickbms"
    target_quickbms = QUICKBMS_PATH
    if os.path.exists(source_quickbms) and not os.path.exists(target_quickbms):
        try:
            shutil.copy2(source_quickbms, target_quickbms)
            os.chmod(target_quickbms, 0o755)  # 直接赋予执行权限
            animate_text(f"✅ 已复制并授权 quickbms 到：{target_quickbms}", GREEN, 0.02)
        except Exception as e:
            animate_text(f"❌ 复制 quickbms 失败：{str(e)}", RED, 0.02)
    elif os.path.exists(target_quickbms):
        animate_text(f"✅ quickbms 已存在：{target_quickbms}", YELLOW, 0.02)
    else:
        animate_text(f"❌ 未找到 quickbms 源文件：{source_quickbms}", YELLOW, 0.02)

def create_unpack_bms():
    bms_content = """
get SIZE long
getdstring NAME 0
log NAME 0 SIZE
    """.strip()
    
    bms_path = DAT_SCRIPT_PATH
    if not os.path.exists(bms_path):
        try:
            with open(bms_path, "w") as f:
                f.write(bms_content)
            animate_text(f"✅ 已创建 解包.bms：{bms_path}", GREEN, 0.02)
        except Exception as e:
            animate_text(f"❌ 创建 解包.bms 失败：{str(e)}", RED, 0.02)
    else:
        animate_text(f"✅ 解包.bms 已存在：{bms_path}", YELLOW, 0.02)


# -------------------- 通用函数 --------------------
def animate_text(text, color="", delay=0.02):
    if color:
        print(color, end='', flush=True)
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    if color:
        print(RESET, end='', flush=True)
    print()

def create_workspace_structure():
    try:
        has_new = False
        if not os.path.exists(WORKSPACE):
            os.makedirs(WORKSPACE, exist_ok=True)
            if not os.path.exists(WORKSPACE):
                animate_text(f"❌ 无法创建工作区：{WORKSPACE}", RED, 0.02)
                return False
            has_new = True
            animate_text(f"✅ 创建工作区：{WORKSPACE}", GREEN, 0.02)

        for item in SUB_DIRS_AND_FILES:
            item_path = os.path.join(WORKSPACE, item)
            if item.endswith('.txt'):
                if not os.path.exists(item_path):
                    with open(item_path, 'w') as f:
                        pass
                    animate_text(f"✅ 创建文件：{item_path}", GREEN, 0.02)
                    has_new = True
            else:
                if not os.path.exists(item_path):
                    os.makedirs(item_path, exist_ok=True)
                    animate_text(f"✅ 创建目录：{item_path}", GREEN, 0.02)
                    has_new = True

        # 检查工具完整性
        tools_check = [
            (QUICKBMS_PATH, "quickbms工具"),
            (URPACK_PATH, "urpack工具"),
            (DAT_SCRIPT_PATH, "DAT解包脚本")
        ]
        missing_tools = [tn for tp, tn in tools_check if not os.path.exists(tp)]
        for tp, tn in tools_check:
            if not os.path.exists(tp):
                animate_text(f"⚠️ 缺失{tn}：{tp}", YELLOW, 0.02)

        if has_new:
            animate_text(f"✅ 工作区结构创建完成", GREEN, 0.02)
        else:
            animate_text(f"✅ 工作区结构已就绪", YELLOW, 0.02)

        return not missing_tools  # 工具齐全返回True
    except PermissionError:
        animate_text(f"❌ 权限不足，无法创建工作区内容", RED, 0.02)
    except Exception as e:
        animate_text(f"❌ 工作区创建失败：{str(e)}", RED, 0.02)
    return False


# -------------------- 卡密验证 --------------------
def validate_card():
    attempts = 0
    last_card = ""
    if os.path.exists(LAST_CARD_FILE):
        with open(LAST_CARD_FILE, "r") as f:
            last_card = f.read().strip()
    
    while attempts < MAX_ATTEMPTS:
        animate_text("\n公告:", YELLOW, 0.02)
        animate_text("笔底相思字生烫，眼底缱绻光凝霜", GREEN, 0.02)
        animate_text("爱如苔痕悄爬满，心似古井忽生澜", GREEN, 0.02)
        
        card = input(f"{RESET}请输入卡密(输入y使用上次[{last_card}]): ").strip()
        if card.lower() == "y":
            if not last_card:
                animate_text("错误：无上次卡密记录！", RED, 0.02)
                attempts += 1
                continue
            card = last_card
        
        # 模拟验证（实际需对接服务器）
        with open(LAST_CARD_FILE, "w") as f:
            f.write(card)
        animate_text("卡密验证成功！", GREEN, 0.02)
        return True
        
        attempts += 1
        animate_text(f"剩余尝试次数：{MAX_ATTEMPTS - attempts}", RED, 0.02)
    
    animate_text("错误：达到最大尝试次数，退出！", RED, 0.02)
    sys.exit(1)


# -------------------- 解包核心逻辑 --------------------
def select_pak_file():
    pak_dir = os.path.join(WORKSPACE, "pak")
    if not os.path.exists(pak_dir):
        animate_text(f"❌ PAK目录不存在：{pak_dir}", RED, 0.02)
        return None
    
    pak_files = [f for f in os.listdir(pak_dir) if f.endswith('.pak')]
    if not pak_files:
        animate_text(f"❌ {pak_dir} 中无.pak文件", RED, 0.02)
        return None
    
    animate_text("\n请选择要解包的PAK文件：", YELLOW, 0.02)
    for i, f in enumerate(pak_files, 1):
        animate_text(f"{i}. {f}", CYAN, 0.01)
    
    while True:
        try:
            choice = int(input(f"{RESET}请输入序号：")) - 1
            if 0 <= choice < len(pak_files):
                return os.path.join(pak_dir, pak_files[choice])
            animate_text("无效序号，请重新输入", RED, 0.02)
        except ValueError:
            animate_text("请输入数字", RED, 0.02)

def unpack_dat_files():
    animate_text("\n=== 开始解包DAT文件 ===", BLUE, 0.02)
    
    # 前置检查
    if not os.path.exists(QUICKBMS_PATH):
        animate_text(f"❌ 缺少quickbms：{QUICKBMS_PATH}", RED, 0.02)
        input(f"{RESET}按回车返回...")
        return
    if not os.path.exists(DAT_SCRIPT_PATH):
        animate_text(f"❌ 缺少解包脚本：{DAT_SCRIPT_PATH}", RED, 0.02)
        input(f"{RESET}按回车返回...")
        return
    
    selected_pak = select_pak_file()
    if not selected_pak:
        input(f"{RESET}按回车返回...")
        return
    
    # 确保输出目录存在
    Path(UNPACK_DAT_DIR).mkdir(parents=True, exist_ok=True)
    animate_text(f"📂 解包至：{UNPACK_DAT_DIR}", YELLOW, 0.02)
    
    try:
        animate_text(f"⏳ 解包 {os.path.basename(selected_pak)} 中...", YELLOW, 0.02)
        cmd = [QUICKBMS_PATH, DAT_SCRIPT_PATH, selected_pak, UNPACK_DAT_DIR]
        
        # 实时输出解包过程
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        ) as process:
            for line in process.stdout:
                print(f"{GREEN}{line.strip()}{RESET}")  # 直接打印解包详情
        
        if process.returncode == 0:
            animate_text(f"✅ {os.path.basename(selected_pak)} 解包完成", GREEN, 0.02)
        else:
            animate_text(f"❌ 解包失败，返回码：{process.returncode}", RED, 0.02)
    except Exception as e:
        animate_text(f"❌ 解包出错：{str(e)}", RED, 0.02)
    
    input(f"{RESET}按回车返回主菜单...")

def unpack_uexp_files():
    animate_text("\n=== 开始解包UEXP文件 ===", BLUE, 0.02)
    
    if not os.path.exists(URPACK_PATH):
        animate_text(f"❌ 缺少urpack：{URPACK_PATH}", RED, 0.02)
        input(f"{RESET}按回车返回...")
        return
    
    selected_pak = select_pak_file()
    if not selected_pak:
        input(f"{RESET}按回车返回...")
        return
    
    Path(UNPACK_UEXP_DIR).mkdir(parents=True, exist_ok=True)
    animate_text(f"📂 解包至：{UNPACK_UEXP_DIR}", YELLOW, 0.02)
    
    try:
        animate_text(f"⏳ 解包 {os.path.basename(selected_pak)} 中...", YELLOW, 0.02)
        cmd = [URPACK_PATH, "-a", selected_pak, UNPACK_UEXP_DIR]
        
        # 实时输出解包过程
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        ) as process:
            为 line 在……内 process.stdout:
                print(f"{GREEN}{line.带()}{RESET}")  # 直接打印解包详情
        
        如果 process.returncode == 0:
            animate_text(f"✅ {os.path.basename(selected_pak)} 解包完成"，绿色，0.02)
            # 执行辅助脚本（若存在）
            fz_script = os.path.join(TOOLS_ROOT, "scripts/fz")
            如果 os.path.exists(fz_script):
                try:
                    subprocess.run([fz_script], check=正确, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    animate_text("✅ 辅助脚本执行完成"，绿色，0.02)
                except Exception as e:
                    animate_text(f"❌ 辅助脚本执行失败：{str(e)}"，红色，0.02)
        其他:
            animate_text(f"❌ 解包失败，返回码：{process.returncode}"，红色，0.02)
    except Exception as e:
        animate_text(f"❌ 解包出错：{str(e)}"，红色，0.02)
    
    input(f"{RESET}按回车返回主菜单...")


# -------------------- 菜单与主流程 --------------------
def tool_menu():
    def 重绘菜单(_M)():
        print("\n" * 3)  # 简单清屏
        title = r"""
  _   _   _   _   _   _   _   _   _   _ 
 / \ / \ / \ / \ / \ / \ / \ / \ / \ / \
|X |Q |T |O |O |L | | | | | | | | | | | |
 \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/
        """
        animate_text(title, f"{BOLD}{YELLOW}", 0.01)
        animate_text("小柒美化工具 v7.0", f"{BOLD}{GREEN}", 0.02)
        animate_text("作者：小柒 | 频道：@xqbbnb | @XQ_TOOL", f"{BOLD}{CYAN}", 0.02)
        animate_text(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"{BOLD}{PURPLE}", 0.02)
   
        print(f"{YELLOW}1. 解包DAT文件{RESET}")  
        print(f"{YELLOW}2. 解包UEXP文件{RESET}")  
        print(f"{YELLOW}3. 打包DAT文件（待实现）{RESET}")
        print(f"{YELLOW}4. 打包UEXP文件（待实现）{重置}")
        print(f"{YELLOW}5. 自动美化工具（待实现）{重置}")
        print(f"{YELLOW}6. 配置工具（待实现）{重置}")
        print(f"{YELLOW}7. 提取功能（待实现）{重置}")
        print(f"{YELLOW}8. 合并非块（待实现）{RESET}")
        print(f"{YELLOW}0. 返回主菜单{RESET}")

重绘菜单(_M)()
在……期间 正确:
选择=输入(f”{重置}请输入选择[0-8]：").带()
如果选择=="0":
动画文本(_T"返回主菜单..."("返回主菜单..."，紫色，0.02)
时间。睡(0.5)
打破
Elifchoice=="1"：
unpack_dat_files()
Elifchoice=="2"：
unpack_uexp_files()
其他：
动画文本(_T)("功能暂未实现，敬请期待"，黄色，0.02)
时间。睡眠(1)
重绘菜单(_M)()

Def安装相依性(_D)()：
动画文本(_T)("\n===环境搭建==="，蓝色，0.02)
动画文本(_T)("正在安装依赖包..."，黄色，0.02)
依赖关系=["请求", "枕头"]
forDEP在...内依赖项：
动画文本(_T)(F"安装{DEP}..."，黄色，0.02)
结果=os.系统(F"管道安装{DEP}>/dev/null2>&1")
如果结果==0:
动画文本(_T)(f"✓{DEP}安装成功"，绿色，0.02)
其他:
动画文本(_T)(f"✗{DEP}安装失败（请手动安装）"，红色，0.02)
时间。睡眠(1)
动画文本(_T)("环境搭建流程完成！"，绿色，0.03)
时间。睡(2)
输入(f”{重置}按回车键返回主菜单...")


#修复：确保show_start_info在main之前定义
定义show_start_info()：
创建工作区结构()

动画文本(_T)("小柒美化工具"，F"{粗体}{绿色}"，0.05)
动画文本(_T)("小柒官方频道@xqbbnb"，f"{BOLD}{CYAN}"，0.03)
animate_text("小柒工具频道@XQ_TOOL"，f"{BOLD}{CYAN}"，0.03)
start_time=日期时间。现在().strftime("%Y-%m-%d%H：%M：%S")
动画文本(f"启动时间-{start_time}"，紫色，0.03)

打印("/_/\\")
打印(“(o.o)”)
打印(">^<")

animate_text("=====================主菜单===============", f"{BOLD}{PURPLE}"，0.02)
animate_text("1.进入工具→高级美化工具"，bold+CYAN，0.02)
animate_text("2.搭建环境→安装依赖包"，bold+GREEN，0.02)
animate_text("3.跳转TG官方频道"，粗体+黄色，0.02)
动画文本("0.退出"，粗体+红色，0.02)
animate_text("======================================", 粗体+紫色，0.02)


Def main()：
show_start_info()
当为True时：
choice=input(f"{RESET}请输入您的选择[0-3]：").strip()
        
如果选择=="1"：
如果validate_card()：
工具菜单(_M)
show_start_info()
Elif choice=="2"：
安装相依性(_D)
show_start_info()
Elif choice=="3"：
动画文本(_T)("跳转TG频道：https://t.me/XQ_TOOL"，紫色，0.03)
time.sleep(3)
Elif choice=="0"：
动画文本(_T)("退出程序，再见！"，红色，0.05)
sys.exit(0)
其他：
动画文本(_T)("无效选择，请重新输入"，红色，0.03)


如果__名称__=="__主要的__"：
主要的()
