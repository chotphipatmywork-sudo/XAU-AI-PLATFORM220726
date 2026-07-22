//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionAssembler.mqh                                  |
//| Layer   : Decision                                               |
//| Version : 1.0.0                                                  |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_DECISIONASSEMBLER_MQH
#define CORE_DECISION_DECISIONASSEMBLER_MQH

#include "models/DecisionResult.mqh"

//--------------------------------------------------

class CDecisionAssembler
{
public:
    CDecisionResult Assemble(
        const CDecisionResult &result)
    {
        return result;
    }
};

#endif