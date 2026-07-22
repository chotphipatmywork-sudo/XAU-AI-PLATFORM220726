//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowSimpleBaselineInferenceProvider.mq5          |
//| Layer   : Tests / AI / Inference                                |
//| Version : 1.0.0                                                  |
//| Purpose : Verify tester-only Simple Baseline provider contract   |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/inference/SimpleTrendBaselineInferenceProvider.mqh"
#include "../core/runtime/RuntimeManager.mqh"

void SetBaselineTrend(CAIInferenceRequest &request,
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
   CShadowRuntimeConfig defaultConfig;
   CShadowRuntimeConfig baselineConfig;
   baselineConfig.InferenceProvider=SHADOW_INFERENCE_SIMPLE_TREND_BASELINE;
   baselineConfig.Execution.StopLossPoints=500.0;
   baselineConfig.Execution.TakeProfitPoints=1000.0;

   const bool forwardDefaultUnchanged=
      (defaultConfig.InferenceProvider==SHADOW_INFERENCE_LEGACY_LOCKED);
   const bool baselineForwardBlocked=
      !baselineConfig.InferenceProviderAllowed(false);
   const bool baselineTesterAllowed=
      baselineConfig.InferenceProviderAllowed(true);
   CRuntimeManager runtime;
   const bool runtimeForwardBlocked=!runtime.Initialize(baselineConfig);
   if(runtime.IsRunning())
      runtime.Shutdown();
   const bool riskRewardValid=
      (baselineConfig.Execution.Valid() &&
       MathAbs(baselineConfig.Execution.TakeProfitPoints/
               baselineConfig.Execution.StopLossPoints-2.0)<0.000001);

   CSimpleTrendBaselineInferenceProvider provider;
   if(!provider.Initialize())
      return(INIT_FAILED);
   CAIInferenceRequest bullish;
   CAIInferenceRequest bearish;
   CAIInferenceRequest mixed;
   SetBaselineTrend(bullish,70.0,60.0,55.0);
   SetBaselineTrend(bearish,30.0,40.0,45.0);
   SetBaselineTrend(mixed,70.0,60.0,40.0);

   const CAIDecision buy=provider.Evaluate(bullish);
   const CAIDecision sell=provider.Evaluate(bearish);
   const CAIDecision hold=provider.Evaluate(mixed);
   const bool mapping=(buy.Valid && buy.Action==AI_ACTION_BUY &&
                       sell.Valid && sell.Action==AI_ACTION_SELL &&
                       hold.Valid && hold.Action==AI_ACTION_HOLD);
   const bool strictAlignment=(hold.Confidence==0.0);
   const bool identity=(provider.ProviderId()==
      "SIMPLE_TREND_ALIGNMENT_BASELINE_TESTER_ONLY");
   const bool noGo=(provider.ModelStatus()==
                    "SIMPLE_BASELINE_BENCHMARK_NO_GO" &&
                    !provider.ModelDeploymentAuthorized());
   const bool valid=(forwardDefaultUnchanged && baselineForwardBlocked &&
                     baselineTesterAllowed && runtimeForwardBlocked &&
                     riskRewardValid && mapping && strictAlignment &&
                     identity && noGo);

   Print("Simple Baseline Forward default unchanged: ",forwardDefaultUnchanged);
   Print("Simple Baseline Forward blocked: ",baselineForwardBlocked);
   Print("Simple Baseline Strategy Tester allowed: ",baselineTesterAllowed);
   Print("Simple Baseline Runtime Forward initialization blocked: ",runtimeForwardBlocked);
   Print("Simple Baseline fixed Risk:Reward 1:2 valid: ",riskRewardValid);
   Print("Simple Baseline BUY/HOLD/SELL mapping valid: ",mapping);
   Print("Simple Baseline strict Trend alignment valid: ",strictAlignment);
   Print("Simple Baseline provider identity valid: ",identity);
   Print("Simple Baseline deployment NO-GO lock valid: ",noGo);
   Print("Simple Baseline provider contract valid: ",valid);

   provider.Shutdown();
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
