//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TradeSetupCandidate.mqh                                |
//| Layer   : Core / AI / Strategy / Models                          |
//| Version : 1.0.0                                                  |
//| Purpose : Accepted directional setup evidence                    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STRATEGY_MODELS_TRADESETUPCANDIDATE_MQH
#define CORE_AI_STRATEGY_MODELS_TRADESETUPCANDIDATE_MQH

#include "HybridRuleSetupContext.mqh"

class CTradeSetupCandidate
  {
public:
   string                     Symbol;
   ENUM_TIMEFRAMES            ExecutionTimeframe;
   datetime                   ClosedBarTime;
   ENUM_TRADE_SETUP_DIRECTION Direction;

   double                     EntryPrice;
   double                     StructuralStopPrice;
   double                     NearestStructuralTargetPrice;
   double                     Point;
   double                     EstimatedCostPoints;
   double                     MinimumRiskReward;

   string                     Reason;
   bool                       Valid;

   CTradeSetupCandidate()
     {
      Reset();
     }

   void Reset()
     {
      Symbol="";
      ExecutionTimeframe=PERIOD_CURRENT;
      ClosedBarTime=0;
      Direction=TRADE_SETUP_NONE;

      EntryPrice=0.0;
      StructuralStopPrice=0.0;
      NearestStructuralTargetPrice=0.0;
      Point=0.0;
      EstimatedCostPoints=0.0;
      MinimumRiskReward=0.0;

      Reason="";
      Valid=false;
     }
  };

#endif

