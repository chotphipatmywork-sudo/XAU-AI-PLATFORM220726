//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetReadinessConfig.mqh                             |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Minimum quality thresholds before model training       |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETREADINESSCONFIG_MQH
#define CORE_AI_MODELS_DATASETREADINESSCONFIG_MQH

class CDatasetReadinessConfig
  {
public:
   int MinimumTotalRecords;
   int MinimumTrainRecords;
   int MinimumValidationRecords;
   int MinimumTestRecords;
   int MinimumLabelCountPerPartition;

   CDatasetReadinessConfig(void)
     {
      MinimumTotalRecords=1000;
      MinimumTrainRecords=700;
      MinimumValidationRecords=100;
      MinimumTestRecords=100;
      MinimumLabelCountPerPartition=5;
     }

   bool IsValid(void) const
     {
      return(MinimumTotalRecords>0 && MinimumTrainRecords>0 &&
             MinimumValidationRecords>0 && MinimumTestRecords>0 &&
             MinimumLabelCountPerPartition>0 &&
             MinimumTrainRecords+MinimumValidationRecords+MinimumTestRecords<=MinimumTotalRecords);
     }
  };

#endif
