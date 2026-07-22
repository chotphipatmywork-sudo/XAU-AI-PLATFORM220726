//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalPriceActionContextExporter.mq5           |
//| Layer   : Tests / AI / Learning / Research                       |
//| Version : 1.0.0                                                  |
//| Purpose : Verify and export bounded past-only price context      |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/HistoricalPriceActionContextExporter.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";
input string OutputFile="XAU_AI_PRICE_ACTION_RESEARCH.csv";
input int ProgressInterval=100;

bool SyntheticEncodingValid(CHistoricalPriceActionContextExporter &exporter)
  {
   return(exporter.EncodeSignedAtr(0.0,1.0)==50.0 &&
          exporter.EncodeSignedAtr(2.0,1.0)==100.0 &&
          exporter.EncodeSignedAtr(-2.0,1.0)==0.0 &&
          exporter.EncodePositiveAtr(1.0,1.0)==50.0 &&
          exporter.EncodePositiveAtr(2.0,1.0)==100.0 &&
          exporter.RangePosition(75.0,50.0,100.0)==50.0);
  }

int OnInit()
  {
   CHistoricalPriceActionContextExporter exporter;
   const datetime bar_open=StringToTime("2026.07.16 08:45:00");
   const datetime observation=exporter.ObservationTime(bar_open,PERIOD_M15);
   const bool timing_valid=(observation==StringToTime("2026.07.16 09:00:00") &&
                            exporter.IsBarClosed(bar_open,observation,PERIOD_M15) &&
                            !exporter.IsBarClosed(StringToTime("2026.07.16 09:00:00"),
                                                  observation,PERIOD_M15));
   const bool encoding_valid=SyntheticEncodingValid(exporter);
   Print("Historical price action encoding valid: ",encoding_valid);
   Print("Historical price action closed-bar timing valid: ",timing_valid);
   if(!encoding_valid || !timing_valid || ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Historical price action context research export started");
   const int written=exporter.Export(DatasetFile,OutputFile,ProgressInterval);
   Print("Historical price action context research records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
