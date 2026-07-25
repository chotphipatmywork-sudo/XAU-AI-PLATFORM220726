//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestCurrentFeedStructuralTargetExporter.mq5            |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.0.0                                                  |
//| Purpose : Verify current-feed past-only Target export contract   |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/PastOnlyStructuralTargetExporter.mqh"

input string RequestFile="XAU_AI_CURRENT_FEED_TARGET_REQUESTS.csv";
input string OutputFile="XAU_AI_CURRENT_FEED_TARGET_LADDERS.csv";
input int ProgressInterval=50;

bool LadderMathValid(CPastOnlyStructuralTargetExporter &exporter)
  {
   const int count=exporter.RequiredBars();
   double highs[];
   double lows[];
   ArrayResize(highs,count);
   ArrayResize(lows,count);
   for(int index=0; index<count; index++)
     {
      highs[index]=99.0;
      lows[index]=101.0;
     }
   highs[4]=105.0;
   highs[10]=110.0;
   highs[16]=120.0;
   double targets[];
   return(exporter.BuildTargetLadder(100.0,true,highs,lows,0.01,targets)==3 &&
          MathAbs(targets[0]-105.0)<0.000001 &&
          MathAbs(targets[1]-110.0)<0.000001 &&
          MathAbs(targets[2]-120.0)<0.000001);
  }

int OnInit()
  {
   CPastOnlyStructuralTargetExporter exporter;
   const bool timing=exporter.ExactTriggerTiming(
      StringToTime("2024.06.30 23:40:00"),
      StringToTime("2024.06.30 23:45:00"));
   const bool ladder=LadderMathValid(exporter);
   Print("Current-feed Target timing valid: ",timing);
   Print("Current-feed Target ladder math valid: ",ladder);
   if(!timing || !ladder || ProgressInterval<=0)
      return(INIT_FAILED);
   Print("Current-feed past-only Target export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,ProgressInterval);
   Print("Current-feed past-only Target records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
