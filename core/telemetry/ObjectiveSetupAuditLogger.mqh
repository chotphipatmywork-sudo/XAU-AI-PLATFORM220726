//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ObjectiveSetupAuditLogger.mqh                         |
//| Layer   : Core / Telemetry                                      |
//| Version : 1.2.0                                                  |
//| Purpose : Audit CR-017 setup, plan, Risk, and paper result       |
//+------------------------------------------------------------------+

#ifndef XAU_OBJECTIVE_SETUP_AUDIT_MQH
#define XAU_OBJECTIVE_SETUP_AUDIT_MQH

#include "../ai/strategy/models/ObjectiveMultiTimeframeSetupInput.mqh"
#include "../ai/strategy/models/ObjectiveMultiTimeframeSetupEvidence.mqh"
#include "../ai/strategy/models/StructureAwareTradePlan.mqh"
#include "../ai/models/AIDecision.mqh"
#include "../risk/models/RiskResult.mqh"
#include "../execution/models/ExecutionResult.mqh"

class CObjectiveSetupAuditLogger
  {
private:
   string m_fileName;

public:
   CObjectiveSetupAuditLogger()
     {
      m_fileName="XAU_AI_OBJECTIVE_SETUP_AUDIT.csv";
     }

   void SetFileName(const string fileName)
     {
      if(fileName!="")
         m_fileName=fileName;
     }

   bool Write(const CObjectiveMultiTimeframeSetupInput &source,
              const CObjectiveMultiTimeframeSetupEvidence &evidence,
              const CStructureAwareTradePlan &plan,
              const bool planAvailable,
              const string setupReason,
              const CAIDecision &decision,
              const CRiskResult &risk,
              const CExecutionResult &execution)
     {
      const int handle=FileOpen(m_fileName,
         FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ,',');
      if(handle==INVALID_HANDLE)
         return(false);
      if(FileSize(handle)==0)
         FileWrite(handle,
            "recorded_at","observation_time","symbol","higher_bar_open",
            "context_bar_open","entry_bar_open","direction",
            "poi_confirmed","trigger_confirmed","reversal_context_confirmed",
            "reference_poi","nearest_target","structural_stop",
            "sweep_penetration_atr","reclaim_distance_atr",
            "trigger_engulfment_atr","plan_available",
            "plan_entry","plan_stop","plan_target","plan_rr","minimum_rr",
            "estimated_cost_points","setup_reason","ai_action","ai_confidence",
            "risk_valid","risk_allowed","risk_message","execution_success",
            "execution_message","synthetic_ticket");
      FileSeek(handle,0,SEEK_END);
      FileWrite(handle,
         TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),
         TimeToString(source.ObservationTime,TIME_DATE|TIME_MINUTES),
         source.Symbol,
         TimeToString(source.HigherBarOpenTime,TIME_DATE|TIME_MINUTES),
         TimeToString(source.ContextBarOpenTime,TIME_DATE|TIME_MINUTES),
         TimeToString(source.EntryBarOpenTime,TIME_DATE|TIME_MINUTES),
         EnumToString(evidence.Direction),
         evidence.PoiConfirmed ? "true" : "false",
         evidence.TriggerConfirmed ? "true" : "false",
         evidence.ReversalContextConfirmed ? "true" : "false",
         evidence.ReferencePoiPrice,
         evidence.NearestTargetPrice,
         evidence.StructuralStopPrice,
         evidence.SweepPenetrationAtr,
         evidence.ReclaimDistanceAtr,
         evidence.TriggerEngulfmentAtr,
         planAvailable ? "true" : "false",
         plan.EntryPrice,
         plan.StopLossPrice,
         plan.TakeProfitPrice,
         plan.RiskReward,
         plan.MinimumRiskReward,
         plan.EstimatedCostPoints,
         setupReason,
         EnumToString(decision.Action),
         decision.Confidence,
         risk.Valid ? "true" : "false",
         risk.AllowTrade ? "true" : "false",
         risk.Message,
         execution.Success ? "true" : "false",
         execution.Message,
         (long)execution.Ticket);
      FileFlush(handle);
      FileClose(handle);
      return(true);
     }
  };

#endif
