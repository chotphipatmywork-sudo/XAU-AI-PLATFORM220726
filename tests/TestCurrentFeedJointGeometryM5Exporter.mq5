//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestCurrentFeedJointGeometryM5Exporter.mq5              |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 2.0.0                                                  |
//| Purpose : Export frozen IMP-100 outcome-free causal M5 paths     |
//+------------------------------------------------------------------+
#property strict
#include "../core/ai/OutcomeFreeM5PathExporter.mqh"
input string RequestFile="XAU_AI_IMP100_OUTCOME_FREE_M5_REQUESTS.csv";
input string OutputFile="XAU_AI_IMP100_OUTCOME_FREE_M5_PATHS.csv";
input string TrainEndExclusive="2024.07.01 00:00";
input int MaximumPathM5Bars=192;
input int ProgressInterval=25;
input bool ShutdownTerminalAfterExport=false;
int OnInit()
  {
   COutcomeFreeM5PathExporter exporter;
   const datetime cutoff=StringToTime(TrainEndExclusive);
   const bool window=exporter.ValidWindow(
      StringToTime("2024.06.01 00:00"),cutoff,MaximumPathM5Bars);
   const bool closed=exporter.BarIsCausallyClosed(
      StringToTime("2024.06.01 00:00"),
      StringToTime("2024.06.01 00:00"),cutoff);
   Print("IMP-100 outcome-free M5 window valid: ",window);
   Print("IMP-100 causal closed-M5 boundary valid: ",closed);
   if(!window || !closed) return(INIT_FAILED);
   Print("IMP-100 outcome-free M5 export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,cutoff,
                                     MaximumPathM5Bars,ProgressInterval);
   Print("IMP-100 outcome-free M5 requests written: ",written);
   if(ShutdownTerminalAfterExport)
      TerminalClose(written==685 ? 0 : 1);
   ExpertRemove();
   return(written==685 ? INIT_SUCCEEDED : INIT_FAILED);
  }
void OnTick() {}