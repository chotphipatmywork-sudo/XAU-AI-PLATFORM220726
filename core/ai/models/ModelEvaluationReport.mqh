//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ModelEvaluationReport.mqh                              |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Report offline model evaluation eligibility            |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_MODELEVALUATIONREPORT_MQH
#define CORE_AI_MODELS_MODELEVALUATIONREPORT_MQH

class CModelEvaluationReport
  {
public:
   bool ValidationMetricsValid;
   bool TestMetricsValid;
   bool ValidationMeetsThresholds;
   bool TestMeetsThresholds;
   bool EligibleForShadowDeployment;

   CModelEvaluationReport(void)
     {
      Reset();
     }

   void Reset(void)
     {
      ValidationMetricsValid=false;
      TestMetricsValid=false;
      ValidationMeetsThresholds=false;
      TestMeetsThresholds=false;
      EligibleForShadowDeployment=false;
     }
  };

#endif
