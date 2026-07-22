//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestModelTrainingContract.mq5                          |
//| Layer   : Tests / AI / Learning                                  |
//| Version : 4.0.0                                                  |
//| Purpose : Model training contract smoke test                     |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/models/ModelTrainingContract.mqh"

int OnInit()
  {
   CModelTrainingContract contract;
   if(!contract.IsValid())
     {
      Print("Model training contract validation failed");
      return(INIT_FAILED);
     }

   Print("Model contract: ",contract.ModelName()," v",contract.ContractVersion());
   Print("Feature/label schema: ",contract.FeatureSchemaVersion(),"/",
         contract.LabelSchemaVersion());
   Print("Model input ",contract.InputName()," features: ",
         contract.FeatureName(0),", ",contract.FeatureName(1),", ",
         contract.FeatureName(2),", ",contract.FeatureName(3),", ",
         contract.FeatureName(4),", ",contract.FeatureName(5),", ",
         contract.FeatureName(6),", ",contract.FeatureName(7),", ",
         contract.FeatureName(8),", ",contract.FeatureName(9),", ",
         contract.FeatureName(10),", ",contract.FeatureName(11));
   Print("Model output ",contract.OutputName()," classes: ",
         contract.ClassName(0),", ",contract.ClassName(1),", ",contract.ClassName(2));
   Print("Model label mapping SELL/HOLD/BUY: ",
         contract.LabelForClassIndex(0),"/",contract.LabelForClassIndex(1),"/",
         contract.LabelForClassIndex(2));
   Print("Model probability contract valid: ",
         contract.ValidateProbabilities(0.20,0.30,0.50));
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
