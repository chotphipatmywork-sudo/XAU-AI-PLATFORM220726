//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestDatasetSplitter.mq5                                |
//| Purpose : Chronological dataset split smoke test                 |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/DatasetSplitter.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";
input string TrainFile="XAU_AI_TRAINING_TRAIN.csv";
input string ValidationFile="XAU_AI_TRAINING_VALIDATION.csv";
input string TestFile="XAU_AI_TRAINING_TEST.csv";
input double TrainRatio=0.70;
input double ValidationRatio=0.15;
input double TestRatio=0.15;
input int PurgeBars=16;

int OnInit()
  {
   CDatasetSplitConfig config;
   config.TrainRatio=TrainRatio;
   config.ValidationRatio=ValidationRatio;
   config.TestRatio=TestRatio;
   config.PurgeBars=PurgeBars;
   CDatasetSplitter splitter;
   CDatasetSplitReport report;
   if(!splitter.Split(DatasetFile,TrainFile,ValidationFile,TestFile,config,report))
     {
      Print("Dataset split failed. Check file names, chronological timestamps, and ratios.");
      return(INIT_FAILED);
     }

   Print("Dataset split total records: ",report.TotalRecords);
   Print("Dataset split TRAIN/VALIDATION/TEST: ",report.TrainRecords,"/",report.ValidationRecords,"/",report.TestRecords);
   Print("Dataset split purged records: ",report.PurgedRecords," (",report.PurgeBarsPerBoundary," bars per boundary)");
   Print("Dataset split last timestamps: ",TimeToString(report.TrainLastTimestamp)," / ",TimeToString(report.ValidationLastTimestamp)," / ",TimeToString(report.TestLastTimestamp));
   Print("Dataset split valid: ",report.Valid);
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
