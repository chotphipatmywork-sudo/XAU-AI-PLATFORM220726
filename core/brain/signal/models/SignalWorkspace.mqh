//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : SignalWorkspace.mqh                                    |
//| Layer   : Brain / Signal / Models                               |
//| Version : 1.0.0                                                  |
//| Purpose : Working Memory for Signal Package                      |
//+------------------------------------------------------------------+

#ifndef CORE_BRAIN_SIGNAL_MODELS_SIGNALWORKSPACE_MQH
#define CORE_BRAIN_SIGNAL_MODELS_SIGNALWORKSPACE_MQH

#include "../../models/BrainAnalysisResult.mqh"
#include "../../Signal.mqh"

//--------------------------------------------------
// Signal Workspace
//--------------------------------------------------

class CSignalWorkspace
{
public:
    //--------------------------------------------------
    // Input
    //--------------------------------------------------

    CBrainAnalysisResult Analysis;

    //--------------------------------------------------
    // Output
    //--------------------------------------------------

    CSignal Signal;

public:
    //--------------------------------------------------

    CSignalWorkspace()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        Analysis.Reset();

        Signal = CSignal();
    }
};

#endif