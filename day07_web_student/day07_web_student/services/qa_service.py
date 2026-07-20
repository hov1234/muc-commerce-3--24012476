from pathlib import Path
import pandas as pd

def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    # 读取三份数据
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")

    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    max_churn_seg = segment_df.loc[segment_df["流失率"].idxmax()]
    max_churn_cat = category_df.loc[category_df["流失率"].idxmax()]

    normalized = question.replace(" ", "").lower()

    # 1.总用户
    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数']):,}名用户。"
    # 2.流失率
    elif any(word in normalized for word in ["流失率", "整体流失", "流失比例"]):
        return f"平台整体流失率为{metrics['流失率']:.1%}，流失用户共{int(metrics['流失人数'])}人。"
    # 3.订单相关
    elif any(word in normalized for word in ["平均订单", "订单数", "下单"]):
        return f"平台用户平均订单数为{metrics['平均订单数']:.2f}单/人。"
    # 4.偏好品类
    elif any(word in normalized for word in ["品类", "偏好", "手机", "服饰"]):
        return f"流失风险最高的偏好品类是{max_churn_cat['PreferedOrderCat']}，流失率{max_churn_cat['流失率']:.1%}。"
    # 5.生命周期风险
    elif any(word in normalized for word in ["生命周期", "新用户", "流失风险", "阶段"]):
        return f"流失风险最高的用户生命周期阶段是「{max_churn_seg['TenureGroup']}」，流失率高达{max_churn_seg['流失率']:.1%}。"
    # 无匹配问题
    else:
        return "暂未识别该问题，可询问总用户数、整体流失率、平均订单数、高风险品类、用户生命周期流失风险。"