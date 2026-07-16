import pandas as pd
import numpy as np
# ===================== 1. 数据读取与基础认识 =====================
# 读取CSV数据\
file_path = "淘宝全品类全国数据.csv"
try:
    df = pd.read_csv(file_path, encoding="utf-8")
except:
    df = pd.read_csv(file_path, encoding="gbk")

print("="*50)
print("1. 数据基础信息概览")
print("="*50)
# 数据规模验证
print(f"总商品记录数：{df.shape[0]} 条")
print(f"总字段数：{df.shape[1]} 个")
print("\n字段完整列表：")
for idx, col in enumerate(df.columns, 1):
    print(f"{idx}. {col}")

# 数据类型与非空值统计
print("\n数据类型与非空值详情：")
df.info()

# 缺失值统计
print("\n各字段缺失值统计：")
missing_stats = df.isna().sum().sort_values(ascending=False)
missing_rate = (missing_stats / df.shape[0] * 100).round(2)
missing_df = pd.DataFrame({
    "缺失数量": missing_stats,
    "缺失占比(%)": missing_rate
})
print(missing_df[missing_df["缺失数量"] > 0])

# 数据样例查看
print("\n前5条商品数据样例：")
print(df.head())

# 商品销量字段格式识别
print("\n商品销量字段前20个值样例（识别文字分档规则）：")
print(df["商品销量"].head(20).to_string())

# ===================== 2. 数据选择 =====================
print("\n" + "="*50)
print("2. 数据选择操作")
print("="*50)

# 2.1 列选择：筛选核心分析字段
core_cols = [
    "商品id", "商品标题", "一级品类", "二级品类", "商品价格", 
    "商品销量", "省份", "店铺标签", "先用后付", "退货宝",
    "风格", "面料", "版型", "适用季节"
]
df_core = df[core_cols].copy()
print(f"核心字段选择后，数据维度：{df_core.shape}")

# 2.2 行选择：筛选价格>0、销量非空的有效商品
df_valid = df_core[
    (df_core["商品价格"] > 0) & 
    (df_core["商品销量"].notna())
].copy()
print(f"有效商品记录数：{df_valid.shape[0]} 条")

# ===================== 3. 筛选与排序=====================
print("\n" + "="*50)
print("3. 数据筛选与排序操作")
print("="*50)

# 3.1 基础筛选：筛选「服饰鞋包」一级品类商品
df_clothes = df_valid[df_valid["一级品类"] == "服饰鞋包"].copy()
print(f"服饰鞋包品类商品数：{df_clothes.shape[0]} 条")

# 3.2 多条件筛选：广东省、价格100-500元的服饰鞋包商品
df_filtered = df_clothes[
    (df_clothes["省份"] == "广东") & 
    (df_clothes["商品价格"] >= 100) & 
    (df_clothes["商品价格"] <= 500)
].copy()
print(f"广东省100-500元服饰鞋包商品数：{df_filtered.shape[0]} 条")

# 3.3 排序：按价格降序、商品id升序排序
df_sorted = df_filtered.sort_values(
    by=["商品价格", "商品id"],
    ascending=[False, True]
).reset_index(drop=True)
print("\n筛选排序后的前10条商品：")
print(df_sorted[["商品id", "商品标题", "商品价格", "商品销量"]].head(10))

# ===================== 4. 统计分析与解释=====================
print("\n" + "="*50)
print("4. 数据统计分析结果")
print("="*50)

# 4.1 数值字段描述性统计
print("数值字段基础描述性统计：")
print(df_valid.describe())

# 4.2 一级品类维度统计：商品数量、均价、价格区间
category_stats = df_valid.groupby("一级品类").agg(
    商品总数=("商品id", "count"),
    平均价格=("商品价格", "mean"),
    最低价格=("商品价格", "min"),
    最高价格=("商品价格", "max"),
    价格中位数=("商品价格", "median")
).round(2).sort_values("商品总数", ascending=False)
print("\n各一级品类商品统计：")
print(category_stats)

# 4.3 省份维度统计：各省份上架商品数、均价
province_stats = df_valid.groupby("省份").agg(
    上架商品数=("商品id", "count"),
    省份均价=("商品价格", "mean")
).round(2).sort_values("上架商品数", ascending=False)
print("\n各省份商品上架统计（Top20）：")
print(province_stats.head(20))

# 4.4 店铺标签分布统计
tag_stats = df_valid["店铺标签"].value_counts().reset_index()
tag_stats.columns = ["店铺标签", "商品数量"]
print("\n店铺标签分布：")
print(tag_stats)

# 4.5 服务开通占比统计（先用后付、退货宝）
pay_after_count = df_valid[df_valid["先用后付"] == "有"].shape[0]
refund_count = df_valid[df_valid["退货宝"] == "有"].shape[0]
total_valid = df_valid.shape[0]
print(f"开通先用后付的商品数：{pay_after_count}，占比：{np.array(pay_after_count/total_valid*100).round(2)}%")
print(f"开通退货宝的商品数：{refund_count}，占比：{np.array(refund_count/total_valid*100).round(2)}%")

# ===================== 5. 销量分档与价格区间深度分析 =====================
print("\n" + "="*50)
print("5. 挑战任务：销量分档与价格区间分析")
print("="*50)

# 5.1 销量数值提取（仅用Pandas字符串方法，无额外库）
df_valid["销量数值"] = df_valid["商品销量"].str.extract(r"(\d+)").fillna(0).astype(int)
print("\n销量数值提取完成，前10条销量数据对照：")
print(df_valid[["商品销量", "销量数值"]].head(10))

# 5.2 销量分档统计
sale_bins = [0, 100, 500, 1000, 5000, 10000, 50000, 100000, 9999999]
sale_labels = ["0-100", "101-500", "501-1000", "1001-5000", "5001-10000", "10001-50000", "50001-100000", "100000以上"]
df_valid["销量分档"] = pd.cut(df_valid["销量数值"], bins=sale_bins, labels=sale_labels, right=True)
sale_group_stats = df_valid.groupby("销量分档").agg(
    商品数量=("商品id", "count"),
    平均价格=("商品价格", "mean")
).round(2)
print("\n销量分档统计：")
print(sale_group_stats)

# 5.3 价格区间统计
price_bins = [0, 50, 100, 200, 500, 1000, 5000, 10000, 999999]
price_labels = ["0-50元", "51-100元", "101-200元", "201-500元", "501-1000元", "1001-5000元", "5001-10000元", "10000元以上"]
df_valid["价格区间"] = pd.cut(df_valid["商品价格"], bins=price_bins, labels=price_labels, right=True)
price_group_stats = df_valid.groupby("价格区间").agg(
    商品数量=("商品id", "count"),
    平均销量=("销量数值", "mean")
).round(2)
print("\n价格区间统计：")
print(price_group_stats)