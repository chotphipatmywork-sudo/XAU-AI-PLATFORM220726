//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestLabelGenerator.mq5                                 |
//| Layer   : Tests / AI / Learning                                  |
//| Version : 1.1.0                                                  |
//| Purpose : Verify exact triple-barrier horizon enforcement        |
//+------------------------------------------------------------------+

#property strict

#include "../core/ai/LabelGenerator.mqh"

void OnStart()
  {
   MqlRates bars[];
   ArrayResize(bars,17);

   for(int index=0; index<ArraySize(bars); index++)
     {
      bars[index].close=100.0;
      bars[index].high=101.0;
      bars[index].low=99.0;
     }

   bars[1].high=116.0;

   CLabelGenerator generator;
   const bool configured=generator.Configure(16,14,1.5);
   ENUM_AI_TRAINING_LABEL label=AI_LABEL_HOLD;
   const bool generated=generator.Generate(bars,0,10.0,label);
   const bool exact_horizon_buy=(generated && label==AI_LABEL_BUY);

   MqlRates short_bars[];
   ArrayResize(short_bars,16);
   for(int index=0; index<ArraySize(short_bars); index++)
     {
      short_bars[index].close=100.0;
      short_bars[index].high=101.0;
      short_bars[index].low=99.0;
     }
   label=AI_LABEL_HOLD;
   const bool truncated_rejected=
      !generator.Generate(short_bars,0,10.0,label);
   const bool late_entry_rejected=
      !generator.Generate(bars,1,10.0,label);
   const bool contract_valid=(configured && exact_horizon_buy &&
                              truncated_rejected && late_entry_rejected);
   Print("Label exact 16-bar horizon BUY valid: ",exact_horizon_buy);
   Print("Label truncated horizon rejected: ",truncated_rejected);
   Print("Label late entry horizon rejected: ",late_entry_rejected);
   Print("Label full-horizon contract valid: ",contract_valid);
  }
