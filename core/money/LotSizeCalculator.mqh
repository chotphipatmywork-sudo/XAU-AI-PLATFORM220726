//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LotSizeCalculator.mqh                                  |
//| Layer   : Core / Money                                           |
//| Version : 1.0.0                                                  |
//| Purpose : Calculate Trading Lot Size                             |
//+------------------------------------------------------------------+

#ifndef CORE_MONEY_LOTSIZECALCULATOR_MQH
#define CORE_MONEY_LOTSIZECALCULATOR_MQH

class CLotSizeCalculator
{
public:
    double Calculate(
        const string symbol,
        const double riskMoney,
        const double stopLossPoints)
    {
        if (stopLossPoints <= 0.0)
            return 0.01;

        double tickValue =
            SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);

        double tickSize =
            SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);

        if (tickValue <= 0.0 || tickSize <= 0.0)
            return 0.01;

        double pointValue =
            tickValue / tickSize;

        double lot =
            riskMoney /
            (stopLossPoints * pointValue);

        double minLot =
            SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);

        double maxLot =
            SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX);

        double stepLot =
            SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);

        lot = MathMax(minLot, MathMin(maxLot, lot));
        lot = MathFloor(lot / stepLot) * stepLot;

        return NormalizeDouble(lot, 2);
    }
};

#endif