//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DecisionResult.mqh                                     |
//| Layer   : Core / Decision / Models                               |
//| Version : 2.0.0                                                  |
//| Purpose : Final AI Decision Result                               |
//+------------------------------------------------------------------+

#ifndef CORE_DECISION_MODELS_DECISIONRESULT_MQH
#define CORE_DECISION_MODELS_DECISIONRESULT_MQH

//--------------------------------------------------
// Decision Type
//--------------------------------------------------

enum ENUM_DECISION
{
   DECISION_NONE = 0,

   DECISION_BUY,

   DECISION_SELL,

   DECISION_WAIT
};

//--------------------------------------------------
// Decision Result
//--------------------------------------------------

class CDecisionResult
{
public:

   ENUM_DECISION Decision;

   double Confidence;

   bool Valid;

   //--------------------------------------------------

   CDecisionResult()
   {
      Reset();
   }

   //--------------------------------------------------

   void Reset()
   {
      Decision = DECISION_NONE;

      Confidence = 0.0;

      Valid = false;
   }
};

#endif