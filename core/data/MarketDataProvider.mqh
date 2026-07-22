//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketDataProvider.mqh                                 |
//| Layer   : Data                                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Market Data Access Layer                               |
//+------------------------------------------------------------------+

#ifndef CORE_DATA_MARKETDATAPROVIDER_MQH
#define CORE_DATA_MARKETDATAPROVIDER_MQH

//--------------------------------------------------

class CMarketDataProvider
{
public:
    double GetClose(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return iClose(symbol, tf, shift);
    }

    double GetOpen(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return iOpen(symbol, tf, shift);
    }

    double GetHigh(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return iHigh(symbol, tf, shift);
    }

    double GetLow(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return iLow(symbol, tf, shift);
    }

    int Bars(const string symbol, const ENUM_TIMEFRAMES tf)
    {
        return iBars(symbol, tf);
    }

    long GetVolume(const string symbol,const ENUM_TIMEFRAMES tf,const int shift)
    {
        return iVolume(symbol,tf,shift);
    }
};

#endif
