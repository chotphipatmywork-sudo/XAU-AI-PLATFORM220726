//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : MarketAnalyzer.mqh                                     |
//| Layer   : Market Analysis                                        |
//+------------------------------------------------------------------+

#ifndef CORE_MARKET_ANALYZER_MQH
#define CORE_MARKET_ANALYZER_MQH

#include "../models/MarketContext.mqh"


class CMarketAnalyzer
{

public:

    bool Analyze(CMarketContext &context)
    {

        if(context.Symbol == "")
            context.Symbol = _Symbol;


        context.Bid =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_BID
            );


        context.Ask =
            SymbolInfoDouble(
                context.Symbol,
                SYMBOL_ASK
            );


        context.Spread =
            context.Ask - context.Bid;


        return true;
    }

};


#endif