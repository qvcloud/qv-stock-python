import baostock as bs
import pandas as pd
import datetime

def get_stock_indicators(stock_code, date=None):
    """
    获取指定股票在指定日期的主要指标数据 (K线数据包含市盈率、市净率等)
    """
    if date is None:
        date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 登录系统
    lg = bs.login()
    if lg.error_code != '0':
        print(f"login respond error_code: {lg.error_code}")
        return None

    # 获取估值指标 (K线数据中包含 peTTM, pbMRQ, psTTM, pcfNcfTTM 等)
    # fields: date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM
    rs = bs.query_history_k_data_plus(stock_code,
        "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
        start_date=date, end_date=date, 
        frequency="d", adjustflag="3")
    
    if rs.error_code != '0':
        print(f"query_history_k_data_plus respond error_code: {rs.error_code}")
        bs.logout()
        return None

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    bs.logout()
    
    if not data_list:
        return None
        
    return pd.DataFrame(data_list, columns=rs.fields)

def get_all_stock_indicators():
    """
    批量获取所有股票的最新指标数据
    """
    # 1. 先读之前保存的股票列表
    try:
        stocks_df = pd.read_csv("all_stocks.csv")
    except FileNotFoundError:
        print("未找到 all_stocks.csv，请先运行 get_stocks.py")
        return

    # 过滤掉指数 (简单逻辑：通常 A 股个股 code 为 sh.6xxxxx 或 sz.0xxxxx/sz.3xxxxx)
    # 过滤掉 tradeStatus 为 0 的停牌股（可选）
    stocks_df = stocks_df[stocks_df['code'].str.contains(r'sh\.6|sz\.(0|3)')]
    
    # 获取最近一个交易日的日期（简单处理：昨天）
    target_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"正在获取日期为 {target_date} 的指标数据...")

    bs.login()
    
    all_indicators = []
    count = 0
    total = len(stocks_df)
    
    # 为了演示效率，这里仅获取前 50 只股票作为示例，实际使用可以去掉 head(50)
    sample_stocks = stocks_df.head(50) 
    
    for _, row in sample_stocks.iterrows():
        code = row['code']
        name = row['code_name']
        
        # 获取 K 线指标数据
        rs = bs.query_history_k_data_plus(code,
            "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
            start_date=target_date, end_date=target_date, 
            frequency="d", adjustflag="3")
        
        while (rs.error_code == '0') & rs.next():
            row_data = rs.get_row_data()
            row_data.append(name) # 加入名称
            all_indicators.append(row_data)
        
        count += 1
        if count % 10 == 0:
            print(f"进度: {count}/{len(sample_stocks)}")

    bs.logout()
    
    if all_indicators:
        fields = rs.fields + ['code_name']
        result_df = pd.DataFrame(all_indicators, columns=fields)
        
        # 保存结果
        output_file = "stock_indicators.csv"
        result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n获取完成！共获取 {len(result_df)} 条指标数据。")
        print(f"结果已保存至: [stock_indicators.csv](stock_indicators.csv)")
        print("\n前 5 条数据如下：")
        print(result_df.head())
    else:
        print("未获取到任何指标数据，请检查日期是否为交易日。")

if __name__ == "__main__":
    get_all_stock_indicators()
