//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : BrainPipelineResult.mqh                                |
//| Layer   : Engine                                                 |
//| Version : 2.0.0                                                  |
//| Purpose : Brain Pipeline Result                                  |
//+------------------------------------------------------------------+

#ifndef CORE_ENGINE_MODELS_BRAINPIPELINERESULT_MQH
#define CORE_ENGINE_MODELS_BRAINPIPELINERESULT_MQH

#include "../../brain/Signal.mqh"
#include "../../brain/models/BrainAnalysisResult.mqh"

//--------------------------------------------------
// Brain Pipeline Result
//--------------------------------------------------

class CBrainPipelineResult
{
public:

    bool Valid;

    CBrainAnalysisResult Analysis;

    CSignal Signal;

public:

    //--------------------------------------------------

    CBrainPipelineResult()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        Valid = false;

        Analysis.Reset();

        Signal = CSignal();
    }
};

#endif