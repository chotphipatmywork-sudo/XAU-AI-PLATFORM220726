//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestHistoricalH1ContextExporter.mq5                    |
//| Layer   : Tests / AI / Learning / Research                        |
//| Version : 1.0.0                                                  |
//| Purpose : Verify and run leakage-safe H1 context export          |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/HistoricalH1ContextExporter.mqh"

input string DatasetFile="XAU_AI_TRAINING_DATASET.csv";
input string OutputFile="XAU_AI_H1_CONTEXT_RESEARCH.csv";
input int ProgressInterval=100;

int OnInit()
  {
   CHistoricalH1ContextExporter exporter;
   const datetime m15_open=StringToTime("2026.07.16 08:45:00");
   const datetime observation=exporter.ObservationTime(m15_open,PERIOD_M15);
   const bool timing_valid=(observation==StringToTime("2026.07.16 09:00:00") &&
                            exporter.IsHigherBarClosed(StringToTime("2026.07.16 08:00:00"),observation) &&
                            !exporter.IsHigherBarClosed(StringToTime("2026.07.16 09:00:00"),observation));
   Print("Historical H1 closed-bar timing valid: ",timing_valid);
   if(!timing_valid || ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Historical H1 context research export started");
   const int written=exporter.Export(DatasetFile,OutputFile,ProgressInterval);
   Print("Historical H1 context research records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
