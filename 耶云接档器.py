# <ETS2存档接收器>
# Copyright (C) 2025-现在 耶云数据-omg@yeee.lol
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


#请勿修改本文件内的版权信息，其余信息可自由开发，谢谢！

#由XXX进行二次开发
import os
import zipfile
import requests
import shutil
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, filedialog
from tkinter.ttk import Frame, Style

class FileReplaceTool:
    def __init__(self, root):
        self.root = root
        self.root.title("耶云数据文件下载器-离线版")
        self.root.geometry("600x400")  # 设置界面大小
        self.root.resizable(False, False)  # 禁止调整窗口大小

        # 配置文件路径
        self.config_file = "config.txt"

        # 定义样式
        self.style = Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10), width=12)

        # 创建主框架
        main_frame = Frame(root, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 添加提示信息
        self.help_text = (
            "欢迎使用耶云数据文件下载器离线版！\n"
            "1. 在上方输入框中输入下载地址。\n"
            "2. 点击「选择文件夹」按钮选择目标文件夹。\n"
            "3. 点击「下载并解压」按钮开始下载并解压文件。\n"
            "4. 如需卸载，点击「卸载」按钮删除目标文件夹。\n"
            "5. 如有问题或建议，请点击「关于」按钮联系我们\n\n"
            "温馨提示:ETS2默认存档位置位于：\n"
            r"C:\Users\你的用户名\Documents\Euro Truck Simulator 2\profiles"
        )
        self.help_label = Label(main_frame, text=self.help_text, justify="left", font=("Arial", 10), fg="gray")
        self.help_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="w")

        # 输入下载地址
        Label(main_frame, text="下载地址:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.url_entry = Entry(main_frame, width=40, font=("Arial", 10))
        self.url_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 输入目标文件夹
        Label(main_frame, text="目标文件夹:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.folder_entry = Entry(main_frame, width=40, font=("Arial", 10))
        self.folder_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # 选择文件夹按钮
        self.select_button = Button(main_frame, text="选择文件夹", command=self.select_folder)
        self.select_button.grid(row=2, column=2, padx=5, pady=5)

        # 操作按钮框架
        button_frame = Frame(main_frame, style="TFrame")
        button_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=15, sticky="nsew")

        self.download_button = Button(button_frame, text="下载并解压", command=self.download_and_extract)
        self.download_button.pack(side="left", padx=10)

        self.uninstall_button = Button(button_frame, text="卸载", command=self.uninstall)
        self.uninstall_button.pack(side="left", padx=10)

        self.about_button = Button(button_frame, text="关于", command=self.show_about)
        self.about_button.pack(side="right", padx=10)

        # 状态信息
        self.status_var = StringVar()
        self.status_label = Label(main_frame, textvariable=self.status_var, fg="green", font=("Arial", 10))
        self.status_label.grid(row=4, column=0, columnspan=3, pady=10, sticky="w")

        # 加载上次选择的路径
        self.load_last_folder()

    def load_last_folder(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                last_folder = f.read().strip()
                if os.path.exists(last_folder):
                    self.folder_entry.delete(0, "end")
                    self.folder_entry.insert(0, last_folder)
                    self.status_var.set(f"已加载上次选择的路径：{last_folder}")
                    return
        self.select_folder()  # 如果没有上次的路径，则弹出文件管理器

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(folder)
            self.status_var.set(f"已选择路径：{folder}")

    def download_and_extract(self):
        url = self.url_entry.get()
        folder = self.folder_entry.get()

        if not url:
            messagebox.showwarning("警告", "请输入下载地址！")
            return

        if not folder:
            messagebox.showwarning("警告", "请输入目标文件夹路径！")
            return

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                self.status_var.set(f"目标文件夹已创建：{folder}")
            except Exception as e:
                messagebox.showerror("错误", f"无法创建目标文件夹: {e}")
                return

        try:
            # 下载文件
            response = requests.get(url)
            response.raise_for_status()
            zip_file_path = os.path.join(folder, "temp_download.zip")
            with open(zip_file_path, "wb") as f:
                f.write(response.content)
            self.status_var.set("下载完成，正在解压...")

            # 解压文件
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(folder)
            os.remove(zip_file_path)
            self.status_var.set("解压完成！")
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {e}")
            self.status_var.set("操作失败！")

    def uninstall(self):
        folder = self.folder_entry.get()
        if not folder:
            messagebox.showwarning("警告", "请输入目标文件夹路径！")
            return

        try:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                self.status_var.set("文件夹已删除！")
            else:
                messagebox.showwarning("警告", "指定文件夹不存在！")
        except Exception as e:
            messagebox.showerror("错误", f"删除失败: {e}")
            self.status_var.set("删除失败！")

    def show_about(self):
        """显示关于窗口"""
        about_text = (
            "耶云数据文件下载器-离线版\n"
            "版本: 1.0.2\n"
            "版权所有: © 2025-现在 耶云数据\n"
            "联系方式: omg@yeee.lol\n"
            "本工具用于下载并解压文件到指定文件夹，支持自动记忆路径。\n"
            "如有问题或建议，请联系开发团队。"
        )
        messagebox.showinfo("关于", about_text)

if __name__ == "__main__":
    root = Tk()
    app = FileReplaceTool(root)
    root.mainloop()
