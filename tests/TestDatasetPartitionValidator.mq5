//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestDatasetPartitionValidator.mq5                      |
//| Purpose : Dataset partition validation smoke test                |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/DatasetPartitionValidator.mqh"

input string TrainFile="XAU_AI_TRAINING_TRAIN.csv";
input string ValidationFile="XAU_AI_TRAINING_VALIDATION.csv";
input string TestFile="XAU_AI_TRAINING_TEST.csv";
input int PurgeBars=16;

int OnInit()
  {
   CDatasetPartitionValidator validator;
   CDatasetPartitionValidationReport report;
   if(!validator.Validate(TrainFile,ValidationFile,TestFile,report,PurgeBars,PeriodSeconds(PERIOD_M15)))
     {
      Print("Dataset partition validation failed.");
      return(INIT_FAILED);
     }

   Print("Partition records TRAIN/VALIDATION/TEST: ",report.TrainRecords,"/",report.ValidationRecords,"/",report.TestRecords);
   Print("TRAIN labels BUY/HOLD/SELL: ",report.TrainBuyCount,"/",report.TrainHoldCount,"/",report.TrainSellCount);
   Print("VALIDATION labels BUY/HOLD/SELL: ",report.ValidationBuyCount,"/",report.ValidationHoldCount,"/",report.ValidationSellCount);
   Print("TEST labels BUY/HOLD/SELL: ",report.TestBuyCount,"/",report.TestHoldCount,"/",report.TestSellCount);
   Print("Partition duplicate IDs: ",report.DuplicateIdCount);
   Print("Partition duplicate timestamps: ",report.DuplicateTimestampCount);
   Print("Partition invalid features: ",report.InvalidFeatureCount);
   Print("Partition invalid labels: ",report.InvalidLabelCount);
   Print("Partition temporal order valid: ",report.TemporalOrderValid);
   Print("Partition boundary gaps in seconds: ",report.TrainValidationGapSeconds,"/",report.ValidationTestGapSeconds);
   Print("Partition label-horizon purge valid: ",report.PurgeBoundaryValid);
   Print("Partition dataset valid: ",report.Valid);
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
