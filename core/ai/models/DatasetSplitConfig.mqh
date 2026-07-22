//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetSplitConfig.mqh                                 |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.1.0                                                  |
//| Purpose : Configure purged chronological dataset partitions      |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETSPLITCONFIG_MQH
#define CORE_AI_MODELS_DATASETSPLITCONFIG_MQH

class CDatasetSplitConfig
  {
public:
   double TrainRatio;
   double ValidationRatio;
   double TestRatio;
   int    PurgeBars;

   CDatasetSplitConfig(void)
     {
      TrainRatio=0.70;
      ValidationRatio=0.15;
      TestRatio=0.15;
      PurgeBars=16;
     }

   bool IsValid(void) const
     {
      const double total=TrainRatio+ValidationRatio+TestRatio;
      return(TrainRatio>0.0 && ValidationRatio>0.0 && TestRatio>0.0 && PurgeBars==16 &&
             MathAbs(total-1.0)<0.000001);
     }
  };

#endif
