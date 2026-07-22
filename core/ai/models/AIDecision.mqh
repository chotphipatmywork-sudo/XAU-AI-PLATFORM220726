//+------------------------------------------------------------------+
//| Project : XAU-AI-PLATFORM                                        |
//| File    : AIDecision.mqh                                         |
//| Layer   : AI / Models                                            |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_AIDECISION_MQH
#define CORE_AI_MODELS_AIDECISION_MQH


//--- Decision Type
enum ENUM_AI_DECISION_TYPE
{
   AI_DECISION_NONE = 0,
   AI_DECISION_BUY,
   AI_DECISION_SELL,
   AI_DECISION_CLOSE,
   AI_DECISION_HOLD
};


//--- AI Action
enum ENUM_AI_ACTION
{
   AI_ACTION_NONE = 0,
   AI_ACTION_BUY,
   AI_ACTION_SELL,
   AI_ACTION_CLOSE,
   AI_ACTION_HOLD
};


//--- Decision Source
enum ENUM_AI_DECISION_SOURCE
{
   AI_SOURCE_UNKNOWN = 0,
   AI_SOURCE_MARKET,
   AI_SOURCE_BRAIN,
   AI_SOURCE_SIGNAL_FUSION,
   AI_SOURCE_AI_MODEL
};


//--- AI Decision Model
class CAIDecision
{

public:

   // Core Decision
   ENUM_AI_DECISION_TYPE   Type;
   ENUM_AI_ACTION          Action;
   ENUM_AI_DECISION_SOURCE Source;


   // Market Context
   string                  Symbol;
   ENUM_TIMEFRAMES         Timeframe;
   datetime                Timestamp;


   // Trade Parameters
   double                  EntryPrice;
   double                  StopLoss;
   double                  TakeProfit;


   // AI Evaluation
   double                  Confidence;
   double                  Score;
   double                  Weight;


   // Money / Risk
   double                  RecommendedRisk;


   // Decision Metadata
   string                  Reason;


   // State
   bool                    Valid;


public:


   CAIDecision()
   {
      Reset();
   }


   void Reset()
   {

      Type        = AI_DECISION_NONE;
      Action      = AI_ACTION_NONE;
      Source      = AI_SOURCE_UNKNOWN;


      Symbol      = "";
      Timeframe   = PERIOD_CURRENT;
      Timestamp   = 0;


      EntryPrice  = 0.0;
      StopLoss    = 0.0;
      TakeProfit  = 0.0;


      Confidence        = 0.0;
      Score             = 0.0;
      Weight            = 0.0;


      RecommendedRisk   = 0.0;


      Reason      = "";


      Valid       = false;

   }


   bool IsValid() const
   {
      return Valid;
   }


   void Approve()
   {
      Valid = true;
   }


   void Invalidate()
   {
      Valid = false;
   }

};


#endif
//+------------------------------------------------------------------+