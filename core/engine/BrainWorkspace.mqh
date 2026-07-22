//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainWorkspace.mqh                                     |
//| Layer   : Engine                                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Brain Workspace                                        |
//+------------------------------------------------------------------+

#ifndef CORE_ENGINE_BRAINWORKSPACE_MQH
#define CORE_ENGINE_BRAINWORKSPACE_MQH

#include "../brain/Signal.mqh"
#include "models/BrainPipelineResult.mqh"

//--------------------------------------------------
// Brain Workspace
//--------------------------------------------------

class CBrainWorkspace
{
public:

    string Symbol;

    ENUM_TIMEFRAMES Timeframe;

    //--------------------------------------------------

    CBrainAnalysisResult Analysis;

    //--------------------------------------------------

    CSignal Signal;

    //--------------------------------------------------

    CBrainPipelineResult Result;

public:
    //--------------------------------------------------

    CBrainWorkspace()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        Symbol = "";

        Timeframe = PERIOD_CURRENT;

        Analysis.Reset();

        Signal = CSignal();
        
        Result.Reset();
    }
};

#endif