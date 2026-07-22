//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalSwingStructureExporter.mq5               |
//| Layer   : Tests / AI / Learning / Research                       |
//| Version : 1.0.0                                                  |
//| Purpose : Verify confirmed swings and export research context    |
//+------------------------------------------------------------------+

#property strict

#include "../core/brain/trend/engines/ConfirmedSwingStructureEngine.mqh"
#include "../core/ai/HistoricalSwingStructureExporter.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";
input string OutputFile="XAU_AI_SWING_STRUCTURE_RESEARCH.csv";
input int ProgressInterval=100;

void SetBase(double &highs[],double &lows[],double &closes[])
  {
   const int count=24;
   ArrayResize(highs,count);
   ArrayResize(lows,count);
   ArrayResize(closes,count);
   for(int index=0; index<count; index++)
     {
      highs[index]=100.0;
      lows[index]=95.0;
      closes[index]=97.0;
     }
  }

bool SyntheticStructureValid(void)
  {
   CConfirmedSwingStructureEngine engine;
   if(!engine.Configure(2,2,18))
      return(false);
   double highs[];
   double lows[];
   double closes[];
   SetBase(highs,lows,closes);
   highs[4]=120.0;
   highs[10]=110.0;
   lows[6]=90.0;
   lows[12]=80.0;
   closes[0]=85.0;
   const CConfirmedSwingStructureResult result=engine.Analyze(highs,lows,closes);
   return(result.Valid &&
          result.StructureDirection==100.0 &&
          result.BreakDirection==0.0 &&
          result.ChochDirection==0.0 &&
          result.RangePosition==0.0);
  }

int OnInit()
  {
   CHistoricalSwingStructureExporter exporter;
   const datetime bar_open=StringToTime("2026.07.16 08:45:00");
   const datetime observation=exporter.ObservationTime(bar_open,PERIOD_M15);
   const bool timing_valid=(observation==StringToTime("2026.07.16 09:00:00") &&
                            exporter.IsBarClosed(bar_open,observation,PERIOD_M15) &&
                            !exporter.IsBarClosed(StringToTime("2026.07.16 09:00:00"),
                                                  observation,PERIOD_M15));
   const bool synthetic_valid=SyntheticStructureValid();
   Print("Confirmed swing structure synthetic valid: ",synthetic_valid);
   Print("Confirmed swing structure timing valid: ",timing_valid);
   if(!synthetic_valid || !timing_valid || ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Historical swing structure research export started");
   const int written=exporter.Export(DatasetFile,OutputFile,ProgressInterval);
   Print("Historical swing structure research records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
