import baostock as bs
import pandas as pd

def get_all_stock_list():
    # 登录系统
    lg = bs.login()
    if lg.error_code != '0':
        print(f"login respond error_code: {lg.error_code}")
        print(f"login respond error_msg: {lg.error_msg}")
        return

    # 获取证券信息
    # 动态获取当前日期
    import datetime
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    rs = bs.query_all_stock(day=current_date)
    
    # 如果当天没有数据（比如周末或节假日），尝试获取前一天的数据
    # BaoStock query_all_stock 在非交易日可能返回空或报错
    if rs.error_code != '0' or rs.next() == False:
        # 简单回退策略：尝试获取最近的交易日数据（此处仅回退一天示例）
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        rs = bs.query_all_stock(day=yesterday)

    if rs.error_code != '0':
        print(f"query_all_stock respond error_code: {rs.error_code}")
        print(f"query_all_stock respond error_msg: {rs.error_msg}")
        bs.logout()
        return

    # 存储结果
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    
    # 转换为 DataFrame
    result = pd.DataFrame(data_list, columns=rs.fields)

    # 登出系统
    bs.logout()

    return result

if __name__ == "__main__":
    stocks_df = get_all_stock_list()
    if stocks_df is not None:
        # 过滤指数，仅保留常见的深市和沪市股票 (A股通常以 sh.6 或 sz.0/sz.3 开头)
        # 注意：这里可能需要更好的逻辑或不进行过滤，默认输出全量
        print(f"共获取到 {len(stocks_df)} 只股票/证券/指数信息")
        
        # 建议：过滤代码中包含 ".sh" 或 ".sz" 的个股
        # 一般来说指数是以 sh.000001 这种格式，个股也是，区分需要看名称或代码规则
        # 此处展示获取的前 10 条
        print("最新前 10 条记录如下：")
        print(stocks_df.head(10))
        
        # 将结果保存到 csv 文件中
        filename = "all_stocks.csv"
        stocks_df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"数据已保存至: [all_stocks.csv](all_stocks.csv)")
