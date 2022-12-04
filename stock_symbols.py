# credit: https://medium.datadriveninvestor.com/download-list-of-all-stock-symbols-using-this-python-package-12937073b25

from stocksymbol import StockSymbol

api_key = 'e64a87dc-0b67-4b3e-ae58-c863212debed'

ss = StockSymbol(api_key)

def getStockSymbolList():
    return ss.get_symbol_list(market="US", symbols_only=True)