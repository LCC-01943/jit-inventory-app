
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="JIT 醫療庫存模型", layout="centered")
st.title("🩺 Just-In-Time 醫療庫存模擬器")

# Sidebar input
st.sidebar.header("參數設定")
days = st.sidebar.slider("模擬天數", 7, 180, 30)
alpha = st.sidebar.slider("指數平滑係數 α", 0.0, 1.0, 0.3)
z = st.sidebar.slider("服務水準 Z 值", 0.0, 3.0, 1.645)
lead_time = st.sidebar.number_input("交貨期 L (天)", min_value=1, value=3)
order_cost = st.sidebar.number_input("每次訂購成本 S", min_value=1, value=50)
holding_cost = st.sidebar.number_input("單位日持有成本 H", min_value=0.1, value=2.0)
initial_inventory = st.sidebar.number_input("初始庫存", min_value=0, value=100)

# 模擬每日需求
np.random.seed(42)
demand = np.random.poisson(lam=20, size=days)
forecast = [demand[0]]
for t in range(1, days):
    forecast.append(alpha * demand[t - 1] + (1 - alpha) * forecast[t - 1])

demand_std = np.std(demand[:10])
safety_stock = z * demand_std * np.sqrt(lead_time)
rop = np.array(forecast) * lead_time + safety_stock

# EOQ 計算
total_annual_demand = np.sum(demand) * (365 / days)
eoq = int(np.sqrt((2 * total_annual_demand * order_cost) / (holding_cost * 365)))

# 模擬補貨
inventory = [initial_inventory]
orders = [0]
pending_orders = []
for t in range(1, days):
    arrivals = sum(q for day, q in pending_orders if day == t)
    pending_orders = [(day, q) for day, q in pending_orders if day != t]

    current_inventory = inventory[-1] + arrivals - demand[t]
    current_inventory = max(current_inventory, 0)

    if current_inventory <= rop[t]:
        orders.append(eoq)
        pending_orders.append((t + lead_time, eoq))
    else:
        orders.append(0)

    inventory.append(current_inventory)

# 顯示圖表與表格
df = pd.DataFrame({
    'Day': np.arange(days),
    'Demand': demand,
    'Forecast': np.round(forecast, 2),
    'ROP': np.round(rop, 2),
    'Inventory': inventory,
    'Order': orders
})

st.subheader("📊 模擬結果")
st.line_chart(df[['Inventory', 'ROP']], use_container_width=True)
st.bar_chart(df['Order'], use_container_width=True)

with st.expander("🔍 查看每日明細表"):
    st.dataframe(df)

st.success(f"建議經濟訂購量 EOQ：{eoq} 單位")
