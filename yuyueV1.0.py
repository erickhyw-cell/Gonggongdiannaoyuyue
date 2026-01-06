import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="公用电脑预约系统", layout="wide")

# 文件路径
DATA_FILE = 'booking_data.csv'

# 初始化数据文件
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=['姓名', '日期', '开始时间', '结束时间', '备注'])
    df.to_csv(DATA_FILE, index=False)

# --- 密码验证逻辑 ---
PASSWORD = "313313"  # 这里设置你的密码

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 请先登录")
    pwd = st.text_input("请输入访问密码", type="password")
    if st.button("登录"):
        if pwd == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ 密码错误，请重试")
    st.stop()  # 只有登录成功才会继续执行下面的代码

# --- 登录成功后显示的主界面 ---
st.title("🖥️ 公用电脑预约系统")

# 侧边栏：显示退出按钮
with st.sidebar:
    if st.button("🚪 退出登录"):
        st.session_state.logged_in = False
        st.rerun()

# --- 侧边栏：填写预约 ---
with st.sidebar:
    st.header("📝 新增预约")
    name = st.text_input("你的姓名")
    date = st.date_input("预约日期", min_value=datetime.today())
    start_time = st.time_input("开始时间")
    end_time = st.time_input("结束时间")
    note = st.text_area("用途备注")
    
    if st.button("提交预约"):
        # 1. 基础校验：结束时间必须晚于开始时间
        if start_time >= end_time:
            st.error("⚠️ 结束时间必须晚于开始时间！")
            st.stop()

        # 读取现有数据
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception:
            df = pd.DataFrame(columns=['姓名', '日期', '开始时间', '结束时间', '备注'])
        
        # 2. 冲突检测逻辑
        # 筛选出当天的预约
        target_date_str = str(date)
        day_bookings = df[df['日期'] == target_date_str]
        
        is_conflict = False
        conflict_msg = ""
        
        # 将输入时间转为字符串方便比较
        new_start_str = str(start_time)
        new_end_str = str(end_time)
        
        for index, row in day_bookings.iterrows():
            exist_start = str(row['开始时间'])
            exist_end = str(row['结束时间'])
            
            # 判断是否有重叠
            if not (new_end_str <= exist_start or new_start_str >= exist_end):
                is_conflict = True
                conflict_msg = f"与现有预约冲突：{row['姓名']} ({exist_start} - {exist_end})"
                break
        
        if is_conflict:
            st.error(f"⚠️ 预约失败！\n{conflict_msg}")
        else:
            # 写入新数据
            new_booking = pd.DataFrame({'姓名': [name], '日期': [date], '开始时间': [start_time], '结束时间': [end_time], '备注': [note]})
            new_booking.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("✅ 预约成功！")
            st.rerun()

# --- 主界面：显示看板 ---
st.subheader("📅 当前预约情况")

if os.path.exists(DATA_FILE):
    df_show = pd.read_csv(DATA_FILE)
    
    # 转换为日历事件格式
    calendar_events = []
    
    # 预定义一组颜色，轮流使用
    colors = ['#FF6C6C', '#8A2BE2', '#20B2AA', '#FFD700', '#FF4500', '#1E90FF', '#32CD32']
    
    for index, row in df_show.iterrows():
        # 分配颜色
        color = colors[index % len(colors)]
        
        calendar_events.append({
            "title": f"{row['姓名']} - {row['备注']}",
            "start": f"{row['日期']}T{row['开始时间']}",
            "end": f"{row['日期']}T{row['结束时间']}",
            "color": color
        })
        
    # 日历配置
    calendar_options = {
        "headerToolbar": {  # 设置日历头部工具栏
            "left": "today prev,next",  # 左侧：今天、上一页、下一页按钮
            "center": "title",  # 中间：显示当前日期范围标题
            "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek"  # 右侧：切换月、周、日、列表视图
        },
        "initialView": "timeGridWeek",  # 设置初始视图为周时间网格
        "slotMinTime": "01:00:00",  # 设置日历显示的起始时间
        "slotMaxTime": "24:00:00",  # 设置日历显示的截止时间
        "slotDuration": "02:00:00",  # 设置时间间隔为 2 小时
        "slotLabelInterval": "02:00:00",  # 设置时间标签间隔为 2 小时
        "height": "auto",  # 让日历高度自动适应内容，防止最后一行被截断
    }
    
    # 渲染日历组件
    calendar(
        events=calendar_events,  # 传入预约事件数据
        options=calendar_options,  # 传入日历显示配置
        custom_css="""
            /* 自定义 CSS：微调事件标题和时间的字体大小 */
            .fc-event-title, .fc-event-time { font-size: 0.85em; }
            /* 强制设置行高，确保每行高度一致且足够显示内容 */
            .fc-timegrid-slot { height: 60px !important; border-bottom: 1px solid #ddd !important; }
        """
    )
    
    st.markdown("---")
    st.subheader("📋 预约管理")

    # 显示详细表格和删除按钮
    cols = st.columns([2, 2, 2, 2, 4, 1])
    cols[0].write("**姓名**")
    cols[1].write("**日期**")
    cols[2].write("**开始时间**")
    cols[3].write("**结束时间**")
    cols[4].write("**备注**")
    cols[5].write("**操作**")

    for index, row in df_show.iterrows():
        col = st.columns([2, 2, 2, 2, 4, 1])
        col[0].write(row['姓名'])
        col[1].write(row['日期'])
        col[2].write(row['开始时间'])
        col[3].write(row['结束时间'])
        col[4].write(row['备注'])
        
        if col[5].button("🔴删除", key=f"del_{index}"):
            # 删除对应行
            df_show = df_show.drop(index)
            # 保存回文件
            df_show.to_csv(DATA_FILE, index=False)
            st.success("已删除该预约")
            st.rerun()

else:
    st.info("暂无预约记录")