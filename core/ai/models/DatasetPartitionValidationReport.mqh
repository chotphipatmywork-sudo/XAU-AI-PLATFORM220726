//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetPartitionValidationReport.mqh                   |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.1.0                                                  |
//| Purpose : Validation summary for purged temporal partitions      |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETPARTITIONVALIDATIONREPORT_MQH
#define CORE_AI_MODELS_DATASETPARTITIONVALIDATIONREPORT_MQH

class CDatasetPartitionValidationReport
  {
public:
   int      TrainRecords;
   int      ValidationRecords;
   int      TestRecords;
   int      TrainBuyCount;
   int      TrainHoldCount;
   int      TrainSellCount;
   int      ValidationBuyCount;
   int      ValidationHoldCount;
   int      ValidationSellCount;
   int      TestBuyCount;
   int      TestHoldCount;
   int      TestSellCount;
   int      DuplicateIdCount;
   int      DuplicateTimestampCount;
   int      InvalidFeatureCount;
   int      InvalidLabelCount;
   datetime TrainFirstTimestamp;
   datetime TrainLastTimestamp;
   datetime ValidationFirstTimestamp;
   datetime ValidationLastTimestamp;
   datetime TestFirstTimestamp;
   datetime TestLastTimestamp;
   bool     TemporalOrderValid;
   bool     PurgeBoundaryValid;
   int      TrainValidationGapSeconds;
   int      ValidationTestGapSeconds;
   bool     Valid;

   CDatasetPartitionValidationReport(void)
     {
      Reset();
     }

   void Reset(void)
     {
      TrainRecords=0;
      ValidationRecords=0;
      TestRecords=0;
      TrainBuyCount=0;
      TrainHoldCount=0;
      TrainSellCount=0;
      ValidationBuyCount=0;
      ValidationHoldCount=0;
      ValidationSellCount=0;
      TestBuyCount=0;
      TestHoldCount=0;
      TestSellCount=0;
      DuplicateIdCount=0;
      DuplicateTimestampCount=0;
      InvalidFeatureCount=0;
      InvalidLabelCount=0;
      TrainFirstTimestamp=0;
      TrainLastTimestamp=0;
      ValidationFirstTimestamp=0;
      ValidationLastTimestamp=0;
      TestFirstTimestamp=0;
      TestLastTimestamp=0;
      TemporalOrderValid=false;
      PurgeBoundaryValid=false;
      TrainValidationGapSeconds=0;
      ValidationTestGapSeconds=0;
      Valid=false;
     }
  };

#endif
