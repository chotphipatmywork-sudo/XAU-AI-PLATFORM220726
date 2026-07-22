//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ATRResult.mqh                                          |
//| Layer   : Brain / Volatility / Models                            |
//| Version : 1.1.0                                                  |
//| Purpose : ATR Analysis Result                                    |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_MODELS_ATRRESULT_MQH
#define CORE_BRAIN_VOLATILITY_MODELS_ATRRESULT_MQH

//--------------------------------------------------
// ATR Result
//--------------------------------------------------

class CATRResult
{
public:
    double Value;

    double Average;

    double Ratio;

    double RegimeAverage;

    double RegimeRatio;

    bool Increasing;

    CATRResult()
    {
        Reset();
    }

    void Reset()
    {
        Value = 0.0;

        Average = 0.0;

        Ratio = 0.0;

        RegimeAverage = 0.0;

        RegimeRatio = 0.0;

        Increasing = false;
    }
};

#endif
