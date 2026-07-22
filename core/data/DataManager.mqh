//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DataManager.mqh                                        |
//| Layer   : Data                                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Central Data Manager                                   |
//+------------------------------------------------------------------+

#ifndef CORE_DATA_DATAMANAGER_MQH
#define CORE_DATA_DATAMANAGER_MQH

#include "MarketDataProvider.mqh"

//--------------------------------------------------

class CDataManager
{
private:
    CMarketDataProvider m_provider;

public:
    //--------------------------------------------------

    double GetClose(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return m_provider.GetClose(symbol, tf, shift);
    }

    double GetOpen(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return m_provider.GetOpen(symbol, tf, shift);
    }

    double GetHigh(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return m_provider.GetHigh(symbol, tf, shift);
    }

    double GetLow(const string symbol, const ENUM_TIMEFRAMES tf, int shift)
    {
        return m_provider.GetLow(symbol, tf, shift);
    }

    int Bars(const string symbol, const ENUM_TIMEFRAMES tf)
    {
        return m_provider.Bars(symbol, tf);
    }

    long GetVolume(const string symbol,const ENUM_TIMEFRAMES tf,const int shift)
    {
        return m_provider.GetVolume(symbol,tf,shift);
    }
};

#endif
