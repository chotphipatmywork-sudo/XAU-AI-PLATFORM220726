//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : VolatilityContext.mqh                                  |
//| Layer   : Brain / Volatility / Models                            |
//| Version : 1.0.0                                                  |
//| Purpose : Input Context for Volatility Analysis                  |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_MODELS_VOLATILITYCONTEXT_MQH
#define CORE_BRAIN_VOLATILITY_MODELS_VOLATILITYCONTEXT_MQH

//--------------------------------------------------
// Volatility Context
//--------------------------------------------------

class CVolatilityContext
{
public:
    string Symbol;

    ENUM_TIMEFRAMES Timeframe;

    int Bars;

    int Shift;

    CVolatilityContext()
    {
        Symbol = "";

        Timeframe = PERIOD_CURRENT;

        Bars = 0;

        Shift = 0;
    }
};

#endif
