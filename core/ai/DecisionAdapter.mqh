//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : DecisionAdapter.mqh                                    |
//| Layer   : Core / AI                                              |
//| Version : 3.0.0                                                  |
//| Purpose : Brain Result -> AI Decision Adapter                    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_DECISIONADAPTER_MQH
#define CORE_AI_DECISIONADAPTER_MQH

#include "../brain/models/BrainAnalysisResult.mqh"
#include "models/AIDecision.mqh"

//--------------------------------------------------

class CDecisionAdapter
{
public:

   CAIDecision Convert(
      const CBrainAnalysisResult &analysis)
   {
      CAIDecision decision;

      decision.Reset();

      if(!analysis.Valid)
         return decision;

      //--------------------------------------------------
      // Placeholder
      // Future AI Logic will map Brain Result
      // into BUY / SELL / HOLD
      //--------------------------------------------------

      decision.Type   = AI_DECISION_HOLD;
      decision.Action = AI_ACTION_HOLD;

      decision.Approve();

      return decision;
   }
};

#endif