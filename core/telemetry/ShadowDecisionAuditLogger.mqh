//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowDecisionAuditLogger.mqh                          |
//| Layer   : Core / Telemetry                                       |
//| Version : 2.1.0                                                  |
//| Purpose : Schema 4.0 one-row-per-bar Shadow decision evidence    |
//+------------------------------------------------------------------+

#ifndef CORE_TELEMETRY_SHADOWDECISIONAUDITLOGGER_MQH
#define CORE_TELEMETRY_SHADOWDECISIONAUDITLOGGER_MQH

#include "../ai/models/AIDecision.mqh"
#include "../decision/models/DecisionResult.mqh"
#include "../risk/models/RiskResult.mqh"
#include "../execution/models/ExecutionResult.mqh"
#include "../ai/inference/models/AIInferenceRequest.mqh"

class CShadowDecisionAuditLogger
  {
private:
   string m_fileName;

public:
   CShadowDecisionAuditLogger()
     {
      m_fileName="XAU_AI_SHADOW_DECISIONS_V4.csv";
     }

   void SetFileName(const string fileName)
     {
      if(fileName!="")
         m_fileName=fileName;
     }

   bool Write(const datetime closedBar,
              const string symbol,
              const ENUM_TIMEFRAMES timeframe,
              const string featureSchemaVersion,
              const string inferenceProvider,
              const string modelStatus,
              const bool modelDeploymentAuthorized,
              const CAIInferenceRequest &request,
              const double barOpen,
              const double barHigh,
              const double barLow,
              const double barClose,
              const double atr,
              const CAIDecision &aiDecision,
              const CDecisionResult &intent,
              const CRiskResult &risk,
              const CExecutionResult &execution)
     {
      const int handle=FileOpen(m_fileName,
                                FILE_READ|FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_SHARE_READ,
                                ',');
      if(handle==INVALID_HANDLE)
         return(false);
      if(FileSize(handle)==0)
         FileWrite(handle,
                   "recorded_at","closed_bar","symbol","timeframe",
                   "feature_schema_version","inference_provider",
                   "model_status","model_deployment_authorized",
                   "bar_open","bar_high","bar_low","bar_close","atr",
                   "trend_regime","trend_momentum","trend_slope",
                   "volatility_regime","volatility_change",
                   "liquidity_activity","liquidity_range_position",
                   "liquidity_sweep_direction","session_asia","session_london",
                   "session_new_york","session_progress",
                   "legacy_trend_score","legacy_volatility_score",
                   "legacy_liquidity_score","legacy_session_score",
                   "ai_action","ai_confidence","decision","risk_valid","risk_allowed",
                   "risk_score","risk_message","execution_success","execution_status",
                   "execution_message","synthetic_ticket");
      FileSeek(handle,0,SEEK_END);
      FileWrite(handle,
                TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),
                TimeToString(closedBar,TIME_DATE|TIME_MINUTES),
                symbol,
                EnumToString(timeframe),
                featureSchemaVersion,
                inferenceProvider,
                modelStatus,
                modelDeploymentAuthorized ? "true" : "false",
                barOpen,
                barHigh,
                barLow,
                barClose,
                atr,
                request.Features.TrendRegime,
                request.Features.TrendMomentum,
                request.Features.TrendSlope,
                request.Features.VolatilityRegime,
                request.Features.VolatilityChange,
                request.Features.LiquidityActivity,
                request.Features.LiquidityRangePosition,
                request.Features.LiquiditySweepDirection,
                request.Features.SessionAsia,
                request.Features.SessionLondon,
                request.Features.SessionNewYork,
                request.Features.SessionProgress,
                request.LegacyTrendScore,
                request.LegacyVolatilityScore,
                request.LegacyLiquidityScore,
                request.LegacySessionScore,
                EnumToString(aiDecision.Action),
                aiDecision.Confidence,
                EnumToString(intent.Decision),
                risk.Valid ? "true" : "false",
                risk.AllowTrade ? "true" : "false",
                risk.Score,
                risk.Message,
                execution.Success ? "true" : "false",
                EnumToString(execution.Status),
                execution.Message,
                (long)execution.Ticket);
      FileFlush(handle);
      FileClose(handle);
      return(true);
     }
  };

#endif
