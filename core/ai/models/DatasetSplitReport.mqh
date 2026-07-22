//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : DatasetSplitReport.mqh                                 |
//| Layer   : Core / AI / Learning                                   |
//| Version : 1.1.0                                                  |
//| Purpose : Report purged chronological dataset split results      |
//+------------------------------------------------------------------+

#ifndef CORE_AI_MODELS_DATASETSPLITREPORT_MQH
#define CORE_AI_MODELS_DATASETSPLITREPORT_MQH

class CDatasetSplitReport
  {
public:
   int      TotalRecords;
   int      TrainRecords;
   int      ValidationRecords;
   int      TestRecords;
   int      PurgedRecords;
   int      PurgeBarsPerBoundary;
   datetime TrainFirstTimestamp;
   datetime TrainLastTimestamp;
   datetime ValidationFirstTimestamp;
   datetime ValidationLastTimestamp;
   datetime TestFirstTimestamp;
   datetime TestLastTimestamp;
   bool     Valid;

   CDatasetSplitReport(void)
     {
      Reset();
     }

   void Reset(void)
     {
      TotalRecords=0;
      TrainRecords=0;
      ValidationRecords=0;
      TestRecords=0;
      PurgedRecords=0;
      PurgeBarsPerBoundary=0;
      TrainFirstTimestamp=0;
      TrainLastTimestamp=0;
      ValidationFirstTimestamp=0;
      ValidationLastTimestamp=0;
      TestFirstTimestamp=0;
      TestLastTimestamp=0;
      Valid=false;
     }
  };

#endif
