//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestCurrentFeedStructuralStopExporter.mq5              |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.0.0                                                  |
//| Purpose : Verify current-feed past-only Stop export              |
//+------------------------------------------------------------------+
#property strict
#include "../core/ai/PastOnlyStructuralStopExporter.mqh"
input string RequestFile="XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv";
input string OutputFile="XAU_AI_CURRENT_FEED_STOP_LADDERS.csv";
input int ProgressInterval=50;
bool TestBuyStopLadder(CPastOnlyStructuralStopExporter &exporter)
  {
   const int size=exporter.RequiredBars();
   double highs[];
   double lows[];
   ArrayResize(highs,size);
   ArrayResize(lows,size);
   ArrayInitialize(highs,101.0);
   ArrayInitialize(lows,99.0);
   lows[4]=95.0;
   lows[10]=90.0;
   lows[16]=80.0;
   double stops[];
   const int count=exporter.BuildStopLadder(100.0,true,highs,lows,0.01,stops);
   return(count==3 && stops[0]==95.0 && stops[1]==90.0 && stops[2]==80.0);
  }
bool TestSellStopLadder(CPastOnlyStructuralStopExporter &exporter)
  {
   const int size=exporter.RequiredBars();
   double highs[];
   double lows[];
   ArrayResize(highs,size);
   ArrayResize(lows,size);
   ArrayInitialize(highs,101.0);
   ArrayInitialize(lows,99.0);
   highs[4]=105.0;
   highs[10]=110.0;
   highs[16]=120.0;
   double stops[];
   const int count=exporter.BuildStopLadder(100.0,false,highs,lows,0.01,stops);
   return(count==3 && stops[0]==105.0 && stops[1]==110.0 && stops[2]==120.0);
  }
int OnInit()
  {
   CPastOnlyStructuralStopExporter exporter;
   const bool buy_valid=TestBuyStopLadder(exporter);
   const bool sell_valid=TestSellStopLadder(exporter);
   Print("Current-feed Stop BUY ladder valid: ",buy_valid);
   Print("Current-feed Stop SELL ladder valid: ",sell_valid);
   if(!buy_valid || !sell_valid)
      return(INIT_FAILED);
   Print("Current-feed structural Stop export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,ProgressInterval);
   Print("Current-feed structural Stop records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }
void OnTick() {}
