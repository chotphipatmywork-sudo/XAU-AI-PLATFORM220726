//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SlopeResult.mqh                                        |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 2.0.0                                                  |
//| Purpose : EMA Slope Analysis Result Model                        |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_SLOPERESULT_MQH
#define CORE_BRAIN_TREND_MODELS_SLOPERESULT_MQH

//--------------------------------------------------
// Slope Result
//--------------------------------------------------

class CSlopeResult
{
public:
    //--------------------------------------------------
    // Slope Value
    //--------------------------------------------------

    double Value;

    //--------------------------------------------------
    // Direction
    //--------------------------------------------------

    bool Rising;

    bool Falling;

    //--------------------------------------------------
    // Constructor
    //--------------------------------------------------

    CSlopeResult()
    {
        Reset();
    }

    //--------------------------------------------------
    // Reset
    //--------------------------------------------------

    void Reset()
    {
        Value = 0.0;

        Rising = false;
        Falling = false;
    }
};

#endif