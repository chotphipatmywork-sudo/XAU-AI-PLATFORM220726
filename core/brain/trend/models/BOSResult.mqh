//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BOSResult.mqh                                          |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Break Of Structure Analysis Result Model               |
//|                                                                  |
//| Version History                                                  |
//| 1.0.0 - Initial Creation                                         |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_BOSRESULT_MQH
#define CORE_BRAIN_TREND_MODELS_BOSRESULT_MQH

//--------------------------------------------------
// BOS Result
//--------------------------------------------------

class CBOSResult
{
public:
    bool BullishBreak;

    bool BearishBreak;

    bool ValidBreak;

    CBOSResult()
    {
        BullishBreak = false;
        BearishBreak = false;
        ValidBreak = false;
    }
};

#endif