//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureResult.mqh                                    |
//| Layer   : Brain / Trend / Models                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Market Structure Analysis Result Model                 |
//|                                                                  |
//| Version History                                                  |
//| 1.0.0 - Initial Creation                                         |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_TREND_MODELS_STRUCTURERESULT_MQH
#define CORE_BRAIN_TREND_MODELS_STRUCTURERESULT_MQH

//--------------------------------------------------
// Structure Result
//--------------------------------------------------

class CStructureResult
{
public:
    bool HigherHigh;

    bool HigherLow;

    bool LowerHigh;

    bool LowerLow;

    bool ValidStructure;

    CStructureResult()
    {
        HigherHigh = false;
        HigherLow = false;

        LowerHigh = false;
        LowerLow = false;

        ValidStructure = false;
    }
};

#endif