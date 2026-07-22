//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketData.mqh                                         |
//| Layer   : Market                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_MARKETDATA_MQH
#define CORE_MARKET_MARKETDATA_MQH


class CMarketData
{

public:


    double Bid() const
    {
        return SymbolInfoDouble(
            _Symbol,
            SYMBOL_BID
        );
    }



    double Ask() const
    {
        return SymbolInfoDouble(
            _Symbol,
            SYMBOL_ASK
        );
    }



    double Spread() const
    {
        return Ask()-Bid();
    }


};


#endif