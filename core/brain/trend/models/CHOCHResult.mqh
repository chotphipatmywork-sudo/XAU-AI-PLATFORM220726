//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : CHOCHResult.mqh                                        |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Change Of Character Analysis Result Model              |
//|                                                                  |
//| Version History                                                  |
//| 1.0.0 - Initial Creation                                         |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_CHOCHRESULT_MQH
#define CORE_BRAIN_TREND_MODELS_CHOCHRESULT_MQH

//--------------------------------------------------
// CHOCH Result
//--------------------------------------------------

class CCHOCHResult
{
public:
    bool BullishCHOCH;

    bool BearishCHOCH;

    bool ValidCHOCH;

    CCHOCHResult()
    {
        BullishCHOCH = false;
        BearishCHOCH = false;
        ValidCHOCH = false;
    }
};

#endif