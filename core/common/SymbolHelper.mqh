//+------------------------------------------------------------------+

#ifndef CORE_COMMON_SYMBOLHELPER_MQH
#define CORE_COMMON_SYMBOLHELPER_MQH

class CSymbolHelper
{
public:
    static double Point(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_POINT);
    }

    static int Digits(const string symbol)
    {
        return (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
    }

    static double TickValue(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
    }

    static double TickSize(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
    }

    static double ContractSize(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_TRADE_CONTRACT_SIZE);
    }

    static double MinLot(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
    }

    static double MaxLot(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);
    }

    static double LotStep(const string symbol)
    {
        return SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
    }
};

#endif