from tkinter import *
from tkinter import filedialog, Toplevel
import tkinter as tk
import speedtest
import psutil
import socket
import threading
import pywifi
from datetime import datetime
import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure






#Hàm Form ROOT 

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x=(screen_width - width) // 2
    y=(screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def check_speed_in_thread():
    global Downloading
    global Uploading
    global Get_Ping
    global save_time
    #Thực hiện kiểm tra tốc độ mạng
    Test = speedtest.Speedtest()
    Downloading = round(Test.download() / (1000000), 2)
    Uploading = round(Test.upload() / (1000000), 2)
    Get_Ping = int(Test.results.ping)
    save_time = datetime.now().strftime("%H:%M:%S %d-%m-%y ")

    #lấy tốc độ và show 3 chỉ số xuống label dưới bằng .config()
    download.config(text=Downloading)
    download_bottom.config(text=Downloading)
    upload.config(text=Uploading)
    ping.config(text=Get_Ping)
    
    #bắt lặp đo lại sau mỗi 10s
    root.after(5000,check_speed)
    #bắt tự động lưu lịch sử đo sau mỗi 5s
    root.after(10000,save_history)


def check_speed():
    #Khởi động một luồng để kiểm tra tốc độ mạng
    thread = threading.Thread(target=check_speed_in_thread)
    thread.start()











#Hàm Menu

def save_history():
    #Sử dụng filedialog để chọn vị trí lưu file
    #file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    file_path="History.txt"
    if file_path:
        with open(file_path, "a") as file: 
            file.write(f" \n")
            file.write(f"Download Speed: {download.cget('text')} Mbps\n")
            file.write(f"Upload Speed: {upload.cget('text')} Mbps\n")
            file.write(f"Ping: {ping.cget('text')} ms\n")
            file.write(f"Time: {save_time}\n")
        print(f"Lịch sử đã được lưu trong file: {file_path} vào lúc {save_time}")



def open_history():
    #Sử dụng filedialog để chọn vị trí file cần mở
    #file_path = filedialog.__file__(defaultextension="History.txt", filetypes=[("Text files", "*.txt")])
    
    file_path="History.txt"
    if file_path:
        with open(file_path, "r") as file: 
            content=file.read()
    #tạo cửa sổ Toplevel để hiển thị lịch sử đo tốc độ mạng
    history_window=Toplevel(root)
    history_window.title("History Test")
    history_window.resizable(False,False)
    history_text=Text(history_window)
    history_text.pack(fill="both",expand=True)
    history_text.insert("1.0",content)




    
    
    #xem biểu đồ thống kê tốc độ bảng hiện tại so với tốc độ cũ đo được
def show_network_chart():
    
    #mở file
    with open("History.txt","r") as file:
        lines=file.readlines()
    #lấy 3 dòng cuối
        last_4_line=lines[-4:]
    
    for line in last_4_line:
        if "Download Speed:" in line:
            download_old=float(line.split(" ")[2])
        if "Upload Speed:" in line:
            upload_old=float(line.split(" ")[2])
        if "Ping:" in line:
            ping_old=float(line.split(" ")[1])
    
    
    
    #Tạo dữ liệu cho biểu đồ
    categories = ['Download', 'Upload', "ping", "Download_Old", "Upload_Old", "ping_Old"]
    #Sử dụng được là do khai báo global var ở trên hàm check_speed_in_thread()
    speeds = [Downloading, Uploading, Get_Ping, download_old, upload_old, ping_old]  
    colors = ["red", "blue", "green", "red", "blue", "green"]
    #Tạo biểu đồ
    fig = Figure(figsize=(8, 5), dpi=100)
    subplot = fig.add_subplot(111)
    subplot.bar(categories, speeds,color=colors)

    #Tạo cửa sổ TopLevel để hiển thị biểu đồ
    chart_window = Toplevel(root)
    chart_window.title("Network Speed Chart")
    chart_window.resizable(False,False)
    #Hiển thị biểu đồ trong cửa sổ TopLevel
    chart_canvas = FigureCanvasTkAgg(fig, master=chart_window)
    chart_canvas.get_tk_widget().pack()






    #Tìm kiếm các mạng xung quanh bằng Pywi
def show_Wifi_in_range():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    #Quét các mạng Wi-Fi xung quanh
    iface.scan()
    scan_results = iface.scan_results()

    #tạo cửa sổ Toplevel để hiển thị các wifi hiện có
    wifi_window=Toplevel(root)
    wifi_window.title("Available Wi-Fi Networks")

    wifi_text=tk.Text(wifi_window)
    wifi_text.pack(fill="both",expand=True)

    for network in scan_results:
        wifi_text.insert(tk.END,f"Wifi: {network.ssid}, Cường độ tín hiệu: {network.signal}dBm\n")






    #Xem thông tin mạng trong máy
def get_network_info():
    network_info = psutil.net_if_addrs()
    result = {}

    for interface, addrs in network_info.items():
        result[interface] = []
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                result[interface].append({
                    "mac_address": addr.address,
                })

    return result

def get_current_network_info():
    network_info = get_network_info()
    current_network_info = {}

    for interface, info in network_info.items():
        for item in info:
            mac_address = item["mac_address"]
            ip_address = socket.gethostbyname(socket.gethostname())
            current_network_info[interface] = {
                "mac_address": mac_address,
                "ip_address": ip_address,
            }

    return current_network_info

def show_network_info():
    current_network_info = get_current_network_info()

    #Tạo cửa sổ mới để hiển thị thông tin mạng
    network_info_window = Toplevel(root)
    network_info_window.title("Network Information")
    network_info_window.resizable(False,False)
    info_text = tk.Text(network_info_window)
    info_text.pack()

    for interface, info in current_network_info.items():
        info_text.insert(tk.END, f"Network Interface: {interface}\n")
        info_text.insert(tk.END, f"IP Address: {info['ip_address']}\n")
        info_text.insert(tk.END, f"MAC Address: {info['mac_address']}\n\n")


    
#Hàm Calculator

def Convert_Mb_to_MB():
    def result():
        try:
            Mb = float(input.get())  # Lấy giá trị từ ô input
            MB = round(Mb / 8, 2)  # Chuyển đổi giá trị từ Mb sang MB
            output.config(text=f"Giá trị sau khi chuyển đổi: {MB} MB")
        except ValueError:
            output.config(text="Vui lòng nhập số hợp lệ")
    
    convert_window = Toplevel(root)
    convert_window.title("Convert your max speed")
    convert_window.geometry("600x300")
    convert_window.resizable(False,False)
    
    intro=tk.Label(convert_window,text="Mời bạn nhập vào giá trị muốn chuyển đổi: ")
    intro.grid(row=0,column=0)
    
    input=tk.Entry(convert_window)
    input.grid(row=0,column=1)

    intro1=tk.Label(convert_window,text="Mb ")
    intro1.grid(row=0,column=2)

    button=tk.Button(convert_window,text="chuyển đổi sang MB",command= result)
    button.grid(row=1,column=1)

    output=tk.Label(convert_window,text="")
    output.grid(row=2,column=1)



    #Thoát App
def Exit_App():
    root.destroy()










#Thiết kế khung app SpeedTest

root = Tk()
root.title("Internet Speedtest")
root.resizable(False,False)
root.configure(bg="#1a212d")
# Đặt cửa sổ ở giữa màn hình
center_window(root, 360, 600)

#icon Logo
image_logo=PhotoImage(file="logo.png")
root.iconphoto(False,image_logo)

#Images 
Top=PhotoImage(file="top.png")
Label(root,image=Top,bg="#1a212d").pack()

Main=PhotoImage(file="main.png")
Label(root,image=Main,bg="#1a212d").pack(pady=(40,0))

button=PhotoImage(file="button.png")
Button=Button(root,image=button,bg="#1a212d",bd=0,activebackground="#1a212d",cursor="hand2",command=check_speed)
Button.pack(pady=10)


#label
Label(root,text="PING",font="arial 10 bold",bg="#384056").place(x=52,y=0)
Label(root,text="DOWLOAD",font="arial 10 bold",bg="#384056").place(x=145,y=0)
Label(root,text="UPLOAD",font="arial 10 bold",bg="#384056").place(x=262,y=0)

Label(root,text="ms",font="arial 10 bold",bg="#384056",fg="white").place(x=60,y=80)
Label(root,text="Mbps",font="arial 10 bold",bg="#384056",fg="white").place(x=162,y=80)
Label(root,text="Mbps",font="arial 10 bold",bg="#384056",fg="white").place(x=273,y=80)

#khung Download ở dưới
Label(root,text="Download",font="arial 15 bold",bg="#384056",fg="white").place(x=140,y=280)
Label(root,text="Mbps",font="arial 10 bold",bg="#384056",fg="white").place(x=168,y=380)



#canh chỉ số 3 dòng trên
ping = Label(root, text="00", font="arial 13 bold", bg="#384056", fg="white")
ping.place(x=72, y=65,anchor="center")

download = Label(root, text="00", font="arial 13 bold", bg="#384056", fg="white")
download.place(x=182, y=65,anchor="center")

upload = Label(root, text="00", font="arial 13 bold", bg="#384056", fg="white")
upload.place(x=292, y=65,anchor="center")

#canh chỉ số dòng download ở dưới
download_bottom = Label(root, text="00", font="arial 40 bold", bg="#384056",fg="white")
download_bottom.place(x=188, y=350,anchor="center")








#Tạo menu chức năng
menu_bar = Menu(root)
root.config(menu=menu_bar)

#Tạo menu con
Menu_Func = Menu(menu_bar)
Menu_Calculator= Menu(menu_bar)

#Thêm menu con vào Menu gốc
menu_bar.add_cascade(label="Menu", menu=Menu_Func)
menu_bar.add_cascade(label="Calculator",menu=Menu_Calculator)
#Thêm hàm cho Menu
Menu_Func.add_command(label="Save Test File", command=save_history)
Menu_Func.add_command(label="Result",command=open_history)
Menu_Func.add_command(label="Show Chart",command=show_network_chart)
Menu_Func.add_command(label="Show Wifi in Range",command=show_Wifi_in_range)
Menu_Func.add_command(label="Network Info",command=show_network_info)
Menu_Func.add_separator()
Menu_Func.add_command(label="Exit",command=Exit_App)

#Thêm hàm cho Calculator
Menu_Calculator.add_command(label="1 Byte\t\t  = \t     8 bits", state="disabled")
Menu_Calculator.add_command(label="1 KB\t\t     =\t1024 B   ", state="disabled")
Menu_Calculator.add_command(label="1 MB\t\t    =\t1024 KB", state="disabled")
Menu_Calculator.add_command(label="1 GB\t\t     =\t1024 MB", state="disabled")
Menu_Calculator.add_command(label="1 TB\t\t     =\t1024  GB", state="disabled")
Menu_Calculator.add_separator()
Menu_Calculator.add_command(label="Convert Mb to MB",command=Convert_Mb_to_MB)

root.mainloop()