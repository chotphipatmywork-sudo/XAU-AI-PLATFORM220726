//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestShadowInferenceProvider.mq5                        |
//| Layer   : Tests / AI / Inference                                |
//| Version : 1.1.0                                                  |
//| Purpose : Verify locked provider parity and Schema 4.0 contract  |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/inference/DevelopmentHeuristicInferenceProvider.mqh"

int OnInit()
  {
   CAIInferenceRequest request;
   request.Features.TrendRegime=90.0;
   request.Features.TrendMomentum=70.0;
   request.Features.TrendSlope=40.0;
   request.Features.VolatilityRegime=55.0;
   request.Features.VolatilityChange=60.0;
   request.Features.LiquidityActivity=35.0;
   request.Features.LiquidityRangePosition=80.0;
   request.Features.LiquiditySweepDirection=100.0;
   request.Features.SessionAsia=0.0;
   request.Features.SessionLondon=100.0;
   request.Features.SessionNewYork=0.0;
   request.Features.SessionProgress=25.0;
   request.LegacyTrendScore=72.0;
   request.LegacyVolatilityScore=54.0;
   request.LegacyLiquidityScore=38.0;
   request.LegacySessionScore=50.0;

   CAIManager direct;
   CDevelopmentHeuristicInferenceProvider provider;
   if(!direct.Initialize() || !provider.Initialize())
      return(INIT_FAILED);

   CAIDecision expected=direct.Evaluate(request.LegacyTrendScore,
                                        request.LegacyVolatilityScore,
                                        request.LegacyLiquidityScore,
                                        request.LegacySessionScore);
   IAIInferenceProvider *boundary=GetPointer(provider);
   CAIDecision actual=boundary.Evaluate(request);

   const bool parity=(actual.Valid==expected.Valid &&
                      actual.Action==expected.Action &&
                      MathAbs(actual.Score-expected.Score)<0.000001 &&
                      MathAbs(actual.Confidence-expected.Confidence)<0.000001);
   const bool identity=(boundary.ProviderId()==
                        "DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO");
   const bool status=(boundary.ModelStatus()==
                      "DEVELOPMENT_HEURISTIC_MODEL_NO_GO");
   const bool locked=!boundary.ModelDeploymentAuthorized();
   const bool valid=(request.FeatureSchemaValid() && parity && identity && status && locked);

   Print("Shadow inference Feature Schema 4.0 valid: ",request.FeatureSchemaValid());
   Print("Shadow inference legacy behavior parity valid: ",parity);
   Print("Shadow inference provider identity valid: ",identity);
   Print("Shadow inference model status valid: ",status);
   Print("Shadow inference deployment lock valid: ",locked);
   Print("Shadow inference provider contract valid: ",valid);

   provider.Shutdown();
   direct.Shutdown();
   ExpertRemove();
   return(valid ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
