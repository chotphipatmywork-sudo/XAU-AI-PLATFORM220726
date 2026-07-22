//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ShadowRuntimeConfig.mqh                                |
//| Layer   : Core / Runtime / Models                                |
//| Version : 1.6.0                                                  |
//| Purpose : Complete safe Shadow Runtime configuration             |
//+------------------------------------------------------------------+

#ifndef CORE_RUNTIME_MODELS_SHADOWRUNTIMECONFIG_MQH
#define CORE_RUNTIME_MODELS_SHADOWRUNTIMECONFIG_MQH

#include "../../execution/shadow/ShadowExecutionConfig.mqh"
#include "../../ai/inference/models/ShadowInferenceProviderMode.mqh"

class CShadowRuntimeConfig
  {
public:
   CShadowExecutionConfig Execution;
   double                 MaximumDailyLossPoints;
   double                 MaximumDrawdownPoints;
   int                    MaximumMarketAgeSeconds;
   int                    MaximumDecisionLagSeconds;
   string                 DecisionAuditFile;
   string                 TelemetryFile;
   string                 ObjectiveSetupAuditFile;
   bool                   UsePersistentCheckpoint;
   ENUM_SHADOW_INFERENCE_PROVIDER InferenceProvider;
   double                 ObjectiveMinimumRiskReward;

   CShadowRuntimeConfig()
     {
      MaximumDailyLossPoints=2000.0;
      MaximumDrawdownPoints=3000.0;
      MaximumMarketAgeSeconds=120;
      MaximumDecisionLagSeconds=120;
      DecisionAuditFile="XAU_AI_SHADOW_DECISIONS_V4.csv";
      TelemetryFile="XAU_AI_SHADOW_TELEMETRY.csv";
      ObjectiveSetupAuditFile="XAU_AI_OBJECTIVE_SETUP_AUDIT.csv";
      UsePersistentCheckpoint=true;
      InferenceProvider=SHADOW_INFERENCE_LEGACY_LOCKED;
      ObjectiveMinimumRiskReward=2.0;
     }

   bool InferenceProviderAllowed(const bool testerMode) const
     {
      if(InferenceProvider==SHADOW_INFERENCE_LEGACY_LOCKED)
         return(true);
      return(testerMode &&
             (InferenceProvider==SHADOW_INFERENCE_DIRECTIONAL_RESEARCH ||
              InferenceProvider==SHADOW_INFERENCE_SIMPLE_TREND_BASELINE ||
              InferenceProvider==SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP));
     }

   bool Valid() const
     {
      return(Execution.Valid() &&
             MaximumDailyLossPoints>0.0 &&
             MaximumDrawdownPoints>0.0 &&
             MaximumMarketAgeSeconds>0 &&
             MaximumDecisionLagSeconds>0 &&
             (InferenceProvider==SHADOW_INFERENCE_LEGACY_LOCKED ||
              InferenceProvider==SHADOW_INFERENCE_DIRECTIONAL_RESEARCH ||
              InferenceProvider==SHADOW_INFERENCE_SIMPLE_TREND_BASELINE ||
              InferenceProvider==SHADOW_INFERENCE_OBJECTIVE_M15_M5_SETUP) &&
             ObjectiveMinimumRiskReward>=2.0 &&
             DecisionAuditFile!="" &&
             TelemetryFile!="" &&
             ObjectiveSetupAuditFile!="");
     }
  };

#endif
