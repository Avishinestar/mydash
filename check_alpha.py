import yfinance as yf
batch_df = yf.download(["^NSEI", "^CNXAUTO"], period="5d", interval="1d", progress=False)
print("Close:")
print(batch_df['Close'])
print("Adj Close:")
print(batch_df['Adj Close'])
