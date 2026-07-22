//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionWorkspace.mqh                                  |
//| Layer   : Decision                                               |
//| Version : 1.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_DECISIONWORKSPACE_MQH
#define CORE_DECISION_DECISIONWORKSPACE_MQH

#include "../engine/models/BrainPipelineResult.mqh"

#include "models/DecisionContext.mqh"
#include "models/DecisionResult.mqh"

//--------------------------------------------------

class CDecisionWorkspace
{
public:
    CBrainPipelineResult Brain;

    CDecisionContext Context;

    CDecisionResult Result;

public:
    CDecisionWorkspace()
    {
        Reset();
    }

    //--------------------------------------------------

    void Reset()
    {
        Brain.Reset();

        Context.Reset();

        Result.Reset();
    }
};

#endif