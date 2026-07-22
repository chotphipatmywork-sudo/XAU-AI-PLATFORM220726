//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestDatasetReadinessGate.mq5                           |
//| Purpose : Offline model-training readiness gate smoke test       |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/DatasetReadinessGate.mqh"

input string TrainFile="XAU_AI_TRAINING_TRAIN.csv";
input string ValidationFile="XAU_AI_TRAINING_VALIDATION.csv";
input string TestFile="XAU_AI_TRAINING_TEST.csv";
input int MinimumTotalRecords=1000;
input int MinimumTrainRecords=700;
input int MinimumValidationRecords=100;
input int MinimumTestRecords=100;
input int MinimumLabelCountPerPartition=5;

int OnInit()
  {
   CDatasetReadinessConfig config;
   config.MinimumTotalRecords=MinimumTotalRecords;
   config.MinimumTrainRecords=MinimumTrainRecords;
   config.MinimumValidationRecords=MinimumValidationRecords;
   config.MinimumTestRecords=MinimumTestRecords;
   config.MinimumLabelCountPerPartition=MinimumLabelCountPerPartition;
   CDatasetReadinessGate gate;
   CDatasetReadinessReport report;
   if(!gate.Evaluate(TrainFile,ValidationFile,TestFile,config,report))
     {
      Print("Dataset readiness evaluation failed. Check files and thresholds.");
      return(INIT_FAILED);
     }

   Print("Readiness total records: ",report.TotalRecords," / minimum: ",MinimumTotalRecords);
   Print("Readiness partition valid: ",report.PartitionValid);
   Print("Readiness size requirement met: ",report.MeetsSizeRequirement);
   Print("Readiness label coverage met: ",report.MeetsLabelCoverage);
   Print("Dataset ready for model training: ",report.Ready);
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
