//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowDirectionalInferenceProvider.mq5             |
//| Layer   : Tests / AI / Inference                                |
//| Version : 1.0.0                                                  |
//| Purpose : Verify tester-only directional research provider       |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/inference/DirectionalResearchInferenceProvider.mqh"
#include "../core/runtime/RuntimeManager.mqh"

void SetTrend(CAIInferenceRequest &request,
              const double regime,
              const double momentum,
              const double slope)
  {
   request.Features.TrendRegime=regime;
   request.Features.TrendMomentum=momentum;
   request.Features.TrendSlope=slope;
   request.Features.VolatilityRegime=50.0;
   request.Features.VolatilityChange=50.0;
   request.Features.LiquidityActivity=50.0;
   request.Features.LiquidityRangePosition=50.0;
   request.Features.LiquiditySweepDirection=50.0;
   request.Features.SessionAsia=100.0;
   request.Features.SessionLondon=0.0;
   request.Features.SessionNewYork=0.0;
   request.Features.SessionProgress=50.0;
  }

int OnInit()
  {
   CShadowRuntimeConfig legacyConfig;
   CShadowRuntimeConfig researchConfig;
   researchConfig.InferenceProvider=SHADOW_INFERENCE_DIRECTIONAL_RESEARCH;

   const bool legacyForwardAllowed=legacyConfig.InferenceProviderAllowed(false);
   const bool researchForwardBlocked=!researchConfig.InferenceProviderAllowed(false);
   const bool researchTesterAllowed=researchConfig.InferenceProviderAllowed(true);
   CRuntimeManager runtime;
   const bool runtimeForwardBlocked=!runtime.Initialize(researchConfig);
   if(runtime.IsRunning())
      runtime.Shutdown();

   CShadowRuntimeConfig retentionConfig;
   retentionConfig.UsePersistentCheckpoint=false;
   retentionConfig.Execution.AuditFile="XAU_AI_PROVIDER_RETENTION_TEST_AUDIT.csv";
   retentionConfig.Execution.StateFile="XAU_AI_PROVIDER_RETENTION_TEST_STATE.csv";
   retentionConfig.DecisionAuditFile="XAU_AI_PROVIDER_RETENTION_TEST_DECISIONS.csv";
   retentionConfig.TelemetryFile="XAU_AI_PROVIDER_RETENTION_TEST_TELEMETRY.csv";
   CRuntimeManager retentionRuntime;
   const bool retentionInitialized=retentionRuntime.Initialize(retentionConfig);
   const string identityBefore=retentionRuntime.InferenceProviderId();
   const string statusBefore=retentionRuntime.InferenceModelStatus();
   if(retentionRuntime.IsRunning())
      retentionRuntime.Shutdown();
   const bool shutdownIdentityRetained=(retentionInitialized &&
      identityBefore==retentionRuntime.InferenceProviderId() &&
      statusBefore==retentionRuntime.InferenceModelStatus());
   FileDelete(retentionConfig.Execution.AuditFile);
   FileDelete(retentionConfig.Execution.StateFile);
   FileDelete(retentionConfig.DecisionAuditFile);
   FileDelete(retentionConfig.TelemetryFile);

   CDirectionalResearchInferenceProvider provider;
   if(!provider.Initialize())
      return(INIT_FAILED);

   CAIInferenceRequest bullish;
   CAIInferenceRequest bearish;
   CAIInferenceRequest neutral;
   SetTrend(bullish,80.0,80.0,80.0);
   SetTrend(bearish,20.0,20.0,20.0);
   SetTrend(neutral,50.0,50.0,50.0);

   CAIDecision buy=provider.Evaluate(bullish);
   CAIDecision sell=provider.Evaluate(bearish);
   CAIDecision hold=provider.Evaluate(neutral);

   const bool mapping=(buy.Valid && buy.Action==AI_ACTION_BUY &&
                       sell.Valid && sell.Action==AI_ACTION_SELL &&
                       hold.Valid && hold.Action==AI_ACTION_HOLD);
   const bool identity=(provider.ProviderId()==
                        "DIRECTIONAL_FEATURE_RESEARCH_TESTER_ONLY");
   const bool noGo=(provider.ModelStatus()==
                    "DIRECTIONAL_FEATURE_RESEARCH_NO_GO" &&
                    !provider.ModelDeploymentAuthorized());
   const bool valid=(legacyForwardAllowed && researchForwardBlocked &&
                     runtimeForwardBlocked &&
                     researchTesterAllowed && shutdownIdentityRetained &&
                     mapping && identity && noGo);

   Print("Shadow legacy provider Forward default valid: ",legacyForwardAllowed);
   Print("Shadow directional provider Forward blocked: ",researchForwardBlocked);
   Print("Shadow directional Runtime Forward initialization blocked: ",runtimeForwardBlocked);
   Print("Shadow directional provider Tester allowed: ",researchTesterAllowed);
   Print("Shadow inference identity retained after Shutdown: ",shutdownIdentityRetained);
   Print("Shadow directional BUY/HOLD/SELL mapping valid: ",mapping);
   Print("Shadow directional provider identity valid: ",identity);
   Print("Shadow directional provider NO-GO lock valid: ",noGo);
   Print("Shadow directional inference contract valid: ",valid);

   provider.Shutdown();
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
