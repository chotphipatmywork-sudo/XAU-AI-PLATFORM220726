//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalTickMicrostructureExporter.mq5           |
//| Layer   : Tests / AI / Learning / Research                      |
//| Version : 1.0.0                                                  |
//| Purpose : Verify and export completed M15 tick microstructure    |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/liquidity/engines/TickMicrostructureEngine.mqh"
#include "../core/ai/HistoricalTickMicrostructureExporter.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";
input string OutputFile="XAU_AI_TICK_MICROSTRUCTURE_RESEARCH.csv";
input int ProgressInterval=100;

bool SyntheticEncodingValid()
  {
   const datetime barOpen=StringToTime("2026.07.16 08:45:00");
   MqlTick ticks[20];
   for(int index=0; index<20; index++)
     {
      ticks[index].time=barOpen+index*40;
      ticks[index].time_msc=(long)ticks[index].time*1000;
      ticks[index].bid=100.0+0.1*index;
      ticks[index].ask=ticks[index].bid+0.02;
     }
   CTickMicrostructureEngine engine;
   const CTickMicrostructureResult result=
      engine.Analyze(ticks,2.0,barOpen,PERIOD_M15);
   return(result.Valid && result.TickCount==20 &&
          MathAbs(result.TickDirectionImbalance-100.0)<0.000001 &&
          MathAbs(result.TickPathEfficiency-100.0)<0.000001 &&
          result.TickBurstConcentration>=0.0 &&
          result.TickBurstConcentration<=100.0 &&
          result.MeanSpreadAtr>0.0 && result.MeanSpreadAtr<100.0 &&
          result.MaximumSpreadAtr>0.0 && result.MaximumSpreadAtr<100.0 &&
          result.RealizedTickVolatilityAtr>0.0 &&
          result.RealizedTickVolatilityAtr<100.0);
  }

int OnInit()
  {
   CHistoricalTickMicrostructureExporter exporter;
   const datetime barOpen=StringToTime("2026.07.16 08:45:00");
   const datetime observation=exporter.ObservationTime(barOpen,PERIOD_M15);
   const bool timingValid=(observation==StringToTime("2026.07.16 09:00:00") &&
                           exporter.IsBarClosed(barOpen,observation,PERIOD_M15) &&
                           !exporter.IsBarClosed(observation,observation,PERIOD_M15));
   const bool syntheticValid=SyntheticEncodingValid();
   Print("Historical tick microstructure synthetic valid: ",syntheticValid);
   Print("Historical tick microstructure closed-bar timing valid: ",timingValid);
   if(!syntheticValid || !timingValid || ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Historical tick microstructure research export started");
   const int written=exporter.Export(DatasetFile,OutputFile,ProgressInterval);
   Print("Historical tick microstructure research records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }

