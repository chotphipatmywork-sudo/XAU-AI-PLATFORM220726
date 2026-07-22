//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : VolatilityResult.mqh                                   |
//| Layer   : Brain / Volatility / Models                            |
//| Version : 1.1.0                                                  |
//| Purpose : Final Output of Volatility Package                     |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_VOLATILITY_MODELS_VOLATILITYRESULT_MQH
#define CORE_BRAIN_VOLATILITY_MODELS_VOLATILITYRESULT_MQH

//--------------------------------------------------
// Volatility State
//--------------------------------------------------

enum ENUM_VOLATILITY_STATE
{
    VOLATILITY_UNKNOWN = 0,
    VOLATILITY_LOW,
    VOLATILITY_NORMAL,
    VOLATILITY_HIGH,
    VOLATILITY_EXPANDING,
    VOLATILITY_CONTRACTING
};

//--------------------------------------------------
// Volatility Result
//--------------------------------------------------

class CVolatilityResult
{
public:
    ENUM_VOLATILITY_STATE State;

    double ATR;

    double ADR;

    double ExpansionScore;

    double CompressionScore;

    double Confidence;

    double AIVolatilityRegime;

    double AIVolatilityChange;

    CVolatilityResult()
    {
        Reset();
    }

    void Reset()
    {
        State = VOLATILITY_UNKNOWN;

        ATR = 0.0;

        ADR = 0.0;

        ExpansionScore = 0.0;

        CompressionScore = 0.0;

        Confidence = 0.0;

        AIVolatilityRegime = 50.0;

        AIVolatilityChange = 50.0;
    }
};

#endif
