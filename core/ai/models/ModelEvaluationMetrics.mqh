//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : ModelEvaluationMetrics.mqh                             |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Store offline classifier evaluation metrics            |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_MODELEVALUATIONMETRICS_MQH
#define CORE_AI_MODELS_MODELEVALUATIONMETRICS_MQH

class CModelEvaluationMetrics
  {
public:
   int    SampleCount;
   double Accuracy;
   double MacroF1;
   double BuyPrecision;
   double BuyRecall;
   double SellPrecision;
   double SellRecall;

   CModelEvaluationMetrics(void)
     {
      Reset();
     }

   void Reset(void)
     {
      SampleCount=0;
      Accuracy=0.0;
      MacroF1=0.0;
      BuyPrecision=0.0;
      BuyRecall=0.0;
      SellPrecision=0.0;
      SellRecall=0.0;
     }
  };

#endif
