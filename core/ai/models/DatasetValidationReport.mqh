//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetValidationReport.mqh                            |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.0.0                                                  |
//| Purpose : Dataset validation summary                             |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETVALIDATIONREPORT_MQH
#define CORE_AI_MODELS_DATASETVALIDATIONREPORT_MQH

class CDatasetValidationReport
  {
public:
   int TotalRecords;
   int BuyCount;
   int HoldCount;
   int SellCount;
   int DuplicateIdCount;
   int DuplicateTimestampCount;
   int InvalidFeatureCount;
   int InvalidLabelCount;
   bool Valid;

   CDatasetValidationReport(void)
     {
      Reset();
     }

   void Reset(void)
     {
      TotalRecords=0;
      BuyCount=0;
      HoldCount=0;
      SellCount=0;
      DuplicateIdCount=0;
      DuplicateTimestampCount=0;
      InvalidFeatureCount=0;
      InvalidLabelCount=0;
      Valid=false;
     }
  };

#endif
