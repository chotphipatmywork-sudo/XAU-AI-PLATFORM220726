//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestPastOnlyStructuralTargetExporter.mq5               |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.0.0                                                  |
//| Purpose : Verify past-only Target ladder and export contract     |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/PastOnlyStructuralTargetExporter.mqh"

input string RequestFile="XAU_AI_PAST_ONLY_TARGET_REQUESTS.csv";
input string OutputFile="XAU_AI_PAST_ONLY_TARGET_LADDERS.csv";
input int ProgressInterval=100;

void SetBase(double &highs[],double &lows[],const int count)
  {
   ArrayResize(highs,count);
   ArrayResize(lows,count);
   for(int index=0; index<count; index++)
     {
      highs[index]=99.0;
      lows[index]=101.0;
     }
  }

bool BuyLadderValid(CPastOnlyStructuralTargetExporter &exporter)
  {
   double highs[];
   double lows[];
   SetBase(highs,lows,exporter.RequiredBars());
   highs[1]=130.0;
   highs[4]=110.0;
   highs[10]=105.0;
   highs[16]=120.0;
   highs[22]=105.004;
   double targets[];
   const int count=exporter.BuildTargetLadder(100.0,true,highs,lows,
                                              0.01,targets);
   return(count==3 && ArraySize(targets)==3 &&
          MathAbs(targets[0]-105.0)<0.000001 &&
          MathAbs(targets[1]-110.0)<0.000001 &&
          MathAbs(targets[2]-120.0)<0.000001);
  }

bool SellLadderValid(CPastOnlyStructuralTargetExporter &exporter)
  {
   double highs[];
   double lows[];
   SetBase(highs,lows,exporter.RequiredBars());
   lows[1]=70.0;
   lows[4]=90.0;
   lows[10]=95.0;
   lows[16]=80.0;
   double targets[];
   const int count=exporter.BuildTargetLadder(100.0,false,highs,lows,
                                              0.01,targets);
   return(count==3 && ArraySize(targets)==3 &&
          MathAbs(targets[0]-95.0)<0.000001 &&
          MathAbs(targets[1]-90.0)<0.000001 &&
          MathAbs(targets[2]-80.0)<0.000001);
  }

int OnInit()
  {
   CPastOnlyStructuralTargetExporter exporter;
   const datetime observation=StringToTime("2025.07.10 00:15:00");
   const bool timing_valid=
      exporter.ExactTriggerTiming(StringToTime("2025.07.10 00:10:00"),
                                  observation) &&
      !exporter.ExactTriggerTiming(StringToTime("2025.07.10 00:05:00"),
                                   observation);
   const bool buy_valid=BuyLadderValid(exporter);
   const bool sell_valid=SellLadderValid(exporter);
   Print("Past-only Target ladder timing valid: ",timing_valid);
   Print("Past-only Target BUY ladder valid: ",buy_valid);
   Print("Past-only Target SELL ladder valid: ",sell_valid);
   if(!timing_valid || !buy_valid || !sell_valid || ProgressInterval<=0)
      return(INIT_FAILED);

   Print("Past-only structural Target export started; deployment=false");
   const int written=exporter.Export(RequestFile,OutputFile,ProgressInterval);
   Print("Past-only structural Target records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }

