//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ATRResult.mqh                                          |
//| Layer   : Indicators / Models                                    |
//| Version : 1.0.0                                                  |
//| Purpose : ATR Indicator Result                                   |
//+------------------------------------------------------------------+

#ifndef CORE_INDICATORS_MODELS_ATRRESULT_MQH
#define CORE_INDICATORS_MODELS_ATRRESULT_MQH

class CATRResult
{
public:
    double ATR;

    CATRResult()
    {
        Reset();
    }

    void Reset()
    {
        ATR = 0.0;
    }
};

#endif