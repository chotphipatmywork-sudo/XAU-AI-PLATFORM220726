//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : HybridRuleSetupEngine.mqh                              |
//| Layer   : Core / AI / Strategy                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Accept complete closed-bar hybrid setup confluence     |
//+------------------------------------------------------------------+

#ifndef CORE_AI_STRATEGY_HYBRIDRULESETUPENGINE_MQH
#define CORE_AI_STRATEGY_HYBRIDRULESETUPENGINE_MQH

#include "models/HybridRuleSetupContext.mqh"
#include "models/TradeSetupCandidate.mqh"

class CHybridRuleSetupEngine
  {
private:
   bool Reject(CTradeSetupCandidate &candidate,
               const string reason) const
     {
      candidate.Reset();
      candidate.Reason=reason;
      return(false);
     }

public:
   bool Build(const CHybridRuleSetupContext &context,
              CTradeSetupCandidate &candidate) const
     {
      candidate.Reset();

      if(context.Symbol=="" || context.ExecutionTimeframe==PERIOD_CURRENT)
         return(Reject(candidate,"Setup requires an explicit symbol and timeframe."));

      if(!context.ClosedBarConfirmed || context.ClosedBarTime<=0)
         return(Reject(candidate,"Setup requires confirmed closed-bar timing."));

      if(context.Direction!=TRADE_SETUP_BUY &&
         context.Direction!=TRADE_SETUP_SELL)
         return(Reject(candidate,"Setup direction must be BUY or SELL."));

      if(!context.HigherTimeframeTrendAligned)
         return(Reject(candidate,"Setup rejected: higher-timeframe Trend is not aligned."));

      if(!context.PointOfInterestConfirmed)
         return(Reject(candidate,"Setup rejected: Point of Interest is not confirmed."));

      if(!context.EntryTriggerConfirmed)
         return(Reject(candidate,"Setup rejected: entry trigger is not confirmed."));

      if(!MathIsValidNumber(context.EntryPrice) ||
         !MathIsValidNumber(context.StructuralStopPrice) ||
         !MathIsValidNumber(context.NearestStructuralTargetPrice) ||
         !MathIsValidNumber(context.Point) ||
         !MathIsValidNumber(context.EstimatedCostPoints) ||
         !MathIsValidNumber(context.MinimumRiskReward) ||
         context.EntryPrice<=0.0 || context.StructuralStopPrice<=0.0 ||
         context.NearestStructuralTargetPrice<=0.0 || context.Point<=0.0 ||
         context.EstimatedCostPoints<0.0 || context.MinimumRiskReward<=0.0)
         return(Reject(candidate,"Setup contains invalid price or planning values."));

      const bool buyGeometry=
         (context.Direction==TRADE_SETUP_BUY &&
          context.StructuralStopPrice<context.EntryPrice &&
          context.NearestStructuralTargetPrice>context.EntryPrice);
      const bool sellGeometry=
         (context.Direction==TRADE_SETUP_SELL &&
          context.StructuralStopPrice>context.EntryPrice &&
          context.NearestStructuralTargetPrice<context.EntryPrice);

      if(!buyGeometry && !sellGeometry)
         return(Reject(candidate,"Setup structural Stop or Target geometry is invalid."));

      candidate.Symbol=context.Symbol;
      candidate.ExecutionTimeframe=context.ExecutionTimeframe;
      candidate.ClosedBarTime=context.ClosedBarTime;
      candidate.Direction=context.Direction;
      candidate.EntryPrice=context.EntryPrice;
      candidate.StructuralStopPrice=context.StructuralStopPrice;
      candidate.NearestStructuralTargetPrice=
         context.NearestStructuralTargetPrice;
      candidate.Point=context.Point;
      candidate.EstimatedCostPoints=context.EstimatedCostPoints;
      candidate.MinimumRiskReward=context.MinimumRiskReward;
      candidate.Reason="Hybrid rule setup candidate accepted.";
      candidate.Valid=true;
      return(true);
     }
  };

#endif

