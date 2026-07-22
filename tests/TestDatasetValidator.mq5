//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestDatasetValidator.mq5                               |
//| Purpose : Dataset validation smoke test                          |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/DatasetValidator.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";

int OnInit()
  {
   CDatasetValidator validator;
   CDatasetValidationReport report;
   if(!validator.Validate(DatasetFile,report))
     {
      Print("Dataset validation failed: file cannot be read: ",DatasetFile);
      return(INIT_FAILED);
     }

   Print("Dataset total records: ",report.TotalRecords);
   Print("Dataset labels BUY/HOLD/SELL: ",report.BuyCount,"/",report.HoldCount,"/",report.SellCount);
   Print("Dataset duplicate IDs: ",report.DuplicateIdCount);
   Print("Dataset duplicate timestamps: ",report.DuplicateTimestampCount);
   Print("Dataset invalid features: ",report.InvalidFeatureCount);
   Print("Dataset invalid labels: ",report.InvalidLabelCount);
   Print("Dataset valid: ",report.Valid);
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
