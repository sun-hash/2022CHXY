from threading import Thread
from re import compile
from csv import writer
from requests import get
from requests import codes
from tkinter.ttk import Combobox, Progressbar
from tkinter.scrolledtext import ScrolledText
from tkinter import END ,Tk ,Label ,messagebox

datas = []

def showNotice(message:str):
    notice.insert(END ,message+"\n")
    notice.see(END)

def queryData():
    progress['mode'] = "indeterminate"
    showNotice("请求数据...")
    progress.start(10)
    url = "https://www.chu.edu.cn/zsw/2022/0728/c1524a141390/page.htm"
    try:
        res = get(url)
    except:
        messagebox.showwarning(title='网络错误',message="请保持网络畅通")
        root.quit()
    if not res.status_code == codes.ok :
        messagebox.showwarning(title='未知错误',message="服务器未返回正确结果")
        root.quit()
    showNotice("数据获取成功\n解析数据...")
    progress.stop()
    progress['mode'] = "determinate"
    res.encoding="utf-8"
    html = res.text
    tbody = compile('''<table class="wp_editor_art_table".*?<tbody>(.*?)</tbody.*?</table>''').findall(html)[0]
    tr = compile('''<tr>(.*?)</tr>''').findall(tbody)
    progress['maximum'] = len(tr)
    progress['value'] = 0
    for td in tr:
        data = compile("<td.*?>(.*?)</td>").findall(td)
        data[1] += '$'
        datas.append(data)
        progress['value'] += 1
    showNotice("数据解析完成")
    combo['values'] = list( { major[4] for major in datas if not major[4] == "录取专业"} )
    combo.bind("<<ComboboxSelected>>",check )


#下拉菜单
def check(*args):
    major = combo.get()
    showNotice("查询数据...")
    results = [ data for data in datas if data[4] == major ]
    if len(results) == 0:
        showNotice("未找到相关数据!")
        return
    showNotice("数据查询完成\n正在写入文件...")
    file = major+".csv"
    progress['maximum'] = len(results)
    progress['value'] = 0
    with open(file,'w',encoding='utf-8-sig') as f:
        wtr = writer(f)
        for data in results:
            wtr.writerow(data)
            progress['value'] += 1
    showNotice("结果保存至:[当前目录]\\"+str(file))

#窗体
root = Tk()
root.geometry('500x300')
root.title('2022各专业新生名单')
Label(root,text='欢迎使用',font=30,fg='red').pack(pady=30)

#进度条
progress = Progressbar(root ,length=480 )
progress.pack(pady=6)

#状态提示
notice = ScrolledText(root ,width=480 ,height=8 )
notice.pack( pady=6 )

#下拉菜单
combo = Combobox(root,state='readonly')
combo.set('选择专业')
combo.pack()

th = Thread(target=queryData )
th.setDaemon(True)
th.start()

root.mainloop()