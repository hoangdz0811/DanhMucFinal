from vnstock import Company


# Hoặc sử dụng VCI (dữ liệu đầy đủ hơn)
company = Company(symbol='DDV', source='VCI')

dx = company.overview()[['symbol', 'charter_capital', 'icb_name2']].head()

print(dx)
