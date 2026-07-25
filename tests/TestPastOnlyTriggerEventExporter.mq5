//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestPastOnlyTriggerEventExporter.mq5                   |
//| Layer   : Tests / AI / Learning / Offline Research               |
//| Version : 1.1.0                                                   |
//| Purpose : Verify causal M5 trigger-event export contract          |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/PastOnlyTriggerEventExporter.mqh"

input string RequestFile="XAU_AI_TRIGGER_EVENT_REQUESTS.csv";
input string OutputFile="XAU_AI_TRIGGER_EVENT_EVIDENCE.csv";
input string DataSymbol="";
input int ProgressInterval=25;

bool CloseEnough(const double left,const double right)
  {
   return(MathAbs(left-right)<=1e-9);
  }

int OnInit()
  {
   CPastOnlyTriggerEventExporter exporter;
   const datetime context_open=StringToTime("2025.07.10 00:05:00");
   const datetime entry_open=StringToTime("2025.07.10 00:10:00");
   const datetime observation=StringToTime("2025.07.10 00:15:00");
   const bool timing_valid=
      exporter.ExactTiming(context_open,entry_open,observation) &&
      !exporter.ExactTiming(context_open,entry_open,observation+300);
   const bool geometry_valid=
      exporter.ValidGeometry("TRADE_SETUP_BUY",100.0,99.0,98.0,104.0,0.01) &&
      exporter.ValidGeometry("TRADE_SETUP_SELL",100.0,101.0,102.0,96.0,0.01) &&
      !exporter.ValidGeometry("TRADE_SETUP_BUY",100.0,101.0,98.0,104.0,0.01);

   double range_atr=0.0,body_atr=0.0,directional_body=0.0;
   double upper_wick=0.0,lower_wick=0.0,close_location=0.0;
   const bool shape_valid=
      exporter.CalculateBarShape("TRADE_SETUP_BUY",100.0,105.0,98.0,104.0,
                                 2.0,range_atr,body_atr,directional_body,
                                 upper_wick,lower_wick,close_location) &&
      CloseEnough(range_atr,3.5) && CloseEnough(body_atr,2.0) &&
      CloseEnough(directional_body,2.0) && CloseEnough(upper_wick,0.5) &&
      CloseEnough(lower_wick,1.0) && CloseEnough(close_location,6.0/7.0);

   double buy_sweep=0.0,buy_reclaim=0.0;
   double sell_sweep=0.0,sell_reclaim=0.0;
   const bool directional_valid=
      exporter.DirectionalEvidence("TRADE_SETUP_BUY",105.0,98.0,104.0,
                                   100.0,2.0,buy_sweep,buy_reclaim) &&
      exporter.DirectionalEvidence("TRADE_SETUP_SELL",102.0,95.0,96.0,
                                   100.0,2.0,sell_sweep,sell_reclaim) &&
      CloseEnough(buy_sweep,1.0) && CloseEnough(buy_reclaim,2.0) &&
      CloseEnough(sell_sweep,1.0) && CloseEnough(sell_reclaim,2.0);

   double highs[]={110.0,109.0,108.0,107.0,106.0};
   double lows[]={90.0,91.0,92.0,93.0,94.0};
   const int level_age=exporter.FindExactLevelAge(highs,107.0,0.01,4);
   int touch_age=-1,touch_count=0;
   const bool age_valid=(level_age==3 &&
      exporter.PriorPoiTouchStats(highs,lows,100.0,0.01,4,
                                  touch_age,touch_count) &&
      touch_age==1 && touch_count==4);

   Print("Past-only trigger-event timing valid: ",timing_valid);
   Print("Past-only trigger-event geometry valid: ",geometry_valid);
   Print("Past-only trigger-event bar shape valid: ",shape_valid);
   Print("Past-only trigger-event directional evidence valid: ",directional_valid);
   Print("Past-only trigger-event structural age valid: ",age_valid);
   if(!timing_valid || !geometry_valid || !shape_valid || !directional_valid ||
      !age_valid || ProgressInterval<=0)
      return(INIT_FAILED);

   const string data_symbol=(DataSymbol=="" ? _Symbol : DataSymbol);
   Print("Past-only trigger-event export started; deployment=false; data_symbol=",
         data_symbol);
   const int written=exporter.Export(RequestFile,OutputFile,data_symbol,
                                     ProgressInterval);
   Print("Past-only trigger-event records written: ",written);
   ExpertRemove();
   return(written>0 ? INIT_SUCCEEDED : INIT_FAILED);
  }

void OnTick()
  {
  }
