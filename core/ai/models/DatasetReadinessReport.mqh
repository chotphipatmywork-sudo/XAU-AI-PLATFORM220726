//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetReadinessReport.mqh                             |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Summarize whether a dataset is ready for model training|
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETREADINESSREPORT_MQH
#define CORE_AI_MODELS_DATASETREADINESSREPORT_MQH

class CDatasetReadinessReport
  {
public:
   int  TotalRecords;
   bool PartitionValid;
   bool MeetsSizeRequirement;
   bool MeetsLabelCoverage;
   bool Ready;

   CDatasetReadinessReport(void)
     {
      Reset();
     }

   void Reset(void)
     {
      TotalRecords=0;
      PartitionValid=false;
      MeetsSizeRequirement=false;
      MeetsLabelCoverage=false;
      Ready=false;
     }
  };

#endif
