//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : PriceHelper.mqh                                        |
//+------------------------------------------------------------------+

#ifndef CORE_COMMON_PRICEHELPER_MQH
#define CORE_COMMON_PRICEHELPER_MQH

class CPriceHelper
{
public:
    static double NormalizePrice(
        const string symbol,
        const double price)
    {
        int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
        return NormalizeDouble(price, digits);
    }

    static double PointsToPrice(
        const string symbol,
        const double points)
    {
        return points * SymbolInfoDouble(symbol, SYMBOL_POINT);
    }

    static double PriceToPoints(
        const string symbol,
        const double distance)
    {
        double point = SymbolInfoDouble(symbol, SYMBOL_POINT);

        if (point <= 0.0)
            return 0.0;

        return distance / point;
    }

    static double NormalizeSL(
        const string symbol,
        const double sl)
    {
        return NormalizePrice(symbol, sl);
    }

    static double NormalizeTP(
        const string symbol,
        const double tp)
    {
        return NormalizePrice(symbol, tp);
    }
};

#endif