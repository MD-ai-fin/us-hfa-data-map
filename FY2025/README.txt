FY2025 美国州级 Housing Authority / Housing Finance Agency
ACFR / 经审计财务报表 采集目录

目录结构
- pdf/          各州 FY2025 ACFR/财务报表 PDF（44/51 州已获取）
- txt/          从 PDF 提取的全文文本
- direct_urls.json      已验证/搜集的直接下载链接
- state_hfa_catalog.json  51 州/特区 HFA 名录与财务页
- fy2025_metrics.json     自动+人工校正的财务指标
- download_log.json       下载日志
- collect_and_analyze.py  主采集与分析脚本
- reextract_and_report.py  基于已有 PDF 重新提取并生成 Word
- FY2025_美国州级住房金融机构ACFR综合分析报告.docx  中文 Word 总结
- FY2025_US_State_HFA_ACFR_Analysis_Report.docx        英文文件名副本

尚未获取 FY2025 独立报告的州/特区（7）
AZ, NH, NJ, NV, NY, OR, RI
原因：尚未发布、404、或仅通过 BondLink/门户登录提供。

重新运行
  python collect_and_analyze.py
  python reextract_and_report.py

注意：reextract_and_report.py 会用自身的正则规则重新提取全部州的指标，
并整份覆盖 fy2025_metrics.json 与两份 Word 报告，不经过
build_map_data.py 里的 MANUAL_OVERRIDES 人工校正层。对已人工核实过
数据的州（如 MS/TN/MD/PA 等），重新运行前请先确认这些人工修正不会被
覆盖丢失，或运行后再对照 MANUAL_OVERRIDES 重新核对一遍。
