# 导入自定义的 customtkinter 用于美化 Tkinter 界面
import customtkinter as ctk
# 导入 tkinter，用于创建右键菜单功能
import tkinter as tk
# 导入 json 用于保存与读取任务数据，导入 os 检查文件是否存在
import json, os

# 设置应用外观为浅色模式
ctk.set_appearance_mode("light")
# 设置默认颜色主题为蓝色
ctk.set_default_color_theme("blue")

# 定义保存任务数据的文件名（保存任务时使用）
SAVE_FILE = "tasks.json"

# 这里指定中文字体，根据你的系统可以更改字体名称
CHINESE_FONT_NAME = "Noto Sans SC"
# 字体大小设置
FONT_SIZE = 14

# 定义一组背景颜色（每个任务卡片会依次使用不同颜色）
COLOR_LIST = ["#ffa2a2", "#ffbea2", "#fee678", "#b7fe78", "#78fe9a", "#85d2fe", "#e5acfd"]

# 定义主界面的任务应用程序类
class TaskApp:
    def __init__(self, 主窗口):
        """
        初始化函数，设置界面、控件以及读取之前保存的任务数据。
        参数:
            主窗口: 主窗口对象
        """
        # 将主窗口保存到实例变量中，方便后续使用
        self.root = 主窗口

        # 拖拽数据，用来记录拖拽时的状态，方便任务卡片进行位置交换
        self.drag_data = {"card": None, "last_y": 0, "acc": 0}
        # 用列表存放所有任务数据，每个任务由任务卡片、状态变量和任务标签组成
        self.tasks = []

        # 创建一个用于输入任务的输入框
        self.entry = ctk.CTkEntry(
            主窗口,
            placeholder_text="输入任务，按 Enter 添加",  # 提示文字
            height=35,  # 输入框高度
            font=ctk.CTkFont(family=CHINESE_FONT_NAME, size=FONT_SIZE)  # 设置字体样式和大小
        )
        # 将输入框添加到主窗口，并设置左右和上下的边距
        self.entry.pack(padx=20, pady=(20, 10), fill="x")
        # 当用户按下 Enter 键时调用 add_task 方法添加任务
        self.entry.bind("<Return>", lambda e: self.add_task())

        # 创建一个带滚动条的容器，用于放置任务卡片，fg_color="transparent" 表示无背景色
        self.frame = ctk.CTkScrollableFrame(主窗口, fg_color="transparent")
        self.frame.pack(padx=20, pady=10, fill="both", expand=True)

        # 创建“保存任务”按钮，点击后执行保存任务方法
        self.save_btn = ctk.CTkButton(
            主窗口,
            text="💾 保存任务",
            font=ctk.CTkFont(family=CHINESE_FONT_NAME, size=FONT_SIZE),
            command=self.save_tasks
        )
        self.save_btn.pack(pady=10)

        # 创建右键菜单，实现任务文本复制功能
        self.context_menu = tk.Menu(主窗口, tearoff=0)
        self.context_menu.add_command(label="复制", command=self._copy_label_text)

        # 加载之前保存的任务数据
        self.load_tasks()

    def add_task(self, text=None, completed=False):
        """
        添加一个任务，并在界面上创建一个任务卡片。
        参数:
            text: 可选，任务文本（如果不传入则从输入框中获取）
            completed: 可选，任务是否被标记完成（默认 False）
        """
        # 获取任务文字，如果 text 参数不存在，就从输入框中获取并去除前后空格
        task_text = text or self.entry.get().strip()
        # 如果任务文本为空，则直接返回，不添加任务
        if not task_text:
            return

        # 根据当前任务数量从颜色列表中按顺序选取背景颜色
        color = COLOR_LIST[len(self.tasks) % len(COLOR_LIST)]

        # 创建一个任务卡片（CTkFrame），设置背景颜色、圆角和高度
        card = ctk.CTkFrame(self.frame, fg_color=color, corner_radius=12, height=40)
        # 将任务卡片填充到水平空间，并设置内边距
        card.pack(fill="x", pady=6, padx=4)
        # 禁止卡片内部组件自动根据内容大小调整
        card.pack_propagate(False)

        # 创建一个变量保存任务是否完成的状态（布尔类型）
        var = ctk.BooleanVar(value=completed)
        # 创建一个复选框用于标记任务是否完成
        cb = ctk.CTkCheckBox(
            card,
            text="",
            variable=var,
            font=ctk.CTkFont(family=CHINESE_FONT_NAME, size=FONT_SIZE),
            # 点击复选框时调用 toggle_task 方法，传入当前的状态变量和标签
            command=lambda: self.toggle_task(var, label)
        )
        # 将复选框放到任务卡片的左侧，并设置左右边距
        cb.pack(side="left", padx=(10, 5))

        # 创建一个标签，用于显示任务的文字
        label = ctk.CTkLabel(
            card,
            text=task_text,
            anchor="w",  # 左对齐
            font=ctk.CTkFont(family=CHINESE_FONT_NAME, size=FONT_SIZE)
        )
        # 将标签放在卡片中间，充满剩余空间
        label.pack(side="left", fill="x", expand=True)

        # 为标签绑定右键点击事件，实现复制任务文字功能
        label.bind("<Button-3>", lambda e, lab=label: self._show_context_menu(e, lab))

        # 创建一个删除按钮，点击后删除该任务
        del_btn = ctk.CTkButton(
            card,
            text="✖",  # 按钮上显示的删除符号
            width=30,
            height=25,
            fg_color="red",  # 正常状态下的背景颜色
            text_color="white",  # 文字颜色
            hover_color="#cc0000",  # 鼠标悬停时的颜色
            font=ctk.CTkFont(family=CHINESE_FONT_NAME, size=FONT_SIZE),
            command=lambda: self.remove_task(card)  # 删除该任务卡片
        )
        # 将删除按钮放到卡片的右侧，并设置左右边距
        del_btn.pack(side="right", padx=10)

        # 为任务卡片及其内部组件绑定拖拽事件，
        # 绑定鼠标左键按下、拖拽和释放事件，支持任务卡片的位置交换
        for widget in (card, cb, label, del_btn):
            widget.bind("<Button-1>", lambda e, c=card: self.start_drag(e, c))
            widget.bind("<B1-Motion>", self.on_drag)
            widget.bind("<ButtonRelease-1>", self.end_drag)

        # 将任务卡片、状态变量、任务标签存入任务列表中
        self.tasks.append((card, var, label))
        # 清空输入框
        self.entry.delete(0, "end")

        # 根据任务是否完成设置文字样式（例如是否加删除线）
        self.toggle_task(var, label)

    def toggle_task(self, var, label):
        """
        根据复选框的状态更新任务标签样式：
        - 如果选中（完成），任务文字变为灰色并添加删除线
        - 否则，任务文字为黑色且正常显示
        """
        if var.get():
            label.configure(
                text_color="gray",
                font=(CHINESE_FONT_NAME, FONT_SIZE, "overstrike")
            )
        else:
            label.configure(
                text_color="black",
                font=(CHINESE_FONT_NAME, FONT_SIZE, "normal")
            )

    def remove_task(self, card):
        """
        删除指定的任务卡片
        参数:
            card: 要删除的任务卡片（CTkFrame 对象）
        """
        # 遍历任务列表，找到对应的卡片，然后销毁它并从列表中删除
        for i, (c, var, label) in enumerate(self.tasks):
            if c == card:
                c.destroy()  # 销毁卡片控件
                self.tasks.pop(i)  # 从任务列表中移除
                break

    def save_tasks(self):
        """
        将当前所有任务的数据保存到 JSON 文件中
        每个任务保存文字和完成状态
        """
        # 使用列表推导，将每个任务的文字和状态存入数据列表中
        data = [{"text": label.cget("text"), "completed": var.get()} for c, var, label in self.tasks]
        # 打开保存文件，使用 UTF-8 编码写入数据
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_tasks(self):
        """
        从保存文件中加载任务，如果文件存在则读取并添加到界面中
        """
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                # 读取 JSON 数据后，循环调用 add_task 添加每个任务
                for item in json.load(f):
                    self.add_task(item["text"], item.get("completed", False))

    def _show_context_menu(self, event, label):
        """
        显示右键菜单，实现任务文字的复制功能。
        参数:
            event: 右键点击事件信息
            label: 被右键点击的任务标签
        """
        # 保存当前的标签对象，方便在复制时获取文字
        self.current_label = label
        # 在鼠标点击处显示右键菜单
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _copy_label_text(self):
        """
        将当前标签的文字复制到系统剪贴板
        """
        text = self.current_label.cget("text")  # 获取标签文本
        self.root.clipboard_clear()  # 清空系统剪贴板
        self.root.clipboard_append(text)  # 将文本添加到剪贴板

    def start_drag(self, event, card):
        """
        记录拖拽开始时的状态，为拖拽交换任务位置做准备
        参数:
            event: 鼠标事件信息
            card: 被拖拽的任务卡片
        """
        self.drag_data["card"] = card         # 记录当前拖拽的卡片
        self.drag_data["last_y"] = event.y_root  # 记录鼠标当前的垂直位置
        self.drag_data["acc"] = 0              # 初始化累计位移为 0

    def on_drag(self, event):
        """
        在拖拽过程中计算鼠标移动的位移，并根据一定的阈值交换任务卡片位置
        参数:
            event: 鼠标拖拽过程中的事件信息
        """
        card = self.drag_data["card"]
        # 如果没有正在拖拽的卡片，直接返回
        if not card:
            return

        # 取得当前鼠标垂直坐标
        current_y = event.y_root
        # 计算上一次记录位置与当前位置的差值（位移）
        delta = current_y - self.drag_data["last_y"]

        # 将此次位移累加到累计值中
        self.drag_data["acc"] += delta
        # 更新上次记录位置为当前位置
        self.drag_data["last_y"] = current_y

        # 找到当前拖拽卡片在任务列表中的索引
        idx = next((i for i, (c, _, _) in enumerate(self.tasks) if c == card), None)
        if idx is None:
            return

        # 定义交换所需的累计位移的阈值
        THRESHOLD = 42

        # 如果累计位移足够大，且向上移动时，交换任务卡片的位置
        while self.drag_data["acc"] <= -THRESHOLD and idx > 0:
            # 交换当前位置与前一个任务的位置
            self.tasks[idx], self.tasks[idx - 1] = self.tasks[idx - 1], self.tasks[idx]
            # 刷新任务卡片在界面中的排列顺序
            self._refresh_cards()
            idx -= 1
            # 更新累计位移
            self.drag_data["acc"] += THRESHOLD

        # 如果累计位移足够大，且向下移动时，交换任务卡片的位置
        while self.drag_data["acc"] >= THRESHOLD and idx < len(self.tasks) - 1:
            # 交换当前位置与后一个任务的位置
            self.tasks[idx], self.tasks[idx + 1] = self.tasks[idx + 1], self.tasks[idx]
            self._refresh_cards()
            idx += 1
            self.drag_data["acc"] -= THRESHOLD

    def end_drag(self, event):
        """
        拖拽结束后重置拖拽数据
        """
        self.drag_data = {"card": None, "last_y": 0, "acc": 0}

    def _refresh_cards(self):
        """
        刷新任务列表中所有任务卡片在界面中的排列，
        先移除所有卡片再依次重新排列。
        """
        # 移除所有已排列的卡片
        for c, var, label in self.tasks:
            c.pack_forget()
        # 重新将卡片依次排列
        for c, var, label in self.tasks:
            c.pack(fill="x", pady=6, padx=4)

def main():
    """
    主函数，程序入口，创建主窗口、设置窗口大小与位置，并启动任务应用程序
    """
    # 创建主窗口对象并命名为“任务清单”
    任务清单 = ctk.CTk()
    任务清单.title("任务清单")

    # 设置窗口大小 (宽 480, 高 600)
    w, h = 480, 600
    # 计算窗口左上角坐标，使窗口居中显示
    x = (任务清单.winfo_screenwidth() - w) // 2
    y = (任务清单.winfo_screenheight() - h) // 2
    任务清单.geometry(f"{w}x{h}+{x}+{y}")
    # 设置窗口的最小尺寸
    任务清单.minsize(w, h)

    # 创建任务应用实例并传入主窗口
    TaskApp(任务清单)
    # 开启事件循环，等待用户操作
    任务清单.mainloop()

# 当本模块作为主程序执行时，调用 main 函数启动应用
if __name__ == "__main__":
    main()
