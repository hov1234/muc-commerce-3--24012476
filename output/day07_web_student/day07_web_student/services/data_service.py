from pathlib import Path
import pandas as pd

def _read_csv(file_path: Path):
    return pd.read_csv(file_path, encoding="utf-8-sig")

def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")
    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))

    # 2-1：补齐4张指标卡
    metrics = [
        {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
        {"label": "总体流失率", "value": f"{metric_map['流失率']:.1%}", "note": "百分比"},
        {"label": "平均订单数", "value": f"{metric_map['平均订单数']:.2f}", "note": "单/人"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()

    # 步骤3-2：品类筛选逻辑（删除多余def，修正缩进、字段名）
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    # 2-2：流失率最高生命周期观察文案
    max_churn_row = segment_df.loc[segment_df["流失率"].idxmax()]
    insight = (
        f"生命周期中「{max_churn_row['TenureGroup']}」阶段流失率最高，"
        f"达 {max_churn_row['流失率']:.1%}，是用户流失的高风险边界。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }