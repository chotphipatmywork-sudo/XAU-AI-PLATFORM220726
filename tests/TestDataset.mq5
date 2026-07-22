//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestDataset.mq5                                        |
//| Layer   : Tests / AI / Learning                                  |
//| Version : 4.0.0                                                  |
//| Purpose : Dataset layer smoke test                               |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/AITrainingEngine.mqh"

void OnStart()
  {
   CAITrainingEngine engine;
   if(!engine.Initialize())
     {
      Print("Dataset initialization failed");
      return;
     }
   CAIFeatureVector features=engine.BuildFeature(
      25.0,50.0,75.0,
      55.0,60.0,
      75.0,80.0,100.0,
      0.0,100.0,0.0,25.0);
   const bool stored=engine.RecordSample(features,1.0,_Symbol,TimeCurrent());
   Print("Dataset sample stored: ",stored);
  }
