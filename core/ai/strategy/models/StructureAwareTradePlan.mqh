//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : StructureAwareTradePlan.mqh                            |
//| Layer   : Core / AI / Strategy / Models                          |
//| Version : 1.0.0                                                  |
//| Purpose : Auditable structural Entry, Stop, Target, and RR plan  |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STRATEGY_MODELS_STRUCTUREAWARETRADEPLAN_MQH
#define CORE_AI_STRATEGY_MODELS_STRUCTUREAWARETRADEPLAN_MQH

#include "HybridRuleSetupContext.mqh"

class CStructureAwareTradePlan
  {
public:
   string                     Symbol;
   ENUM_TIMEFRAMES            ExecutionTimeframe;
   datetime                   ClosedBarTime;
   ENUM_TRADE_SETUP_DIRECTION Direction;

   double                     EntryPrice;
   double                     StopLossPrice;
   double                     TakeProfitPrice;

   double                     GrossRiskPoints;
   double                     GrossRewardPoints;
   double                     EstimatedCostPoints;
   double                     EffectiveRiskPoints;
   double                     NetRewardPoints;
   double                     RiskReward;
   double                     MinimumRiskReward;

   string                     Reason;
   bool                       Valid;

   CStructureAwareTradePlan()
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
      StopLossPrice=0.0;
      TakeProfitPrice=0.0;

      GrossRiskPoints=0.0;
      GrossRewardPoints=0.0;
      EstimatedCostPoints=0.0;
      EffectiveRiskPoints=0.0;
      NetRewardPoints=0.0;
      RiskReward=0.0;
      MinimumRiskReward=0.0;

      Reason="";
      Valid=false;
     }
  };

#endif

