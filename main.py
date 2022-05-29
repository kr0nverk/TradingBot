import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

if __name__ == '__main__':

    stock = 'TSLA'

    start = '2016-01-01'
    end = '2022-05-01'
    data = yf.download(stock, start, end)

    # Скользящие средние
    short_ma = 5
    long_ma = 12

    # Перепродано/Перекупано
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    sr_sell = 0.7
    sr_buy = 0.3

    # Скользящая средняя
    data['MA' + str(short_ma)] = data["Close"].rolling(short_ma).mean()
    data['MA' + str(long_ma)] = data["Close"].rolling(long_ma).mean()

    #plt.plot(data['MA5'])
    #plt.plot(data['MA12'])

    # Доходность
    data['return'] = data['Close'].pct_change()
    # Движение цены вверх/вниз
    data['Up'] = np.maximum(data['Close'].diff(),0)
    data['Down'] = np.maximum(-data['Close'].diff(),0)
    # Относительная Сила за 14 дней
    data['RS'] = data['Up'].rolling(rsi_period).mean()/data['Down'].rolling(rsi_period).mean()
    # Индекс ОС
    data['RSI'] = 100 - 100/(1 + data['RS'])
    # Округление к близкому круглому числу 10-20:11,12,13; 100-200:110,120,130;
    data['S&R'] = (data['Close']/(10**np.floor(np.log10(data['Close']))))%1

    #plt.plot(data['S&R'])

    start = max(long_ma,rsi_period)
    # 1-купить -1-продать
    data['MACD_signal'] = 2*(data['MA' + str(short_ma)]>data['MA' + str(long_ma)]) - 1
    data['RSI_signal'] = 1*(data['RSI'] < rsi_oversold) - 1*(data['RSI'] > rsi_overbought)
    data['S&R-signal'] = 1*(data['S&R'] < sr_buy) - 1*(data['S&R'] > sr_sell)

    BnH_return = np.array(data['return'][start+1:])
    MACD_return = np.array(data['return'][start+1:])*np.array(data['MACD_signal'][start:-1])
    RSI_return = np.array(data['return'][start + 1:]) * np.array(data['RSI_signal'][start:-1])
    SR_return = np.array(data['return'][start + 1:]) * np.array(data['S&R-signal'][start:-1])

    #plt.plot(np.cumprod(1+BnH_return))
    #plt.plot(np.cumprod(1 + MACD_return))
    #plt.plot(np.cumprod(1 + RSI_return))
    #plt.plot(np.cumprod(1 + SR_return))

    # Годовые заработки
    BnH = np.prod(1 + BnH_return) ** (252 / len(BnH_return))
    MACD = np.prod(1 + MACD_return) ** (252 / len(MACD_return))
    RSI = np.prod(1 + RSI_return) ** (252 / len(RSI_return))
    SR = np.prod(1 + SR_return) ** (252 / len(SR_return))

    BnH_risk = np.std(BnH_return) * (252) ** (1 / 2)
    MACD_risk = np.std(MACD_return) * (252) ** (1 / 2)
    RSI_risk = np.std(RSI_return) * (252) ** (1 / 2)
    SR_risk = np.std(SR_return) * (252) ** (1 / 2)

    print('Доходность и риск стратегии buy-and-hold ' + str(round(BnH * 100, 2)) + '% и ' + str(
        round(BnH_risk * 100, 2)) + '%')
    print('Доходность и риск стратегии скользящих средних ' + str(round(MACD * 100, 2)) + '% и ' + str(
        round(MACD_risk * 100, 2)) + '%')
    print('Доходность и риск стратегии RSI ' + str(round(RSI * 100, 2)) + '% и ' + str(
        round(RSI_risk * 100, 2)) + '%')
    print('Доходность и риск стратегии поддержки и сопротивления ' + str(round(SR * 100, 2)) + '% и ' + str(
        round(SR_risk * 100, 2)) + '%')

    #print(data)
    plt.show()
