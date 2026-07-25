//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ObjectiveMultiTimeframeSetupAdapter.mqh                |
//| Layer   : Core / AI / Strategy                                   |
//| Version : 1.3.0                                                  |
//| Purpose : Causal M15/M5 reversal-context objective setup         |
//+------------------------------------------------------------------+

#ifndef XAU_OBJECTIVE_MTF_ADAPTER_MQH
#define XAU_OBJECTIVE_MTF_ADAPTER_MQH

#include "models/ObjectiveMultiTimeframeSetupInput.mqh"
#include "models/ObjectiveHybridSetupConfig.mqh"
#include "models/ObjectiveMultiTimeframeSetupEvidence.mqh"
#include "models/HybridRuleSetupContext.mqh"

class CObjectiveMultiTimeframeSetupAdapter
  {
private:
   CObjectiveHybridSetupConfig m_config;

   bool Reject(CHybridRuleSetupContext &context,
               CObjectiveMultiTimeframeSetupEvidence &evidence,
               const string reason) const
     {
      context.Reset();
      evidence.Reset();
      evidence.Reason=reason;
      return(false);
     }

   bool ValidScore(const double value) const
     {
      return(MathIsValidNumber(value) && value>=0.0 && value<=100.0);
     }

   bool ValidBar(const double openPrice,
                 const double highPrice,
                 const double lowPrice,
                 const double closePrice) const
     {
      if(!MathIsValidNumber(openPrice) ||
         !MathIsValidNumber(highPrice) ||
         !MathIsValidNumber(lowPrice) ||
         !MathIsValidNumber(closePrice) ||
         openPrice<=0.0 || highPrice<=0.0 ||
         lowPrice<=0.0 || closePrice<=0.0)
         return(false);

      return(highPrice>=openPrice &&
             highPrice>=closePrice &&
             highPrice>=lowPrice &&
             lowPrice<=openPrice &&
             lowPrice<=closePrice);
     }

   ENUM_TRADE_SETUP_DIRECTION AlignedDirection(
      const CTrendResult &trend) const
     {
      if(!trend.Valid)
         return(TRADE_SETUP_NONE);

      if(trend.Direction==TREND_BULLISH &&
         trend.AITrendRegime>=m_config.BullishMinimum &&
         trend.AITrendMomentum>=m_config.BullishMinimum &&
         trend.AITrendSlope>=m_config.BullishMinimum)
         return(TRADE_SETUP_BUY);

      if(trend.Direction==TREND_BEARISH &&
         trend.AITrendRegime<=m_config.BearishMaximum &&
         trend.AITrendMomentum<=m_config.BearishMaximum &&
         trend.AITrendSlope<=m_config.BearishMaximum)
         return(TRADE_SETUP_SELL);

      return(TRADE_SETUP_NONE);
     }

public:
   bool SetConfig(const CObjectiveHybridSetupConfig &config)
     {
      if(!config.Valid())
         return(false);

      m_config.BullishMinimum=config.BullishMinimum;
      m_config.BearishMaximum=config.BearishMaximum;
      m_config.PoiTolerancePoints=config.PoiTolerancePoints;
      m_config.PoiToleranceAtrFraction=config.PoiToleranceAtrFraction;
      m_config.SweepPenetrationPoints=config.SweepPenetrationPoints;
      m_config.SweepPenetrationAtrFraction=
         config.SweepPenetrationAtrFraction;
      m_config.MinimumReclaimAtr=config.MinimumReclaimAtr;
      m_config.StopBufferAtrFraction=config.StopBufferAtrFraction;
      return(true);
     }

   bool Project(const CObjectiveMultiTimeframeSetupInput &source,
                CHybridRuleSetupContext &context,
                CObjectiveMultiTimeframeSetupEvidence &evidence) const
     {
      context.Reset();
      evidence.Reset();

      if(!m_config.Valid())
         return(Reject(context,evidence,"Objective setup configuration is invalid."));

      if(source.Symbol=="" || source.HigherTimeframe!=PERIOD_M15 ||
         source.EntryTimeframe!=PERIOD_M5)
         return(Reject(context,evidence,
                       "Objective setup requires explicit M15 and M5 timeframes."));

      if(source.ObservationTime<=0 || source.HigherBarOpenTime<=0 ||
         source.ContextBarOpenTime<=0 ||
         source.EntryBarOpenTime<=0 ||
         source.HigherTrendKnownTime<=0 ||
         source.EntryStructureKnownTime<=0 ||
         source.HigherBarOpenTime+900!=source.ObservationTime ||
         source.ContextBarOpenTime+600!=source.ObservationTime ||
         source.EntryBarOpenTime+300!=source.ObservationTime ||
         source.ContextBarOpenTime+300!=source.EntryBarOpenTime)
         return(Reject(context,evidence,
                       "Objective setup requires synchronized M15 and causal context/trigger M5 bars."));

      if(source.HigherTrendKnownTime!=source.ObservationTime ||
         source.EntryStructureKnownTime!=source.ObservationTime)
         return(Reject(context,evidence,
                       "Objective setup contains future-known or stale timing evidence."));

      if(!ValidBar(source.ContextOpen,source.ContextHigh,
                   source.ContextLow,source.ContextClose) ||
         !ValidBar(source.EntryOpen,source.EntryHigh,
                   source.EntryLow,source.EntryClose) ||
         !MathIsValidNumber(source.EntryAtr) ||
         !MathIsValidNumber(source.Point) ||
         !MathIsValidNumber(source.EstimatedCostPoints) ||
         !MathIsValidNumber(source.MinimumRiskReward) ||
         source.EntryAtr<=0.0 || source.Point<=0.0 ||
         source.EstimatedCostPoints<0.0 || source.MinimumRiskReward<=0.0)
         return(Reject(context,evidence,
                       "Objective setup contains invalid M5 price, ATR, point, cost, or RR data."));

      if(source.HigherTrend.Valid &&
         (!ValidScore(source.HigherTrend.AITrendRegime) ||
          !ValidScore(source.HigherTrend.AITrendMomentum) ||
          !ValidScore(source.HigherTrend.AITrendSlope)))
         return(Reject(context,evidence,
                       "Objective setup contains invalid M15 Trend components."));

      if(source.EntryStructure.Valid &&
         (!MathIsValidNumber(source.EntryStructure.LatestSwingHigh) ||
          !MathIsValidNumber(source.EntryStructure.LatestSwingLow) ||
          source.EntryStructure.LatestSwingHigh<=0.0 ||
          source.EntryStructure.LatestSwingLow<=0.0 ||
          source.EntryStructure.LatestSwingHigh<=
          source.EntryStructure.LatestSwingLow))
         return(Reject(context,evidence,
                       "Objective setup contains invalid confirmed M5 swing geometry."));

      context.Symbol=source.Symbol;
      context.ExecutionTimeframe=source.EntryTimeframe;
      context.ClosedBarTime=source.ObservationTime;
      context.ClosedBarConfirmed=true;
      context.EntryPrice=source.EntryClose;
      context.Point=source.Point;
      context.EstimatedCostPoints=source.EstimatedCostPoints;
      context.MinimumRiskReward=source.MinimumRiskReward;

      evidence.ValidObservation=true;
      evidence.Direction=AlignedDirection(source.HigherTrend);
      context.Direction=evidence.Direction;
      context.HigherTimeframeTrendAligned=
         (evidence.Direction==TRADE_SETUP_BUY ||
          evidence.Direction==TRADE_SETUP_SELL);

      if(!context.HigherTimeframeTrendAligned)
        {
         evidence.Reason="Objective observation is valid but M15 Trend is not aligned.";
         return(true);
        }

      if(!source.EntryStructure.Valid)
        {
         evidence.Reason="Objective observation is valid but confirmed M5 structure is unavailable.";
         return(true);
        }

      const double zoneTolerance=
         MathMax(m_config.PoiTolerancePoints*source.Point,
                 m_config.PoiToleranceAtrFraction*source.EntryAtr);
      const double sweepTolerance=
         MathMax(m_config.SweepPenetrationPoints*source.Point,
                 m_config.SweepPenetrationAtrFraction*source.EntryAtr);
      const double stopBuffer=
         MathMax(m_config.StopBufferAtrFraction*source.EntryAtr,
                 source.EstimatedCostPoints*source.Point);

      evidence.ZoneTolerancePrice=zoneTolerance;
      evidence.SweepTolerancePrice=sweepTolerance;

      if(evidence.Direction==TRADE_SETUP_BUY)
        {
         evidence.ReferencePoiPrice=source.EntryStructure.LatestSwingLow;
         evidence.NearestTargetPrice=source.EntryStructure.LatestSwingHigh;
         evidence.PoiConfirmed=
            (source.EntryLow<=evidence.ReferencePoiPrice+zoneTolerance &&
             source.EntryHigh>=evidence.ReferencePoiPrice-zoneTolerance);
         evidence.SweepPenetrationAtr=
            MathMax(0.0,(evidence.ReferencePoiPrice-source.EntryLow)/source.EntryAtr);
         evidence.ReclaimDistanceAtr=
            MathMax(0.0,(source.EntryClose-evidence.ReferencePoiPrice)/source.EntryAtr);
         evidence.TriggerConfirmed=
            (evidence.PoiConfirmed &&
             source.EntryLow<evidence.ReferencePoiPrice-sweepTolerance &&
             source.EntryClose>evidence.ReferencePoiPrice &&
             source.EntryClose>source.EntryOpen &&
             evidence.ReclaimDistanceAtr+0.000000001>=m_config.MinimumReclaimAtr);
         evidence.TriggerEngulfmentAtr=
            MathMax(0.0,(source.EntryClose-source.ContextOpen)/source.EntryAtr);
         evidence.ReversalContextConfirmed=
            (evidence.TriggerConfirmed &&
             source.ContextClose<source.ContextOpen &&
             source.EntryClose>source.ContextOpen);
         evidence.StructuralStopPrice=source.EntryLow-stopBuffer;
        }
      else
        {
         evidence.ReferencePoiPrice=source.EntryStructure.LatestSwingHigh;
         evidence.NearestTargetPrice=source.EntryStructure.LatestSwingLow;
         evidence.PoiConfirmed=
            (source.EntryHigh>=evidence.ReferencePoiPrice-zoneTolerance &&
             source.EntryLow<=evidence.ReferencePoiPrice+zoneTolerance);
         evidence.SweepPenetrationAtr=
            MathMax(0.0,(source.EntryHigh-evidence.ReferencePoiPrice)/source.EntryAtr);
         evidence.ReclaimDistanceAtr=
            MathMax(0.0,(evidence.ReferencePoiPrice-source.EntryClose)/source.EntryAtr);
         evidence.TriggerConfirmed=
            (evidence.PoiConfirmed &&
             source.EntryHigh>evidence.ReferencePoiPrice+sweepTolerance &&
             source.EntryClose<evidence.ReferencePoiPrice &&
             source.EntryClose<source.EntryOpen &&
             evidence.ReclaimDistanceAtr+0.000000001>=m_config.MinimumReclaimAtr);
         evidence.TriggerEngulfmentAtr=
            MathMax(0.0,(source.ContextOpen-source.EntryClose)/source.EntryAtr);
         evidence.ReversalContextConfirmed=
            (evidence.TriggerConfirmed &&
             source.ContextClose>source.ContextOpen &&
             source.EntryClose<source.ContextOpen);
         evidence.StructuralStopPrice=source.EntryHigh+stopBuffer;
        }

      context.PointOfInterestConfirmed=evidence.PoiConfirmed;
      context.EntryTriggerConfirmed=
         (evidence.TriggerConfirmed && evidence.ReversalContextConfirmed);
      context.StructuralStopPrice=evidence.StructuralStopPrice;
      context.NearestStructuralTargetPrice=evidence.NearestTargetPrice;

      if(!evidence.PoiConfirmed)
         evidence.Reason="Objective observation is valid but M5 POI is not confirmed.";
      else if(!evidence.TriggerConfirmed)
         evidence.Reason="Objective observation is valid but M5 sweep/reclaim trigger is incomplete.";
      else if(!evidence.ReversalContextConfirmed)
         evidence.Reason="Objective M5 trigger is valid but reversal context failed.";
      else
         evidence.Reason="Objective M15/M5 reversal-context evidence projected; Risk approval remains required.";

      return(true);
     }
  };

#endif
