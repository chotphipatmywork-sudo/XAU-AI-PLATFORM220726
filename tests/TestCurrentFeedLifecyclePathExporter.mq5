//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestCurrentFeedLifecyclePathExporter.mq5               |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.0.0                                                  |
//| Purpose : Verify current-feed causal M5 lifecycle export         |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/PastOnlyLifecyclePathExporter.mqh"

input string RequestFile="XAU_AI_CURRENT_FEED_LIFECYCLE_REQUESTS.csv";
input string OutputFile="XAU_AI_CURRENT_FEED_LIFECYCLE_M5_PATHS.csv";
input int ProgressInterval=10;

int OnInit()
  {
   CPastOnlyLifecyclePathExporter exporter;
   const datetime observation=StringToTime("2024.06.01 00:00:00");
   const datetime known_at=StringToTime("2024.06.01 00:15:00");
   const bool window=exporter.ValidWindow(observation,known_at,192);
   const bool geometry=exporter.ValidGeometry(
      "TRADE_SETUP_BUY",100.0,90.0,121.0,0.0,0.01,2.1);
   Print("Current-feed lifecycle window valid: ",window);
   Print("Current-feed lifecycle geometry valid: ",geometry);
   if(!window || !geometry || ProgressInterval<=0)
      return(INIT_FAILED);
   Print("Current-feed lifecycle M5 export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,ProgressInterval);
   Print("Current-feed lifecycle requests written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
