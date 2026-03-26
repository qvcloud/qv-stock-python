import baostock as bs
import pandas as pd
import datetime

def get_daily_k_data(stock_code, start_date=None, end_date=None):
    """
    获取指定股票的日线 K 线数据
    :param stock_code: 股票代码，如 sh.600000
    :param start_date: 开始日期，格式 YYYY-MM-DD
    :param end_date: 结束日期，格式 YYYY-MM-DD
    """
    if end_date is None:
        end_date = datetime.date.today().strftime('%Y-%m-%d')
    if start_date is None:
        # 默认获取从上市第一天到今天
        # BaoStock 可以通过 query_stock_basic 获取上市日期
        # 如果不指定，直接传一个足够早的日期如 1990-01-01 也可以获取全量
        start_date = "1990-01-01"
    
    # 登录系统
    lg = bs.login()
    if lg.error_code != '0':
        print(f"login respond error_code: {lg.error_code}")
        return None

    # 获取日线 K 线
    # fields: date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST
    # frequency: d 日线, w 周线, m 月线
    # adjustflag: 复权类型，默认不复权：3；后复权：1；前复权：2
    rs = bs.query_history_k_data_plus(stock_code,
        "date,code,open,high,low,close,preclose,volume,amount,turn,pctChg,isST",
        start_date=start_date, end_date=end_date, 
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

if __name__ == "__main__":
    # 示例：获取平安银行 (sz.000001) 最近一个月的日线数据
    stock_code = "sz.000001"
    print(f"正在获取 {stock_code} 的日线数据...")
    
    df = get_daily_k_data(stock_code)
    
    if df is not None and not df.empty:
        print(f"成功获取到 {len(df)} 行数据")
        print(df.tail(10)) # 显示最近 10 天
        
        # 保存到 CSV
        filename = f"{stock_code}_daily.csv"
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"数据已保存至: [{filename}]({filename})")
    else:
        print("未获取到数据，请确认代码和日期范围是否正确。")
