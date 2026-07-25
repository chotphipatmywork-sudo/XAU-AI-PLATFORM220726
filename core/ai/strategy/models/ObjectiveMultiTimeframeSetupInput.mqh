//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ObjectiveMultiTimeframeSetupInput.mqh                  |
//| Layer   : Core / AI / Strategy / Models                          |
//| Version : 1.2.0                                                  |
//| Purpose : Explicit M15 and causal context/trigger M5 input       |
//+------------------------------------------------------------------+

#ifndef XAU_OBJECTIVE_MTF_INPUT_MQH
#define XAU_OBJECTIVE_MTF_INPUT_MQH

#include "../../../brain/trend/models/TrendResult.mqh"
#include "../../../brain/trend/models/ConfirmedSwingStructureResult.mqh"

class CObjectiveMultiTimeframeSetupInput
  {
public:
   string                         Symbol;
   ENUM_TIMEFRAMES                HigherTimeframe;
   ENUM_TIMEFRAMES                EntryTimeframe;
   datetime                       ObservationTime;
   datetime                       HigherBarOpenTime;
   datetime                       ContextBarOpenTime;
   datetime                       EntryBarOpenTime;
   datetime                       HigherTrendKnownTime;
   datetime                       EntryStructureKnownTime;

   CTrendResult                   HigherTrend;
   CConfirmedSwingStructureResult EntryStructure;

   double                         ContextOpen;
   double                         ContextHigh;
   double                         ContextLow;
   double                         ContextClose;
   double                         EntryOpen;
   double                         EntryHigh;
   double                         EntryLow;
   double                         EntryClose;
   double                         EntryAtr;
   double                         Point;
   double                         EstimatedCostPoints;
   double                         MinimumRiskReward;

   CObjectiveMultiTimeframeSetupInput()
     {
      Reset();
     }

   void Reset()
     {
      Symbol="";
      HigherTimeframe=PERIOD_CURRENT;
      EntryTimeframe=PERIOD_CURRENT;
      ObservationTime=0;
      HigherBarOpenTime=0;
      ContextBarOpenTime=0;
      EntryBarOpenTime=0;
      HigherTrendKnownTime=0;
      EntryStructureKnownTime=0;

      HigherTrend.Reset();
      EntryStructure.Reset();

      ContextOpen=0.0;
      ContextHigh=0.0;
      ContextLow=0.0;
      ContextClose=0.0;
      EntryOpen=0.0;
      EntryHigh=0.0;
      EntryLow=0.0;
      EntryClose=0.0;
      EntryAtr=0.0;
      Point=0.0;
      EstimatedCostPoints=0.0;
      MinimumRiskReward=2.0;
     }

   void SetHigherTrend(const CTrendResult &source)
     {
      HigherTrend.Direction=source.Direction;
      HigherTrend.Strength=source.Strength;
      HigherTrend.AITrendScore=source.AITrendScore;
      HigherTrend.AITrendRegime=source.AITrendRegime;
      HigherTrend.AITrendMomentum=source.AITrendMomentum;
      HigherTrend.AITrendSlope=source.AITrendSlope;
      HigherTrend.Confidence=source.Confidence;
      HigherTrend.Valid=source.Valid;
     }

   void SetEntryStructure(const CConfirmedSwingStructureResult &source)
     {
      EntryStructure.Valid=source.Valid;
      EntryStructure.StructureDirection=source.StructureDirection;
      EntryStructure.BreakDirection=source.BreakDirection;
      EntryStructure.ChochDirection=source.ChochDirection;
      EntryStructure.RangePosition=source.RangePosition;
      EntryStructure.LatestSwingHigh=source.LatestSwingHigh;
      EntryStructure.LatestSwingLow=source.LatestSwingLow;
     }
  };

#endif
