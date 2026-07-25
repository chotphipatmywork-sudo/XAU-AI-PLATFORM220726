//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestCurrentFeedJointGeometryM5Exporter.mq5              |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.0.0                                                  |
//| Purpose : Export frozen IMP-096 M5 causal paths                  |
//+------------------------------------------------------------------+
#property strict
#include "../core/ai/PastOnlyLifecyclePathExporter.mqh"
input string RequestFile="XAU_AI_CURRENT_FEED_JOINT_M5_REQUESTS.csv";
input string OutputFile="XAU_AI_CURRENT_FEED_JOINT_M5_PATHS.csv";
input int ProgressInterval=10;
int OnInit()
  {
   CPastOnlyLifecyclePathExporter exporter;
   const bool window=exporter.ValidWindow(StringToTime("2024.06.01 00:00"),
                                          StringToTime("2024.06.01 00:15"),192);
   const bool geometry=exporter.ValidGeometry("TRADE_SETUP_BUY",100.0,90.0,
                                              121.0,0.0,0.01,2.1);
   Print("Joint geometry M5 window valid: ",window);
   Print("Joint geometry M5 geometry valid: ",geometry);
   if(!window || !geometry) return(INIT_FAILED);
   Print("Joint geometry M5 export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,ProgressInterval);
   Print("Joint geometry M5 requests written: ",written);
   ExpertRemove();
   return(written==76 ? INIT_SUCCEEDED : INIT_FAILED);
  }
void OnTick() {}
