//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ObjectiveMultiTimeframeSetupEvidence.mqh               |
//| Layer   : Core / AI / Strategy / Models                          |
//| Version : 1.2.0                                                  |
//| Purpose : Auditable M15/M5 reversal-context setup evidence       |
//+------------------------------------------------------------------+

#ifndef XAU_OBJECTIVE_MTF_EVIDENCE_MQH
#define XAU_OBJECTIVE_MTF_EVIDENCE_MQH

#include "HybridRuleSetupContext.mqh"

class CObjectiveMultiTimeframeSetupEvidence
  {
public:
   bool                       ValidObservation;
   bool                       PoiConfirmed;
   bool                       TriggerConfirmed;
   bool                       ReversalContextConfirmed;
   ENUM_TRADE_SETUP_DIRECTION Direction;
   double                     ReferencePoiPrice;
   double                     NearestTargetPrice;
   double                     ZoneTolerancePrice;
   double                     SweepTolerancePrice;
   double                     SweepPenetrationAtr;
   double                     ReclaimDistanceAtr;
   double                     TriggerEngulfmentAtr;
   double                     StructuralStopPrice;
   string                     Reason;

   CObjectiveMultiTimeframeSetupEvidence()
     {
      Reset();
     }

   void Reset()
     {
      ValidObservation=false;
      PoiConfirmed=false;
      TriggerConfirmed=false;
      ReversalContextConfirmed=false;
      Direction=TRADE_SETUP_NONE;
      ReferencePoiPrice=0.0;
      NearestTargetPrice=0.0;
      ZoneTolerancePrice=0.0;
      SweepTolerancePrice=0.0;
      SweepPenetrationAtr=0.0;
      ReclaimDistanceAtr=0.0;
      TriggerEngulfmentAtr=0.0;
      StructuralStopPrice=0.0;
      Reason="";
     }
  };

#endif
