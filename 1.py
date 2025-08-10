importsys
进口时间
从……起datetimeimportdatetime

def show_start_info():
    print("\033[1；32m小柒美化工具\033[0m")
    print("\033[1；33m小柒官方频道@xqbnb\033[0m")
    print("\033[1；34m小柒工具频道@XQ_TOOL\033[0m")
start_time=日期时间。现在().strftime("%Y-%m-%d%H：%M：%S")
    print(F"启动时间-{start_time}")
    print(" /_/")
    print("(o.o)")
    print("> ^ <")
    print("\033[1;35m================主菜单================\033[0m")
    print("\033[1；36m1.进入工具\033[0m")
    print("\033[1；32m2.搭建环境(首次必需执行)\033[0m")
    print("\033[1；31m0.退出\033[0m")
    print("\033[1;35m========================================\033[0m")

def enter_tool():
    print("\n===进入工具===")
    print("这里可以添加真正的工具功能逻辑，比如解包操作等...")
时间。sleep(2)
    input("按回车键返回主菜单...")

def setup_environment():
    print("\n===搭建环境===")
    print("正在执行环境搭建流程...")
    print("假设这里完成了依赖安装、目录创建等操作")
    time.sleep(3)
    input("环境搭建完成，按回车键返回主菜单...")

def main():
在……期间 正确:
        show_start_info()
选择=input("请输入您的选择 [0-2]: ")
ifchoice=="1":
            enter_tool()
Elifchoice=="2":
            setup_environment()
        elif choice == "0":
            print("退出程序，再见！")
sys.出口(0)
其他:
            print("无效的选择，请重新输入！")
时间。sleep(1)
        print("\n" * 50)

if__name__=="__main__":
    main()
