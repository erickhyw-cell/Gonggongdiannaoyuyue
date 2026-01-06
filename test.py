import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 文件路径
DATA_FILE = 'booking_data.csv'

# 初始化数据文件
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=['姓名', '日期', '开始时间', '结束时间', '备注'])
    df.to_csv(DATA_FILE, index=False)

# --- 密码验证逻辑 ---
PASSWORD = "admin"  # 这里设置你的密码

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
        # 读取现有数据
        df = pd.read_csv(DATA_FILE)
        # 这里可以加入“时间冲突检测”的逻辑代码
        # ...
        
        # 写入新数据
        new_booking = pd.DataFrame({'姓名': [name], '日期': [date], '开始时间': [start_time], '结束时间': [end_time], '备注': [note]})
        new_booking.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("预约成功！")

# --- 主界面：显示看板 ---
st.subheader("📅 当前预约情况")
if os.path.exists(DATA_FILE):
    df_show = pd.read_csv(DATA_FILE)
    st.dataframe(df_show, use_container_width=True)
else:
    st.info("暂无预约记录")