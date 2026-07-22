//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : TestBrain.mq5                                          |
//| Purpose : Brain integration test                                 |
//+------------------------------------------------------------------+
#property strict

#include "../core/brain/Brain.mqh"

//--------------------------------------------------

CBrain Brain;

//--------------------------------------------------

int OnInit()
{
   CBrainPipelineResult pipeline =
      Brain.Think(
         _Symbol,
         PERIOD_CURRENT);

   Print("========== BRAIN ==========");

   Print("Symbol      : ", _Symbol);

   Print("Timeframe   : ", EnumToString(PERIOD_CURRENT));

   Print("Brain Valid : ", pipeline.Valid);

   Print("Signal Type : ", EnumToString(pipeline.Signal.type));

   Print("Confidence  : ", pipeline.Signal.confidence);

   Print("Source      : ", pipeline.Signal.source);

   Print("Reason      : ", pipeline.Signal.reason);

   Print("Timestamp   : ", TimeToString(pipeline.Signal.timestamp));

   return INIT_SUCCEEDED;
}

//--------------------------------------------------

void OnTick()
{
}

//--------------------------------------------------

void OnDeinit(const int reason)
{
}
