//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ModelEvaluationContract.mqh                            |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Define minimum offline model evaluation requirements   |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELEVALUATIONCONTRACT_MQH
#define CORE_AI_MODELEVALUATIONCONTRACT_MQH

#include "models/ModelEvaluationMetrics.mqh"
#include "models/ModelEvaluationReport.mqh"

class CModelEvaluationContract
  {
private:
   bool IsRatioValid(const double value) const
     {
      return(value>=0.0 && value<=1.0);
     }

   bool MeetsThresholds(const CModelEvaluationMetrics &metrics) const
     {
      return(metrics.SampleCount>=MinimumSampleCount() &&
             metrics.Accuracy>=MinimumAccuracy() &&
             metrics.MacroF1>=MinimumMacroF1() &&
             metrics.BuyPrecision>=MinimumDirectionalPrecision() &&
             metrics.SellPrecision>=MinimumDirectionalPrecision() &&
             metrics.BuyRecall>=MinimumDirectionalRecall() &&
             metrics.SellRecall>=MinimumDirectionalRecall());
     }

public:
   string ContractVersion(void) const { return("1.0.0"); }
   int MinimumSampleCount(void) const { return(100); }
   double MinimumAccuracy(void) const { return(0.45); }
   double MinimumMacroF1(void) const { return(0.40); }
   double MinimumDirectionalPrecision(void) const { return(0.50); }
   double MinimumDirectionalRecall(void) const { return(0.30); }

   bool ValidateMetrics(const CModelEvaluationMetrics &metrics) const
     {
      return(metrics.SampleCount>0 && IsRatioValid(metrics.Accuracy) &&
             IsRatioValid(metrics.MacroF1) && IsRatioValid(metrics.BuyPrecision) &&
             IsRatioValid(metrics.BuyRecall) && IsRatioValid(metrics.SellPrecision) &&
             IsRatioValid(metrics.SellRecall));
     }

   bool Evaluate(const CModelEvaluationMetrics &validation_metrics,
                 const CModelEvaluationMetrics &test_metrics,
                 CModelEvaluationReport &report) const
     {
      report.Reset();
      report.ValidationMetricsValid=ValidateMetrics(validation_metrics);
      report.TestMetricsValid=ValidateMetrics(test_metrics);
      if(!report.ValidationMetricsValid || !report.TestMetricsValid)
         return(false);

      report.ValidationMeetsThresholds=MeetsThresholds(validation_metrics);
      report.TestMeetsThresholds=MeetsThresholds(test_metrics);
      report.EligibleForShadowDeployment=(report.ValidationMeetsThresholds &&
                                          report.TestMeetsThresholds);
      return(true);
     }
  };

#endif
