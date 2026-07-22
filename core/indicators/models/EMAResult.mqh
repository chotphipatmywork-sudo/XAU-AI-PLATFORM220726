//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : EMAResult.mqh                                          |
//| Layer   : Indicators / Models                                    |
//| Version : 1.0.0                                                  |
//| Purpose : EMA Indicator Result                                   |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_MODELS_EMARESULT_MQH
#define CORE_INDICATORS_MODELS_EMARESULT_MQH

class CEMAResult
{
public:
    double FastEMA;
    double SlowEMA;

    bool Bullish;
    bool Bearish;

    CEMAResult()
    {
        Reset();
    }

    void Reset()
    {
        FastEMA = 0.0;
        SlowEMA = 0.0;

        Bullish = false;
        Bearish = false;
    }
};

#endif