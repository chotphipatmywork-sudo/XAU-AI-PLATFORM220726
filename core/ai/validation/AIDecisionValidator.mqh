//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : AIDecisionValidator.mqh                                |
//| Layer   : Core / AI / Validation                                 |
//| Version : 1.0.0                                                  |
//| Purpose : Validate AI Decision                                   |
//+------------------------------------------------------------------+

#ifndef CORE_AI_VALIDATION_AIDECISIONVALIDATOR_MQH
#define CORE_AI_VALIDATION_AIDECISIONVALIDATOR_MQH

#include "../models/AIDecision.mqh"

//--------------------------------------------------
// AI Decision Validator
//--------------------------------------------------

class CAIDecisionValidator
{
public:

   //--------------------------------------------------

   bool Validate(
      const CAIDecision &decision) const
   {
      if(decision.Symbol == "")
         return false;

      if(decision.Confidence < 0.0 ||
         decision.Confidence > 100.0)
         return false;

      if(decision.Score < 0.0 ||
         decision.Score > 100.0)
         return false;

      if(decision.Type == AI_DECISION_NONE)
         return false;

      if(decision.Action == AI_ACTION_NONE)
         return false;

      return true;
   }

};

#endif