//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : AIDecisionIntentAdapter.mqh                            |
//| Layer   : Core / Decision                                        |
//| Version : 1.0.0                                                  |
//| Purpose : Convert AI Runtime output into trading intent          |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_AIDECISIONINTENTADAPTER_MQH
#define CORE_DECISION_AIDECISIONINTENTADAPTER_MQH

#include "../ai/models/AIDecision.mqh"
#include "models/DecisionResult.mqh"

class CAIDecisionIntentAdapter
  {
public:
   CDecisionResult Convert(const CAIDecision &aiDecision)
     {
      CDecisionResult result;
      if(!aiDecision.Valid)
         return(result);

      if(aiDecision.Action==AI_ACTION_BUY ||
         aiDecision.Type==AI_DECISION_BUY)
         result.Decision=DECISION_BUY;
      else if(aiDecision.Action==AI_ACTION_SELL ||
              aiDecision.Type==AI_DECISION_SELL)
         result.Decision=DECISION_SELL;
      else
         result.Decision=DECISION_WAIT;

      result.Confidence=aiDecision.Confidence;
      result.Valid=true;
      return(result);
     }
  };

#endif
