//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestModelEvaluationContract.mq5                        |
//| Purpose : Model evaluation contract smoke test                   |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/ModelEvaluationContract.mqh"

int OnInit()
  {
   CModelEvaluationMetrics validation_metrics;
   validation_metrics.SampleCount=486;
   validation_metrics.Accuracy=0.60;
   validation_metrics.MacroF1=0.55;
   validation_metrics.BuyPrecision=0.62;
   validation_metrics.BuyRecall=0.48;
   validation_metrics.SellPrecision=0.64;
   validation_metrics.SellRecall=0.51;

   CModelEvaluationMetrics test_metrics;
   test_metrics.SampleCount=487;
   test_metrics.Accuracy=0.58;
   test_metrics.MacroF1=0.52;
   test_metrics.BuyPrecision=0.60;
   test_metrics.BuyRecall=0.45;
   test_metrics.SellPrecision=0.61;
   test_metrics.SellRecall=0.46;

   CModelEvaluationContract contract;
   CModelEvaluationReport report;
   if(!contract.Evaluate(validation_metrics,test_metrics,report))
     {
      Print("Model evaluation contract rejected invalid metrics");
      return(INIT_FAILED);
     }

   Print("Model evaluation contract v",contract.ContractVersion());
   Print("Minimum samples/accuracy/macro F1: ",contract.MinimumSampleCount(),"/",
         contract.MinimumAccuracy(),"/",contract.MinimumMacroF1());
   Print("Validation thresholds met: ",report.ValidationMeetsThresholds);
   Print("Test thresholds met: ",report.TestMeetsThresholds);
   Print("Eligible for shadow deployment: ",report.EligibleForShadowDeployment);
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
