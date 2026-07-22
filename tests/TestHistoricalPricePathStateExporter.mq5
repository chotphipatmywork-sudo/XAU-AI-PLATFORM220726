//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalPricePathStateExporter.mq5               |
//| Layer   : Tests / AI / Learning / Research                       |
//| Version : 1.0.0                                                  |
//| Purpose : Verify and export completed 16-bar price-path state    |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/trend/engines/PricePathStateEngine.mqh"
#include "../core/ai/HistoricalPricePathStateExporter.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";
input string OutputFile="XAU_AI_PRICE_PATH_RESEARCH.csv";
input int ProgressInterval=100;

bool SyntheticPathValid(void)
  {
   double closes[];
   double highs[];
   double lows[];
   ArrayResize(closes,17);
   ArrayResize(highs,16);
   ArrayResize(lows,16);
   for(int index=0; index<17; index++)
     {
      closes[index]=116.0-index;
      if(index<16)
        {
         highs[index]=closes[index]+1.0;
         lows[index]=closes[index]-1.0;
        }
     }
   CPricePathStateEngine engine;
   const CPricePathStateResult result=engine.Analyze(closes,highs,lows,2.0);
   return(result.Valid &&
          result.PathDirectionalEfficiency==100.0 &&
          result.UpCloseRatio==100.0 &&
          result.DirectionalRunBalance==100.0 &&
          result.ReturnSignPersistence==100.0 &&
          result.PathTravelAtr==50.0 &&
          result.RangeEfficiency==100.0 &&
          result.RangeExpansion==50.0);
  }

int OnInit()
  {
   CHistoricalPricePathStateExporter exporter;
   const datetime bar_open=StringToTime("2026.07.16 08:45:00");
   const datetime observation=exporter.ObservationTime(bar_open,PERIOD_M15);
   const bool timing_valid=(observation==StringToTime("2026.07.16 09:00:00") &&
                            exporter.IsBarClosed(bar_open,observation,PERIOD_M15) &&
                            !exporter.IsBarClosed(StringToTime("2026.07.16 09:00:00"),
                                                  observation,PERIOD_M15));
   const bool synthetic_valid=SyntheticPathValid();
   Print("Historical price path synthetic valid: ",synthetic_valid);
   Print("Historical price path closed-bar timing valid: ",timing_valid);
   if(!synthetic_valid || !timing_valid || ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Historical price path state research export started");
   const int written=exporter.Export(DatasetFile,OutputFile,ProgressInterval);
   Print("Historical price path state research records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
