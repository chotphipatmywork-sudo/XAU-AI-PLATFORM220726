//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : LiquidityContext.mqh                                   |
//| Layer   : Brain / Liquidity / Models                             |
//| Version : 1.0.0                                                  |
//| Purpose : Input Context for Liquidity Analysis                   |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_LIQUIDITY_MODELS_LIQUIDITYCONTEXT_MQH
#define CORE_BRAIN_LIQUIDITY_MODELS_LIQUIDITYCONTEXT_MQH

//--------------------------------------------------
// Liquidity Context
//--------------------------------------------------

class CLiquidityContext
{
public:
    string Symbol;

    ENUM_TIMEFRAMES Timeframe;

    int Bars;

    int Shift;

    double High;

    double Low;

    double Close;

    double Volume;

    double ReferenceHigh;

    double ReferenceLow;

    double AverageVolume;

    CLiquidityContext()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        Symbol = "";

        Timeframe = PERIOD_CURRENT;

        Bars = 0;

        Shift = 0;

        High = 0.0;

        Low = 0.0;

        Close = 0.0;

        Volume = 0.0;

        ReferenceHigh = 0.0;

        ReferenceLow = 0.0;

        AverageVolume = 0.0;
    }
};

#endif
