//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HybridRuleSetupContext.mqh                             |
//| Layer   : Core / AI / Strategy / Models                          |
//| Version : 1.0.0                                                  |
//| Purpose : Closed-bar inputs for bounded hybrid setup research    |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STRATEGY_MODELS_HYBRIDRULESETUPCONTEXT_MQH
#define CORE_AI_STRATEGY_MODELS_HYBRIDRULESETUPCONTEXT_MQH

enum ENUM_TRADE_SETUP_DIRECTION
  {
   TRADE_SETUP_NONE=0,
   TRADE_SETUP_BUY,
   TRADE_SETUP_SELL
  };

class CHybridRuleSetupContext
  {
public:
   string                     Symbol;
   ENUM_TIMEFRAMES            ExecutionTimeframe;
   datetime                   ClosedBarTime;
   ENUM_TRADE_SETUP_DIRECTION Direction;

   bool                       ClosedBarConfirmed;
   bool                       HigherTimeframeTrendAligned;
   bool                       PointOfInterestConfirmed;
   bool                       EntryTriggerConfirmed;

   double                     EntryPrice;
   double                     StructuralStopPrice;
   double                     NearestStructuralTargetPrice;
   double                     Point;
   double                     EstimatedCostPoints;
   double                     MinimumRiskReward;

   CHybridRuleSetupContext()
     {
      Reset();
     }

   void Reset()
     {
      Symbol="";
      ExecutionTimeframe=PERIOD_CURRENT;
      ClosedBarTime=0;
      Direction=TRADE_SETUP_NONE;

      ClosedBarConfirmed=false;
      HigherTimeframeTrendAligned=false;
      PointOfInterestConfirmed=false;
      EntryTriggerConfirmed=false;

      EntryPrice=0.0;
      StructuralStopPrice=0.0;
      NearestStructuralTargetPrice=0.0;
      Point=0.0;
      EstimatedCostPoints=0.0;
      MinimumRiskReward=2.0;
     }
  };

#endif

