//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalDatasetOrchestrator.mq5                  |
//| Layer   : Tests / AI / Learning                                  |
//| Version : 4.0.1                                                  |
//| Purpose : One-shot historical dataset orchestration test         |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/HistoricalDatasetOrchestrator.mqh"

input int DatasetBars=300;
input bool ReplaceExistingDataset=true;
input int ProgressInterval=100;
input int LabelHorizonBars=16;
input int LabelAtrPeriod=14;
input double LabelBarrierAtrMultiplier=1.50;

int OnInit()
  {
   if(DatasetBars<=0 || ProgressInterval<=0 || LabelHorizonBars<=0 ||
      LabelAtrPeriod<=0 || LabelBarrierAtrMultiplier<=0.0)
      return(INIT_PARAMETERS_INCORRECT);

   const datetime to=TimeCurrent();
   const datetime from=to-DatasetBars*PeriodSeconds(PERIOD_M15);
   CHistoricalDatasetOrchestrator orchestrator;
   if(!orchestrator.ConfigureLabeling(LabelHorizonBars,LabelAtrPeriod,LabelBarrierAtrMultiplier))
      return(INIT_FAILED);
   Print("Historical dataset generation started. Requested bars: ",DatasetBars);
   Print("Historical feature schema 4.0.0");
   Print("Historical label schema 1.1.0: horizon ",LabelHorizonBars,
         " bars, barrier ",LabelBarrierAtrMultiplier," ATR(",LabelAtrPeriod,")");
   const int records_written=orchestrator.Build(_Symbol,PERIOD_M15,from,to,!ReplaceExistingDataset,ProgressInterval);
   Print("Historical dataset records written: ",records_written);
   ExpertRemove();
   return(INIT_SUCCEEDED);
  }

void OnTick()
  {
  }
