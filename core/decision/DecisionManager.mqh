//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionManager.mqh                                    |
//| Layer   : Decision                                               |
//| Version : 1.1.0                                                  |
//| Purpose : Decision Manager                                       |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_DECISIONMANAGER_MQH
#define CORE_DECISION_DECISIONMANAGER_MQH

#include "DecisionEngine.mqh"

//--------------------------------------------------
// Decision Manager
//--------------------------------------------------

class CDecisionManager
{
private:
    CDecisionEngine m_engine;

public:
    //--------------------------------------------------

    CDecisionResult Analyze(const CDecisionContext &context)
    {
        return m_engine.Evaluate(context);
    }
};

#endif
