//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestPastOnlyLifecyclePathExporter.mq5                  |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.1.0                                                  |
//| Purpose : Verify mature M5 lifecycle path export contract        |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/PastOnlyLifecyclePathExporter.mqh"

input string RequestFile="XAU_AI_LIFECYCLE_PATH_REQUESTS.csv";
input string OutputFile="XAU_AI_LIFECYCLE_M5_PATHS.csv";
input int ProgressInterval=25;

int OnInit()
  {
   CPastOnlyLifecyclePathExporter exporter;
   const datetime observation=StringToTime("2025.07.10 00:15:00");
   const datetime known_at=StringToTime("2025.07.10 00:30:00");
   const bool window_valid=
      exporter.ValidWindow(observation,known_at,192) &&
      !exporter.ValidWindow(observation,known_at,0) &&
      !exporter.ValidWindow(observation,known_at,193) &&
      exporter.BarWithinWindow(observation,observation,known_at) &&
      exporter.BarWithinWindow(observation+600,observation,known_at) &&
      !exporter.BarWithinWindow(known_at,observation,known_at);
   const bool buy_valid=exporter.ValidGeometry(
      "TRADE_SETUP_BUY",100.0,90.0,121.0,2.0,0.01,
      (20.98/10.02));
   const bool sell_valid=exporter.ValidGeometry(
      "TRADE_SETUP_SELL",100.0,110.0,79.0,2.0,0.01,
      (20.98/10.02));
   const bool invalid_rejected=!exporter.ValidGeometry(
      "TRADE_SETUP_BUY",100.0,110.0,121.0,2.0,0.01,
      (20.98/10.02));
   Print("Past-only lifecycle window valid: ",window_valid);
   Print("Past-only lifecycle BUY geometry valid: ",buy_valid);
   Print("Past-only lifecycle SELL geometry valid: ",sell_valid);
   Print("Past-only lifecycle invalid geometry rejected: ",invalid_rejected);
   if(!window_valid || !buy_valid || !sell_valid || !invalid_rejected ||
      ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Past-only lifecycle M5 export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,ProgressInterval);
   Print("Past-only lifecycle requests written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
